"""Tests for logging utilities."""

import logging
import tempfile
from pathlib import Path

import pytest

from yoinkr.utils.logging import LoggingConfig, ScraperLogger, get_logger


class TestLoggingConfig:
    """Tests for LoggingConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = LoggingConfig()
        assert config.level == logging.INFO
        assert config.console_enabled is True
        assert config.file_enabled is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = LoggingConfig(
            level=logging.DEBUG,
            console_enabled=False,
            file_enabled=True,
            file_path="/tmp/test.log",
        )
        assert config.level == logging.DEBUG
        assert config.console_enabled is False
        assert config.file_enabled is True


class TestScraperLogger:
    """Tests for ScraperLogger."""

    def test_create_logger(self):
        """Test creating logger."""
        logger = ScraperLogger("test_logger")
        assert logger.logger is not None
        assert logger.logger.name == "test_logger"

    def test_log_levels(self, caplog):
        """Test logging at different levels."""
        config = LoggingConfig(level=logging.DEBUG)
        logger = ScraperLogger("test_levels", config)

        with caplog.at_level(logging.DEBUG, logger="test_levels"):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text

    def test_file_logging(self):
        """Test file logging."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            path = f.name

        try:
            config = LoggingConfig(
                file_enabled=True,
                file_path=path,
                console_enabled=False,
            )
            logger = ScraperLogger("file_test", config)
            logger.info("Test message to file")

            # Force flush
            for handler in logger.logger.handlers:
                handler.flush()

            with open(path, "r") as f:
                content = f.read()

            assert "Test message to file" in content
        finally:
            Path(path).unlink(missing_ok=True)

    def test_scrape_start(self, caplog):
        """Test scrape_start helper."""
        config = LoggingConfig(level=logging.INFO)
        logger = ScraperLogger("scrape_test", config)

        with caplog.at_level(logging.INFO, logger="scrape_test"):
            logger.scrape_start("https://example.com")

        assert "Starting scrape" in caplog.text
        assert "example.com" in caplog.text

    def test_scrape_success(self, caplog):
        """Test scrape_success helper."""
        config = LoggingConfig(level=logging.INFO)
        logger = ScraperLogger("scrape_test", config)

        with caplog.at_level(logging.INFO, logger="scrape_test"):
            logger.scrape_success("https://example.com", items=5, time=1.5)

        assert "Scraped" in caplog.text
        assert "5 items" in caplog.text

    def test_scrape_error(self, caplog):
        """Test scrape_error helper."""
        config = LoggingConfig(level=logging.ERROR)
        logger = ScraperLogger("scrape_test", config)

        with caplog.at_level(logging.ERROR, logger="scrape_test"):
            logger.scrape_error("https://example.com", "Connection timeout")

        assert "Failed to scrape" in caplog.text
        assert "Connection timeout" in caplog.text

    def test_batch_logging(self, caplog):
        """Test batch logging helpers."""
        config = LoggingConfig(level=logging.INFO)
        logger = ScraperLogger("batch_test", config)

        with caplog.at_level(logging.INFO, logger="batch_test"):
            logger.batch_start(10)
            logger.batch_complete(total=10, successful=8, failed=2)

        assert "Starting batch" in caplog.text
        assert "10 URLs" in caplog.text
        assert "8/10 successful" in caplog.text


class TestGetLogger:
    """Tests for get_logger helper."""

    def test_get_logger_default(self):
        """Test getting default logger."""
        logger = get_logger()
        assert logger.logger.name == "yoinkr"

    def test_get_logger_custom(self):
        """Test getting custom logger."""
        logger = get_logger(
            name="custom",
            level=logging.DEBUG,
        )
        assert logger.logger.name == "custom"
        assert logger.config.level == logging.DEBUG

    def test_get_logger_with_file(self):
        """Test getting logger with file."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            path = f.name

        try:
            logger = get_logger(file_path=path)
            assert logger.config.file_enabled is True
            assert logger.config.file_path == path
        finally:
            Path(path).unlink(missing_ok=True)
