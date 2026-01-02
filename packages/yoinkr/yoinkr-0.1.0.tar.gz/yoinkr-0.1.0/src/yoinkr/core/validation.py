"""Validation system for extracted data."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class ValidationResult:
    """Result of field validation."""

    is_valid: bool
    value: Any
    original_value: Any
    field_name: str
    error_message: Optional[str] = None
    validation_type: str = ""


@dataclass
class ValidationConfig:
    """Configuration for validation behavior."""

    skip_empty: bool = True
    log_failures: bool = True
    raise_on_failure: bool = False
    custom_validators: dict[str, Callable[[Any], bool]] = field(default_factory=dict)


class FieldValidator(ABC):
    """Base class for field validators."""

    @abstractmethod
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """
        Validate a field value.

        Args:
            value: Value to validate
            field_name: Name of the field

        Returns:
            ValidationResult
        """
        pass


class TextFieldValidator(FieldValidator):
    """Validates text fields."""

    def __init__(
        self,
        min_length: int = 0,
        max_length: Optional[int] = None,
        required: bool = False,
        pattern: Optional[str] = None,
        strip_whitespace: bool = True,
    ) -> None:
        """
        Initialize text validator.

        Args:
            min_length: Minimum text length
            max_length: Maximum text length
            required: Whether field is required
            pattern: Regex pattern to match
            strip_whitespace: Whether to strip whitespace
        """
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.pattern = re.compile(pattern) if pattern else None
        self.strip_whitespace = strip_whitespace

    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate text field."""
        # Handle None/empty
        if value is None or value == "":
            if self.required:
                return ValidationResult(
                    is_valid=False,
                    value=value,
                    original_value=value,
                    field_name=field_name,
                    error_message=f"Required field '{field_name}' is empty",
                    validation_type="text",
                )
            return ValidationResult(True, value, value, field_name, validation_type="text")

        text = str(value)
        if self.strip_whitespace:
            text = text.strip()

        # Length checks
        if len(text) < self.min_length:
            return ValidationResult(
                False,
                text,
                value,
                field_name,
                f"Field '{field_name}' too short: {len(text)} < {self.min_length}",
                "text",
            )

        if self.max_length and len(text) > self.max_length:
            return ValidationResult(
                False,
                text,
                value,
                field_name,
                f"Field '{field_name}' too long: {len(text)} > {self.max_length}",
                "text",
            )

        # Pattern match
        if self.pattern and not self.pattern.search(text):
            return ValidationResult(
                False,
                text,
                value,
                field_name,
                f"Field '{field_name}' doesn't match required pattern",
                "text",
            )

        return ValidationResult(True, text, value, field_name, validation_type="text")


class NumericFieldValidator(FieldValidator):
    """Validates numeric fields."""

    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        required: bool = False,
        allow_negative: bool = True,
        integer_only: bool = False,
    ) -> None:
        """
        Initialize numeric validator.

        Args:
            min_value: Minimum value
            max_value: Maximum value
            required: Whether field is required
            allow_negative: Whether negative values are allowed
            integer_only: Whether only integers are allowed
        """
        self.min_value = min_value
        self.max_value = max_value
        self.required = required
        self.allow_negative = allow_negative
        self.integer_only = integer_only

    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate numeric field."""
        if value is None:
            if self.required:
                return ValidationResult(
                    False,
                    None,
                    value,
                    field_name,
                    f"Required numeric field '{field_name}' is missing",
                    "numeric",
                )
            return ValidationResult(True, None, value, field_name, validation_type="numeric")

        try:
            # Clean and parse
            if isinstance(value, str):
                cleaned = re.sub(r"[^\d.\-]", "", value)
                if not cleaned or cleaned == "-":
                    if self.required:
                        return ValidationResult(
                            False,
                            None,
                            value,
                            field_name,
                            f"Field '{field_name}' is not a valid number",
                            "numeric",
                        )
                    return ValidationResult(
                        True, None, value, field_name, validation_type="numeric"
                    )
                num = float(cleaned)
            else:
                num = float(value)

            # Integer check
            if self.integer_only and num != int(num):
                return ValidationResult(
                    False,
                    num,
                    value,
                    field_name,
                    f"Field '{field_name}' must be an integer",
                    "numeric",
                )

            if self.integer_only:
                num = int(num)

            # Negative check
            if not self.allow_negative and num < 0:
                return ValidationResult(
                    False,
                    num,
                    value,
                    field_name,
                    f"Field '{field_name}' cannot be negative",
                    "numeric",
                )

            # Range checks
            if self.min_value is not None and num < self.min_value:
                return ValidationResult(
                    False,
                    num,
                    value,
                    field_name,
                    f"Field '{field_name}' below minimum: {num} < {self.min_value}",
                    "numeric",
                )

            if self.max_value is not None and num > self.max_value:
                return ValidationResult(
                    False,
                    num,
                    value,
                    field_name,
                    f"Field '{field_name}' above maximum: {num} > {self.max_value}",
                    "numeric",
                )

            return ValidationResult(True, num, value, field_name, validation_type="numeric")

        except (ValueError, TypeError) as e:
            return ValidationResult(
                False,
                None,
                value,
                field_name,
                f"Field '{field_name}' is not a valid number: {e}",
                "numeric",
            )


class PatternFieldValidator(FieldValidator):
    """Validates fields against regex patterns."""

    COMMON_PATTERNS = {
        "email": r"^[\w\.-]+@[\w\.-]+\.\w+$",
        "url": r"^https?://[\w\.-]+",
        "phone": r"^[\d\s\+\-\(\)]+$",
        "date_iso": r"^\d{4}-\d{2}-\d{2}",
        "price": r"^\$?[\d,]+\.?\d*$",
        "currency": r"^[A-Z]{3}$",
        "slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    }

    def __init__(
        self,
        pattern: Optional[str] = None,
        pattern_name: Optional[str] = None,
        required: bool = False,
    ) -> None:
        """
        Initialize pattern validator.

        Args:
            pattern: Custom regex pattern
            pattern_name: Name of common pattern to use
            required: Whether field is required
        """
        if pattern_name and pattern_name in self.COMMON_PATTERNS:
            self.pattern = re.compile(self.COMMON_PATTERNS[pattern_name], re.IGNORECASE)
        elif pattern:
            self.pattern = re.compile(pattern)
        else:
            raise ValueError("Must provide either 'pattern' or 'pattern_name'")

        self.required = required

    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate field against pattern."""
        if value is None or value == "":
            if self.required:
                return ValidationResult(
                    False,
                    value,
                    value,
                    field_name,
                    f"Required field '{field_name}' is missing",
                    "pattern",
                )
            return ValidationResult(True, value, value, field_name, validation_type="pattern")

        text = str(value)
        if self.pattern.match(text):
            return ValidationResult(True, text, value, field_name, validation_type="pattern")

        return ValidationResult(
            False,
            text,
            value,
            field_name,
            f"Field '{field_name}' doesn't match required pattern",
            "pattern",
        )


class ListFieldValidator(FieldValidator):
    """Validates list fields."""

    def __init__(
        self,
        min_items: int = 0,
        max_items: Optional[int] = None,
        required: bool = False,
        item_validator: Optional[FieldValidator] = None,
    ) -> None:
        """
        Initialize list validator.

        Args:
            min_items: Minimum number of items
            max_items: Maximum number of items
            required: Whether field is required
            item_validator: Validator for individual items
        """
        self.min_items = min_items
        self.max_items = max_items
        self.required = required
        self.item_validator = item_validator

    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate list field."""
        if value is None:
            if self.required:
                return ValidationResult(
                    False,
                    None,
                    value,
                    field_name,
                    f"Required list field '{field_name}' is missing",
                    "list",
                )
            return ValidationResult(True, None, value, field_name, validation_type="list")

        if not isinstance(value, list):
            return ValidationResult(
                False,
                value,
                value,
                field_name,
                f"Field '{field_name}' is not a list",
                "list",
            )

        # Length checks
        if len(value) < self.min_items:
            return ValidationResult(
                False,
                value,
                value,
                field_name,
                f"Field '{field_name}' has too few items: {len(value)} < {self.min_items}",
                "list",
            )

        if self.max_items and len(value) > self.max_items:
            return ValidationResult(
                False,
                value,
                value,
                field_name,
                f"Field '{field_name}' has too many items: {len(value)} > {self.max_items}",
                "list",
            )

        # Validate items
        if self.item_validator:
            validated_items = []
            for i, item in enumerate(value):
                result = self.item_validator.validate(item, f"{field_name}[{i}]")
                if not result.is_valid:
                    return ValidationResult(
                        False,
                        value,
                        value,
                        field_name,
                        result.error_message,
                        "list",
                    )
                validated_items.append(result.value)
            return ValidationResult(
                True, validated_items, value, field_name, validation_type="list"
            )

        return ValidationResult(True, value, value, field_name, validation_type="list")


class ValidationService:
    """Service for validating extraction results."""

    def __init__(self, config: Optional[ValidationConfig] = None) -> None:
        """
        Initialize validation service.

        Args:
            config: Validation configuration
        """
        self.config = config or ValidationConfig()
        self.validators: dict[str, FieldValidator] = {}

    def register_validator(self, field_name: str, validator: FieldValidator) -> None:
        """
        Register a validator for a specific field.

        Args:
            field_name: Name of the field
            validator: Validator instance
        """
        self.validators[field_name] = validator

    def validate_result(self, data: dict[str, Any]) -> dict[str, ValidationResult]:
        """
        Validate all fields in extraction result.

        Args:
            data: Extracted data dictionary

        Returns:
            Dictionary of field names to ValidationResults
        """
        results: dict[str, ValidationResult] = {}

        for field_name, value in data.items():
            if field_name in self.validators:
                result = self.validators[field_name].validate(value, field_name)
                results[field_name] = result

                if not result.is_valid and self.config.raise_on_failure:
                    from .exceptions import ValidationError

                    raise ValidationError(
                        result.error_message or "Validation failed",
                        field=field_name,
                        value=value,
                    )

        return results

    def get_valid_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Return only valid fields with cleaned values.

        Args:
            data: Extracted data dictionary

        Returns:
            Dictionary with valid/cleaned values
        """
        results = self.validate_result(data)

        valid_data: dict[str, Any] = {}
        for field_name, result in results.items():
            if result.is_valid:
                valid_data[field_name] = result.value

        # Include unvalidated fields as-is
        for field_name, value in data.items():
            if field_name not in results:
                valid_data[field_name] = value

        return valid_data

    def is_valid(self, data: dict[str, Any]) -> bool:
        """
        Check if all validated fields are valid.

        Args:
            data: Extracted data dictionary

        Returns:
            True if all validated fields are valid
        """
        results = self.validate_result(data)
        return all(r.is_valid for r in results.values())

    def get_errors(self, data: dict[str, Any]) -> list[str]:
        """
        Get list of validation error messages.

        Args:
            data: Extracted data dictionary

        Returns:
            List of error messages
        """
        results = self.validate_result(data)
        return [r.error_message for r in results.values() if not r.is_valid and r.error_message]
