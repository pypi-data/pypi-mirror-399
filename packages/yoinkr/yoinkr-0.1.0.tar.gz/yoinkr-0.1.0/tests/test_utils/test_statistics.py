"""Tests for statistics utilities."""

from datetime import datetime, timedelta

import pytest

from yoinkr.core.types import ScrapeResult
from yoinkr.utils.statistics import ScrapingStatistics, StatisticsCollector


class TestScrapingStatistics:
    """Tests for ScrapingStatistics."""

    def test_default_values(self):
        """Test default statistics values."""
        stats = ScrapingStatistics()
        assert stats.total_urls == 0
        assert stats.successful == 0
        assert stats.failed == 0

    def test_success_rate_empty(self):
        """Test success rate with no URLs."""
        stats = ScrapingStatistics()
        assert stats.success_rate == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = ScrapingStatistics(total_urls=10, successful=8, failed=2)
        assert stats.success_rate == 80.0

    def test_avg_times_empty(self):
        """Test average times with no data."""
        stats = ScrapingStatistics()
        assert stats.avg_fetch_time == 0.0
        assert stats.avg_extract_time == 0.0
        assert stats.avg_total_time == 0.0

    def test_avg_times_calculation(self):
        """Test average time calculations."""
        stats = ScrapingStatistics(
            fetch_times=[1.0, 2.0, 3.0],
            extract_times=[0.1, 0.2, 0.3],
            total_times=[1.1, 2.2, 3.3],
        )
        assert stats.avg_fetch_time == 2.0
        assert stats.avg_extract_time == 0.2
        assert stats.avg_total_time == 2.2

    def test_total_duration(self):
        """Test total duration calculation."""
        now = datetime.now()
        stats = ScrapingStatistics(
            start_time=now,
            end_time=now + timedelta(seconds=60),
        )
        assert stats.total_duration == 60.0

    def test_urls_per_minute(self):
        """Test URLs per minute calculation."""
        now = datetime.now()
        stats = ScrapingStatistics(
            total_urls=120,
            start_time=now,
            end_time=now + timedelta(seconds=60),
        )
        assert stats.urls_per_minute == 120.0


class TestStatisticsCollector:
    """Tests for StatisticsCollector."""

    @pytest.fixture
    def collector(self):
        return StatisticsCollector()

    def test_start_end(self, collector):
        """Test start and end marking."""
        collector.start()
        assert collector.stats.start_time is not None

        collector.end()
        assert collector.stats.end_time is not None

    def test_record_successful_result(self, collector):
        """Test recording successful result."""
        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={"title": "Test"},
            fetch_time=1.5,
            extract_time=0.1,
            total_time=1.6,
            html="<html>...</html>",
        )

        collector.record_result(result)

        assert collector.stats.total_urls == 1
        assert collector.stats.successful == 1
        assert collector.stats.failed == 0
        assert 1.5 in collector.stats.fetch_times

    def test_record_failed_result(self, collector):
        """Test recording failed result."""
        result = ScrapeResult(
            url="https://example.com",
            success=False,
            data={},
            errors=[{"error": "Connection timeout"}],
        )

        collector.record_result(result)

        assert collector.stats.total_urls == 1
        assert collector.stats.successful == 0
        assert collector.stats.failed == 1
        assert "Connection timeout" in collector.stats.error_counts

    def test_count_items(self, collector):
        """Test item counting."""
        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={
                "title": "Test",
                "prices": [1, 2, 3],
                "nested": {"a": 1, "b": 2},
            },
        )

        collector.record_result(result)

        # 1 (title) + 3 (prices list) + 2 (nested values)
        assert collector.stats.items_extracted == 6

    def test_get_summary(self, collector):
        """Test getting summary."""
        collector.start()

        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={"title": "Test"},
            fetch_time=1.0,
            extract_time=0.1,
            total_time=1.1,
        )
        collector.record_result(result)

        collector.end()

        summary = collector.get_summary()

        assert summary["total_urls"] == 1
        assert summary["successful"] == 1
        assert "100.0%" in summary["success_rate"]

    def test_reset(self, collector):
        """Test reset functionality."""
        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={},
        )
        collector.record_result(result)

        assert collector.stats.total_urls == 1

        collector.reset()

        assert collector.stats.total_urls == 0
