"""Page fetching for the universal scraper."""

import asyncio
from typing import Any, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from ..utils.logging import get_logger
from .browser_config import BrowserConfig
from .exceptions import BrowserError, FetchError

logger = get_logger(__name__)


class Fetcher:
    """Playwright-based page fetcher."""

    def __init__(
        self,
        headless: bool = True,
        javascript: bool = True,
        timeout: int = 30,
        proxy: Optional[str] = None,
        proxy_country: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        connection_pooling: bool = True,
        resource_blocking: bool = False,
        blocked_resource_types: Optional[list[str]] = None,
        user_agent: Optional[str] = None,
        viewport: Optional[dict[str, int]] = None,
        locale: Optional[str] = None,
        timezone: Optional[str] = None,
        debug: bool = False,
        config: Optional[BrowserConfig] = None,
    ) -> None:
        """
        Initialize the fetcher.

        Args:
            headless: Run browser in headless mode
            javascript: Enable JavaScript
            timeout: Default timeout in seconds
            proxy: Proxy URL
            proxy_country: Proxy country code (for geo-targeting)
            proxy_username: Proxy username
            proxy_password: Proxy password
            connection_pooling: Reuse browser context
            resource_blocking: Block specified resource types
            blocked_resource_types: Resource types to block
            user_agent: Custom user agent
            viewport: Viewport dimensions
            locale: Browser locale
            timezone: Browser timezone
            debug: Enable debug mode
            config: Full BrowserConfig (overrides other options)
        """
        if config:
            self._config = config
        else:
            self._config = BrowserConfig(
                headless=headless,
                javascript_enabled=javascript,
                timeout=timeout * 1000,  # Convert to ms
                proxy=proxy,
                proxy_username=proxy_username,
                proxy_password=proxy_password,
                connection_pooling=connection_pooling,
                resource_blocking=resource_blocking,
                blocked_resource_types=blocked_resource_types or ["image", "media", "font"],
                user_agent=user_agent,
                viewport=viewport,
                locale=locale,
                timezone=timezone,
            )

        self._proxy_country = proxy_country
        self._debug = debug

        self._playwright: Any = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._started = False

    async def start(self) -> None:
        """Start the browser."""
        if self._started:
            return

        logger.info(
            "Starting browser",
            extra={
                "browser_type": self._config.browser_type,
                "headless": self._config.headless,
            },
        )

        try:
            self._playwright = await async_playwright().start()

            # Get browser type
            browser_type = getattr(
                self._playwright, self._config.browser_type, self._playwright.chromium
            )

            # Launch browser
            launch_args = self._config.to_playwright_args()
            self._browser = await browser_type.launch(**launch_args)
            logger.debug("Browser launched successfully")

            # Create context
            context_args = self._config.to_context_args()
            self._context = await self._browser.new_context(**context_args)
            logger.debug("Browser context created")

            # Set up resource blocking if enabled
            if self._config.resource_blocking:
                await self._setup_resource_blocking()
                logger.debug(
                    "Resource blocking enabled",
                    extra={
                        "blocked_types": self._config.blocked_resource_types,
                    },
                )

            self._started = True
            logger.info("Browser started successfully")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            await self.stop()
            raise BrowserError(f"Failed to start browser: {e}")

    async def stop(self) -> None:
        """Stop the browser and clean up resources."""
        logger.info("Stopping browser")

        if self._context:
            try:
                await self._context.close()
                logger.debug("Browser context closed")
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
            self._context = None

        if self._browser:
            try:
                await self._browser.close()
                logger.debug("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
                logger.debug("Playwright stopped")
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            self._playwright = None

        self._started = False
        logger.info("Browser stopped")

    async def _setup_resource_blocking(self) -> None:
        """Set up resource blocking for the context."""
        if not self._context:
            return

        blocked_types = self._config.blocked_resource_types

        async def block_route(route: Any) -> None:
            if route.request.resource_type in blocked_types:
                await route.abort()
            else:
                await route.continue_()

        await self._context.route("**/*", block_route)

    async def fetch(
        self,
        url: str,
        wait_for: Optional[str] = None,
        wait_timeout: int = 30,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        screenshot: bool = False,
    ) -> dict[str, Any]:
        """
        Fetch a page and return its content.

        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for
            wait_timeout: Timeout for waiting (seconds)
            headers: Additional headers
            cookies: Cookies to set
            screenshot: Whether to take a screenshot

        Returns:
            Dict with html, status_code, final_url, title, screenshot
        """
        if not self._started or not self._context:
            raise BrowserError("Fetcher not started. Call start() first.")

        logger.debug(f"Fetching URL: {url}", extra={"url": url})
        page: Optional[Page] = None

        try:
            page = await self._context.new_page()

            # Set extra headers if provided
            if headers:
                await page.set_extra_http_headers(headers)
                logger.debug("Extra headers set", extra={"header_count": len(headers)})

            # Set cookies if provided
            if cookies:
                cookie_list = [{"name": k, "value": v, "url": url} for k, v in cookies.items()]
                await self._context.add_cookies(cookie_list)
                logger.debug("Cookies set", extra={"cookie_count": len(cookies)})

            # Navigate to the URL
            response = await page.goto(
                url,
                timeout=self._config.timeout,
                wait_until="domcontentloaded",
            )

            if not response:
                logger.error(f"No response from {url}")
                raise FetchError(f"No response from {url}", url=url)

            logger.debug(
                f"Response received",
                extra={
                    "url": url,
                    "status_code": response.status,
                    "final_url": page.url,
                },
            )

            # Wait for selector if specified
            if wait_for:
                try:
                    await page.wait_for_selector(wait_for, timeout=wait_timeout * 1000)
                    logger.debug(f"Selector found: {wait_for}")
                except Exception:
                    # Continue even if selector not found
                    logger.warning(
                        f"Selector not found: {wait_for}",
                        extra={
                            "url": url,
                            "selector": wait_for,
                        },
                    )

            # Get page content
            html = await page.content()
            title = await page.title()

            # Take screenshot if requested
            screenshot_bytes = None
            if screenshot:
                screenshot_bytes = await page.screenshot(full_page=True)
                logger.debug("Screenshot captured")

            logger.info(
                f"Page fetched successfully",
                extra={
                    "url": url,
                    "status_code": response.status,
                    "content_length": len(html),
                },
            )

            return {
                "html": html,
                "status_code": response.status,
                "final_url": page.url,
                "title": title,
                "screenshot": screenshot_bytes,
            }

        except Exception as e:
            if isinstance(e, (FetchError, BrowserError)):
                raise
            logger.error(
                f"Failed to fetch {url}: {e}",
                extra={
                    "url": url,
                    "error": str(e),
                },
            )
            raise FetchError(f"Failed to fetch {url}: {e}", url=url)

        finally:
            if page and not self._config.connection_pooling:
                await page.close()
            elif page:
                # Close page but keep context for pooling
                await page.close()

    async def fetch_simple(self, url: str) -> str:
        """
        Simple fetch that returns just the HTML.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        result = await self.fetch(url)
        return result["html"]

    async def __aenter__(self) -> "Fetcher":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
