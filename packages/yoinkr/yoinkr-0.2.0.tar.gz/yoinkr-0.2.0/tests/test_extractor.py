"""Tests for the Extractor pipeline."""

import pytest

from yoinkr.core.extractor import Extractor, MethodRegistry
from yoinkr.core.types import Instruction, Method


@pytest.fixture
def extractor():
    return Extractor()


@pytest.fixture
def registry():
    return MethodRegistry()


class TestMethodRegistry:
    """Tests for MethodRegistry."""

    def test_default_methods_registered(self, registry):
        """Test that default methods are registered."""
        methods = registry.available_methods()
        assert "css" in methods
        assert "xpath" in methods
        assert "regex" in methods
        assert "text" in methods
        assert "meta" in methods

    def test_get_method(self, registry):
        """Test getting a method."""
        method = registry.get("css")
        assert method.name == "css"

    def test_get_unknown_method_raises(self, registry):
        """Test that getting unknown method raises error."""
        with pytest.raises(ValueError, match="Unknown method"):
            registry.get("unknown")


class TestExtractor:
    """Tests for Extractor."""

    @pytest.mark.asyncio
    async def test_extract_single_instruction(self, extractor, sample_html):
        """Test extracting with single instruction."""
        instructions = [Instruction("title", "h1.main-title")]
        result = await extractor.extract(sample_html, instructions)

        assert "data" in result
        assert result["data"]["title"] == "Welcome to Test Page"
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_extract_multiple_instructions(self, extractor, sample_html):
        """Test extracting with multiple instructions."""
        instructions = [
            Instruction("title", "h1.main-title"),
            Instruction("description", ".description"),
            Instruction("email", r"[\w\.-]+@[\w\.-]+\.\w+", method="regex"),
        ]
        result = await extractor.extract(sample_html, instructions)

        assert result["data"]["title"] == "Welcome to Test Page"
        assert "test page" in result["data"]["description"].lower()
        assert result["data"]["email"] == "support@example.com"

    @pytest.mark.asyncio
    async def test_extract_with_transform(self, extractor, sample_html):
        """Test extracting with transform."""
        instructions = [
            Instruction("price", ".price", transform="float"),
            Instruction("title_lower", "h1.main-title", transform="lowercase"),
        ]
        result = await extractor.extract(sample_html, instructions)

        assert result["data"]["price"] == 29.99
        assert result["data"]["title_lower"] == "welcome to test page"

    @pytest.mark.asyncio
    async def test_extract_multiple_with_transform(self, extractor, sample_html):
        """Test extracting multiple values with transform."""
        instructions = [
            Instruction("prices", ".price", multiple=True, transform="float"),
        ]
        result = await extractor.extract(sample_html, instructions)

        assert result["data"]["prices"] == [29.99, 49.99, 99.99]

    @pytest.mark.asyncio
    async def test_extract_nested_children(self, extractor, sample_html):
        """Test extracting with nested children."""
        instructions = [
            Instruction(
                name="products",
                find=".product",
                multiple=True,
                children=[
                    Instruction("name", ".product-name"),
                    Instruction("price", ".price", transform="float"),
                    Instruction("link", ".product-link", attribute="href"),
                ],
            )
        ]
        result = await extractor.extract(sample_html, instructions)

        products = result["data"]["products"]
        assert len(products) == 3
        assert products[0]["name"] == "Product One"
        assert products[0]["price"] == 29.99
        assert products[0]["link"] == "/products/1"

    @pytest.mark.asyncio
    async def test_extract_nested_with_limit(self, extractor, sample_html):
        """Test extracting nested with limit."""
        instructions = [
            Instruction(
                name="products",
                find=".product",
                multiple=True,
                limit=2,
                children=[
                    Instruction("name", ".product-name"),
                ],
            )
        ]
        result = await extractor.extract(sample_html, instructions)

        products = result["data"]["products"]
        assert len(products) == 2

    @pytest.mark.asyncio
    async def test_extract_required_field_missing(self, extractor, sample_html):
        """Test that missing required field adds error."""
        instructions = [
            Instruction("missing", ".does-not-exist", required=True),
        ]
        result = await extractor.extract(sample_html, instructions)

        assert result["data"]["missing"] is None
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "missing"
        assert "Required" in result["errors"][0]["error"]

    @pytest.mark.asyncio
    async def test_extract_with_default(self, extractor, sample_html):
        """Test extracting with default value."""
        instructions = [
            Instruction("missing", ".does-not-exist", default="N/A"),
        ]
        result = await extractor.extract(sample_html, instructions)

        assert result["data"]["missing"] == "N/A"

    @pytest.mark.asyncio
    async def test_extract_with_scope(self, extractor, sample_html):
        """Test extracting with scope."""
        instructions = [
            Instruction("first_product_name", ".product-name", scope=".product"),
        ]
        result = await extractor.extract(sample_html, instructions)

        assert result["data"]["first_product_name"] == "Product One"

    @pytest.mark.asyncio
    async def test_transform_int(self, extractor):
        """Test int transform."""
        html = "<div class='count'>42 items</div>"
        instructions = [Instruction("count", ".count", transform="int")]
        result = await extractor.extract(html, instructions)

        assert result["data"]["count"] == 42

    @pytest.mark.asyncio
    async def test_transform_clean(self, extractor):
        """Test clean transform."""
        html = "<div class='text'>  Hello    World  </div>"
        instructions = [Instruction("text", ".text", transform="clean")]
        result = await extractor.extract(html, instructions)

        assert result["data"]["text"] == "Hello World"

    @pytest.mark.asyncio
    async def test_transform_bool(self, extractor):
        """Test bool transform."""
        html = "<div class='active'>true</div>"
        instructions = [Instruction("active", ".active", transform="bool")]
        result = await extractor.extract(html, instructions)

        assert result["data"]["active"] is True

    @pytest.mark.asyncio
    async def test_register_custom_transform(self, extractor):
        """Test registering custom transform."""
        extractor.register_transform("reverse", lambda x: x[::-1] if isinstance(x, str) else x)

        html = "<div class='text'>Hello</div>"
        instructions = [Instruction("text", ".text", transform="reverse")]
        result = await extractor.extract(html, instructions)

        assert result["data"]["text"] == "olleH"

    @pytest.mark.asyncio
    async def test_extract_handles_exception(self, extractor):
        """Test that extraction handles exceptions gracefully."""
        instructions = [
            # Invalid XPath should cause an error
            Instruction("bad", "[[[invalid", method="xpath"),
        ]
        result = await extractor.extract("<html></html>", instructions)

        assert result["data"]["bad"] is None
        assert len(result["errors"]) == 1


class TestExtractorNested:
    """Tests for nested extraction with sample_html_nested fixture."""

    @pytest.mark.asyncio
    async def test_extract_articles(self, extractor, sample_html_nested):
        """Test extracting nested article data."""
        instructions = [
            Instruction(
                name="articles",
                find=".post",
                multiple=True,
                children=[
                    Instruction("title", ".title"),
                    Instruction("author", ".author"),
                    Instruction("date", "time", attribute="datetime"),
                    Instruction("content", ".content"),
                ],
            )
        ]
        result = await extractor.extract(sample_html_nested, instructions)

        articles = result["data"]["articles"]
        assert len(articles) == 2

        assert articles[0]["title"] == "First Article"
        assert articles[0]["author"] == "John Doe"
        assert articles[0]["date"] == "2024-01-01"

        assert articles[1]["title"] == "Second Article"
        assert articles[1]["author"] == "Jane Smith"
