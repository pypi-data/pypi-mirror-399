"""Error model definitions for TOON Converter."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ErrorSeverity(Enum):
    """Error severity levels."""
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ErrorDetail:
    """Detailed error information with location and correction suggestions."""
    severity: ErrorSeverity
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    error_type: Optional[str] = None
    corrected_example: Optional[str] = None

    def format_message(self) -> str:
        """Format error message with location and example."""
        parts = []
        if self.line:
            parts.append(f"Line {self.line}")
        if self.column:
            parts.append(f"Column {self.column}")

        location = ", ".join(parts) if parts else "Unknown location"
        result = f"{self.severity.value} at {location}: {self.message}"

        if self.corrected_example:
            result += f"\n\nCorrected example:\n{self.corrected_example}"

        return result


class ConversionError(Exception):
    """Exception raised during conversion process."""

    def __init__(self, message: str, line: int = None, column: int = None,
                 error_type: str = None, example: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.error_type = error_type
        self.example = example
        super().__init__(message)

    def __str__(self):
        parts = []
        if self.line:
            parts.append(f"Line {self.line}")
        if self.column:
            parts.append(f"Column {self.column}")
        if self.error_type:
            parts.append(self.error_type)

        location = ", ".join(parts) if parts else "Unknown location"
        result = f"Error at {location}: {self.message}"

        if self.example:
            result += f"\n\nCorrected example:\n{self.example}"

        return result
