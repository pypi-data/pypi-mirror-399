"""Tests for XPath extraction method."""

import pytest

from yoinkr.core.methods.xpath import XPathMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def xpath_method():
    return XPathMethod()


class TestXPathMethod:
    """Tests for XPathMethod."""

    @pytest.mark.asyncio
    async def test_extract_single_element(self, xpath_method, sample_html):
        """Test extracting a single element."""
        instr = Instruction("title", "//h1[@class='main-title']/text()", method="xpath")
        result = await xpath_method.extract(sample_html, instr)
        assert result == "Welcome to Test Page"

    @pytest.mark.asyncio
    async def test_extract_multiple_elements(self, xpath_method, sample_html):
        """Test extracting multiple elements."""
        instr = Instruction(
            "prices", "//span[@class='price']/text()", method="xpath", multiple=True
        )
        result = await xpath_method.extract(sample_html, instr)
        assert result == ["$29.99", "$49.99", "$99.99"]

    @pytest.mark.asyncio
    async def test_extract_attribute(self, xpath_method, sample_html):
        """Test extracting an attribute using XPath."""
        instr = Instruction(
            "links", "//a[@class='product-link']/@href", method="xpath", multiple=True
        )
        result = await xpath_method.extract(sample_html, instr)
        assert result == ["/products/1", "/products/2", "/products/3"]

    @pytest.mark.asyncio
    async def test_extract_with_limit(self, xpath_method, sample_html):
        """Test extracting with limit."""
        instr = Instruction(
            "names", "//h2[@class='product-name']/text()", method="xpath", multiple=True, limit=2
        )
        result = await xpath_method.extract(sample_html, instr)
        assert len(result) == 2
        assert result == ["Product One", "Product Two"]

    @pytest.mark.asyncio
    async def test_extract_not_found_returns_default(self, xpath_method, sample_html):
        """Test that missing element returns default."""
        instr = Instruction("missing", "//div[@class='nonexistent']", method="xpath", default="N/A")
        result = await xpath_method.extract(sample_html, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_extract_element_text_content(self, xpath_method, sample_html):
        """Test extracting element text content."""
        instr = Instruction("description", "//p[@class='description']", method="xpath")
        result = await xpath_method.extract(sample_html, instr)
        assert result == "This is a test page for the universal scraper."

    @pytest.mark.asyncio
    async def test_extract_with_filter(self, xpath_method, sample_html):
        """Test extracting with filter."""
        instr = Instruction(
            "product_links",
            "//a[@class='product-link']/@href",
            method="xpath",
            multiple=True,
            filter=r"/products/[12]$",
        )
        result = await xpath_method.extract(sample_html, instr)
        assert result == ["/products/1", "/products/2"]

    @pytest.mark.asyncio
    async def test_method_name(self, xpath_method):
        """Test method name property."""
        assert xpath_method.name == "xpath"
