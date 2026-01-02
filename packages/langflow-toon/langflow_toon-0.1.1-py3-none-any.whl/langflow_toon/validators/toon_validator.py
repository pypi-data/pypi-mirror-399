"""TOON output validation for TOON Converter."""

from typing import Any, Optional

from ..models.errors import ErrorDetail, ErrorSeverity


class ToonValidator:
    """Validator for TOON format output."""

    @staticmethod
    def validate_toon_output(toon_string: str) -> Optional[ErrorDetail]:
        """
        Validate TOON format output string.

        Args:
            toon_string: TOON format string to validate

        Returns:
            ErrorDetail if validation fails, None otherwise
        """
        if not toon_string:
            return ErrorDetail(
                severity=ErrorSeverity.CRITICAL,
                message="TOON output is empty",
                error_type="EMPTY_TOON_OUTPUT"
            )

        # Basic structural validation
        if not ToonValidator._is_valid_structure(toon_string):
            return ErrorDetail(
                severity=ErrorSeverity.ERROR,
                message="TOON output has invalid structure",
                error_type="INVALID_TOON_STRUCTURE"
            )

        return None

    @staticmethod
    def _is_valid_structure(toon_string: str) -> bool:
        """
        Check basic TOON structure validity.

        Args:
            toon_string: TOON string to validate

        Returns:
            True if structure appears valid, False otherwise
        """
        content = toon_string.strip()

        # TOON should start with { (object) or [ (array) or be a primitive
        if not content:
            return False

        # Check for balanced braces/brackets
        stack = []
        pairs = {']': '[', '}': '{', ')': '('}

        for char in content:
            if char in '([{':
                stack.append(char)
            elif char in ')]}':
                if not stack or stack[-1] != pairs.get(char):
                    return False
                stack.pop()

        return len(stack) == 0

    @staticmethod
    def validate_token_reduction(original_tokens: int, toon_tokens: int) -> Optional[ErrorDetail]:
        """
        Validate token reduction meets expectations.

        Args:
            original_tokens: Token count of original format
            toon_tokens: Token count of TOON format

        Returns:
            ErrorDetail if reduction is too low or negative, None otherwise
        """
        if original_tokens <= 0:
            return None  # Can't calculate reduction without baseline

        reduction_pct = ((original_tokens - toon_tokens) / original_tokens) * 100

        # Warn if token reduction is less than 5%
        if reduction_pct < 5:
            return ErrorDetail(
                severity=ErrorSeverity.WARNING,
                message=f"Token reduction is only {reduction_pct:.1f}% (expected 5%+ for non-tabular data)",
                error_type="LOW_TOKEN_REDUCTION"
            )

        # Warn if TOON is larger than original
        if toon_tokens > original_tokens:
            increase_pct = ((toon_tokens - original_tokens) / original_tokens) * 100
            return ErrorDetail(
                severity=ErrorSeverity.WARNING,
                message=f"TOON output is {increase_pct:.1f}% larger than original",
                error_type="TOKEN_INCREASE"
            )

        return None

    @staticmethod
    def validate_data_integrity(original_data: Any, toon_data: Any) -> Optional[ErrorDetail]:
        """
        Validate that TOON data preserves original data integrity.

        Args:
            original_data: Original parsed data structure
            toon_data: TOON parsed data structure

        Returns:
            ErrorDetail if integrity check fails, None otherwise
        """
        if type(original_data) != type(toon_data):
            return ErrorDetail(
                severity=ErrorSeverity.ERROR,
                message=f"Type mismatch: original is {type(original_data).__name__}, TOON is {type(toon_data).__name__}",
                error_type="TYPE_MISMATCH"
            )

        # Check dict length
        if isinstance(original_data, dict) and isinstance(toon_data, dict):
            if len(original_data) != len(toon_data):
                return ErrorDetail(
                    severity=ErrorSeverity.ERROR,
                    message=f"Key count mismatch: original has {len(original_data)}, TOON has {len(toon_data)}",
                    error_type="KEY_COUNT_MISMATCH"
                )

        # Check list length
        if isinstance(original_data, list) and isinstance(toon_data, list):
            if len(original_data) != len(toon_data):
                return ErrorDetail(
                    severity=ErrorSeverity.ERROR,
                    message=f"Item count mismatch: original has {len(original_data)}, TOON has {len(toon_data)}",
                    error_type="ITEM_COUNT_MISMATCH"
                )

        return None
