"""Base converter interface for TOON format conversion."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class ConversionConfig:
    """Configuration options for TOON conversion."""
    delimiter: str = ","
    indent: int = 2
    sort_keys: bool = False
    ensure_ascii: bool = False


class BaseConverter(ABC):
    """Abstract base class for format-specific TOON converters."""

    @abstractmethod
    def convert(self, input_data: str, config: ConversionConfig = None) -> str:
        """
        Convert input data to TOON format.

        Args:
            input_data: Raw input string in the source format
            config: Conversion configuration options

        Returns:
            TOON format string

        Raises:
            ValueError: If input data is malformed or invalid
        """
        pass

    def _parse_input(self, input_data: str) -> Any:
        """
        Parse input data into Python structures.

        Args:
            input_data: Raw input string

        Returns:
            Parsed Python data structure (dict, list, etc.)
        """
        pass

    def _validate_parsed_data(self, data: Any) -> None:
        """
        Validate parsed data meets constraints.

        Args:
            data: Parsed Python data structure

        Raises:
            ValueError: If data validation fails
        """
        # Check nesting depth
        depth = self._calculate_depth(data)
        from ..config.constants import MAX_NESTING_DEPTH
        if depth > MAX_NESTING_DEPTH:
            raise ValueError(
                f"Data nesting depth ({depth}) exceeds maximum ({MAX_NESTING_DEPTH})"
            )

        # Check row limit for tabular data
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    from ..config.constants import MAX_ROWS
                    if len(value) > MAX_ROWS:
                        raise ValueError(
                            f"Data row count ({len(value)}) exceeds maximum ({MAX_ROWS})"
                        )
        elif isinstance(data, list):
            from ..config.constants import MAX_ROWS
            if len(data) > MAX_ROWS:
                raise ValueError(
                    f"Data row count ({len(data)}) exceeds maximum ({MAX_ROWS})"
                )

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of a data structure."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._calculate_depth(v, current_depth + 1)
                for v in obj.values()
            )
        elif isinstance(obj, (list, tuple)):
            if not obj:
                return current_depth
            return max(
                self._calculate_depth(item, current_depth + 1)
                for item in obj
            )
        else:
            return current_depth
