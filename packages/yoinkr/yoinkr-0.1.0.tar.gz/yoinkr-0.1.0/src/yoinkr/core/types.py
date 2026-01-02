"""Core types for the universal scraper."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Method(str, Enum):
    """Supported extraction methods."""

    CSS = "css"
    XPATH = "xpath"
    REGEX = "regex"
    TEXT = "text"
    META = "meta"
    JSONPATH = "jsonpath"
    ATTR = "attr"
    MULTIATTR = "multiattr"


@dataclass
class Instruction:
    """
    A single extraction instruction.

    Examples:
        Instruction("title", "h1.main-title")
        Instruction("prices", r"\\$[\\d,.]+", method="regex", multiple=True)
        Instruction("links", "//a/@href", method="xpath", multiple=True)
        Instruction("image", "img.product", attribute="src")
    """

    name: str  # Field name in output
    find: str  # What to find (selector/pattern)
    method: Method | str = Method.CSS  # Extraction method

    # Result options
    multiple: bool = False  # Return list vs single value
    attribute: Optional[str] = None  # Extract attribute instead of text
    default: Optional[Any] = None  # Default if not found
    required: bool = False  # Raise error if not found

    # Transformations
    transform: Optional[str] = None  # Transform: lowercase, int, float, clean
    regex_group: Optional[int] = None  # Regex capture group (0 = full match)

    # Nested extraction (for lists of items)
    scope: Optional[str] = None  # CSS selector to scope within
    children: Optional[list["Instruction"]] = None

    # Filtering
    filter: Optional[str] = None  # Regex filter for results
    limit: Optional[int] = None  # Max results

    def __post_init__(self) -> None:
        """Convert string method to Method enum if needed."""
        if isinstance(self.method, str):
            self.method = Method(self.method)


@dataclass
class ScrapeOptions:
    """Options for a scrape operation."""

    # Browser
    javascript: bool = True
    wait_for: Optional[str] = None  # Wait for selector
    wait_timeout: int = 30

    # Request
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    user_agent: Optional[str] = None

    # Proxy
    proxy: Optional[str] = None
    proxy_country: Optional[str] = None

    # Output
    include_html: bool = False
    include_screenshot: bool = False


@dataclass
class ScrapeResult:
    """Result from a scrape operation."""

    url: str
    success: bool
    data: dict[str, Any]

    # Metadata
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    page_title: Optional[str] = None

    # Optional
    html: Optional[str] = None
    screenshot: Optional[bytes] = None

    # Timing
    fetch_time: float = 0.0
    extract_time: float = 0.0
    total_time: float = 0.0

    # Errors (non-fatal)
    errors: list[dict[str, str]] = field(default_factory=list)

    def is_partial(self) -> bool:
        """Check if result has partial data with some errors."""
        return self.success and len(self.errors) > 0

    def get_error_fields(self) -> list[str]:
        """Get list of fields that had extraction errors."""
        return [e.get("field", "") for e in self.errors if "field" in e]
