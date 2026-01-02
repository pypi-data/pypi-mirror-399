"""Browser configuration for yoinkr."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BrowserConfig:
    """Complete browser configuration."""

    # Basic
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    timeout: int = 30000  # ms

    # JavaScript
    javascript_enabled: bool = True

    # User agent
    user_agent: Optional[str] = None
    randomize_user_agent: bool = False

    # Viewport
    viewport: Optional[dict[str, int]] = None  # {'width': 1920, 'height': 1080}
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False

    # Locale & Timezone
    locale: Optional[str] = None  # e.g., 'en-US', 'en-ZA'
    timezone: Optional[str] = None  # e.g., 'Africa/Johannesburg'

    # Geolocation
    geolocation: Optional[dict[str, float]] = None  # {'latitude': -26.2, 'longitude': 28.0}

    # Permissions
    permissions: list[str] = field(default_factory=list)  # ['geolocation', 'notifications']

    # Network
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    extra_http_headers: dict[str, str] = field(default_factory=dict)
    ignore_https_errors: bool = False

    # Performance
    resource_blocking: bool = False
    blocked_resource_types: list[str] = field(default_factory=lambda: ["image", "media", "font"])
    connection_pooling: bool = True

    # Downloads
    downloads_path: Optional[str] = None
    accept_downloads: bool = False

    # Recording
    record_video: bool = False
    video_dir: Optional[str] = None
    record_har: bool = False
    har_path: Optional[str] = None

    # Storage
    storage_state: Optional[str] = None  # Path to saved state

    def to_playwright_args(self) -> dict[str, Any]:
        """Convert to Playwright browser launch args."""
        args: dict[str, Any] = {
            "headless": self.headless,
        }

        if self.proxy:
            args["proxy"] = {"server": self.proxy}
            if self.proxy_username:
                args["proxy"]["username"] = self.proxy_username
                args["proxy"]["password"] = self.proxy_password

        if self.downloads_path:
            args["downloads_path"] = self.downloads_path

        if self.ignore_https_errors:
            args["ignore_https_errors"] = True

        return args

    def to_context_args(self) -> dict[str, Any]:
        """Convert to Playwright context args."""
        args: dict[str, Any] = {
            "java_script_enabled": self.javascript_enabled,
        }

        if self.viewport:
            args["viewport"] = self.viewport

        if self.user_agent:
            args["user_agent"] = self.user_agent

        if self.locale:
            args["locale"] = self.locale

        if self.timezone:
            args["timezone_id"] = self.timezone

        if self.geolocation:
            args["geolocation"] = self.geolocation

        if self.permissions:
            args["permissions"] = self.permissions

        if self.extra_http_headers:
            args["extra_http_headers"] = self.extra_http_headers

        if self.device_scale_factor != 1.0:
            args["device_scale_factor"] = self.device_scale_factor

        if self.is_mobile:
            args["is_mobile"] = True

        if self.has_touch:
            args["has_touch"] = True

        if self.storage_state:
            args["storage_state"] = self.storage_state

        if self.record_video and self.video_dir:
            args["record_video_dir"] = self.video_dir

        if self.record_har and self.har_path:
            args["record_har_path"] = self.har_path

        if self.accept_downloads:
            args["accept_downloads"] = True

        return args


# Default configurations for common scenarios
DESKTOP_CONFIG = BrowserConfig(
    viewport={"width": 1920, "height": 1080},
    locale="en-US",
)

MOBILE_CONFIG = BrowserConfig(
    viewport={"width": 390, "height": 844},
    is_mobile=True,
    has_touch=True,
    user_agent=(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
    ),
)

FAST_CONFIG = BrowserConfig(
    headless=True,
    resource_blocking=True,
    blocked_resource_types=["image", "media", "font", "stylesheet"],
    javascript_enabled=False,
)

STEALTH_CONFIG = BrowserConfig(
    randomize_user_agent=True,
    viewport={"width": 1920, "height": 1080},
    locale="en-US",
    timezone="America/New_York",
)
