"""Celery tasks for async scraping."""

try:
    import asyncio
    from typing import Any, Optional

    from celery import shared_task

    @shared_task(bind=True, max_retries=3)
    def scrape_url_task(
        self,
        url: str,
        instructions: list[dict[str, Any]],
        config_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Celery task for async scraping.

        Args:
            url: URL to scrape
            instructions: List of instruction dicts
            config_id: Optional ScrapeConfig ID

        Returns:
            Dict with url, success, data, errors
        """
        from yoinkr import Instruction, Method, Scraper

        # Build instructions
        if config_id:
            from .models import ScrapeConfig

            config = ScrapeConfig.objects.get(id=config_id)
            instr_list = config.get_instructions()
        else:
            instr_list = [
                Instruction(
                    name=i["name"],
                    find=i["find"],
                    method=Method(i.get("method", "css")),
                    multiple=i.get("multiple", False),
                    attribute=i.get("attribute"),
                    transform=i.get("transform"),
                )
                for i in instructions
            ]

        async def run():
            async with Scraper() as scraper:
                return await scraper.extract(url, instr_list)

        result = asyncio.run(run())

        return {
            "url": result.url,
            "success": result.success,
            "data": result.data,
            "errors": result.errors,
            "fetch_time": result.fetch_time,
            "extract_time": result.extract_time,
            "total_time": result.total_time,
        }

    @shared_task
    def scrape_batch_task(
        urls: list[str],
        instructions: list[dict[str, Any]],
        concurrency: int = 3,
        delay: Optional[tuple[float, float]] = None,
    ) -> list[dict[str, Any]]:
        """
        Scrape multiple URLs.

        Args:
            urls: List of URLs to scrape
            instructions: List of instruction dicts
            concurrency: Max concurrent requests
            delay: Random delay range (min, max)

        Returns:
            List of result dicts
        """
        from yoinkr import Instruction, Method, Scraper

        instr_list = [
            Instruction(
                name=i["name"],
                find=i["find"],
                method=Method(i.get("method", "css")),
                multiple=i.get("multiple", False),
                attribute=i.get("attribute"),
                transform=i.get("transform"),
            )
            for i in instructions
        ]

        async def run():
            async with Scraper() as scraper:
                return await scraper.extract_many(
                    urls=urls,
                    instructions=instr_list,
                    concurrency=concurrency,
                    delay=delay,
                )

        results = asyncio.run(run())

        return [
            {
                "url": r.url,
                "success": r.success,
                "data": r.data,
                "errors": r.errors,
            }
            for r in results
        ]

    @shared_task
    def scrape_config_task(config_id: int, url: Optional[str] = None) -> dict[str, Any]:
        """
        Scrape using a saved configuration.

        Args:
            config_id: ScrapeConfig ID
            url: Optional URL (uses default_url if not provided)

        Returns:
            Result dict
        """
        from .models import ScrapeConfig

        config = ScrapeConfig.objects.get(id=config_id)

        async def run():
            return await config.execute(url)

        result = asyncio.run(run())

        return {
            "url": result.url,
            "success": result.success,
            "data": result.data,
            "errors": result.errors,
        }

except ImportError:
    # Celery not installed
    def scrape_url_task(*args, **kwargs):
        raise ImportError("Celery is required for async tasks")

    def scrape_batch_task(*args, **kwargs):
        raise ImportError("Celery is required for async tasks")

    def scrape_config_task(*args, **kwargs):
        raise ImportError("Celery is required for async tasks")
