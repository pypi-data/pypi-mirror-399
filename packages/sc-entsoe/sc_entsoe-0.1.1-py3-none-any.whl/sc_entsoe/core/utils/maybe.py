"""Maybe/Option-like utilities for Python."""

from typing import TypeVar

T = TypeVar("T")


def Ptr(v: T) -> T | None:
    """Return a pointer to the value (returns the value itself in Python)."""
    return v


def PtrNilEmpty(v: T) -> T | None:
    """Return None if value is empty/zero, otherwise return the value."""
    if not v:
        return None
    return v


def Value(p: T | None) -> T:
    """Return the value from a pointer, or zero value if None."""
    if p is None:
        return None  # type: ignore
    return p
