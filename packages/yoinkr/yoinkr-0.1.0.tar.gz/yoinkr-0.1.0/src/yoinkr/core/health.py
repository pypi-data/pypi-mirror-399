"""
Health check module for the universal scraper.

Provides health checks to verify browser, dependencies, and system state
before and during scraping operations.
"""

import asyncio
import importlib.util
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from ..utils.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def is_healthy(self) -> bool:
        """Check if the result is healthy."""
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HealthReport:
    """Overall health report."""

    status: HealthStatus
    checks: list[HealthCheckResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def is_healthy(self) -> bool:
        """Check if overall health is good."""
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp.isoformat(),
        }


class HealthChecker:
    """
    Health checker for the scraper.

    Verifies that all required components are available and functioning.

    Example:
        >>> checker = HealthChecker()
        >>> report = await checker.check_all()
        >>> if report.is_healthy():
        ...     print("All systems operational")
    """

    def __init__(self) -> None:
        """Initialize the health checker."""
        self._checks: list[tuple[str, callable]] = [
            ("playwright", self._check_playwright),
            ("browser_binary", self._check_browser_binary),
            ("beautifulsoup", self._check_beautifulsoup),
            ("lxml", self._check_lxml),
            ("memory", self._check_memory),
        ]

    async def check_all(self) -> HealthReport:
        """
        Run all health checks.

        Returns:
            HealthReport with all check results
        """
        logger.info("Running health checks")
        results: list[HealthCheckResult] = []

        for name, check_func in self._checks:
            try:
                result = await self._run_check(name, check_func)
                results.append(result)
            except Exception as e:
                results.append(
                    HealthCheckResult(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {e}",
                    )
                )

        # Determine overall status
        if all(r.is_healthy() for r in results):
            overall_status = HealthStatus.HEALTHY
        elif any(r.status == HealthStatus.UNHEALTHY for r in results):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        report = HealthReport(status=overall_status, checks=results)
        logger.info(
            f"Health check complete: {overall_status.value}",
            extra={
                "status": overall_status.value,
                "checks_passed": sum(1 for r in results if r.is_healthy()),
                "checks_total": len(results),
            },
        )

        return report

    async def check_browser(self) -> HealthCheckResult:
        """
        Check if browser can be launched.

        Returns:
            HealthCheckResult for browser check
        """
        return await self._run_check("browser", self._check_browser_launch)

    async def check_dependencies(self) -> HealthCheckResult:
        """
        Check if all Python dependencies are available.

        Returns:
            HealthCheckResult for dependencies
        """
        results = []
        results.append(await self._run_check("playwright", self._check_playwright))
        results.append(await self._run_check("beautifulsoup", self._check_beautifulsoup))
        results.append(await self._run_check("lxml", self._check_lxml))

        # Aggregate results
        if all(r.is_healthy() for r in results):
            return HealthCheckResult(
                name="dependencies",
                status=HealthStatus.HEALTHY,
                message="All dependencies available",
            )
        else:
            failed = [r.name for r in results if not r.is_healthy()]
            return HealthCheckResult(
                name="dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"Missing dependencies: {', '.join(failed)}",
            )

    async def _run_check(self, name: str, check_func: callable) -> HealthCheckResult:
        """Run a single health check with timing."""
        import time

        start = time.time()
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()

            result.duration_ms = (time.time() - start) * 1000
            return result

        except Exception as e:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                duration_ms=(time.time() - start) * 1000,
            )

    def _check_playwright(self) -> HealthCheckResult:
        """Check if Playwright is installed."""
        if importlib.util.find_spec("playwright") is not None:
            return HealthCheckResult(
                name="playwright",
                status=HealthStatus.HEALTHY,
                message="Playwright is installed",
            )
        return HealthCheckResult(
            name="playwright",
            status=HealthStatus.UNHEALTHY,
            message="Playwright is not installed. Run: pip install playwright",
        )

    def _check_browser_binary(self) -> HealthCheckResult:
        """Check if browser binaries are available."""
        # Check for chromium in common locations
        chromium_paths = [
            shutil.which("chromium"),
            shutil.which("chromium-browser"),
            shutil.which("google-chrome"),
        ]

        if any(chromium_paths):
            return HealthCheckResult(
                name="browser_binary",
                status=HealthStatus.HEALTHY,
                message="Browser binary found",
            )

        # Check Playwright browsers
        try:
            from playwright._impl._driver import compute_driver_executable

            driver = compute_driver_executable()
            if driver:
                return HealthCheckResult(
                    name="browser_binary",
                    status=HealthStatus.HEALTHY,
                    message="Playwright browser available",
                )
        except Exception:
            pass

        return HealthCheckResult(
            name="browser_binary",
            status=HealthStatus.DEGRADED,
            message="Browser binary not found. Run: playwright install chromium",
        )

    async def _check_browser_launch(self) -> HealthCheckResult:
        """Check if browser can actually be launched."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                await browser.close()

            return HealthCheckResult(
                name="browser",
                status=HealthStatus.HEALTHY,
                message="Browser launches successfully",
            )
        except Exception as e:
            return HealthCheckResult(
                name="browser",
                status=HealthStatus.UNHEALTHY,
                message=f"Browser launch failed: {e}",
            )

    def _check_beautifulsoup(self) -> HealthCheckResult:
        """Check if BeautifulSoup is installed."""
        if importlib.util.find_spec("bs4") is not None:
            return HealthCheckResult(
                name="beautifulsoup",
                status=HealthStatus.HEALTHY,
                message="BeautifulSoup is installed",
            )
        return HealthCheckResult(
            name="beautifulsoup",
            status=HealthStatus.UNHEALTHY,
            message="BeautifulSoup is not installed",
        )

    def _check_lxml(self) -> HealthCheckResult:
        """Check if lxml is installed."""
        if importlib.util.find_spec("lxml") is not None:
            return HealthCheckResult(
                name="lxml",
                status=HealthStatus.HEALTHY,
                message="lxml is installed",
            )
        return HealthCheckResult(
            name="lxml",
            status=HealthStatus.UNHEALTHY,
            message="lxml is not installed",
        )

    def _check_memory(self) -> HealthCheckResult:
        """Check available memory."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)

            if available_mb > 512:
                status = HealthStatus.HEALTHY
                message = f"Sufficient memory available: {available_mb:.0f}MB"
            elif available_mb > 256:
                status = HealthStatus.DEGRADED
                message = f"Low memory: {available_mb:.0f}MB"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Very low memory: {available_mb:.0f}MB"

            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                details={"available_mb": available_mb, "percent_used": memory.percent},
            )
        except ImportError:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message="psutil not installed, cannot check memory",
            )


async def check_health() -> HealthReport:
    """
    Convenience function to run all health checks.

    Returns:
        HealthReport with all check results
    """
    checker = HealthChecker()
    return await checker.check_all()
