#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Qt handler for logkiss.
This module provides a handler for logging to Qt text widgets.
The Qt module is optional and only required if you want to use the QtTextEditHandler.
"""

import logging
import sys
from typing import Optional, Dict, Any, Union

# Try to import Qt modules
QT_AVAILABLE = False
try:
    # Try PyQt5 first
    from PyQt5.QtWidgets import QTextEdit
    from PyQt5.QtGui import QColor, QTextCharFormat, QBrush, QFont
    from PyQt5.QtCore import Qt

    QT_AVAILABLE = True
except ImportError:
    try:
        # Try PySide2 as fallback
        from PySide2.QtWidgets import QTextEdit
        from PySide2.QtGui import QColor, QTextCharFormat, QBrush, QFont
        from PySide2.QtCore import Qt

        QT_AVAILABLE = True
    except ImportError:
        try:
            # Try PySide6 as another fallback
            from PySide6.QtWidgets import QTextEdit
            from PySide6.QtGui import QColor, QTextCharFormat, QBrush, QFont
            from PySide6.QtCore import Qt

            QT_AVAILABLE = True
        except ImportError:
            # Define placeholder classes for type hinting when Qt is not available
            class QTextEdit:
                pass

            class QColor:
                def __init__(self, *args):
                    pass

            class QFont:
                Bold = 75

            QBrush = object
            QTextCharFormat = object
            Qt = object


# Import from logkiss
from . import logkiss


class QtTextEditHandler(logging.Handler):
    """
    Custom logging handler that outputs log messages to a QTextEdit widget with colors.
    Supports light and dark themes.

    This handler requires PyQt5, PySide2, or PySide6 to be installed.
    If none of these modules are available, an ImportError will be raised when
    trying to use the handler.

    Args:
        text_edit: A QTextEdit widget to output logs to
        theme: The theme to use, "light" or "dark", defaults to "light"
        formatter: Optional custom formatter, if None, logkiss.ColoredFormatter is used

    Example:
        >>> import logkiss
        >>> from PyQt5.QtWidgets import QApplication, QTextEdit
        >>> app = QApplication([])
        >>> text_edit = QTextEdit()
        >>> handler = logkiss.QtTextEditHandler(text_edit)
        >>> logger = logkiss.getLogger()
        >>> logger.addHandler(handler)
        >>> logger.info("Hello from Qt!")
    """

    def __init__(self, text_edit: QTextEdit, theme: str = "light", formatter: Optional[logging.Formatter] = None):
        if not QT_AVAILABLE:
            raise ImportError("Qt modules not available. Install PyQt5, PySide2, or PySide6 to use QtTextEditHandler.")

        super().__init__()
        self.text_edit = text_edit
        self.formatter = formatter or logkiss.ColoredFormatter()
        self.theme = theme
        self.set_theme(theme)

    def set_theme(self, theme: str) -> None:
        """
        Set color theme (light or dark)

        Args:
            theme: The theme to use, "light" or "dark"
        """
        self.theme = theme
        if theme == "light":
            self.text_edit.setStyleSheet("background-color: white; color: black;")
            # Colors for light theme (darker colors for better visibility)
            self.level_colors = {
                logging.DEBUG: QColor(0, 130, 130),  # dark cyan
                logging.INFO: QColor(0, 0, 0),  # black
                logging.WARNING: QColor(180, 90, 0),  # dark orange
                logging.ERROR: QColor(200, 0, 0),  # dark red
                logging.CRITICAL: QColor(200, 0, 0),  # dark red (with background)
            }
            self.level_backgrounds = {
                logging.CRITICAL: QColor(255, 210, 210),  # light red background
            }
        else:  # dark theme
            self.text_edit.setStyleSheet("background-color: #2d2d2d; color: #f0f0f0;")
            # Colors for dark theme (brighter colors)
            self.level_colors = {
                logging.DEBUG: QColor(0, 255, 255),  # cyan
                logging.INFO: QColor(255, 255, 255),  # white
                logging.WARNING: QColor(255, 255, 0),  # yellow
                logging.ERROR: QColor(255, 100, 100),  # light red
                logging.CRITICAL: QColor(255, 100, 100),  # light red (with background)
            }
            self.level_backgrounds = {
                logging.CRITICAL: QColor(100, 0, 0),  # dark red background
            }

        # Font styles are the same for both themes
        self.level_styles = {
            logging.WARNING: QFont.Bold,
            logging.ERROR: QFont.Bold,
            logging.CRITICAL: QFont.Bold,
        }

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the QTextEdit widget with color formatting.

        Args:
            record: The log record to emit
        """
        if not QT_AVAILABLE:
            return

        try:
            # Get formatted message
            msg = self.format(record)

            # Create text format
            text_format = QTextCharFormat()
            text_format.setForeground(QBrush(self.level_colors.get(record.levelno, QColor(255, 255, 255))))

            # Apply background color if specified for the level
            if record.levelno in self.level_backgrounds:
                text_format.setBackground(QBrush(self.level_backgrounds[record.levelno]))

            # Apply font style if specified for the level
            if record.levelno in self.level_styles:
                font = text_format.font()
                font.setWeight(self.level_styles[record.levelno])
                text_format.setFont(font)

            # Insert text with formatting
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(msg + "\n", text_format)

            # Auto-scroll to bottom
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()
        except Exception:
            self.handleError(record)
