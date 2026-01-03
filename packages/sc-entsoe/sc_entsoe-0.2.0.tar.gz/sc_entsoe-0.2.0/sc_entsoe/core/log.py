"""Logging utilities for sc-entsoe library."""

import logging
from typing import Any


class SimpleLogger:
    """Simple logger wrapper that mimics structlog interface."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def debug(self, msg: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(self._format_msg(msg, kwargs))

    def info(self, msg: str, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(self._format_msg(msg, kwargs))

    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(self._format_msg(msg, kwargs))

    def error(self, msg: str, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(self._format_msg(msg, kwargs))

    def exception(self, msg: str, **kwargs: Any) -> None:
        """Log exception message."""
        self._logger.exception(self._format_msg(msg, kwargs))

    def _format_msg(self, msg: str, kwargs: dict[str, Any]) -> str:
        """Format message with kwargs."""
        if kwargs:
            parts = [f"{k}={v}" for k, v in kwargs.items()]
            return f"{msg} {' '.join(parts)}"
        return msg


def get_logger(name: str) -> SimpleLogger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger
    """
    return SimpleLogger(logging.getLogger(name))


def configure_logging(debug: bool = False) -> None:
    """Configure logging for the library.

    Args:
        debug: Enable debug logging
    """
    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
