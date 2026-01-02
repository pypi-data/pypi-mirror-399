"""Tests for the validation system."""

import pytest

from yoinkr.core.validation import (
    ListFieldValidator,
    NumericFieldValidator,
    PatternFieldValidator,
    TextFieldValidator,
    ValidationConfig,
    ValidationResult,
    ValidationService,
)


class TestTextFieldValidator:
    """Tests for TextFieldValidator."""

    def test_valid_text(self):
        """Test valid text passes."""
        validator = TextFieldValidator()
        result = validator.validate("Hello World", "greeting")

        assert result.is_valid is True
        assert result.value == "Hello World"

    def test_required_empty_fails(self):
        """Test required empty field fails."""
        validator = TextFieldValidator(required=True)
        result = validator.validate("", "name")

        assert result.is_valid is False
        assert "empty" in result.error_message.lower()

    def test_required_none_fails(self):
        """Test required None field fails."""
        validator = TextFieldValidator(required=True)
        result = validator.validate(None, "name")

        assert result.is_valid is False

    def test_min_length(self):
        """Test minimum length validation."""
        validator = TextFieldValidator(min_length=5)

        assert validator.validate("Hello", "f").is_valid is True
        assert validator.validate("Hi", "f").is_valid is False

    def test_max_length(self):
        """Test maximum length validation."""
        validator = TextFieldValidator(max_length=5)

        assert validator.validate("Hello", "f").is_valid is True
        assert validator.validate("Hello World", "f").is_valid is False

    def test_pattern(self):
        """Test pattern validation."""
        validator = TextFieldValidator(pattern=r"^\d{3}-\d{4}$")

        assert validator.validate("123-4567", "phone").is_valid is True
        assert validator.validate("abc-defg", "phone").is_valid is False

    def test_strip_whitespace(self):
        """Test whitespace stripping."""
        validator = TextFieldValidator(strip_whitespace=True)
        result = validator.validate("  Hello  ", "text")

        assert result.value == "Hello"


class TestNumericFieldValidator:
    """Tests for NumericFieldValidator."""

    def test_valid_number(self):
        """Test valid number passes."""
        validator = NumericFieldValidator()
        result = validator.validate(42, "count")

        assert result.is_valid is True
        assert result.value == 42.0

    def test_string_number(self):
        """Test string number conversion."""
        validator = NumericFieldValidator()
        result = validator.validate("$29.99", "price")

        assert result.is_valid is True
        assert result.value == 29.99

    def test_required_none_fails(self):
        """Test required None fails."""
        validator = NumericFieldValidator(required=True)
        result = validator.validate(None, "count")

        assert result.is_valid is False

    def test_min_value(self):
        """Test minimum value validation."""
        validator = NumericFieldValidator(min_value=0)

        assert validator.validate(10, "f").is_valid is True
        assert validator.validate(-5, "f").is_valid is False

    def test_max_value(self):
        """Test maximum value validation."""
        validator = NumericFieldValidator(max_value=100)

        assert validator.validate(50, "f").is_valid is True
        assert validator.validate(150, "f").is_valid is False

    def test_allow_negative(self):
        """Test negative number handling."""
        no_neg = NumericFieldValidator(allow_negative=False)
        allow_neg = NumericFieldValidator(allow_negative=True)

        assert no_neg.validate(-5, "f").is_valid is False
        assert allow_neg.validate(-5, "f").is_valid is True

    def test_integer_only(self):
        """Test integer only validation."""
        validator = NumericFieldValidator(integer_only=True)

        result_int = validator.validate(42, "count")
        result_float = validator.validate(42.5, "count")

        assert result_int.is_valid is True
        assert result_int.value == 42
        assert result_float.is_valid is False

    def test_invalid_string(self):
        """Test invalid string handling."""
        validator = NumericFieldValidator(required=True)
        result = validator.validate("not a number", "count")

        assert result.is_valid is False


class TestPatternFieldValidator:
    """Tests for PatternFieldValidator."""

    def test_email_pattern(self):
        """Test email pattern validation."""
        validator = PatternFieldValidator(pattern_name="email")

        assert validator.validate("test@example.com", "email").is_valid is True
        assert validator.validate("invalid", "email").is_valid is False

    def test_url_pattern(self):
        """Test URL pattern validation."""
        validator = PatternFieldValidator(pattern_name="url")

        assert validator.validate("https://example.com", "url").is_valid is True
        assert validator.validate("not-a-url", "url").is_valid is False

    def test_custom_pattern(self):
        """Test custom pattern validation."""
        validator = PatternFieldValidator(pattern=r"^SKU-\d{4}$")

        assert validator.validate("SKU-1234", "sku").is_valid is True
        assert validator.validate("PRODUCT-1234", "sku").is_valid is False

    def test_required(self):
        """Test required field validation."""
        validator = PatternFieldValidator(pattern_name="email", required=True)

        assert validator.validate("", "email").is_valid is False
        assert validator.validate(None, "email").is_valid is False

    def test_must_provide_pattern(self):
        """Test that pattern or pattern_name is required."""
        with pytest.raises(ValueError, match="Must provide"):
            PatternFieldValidator()


class TestListFieldValidator:
    """Tests for ListFieldValidator."""

    def test_valid_list(self):
        """Test valid list passes."""
        validator = ListFieldValidator()
        result = validator.validate([1, 2, 3], "items")

        assert result.is_valid is True

    def test_required_none_fails(self):
        """Test required None fails."""
        validator = ListFieldValidator(required=True)
        result = validator.validate(None, "items")

        assert result.is_valid is False

    def test_not_a_list_fails(self):
        """Test non-list value fails."""
        validator = ListFieldValidator()
        result = validator.validate("not a list", "items")

        assert result.is_valid is False

    def test_min_items(self):
        """Test minimum items validation."""
        validator = ListFieldValidator(min_items=2)

        assert validator.validate([1, 2], "f").is_valid is True
        assert validator.validate([1], "f").is_valid is False

    def test_max_items(self):
        """Test maximum items validation."""
        validator = ListFieldValidator(max_items=3)

        assert validator.validate([1, 2], "f").is_valid is True
        assert validator.validate([1, 2, 3, 4], "f").is_valid is False

    def test_item_validator(self):
        """Test item validation."""
        item_val = NumericFieldValidator(min_value=0)
        validator = ListFieldValidator(item_validator=item_val)

        assert validator.validate([1, 2, 3], "f").is_valid is True
        assert validator.validate([1, -2, 3], "f").is_valid is False


class TestValidationService:
    """Tests for ValidationService."""

    @pytest.fixture
    def service(self):
        """Create validation service with common validators."""
        svc = ValidationService()
        svc.register_validator("title", TextFieldValidator(min_length=1, required=True))
        svc.register_validator("price", NumericFieldValidator(min_value=0))
        svc.register_validator("email", PatternFieldValidator(pattern_name="email"))
        return svc

    def test_validate_result(self, service):
        """Test validating extraction result."""
        data = {
            "title": "Product Name",
            "price": "$29.99",
            "email": "test@example.com",
        }

        results = service.validate_result(data)

        assert results["title"].is_valid is True
        assert results["price"].is_valid is True
        assert results["price"].value == 29.99
        assert results["email"].is_valid is True

    def test_get_valid_data(self, service):
        """Test getting valid data only."""
        data = {
            "title": "Product",
            "price": "$29.99",
            "description": "Not validated",  # Not in validators
        }

        valid = service.get_valid_data(data)

        assert valid["title"] == "Product"
        assert valid["price"] == 29.99
        assert valid["description"] == "Not validated"

    def test_is_valid(self, service):
        """Test is_valid check."""
        valid_data = {"title": "Product", "price": "29.99"}
        invalid_data = {"title": "", "price": "-10"}  # Empty required, negative

        assert service.is_valid(valid_data) is True
        assert service.is_valid(invalid_data) is False

    def test_get_errors(self, service):
        """Test getting error messages."""
        data = {"title": "", "price": "-10"}

        errors = service.get_errors(data)

        assert len(errors) == 2
        assert any("title" in e.lower() for e in errors)
        assert any("price" in e.lower() for e in errors)

    def test_raise_on_failure(self):
        """Test raising exception on failure."""
        from yoinkr.core.exceptions import ValidationError

        config = ValidationConfig(raise_on_failure=True)
        service = ValidationService(config)
        service.register_validator("name", TextFieldValidator(required=True))

        with pytest.raises(ValidationError):
            service.validate_result({"name": ""})
