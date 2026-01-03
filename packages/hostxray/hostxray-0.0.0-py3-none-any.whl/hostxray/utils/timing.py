from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace
from functools import wraps
from typing import Any


def timed(name: str):
    """Decorator that injects duration_ms into CollectorResult.

    Collector functions must return `(spec, CollectorResult)` where duration_ms is
    initially set to 0; this decorator overwrites it.
    """

    def deco(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            start = time.perf_counter()
            spec, result = fn(*args, **kwargs)
            end = time.perf_counter()
            duration_ms = int((end - start) * 1000)
            return spec, replace(result, duration_ms=duration_ms)

        return wrapper

    return deco
