"""
Custom exceptions for the universal scraper.

This module defines a hierarchy of exceptions for handling errors:

- ScraperError: Base exception for all scraper errors
- FetchError: Errors during page fetching (network, HTTP errors)
- ExtractionError: Errors during data extraction
- ValidationError: Errors during data validation
- BrowserError: Browser-related errors (launch, crash)
- ConfigurationError: Invalid configuration
- SecurityError: Security-related errors (injection, unsafe URLs)
- RateLimitError: Rate limiting errors
- TimeoutError: Timeout during operations

Example:
    >>> try:
    ...     result = await scraper.extract(url, instructions)
    ... except FetchError as e:
    ...     print(f"Failed to fetch {e.url}: {e.status_code}")
    ... except ExtractionError as e:
    ...     print(f"Failed to extract {e.field}: {e.message}")
"""

from typing import Any, Optional


class ScraperError(Exception):
    """Base exception for all scraper errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class FetchError(ScraperError):
    """Error during page fetching."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.url = url
        self.status_code = status_code


class ExtractionError(ScraperError):
    """Error during data extraction."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        method: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.field = field
        self.method = method


class ValidationError(ScraperError):
    """Error during data validation."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.field = field
        self.value = value


class BrowserError(ScraperError):
    """Error related to browser operations."""

    pass


class ConfigurationError(ScraperError):
    """Error in configuration values."""

    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        value: Any = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.parameter = parameter
        self.value = value


class SecurityError(ScraperError):
    """Security-related error (injection, unsafe input)."""

    def __init__(
        self,
        message: str,
        input_type: Optional[str] = None,
        value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.input_type = input_type
        self.value = value


class RateLimitError(ScraperError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str,
        domain: Optional[str] = None,
        retry_after: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.domain = domain
        self.retry_after = retry_after


class CircuitBreakerError(ScraperError):
    """Circuit breaker is open, requests blocked."""

    def __init__(
        self,
        message: str,
        domain: Optional[str] = None,
        reset_at: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.domain = domain
        self.reset_at = reset_at


class TimeoutError(ScraperError):
    """Timeout during scraping operations."""

    def __init__(
        self,
        message: str,
        timeout: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.timeout = timeout
