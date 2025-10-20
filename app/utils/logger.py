"""Application-wide logging utilities."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config.settings import app_settings

_COLOR_CODES = {
    "grey": "\033[90m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
}

_LEVEL_COLORS = {
    logging.DEBUG: _COLOR_CODES["cyan"],
    logging.INFO: _COLOR_CODES["green"],
    logging.WARNING: _COLOR_CODES["yellow"],
    logging.ERROR: _COLOR_CODES["red"],
    logging.CRITICAL: _COLOR_CODES["magenta"],
}

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_configured = False


def _resolve_level(level_name: str) -> int:
    try:
        return getattr(logging, level_name.upper())
    except AttributeError:
        return logging.INFO


class ColoredFormatter(logging.Formatter):
    """Formatter that adds ANSI colors when enabled."""

    def __init__(self, fmt: str, datefmt: Optional[str], use_colors: bool) -> None:
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - short override
        message = super().format(record)
        if not self.use_colors:
            return message

        color = _LEVEL_COLORS.get(record.levelno)
        if not color:
            return message
        return f"{color}{message}{_COLOR_CODES['reset']}"


def configure_logging() -> logging.Logger:
    """Configure root logging handlers once."""
    global _configured
    if _configured:
        return logging.getLogger()

    log_dir: Path = Path(app_settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    level = _resolve_level(app_settings.log_level)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(
        ColoredFormatter(_LOG_FORMAT, _DATE_FORMAT, use_colors=app_settings.log_use_colors)
    )
    root_logger.addHandler(console_handler)

    file_formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)

    complete_path = log_dir / app_settings.log_complete_file
    complete_handler = logging.FileHandler(complete_path, encoding="utf-8")
    complete_handler.setLevel(level)
    complete_handler.setFormatter(file_formatter)
    root_logger.addHandler(complete_handler)

    session_filename = f"{app_settings.log_session_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    session_path = log_dir / session_filename
    session_handler = logging.FileHandler(session_path, encoding="utf-8")
    session_handler.setLevel(level)
    session_handler.setFormatter(file_formatter)
    root_logger.addHandler(session_handler)

    _configured = True
    return root_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger, ensuring handlers exist."""
    configure_logging()
    if name is None:
        return logging.getLogger(app_settings.app_name)
    return logging.getLogger(name)
