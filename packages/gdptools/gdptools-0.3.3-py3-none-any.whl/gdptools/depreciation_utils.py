"""Utilities for managing kwargs deprecation helpers."""

from __future__ import annotations

import functools
import warnings
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def deprecate_kwargs(
    mapping: dict[str, str], *, removed_in: str | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator to rename deprecated keyword arguments.

    Args:
        mapping (dict[str, str]): Map of ``old_param_name -> new_param_name`` to rename.
        removed_in (str | None): Version when the old names will be removed (for documentation).

    Returns:
        Callable: A decorator that wraps a function to rename deprecated keyword
        arguments, emitting a ``DeprecationWarning`` when a rename occurs.

    Raises:
        TypeError: If both an old and its corresponding new keyword are supplied
        to the wrapped function at the same time.

    Notes:
        The wrapper renames any matching deprecated kwargs before calling the
        original function and issues a ``DeprecationWarning`` with guidance.

    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # 1) Rename any old args, emitting a DeprecationWarning
            for old, new in mapping.items():
                if old in kwargs:
                    if new in kwargs:
                        raise TypeError(f"{func.__qualname__} received both '{old}' and '{new}'")
                    msg = (
                        f"'{old}' is deprecated"
                        + (f" and will be removed in {removed_in}" if removed_in else "")
                        + f"; use '{new}' instead"
                    )
                    warnings.warn(msg, DeprecationWarning, stacklevel=2)
                    kwargs[new] = kwargs.pop(old)
            # 2) Call the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
