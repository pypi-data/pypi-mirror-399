"""
Yoinkr - A universal web scraping library for Python and Django.

A production-ready web scraping library with support for multiple extraction
methods, browser automation, rate limiting, circuit breakers, and more.

Usage:
    from yoinkr import Scraper, Instruction

    async with Scraper() as scraper:
        result = await scraper.extract(
            url="https://example.com",
            instructions=[
                Instruction("title", "h1"),
                Instruction("links", "a", attribute="href", multiple=True),
            ]
        )

    print(result.data)

Modules:
    core: Core scraping functionality (Scraper, Extractor, types)
    utils: Utility modules (proxy, logging, retry, statistics)
    django: Django integration (models, admin, tasks)
"""

# Core
from .core.browser_config import (
    DESKTOP_CONFIG,
    FAST_CONFIG,
    MOBILE_CONFIG,
    STEALTH_CONFIG,
    BrowserConfig,
)
from .core.circuit_breaker import (
    Circuit,
    CircuitBreaker,
    CircuitState,
    CircuitStats,
)
from .core.config import (
    ConfigValidator,
    ScraperConfig,
    load_dotenv,
)
from .core.exceptions import (
    BrowserError,
    CircuitBreakerError,
    ConfigurationError,
    ExtractionError,
    FetchError,
    RateLimitError,
    ScraperError,
    SecurityError,
    ValidationError,
)
from .core.extractor import Extractor, MethodRegistry
from .core.health import (
    HealthChecker,
    HealthCheckResult,
    HealthReport,
    HealthStatus,
)
from .core.rate_limiter import (
    RateLimiter,
    TokenBucket,
)
from .core.scraper import Scraper
from .core.security import (
    SecurityConfig,
    SecurityValidator,
    sanitize_output,
    validate_proxy_url,
)
from .core.types import Instruction, Method, ScrapeOptions, ScrapeResult
from .core.validation import (
    FieldValidator,
    ListFieldValidator,
    NumericFieldValidator,
    PatternFieldValidator,
    TextFieldValidator,
    ValidationConfig,
    ValidationResult,
    ValidationService,
)
from .utils.input import URLSource
from .utils.logging import LoggingConfig, ScraperLogger, get_logger
from .utils.page import PageUtils

# Utilities
from .utils.proxy import ProxyBuilder, south_africa_proxy
from .utils.retry import RetryConfig, RetryHandler, with_retry
from .utils.statistics import ScrapingStatistics, StatisticsCollector
from .utils.user_agents import USER_AGENT_DISTRIBUTION, UserAgentSelector

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Main
    "Scraper",
    "Instruction",
    "Method",
    # Types
    "ScrapeOptions",
    "ScrapeResult",
    # Extraction
    "Extractor",
    "MethodRegistry",
    # Exceptions
    "ScraperError",
    "ExtractionError",
    "FetchError",
    "BrowserError",
    "ValidationError",
    "ConfigurationError",
    "SecurityError",
    "RateLimitError",
    "CircuitBreakerError",
    # Browser Config
    "BrowserConfig",
    "DESKTOP_CONFIG",
    "MOBILE_CONFIG",
    "FAST_CONFIG",
    "STEALTH_CONFIG",
    # Configuration
    "ScraperConfig",
    "ConfigValidator",
    "load_dotenv",
    # Health Checks
    "HealthChecker",
    "HealthCheckResult",
    "HealthReport",
    "HealthStatus",
    # Rate Limiting
    "RateLimiter",
    "TokenBucket",
    # Circuit Breaker
    "CircuitBreaker",
    "Circuit",
    "CircuitState",
    "CircuitStats",
    # Security
    "SecurityValidator",
    "SecurityConfig",
    "sanitize_output",
    "validate_proxy_url",
    # Validation
    "ValidationConfig",
    "ValidationResult",
    "ValidationService",
    "FieldValidator",
    "TextFieldValidator",
    "NumericFieldValidator",
    "PatternFieldValidator",
    "ListFieldValidator",
    # Proxy
    "ProxyBuilder",
    "south_africa_proxy",
    # User Agents
    "UserAgentSelector",
    "USER_AGENT_DISTRIBUTION",
    # Statistics
    "StatisticsCollector",
    "ScrapingStatistics",
    # Retry
    "RetryConfig",
    "RetryHandler",
    "with_retry",
    # Input
    "URLSource",
    # Page Utils
    "PageUtils",
    # Logging
    "LoggingConfig",
    "ScraperLogger",
    "get_logger",
]
