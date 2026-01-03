"""HTTP utilities."""

from collections.abc import Callable

from fastapi import Request, Response


def nop_wrapper(handler: Callable[[Request], Response]) -> Callable[[Request], Response]:
    """No-op wrapper for HTTP handlers."""
    return handler
