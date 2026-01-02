"""Statistics collection and aggregation."""

import statistics as stats
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..core.types import ScrapeResult


@dataclass
class ScrapingStatistics:
    """Statistics for a scraping session."""

    total_urls: int = 0
    successful: int = 0
    failed: int = 0

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    fetch_times: list[float] = field(default_factory=list)
    extract_times: list[float] = field(default_factory=list)
    total_times: list[float] = field(default_factory=list)

    # Data
    items_extracted: int = 0
    bytes_processed: int = 0

    # Errors
    error_counts: dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_urls == 0:
            return 0.0
        return (self.successful / self.total_urls) * 100

    @property
    def avg_fetch_time(self) -> float:
        """Calculate average fetch time."""
        return stats.mean(self.fetch_times) if self.fetch_times else 0.0

    @property
    def avg_extract_time(self) -> float:
        """Calculate average extraction time."""
        return stats.mean(self.extract_times) if self.extract_times else 0.0

    @property
    def avg_total_time(self) -> float:
        """Calculate average total time."""
        return stats.mean(self.total_times) if self.total_times else 0.0

    @property
    def total_duration(self) -> float:
        """Calculate total session duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def urls_per_minute(self) -> float:
        """Calculate throughput in URLs per minute."""
        if self.total_duration > 0:
            return (self.total_urls / self.total_duration) * 60
        return 0.0


class StatisticsCollector:
    """Collects and aggregates scraping statistics."""

    def __init__(self) -> None:
        """Initialize the collector."""
        self.stats = ScrapingStatistics()

    def start(self) -> None:
        """Mark session start."""
        self.stats.start_time = datetime.now()

    def end(self) -> None:
        """Mark session end."""
        self.stats.end_time = datetime.now()

    def record_result(self, result: "ScrapeResult") -> None:
        """
        Record a single scrape result.

        Args:
            result: ScrapeResult to record
        """
        self.stats.total_urls += 1

        if result.success:
            self.stats.successful += 1
        else:
            self.stats.failed += 1

            # Track error types
            for error in result.errors:
                error_type = error.get("error", "Unknown")[:50]
                self.stats.error_counts[error_type] = self.stats.error_counts.get(error_type, 0) + 1

        # Timing
        if result.fetch_time:
            self.stats.fetch_times.append(result.fetch_time)
        if result.extract_time:
            self.stats.extract_times.append(result.extract_time)
        if result.total_time:
            self.stats.total_times.append(result.total_time)

        # Data volume
        if result.html:
            self.stats.bytes_processed += len(result.html.encode("utf-8"))

        # Count extracted items
        self._count_items(result.data)

    def _count_items(self, data: dict[str, Any], depth: int = 0) -> None:
        """Recursively count extracted items."""
        for value in data.values():
            if isinstance(value, list):
                self.stats.items_extracted += len(value)
            elif isinstance(value, dict):
                self._count_items(value, depth + 1)
            elif value is not None:
                self.stats.items_extracted += 1

    def get_summary(self) -> dict[str, Any]:
        """
        Get statistics summary.

        Returns:
            Dictionary with formatted statistics
        """
        return {
            "total_urls": self.stats.total_urls,
            "successful": self.stats.successful,
            "failed": self.stats.failed,
            "success_rate": f"{self.stats.success_rate:.1f}%",
            "items_extracted": self.stats.items_extracted,
            "bytes_processed": self.stats.bytes_processed,
            "avg_fetch_time": f"{self.stats.avg_fetch_time:.2f}s",
            "avg_extract_time": f"{self.stats.avg_extract_time:.3f}s",
            "avg_total_time": f"{self.stats.avg_total_time:.2f}s",
            "total_duration": f"{self.stats.total_duration:.1f}s",
            "urls_per_minute": f"{self.stats.urls_per_minute:.1f}",
            "top_errors": dict(
                sorted(
                    self.stats.error_counts.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
            ),
        }

    def print_summary(self) -> None:
        """Print formatted summary to console."""
        summary = self.get_summary()
        print("\n" + "=" * 50)
        print("SCRAPING STATISTICS")
        print("=" * 50)
        print(f"URLs Processed: {summary['total_urls']}")
        print(f"  + Successful: {summary['successful']}")
        print(f"  - Failed: {summary['failed']}")
        print(f"  Success Rate: {summary['success_rate']}")
        print(f"\nItems Extracted: {summary['items_extracted']}")
        print(f"Data Processed: {summary['bytes_processed']} bytes")
        print("\nTiming:")
        print(f"  Avg Fetch: {summary['avg_fetch_time']}")
        print(f"  Avg Extract: {summary['avg_extract_time']}")
        print(f"  Avg Total: {summary['avg_total_time']}")
        print(f"  Total Duration: {summary['total_duration']}")
        print(f"  Throughput: {summary['urls_per_minute']} URLs/min")

        if summary["top_errors"]:
            print("\nTop Errors:")
            for error, count in summary["top_errors"].items():
                print(f"  {count}x: {error}")

        print("=" * 50 + "\n")

    def reset(self) -> None:
        """Reset all statistics."""
        self.stats = ScrapingStatistics()
