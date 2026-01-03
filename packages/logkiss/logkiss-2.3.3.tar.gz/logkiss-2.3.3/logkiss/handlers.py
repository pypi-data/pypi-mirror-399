"""
Handlers module for logkiss logging.

Copyright (c) 2025 Taka Suzuki
SPDX-License-Identifier: MIT
See LICENSE for details.

This module contains various handlers used in logkiss.
Main classes:
- BaseHandler: Base handler class for implementing custom handlers
- AWSCloudWatchHandler: Handler for sending logs to AWS CloudWatch Logs
"""

import json
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union


class BaseHandler(logging.Handler):
    """Base handler class for implementing custom handlers"""

    def __init__(self, level=logging.NOTSET):
        """Initialize the handler"""
        super().__init__(level)

    def handle(self, record):
        """Handle a log record"""
        raise NotImplementedError("handle method must be implemented")


class AWSCloudWatchHandler(logging.Handler):
    """
    AWS CloudWatch Logs handler

    CloudWatchにログを送信するためのハンドラー。boto3モジュールが必要です。
    実際のインポートと初期化は実際に使用されるまで遅延されます。
    """

    def __init__(
        self,
        log_group_name: str,
        log_stream_name: Optional[str] = None,
        region_name: Optional[str] = None,
        batch_size: int = 100,
        flush_interval: float = 5.0,
    ) -> None:
        """初期化処理は実際の実装クラスに委譲します"""
        # 先に基底クラスの初期化
        super().__init__()

        # boto3が利用可能か確認
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 package is required. " "Install it with: pip install 'logkiss[cloud]'")

        # 属性を初期化して、初期化失敗時のエラーを防ぐ
        self._batch = []
        self._batch_lock = threading.Lock()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._sequence_token = None
        self._executor = None
        self._running = False
        self._flush_thread = None

        try:
            # AWS CloudWatch Logsクライアントを初期化
            self.client = boto3.client("logs", region_name=region_name)
            self.log_group_name = log_group_name

            if log_stream_name is None:
                # Try to determine an appropriate log stream name
                # First check if we're running on EC2
                log_stream_name = self._get_instance_identifier()

            self.log_stream_name = log_stream_name
            self._ensure_log_group_and_stream()

            # 定期的なフラッシュを開始
            self._start_periodic_flush()
        except Exception as e:
            import sys

            print(f"Error initializing AWSCloudWatchHandler: {e}", file=sys.stderr)
            # 初期化に失敗した場合は、runningフラグをFalseにして、スレッドが開始されないようにする
            self._running = False
            raise

    def _get_instance_identifier(self) -> str:
        """
        Get instance identifier for log stream name
        """
        try:
            # Try to get EC2 instance ID
            import requests

            response = requests.get("http://169.254.169.254/latest/meta-data/instance-id", timeout=0.1)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass

        # Fallback to hostname
        import socket

        return socket.gethostname()

    def _ensure_log_group_and_stream(self) -> None:
        """
        Ensure log group and stream exist
        """
        # Create log group if it doesn't exist
        try:
            self.client.create_log_group(logGroupName=self.log_group_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

        # Create log stream if it doesn't exist
        try:
            self.client.create_log_stream(logGroupName=self.log_group_name, logStreamName=self.log_stream_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            # Log stream already exists, get the sequence token
            response = self.client.describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.log_stream_name, limit=1)

            if response.get("logStreams"):
                self._sequence_token = response["logStreams"][0].get("uploadSequenceToken")

    def _start_periodic_flush(self) -> None:
        """Start a background thread to periodically flush the batch."""
        self._running = True
        self._flush_thread = threading.Thread(target=self._periodic_flush_worker, daemon=True)
        self._flush_thread.start()

    def _periodic_flush_worker(self) -> None:
        """Worker function for the periodic flush thread."""
        while self._running:
            try:
                # Sleep for the specified interval
                time.sleep(self._flush_interval)

                # バッチが空でなければフラッシュ
                if self._batch:
                    self._flush()
            except Exception as e:
                import sys

                print(f"Error in periodic flush: {e}", file=sys.stderr)

    def emit(self, record: logging.LogRecord) -> None:
        """Process log record"""
        try:
            # フォーマット済みのメッセージを取得
            msg = self.format(record)

            # タイムスタンプ（ミリ秒単位）
            timestamp = int(record.created * 1000)

            # バッチに追加するエントリ
            entry = {"timestamp": timestamp, "message": msg}

            # exc_info=Trueが指定された場合のスタックトレース情報を追加
            if record.exc_info:
                import traceback
                import json

                # JSONとして追加情報を埋め込む
                entry["message"] += "\nStack Trace: " + json.dumps({"stack_trace": traceback.format_exception(*record.exc_info)})

            # バッチに追加
            with self._batch_lock:
                self._batch.append(entry)

                # バッチサイズに達したらフラッシュ
                if len(self._batch) >= self._batch_size:
                    self._flush()
        except Exception as e:
            import sys

            print(f"Error in AWSCloudWatchHandler.emit: {e}", file=sys.stderr)

    def _flush(self) -> None:
        """Flush batch"""
        if not self._running:
            return

        entries = []
        with self._batch_lock:
            if not self._batch:
                return

            entries = self._batch
            self._batch = []

        if not entries:
            return

        # Sort entries by timestamp
        entries.sort(key=lambda x: x["timestamp"])

        # Convert to CloudWatch Logs format
        log_events = [{"timestamp": entry["timestamp"], "message": entry["message"]} for entry in entries]

        # ここでLazy Importを行う - 実際にAWS操作が必要なときだけ
        try:
            import boto3

            # Send to CloudWatch Logs
            kwargs = {"logGroupName": self.log_group_name, "logStreamName": self.log_stream_name, "logEvents": log_events}

            if self._sequence_token:
                kwargs["sequenceToken"] = self._sequence_token

            response = self.client.put_log_events(**kwargs)
            self._sequence_token = response.get("nextSequenceToken")
        except Exception as e:
            if hasattr(e, "__class__") and e.__class__.__name__ == "InvalidSequenceTokenException":
                # Get the correct sequence token from the error message
                import re

                match = re.search(r"sequenceToken is: (\S+)", str(e))
                if match:
                    self._sequence_token = match.group(1)
                    # Retry with the correct sequence token
                    self._flush()
            else:
                import sys

                print(f"Error writing to CloudWatch Logs: {e}", file=sys.stderr)
                # Put the entries back in the batch
                with self._batch_lock:
                    self._batch = entries + self._batch

    def flush(self) -> None:
        """Flush all queued messages to CloudWatch Logs"""
        self._flush()

    def close(self):
        """
        Close the handler and release all resources.
        """
        if not hasattr(self, "_running"):
            # 初期化が完了していない場合は何もしない
            super().close()
            return

        try:
            # スレッドを停止
            self._running = False

            # 最後の一回フラッシュを試みる
            try:
                self._flush()
            except Exception as e:
                import sys

                print(f"Error in final flush: {e}", file=sys.stderr)

            # スレッドが存在し、実行中であれば、終了を待つ（最大1秒）
            if hasattr(self, "_flush_thread") and self._flush_thread is not None:
                if self._flush_thread.is_alive():
                    self._flush_thread.join(timeout=1.0)
        except Exception as e:
            import sys

            print(f"Error closing handler: {e}", file=sys.stderr)
        finally:
            # 親クラスのcloseメソッドを呼び出す
            super().close()

    def __del__(self):
        """Cleanup when the handler is deleted"""
        try:
            if hasattr(self, "_running") and self._running:
                self.close()
        except Exception:
            # __del__内では例外を無視
            pass
