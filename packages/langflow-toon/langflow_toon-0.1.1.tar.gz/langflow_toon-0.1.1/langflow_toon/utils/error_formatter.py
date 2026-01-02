"""Error formatting utilities for user-friendly error messages."""

from typing import Optional


def format_error_message(
    message: str,
    line: int = None,
    column: int = None,
    error_type: str = None,
    corrected_example: str = None
) -> str:
    """
    Format a user-friendly error message with location and correction.

    Args:
        message: Human-readable error description
        line: Line number where error occurred
        column: Column number where error occurred
        error_type: Type of error (e.g., "INVALID_JSON", "MISSING_FIELD")
        corrected_example: Example of corrected input

    Returns:
        Formatted error message string
    """
    parts = []
    if line:
        parts.append(f"Line {line}")
    if column:
        parts.append(f"Column {column}")
    if error_type:
        parts.append(error_type)

    location = ", ".join(parts) if parts else "Unknown location"
    result = f"Error at {location}: {message}"

    if corrected_example:
        result += f"\n\nCorrected example:\n{corrected_example}"

    return result


def format_parse_error(error: Exception, content: str = None) -> dict:
    """
    Format a parse exception into a structured error dictionary.

    Args:
        error: The exception that occurred
        content: Optional content that caused the error

    Returns:
        Dictionary with error details
    """
    error_dict = {
        "severity": "ERROR",
        "message": str(error),
        "line": None,
        "column": None,
        "error_type": type(error).__name__,
        "corrected_example": None
    }

    # Try to extract line/column from common error types
    if hasattr(error, "lineno"):
        error_dict["line"] = error.lineno
    if hasattr(error, "colno"):
        error_dict["column"] = error.colno
    if hasattr(error, "msg"):
        error_dict["message"] = error.msg

    # JSON decode error handling
    if "JSONDecodeError" in type(error).__name__:
        error_dict["error_type"] = "INVALID_JSON"
        error_dict["message"] = f"Invalid JSON format: {error.msg}"

        # Try to generate a corrected example
        if content and error_dict.get("line"):
            lines = content.split("\n")
            error_line_idx = error_dict["line"] - 1
            if 0 <= error_line_idx < len(lines):
                error_dict["corrected_example"] = f"Line {error_dict['line']}: {lines[error_line_idx]}"

    return error_dict
