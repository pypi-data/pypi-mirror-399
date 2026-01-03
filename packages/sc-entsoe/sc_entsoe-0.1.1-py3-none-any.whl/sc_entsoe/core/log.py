"""Logging utilities for sc-entsoe library."""

from typing import cast

import structlog


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return cast(structlog.BoundLogger, structlog.get_logger(name))


def configure_logging(debug: bool = False) -> None:
    """Configure structlog for the library.

    Args:
        debug: Enable debug logging
    """
    import logging

    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
