"""Django models for scraping configuration."""

try:
    from django.db import models

    class ScrapeConfig(models.Model):
        """
        Reusable scrape configuration stored in database.
        Allows non-developers to configure scraping via Django admin.
        """

        name = models.CharField(max_length=255, unique=True)
        description = models.TextField(blank=True)

        # Default URL (can be overridden)
        default_url = models.URLField(blank=True)

        # Browser options
        javascript_enabled = models.BooleanField(default=True)
        wait_for_selector = models.CharField(max_length=500, blank=True)
        wait_timeout = models.IntegerField(default=30)

        # Proxy
        proxy_url = models.CharField(max_length=500, blank=True)
        proxy_country = models.CharField(max_length=2, blank=True)

        # Status
        is_active = models.BooleanField(default=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            verbose_name = "Scrape Configuration"
            verbose_name_plural = "Scrape Configurations"
            ordering = ["-updated_at"]

        def __str__(self) -> str:
            return self.name

        def get_instructions(self) -> list:
            """Convert stored instructions to Instruction objects."""
            from yoinkr import Instruction, Method

            return [
                Instruction(
                    name=i.name,
                    find=i.selector,
                    method=Method(i.method),
                    multiple=i.multiple,
                    attribute=i.attribute or None,
                    default=i.default_value or None,
                    required=i.required,
                    transform=i.transform or None,
                )
                for i in self.instructions.all()
            ]

        async def execute(self, url: str = None):
            """
            Execute this config.

            Args:
                url: URL to scrape (uses default_url if not provided)

            Returns:
                ScrapeResult
            """
            from yoinkr import ScrapeOptions, Scraper

            target_url = url or self.default_url
            if not target_url:
                raise ValueError("No URL provided")

            options = ScrapeOptions(
                javascript=self.javascript_enabled,
                wait_for=self.wait_for_selector or None,
                wait_timeout=self.wait_timeout,
            )

            async with Scraper(
                javascript=self.javascript_enabled,
                proxy=self.proxy_url or None,
                proxy_country=self.proxy_country or None,
            ) as scraper:
                return await scraper.extract(
                    url=target_url,
                    instructions=self.get_instructions(),
                    options=options,
                )

    class InstructionModel(models.Model):
        """Single extraction instruction."""

        METHOD_CHOICES = [
            ("css", "CSS Selector"),
            ("xpath", "XPath"),
            ("regex", "Regex"),
            ("text", "Text Search"),
            ("meta", "Meta Tag"),
        ]

        TRANSFORM_CHOICES = [
            ("", "None"),
            ("lowercase", "Lowercase"),
            ("uppercase", "Uppercase"),
            ("int", "Integer"),
            ("float", "Float"),
            ("clean", "Clean Whitespace"),
            ("bool", "Boolean"),
        ]

        config = models.ForeignKey(
            ScrapeConfig,
            on_delete=models.CASCADE,
            related_name="instructions",
        )

        name = models.CharField(
            max_length=100,
            help_text="Field name in output",
        )
        selector = models.TextField(
            help_text="CSS selector, XPath, regex pattern, etc.",
        )
        method = models.CharField(
            max_length=20,
            choices=METHOD_CHOICES,
            default="css",
        )

        multiple = models.BooleanField(
            default=False,
            help_text="Return list vs single value",
        )
        attribute = models.CharField(
            max_length=100,
            blank=True,
            help_text="Extract attribute instead of text (e.g., 'href', 'src')",
        )
        default_value = models.TextField(
            blank=True,
            help_text="Default value if not found",
        )
        required = models.BooleanField(
            default=False,
            help_text="Raise error if not found",
        )
        transform = models.CharField(
            max_length=50,
            choices=TRANSFORM_CHOICES,
            blank=True,
            help_text="Transform the extracted value",
        )

        order = models.IntegerField(
            default=0,
            help_text="Order in which instructions are processed",
        )

        class Meta:
            ordering = ["order", "id"]
            verbose_name = "Extraction Instruction"
            verbose_name_plural = "Extraction Instructions"

        def __str__(self) -> str:
            return f"{self.config.name}.{self.name}"

except ImportError:
    # Django not installed
    pass
