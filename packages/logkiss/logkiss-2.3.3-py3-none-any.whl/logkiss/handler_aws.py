#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AWS CloudWatch Logs Handler for logkiss.

This module provides a handler for sending logs to AWS CloudWatch Logs.
It uses the boto3 library for AWS integration.

Copyright (c) 2025 Taka Suzuki
SPDX-License-Identifier: MIT
"""

import logging
import os
import json
import time
from typing import Dict, Any, Optional, Union
from datetime import datetime

try:
    import boto3

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False


class AWSCloudWatchHandler(logging.Handler):
    """AWS CloudWatch Logs handler for logkiss.

    This handler uses boto3 to send logs to AWS CloudWatch Logs.
    It provides a simple interface for configuring and using the handler.

    Args:
        log_group (str): The name of the CloudWatch Logs log group.
        log_stream (str, optional): The name of the CloudWatch Logs log stream.
            If not provided, a default stream name will be generated.
        aws_region (str, optional): AWS region name. If not provided, it will be
            determined from the environment or AWS configuration.
        aws_access_key_id (str, optional): AWS access key ID. If not provided,
            it will be determined from the environment or AWS configuration.
        aws_secret_access_key (str, optional): AWS secret access key. If not provided,
            it will be determined from the environment or AWS configuration.
        batch_size (int, optional): Maximum number of log events to send in a single batch.
            Defaults to 10000 (AWS CloudWatch Logs limit).
    """

    def __init__(
        self,
        log_group: str,
        log_stream: Optional[str] = None,
        aws_region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        batch_size: int = 10000,
    ) -> None:
        """Initialize the handler."""
        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required to use AWSCloudWatchHandler. " "Please install it with: pip install boto3")

        super().__init__()

        self.log_group = log_group
        self.log_stream = log_stream or f"logkiss-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        self.batch_size = min(batch_size, 10000)  # AWS limit

        # Initialize boto3 client
        self.client = boto3.client(
            "logs",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        # Ensure log group exists
        self._create_log_group()

        # Create log stream
        self._create_log_stream()

        # Initialize sequence token
        self.sequence_token = None

        # Set formatter
        formatter = logging.Formatter("%(message)s")
        self.setFormatter(formatter)

    def _create_log_group(self) -> None:
        """Create the log group if it doesn't exist."""
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def _create_log_stream(self) -> None:
        """Create the log stream if it doesn't exist."""
        try:
            self.client.create_log_stream(logGroupName=self.log_group, logStreamName=self.log_stream)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        # Prepare the log event
        log_event = {
            "timestamp": int(record.created * 1000),
            "message": self.format(record),
        }

        # Add structured logging if extra fields are present
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            try:
                # Convert the message to JSON format
                log_event["message"] = json.dumps({"message": log_event["message"], "extra": record.extra})
            except (TypeError, ValueError):
                # Fallback to string representation if JSON conversion fails
                log_event["message"] = f"{log_event['message']} {str(record.extra)}"

        # Send the log event
        self._put_log_events([log_event])

    def _put_log_events(self, log_events: list) -> None:
        """Send log events to CloudWatch Logs.

        Args:
            log_events (list): List of log events to send.
        """
        kwargs = {"logGroupName": self.log_group, "logStreamName": self.log_stream, "logEvents": log_events}

        if self.sequence_token:
            kwargs["sequenceToken"] = self.sequence_token

        try:
            response = self.client.put_log_events(**kwargs)
            self.sequence_token = response.get("nextSequenceToken")
        except (self.client.exceptions.InvalidSequenceTokenException, self.client.exceptions.DataAlreadyAcceptedException) as e:
            # Handle sequence token issues
            if hasattr(e, "response"):
                self.sequence_token = e.response.get("expectedSequenceToken")
                if self.sequence_token:
                    # Retry with correct sequence token
                    kwargs["sequenceToken"] = self.sequence_token
                    response = self.client.put_log_events(**kwargs)
                    self.sequence_token = response.get("nextSequenceToken")

    def close(self) -> None:
        """Close the handler."""
        self.client = None
        super().close()


def setup_aws_logging(
    log_group: str,
    log_stream: Optional[str] = None,
    aws_region: Optional[str] = None,
    level: Union[int, str] = logging.INFO,
) -> AWSCloudWatchHandler:
    """AWS CloudWatch Logsの設定を行います。

    Args:
        log_group: CloudWatch Logsのロググループ名
        log_stream: CloudWatch Logsのログストリーム名（省略可）
        aws_region: AWSリージョン名（省略可）
        level: ログレベル

    Returns:
        AWSCloudWatchHandler: 設定されたハンドラー
    """
    # ルートロガーを取得
    root_logger = logging.getLogger()

    # AWSCloudWatchHandlerを作成
    handler = AWSCloudWatchHandler(
        log_group=log_group,
        log_stream=log_stream,
        aws_region=aws_region,
    )

    # ログレベルを設定
    handler.setLevel(level)

    # ルートロガーにハンドラーを追加
    root_logger.addHandler(handler)

    return handler


def create_handler(
    log_group: str,
    log_stream: Optional[str] = None,
    aws_region: Optional[str] = None,
) -> AWSCloudWatchHandler:
    """Create an AWSCloudWatchHandler with minimal configuration.

    Args:
        log_group (str): The name of the CloudWatch Logs log group.
        log_stream (str, optional): The name of the CloudWatch Logs log stream.
        aws_region (str, optional): AWS region name.

    Returns:
        AWSCloudWatchHandler: The created handler.
    """
    # Use environment variable if aws_region is not provided
    if aws_region is None:
        aws_region = os.environ.get("AWS_REGION")

    # Create the handler
    return AWSCloudWatchHandler(
        log_group=log_group,
        log_stream=log_stream,
        aws_region=aws_region,
    )
