"""
Django integration for Yoinkr.

This package provides Django-specific components for integrating
Yoinkr into Django projects:

- **models**: ScrapeConfig and InstructionModel for database storage
- **admin**: Admin interface with inline instructions and test actions
- **tasks**: Celery tasks for async scraping operations
- **management/commands**: `./manage.py scrape` command

Setup:
    1. Add 'yoinkr.django' to INSTALLED_APPS
    2. Run migrations: `./manage.py migrate yoinkr`
    3. Configure scrape configs in Django admin

Example:
    >>> from yoinkr.django.models import ScrapeConfig
    >>> config = ScrapeConfig.objects.get(name="my-config")
    >>> result = await config.execute()

For Celery tasks:
    >>> from yoinkr.django.tasks import scrape_url_task
    >>> scrape_url_task.delay(url, instructions)
"""

from .apps import YoinkrConfig

default_app_config = "yoinkr.django.apps.YoinkrConfig"

__all__ = ["YoinkrConfig"]
