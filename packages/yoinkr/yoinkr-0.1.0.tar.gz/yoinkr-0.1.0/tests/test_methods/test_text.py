"""Tests for Text extraction method."""

import pytest

from yoinkr.core.methods.text import TextMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def text_method():
    return TextMethod()


class TestTextMethod:
    """Tests for TextMethod."""

    @pytest.mark.asyncio
    async def test_extract_single_line(self, text_method, sample_html):
        """Test extracting a single line containing text."""
        instr = Instruction("contact", "contact us", method="text")
        result = await text_method.extract(sample_html, instr)
        assert "support@example.com" in result

    @pytest.mark.asyncio
    async def test_extract_multiple_lines(self, text_method, sample_html):
        """Test extracting multiple lines containing text."""
        instr = Instruction("product_mentions", "product", method="text", multiple=True)
        result = await text_method.extract(sample_html, instr)
        assert len(result) > 0
        assert all("product" in line.lower() for line in result)

    @pytest.mark.asyncio
    async def test_extract_case_insensitive(self, text_method, sample_html):
        """Test that text search is case insensitive."""
        instr = Instruction("title", "WELCOME", method="text")
        result = await text_method.extract(sample_html, instr)
        assert result is not None
        assert "welcome" in result.lower()

    @pytest.mark.asyncio
    async def test_extract_with_limit(self, text_method, sample_html):
        """Test extracting with limit."""
        instr = Instruction("product_lines", "product", method="text", multiple=True, limit=2)
        result = await text_method.extract(sample_html, instr)
        assert len(result) <= 2

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_default(self, text_method, sample_html):
        """Test that missing text returns default."""
        instr = Instruction("missing", "ZZZZNOTFOUND", method="text", default="N/A")
        result = await text_method.extract(sample_html, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_extract_phone(self, text_method, sample_html):
        """Test extracting line with phone."""
        instr = Instruction("phone_line", "phone", method="text")
        result = await text_method.extract(sample_html, instr)
        assert "+1-555-123-4567" in result

    @pytest.mark.asyncio
    async def test_method_name(self, text_method):
        """Test method name property."""
        assert text_method.name == "text"
