"""
Rate limiter with token bucket algorithm.

Provides rate limiting for scraping operations to prevent
overwhelming target servers and getting blocked.
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

from ..utils.logging import get_logger
from .exceptions import RateLimitError

logger = get_logger(__name__)


@dataclass
class RateLimiterConfig:
    """Configuration for rate limiting."""

    requests_per_second: float = 1.0  # Max requests per second
    burst_size: int = 5  # Max burst of requests
    per_domain: bool = True  # Apply limits per domain
    block_on_limit: bool = False  # Raise error vs wait


class TokenBucket:
    """
    Token bucket rate limiter.

    Allows bursts up to bucket size, then limits to fill rate.
    """

    def __init__(
        self,
        fill_rate: float,
        capacity: int,
    ) -> None:
        """
        Initialize the token bucket.

        Args:
            fill_rate: Tokens added per second
            capacity: Maximum tokens (burst size)
        """
        self.fill_rate = fill_rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, waiting if necessary.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Time waited in seconds
        """
        async with self._lock:
            waited = 0.0

            while True:
                self._refill()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return waited

                # Calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.fill_rate

                await asyncio.sleep(wait_time)
                waited += wait_time

    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without waiting.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if acquired, False otherwise
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
        self.last_update = now

    @property
    def available_tokens(self) -> float:
        """Get current available tokens."""
        self._refill()
        return self.tokens


class RateLimiter:
    """
    Rate limiter for scraping operations.

    Supports:
    - Global rate limiting
    - Per-domain rate limiting
    - Token bucket algorithm with bursts
    - Async operation

    Example:
        >>> limiter = RateLimiter(requests_per_second=2.0)
        >>> async with limiter.acquire("https://example.com"):
        ...     # Make request
        ...     pass
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: int = 5,
        per_domain: bool = True,
        block_on_limit: bool = False,
    ) -> None:
        """
        Initialize the rate limiter.

        Args:
            requests_per_second: Maximum requests per second
            burst_size: Maximum burst of requests
            per_domain: Apply limits per domain (vs global)
            block_on_limit: Raise RateLimitError instead of waiting
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.per_domain = per_domain
        self.block_on_limit = block_on_limit

        self._global_bucket = TokenBucket(requests_per_second, burst_size)
        self._domain_buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(requests_per_second, burst_size)
        )
        self._lock = asyncio.Lock()

        logger.debug(
            f"Rate limiter initialized: {requests_per_second}/s, burst={burst_size}, per_domain={per_domain}"
        )

    async def acquire(self, url: str) -> "RateLimitContext":
        """
        Acquire permission to make a request.

        Args:
            url: URL being requested

        Returns:
            RateLimitContext for use with async with

        Raises:
            RateLimitError: If block_on_limit is True and limit exceeded
        """
        return RateLimitContext(self, url)

    async def wait(self, url: str) -> float:
        """
        Wait for rate limit and return time waited.

        Args:
            url: URL being requested

        Returns:
            Time waited in seconds

        Raises:
            RateLimitError: If block_on_limit is True and limit exceeded
        """
        domain = self._extract_domain(url) if self.per_domain else "global"

        if self.block_on_limit:
            bucket = self._get_bucket(domain)
            if not bucket.try_acquire():
                retry_after = 1.0 / self.requests_per_second
                raise RateLimitError(
                    f"Rate limit exceeded for {domain}",
                    domain=domain,
                    retry_after=retry_after,
                )
            return 0.0

        # Wait for token
        bucket = self._get_bucket(domain)
        waited = await bucket.acquire()

        if waited > 0:
            logger.debug(f"Rate limited: waited {waited:.2f}s for {domain}")

        return waited

    def _get_bucket(self, domain: str) -> TokenBucket:
        """Get the token bucket for a domain."""
        if self.per_domain:
            return self._domain_buckets[domain]
        return self._global_bucket

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc or "unknown"
        except Exception:
            return "unknown"

    def get_stats(self) -> dict[str, any]:
        """Get rate limiter statistics."""
        return {
            "requests_per_second": self.requests_per_second,
            "burst_size": self.burst_size,
            "per_domain": self.per_domain,
            "global_tokens": self._global_bucket.available_tokens,
            "domain_count": len(self._domain_buckets),
        }

    def reset(self) -> None:
        """Reset all rate limits."""
        self._global_bucket = TokenBucket(self.requests_per_second, self.burst_size)
        self._domain_buckets.clear()
        logger.debug("Rate limiter reset")


class RateLimitContext:
    """Async context manager for rate limiting."""

    def __init__(self, limiter: RateLimiter, url: str) -> None:
        self.limiter = limiter
        self.url = url
        self.waited = 0.0

    async def __aenter__(self) -> "RateLimitContext":
        self.waited = await self.limiter.wait(self.url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass


# Convenience function
async def rate_limit(
    url: str,
    requests_per_second: float = 1.0,
    _limiter: Optional[RateLimiter] = None,
) -> float:
    """
    Simple rate limiting function.

    Args:
        url: URL being requested
        requests_per_second: Rate limit
        _limiter: Optional existing limiter

    Returns:
        Time waited in seconds
    """
    if _limiter is None:
        _limiter = RateLimiter(requests_per_second=requests_per_second)

    return await _limiter.wait(url)
