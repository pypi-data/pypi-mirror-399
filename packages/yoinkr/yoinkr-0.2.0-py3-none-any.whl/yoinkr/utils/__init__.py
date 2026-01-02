"""
Utility modules for yoinkr.

This package provides supporting utilities for scraping operations:

- **proxy**: Proxy URL builders for Smartproxy, Brightdata, Oxylabs
- **user_agents**: Weighted user agent rotation by market share
- **statistics**: Statistics collection and aggregation
- **retry**: Retry logic with exponential backoff and jitter
- **input**: File-based URL input (txt, csv, json)
- **page**: Playwright page interaction utilities
- **logging**: Structured logging with file rotation

Example:
    >>> from yoinkr.utils import ProxyBuilder, UserAgentSelector
    >>> proxy = ProxyBuilder.smartproxy("user", "pass", country="ZA")
    >>> ua = UserAgentSelector().get_random()
"""

from .input import URLSource
from .logging import LoggingConfig, ScraperLogger, get_logger
from .page import PageUtils
from .proxy import ProxyBuilder, south_africa_proxy
from .retry import RetryConfig, RetryHandler, retry_async, with_retry
from .statistics import ScrapingStatistics, StatisticsCollector
from .user_agents import USER_AGENT_DISTRIBUTION, UserAgentSelector

__all__ = [
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
    "retry_async",
    # Input
    "URLSource",
    # Page Utils
    "PageUtils",
    # Logging
    "LoggingConfig",
    "ScraperLogger",
    "get_logger",
]
