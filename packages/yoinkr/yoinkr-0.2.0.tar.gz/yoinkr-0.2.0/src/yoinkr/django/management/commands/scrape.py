"""Management command for scraping."""

try:
    import asyncio
    import json
    from typing import Any

    from django.core.management.base import BaseCommand, CommandError

    class Command(BaseCommand):
        """Scrape a URL with instructions."""

        help = "Scrape a URL with instructions"

        def add_arguments(self, parser) -> None:
            """Add command arguments."""
            parser.add_argument("url", help="URL to scrape")
            parser.add_argument(
                "-i",
                "--instruction",
                action="append",
                nargs="+",
                metavar="NAME SELECTOR [METHOD]",
                help="Instruction: name selector [method]",
            )
            parser.add_argument(
                "-c",
                "--config",
                help="Use saved config name or ID",
            )
            parser.add_argument(
                "--no-js",
                action="store_true",
                help="Disable JavaScript",
            )
            parser.add_argument(
                "--pretty",
                action="store_true",
                help="Pretty print JSON output",
            )
            parser.add_argument(
                "--timeout",
                type=int,
                default=30,
                help="Timeout in seconds (default: 30)",
            )
            parser.add_argument(
                "--wait-for",
                help="CSS selector to wait for before extraction",
            )
            parser.add_argument(
                "--proxy",
                help="Proxy URL",
            )
            parser.add_argument(
                "--include-html",
                action="store_true",
                help="Include HTML in output",
            )

        def handle(self, *args: Any, **options: Any) -> None:
            """Execute the command."""
            from yoinkr import Instruction, Method, ScrapeOptions, Scraper

            url = options["url"]
            instructions = []

            # Build instructions from config or command line
            if options["config"]:
                from yoinkr.django.models import ScrapeConfig

                try:
                    # Try as ID first
                    config = ScrapeConfig.objects.get(id=int(options["config"]))
                except (ValueError, ScrapeConfig.DoesNotExist):
                    # Try as name
                    try:
                        config = ScrapeConfig.objects.get(name=options["config"])
                    except ScrapeConfig.DoesNotExist:
                        raise CommandError(f"Config not found: {options['config']}")

                instructions = config.get_instructions()
                self.stdout.write(f"Using config: {config.name} ({len(instructions)} instructions)")

            elif options["instruction"]:
                for parts in options["instruction"]:
                    name = parts[0]
                    selector = parts[1]
                    method = parts[2] if len(parts) > 2 else "css"
                    instructions.append(Instruction(name, selector, method=Method(method)))
            else:
                raise CommandError("Provide -i instructions or -c config")

            # Build options
            scrape_options = ScrapeOptions(
                javascript=not options["no_js"],
                wait_for=options.get("wait_for"),
                wait_timeout=options["timeout"],
                include_html=options["include_html"],
            )

            # Run scrape
            async def run():
                async with Scraper(
                    javascript=not options["no_js"],
                    timeout=options["timeout"],
                    proxy=options.get("proxy"),
                ) as scraper:
                    return await scraper.extract(
                        url=url,
                        instructions=instructions,
                        options=scrape_options,
                    )

            self.stdout.write(f"Scraping: {url}")
            result = asyncio.run(run())

            # Output
            output = {
                "url": result.url,
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "timing": {
                    "fetch": result.fetch_time,
                    "extract": result.extract_time,
                    "total": result.total_time,
                },
            }

            if result.html and options["include_html"]:
                output["html"] = result.html

            indent = 2 if options["pretty"] else None
            self.stdout.write(json.dumps(output, indent=indent, default=str))

            if result.success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nSuccess! Extracted {len(result.data)} fields in {result.total_time:.2f}s"
                    )
                )
            else:
                self.stdout.write(self.style.ERROR(f"\nFailed: {result.errors}"))

except ImportError:
    # Django not installed
    pass
