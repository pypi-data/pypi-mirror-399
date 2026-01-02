"""Retry logic with exponential backoff for HTTP requests."""

import asyncio
import random
from dataclasses import dataclass, field
from functools import wraps
from typing import Awaitable, Callable, TypeVar

import httpx

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_status_codes: set[int] = field(
        default_factory=lambda: {408, 429, 500, 502, 503, 504}
    )


def with_retry(
    config: RetryConfig | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Decorator for async functions that should be retried on failure.

    Args:
        config: Retry configuration. Uses defaults if not provided.

    Returns:
        Decorated function with retry logic.
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: object, **kwargs: object) -> T:
            last_exception: Exception | None = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code not in config.retryable_status_codes:
                        raise  # Non-retryable error
                    last_exception = e

                except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                    last_exception = e

                # Calculate delay with exponential backoff
                if attempt < config.max_attempts:
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay,
                    )

                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        delay = delay * (0.5 + random.random())

                    await asyncio.sleep(delay)

            # All attempts exhausted
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Retry exhausted without exception")

        return wrapper

    return decorator
