"""Tests for CSS extraction method."""

import pytest

from yoinkr.core.methods.css import CSSMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def css_method():
    return CSSMethod()


class TestCSSMethod:
    """Tests for CSSMethod."""

    @pytest.mark.asyncio
    async def test_extract_single_element(self, css_method, sample_html):
        """Test extracting a single element."""
        instr = Instruction("title", "h1.main-title")
        result = await css_method.extract(sample_html, instr)
        assert result == "Welcome to Test Page"

    @pytest.mark.asyncio
    async def test_extract_multiple_elements(self, css_method, sample_html):
        """Test extracting multiple elements."""
        instr = Instruction("prices", ".price", multiple=True)
        result = await css_method.extract(sample_html, instr)
        assert result == ["$29.99", "$49.99", "$99.99"]

    @pytest.mark.asyncio
    async def test_extract_attribute(self, css_method, sample_html):
        """Test extracting an attribute."""
        instr = Instruction("link", ".product-link", attribute="href")
        result = await css_method.extract(sample_html, instr)
        assert result == "/products/1"

    @pytest.mark.asyncio
    async def test_extract_multiple_attributes(self, css_method, sample_html):
        """Test extracting multiple attributes."""
        instr = Instruction("links", ".product-link", attribute="href", multiple=True)
        result = await css_method.extract(sample_html, instr)
        assert result == ["/products/1", "/products/2", "/products/3"]

    @pytest.mark.asyncio
    async def test_extract_with_limit(self, css_method, sample_html):
        """Test extracting with limit."""
        instr = Instruction("prices", ".price", multiple=True, limit=2)
        result = await css_method.extract(sample_html, instr)
        assert len(result) == 2
        assert result == ["$29.99", "$49.99"]

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_default(self, css_method, sample_html):
        """Test that missing element returns default."""
        instr = Instruction("missing", ".does-not-exist", default="N/A")
        result = await css_method.extract(sample_html, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_none(self, css_method, sample_html):
        """Test that missing element returns None when no default."""
        instr = Instruction("missing", ".does-not-exist")
        result = await css_method.extract(sample_html, instr)
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_with_filter(self, css_method, sample_html):
        """Test extracting with filter."""
        instr = Instruction("expensive_prices", ".price", multiple=True, filter=r"\$[4-9]\d")
        result = await css_method.extract(sample_html, instr)
        assert result == ["$49.99", "$99.99"]

    @pytest.mark.asyncio
    async def test_extract_data_attribute(self, css_method, sample_html):
        """Test extracting data attribute."""
        instr = Instruction("product_ids", ".product", attribute="data-id", multiple=True)
        result = await css_method.extract(sample_html, instr)
        assert result == ["1", "2", "3"]

    @pytest.mark.asyncio
    async def test_extract_image_src(self, css_method, sample_html):
        """Test extracting image src."""
        instr = Instruction("images", ".product img", attribute="src", multiple=True)
        result = await css_method.extract(sample_html, instr)
        assert result == ["/images/product1.jpg", "/images/product2.jpg", "/images/product3.jpg"]

    @pytest.mark.asyncio
    async def test_method_name(self, css_method):
        """Test method name property."""
        assert css_method.name == "css"
