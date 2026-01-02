"""Tests for core types."""

import pytest

from yoinkr.core.types import Instruction, Method, ScrapeOptions, ScrapeResult


class TestMethod:
    """Tests for Method enum."""

    def test_method_values(self):
        """Test that Method enum has expected values."""
        assert Method.CSS.value == "css"
        assert Method.XPATH.value == "xpath"
        assert Method.REGEX.value == "regex"
        assert Method.TEXT.value == "text"
        assert Method.META.value == "meta"

    def test_method_from_string(self):
        """Test creating Method from string."""
        assert Method("css") == Method.CSS
        assert Method("xpath") == Method.XPATH
        assert Method("regex") == Method.REGEX


class TestInstruction:
    """Tests for Instruction dataclass."""

    def test_basic_instruction(self):
        """Test creating a basic instruction."""
        instr = Instruction("title", "h1")
        assert instr.name == "title"
        assert instr.find == "h1"
        assert instr.method == Method.CSS
        assert instr.multiple is False
        assert instr.attribute is None
        assert instr.default is None

    def test_instruction_with_method_string(self):
        """Test creating instruction with string method."""
        instr = Instruction("links", "//a/@href", method="xpath")
        assert instr.method == Method.XPATH

    def test_instruction_with_method_enum(self):
        """Test creating instruction with Method enum."""
        instr = Instruction("pattern", r"\\d+", method=Method.REGEX)
        assert instr.method == Method.REGEX

    def test_instruction_multiple(self):
        """Test instruction with multiple=True."""
        instr = Instruction("items", ".item", multiple=True)
        assert instr.multiple is True

    def test_instruction_with_attribute(self):
        """Test instruction with attribute extraction."""
        instr = Instruction("image", "img.hero", attribute="src")
        assert instr.attribute == "src"

    def test_instruction_with_transform(self):
        """Test instruction with transform."""
        instr = Instruction("price", ".price", transform="float")
        assert instr.transform == "float"

    def test_instruction_with_children(self):
        """Test instruction with nested children."""
        children = [
            Instruction("name", ".product-name"),
            Instruction("price", ".price"),
        ]
        instr = Instruction("products", ".product", children=children, multiple=True)
        assert instr.children is not None
        assert len(instr.children) == 2

    def test_instruction_with_scope(self):
        """Test instruction with scope."""
        instr = Instruction("title", "h2", scope=".article")
        assert instr.scope == ".article"

    def test_instruction_with_filter(self):
        """Test instruction with filter."""
        instr = Instruction("links", "a", attribute="href", filter=r"^/products/")
        assert instr.filter == r"^/products/"

    def test_instruction_with_limit(self):
        """Test instruction with limit."""
        instr = Instruction("items", ".item", multiple=True, limit=5)
        assert instr.limit == 5

    def test_instruction_required(self):
        """Test required instruction."""
        instr = Instruction("title", "h1", required=True)
        assert instr.required is True


class TestScrapeOptions:
    """Tests for ScrapeOptions dataclass."""

    def test_default_options(self):
        """Test default scrape options."""
        opts = ScrapeOptions()
        assert opts.javascript is True
        assert opts.wait_for is None
        assert opts.wait_timeout == 30
        assert opts.headers == {}
        assert opts.cookies == {}
        assert opts.include_html is False
        assert opts.include_screenshot is False

    def test_custom_options(self):
        """Test custom scrape options."""
        opts = ScrapeOptions(
            javascript=False,
            wait_for=".loaded",
            wait_timeout=60,
            headers={"Authorization": "Bearer token"},
            proxy="http://proxy.example.com:8080",
        )
        assert opts.javascript is False
        assert opts.wait_for == ".loaded"
        assert opts.wait_timeout == 60
        assert "Authorization" in opts.headers
        assert opts.proxy == "http://proxy.example.com:8080"


class TestScrapeResult:
    """Tests for ScrapeResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful result."""
        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={"title": "Example", "price": 29.99},
        )
        assert result.success is True
        assert result.data["title"] == "Example"
        assert result.errors == []

    def test_failed_result(self):
        """Test creating a failed result."""
        result = ScrapeResult(
            url="https://example.com",
            success=False,
            data={},
            errors=[{"error": "Connection timeout"}],
        )
        assert result.success is False
        assert len(result.errors) == 1

    def test_result_with_metadata(self):
        """Test result with metadata."""
        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={"title": "Test"},
            status_code=200,
            final_url="https://example.com/redirected",
            page_title="Test Page",
            fetch_time=1.5,
            extract_time=0.1,
            total_time=1.6,
        )
        assert result.status_code == 200
        assert result.final_url == "https://example.com/redirected"
        assert result.fetch_time == 1.5

    def test_is_partial(self):
        """Test is_partial method."""
        # Successful with no errors
        result1 = ScrapeResult(url="https://example.com", success=True, data={})
        assert result1.is_partial() is False

        # Successful with errors (partial)
        result2 = ScrapeResult(
            url="https://example.com",
            success=True,
            data={"title": "Test"},
            errors=[{"field": "price", "error": "Not found"}],
        )
        assert result2.is_partial() is True

    def test_get_error_fields(self):
        """Test get_error_fields method."""
        result = ScrapeResult(
            url="https://example.com",
            success=True,
            data={},
            errors=[
                {"field": "price", "error": "Not found"},
                {"field": "description", "error": "Empty"},
                {"error": "General error"},  # No field - should be excluded
            ],
        )
        fields = result.get_error_fields()
        assert "price" in fields
        assert "description" in fields
        assert len(fields) == 2  # Only errors with 'field' key are included
