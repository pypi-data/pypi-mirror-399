"""JSON to TOON converter."""

import json
from typing import Any, Dict, List, Optional

from ..converters.base import BaseConverter, ConversionConfig
from ..models.data import ConversionResult, TokenStatistics
from ..models.errors import ConversionError
from ..utils.error_formatter import format_parse_error


class JsonConverter(BaseConverter):
    """Converter for JSON input format."""

    def convert(self, content: str, config: ConversionConfig) -> ConversionResult:
        """
        Convert JSON content to TOON format.

        Args:
            content: JSON string content
            config: Conversion configuration

        Returns:
            ConversionResult with TOON output and statistics

        Raises:
            ConversionError: If JSON parsing fails
        """
        try:
            # Parse JSON
            parsed_data = json.loads(content)

            # Validate parsed data
            self._validate_parsed_data(parsed_data)

            # Convert to TOON using custom encoder
            from ..utils.toon_encoder import encode_toon
            toon_string = encode_toon(parsed_data)

            # Calculate statistics
            original_tokens = TokenStatistics.calculate(content)
            toon_tokens = TokenStatistics.calculate(toon_string)

            return ConversionResult(
                toon_output=toon_string,
                original_tokens=original_tokens,
                toon_tokens=toon_tokens,
                token_reduction=original_tokens - toon_tokens,
                warnings=[]
            )

        except json.JSONDecodeError as e:
            error_dict = format_parse_error(e, content)
            raise ConversionError(
                message=error_dict["message"],
                line=error_dict.get("line"),
                column=error_dict.get("column"),
                error_type=error_dict.get("error_type"),
                example=error_dict.get("corrected_example")
            )
        except Exception as e:
            raise ConversionError(
                message=f"JSON conversion failed: {str(e)}",
                error_type="JSON_CONVERSION_ERROR"
            )

    def _validate_parsed_data(self, data: Any) -> None:
        """Validate parsed JSON data structure."""
        # Depth and size validation inherited from BaseConverter
        super()._validate_parsed_data(data)

        # Additional JSON-specific validations can be added here
        pass
