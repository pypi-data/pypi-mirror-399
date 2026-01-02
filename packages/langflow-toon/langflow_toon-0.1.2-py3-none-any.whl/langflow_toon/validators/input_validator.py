"""Input validation for TOON Converter."""

from typing import Any, Dict, List, Optional

from ..config.constants import (
    MAX_NESTING_DEPTH,
    MAX_ROWS,
    SUPPORTED_FORMATS
)
from ..models.data import ConversionConfig
from ..models.errors import ConversionError, ErrorDetail, ErrorSeverity


class InputValidator:
    """Validator for input data and configuration."""

    @staticmethod
    def validate_content(content: str) -> None:
        """
        Validate that content is not empty.

        Args:
            content: Input content string

        Raises:
            ConversionError: If content is empty or whitespace only
        """
        if not content or not content.strip():
            raise ConversionError(
                message="Input content cannot be empty",
                error_type="EMPTY_INPUT"
            )

    @staticmethod
    def validate_format(input_format: str) -> str:
        """
        Validate and normalize input format.

        Args:
            input_format: Input format string (case-insensitive)

        Returns:
            Normalized format string in uppercase

        Raises:
            ConversionError: If format is not supported
        """
        if not input_format:
            raise ConversionError(
                message="Input format must be specified",
                error_type="MISSING_FORMAT"
            )

        normalized = input_format.strip().upper()

        # Check if format is supported (check keys first: JSON, XML, CSV, HTML)
        if normalized not in SUPPORTED_FORMATS:
            # Also check against extensions and mime types
            all_formats = set()
            for fmt_group in SUPPORTED_FORMATS.values():
                all_formats.update(fmt_group)
            all_formats.update(SUPPORTED_FORMATS.keys())

            supported = ", ".join(sorted(SUPPORTED_FORMATS.keys()))
            raise ConversionError(
                message=f"Unsupported format '{input_format}'. Supported formats: {supported}",
                error_type="UNSUPPORTED_FORMAT"
            )

        return normalized

    @staticmethod
    def validate_config(config: ConversionConfig) -> List[ErrorDetail]:
        """
        Validate conversion configuration.

        Args:
            config: ConversionConfig to validate

        Returns:
            List of ErrorDetail objects (empty if valid)
        """
        errors = []

        # Validate delimiter if specified
        # config.delimiter.value is the enum value: "comma", "tab", or "pipe"
        valid_delimiter_values = {"comma", "tab", "pipe"}
        if config.delimiter and config.delimiter.value not in valid_delimiter_values:
            errors.append(ErrorDetail(
                severity=ErrorSeverity.WARNING,
                message=f"Invalid delimiter '{config.delimiter.value}'. Using default comma.",
                error_type="INVALID_DELIMITER"
            ))

        return errors

    @staticmethod
    def validate_structure_size(data: Any) -> Optional[ErrorDetail]:
        """
        Validate data structure size against limits.

        Args:
            data: Parsed data structure (dict, list, etc.)

        Returns:
            ErrorDetail if size exceeds limits, None otherwise
        """
        # Check row limit for lists
        if isinstance(data, list):
            if len(data) > MAX_ROWS:
                return ErrorDetail(
                    severity=ErrorSeverity.ERROR,
                    message=f"Data has {len(data)} rows, exceeding maximum of {MAX_ROWS}",
                    error_type="MAX_ROWS_EXCEEDED"
                )

        # Check row limit for dict values that are lists
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > MAX_ROWS:
                    return ErrorDetail(
                        severity=ErrorSeverity.ERROR,
                        message=f"Field '{key}' has {len(value)} rows, exceeding maximum of {MAX_ROWS}",
                        error_type="MAX_ROWS_EXCEEDED",
                        corrected_example=f"Consider splitting into smaller chunks or using pagination."
                    )

        return None

    @staticmethod
    def validate_nesting_depth(data: Any, current_depth: int = 0) -> Optional[ErrorDetail]:
        """
        Validate nesting depth of data structure.

        Args:
            data: Data structure to check
            current_depth: Current nesting depth

        Returns:
            ErrorDetail if depth exceeds limit, None otherwise
        """
        if current_depth > MAX_NESTING_DEPTH:
            return ErrorDetail(
                severity=ErrorSeverity.ERROR,
                message=f"Nesting depth {current_depth} exceeds maximum of {MAX_NESTING_DEPTH}",
                error_type="MAX_DEPTH_EXCEEDED"
            )

        if isinstance(data, dict):
            for value in data.values():
                result = InputValidator.validate_nesting_depth(value, current_depth + 1)
                if result:
                    return result

        elif isinstance(data, list):
            for item in data:
                result = InputValidator.validate_nesting_depth(item, current_depth + 1)
                if result:
                    return result

        return None

    @staticmethod
    def validate_csv_input(content: str, delimiter: str = ",") -> List[ErrorDetail]:
        """
        Validate CSV-specific constraints.

        Args:
            content: CSV content string
            delimiter: Delimiter character to use

        Returns:
            List of ErrorDetail objects (empty if valid)
        """
        errors = []
        lines = content.strip().split("\n")

        if len(lines) < 2:
            errors.append(ErrorDetail(
                severity=ErrorSeverity.WARNING,
                message="CSV appears to have no data rows (only header or empty)",
                error_type="CSV_NO_DATA",
                corrected_example="name,value\nitem1,100"
            ))
            return errors

        # Check for inconsistent column counts
        header_cols = len(lines[0].split(delimiter))
        for i, line in enumerate(lines[1:], start=2):
            if line.strip():  # Skip empty lines
                row_cols = len(line.split(delimiter))
                if row_cols != header_cols:
                    errors.append(ErrorDetail(
                        severity=ErrorSeverity.WARNING,
                        message=f"Row {i} has {row_cols} columns, expected {header_cols}",
                        line=i,
                        error_type="CSV_INCONSISTENT_COLUMNS"
                    ))

        return errors
