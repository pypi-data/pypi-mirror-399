"""Retry logic with exponential backoff"""

import asyncio
import time
from typing import Awaitable, Callable, Optional, TypeVar

from .exceptions import AuditTrailApiError

T = TypeVar("T")


async def with_retry(
    fn: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    delay: float = 1.0,
) -> T:
    """Execute async function with retry and exponential backoff"""
    last_error: Optional[Exception] = None

    for attempt in range(max_attempts):
        try:
            return await fn()
        except AuditTrailApiError as e:
            # Don't retry on 4xx client errors
            if 400 <= e.status_code < 500:
                raise
            last_error = e
        except Exception as e:
            last_error = e

        # Wait before retry with exponential backoff
        if attempt < max_attempts - 1:
            wait_time = delay * (2**attempt)
            await asyncio.sleep(wait_time)

    raise last_error or AuditTrailApiError("Unknown error", 500)


def with_retry_sync(
    fn: Callable[[], T],
    max_attempts: int = 3,
    delay: float = 1.0,
) -> T:
    """Execute sync function with retry and exponential backoff"""
    last_error: Optional[Exception] = None

    for attempt in range(max_attempts):
        try:
            return fn()
        except AuditTrailApiError as e:
            if 400 <= e.status_code < 500:
                raise
            last_error = e
        except Exception as e:
            last_error = e

        if attempt < max_attempts - 1:
            wait_time = delay * (2**attempt)
            time.sleep(wait_time)

    raise last_error or AuditTrailApiError("Unknown error", 500)
