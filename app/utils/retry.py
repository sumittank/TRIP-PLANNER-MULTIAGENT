"""Retry utilities for external API calls."""

import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


def retry_call(
    func: Callable[[], T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> T:
    last_error: Exception | None = None
    wait = delay
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as exc:
            last_error = exc
            logger.warning("Attempt %s/%s failed: %s", attempt, max_retries, exc)
            if attempt < max_retries:
                time.sleep(wait)
                wait *= backoff
    raise last_error  # type: ignore[misc]
