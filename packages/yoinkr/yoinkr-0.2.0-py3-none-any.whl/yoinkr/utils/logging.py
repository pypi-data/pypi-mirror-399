"""Logging configuration for yoinkr."""

import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class LoggingConfig:
    """Configuration for scraper logging."""

    level: int = logging.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console
    console_enabled: bool = True
    console_level: Optional[int] = None

    # File
    file_enabled: bool = False
    file_path: Optional[str] = None
    file_level: Optional[int] = None
    file_rotation: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    # Per-session log file
    session_log: bool = False
    session_log_dir: str = "./logs"


class ScraperLogger:
    """Logger for scraper operations."""

    def __init__(
        self,
        name: str = "yoinkr",
        config: Optional[LoggingConfig] = None,
    ) -> None:
        """
        Initialize the logger.

        Args:
            name: Logger name
            config: Logging configuration
        """
        self.config = config or LoggingConfig()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.config.level)

        # Clear existing handlers
        self.logger.handlers.clear()

        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up logging handlers."""
        formatter = logging.Formatter(self.config.format)

        # Console handler
        if self.config.console_enabled:
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(self.config.console_level or self.config.level)
            console.setFormatter(formatter)
            self.logger.addHandler(console)

        # File handler
        if self.config.file_enabled and self.config.file_path:
            if self.config.file_rotation:
                from logging.handlers import RotatingFileHandler

                file_handler = RotatingFileHandler(
                    self.config.file_path,
                    maxBytes=self.config.max_file_size,
                    backupCount=self.config.backup_count,
                )
            else:
                file_handler = logging.FileHandler(self.config.file_path)

            file_handler.setLevel(self.config.file_level or self.config.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Session log
        if self.config.session_log:
            log_dir = Path(self.config.session_log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_file = log_dir / f"scrape_{timestamp}.log"

            session_handler = logging.FileHandler(session_file)
            session_handler.setLevel(logging.DEBUG)
            session_handler.setFormatter(formatter)
            self.logger.addHandler(session_handler)

    def info(self, msg: str, *args: object, **kwargs: object) -> None:
        """Log info message."""
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args: object, **kwargs: object) -> None:
        """Log debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args: object, **kwargs: object) -> None:
        """Log warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: object, **kwargs: object) -> None:
        """Log error message."""
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args: object, **kwargs: object) -> None:
        """Log exception with traceback."""
        self.logger.exception(msg, *args, **kwargs)

    def scrape_start(self, url: str) -> None:
        """Log scrape start."""
        self.info(f"Starting scrape: {url}")

    def scrape_success(self, url: str, items: int, time: float) -> None:
        """Log successful scrape."""
        self.info(f"Scraped {url}: {items} items in {time:.2f}s")

    def scrape_error(self, url: str, error: str) -> None:
        """Log scrape error."""
        self.error(f"Failed to scrape {url}: {error}")

    def batch_start(self, count: int) -> None:
        """Log batch start."""
        self.info(f"Starting batch scrape of {count} URLs")

    def batch_complete(self, total: int, successful: int, failed: int) -> None:
        """Log batch completion."""
        self.info(f"Batch complete: {successful}/{total} successful, {failed} failed")


def get_logger(
    name: str = "yoinkr",
    level: int = logging.INFO,
    file_path: Optional[str] = None,
) -> ScraperLogger:
    """
    Get a configured logger.

    Args:
        name: Logger name
        level: Logging level
        file_path: Optional file path for file logging

    Returns:
        Configured ScraperLogger
    """
    config = LoggingConfig(
        level=level,
        file_enabled=file_path is not None,
        file_path=file_path,
    )
    return ScraperLogger(name, config)
