"""Tests for Django models (requires Django to be installed)."""

import pytest

# Skip all tests in this module if Django is not installed
pytest.importorskip("django")


class TestScrapeConfig:
    """Tests for ScrapeConfig model."""

    @pytest.mark.skip(reason="Requires Django test setup")
    def test_create_config(self):
        """Test creating a scrape config."""
        from yoinkr.django.models import ScrapeConfig

        config = ScrapeConfig(
            name="test-config",
            description="Test configuration",
            default_url="https://example.com",
        )
        assert config.name == "test-config"

    @pytest.mark.skip(reason="Requires Django test setup")
    def test_get_instructions(self):
        """Test getting instructions from config."""
        pass


class TestInstructionModel:
    """Tests for InstructionModel."""

    @pytest.mark.skip(reason="Requires Django test setup")
    def test_create_instruction(self):
        """Test creating an instruction."""
        pass
