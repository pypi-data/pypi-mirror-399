"""Tests for the main Scraper class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yoinkr.core.scraper import Scraper
from yoinkr.core.types import Instruction, ScrapeOptions, ScrapeResult


class TestScraperInit:
    """Tests for Scraper initialization."""

    def test_default_init(self):
        """Test default initialization."""
        scraper = Scraper()
        assert scraper._headless is True
        assert scraper._javascript is True
        assert scraper._timeout == 30
        assert scraper._started is False

    def test_init_with_options(self):
        """Test initialization with options."""
        scraper = Scraper(
            headless=False,
            javascript=False,
            timeout=60,
            proxy="http://proxy.example.com:8080",
            user_agent="Custom UA",
        )
        assert scraper._headless is False
        assert scraper._javascript is False
        assert scraper._timeout == 60
        assert scraper._proxy == "http://proxy.example.com:8080"
        assert scraper._user_agent == "Custom UA"

    def test_is_started_property(self):
        """Test is_started property."""
        scraper = Scraper()
        assert scraper.is_started is False


class TestScraperMocked:
    """Tests for Scraper with mocked Fetcher."""

    @pytest.fixture
    def mock_fetcher(self):
        """Create a mock fetcher."""
        fetcher = AsyncMock()
        fetcher.start = AsyncMock()
        fetcher.stop = AsyncMock()
        fetcher.fetch = AsyncMock(
            return_value={
                "html": "<html><h1>Test</h1><p class='price'>$29.99</p></html>",
                "status_code": 200,
                "final_url": "https://example.com",
                "title": "Test Page",
                "screenshot": None,
            }
        )
        return fetcher

    @pytest.mark.asyncio
    async def test_extract_basic(self, mock_fetcher):
        """Test basic extraction."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                result = await scraper.extract(
                    url="https://example.com",
                    instructions=[
                        Instruction("title", "h1"),
                        Instruction("price", ".price"),
                    ],
                )

                assert result.success is True
                assert result.data["title"] == "Test"
                assert result.data["price"] == "$29.99"
                assert result.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_extract_with_transform(self, mock_fetcher):
        """Test extraction with transform."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                result = await scraper.extract(
                    url="https://example.com",
                    instructions=[
                        Instruction("price", ".price", transform="float"),
                    ],
                )

                assert result.data["price"] == 29.99

    @pytest.mark.asyncio
    async def test_extract_with_options(self, mock_fetcher):
        """Test extraction with options."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                options = ScrapeOptions(
                    wait_for=".loaded",
                    headers={"X-Custom": "value"},
                    include_html=True,
                )
                result = await scraper.extract(
                    url="https://example.com",
                    instructions=[Instruction("title", "h1")],
                    options=options,
                )

                assert result.success is True
                assert result.html is not None
                mock_fetcher.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_timing(self, mock_fetcher):
        """Test that timing is recorded."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                result = await scraper.extract(
                    url="https://example.com",
                    instructions=[Instruction("title", "h1")],
                )

                assert result.fetch_time >= 0
                assert result.extract_time >= 0
                assert result.total_time >= 0

    @pytest.mark.asyncio
    async def test_extract_callback(self, mock_fetcher):
        """Test on_result callback."""
        callback_results = []

        async def on_result(result: ScrapeResult):
            callback_results.append(result)

        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper(on_result=on_result) as scraper:
                await scraper.extract(
                    url="https://example.com",
                    instructions=[Instruction("title", "h1")],
                )

                assert len(callback_results) == 1
                assert callback_results[0].success is True

    @pytest.mark.asyncio
    async def test_extract_many(self, mock_fetcher):
        """Test extracting from multiple URLs."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                urls = [
                    "https://example.com/1",
                    "https://example.com/2",
                    "https://example.com/3",
                ]
                results = await scraper.extract_many(
                    urls=urls,
                    instructions=[Instruction("title", "h1")],
                    concurrency=2,
                )

                assert len(results) == 3
                assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_extract_many_with_delay(self, mock_fetcher):
        """Test extracting with delay between requests."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                urls = ["https://example.com/1", "https://example.com/2"]
                results = await scraper.extract_many(
                    urls=urls,
                    instructions=[Instruction("title", "h1")],
                    delay=(0.01, 0.02),  # Short delay for testing
                )

                assert len(results) == 2

    @pytest.mark.asyncio
    async def test_extract_error_handling(self, mock_fetcher):
        """Test error handling during extraction."""
        mock_fetcher.fetch = AsyncMock(side_effect=Exception("Network error"))

        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                result = await scraper.extract(
                    url="https://example.com",
                    instructions=[Instruction("title", "h1")],
                )

                assert result.success is False
                assert len(result.errors) > 0
                assert "Network error" in result.errors[0]["error"]

    @pytest.mark.asyncio
    async def test_scraper_not_started_raises(self):
        """Test that extracting without starting raises error."""
        scraper = Scraper()

        with pytest.raises(RuntimeError, match="not started"):
            await scraper.extract(
                url="https://example.com",
                instructions=[Instruction("title", "h1")],
            )

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_fetcher):
        """Test async context manager."""
        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper() as scraper:
                assert scraper.is_started is True

            # After exiting, should be stopped
            assert scraper.is_started is False
            mock_fetcher.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_callback(self, mock_fetcher):
        """Test synchronous callback."""
        callback_results = []

        def on_result(result: ScrapeResult):
            callback_results.append(result)

        with patch("yoinkr.core.scraper.Fetcher", return_value=mock_fetcher):
            async with Scraper(on_result=on_result) as scraper:
                await scraper.extract(
                    url="https://example.com",
                    instructions=[Instruction("title", "h1")],
                )

                assert len(callback_results) == 1
