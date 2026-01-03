"""logkiss - Keep It Simple and Stupid Logger.

Copyright (c) 2025 Taka Suzuki
SPDX-License-Identifier: MIT
See LICENSE for details.

A simple and colorful Python logging library.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Set debug mode
DEBUG_MODE = os.environ.get("LOGKISS_DEBUG", "0").lower() in ("1", "true", "yes")

# Import logkiss module classes
from .logkiss import (
    KissLogger,
    KissConsoleHandler,
    ColoredFormatter,
)

# Import config module
from .config import dictConfig, fileConfig, yaml_config

# Import base handler only
from .handlers import BaseHandler

# プロキシクラスと遅延インポート機能
# クラウドサービス依存関係を実際に使用するまで読み込まない


# AWS CloudWatchハンドラー用プロキシクラス
class AWSCloudWatchHandler:
    """AWS CloudWatch Logs対応のロギングハンドラー

    実際のAWS SDK (boto3)の読み込みは初めて使用されるときまで遅延されます。
    """

    def __new__(cls, *args, **kwargs):
        # 遅延インポート
        try:
            from .handlers import AWSCloudWatchHandler as RealHandler

            # 実際のクラスのインスタンスを返す
            return RealHandler(*args, **kwargs)
        except ImportError as exc:
            raise ImportError(
                "AWSCloudWatchHandler requires boto3 package. " "Install it with: pip install 'logkiss[aws]' or pip install boto3"
            ) from exc


# GCP Cloud Loggingハンドラー用プロキシクラス
class GCloudLoggingHandler:
    """Google Cloud Logging対応のロギングハンドラー

    実際のGoogle Cloud SDK (google-cloud-logging)の読み込みは初めて使用されるときまで遅延されます。
    """

    def __new__(cls, *args, **kwargs):
        # 遅延インポート
        try:
            from .handler_gcp import GCloudLoggingHandler as RealHandler

            # 実際のクラスのインスタンスを返す
            return RealHandler(*args, **kwargs)
        except ImportError as exc:
            raise ImportError(
                "GCloudLoggingHandler requires google-cloud-logging package. "
                "Install it with: pip install 'logkiss[gcp]' or pip install google-cloud-logging"
            ) from exc


# GCPロギング設定関数の遅延インポート版
def setup_gcp_logging(*args, **kwargs):
    """Google Cloud Loggingの設定を行う（遅延ロード）

    実際のGoogle Cloud SDK (google-cloud-logging)の読み込みは初めて使用されるときまで遅延されます。
    """
    try:
        from .handler_gcp import setup_gcp_logging as real_setup

        return real_setup(*args, **kwargs)
    except ImportError as exc:
        raise ImportError(
            "setup_gcp_logging requires google-cloud-logging package. "
            "Install it with: pip install 'logkiss[gcp]' or pip install google-cloud-logging"
        ) from exc


# Try to import Qt handler if available
try:
    from .handler_qt import QtTextEditHandler, QT_AVAILABLE
except ImportError:
    QT_AVAILABLE = False

# Import standard logging module functions
from logging import (
    BASIC_FORMAT,
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    NOTSET,
    WARN,
    WARNING,
    addLevelName,
    basicConfig,
    critical,
    debug,
    disable,
    error,
    exception,
    fatal,
    getLevelName,
    getLogger as _getLogger,
    getLoggerClass,
    info,
    log,
    makeLogRecord,
    setLoggerClass,
    warn,
    warning,
    getLogRecordFactory,
    setLogRecordFactory,
)

# logkissとしてgetLoggerを標準logging.getLoggerで公開
getLogger = logging.getLogger


def init_logging(*args, **kwargs):
    """
    [DEPRECATED] For backward compatibility only. Does nothing.
    Use standard logging.basicConfig or logging.getLogger instead.
    """
    import warnings

    warnings.warn(
        "logkiss.init_logging() is deprecated. Use standard logging.basicConfig or logging.getLogger instead.", DeprecationWarning, stacklevel=2
    )
    return logging.getLogger()


# Define __all__
__all__ = [
    "BASIC_FORMAT",
    "BufferingFormatter",
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "FATAL",
    "FileHandler",
    "Filter",
    "Formatter",
    "Handler",
    "INFO",
    "LogRecord",
    "Logger",
    "LoggerAdapter",
    "NOTSET",
    "NullHandler",
    "StreamHandler",
    "WARN",
    "WARNING",
    "addLevelName",
    "basicConfig",
    "critical",
    "debug",
    "disable",
    "error",
    "exception",
    "fatal",
    "getLevelName",
    "getLogger",
    "getLoggerClass",
    "info",
    "log",
    "makeLogRecord",
    "setLoggerClass",
    "warn",
    "warning",
    # ハンドラー
    "BaseHandler",
    "AWSCloudWatchHandler",
    "GCloudLoggingHandler",
    "setup_gcp_logging",
    # Qt handler
    "QtTextEditHandler",
    "QT_AVAILABLE",
    # 設定
    "dictConfig",
    "fileConfig",
    "yaml_config",
]

# グローバル設定
# Inherit standard logging module functions
BASIC_FORMAT = logging.BASIC_FORMAT
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

# Inherit logging module functions
disable = logging.disable
shutdown = logging.shutdown
addLevelName = logging.addLevelName
getLevelName = logging.getLevelName
makeLogRecord = logging.makeLogRecord


def getLoggerClass() -> type:
    """Get current logger class"""
    return logging.getLoggerClass()


def setLoggerClass(cls: type) -> None:
    """Set logger class"""
    logging.setLoggerClass(cls)


# Inherit standard logging module classes
BufferingFormatter = logging.BufferingFormatter
Filter = logging.Filter
Formatter = logging.Formatter
Handler = logging.Handler
LogRecord = logging.LogRecord
Logger = logging.Logger
LoggerAdapter = logging.LoggerAdapter
Manager = logging.Manager
PlaceHolder = logging.PlaceHolder
StreamHandler = logging.StreamHandler
FileHandler = logging.FileHandler
NullHandler = logging.NullHandler
RotatingFileHandler = logging.handlers.RotatingFileHandler
TimedRotatingFileHandler = logging.handlers.TimedRotatingFileHandler

# Inherit other variables
raiseExceptions = logging.raiseExceptions


def use_console_handler(logger: Optional[logging.Logger] = None) -> None:
    """Use standard ConsoleHandler

    .. deprecated:: 2.2.0
       This function is deprecated. Use standard logging methods instead:

       .. code-block:: python

          # Remove existing handlers and add a standard one
          logger.handlers.clear()
          logger.addHandler(logging.StreamHandler())
    """
    import warnings

    warnings.warn(
        "use_console_handler is deprecated. Use standard logging methods instead: "
        "logger.handlers.clear() and logger.addHandler(logging.StreamHandler())",
        DeprecationWarning,
        stacklevel=2,
    )

    if logger is None:
        logger = logging.getLogger()

    # Remove KissConsoleHandler
    for handler in logger.handlers[:]:
        if isinstance(handler, KissConsoleHandler):
            logger.removeHandler(handler)

    # Add standard ConsoleHandler
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s,%(msecs)03d %(levelname)-5s | %(filename)s:%(lineno)3d | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)


# Version information
__version__ = "2.3.1"

# --- logkiss default handler initialization ---
# --- logkiss default handler initialization ---
root_logger = logging.getLogger()
root_logger.handlers.clear()  # 既存のハンドラを全て除去
handler = KissConsoleHandler()

# --- サブロガーにハンドラがある場合はルートで出力しないフィルタ ---
class _SkipIfLoggerHasHandlers(logging.Filter):
    def filter(self, record):
        logger = logging.getLogger(record.name)
        # サブロガーで、ルート以外でハンドラが1つ以上あればルートで出力しない
        if logger is not root_logger and logger.handlers:
            return False
        return True
handler.addFilter(_SkipIfLoggerHasHandlers())
# -------------------------------------------------------------

root_logger.addHandler(handler)
root_logger.propagate = False
