"""Tests for the Fetcher."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yoinkr.core.browser_config import (
    DESKTOP_CONFIG,
    FAST_CONFIG,
    MOBILE_CONFIG,
    STEALTH_CONFIG,
    BrowserConfig,
)
from yoinkr.core.fetcher import Fetcher


class TestBrowserConfig:
    """Tests for BrowserConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = BrowserConfig()
        assert config.headless is True
        assert config.browser_type == "chromium"
        assert config.timeout == 30000
        assert config.javascript_enabled is True

    def test_to_playwright_args(self):
        """Test converting to Playwright launch args."""
        config = BrowserConfig(
            headless=False,
            proxy="http://proxy.example.com:8080",
            proxy_username="user",
            proxy_password="pass",
        )
        args = config.to_playwright_args()

        assert args["headless"] is False
        assert args["proxy"]["server"] == "http://proxy.example.com:8080"
        assert args["proxy"]["username"] == "user"
        assert args["proxy"]["password"] == "pass"

    def test_to_context_args(self):
        """Test converting to Playwright context args."""
        config = BrowserConfig(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone="America/New_York",
            user_agent="Custom UA",
        )
        args = config.to_context_args()

        assert args["viewport"] == {"width": 1920, "height": 1080}
        assert args["locale"] == "en-US"
        assert args["timezone_id"] == "America/New_York"
        assert args["user_agent"] == "Custom UA"

    def test_desktop_config(self):
        """Test desktop preset configuration."""
        assert DESKTOP_CONFIG.viewport == {"width": 1920, "height": 1080}
        assert DESKTOP_CONFIG.locale == "en-US"

    def test_mobile_config(self):
        """Test mobile preset configuration."""
        assert MOBILE_CONFIG.is_mobile is True
        assert MOBILE_CONFIG.has_touch is True
        assert MOBILE_CONFIG.viewport == {"width": 390, "height": 844}

    def test_fast_config(self):
        """Test fast preset configuration."""
        assert FAST_CONFIG.resource_blocking is True
        assert FAST_CONFIG.javascript_enabled is False
        assert "image" in FAST_CONFIG.blocked_resource_types

    def test_stealth_config(self):
        """Test stealth preset configuration."""
        assert STEALTH_CONFIG.randomize_user_agent is True
        assert STEALTH_CONFIG.locale == "en-US"
        assert STEALTH_CONFIG.timezone == "America/New_York"


class TestFetcher:
    """Tests for Fetcher (mocked)."""

    def test_fetcher_init_defaults(self):
        """Test fetcher initialization with defaults."""
        fetcher = Fetcher()
        assert fetcher._config.headless is True
        assert fetcher._config.javascript_enabled is True
        assert fetcher._started is False

    def test_fetcher_init_with_config(self):
        """Test fetcher initialization with BrowserConfig."""
        config = BrowserConfig(headless=False, timeout=60000)
        fetcher = Fetcher(config=config)
        assert fetcher._config.headless is False
        assert fetcher._config.timeout == 60000

    def test_fetcher_init_with_options(self):
        """Test fetcher initialization with individual options."""
        fetcher = Fetcher(
            headless=False,
            javascript=False,
            timeout=60,
            proxy="http://proxy.example.com:8080",
            user_agent="Custom UA",
        )
        assert fetcher._config.headless is False
        assert fetcher._config.javascript_enabled is False
        assert fetcher._config.timeout == 60000  # Converted to ms
        assert fetcher._config.proxy == "http://proxy.example.com:8080"
        assert fetcher._config.user_agent == "Custom UA"


class TestFetcherIntegration:
    """Integration tests for Fetcher (requires Playwright)."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Playwright installation")
    async def test_fetch_real_page(self):
        """Test fetching a real page."""
        async with Fetcher() as fetcher:
            result = await fetcher.fetch("https://example.com")

            assert result["status_code"] == 200
            assert "Example Domain" in result["html"]
            assert result["title"] == "Example Domain"
            assert result["final_url"] == "https://example.com/"

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Playwright installation")
    async def test_fetch_with_screenshot(self):
        """Test fetching with screenshot."""
        async with Fetcher() as fetcher:
            result = await fetcher.fetch("https://example.com", screenshot=True)

            assert result["screenshot"] is not None
            assert len(result["screenshot"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Playwright installation")
    async def test_fetch_simple(self):
        """Test simple fetch."""
        async with Fetcher() as fetcher:
            html = await fetcher.fetch_simple("https://example.com")

            assert "Example Domain" in html
