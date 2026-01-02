"""Page utilities for Playwright interactions."""

import asyncio
from typing import Any, Optional


class PageUtils:
    """Utilities for Playwright page interactions."""

    @staticmethod
    async def scroll_to_bottom(page: Any, step: int = 300, delay: float = 0.1) -> None:
        """
        Scroll page to bottom in steps.

        Args:
            page: Playwright page object
            step: Pixels to scroll per step
            delay: Delay between steps in seconds
        """
        current = 0

        while True:
            # Get current scroll height
            scroll_height = await page.evaluate("document.body.scrollHeight")

            if current >= scroll_height:
                break

            current += step
            await page.evaluate(f"window.scrollTo(0, {current})")
            await asyncio.sleep(delay)

    @staticmethod
    async def scroll_to_element(page: Any, selector: str) -> None:
        """
        Scroll element into view.

        Args:
            page: Playwright page object
            selector: CSS selector for element
        """
        await page.evaluate(
            f'''
            document.querySelector("{selector}")?.scrollIntoView({{
                behavior: "smooth",
                block: "center"
            }})
        '''
        )

    @staticmethod
    async def wait_for_network_idle(page: Any, timeout: int = 30000) -> None:
        """
        Wait for network to be idle.

        Args:
            page: Playwright page object
            timeout: Timeout in milliseconds
        """
        await page.wait_for_load_state("networkidle", timeout=timeout)

    @staticmethod
    async def wait_for_selector_or_timeout(
        page: Any,
        selector: str,
        timeout: int = 10000,
        state: str = "visible",
    ) -> bool:
        """
        Wait for selector, return False if timeout.

        Args:
            page: Playwright page object
            selector: CSS selector
            timeout: Timeout in milliseconds
            state: State to wait for (visible, attached, etc.)

        Returns:
            True if found, False if timeout
        """
        try:
            await page.wait_for_selector(selector, timeout=timeout, state=state)
            return True
        except Exception:
            return False

    @staticmethod
    async def safe_click(page: Any, selector: str, timeout: int = 5000) -> bool:
        """
        Safely click an element.

        Args:
            page: Playwright page object
            selector: CSS selector
            timeout: Timeout in milliseconds

        Returns:
            True if clicked, False if failed
        """
        try:
            await page.click(selector, timeout=timeout)
            return True
        except Exception:
            return False

    @staticmethod
    async def safe_fill(page: Any, selector: str, value: str, timeout: int = 5000) -> bool:
        """
        Safely fill an input field.

        Args:
            page: Playwright page object
            selector: CSS selector
            value: Value to fill
            timeout: Timeout in milliseconds

        Returns:
            True if filled, False if failed
        """
        try:
            await page.fill(selector, value, timeout=timeout)
            return True
        except Exception:
            return False

    @staticmethod
    async def get_page_metrics(page: Any) -> dict[str, Any]:
        """
        Get page performance metrics.

        Args:
            page: Playwright page object

        Returns:
            Dictionary with performance metrics
        """
        return await page.evaluate(
            """
            () => {
                const timing = performance.timing;
                return {
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                    firstByte: timing.responseStart - timing.navigationStart,
                };
            }
        """
        )

    @staticmethod
    async def block_resources(page: Any, types: Optional[list[str]] = None) -> None:
        """
        Block specific resource types for faster loading.

        Args:
            page: Playwright page object
            types: Resource types to block
        """
        blocked = types or ["image", "media", "font", "stylesheet"]

        async def block_route(route: Any) -> None:
            if route.request.resource_type in blocked:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", block_route)

    @staticmethod
    async def inject_script(page: Any, script: str) -> None:
        """
        Inject JavaScript into page.

        Args:
            page: Playwright page object
            script: JavaScript code to inject
        """
        await page.add_script_tag(content=script)

    @staticmethod
    async def take_full_page_screenshot(page: Any) -> bytes:
        """
        Take full page screenshot.

        Args:
            page: Playwright page object

        Returns:
            Screenshot as bytes
        """
        return await page.screenshot(full_page=True)

    @staticmethod
    async def get_cookies(page: Any) -> list[dict[str, Any]]:
        """
        Get all cookies from page context.

        Args:
            page: Playwright page object

        Returns:
            List of cookie dictionaries
        """
        context = page.context
        return await context.cookies()

    @staticmethod
    async def set_cookies(page: Any, cookies: list[dict[str, Any]]) -> None:
        """
        Set cookies in page context.

        Args:
            page: Playwright page object
            cookies: List of cookie dictionaries
        """
        context = page.context
        await context.add_cookies(cookies)

    @staticmethod
    async def clear_cookies(page: Any) -> None:
        """
        Clear all cookies from page context.

        Args:
            page: Playwright page object
        """
        context = page.context
        await context.clear_cookies()

    @staticmethod
    async def get_local_storage(page: Any) -> dict[str, str]:
        """
        Get all localStorage items.

        Args:
            page: Playwright page object

        Returns:
            Dictionary of localStorage items
        """
        return await page.evaluate(
            """
            () => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            }
        """
        )

    @staticmethod
    async def set_local_storage(page: Any, items: dict[str, str]) -> None:
        """
        Set localStorage items.

        Args:
            page: Playwright page object
            items: Dictionary of items to set
        """
        for key, value in items.items():
            await page.evaluate(f"localStorage.setItem('{key}', '{value}')")
