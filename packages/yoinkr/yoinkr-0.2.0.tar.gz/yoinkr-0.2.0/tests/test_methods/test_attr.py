"""Tests for AttrMethod and MultiAttrMethod."""

import pytest

from yoinkr.core.methods.attr import AttrMethod, MultiAttrMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def method():
    """Create an AttrMethod instance."""
    return AttrMethod()


@pytest.fixture
def multi_method():
    """Create a MultiAttrMethod instance."""
    return MultiAttrMethod()


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <html>
        <body>
            <img class="product-image" src="/images/product.jpg" alt="Product Image" data-id="123">
            <a href="https://example.com" class="link primary" target="_blank" title="Example">Link</a>
            <a href="https://other.com" class="link secondary">Other Link</a>
            <div class="item" data-price="29.99" data-stock="10" data-sku="ABC123">Item 1</div>
            <div class="item" data-price="49.99" data-stock="5" data-sku="DEF456">Item 2</div>
            <div class="item" data-price="19.99" data-stock="0" data-sku="GHI789">Item 3</div>
            <input type="text" name="email" value="test@example.com" placeholder="Enter email">
        </body>
    </html>
    """


class TestAttrMethod:
    """Tests for AttrMethod."""

    def test_name(self, method):
        """Test method name."""
        assert method.name == "attr"

    @pytest.mark.asyncio
    async def test_simple_attribute(self, method, sample_html):
        """Test simple attribute extraction with @ syntax."""
        instr = Instruction("src", "img@src", method="attr")
        result = await method.extract(sample_html, instr)
        assert result == "/images/product.jpg"

    @pytest.mark.asyncio
    async def test_href_attribute(self, method, sample_html):
        """Test href extraction."""
        instr = Instruction("url", "a@href", method="attr")
        result = await method.extract(sample_html, instr)
        assert result == "https://example.com"

    @pytest.mark.asyncio
    async def test_multiple_attributes(self, method, sample_html):
        """Test extracting multiple href values."""
        instr = Instruction("urls", "a@href", method="attr", multiple=True)
        result = await method.extract(sample_html, instr)
        assert result == ["https://example.com", "https://other.com"]

    @pytest.mark.asyncio
    async def test_data_attribute(self, method, sample_html):
        """Test data-* attribute extraction."""
        instr = Instruction("id", "img@data-id", method="attr")
        result = await method.extract(sample_html, instr)
        assert result == "123"

    @pytest.mark.asyncio
    async def test_data_attribute_multiple(self, method, sample_html):
        """Test multiple data attribute extraction."""
        instr = Instruction("prices", ".item@data-price", method="attr", multiple=True)
        result = await method.extract(sample_html, instr)
        assert result == ["29.99", "49.99", "19.99"]

    @pytest.mark.asyncio
    async def test_class_attribute(self, method, sample_html):
        """Test class attribute (joined as string)."""
        instr = Instruction("classes", "a.link@class", method="attr")
        result = await method.extract(sample_html, instr)
        assert result == "link primary"

    @pytest.mark.asyncio
    async def test_fallback_to_instruction_attribute(self, method, sample_html):
        """Test fallback to instruction.attribute when no @ in find."""
        instr = Instruction("alt", "img", method="attr", attribute="alt")
        result = await method.extract(sample_html, instr)
        assert result == "Product Image"

    @pytest.mark.asyncio
    async def test_not_found_default(self, method, sample_html):
        """Test default value when attribute not found."""
        instr = Instruction("missing", "img@nonexistent", method="attr", default="N/A")
        result = await method.extract(sample_html, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_element_not_found_default(self, method, sample_html):
        """Test default when element not found."""
        instr = Instruction("missing", ".nonexistent@href", method="attr", default="none")
        result = await method.extract(sample_html, instr)
        assert result == "none"

    @pytest.mark.asyncio
    async def test_filter(self, method, sample_html):
        """Test filter on attribute values."""
        instr = Instruction("urls", "a@href", method="attr", multiple=True, filter="example")
        result = await method.extract(sample_html, instr)
        assert result == ["https://example.com"]

    @pytest.mark.asyncio
    async def test_limit(self, method, sample_html):
        """Test limit on results."""
        instr = Instruction("prices", ".item@data-price", method="attr", multiple=True, limit=2)
        result = await method.extract(sample_html, instr)
        assert len(result) == 2
        assert result == ["29.99", "49.99"]

    @pytest.mark.asyncio
    async def test_input_value(self, method, sample_html):
        """Test extracting input value attribute."""
        instr = Instruction("email", "input[name='email']@value", method="attr")
        result = await method.extract(sample_html, instr)
        assert result == "test@example.com"

    @pytest.mark.asyncio
    async def test_complex_selector(self, method, sample_html):
        """Test complex CSS selector with attribute."""
        instr = Instruction("url", "a.link.primary@href", method="attr")
        result = await method.extract(sample_html, instr)
        assert result == "https://example.com"


class TestMultiAttrMethod:
    """Tests for MultiAttrMethod."""

    def test_name(self, multi_method):
        """Test method name."""
        assert multi_method.name == "multiattr"

    @pytest.mark.asyncio
    async def test_multiple_attrs_single(self, multi_method, sample_html):
        """Test extracting multiple attributes from single element."""
        instr = Instruction("link", "a@href,title,target", method="multiattr")
        result = await multi_method.extract(sample_html, instr)
        assert result == {
            "href": "https://example.com",
            "title": "Example",
            "target": "_blank",
        }

    @pytest.mark.asyncio
    async def test_multiple_attrs_multiple_elements(self, multi_method, sample_html):
        """Test extracting multiple attributes from multiple elements."""
        instr = Instruction(
            "items", ".item@data-price,data-stock,data-sku", method="multiattr", multiple=True
        )
        result = await multi_method.extract(sample_html, instr)
        assert len(result) == 3
        assert result[0] == {"data-price": "29.99", "data-stock": "10", "data-sku": "ABC123"}
        assert result[1] == {"data-price": "49.99", "data-stock": "5", "data-sku": "DEF456"}
        assert result[2] == {"data-price": "19.99", "data-stock": "0", "data-sku": "GHI789"}

    @pytest.mark.asyncio
    async def test_missing_attrs_return_none(self, multi_method, sample_html):
        """Test that missing attributes return None in dict."""
        instr = Instruction("link", "a@href,nonexistent", method="multiattr")
        result = await multi_method.extract(sample_html, instr)
        assert result == {"href": "https://example.com", "nonexistent": None}

    @pytest.mark.asyncio
    async def test_limit(self, multi_method, sample_html):
        """Test limit on multi-attr results."""
        instr = Instruction(
            "items",
            ".item@data-price,data-sku",
            method="multiattr",
            multiple=True,
            limit=2,
        )
        result = await multi_method.extract(sample_html, instr)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_not_found_default(self, multi_method, sample_html):
        """Test default when no elements found."""
        instr = Instruction("missing", ".nonexistent@href,title", method="multiattr", default={})
        result = await multi_method.extract(sample_html, instr)
        assert result == {}

    @pytest.mark.asyncio
    async def test_no_attrs_specified(self, multi_method, sample_html):
        """Test behavior when no attributes specified."""
        instr = Instruction("link", "a", method="multiattr", default="fallback")
        result = await multi_method.extract(sample_html, instr)
        assert result == "fallback"
