"""Tests for JSONPathMethod."""

import pytest

from yoinkr.core.methods.jsonpath import JSONPathMethod
from yoinkr.core.types import Instruction


@pytest.fixture
def method():
    """Create a JSONPathMethod instance."""
    return JSONPathMethod()


@pytest.fixture
def sample_json():
    """Sample JSON data as string."""
    return """{
        "title": "Test Product",
        "price": 29.99,
        "tags": ["electronics", "gadget", "new"],
        "details": {
            "brand": "TestBrand",
            "model": "X100",
            "specs": {
                "weight": "500g",
                "dimensions": "10x5x2"
            }
        },
        "variants": [
            {"color": "red", "stock": 10},
            {"color": "blue", "stock": 5},
            {"color": "green", "stock": 0}
        ]
    }"""


@pytest.fixture
def sample_json_dict():
    """Sample JSON data as dict."""
    return {
        "title": "Test Product",
        "price": 29.99,
        "tags": ["electronics", "gadget", "new"],
        "details": {
            "brand": "TestBrand",
            "model": "X100",
        },
        "items": [
            {"name": "Item 1", "value": 100},
            {"name": "Item 2", "value": 200},
        ],
    }


class TestJSONPathMethod:
    """Tests for JSONPathMethod."""

    def test_name(self, method):
        """Test method name."""
        assert method.name == "jsonpath"

    @pytest.mark.asyncio
    async def test_simple_field(self, method, sample_json):
        """Test simple field extraction."""
        instr = Instruction("title", "$.title", method="jsonpath")
        result = await method.extract(sample_json, instr)
        assert result == "Test Product"

    @pytest.mark.asyncio
    async def test_numeric_field(self, method, sample_json):
        """Test numeric field extraction."""
        instr = Instruction("price", "$.price", method="jsonpath")
        result = await method.extract(sample_json, instr)
        assert result == 29.99

    @pytest.mark.asyncio
    async def test_nested_field(self, method, sample_json):
        """Test nested field extraction."""
        instr = Instruction("brand", "$.details.brand", method="jsonpath")
        result = await method.extract(sample_json, instr)
        assert result == "TestBrand"

    @pytest.mark.asyncio
    async def test_deep_nested_field(self, method, sample_json):
        """Test deeply nested field extraction."""
        instr = Instruction("weight", "$.details.specs.weight", method="jsonpath")
        result = await method.extract(sample_json, instr)
        assert result == "500g"

    @pytest.mark.asyncio
    async def test_array_index(self, method, sample_json):
        """Test array index access."""
        instr = Instruction("first_tag", "$.tags[0]", method="jsonpath")
        result = await method.extract(sample_json, instr)
        assert result == "electronics"

    @pytest.mark.asyncio
    async def test_array_all_elements(self, method, sample_json):
        """Test extracting all array elements."""
        instr = Instruction("tags", "$.tags[*]", method="jsonpath", multiple=True)
        result = await method.extract(sample_json, instr)
        assert result == ["electronics", "gadget", "new"]

    @pytest.mark.asyncio
    async def test_array_field_from_objects(self, method, sample_json):
        """Test extracting field from array of objects."""
        instr = Instruction("colors", "$.variants[*].color", method="jsonpath", multiple=True)
        result = await method.extract(sample_json, instr)
        assert result == ["red", "blue", "green"]

    @pytest.mark.asyncio
    async def test_recursive_descent(self, method, sample_json):
        """Test recursive descent to find field at any level."""
        instr = Instruction("brand", "$..brand", method="jsonpath")
        result = await method.extract(sample_json, instr)
        assert result == "TestBrand"

    @pytest.mark.asyncio
    async def test_dict_source(self, method, sample_json_dict):
        """Test extraction from dict source."""
        instr = Instruction("title", "$.title", method="jsonpath")
        result = await method.extract(sample_json_dict, instr)
        assert result == "Test Product"

    @pytest.mark.asyncio
    async def test_not_found_default(self, method, sample_json):
        """Test default value when field not found."""
        instr = Instruction("missing", "$.nonexistent", method="jsonpath", default="N/A")
        result = await method.extract(sample_json, instr)
        assert result == "N/A"

    @pytest.mark.asyncio
    async def test_filter(self, method, sample_json):
        """Test filter on results."""
        instr = Instruction(
            "colors", "$.variants[*].color", method="jsonpath", multiple=True, filter="^b"
        )
        result = await method.extract(sample_json, instr)
        assert result == ["blue"]

    @pytest.mark.asyncio
    async def test_limit(self, method, sample_json):
        """Test limit on results."""
        instr = Instruction(
            "colors", "$.variants[*].color", method="jsonpath", multiple=True, limit=2
        )
        result = await method.extract(sample_json, instr)
        assert len(result) == 2
        assert result == ["red", "blue"]

    @pytest.mark.asyncio
    async def test_html_with_json_script(self, method):
        """Test extracting JSON from HTML script tag."""
        html = """
        <html>
            <head>
                <script type="application/json">
                    {"name": "Product", "price": 99}
                </script>
            </head>
        </html>
        """
        instr = Instruction("name", "$.name", method="jsonpath")
        result = await method.extract(html, instr)
        assert result == "Product"

    @pytest.mark.asyncio
    async def test_html_with_ld_json(self, method):
        """Test extracting JSON-LD from HTML."""
        html = """
        <html>
            <head>
                <script type="application/ld+json">
                    {"@type": "Product", "name": "Widget"}
                </script>
            </head>
        </html>
        """
        instr = Instruction("name", "$.name", method="jsonpath")
        result = await method.extract(html, instr)
        assert result == "Widget"

    @pytest.mark.asyncio
    async def test_invalid_json_returns_default(self, method):
        """Test that invalid JSON returns default."""
        instr = Instruction("field", "$.field", method="jsonpath", default="fallback")
        result = await method.extract("not valid json", instr)
        assert result == "fallback"

    @pytest.mark.asyncio
    async def test_root_access(self, method):
        """Test accessing root with $."""
        data = {"a": 1, "b": 2}
        instr = Instruction("root", "$", method="jsonpath")
        result = await method.extract(data, instr)
        assert result == {"a": 1, "b": 2}

    @pytest.mark.asyncio
    async def test_multiple_false_returns_first(self, method, sample_json):
        """Test that multiple=False returns first result."""
        instr = Instruction("color", "$.variants[*].color", method="jsonpath", multiple=False)
        result = await method.extract(sample_json, instr)
        assert result == "red"
