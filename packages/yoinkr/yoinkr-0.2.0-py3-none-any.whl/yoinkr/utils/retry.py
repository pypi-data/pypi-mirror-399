"""Retry logic with exponential backoff."""

import asyncio
import random
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: tuple[float, float] = (0.0, 0.5),
        retry_on: tuple[type[Exception], ...] = (Exception,),
        retry_if: Optional[Callable[[Exception], bool]] = None,
    ) -> None:
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Random jitter range (min, max) as fraction
            retry_on: Tuple of exception types to retry on
            retry_if: Optional function to decide if should retry
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on = retry_on
        self.retry_if = retry_if

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for attempt with exponential backoff and jitter.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = min(
            self.base_delay * (self.exponential_base**attempt),
            self.max_delay,
        )

        # Add jitter
        jitter = random.uniform(*self.jitter)
        delay = delay * (1 + jitter)

        return delay

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if we should retry.

        Args:
            exception: The exception that was raised
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False

        if not isinstance(exception, self.retry_on):
            return False

        if self.retry_if and not self.retry_if(exception):
            return False

        return True


def with_retry(config: Optional[RetryConfig] = None) -> Callable[[F], F]:
    """
    Decorator for retry logic.

    Args:
        config: Optional retry configuration

    Returns:
        Decorated function
    """
    config = config or RetryConfig()

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if not config.should_retry(e, attempt):
                        raise

                    delay = config.get_delay(attempt)
                    await asyncio.sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper  # type: ignore

    return decorator


class RetryHandler:
    """Handler for managing retries."""

    def __init__(self, config: Optional[RetryConfig] = None) -> None:
        """
        Initialize the handler.

        Args:
            config: Optional retry configuration
        """
        self.config = config or RetryConfig()

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if not self.config.should_retry(e, attempt):
                    raise

                delay = self.config.get_delay(attempt)
                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception


async def retry_async(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs: Any,
) -> Any:
    """
    Simple async retry helper.

    Args:
        func: Async function to retry
        *args: Positional arguments
        max_retries: Maximum retries
        base_delay: Base delay between retries
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    config = RetryConfig(max_retries=max_retries, base_delay=base_delay)
    handler = RetryHandler(config)
    return await handler.execute(func, *args, **kwargs)
