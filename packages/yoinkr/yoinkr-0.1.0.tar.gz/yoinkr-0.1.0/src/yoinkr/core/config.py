"""
Configuration management with environment variable support and validation.

This module provides:
- Environment variable loading
- Configuration validation
- Default value management
"""

import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlparse

from ..utils.logging import get_logger
from .exceptions import ConfigurationError

logger = get_logger(__name__)


@dataclass
class ScraperConfig:
    """
    Global scraper configuration loaded from environment variables.

    Environment Variables:
        SCRAPER_HEADLESS: Run browser in headless mode (default: true)
        SCRAPER_TIMEOUT: Default timeout in seconds (default: 30)
        SCRAPER_JAVASCRIPT: Enable JavaScript (default: true)
        SCRAPER_USER_AGENT: Custom user agent
        SCRAPER_PROXY: Proxy URL
        SCRAPER_PROXY_USER: Proxy username
        SCRAPER_PROXY_PASS: Proxy password
        SCRAPER_LOG_LEVEL: Logging level (default: INFO)
        SCRAPER_LOG_FILE: Log file path
        SCRAPER_MAX_RETRIES: Maximum retries (default: 3)
        SCRAPER_RETRY_DELAY: Base retry delay in seconds (default: 1.0)
        SCRAPER_RATE_LIMIT: Requests per second limit (default: 0 = unlimited)
        SCRAPER_CONCURRENCY: Max concurrent requests (default: 5)

    Example:
        >>> config = ScraperConfig.from_env()
        >>> print(config.timeout)
    """

    headless: bool = True
    timeout: int = 30
    javascript: bool = True
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_user: Optional[str] = None
    proxy_pass: Optional[str] = None
    log_level: str = "INFO"
    log_file: Optional[str] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: float = 0.0  # 0 = unlimited
    concurrency: int = 5

    @classmethod
    def from_env(cls, prefix: str = "SCRAPER_") -> "ScraperConfig":
        """
        Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix (default: SCRAPER_)

        Returns:
            ScraperConfig instance
        """

        def get_env(name: str, default: Any = None) -> Optional[str]:
            return os.getenv(f"{prefix}{name}", default)

        def get_bool(name: str, default: bool) -> bool:
            value = get_env(name)
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on")

        def get_int(name: str, default: int) -> int:
            value = get_env(name)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                logger.warning(
                    f"Invalid integer for {prefix}{name}: {value}, using default {default}"
                )
                return default

        def get_float(name: str, default: float) -> float:
            value = get_env(name)
            if value is None:
                return default
            try:
                return float(value)
            except ValueError:
                logger.warning(
                    f"Invalid float for {prefix}{name}: {value}, using default {default}"
                )
                return default

        config = cls(
            headless=get_bool("HEADLESS", True),
            timeout=get_int("TIMEOUT", 30),
            javascript=get_bool("JAVASCRIPT", True),
            user_agent=get_env("USER_AGENT"),
            proxy=get_env("PROXY"),
            proxy_user=get_env("PROXY_USER"),
            proxy_pass=get_env("PROXY_PASS"),
            log_level=get_env("LOG_LEVEL", "INFO") or "INFO",
            log_file=get_env("LOG_FILE"),
            max_retries=get_int("MAX_RETRIES", 3),
            retry_delay=get_float("RETRY_DELAY", 1.0),
            rate_limit=get_float("RATE_LIMIT", 0.0),
            concurrency=get_int("CONCURRENCY", 5),
        )

        logger.debug(
            "Configuration loaded from environment",
            extra={
                "headless": config.headless,
                "timeout": config.timeout,
                "javascript": config.javascript,
                "has_proxy": bool(config.proxy),
                "log_level": config.log_level,
            },
        )

        return config

    def validate(self) -> list[str]:
        """
        Validate configuration values.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: list[str] = []

        # Timeout validation
        if self.timeout <= 0:
            errors.append("timeout must be positive")
        if self.timeout > 300:
            errors.append("timeout exceeds maximum (300 seconds)")

        # Retry validation
        if self.max_retries < 0:
            errors.append("max_retries cannot be negative")
        if self.max_retries > 10:
            errors.append("max_retries exceeds maximum (10)")

        if self.retry_delay < 0:
            errors.append("retry_delay cannot be negative")

        # Rate limit validation
        if self.rate_limit < 0:
            errors.append("rate_limit cannot be negative")

        # Concurrency validation
        if self.concurrency <= 0:
            errors.append("concurrency must be positive")
        if self.concurrency > 50:
            errors.append("concurrency exceeds maximum (50)")

        # Proxy validation
        if self.proxy:
            if not self._is_valid_proxy_url(self.proxy):
                errors.append(f"Invalid proxy URL format: {self.proxy}")

        # Log level validation
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if self.log_level.upper() not in valid_levels:
            errors.append(f"Invalid log_level: {self.log_level}. Must be one of {valid_levels}")

        return errors

    def validate_or_raise(self) -> None:
        """
        Validate configuration and raise if invalid.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        errors = self.validate()
        if errors:
            raise ConfigurationError(
                f"Invalid configuration: {'; '.join(errors)}",
                details={"errors": errors},
            )

    def _is_valid_proxy_url(self, url: str) -> bool:
        """Validate proxy URL format."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https", "socks5") and bool(parsed.netloc)
        except Exception:
            return False


class ConfigValidator:
    """
    Validator for browser and scrape configurations.

    Validates BrowserConfig and ScrapeOptions before use.
    """

    # Valid values for various fields
    VALID_BROWSER_TYPES = ("chromium", "firefox", "webkit")
    VALID_LOCALES = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")
    VALID_TIMEZONES = re.compile(r"^[A-Za-z_]+/[A-Za-z_]+$")

    @classmethod
    def validate_browser_config(cls, config: Any) -> list[str]:
        """
        Validate a BrowserConfig.

        Args:
            config: BrowserConfig instance

        Returns:
            List of validation error messages
        """
        errors: list[str] = []

        # Timeout
        if config.timeout <= 0:
            errors.append("timeout must be positive")
        if config.timeout > 300000:  # 5 minutes in ms
            errors.append("timeout exceeds maximum (300000ms)")

        # Browser type
        if config.browser_type not in cls.VALID_BROWSER_TYPES:
            errors.append(f"Invalid browser_type: {config.browser_type}")

        # Viewport
        if config.viewport:
            if config.viewport.get("width", 0) <= 0:
                errors.append("viewport width must be positive")
            if config.viewport.get("height", 0) <= 0:
                errors.append("viewport height must be positive")
            if config.viewport.get("width", 0) > 4096:
                errors.append("viewport width exceeds maximum (4096)")
            if config.viewport.get("height", 0) > 4096:
                errors.append("viewport height exceeds maximum (4096)")

        # Device scale factor
        if config.device_scale_factor <= 0:
            errors.append("device_scale_factor must be positive")
        if config.device_scale_factor > 4:
            errors.append("device_scale_factor exceeds maximum (4)")

        # Locale
        if config.locale and not cls.VALID_LOCALES.match(config.locale):
            errors.append(f"Invalid locale format: {config.locale}")

        # Timezone
        if config.timezone and not cls.VALID_TIMEZONES.match(config.timezone):
            errors.append(f"Invalid timezone format: {config.timezone}")

        # Geolocation
        if config.geolocation:
            lat = config.geolocation.get("latitude", 0)
            lon = config.geolocation.get("longitude", 0)
            if not -90 <= lat <= 90:
                errors.append("geolocation latitude must be between -90 and 90")
            if not -180 <= lon <= 180:
                errors.append("geolocation longitude must be between -180 and 180")

        # Proxy
        if config.proxy:
            try:
                parsed = urlparse(config.proxy)
                if parsed.scheme not in ("http", "https", "socks5"):
                    errors.append(f"Invalid proxy scheme: {parsed.scheme}")
            except Exception:
                errors.append(f"Invalid proxy URL: {config.proxy}")

        return errors

    @classmethod
    def validate_scrape_options(cls, options: Any) -> list[str]:
        """
        Validate ScrapeOptions.

        Args:
            options: ScrapeOptions instance

        Returns:
            List of validation error messages
        """
        errors: list[str] = []

        # Wait timeout
        if options.wait_timeout <= 0:
            errors.append("wait_timeout must be positive")
        if options.wait_timeout > 300:
            errors.append("wait_timeout exceeds maximum (300 seconds)")

        # Wait for selector
        if options.wait_for:
            if not cls._is_valid_selector(options.wait_for):
                errors.append(f"Invalid wait_for selector: {options.wait_for}")

        # Proxy
        if options.proxy:
            try:
                parsed = urlparse(options.proxy)
                if parsed.scheme not in ("http", "https", "socks5"):
                    errors.append(f"Invalid proxy scheme: {parsed.scheme}")
            except Exception:
                errors.append(f"Invalid proxy URL: {options.proxy}")

        # Proxy country
        if options.proxy_country:
            if not re.match(r"^[A-Z]{2}$", options.proxy_country.upper()):
                errors.append(f"Invalid proxy_country: {options.proxy_country}")

        return errors

    @classmethod
    def _is_valid_selector(cls, selector: str) -> bool:
        """Basic CSS selector validation."""
        # Very basic check - not a full CSS parser
        if not selector or not selector.strip():
            return False
        # Check for obviously invalid characters
        if any(c in selector for c in ["\n", "\r", "\0"]):
            return False
        return True


def load_dotenv(path: str = ".env") -> dict[str, str]:
    """
    Load environment variables from a .env file.

    Args:
        path: Path to .env file

    Returns:
        Dictionary of loaded variables
    """
    loaded: dict[str, str] = {}

    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=value
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
                    loaded[key] = value

        logger.debug(f"Loaded {len(loaded)} variables from {path}")
    except FileNotFoundError:
        logger.debug(f".env file not found at {path}")
    except Exception as e:
        logger.warning(f"Error loading .env file: {e}")

    return loaded


# Global configuration instance
_config: Optional[ScraperConfig] = None


def get_config() -> ScraperConfig:
    """
    Get the global configuration, loading from environment if needed.

    Returns:
        ScraperConfig instance
    """
    global _config
    if _config is None:
        _config = ScraperConfig.from_env()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
