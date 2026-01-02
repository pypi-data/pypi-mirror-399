"""Main Scraper class for yoinkr."""

import asyncio
import random
import signal
import time
from typing import Any, Callable, Optional

from ..utils.logging import get_logger
from .browser_config import BrowserConfig
from .extractor import Extractor
from .fetcher import Fetcher
from .types import Instruction, ScrapeOptions, ScrapeResult

logger = get_logger(__name__)


class Scraper:
    """
    Universal web scraper.

    Usage:
        async with Scraper() as scraper:
            result = await scraper.extract(url, instructions)

    Or without context manager:
        scraper = Scraper()
        await scraper.start()
        result = await scraper.extract(url, instructions)
        await scraper.stop()
    """

    def __init__(
        self,
        # Browser options
        headless: bool = True,
        javascript: bool = True,
        timeout: int = 30,
        # Proxy
        proxy: Optional[str] = None,
        proxy_country: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        # Performance
        connection_pooling: bool = True,
        resource_blocking: bool = False,
        # User agent
        user_agent: Optional[str] = None,
        randomize_user_agent: bool = False,
        # Viewport
        viewport: Optional[dict[str, int]] = None,
        # Locale
        locale: Optional[str] = None,
        timezone: Optional[str] = None,
        # Callbacks
        on_result: Optional[Callable[["ScrapeResult"], Any]] = None,
        on_error: Optional[Callable[["ScrapeResult", Exception], Any]] = None,
        # Browser config
        config: Optional[BrowserConfig] = None,
        # Debug
        debug: bool = False,
    ) -> None:
        """
        Initialize the scraper.

        Args:
            headless: Run browser in headless mode
            javascript: Enable JavaScript
            timeout: Default timeout in seconds
            proxy: Proxy URL
            proxy_country: Proxy country code
            proxy_username: Proxy username
            proxy_password: Proxy password
            connection_pooling: Reuse browser context
            resource_blocking: Block images/media/fonts
            user_agent: Custom user agent
            randomize_user_agent: Use random user agents
            viewport: Browser viewport dimensions
            locale: Browser locale
            timezone: Browser timezone
            on_result: Callback for each result
            on_error: Callback for errors
            config: Full BrowserConfig (overrides other options)
            debug: Enable debug mode
        """
        self._headless = headless
        self._javascript = javascript
        self._timeout = timeout
        self._proxy = proxy
        self._proxy_country = proxy_country
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password
        self._connection_pooling = connection_pooling
        self._resource_blocking = resource_blocking
        self._user_agent = user_agent
        self._randomize_user_agent = randomize_user_agent
        self._viewport = viewport
        self._locale = locale
        self._timezone = timezone
        self._on_result = on_result
        self._on_error = on_error
        self._config = config
        self._debug = debug

        self._fetcher: Optional[Fetcher] = None
        self._extractor: Optional[Extractor] = None
        self._started = False
        self._shutting_down = False

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

        logger.debug(
            "Scraper initialized",
            extra={
                "headless": headless,
                "javascript": javascript,
                "timeout": timeout,
                "proxy": bool(proxy),
            },
        )

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        try:
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, self._handle_shutdown_signal)
        except (RuntimeError, NotImplementedError):
            # Signal handlers not supported (e.g., Windows, non-main thread)
            pass

    def _handle_shutdown_signal(self) -> None:
        """Handle shutdown signals gracefully."""
        if self._shutting_down:
            return
        self._shutting_down = True
        logger.info("Received shutdown signal, cleaning up...")
        asyncio.create_task(self._graceful_shutdown())

    async def _graceful_shutdown(self) -> None:
        """Perform graceful shutdown."""
        logger.info("Performing graceful shutdown")
        await self.stop()
        logger.info("Shutdown complete")

    async def start(self) -> None:
        """Initialize browser and extractor."""
        if self._started:
            return

        logger.info("Starting scraper")
        self._fetcher = Fetcher(
            headless=self._headless,
            javascript=self._javascript,
            timeout=self._timeout,
            proxy=self._proxy,
            proxy_country=self._proxy_country,
            proxy_username=self._proxy_username,
            proxy_password=self._proxy_password,
            connection_pooling=self._connection_pooling,
            resource_blocking=self._resource_blocking,
            user_agent=self._user_agent,
            viewport=self._viewport,
            locale=self._locale,
            timezone=self._timezone,
            debug=self._debug,
            config=self._config,
        )
        await self._fetcher.start()

        self._extractor = Extractor()
        self._started = True
        logger.info("Scraper started successfully")

    async def stop(self) -> None:
        """Clean up resources."""
        logger.info("Stopping scraper")
        if self._fetcher:
            await self._fetcher.stop()
            self._fetcher = None
        self._extractor = None
        self._started = False
        logger.info("Scraper stopped")

    async def __aenter__(self) -> "Scraper":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()

    async def extract(
        self,
        url: str,
        instructions: list[Instruction],
        options: Optional[ScrapeOptions] = None,
    ) -> ScrapeResult:
        """
        Extract data from a URL using provided instructions.

        Args:
            url: URL to scrape
            instructions: List of extraction instructions
            options: Optional scrape options

        Returns:
            ScrapeResult with extracted data
        """
        if not self._started or not self._fetcher or not self._extractor:
            raise RuntimeError("Scraper not started. Use 'async with Scraper()' or call start()")

        options = options or ScrapeOptions()
        start_time = time.time()

        logger.debug(
            f"Starting extraction for {url}",
            extra={
                "url": url,
                "instruction_count": len(instructions),
            },
        )

        try:
            # Fetch page
            fetch_start = time.time()
            page_data = await self._fetcher.fetch(
                url=url,
                wait_for=options.wait_for,
                wait_timeout=options.wait_timeout,
                headers=options.headers or None,
                cookies=options.cookies or None,
                screenshot=options.include_screenshot,
            )
            fetch_time = time.time() - fetch_start
            logger.debug(
                f"Page fetched in {fetch_time:.2f}s",
                extra={
                    "url": url,
                    "status_code": page_data.get("status_code"),
                    "fetch_time": fetch_time,
                },
            )

            # Extract data
            extract_start = time.time()
            extraction = await self._extractor.extract(
                source=page_data["html"],
                instructions=instructions,
            )
            extract_time = time.time() - extract_start
            logger.debug(
                f"Data extracted in {extract_time:.3f}s",
                extra={
                    "url": url,
                    "fields_extracted": len(extraction["data"]),
                    "extract_time": extract_time,
                },
            )

            result = ScrapeResult(
                url=url,
                success=True,
                data=extraction["data"],
                status_code=page_data.get("status_code"),
                final_url=page_data.get("final_url"),
                page_title=page_data.get("title"),
                html=page_data["html"] if options.include_html else None,
                screenshot=page_data.get("screenshot") if options.include_screenshot else None,
                fetch_time=fetch_time,
                extract_time=extract_time,
                total_time=time.time() - start_time,
                errors=extraction.get("errors", []),
            )

            if result.errors:
                logger.warning(
                    f"Extraction completed with {len(result.errors)} errors",
                    extra={
                        "url": url,
                        "errors": result.errors,
                    },
                )
            else:
                logger.info(
                    f"Extraction successful for {url}",
                    extra={
                        "url": url,
                        "total_time": result.total_time,
                    },
                )

            if self._on_result:
                await self._call_callback(self._on_result, result)

            return result

        except Exception as e:
            logger.error(
                f"Extraction failed for {url}: {e}",
                extra={
                    "url": url,
                    "error": str(e),
                },
            )

            result = ScrapeResult(
                url=url,
                success=False,
                data={},
                total_time=time.time() - start_time,
                errors=[{"error": str(e)}],
            )

            if self._on_error:
                await self._call_callback(self._on_error, result, e)

            return result

    async def extract_many(
        self,
        urls: list[str],
        instructions: list[Instruction],
        options: Optional[ScrapeOptions] = None,
        concurrency: int = 1,
        delay: Optional[tuple[float, float]] = None,
    ) -> list[ScrapeResult]:
        """
        Extract data from multiple URLs.

        Args:
            urls: List of URLs
            instructions: Extraction instructions (same for all)
            options: Scrape options
            concurrency: Max concurrent requests
            delay: Random delay range (min, max) between requests

        Returns:
            List of ScrapeResults
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def process_url(url: str) -> ScrapeResult:
            async with semaphore:
                result = await self.extract(url, instructions, options)

                if delay:
                    await asyncio.sleep(random.uniform(*delay))

                return result

        tasks = [process_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    ScrapeResult(
                        url=urls[i],
                        success=False,
                        data={},
                        errors=[{"error": str(result)}],
                    )
                )
            else:
                final_results.append(result)

        return final_results

    async def _call_callback(self, callback: Callable[..., Any], *args: Any) -> None:
        """Call callback, handling both sync and async."""
        if asyncio.iscoroutinefunction(callback):
            await callback(*args)
        else:
            callback(*args)

    @property
    def is_started(self) -> bool:
        """Check if scraper is started."""
        return self._started
