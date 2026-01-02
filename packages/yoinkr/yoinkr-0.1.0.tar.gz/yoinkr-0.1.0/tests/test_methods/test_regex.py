"""Tests for Regex extraction method."""

import pytest

from yoinkr.core.methods.regex import RegexMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def regex_method():
    return RegexMethod()


class TestRegexMethod:
    """Tests for RegexMethod."""

    @pytest.mark.asyncio
    async def test_extract_single_match(self, regex_method, sample_html):
        """Test extracting a single match."""
        instr = Instruction("email", r"[\w\.-]+@[\w\.-]+\.\w+", method="regex")
        result = await regex_method.extract(sample_html, instr)
        assert result == "support@example.com"

    @pytest.mark.asyncio
    async def test_extract_multiple_matches(self, regex_method, sample_html):
        """Test extracting multiple matches."""
        instr = Instruction("prices", r"\$[\d,.]+", method="regex", multiple=True)
        result = await regex_method.extract(sample_html, instr)
        assert result == ["$29.99", "$49.99", "$99.99"]

    @pytest.mark.asyncio
    async def test_extract_with_group(self, regex_method, sample_html):
        """Test extracting with a specific capture group."""
        instr = Instruction(
            "phone_digits",
            r"Phone:\s*(\+[\d\-]+)",
            method="regex",
            regex_group=1,
        )
        result = await regex_method.extract(sample_html, instr)
        assert result == "+1-555-123-4567"

    @pytest.mark.asyncio
    async def test_extract_date_pattern(self, regex_method, sample_html):
        """Test extracting date pattern."""
        instr = Instruction("date", r"\d{4}-\d{2}-\d{2}", method="regex")
        result = await regex_method.extract(sample_html, instr)
        assert result == "2024-01-15"

    @pytest.mark.asyncio
    async def test_extract_with_limit(self, regex_method, sample_html):
        """Test extracting with limit."""
        instr = Instruction("prices", r"\$[\d,.]+", method="regex", multiple=True, limit=2)
        result = await regex_method.extract(sample_html, instr)
        assert len(result) == 2
        assert result == ["$29.99", "$49.99"]

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_default(self, regex_method, sample_html):
        """Test that missing pattern returns default."""
        instr = Instruction("missing", r"ZZZZNOTFOUND", method="regex", default="N/A")
        result = await regex_method.extract(sample_html, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_extract_with_filter(self, regex_method, sample_html):
        """Test extracting with filter."""
        instr = Instruction(
            "high_prices",
            r"\$[\d,.]+",
            method="regex",
            multiple=True,
            filter=r"\$[4-9]\d",
        )
        result = await regex_method.extract(sample_html, instr)
        assert result == ["$49.99", "$99.99"]

    @pytest.mark.asyncio
    async def test_extract_multiple_groups(self, regex_method):
        """Test extracting with multiple capture groups."""
        html = "Product: Widget (SKU: ABC123) - Price: $50"
        instr = Instruction(
            "sku",
            r"SKU:\s*(\w+)",
            method="regex",
            regex_group=1,
        )
        result = await regex_method.extract(html, instr)
        assert result == "ABC123"

    @pytest.mark.asyncio
    async def test_method_name(self, regex_method):
        """Test method name property."""
        assert regex_method.name == "regex"
