"""Tests for Meta extraction method."""

import pytest

from yoinkr.core.methods.meta import MetaMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def meta_method():
    return MetaMethod()


class TestMetaMethod:
    """Tests for MetaMethod."""

    @pytest.mark.asyncio
    async def test_extract_meta_name(self, meta_method, sample_html):
        """Test extracting meta tag by name."""
        instr = Instruction("description", "description", method="meta")
        result = await meta_method.extract(sample_html, instr)
        assert result == "A test page for scraping"

    @pytest.mark.asyncio
    async def test_extract_meta_property(self, meta_method, sample_html):
        """Test extracting meta tag by property (Open Graph)."""
        instr = Instruction("og_title", "og:title", method="meta")
        result = await meta_method.extract(sample_html, instr)
        assert result == "OG Test Title"

    @pytest.mark.asyncio
    async def test_extract_og_image(self, meta_method, sample_html):
        """Test extracting Open Graph image."""
        instr = Instruction("og_image", "og:image", method="meta")
        result = await meta_method.extract(sample_html, instr)
        assert result == "https://example.com/image.jpg"

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_default(self, meta_method, sample_html):
        """Test that missing meta returns default."""
        instr = Instruction("missing", "nonexistent-meta", method="meta", default="N/A")
        result = await meta_method.extract(sample_html, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_none(self, meta_method, sample_html):
        """Test that missing meta returns None when no default."""
        instr = Instruction("missing", "nonexistent-meta", method="meta")
        result = await meta_method.extract(sample_html, instr)
        assert result is None

    @pytest.mark.asyncio
    async def test_method_name(self, meta_method):
        """Test method name property."""
        assert meta_method.name == "meta"

    @pytest.mark.asyncio
    async def test_extract_with_filter(self, meta_method):
        """Test extracting with filter."""
        html = """
        <html><head>
            <meta property="og:image" content="https://example.com/small.jpg">
        </head></html>
        """
        instr = Instruction(
            "og_image",
            "og:image",
            method="meta",
            filter=r"large\.jpg$",
        )
        result = await meta_method.extract(html, instr)
        # Should not match because filter doesn't match
        assert result is None
