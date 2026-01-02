"""Django app configuration."""

try:
    from django.apps import AppConfig

    class YoinkrConfig(AppConfig):
        """Django app configuration for Yoinkr."""

        name = "yoinkr.django"
        label = "yoinkr"
        verbose_name = "Yoinkr"
        default_auto_field = "django.db.models.BigAutoField"

        def ready(self) -> None:
            """Called when Django starts."""
            pass

except ImportError:
    # Django not installed
    class YoinkrConfig:  # type: ignore
        """Placeholder when Django is not installed."""

        name = "yoinkr.django"
