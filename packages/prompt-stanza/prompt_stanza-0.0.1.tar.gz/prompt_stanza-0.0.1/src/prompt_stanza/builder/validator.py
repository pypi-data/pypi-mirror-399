"""Input validator for schema-based validation."""

from typing import Any

import tiktoken

from ..exceptions import ValidationError
from ..models import SchemaField


class Validator:
    """
    Validator for input validation and sanitization based on schema rules.

    Handles:
    - Required field validation
    - Type validation and conversion
    - Length constraints (min_length, max_length)
    - Default value application
    """

    @staticmethod
    def validate_and_sanitize(
        schema: list[SchemaField],
        inputs: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Validate and sanitize inputs based on schema rules.

        Args:
            schema: List of schema field definitions
            inputs: Input values to validate
            **kwargs: Additional inputs from kwargs

        Returns:
            Validated and sanitized inputs

        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        all_inputs = {**inputs, **kwargs}

        # If no schema, pass through all inputs without validation
        if not schema:
            return all_inputs

        for field in schema:
            field_name = field.name
            value = all_inputs.get(field_name)

            # Check required fields
            if field.required and value is None:
                if field.default is not None:
                    value = field.default
                else:
                    raise ValidationError(f"Required field '{field_name}' is missing")

            # Apply default if value is missing
            if value is None and field.default is not None:
                value = field.default

            # Skip validation if value is still None and not required
            if value is None:
                continue

            # Type validation
            validated_value = Validator._validate_type(field, value)

            # Length validation for strings
            if field.type == "str" and isinstance(validated_value, str):
                validated_value = Validator._validate_length(field, validated_value)

            # Token count validation for strings
            if field.type == "str" and isinstance(validated_value, str) and field.max_tokens:
                validated_value = Validator._validate_tokens(field, validated_value)

            # Block phrase validation for strings
            if field.type == "str" and isinstance(validated_value, str) and field.block_phrases:
                Validator._validate_block_phrases(field, validated_value)

            validated[field_name] = validated_value

        return validated

    @staticmethod
    def _validate_type(field: SchemaField, value: Any) -> Any:
        """
        Validate and convert value to expected type.

        Args:
            field: Schema field definition
            value: Value to validate

        Returns:
            Converted value

        Raises:
            ValidationError: If type conversion fails
        """
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }

        expected_type = type_map.get(field.type)
        if expected_type is None:
            raise ValidationError(f"Unknown type '{field.type}' for field '{field.name}'")

        # Try to convert to expected type
        if not isinstance(value, expected_type):
            try:
                if field.type == "bool":
                    # Handle boolean conversion specially
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes")
                    else:
                        value = bool(value)
                else:
                    value = expected_type(value)
            except (ValueError, TypeError) as e:
                raise ValidationError(
                    f"Field '{field.name}' expects type '{field.type}', "
                    f"got '{type(value).__name__}'"
                ) from e

        return value

    @staticmethod
    def _validate_length(field: SchemaField, value: str) -> str:
        """
        Validate string length constraints.

        Args:
            field: Schema field definition
            value: String value to validate

        Returns:
            Validated string (truncated if max_length exceeded)

        Raises:
            ValidationError: If min_length constraint is violated
        """
        if field.min_length is not None and len(value) < field.min_length:
            raise ValidationError(
                f"Field '{field.name}' must be at least {field.min_length} characters, "
                f"got {len(value)}"
            )

        if field.max_length is not None and len(value) > field.max_length:
            # Truncate to max_length (sanitization)
            value = value[: field.max_length]

        return value

    @staticmethod
    def _validate_tokens(field: SchemaField, value: str) -> str:
        """
        Validate token count and truncate if necessary.

        Args:
            field: Schema field definition
            value: String value to validate

        Returns:
            Validated string (truncated if max_tokens exceeded)
        """
        if field.max_tokens is None:
            return value

        try:
            # Use cl100k_base encoding (used by gpt-4, gpt-3.5-turbo)
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(value)

            if len(tokens) > field.max_tokens:
                # Truncate to max_tokens
                truncated_tokens = tokens[: field.max_tokens]
                value = encoding.decode(truncated_tokens)
        except Exception:
            # If tiktoken fails, fall back to character-based estimation (4 chars ≈ 1 token)
            estimated_tokens = len(value) // 4
            if estimated_tokens > field.max_tokens:
                estimated_chars = field.max_tokens * 4
                value = value[:estimated_chars]

        return value

    @staticmethod
    def _validate_block_phrases(field: SchemaField, value: str) -> None:
        """
        Validate that input does not contain blocked phrases.

        Args:
            field: Schema field definition
            value: String value to validate

        Raises:
            ValidationError: If blocked phrase is found
        """
        if not field.block_phrases:
            return

        value_lower = value.lower()

        for phrase in field.block_phrases:
            if phrase.lower() in value_lower:
                raise ValidationError(f"Field '{field.name}' contains blocked phrase: '{phrase}'")
