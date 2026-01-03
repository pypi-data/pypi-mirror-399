#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
logkissの設定モジュール

標準のloggingモジュールの設定関数を拡張し、色付きログなどの機能をサポートします。
"""

import logging
import logging.config
import os
import sys
from typing import Dict, Any, Optional, Union
from pathlib import Path
import yaml
from yaml import safe_load
from yaml.error import YAMLError

# 循環インポートを避けるために関数内でインポートする
def _get_colored_formatter():
    from logkiss.logkiss import ColoredFormatter
    return ColoredFormatter


def dictConfig(config: Dict[str, Any]) -> None:
    """
    Configure logging using a dictionary

    This function is similar to logging.config.dictConfig, but it also handles
    color settings for ColoredFormatter.

    Args:
        config: A dictionary containing logging configuration

    Example:
        >>> import logkiss.config
        >>> logkiss.config.dictConfig({
        ...     "version": 1,
        ...     "formatters": {
        ...         "colored": {
        ...             "format": "%(asctime)s [%(levelname)s] %(message)s",
        ...             "datefmt": "%Y-%m-%d %H:%M:%S",
        ...             "class": "logkiss.ColoredFormatter",
        ...             "colors": {
        ...                 "levels": {
        ...                     "DEBUG": {"fg": "blue"},
        ...                     "INFO": {"fg": "white"},
        ...                     "WARNING": {"fg": "yellow"},
        ...                     "ERROR": {"fg": "black", "bg": "red"},
        ...                     "CRITICAL": {"fg": "black", "bg": "bright_red", "style": "bold"}
        ...                 }
        ...             }
        ...         }
        ...     },
        ...     "handlers": {
        ...         "console": {
        ...             "class": "logging.StreamHandler",
        ...             "level": "DEBUG",
        ...             "formatter": "colored",
        ...             "stream": "ext://sys.stdout"
        ...         }
        ...     },
        ...     "root": {
        ...         "level": "DEBUG",
        ...         "handlers": ["console"]
        ...     }
        ... })
    """
    # Get color settings in advance
    color_configs = {}
    if "formatters" in config:
        for formatter_name, formatter_config in config["formatters"].items():
            if "colors" in formatter_config:
                # ディープコピーを作成して完全に置き換え
                import copy
                color_configs[formatter_name] = copy.deepcopy(formatter_config["colors"])
    
    # logging.config.dictConfigを使用して設定を適用
    logging.config.dictConfig(config)
    
    # 色設定を適用
    if color_configs:
        # 対応するフォーマッタを取得
        ColoredFormatter = _get_colored_formatter()
        
        # ルートロガーのハンドラーを取得
        root_logger = logging.getLogger("")
        if root_logger.handlers:
            # 全てのハンドラーに対して処理
            for handler in root_logger.handlers:
                if hasattr(handler, 'formatter') and isinstance(handler.formatter, ColoredFormatter):
                    formatter = handler.formatter
                    
                    # フォーマッター名を特定
                    for formatter_name, color_config in color_configs.items():
                        # 色設定を完全に置き換え
                        # ColorManagerの設定を更新
                        if hasattr(formatter, 'color_manager'):
                            formatter.color_manager.config = color_config
                        
                        # 一度適用したら終了
                        break


def fileConfig(fname: Union[str, Path], defaults: Optional[Dict[str, str]] = None, 
               disable_existing_loggers: bool = True) -> None:
    """
    標準ロギングライブラリのlogging.config.fileConfigと互換性のある設定関数

    この関数は標準のlogging.config.fileConfigを呼び出し、その後にlogkissの
    色設定を適用します。

    Args:
        fname: 設定ファイルのパス
        defaults: デフォルト値の辞書
        disable_existing_loggers: 既存のロガーを無効化するかどうか

    Note:
        現在のバージョンでは、標準のfileConfig形式での色設定はサポートされていません。
        色設定を行う場合は、YAMLファイルとdictConfigを使用してください。
    """
    # 標準のfileConfigを呼び出し
    logging.config.fileConfig(fname, defaults, disable_existing_loggers)


def load_yaml_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    YAMLファイルから設定を読み込む

    Args:
        config_path: 設定ファイルのパス

    Returns:
        設定辞書

    Raises:
        ValueError: 設定ファイルが存在しない場合
        yaml.YAMLError: YAMLの形式が不正な場合
    """
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            config = safe_load(f)
    except FileNotFoundError as exc:
        raise ValueError(f"Configuration file not found: {config_path}") from exc
    except yaml.YAMLError as exc:
        raise yaml.YAMLError(f"Invalid YAML format in {config_path}: {exc}")
    
    # 空の設定ファイルの場合はデフォルト設定を返す
    if config is None:
        return {"version": 1}
    
    return config


def yaml_config(config_path: Union[str, Path]) -> None:
    """
    YAMLファイルから設定を読み込み、dictConfigで適用する

    環境変数が設定されている場合は、それらがYAMLファイルの設定よりも優先されます。

    Args:
        config_path: 設定ファイルのパス

    Example:
        >>> import logkiss.config
        >>> logkiss.config.yaml_config("logging_config.yaml")
    """
    # YAMLファイルから設定を読み込む
    config = load_yaml_config(config_path)
    
    # 最小限の設定が含まれていることを確認
    if "version" not in config:
        config["version"] = 1
    
    # 基本的なロギング設定がない場合は追加
    if "handlers" not in config:
        config["handlers"] = {
            "console": {
                "class": "logkiss.KissConsoleHandler",
                "level": "WARNING",
                "formatter": "colored"
            }
        }
    
    if "formatters" not in config:
        config["formatters"] = {
            "colored": {
                "class": "logkiss.ColoredFormatter",
                "format": "%(asctime)s [%(levelname)s] %(message)s"
            }
        }
    
    if "root" not in config:
        config["root"] = {
            "level": "WARNING",
            "handlers": ["console"]
        }
    
    # 環境変数から設定を取得
    level_env = os.environ.get("LOGKISS_LEVEL")
    fmt_env = os.environ.get("LOGKISS_FORMAT")
    datefmt_env = os.environ.get("LOGKISS_DATEFMT")
    
    # ログレベルを文字列から数値に変換
    if level_env:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level_value = level_map.get(level_env.upper(), logging.WARNING)
    
    # 環境変数が設定されている場合は、それらを設定に反映
    if level_env:
        # ルートロガーのレベルを設定
        if "loggers" in config and "" in config["loggers"]:
            config["loggers"][""]["level"] = level_value
        # rootセクションがある場合はそちらも設定
        if "root" in config:
            config["root"]["level"] = level_value
        # ハンドラーのレベルも設定
        if "handlers" in config:
            for handler in config["handlers"].values():
                handler["level"] = level_value
    
    # フォーマット文字列を設定
    if fmt_env and "formatters" in config:
        for formatter in config["formatters"].values():
            formatter["format"] = fmt_env
    
    # 日付フォーマット文字列を設定
    if datefmt_env and "formatters" in config:
        for formatter in config["formatters"].values():
            formatter["datefmt"] = datefmt_env
    
    # 設定を適用
    dictConfig(config)


def find_config_file() -> Optional[Path]:
    """
    設定ファイルを探す

    環境変数LOGKISS_CONFIGで指定されたパス、またはデフォルトの場所から設定ファイルを探します。

    Returns:
        設定ファイルのパス、見つからない場合はNone
    """
    # 環境変数から設定ファイルのパスを取得
    env_path = os.environ.get("LOGKISS_CONFIG")
    if env_path:
        p = Path(env_path).expanduser()
        if p.exists():
            return p

    # デフォルトの場所を探す
    candidates = []
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        userprofile = os.environ.get("USERPROFILE")
        if appdata:
            candidates.append(Path(appdata) / "logkiss" / "config.yaml")
        if userprofile:
            candidates.append(Path(userprofile) / ".config" / "logkiss" / "config.yaml")
    else:
        home = Path.home()
        candidates.append(home / ".config" / "logkiss" / "config.yaml")
        candidates.append(Path.cwd() / "logkiss.yaml")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def auto_config() -> None:
    """
    環境変数と設定ファイルから自動的に設定を適用する

    環境変数LOGKISS_SKIP_CONFIGが指定されている場合は設定ファイルの読み込みをスキップします。
    それ以外の場合は、設定ファイルを探して適用します。
    設定ファイルが見つからない場合は、環境変数から設定を適用します。
    """
    # 設定ファイルの読み込みをスキップするかチェック
    skip_config = os.environ.get("LOGKISS_SKIP_CONFIG", "").lower() in ("1", "true", "yes")
    if skip_config:
        # 環境変数から設定を適用
        _config_from_env()
        return

    # 設定ファイルを探す
    config_path = find_config_file()
    if config_path:
        # 設定ファイルから設定を適用
        yaml_config(config_path)
    else:
        # 環境変数から設定を適用
        _config_from_env()


def _config_from_env() -> None:
    """
    環境変数から設定を適用する

    環境変数:
        LOGKISS_LEVEL: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        LOGKISS_FORMAT: ログフォーマット文字列
        LOGKISS_DATEFMT: 日付フォーマット文字列
        LOGKISS_DISABLE_COLOR: カラー出力を無効化する場合は'true'
        NO_COLOR: 業界標準の環境変数（値は何でもよい）
    """
    # 環境変数から設定を取得
    level = os.environ.get("LOGKISS_LEVEL", "WARNING")
    fmt = os.environ.get("LOGKISS_FORMAT", "%(asctime)s,%(msecs)03d %(levelname)-5s | %(filename)s:%(lineno)3d | %(message)s")
    datefmt = os.environ.get("LOGKISS_DATEFMT", "%Y-%m-%d %H:%M:%S")

    # カラー出力の設定
    # カラー出力の設定はフォーマッター内で行われるので、ここでは特に設定しない
    
    # 環境変数の確認はフォーマッター内で行われる
    # 1. LOGKISS_DISABLE_COLOR: このライブラリ固有の環境変数
    # 2. NO_COLOR: 業界標準の環境変数 (https://no-color.org/)

    # dictConfig用の設定辞書を作成
    config = {
        "version": 1,
        "formatters": {
            "colored": {
                "()": "logkiss.ColoredFormatter",
                "format": fmt,
                "datefmt": datefmt,
                "colors": {
                    "levels": {
                        "DEBUG": {"fg": "blue"},
                        "INFO": {"fg": "white"},
                        "WARNING": {"fg": "yellow"},
                        "ERROR": {"fg": "black", "bg": "red"},
                        "CRITICAL": {"fg": "black", "bg": "bright_red", "style": "bold"},
                    }
                }
            }
        },
        "handlers": {
            "console": {
                "class": "logkiss.KissConsoleHandler",
                "level": level,
                "formatter": "colored"
            }
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": level
            }
        }
    }

    # 設定を適用
    dictConfig(config)


def _auto_config_from_env() -> None:
    """
    環境変数から自動的に設定を適用する

    KissLogger.reload_config()メソッドから呼び出されるための内部関数です。
    """
    _config_from_env()


# モジュール読み込み時に自動的に設定を適用
# ただし、引数なしでimportした場合のみ
# 例: import logkiss
# 例外: from logkiss import getLogger
if __name__ != "__main__" and not hasattr(logging.getLogger(), "_logkiss_configured"):
    auto_config()
    # 設定済みフラグを設定
    setattr(logging.getLogger(), "_logkiss_configured", True)


# 後方互換性のために残す（非推奨）
config_from_env = _config_from_env
