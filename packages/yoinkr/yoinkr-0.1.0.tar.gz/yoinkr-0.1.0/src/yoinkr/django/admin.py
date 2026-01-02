"""Django admin configuration."""

try:
    from django.contrib import admin

    from .models import InstructionModel, ScrapeConfig

    class InstructionInline(admin.TabularInline):
        """Inline for extraction instructions."""

        model = InstructionModel
        extra = 1
        fields = [
            "name",
            "selector",
            "method",
            "multiple",
            "attribute",
            "transform",
            "required",
            "order",
        ]
        ordering = ["order"]

    @admin.register(ScrapeConfig)
    class ScrapeConfigAdmin(admin.ModelAdmin):
        """Admin for scrape configurations."""

        list_display = [
            "name",
            "default_url",
            "instruction_count",
            "is_active",
            "updated_at",
        ]
        list_filter = ["is_active", "javascript_enabled", "created_at"]
        search_fields = ["name", "description", "default_url"]
        readonly_fields = ["created_at", "updated_at"]
        inlines = [InstructionInline]

        fieldsets = (
            (
                None,
                {
                    "fields": ("name", "description", "default_url", "is_active"),
                },
            ),
            (
                "Browser Options",
                {
                    "fields": ("javascript_enabled", "wait_for_selector", "wait_timeout"),
                    "classes": ("collapse",),
                },
            ),
            (
                "Proxy Settings",
                {
                    "fields": ("proxy_url", "proxy_country"),
                    "classes": ("collapse",),
                },
            ),
            (
                "Timestamps",
                {
                    "fields": ("created_at", "updated_at"),
                    "classes": ("collapse",),
                },
            ),
        )

        def instruction_count(self, obj: ScrapeConfig) -> int:
            """Get number of instructions."""
            return obj.instructions.count()

        instruction_count.short_description = "Instructions"

        actions = ["test_scrape"]

        @admin.action(description="Test scrape (uses default URL)")
        def test_scrape(self, request, queryset):
            """Test scrape action."""
            import asyncio

            for config in queryset:
                if not config.default_url:
                    self.message_user(
                        request,
                        f"{config.name}: No default URL set",
                        level="warning",
                    )
                    continue

                try:
                    result = asyncio.run(config.execute())
                    if result.success:
                        self.message_user(
                            request,
                            f"{config.name}: Success - {len(result.data)} fields extracted",
                        )
                    else:
                        self.message_user(
                            request,
                            f"{config.name}: Failed - {result.errors}",
                            level="error",
                        )
                except Exception as e:
                    self.message_user(
                        request,
                        f"{config.name}: Error - {e}",
                        level="error",
                    )

    @admin.register(InstructionModel)
    class InstructionModelAdmin(admin.ModelAdmin):
        """Admin for individual instructions (for advanced editing)."""

        list_display = [
            "name",
            "config",
            "method",
            "multiple",
            "required",
            "order",
        ]
        list_filter = ["config", "method", "multiple", "required"]
        search_fields = ["name", "selector", "config__name"]
        ordering = ["config", "order"]

except ImportError:
    # Django not installed
    pass
