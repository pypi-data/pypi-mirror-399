"""
Core components of the yoinkr library.

This module contains the fundamental building blocks for web scraping:

- **Scraper**: Main entry point for scraping operations
- **Fetcher**: Browser-based page fetching with Playwright
- **Extractor**: Extraction pipeline with method registry
- **Types**: Core data structures (Instruction, ScrapeResult, ScrapeOptions)
- **Validation**: Field validation system
- **BrowserConfig**: Browser configuration with presets
- **Exceptions**: Custom exception hierarchy

Example:
    >>> from yoinkr.core import Scraper, Instruction
    >>> async with Scraper() as scraper:
    ...     result = await scraper.extract(
    ...         url="https://example.com",
    ...         instructions=[Instruction("title", "h1")]
    ...     )
"""

from .browser_config import (
    DESKTOP_CONFIG,
    FAST_CONFIG,
    MOBILE_CONFIG,
    STEALTH_CONFIG,
    BrowserConfig,
)
from .exceptions import (
    BrowserError,
    ConfigurationError,
    ExtractionError,
    FetchError,
    RateLimitError,
    ScraperError,
    SecurityError,
    ValidationError,
)
from .extractor import Extractor, MethodRegistry
from .scraper import Scraper
from .types import Instruction, Method, ScrapeOptions, ScrapeResult
from .validation import (
    FieldValidator,
    ListFieldValidator,
    NumericFieldValidator,
    PatternFieldValidator,
    TextFieldValidator,
    ValidationConfig,
    ValidationResult,
    ValidationService,
)

__all__ = [
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
    # Browser Config
    "BrowserConfig",
    "DESKTOP_CONFIG",
    "MOBILE_CONFIG",
    "FAST_CONFIG",
    "STEALTH_CONFIG",
    # Validation
    "ValidationConfig",
    "ValidationResult",
    "ValidationService",
    "FieldValidator",
    "TextFieldValidator",
    "NumericFieldValidator",
    "PatternFieldValidator",
    "ListFieldValidator",
]
