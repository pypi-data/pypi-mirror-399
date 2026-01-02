"""
Circuit breaker pattern implementation for resilient scraping.

This module provides a circuit breaker that prevents cascading failures
by temporarily blocking requests to failing endpoints.

Example:
    >>> breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
    >>> async with breaker.call("https://example.com"):
    ...     result = await fetch_page(url)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from ..utils.logging import get_logger
from .exceptions import CircuitBreakerError

logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Failure threshold exceeded, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitStats:
    """Statistics for a circuit."""

    failures: int = 0
    successes: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    total_requests: int = 0
    total_blocked: int = 0

    def record_failure(self) -> None:
        """Record a failed request."""
        self.failures += 1
        self.total_requests += 1
        self.last_failure_time = time.time()

    def record_success(self) -> None:
        """Record a successful request."""
        self.successes += 1
        self.total_requests += 1
        self.last_success_time = time.time()

    def record_blocked(self) -> None:
        """Record a blocked request."""
        self.total_blocked += 1

    def reset(self) -> None:
        """Reset failure count after recovery."""
        self.failures = 0


@dataclass
class Circuit:
    """Individual circuit for a domain or endpoint."""

    name: str
    failure_threshold: int
    recovery_timeout: float
    half_open_max_calls: int
    state: CircuitState = CircuitState.CLOSED
    stats: CircuitStats = field(default_factory=CircuitStats)
    opened_at: float | None = None
    half_open_calls: int = 0
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def __post_init__(self) -> None:
        """Initialize lock if not already set."""
        if not isinstance(self._lock, asyncio.Lock):
            object.__setattr__(self, "_lock", asyncio.Lock())

    async def can_execute(self) -> bool:
        """Check if a request can be executed."""
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                if self.opened_at and time.time() - self.opened_at >= self.recovery_timeout:
                    self._transition_to_half_open()
                    return True
                return False

            if self.state == CircuitState.HALF_OPEN:
                # Allow limited requests in half-open state
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False

            return False

    async def record_success(self) -> None:
        """Record a successful request."""
        async with self._lock:
            self.stats.record_success()

            if self.state == CircuitState.HALF_OPEN:
                # Service recovered, close the circuit
                self._transition_to_closed()
                logger.info(f"Circuit '{self.name}' recovered and closed")

    async def record_failure(self) -> None:
        """Record a failed request."""
        async with self._lock:
            self.stats.record_failure()

            if self.state == CircuitState.HALF_OPEN:
                # Still failing, reopen circuit
                self._transition_to_open()
                logger.warning(f"Circuit '{self.name}' reopened after failure in half-open state")

            elif self.state == CircuitState.CLOSED:
                if self.stats.failures >= self.failure_threshold:
                    self._transition_to_open()
                    logger.warning(
                        f"Circuit '{self.name}' opened after {self.stats.failures} failures"
                    )

    def _transition_to_open(self) -> None:
        """Transition to open state."""
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        self.half_open_calls = 0

    def _transition_to_half_open(self) -> None:
        """Transition to half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        logger.info(f"Circuit '{self.name}' transitioning to half-open state")

    def _transition_to_closed(self) -> None:
        """Transition to closed state."""
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self.half_open_calls = 0
        self.stats.reset()


class CircuitBreakerContext:
    """Context manager for circuit breaker calls."""

    def __init__(self, circuit: Circuit, breaker: "CircuitBreaker") -> None:
        self.circuit = circuit
        self.breaker = breaker
        self._success = False

    async def __aenter__(self) -> "CircuitBreakerContext":
        """Enter the circuit breaker context."""
        can_execute = await self.circuit.can_execute()
        if not can_execute:
            self.circuit.stats.record_blocked()
            raise CircuitBreakerError(
                f"Circuit '{self.circuit.name}' is {self.circuit.state.value}. "
                f"Retry after {self.breaker.recovery_timeout}s"
            )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the circuit breaker context."""
        if exc_type is None:
            await self.circuit.record_success()
        else:
            # Only count certain exceptions as failures
            if self.breaker.should_count_as_failure(exc_val):
                await self.circuit.record_failure()

    def success(self) -> None:
        """Manually mark the call as successful."""
        self._success = True


class CircuitBreaker:
    """
    Circuit breaker for managing request failures.

    The circuit breaker pattern prevents cascading failures by temporarily
    blocking requests to endpoints that are failing.

    States:
        - CLOSED: Normal operation, all requests allowed
        - OPEN: Failure threshold exceeded, requests blocked
        - HALF_OPEN: Testing if service recovered, limited requests

    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before testing recovery
        half_open_max_calls: Max requests allowed in half-open state
        per_domain: If True, maintain separate circuits per domain
        failure_exceptions: Exception types that count as failures

    Example:
        >>> breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        >>> async with breaker.call("https://example.com"):
        ...     await scraper.fetch(url)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
        per_domain: bool = True,
        failure_exceptions: tuple[type[Exception], ...] | None = None,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.per_domain = per_domain
        self.failure_exceptions = failure_exceptions or (Exception,)
        self._circuits: dict[str, Circuit] = {}
        self._lock = asyncio.Lock()

    def _get_circuit_name(self, url: str) -> str:
        """Get circuit name for URL."""
        if self.per_domain:
            parsed = urlparse(url)
            return parsed.netloc or "default"
        return "default"

    async def _get_circuit(self, url: str) -> Circuit:
        """Get or create circuit for URL."""
        name = self._get_circuit_name(url)

        async with self._lock:
            if name not in self._circuits:
                self._circuits[name] = Circuit(
                    name=name,
                    failure_threshold=self.failure_threshold,
                    recovery_timeout=self.recovery_timeout,
                    half_open_max_calls=self.half_open_max_calls,
                )
                logger.debug(f"Created circuit for '{name}'")

            return self._circuits[name]

    def should_count_as_failure(self, exception: Exception) -> bool:
        """Check if an exception should count as a failure."""
        return isinstance(exception, self.failure_exceptions)

    def call(self, url: str) -> "CircuitBreakerCallable":
        """
        Get a context manager for making a protected call.

        Args:
            url: The URL being requested

        Returns:
            Context manager that tracks success/failure

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return CircuitBreakerCallable(self, url)

    async def get_state(self, url: str) -> CircuitState:
        """Get the current state of a circuit."""
        circuit = await self._get_circuit(url)
        return circuit.state

    async def get_stats(self, url: str) -> CircuitStats:
        """Get statistics for a circuit."""
        circuit = await self._get_circuit(url)
        return circuit.stats

    async def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all circuits."""
        result = {}
        for name, circuit in self._circuits.items():
            result[name] = {
                "state": circuit.state.value,
                "failures": circuit.stats.failures,
                "successes": circuit.stats.successes,
                "total_requests": circuit.stats.total_requests,
                "total_blocked": circuit.stats.total_blocked,
            }
        return result

    async def reset(self, url: str | None = None) -> None:
        """
        Reset circuit(s) to closed state.

        Args:
            url: Specific URL to reset, or None to reset all
        """
        if url:
            name = self._get_circuit_name(url)
            if name in self._circuits:
                circuit = self._circuits[name]
                circuit.state = CircuitState.CLOSED
                circuit.opened_at = None
                circuit.half_open_calls = 0
                circuit.stats.reset()
                logger.info(f"Circuit '{name}' manually reset")
        else:
            for circuit in self._circuits.values():
                circuit.state = CircuitState.CLOSED
                circuit.opened_at = None
                circuit.half_open_calls = 0
                circuit.stats.reset()
            logger.info("All circuits manually reset")


class CircuitBreakerCallable:
    """Awaitable that returns a context manager."""

    def __init__(self, breaker: CircuitBreaker, url: str) -> None:
        self.breaker = breaker
        self.url = url
        self._circuit: Circuit | None = None

    def __await__(self):
        """Allow await to get context manager."""
        return self._get_context().__await__()

    async def _get_context(self) -> CircuitBreakerContext:
        """Get the circuit breaker context."""
        self._circuit = await self.breaker._get_circuit(self.url)
        return CircuitBreakerContext(self._circuit, self.breaker)

    async def __aenter__(self) -> CircuitBreakerContext:
        """Enter as async context manager."""
        ctx = await self._get_context()
        return await ctx.__aenter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit as async context manager."""
        if self._circuit:
            ctx = CircuitBreakerContext(self._circuit, self.breaker)
            await ctx.__aexit__(exc_type, exc_val, exc_tb)
