"""Langflow custom component for TOON format conversion."""

from typing import Optional, Union

from langflow import CustomComponent
from langflow.base.io.text import TextComponent

from ..core.toon_converter import ToonConverter
from ..models.data import ConversionConfig, Delimiter


class ToonConverterComponent(CustomComponent):
    """
    Langflow custom component for converting JSON, XML, CSV, or HTML
    to TOON format for optimized token usage in LLM prompts.
    """

    display_name = "TOON Converter"
    description = "Convert JSON, XML, CSV, or HTML to TOON format for token optimization"

    # Input fields
    input_text: Optional[str] = None
    input_format: Optional[str] = None
    csv_delimiter: Optional[str] = "comma"
    auto_detect: bool = False
    sort_keys: bool = False
    ensure_ascii: bool = False

    # Output fields
    toon_output: Optional[str] = None
    original_tokens: Optional[int] = None
    toon_tokens: Optional[int] = None
    token_reduction: Optional[int] = None
    warnings: Optional[str] = None

    def build_config(self):
        """Build component configuration for Langflow UI."""
        return {
            "input_text": {
                "display_name": "Input Content",
                "info": "The content to convert to TOON format",
                "type": "str",
                "multiline": True,
            },
            "input_format": {
                "display_name": "Input Format",
                "info": "Format of input content (JSON, XML, CSV, HTML). Leave empty for auto-detection.",
                "type": "str",
                "options": ["JSON", "XML", "CSV", "HTML"],
            },
            "csv_delimiter": {
                "display_name": "CSV Delimiter",
                "info": "Delimiter for CSV files",
                "type": "str",
                "options": ["comma", "tab", "pipe"],
                "default": "comma",
            },
            "auto_detect": {
                "display_name": "Auto Detect Format",
                "info": "Automatically detect input format",
                "type": "bool",
                "default": False,
            },
            "sort_keys": {
                "display_name": "Sort Keys",
                "info": "Sort object keys alphabetically in TOON output",
                "type": "bool",
                "default": False,
            },
            "ensure_ascii": {
                "display_name": "Ensure ASCII",
                "info": "Encode non-ASCII characters as escape sequences",
                "type": "bool",
                "default": False,
            },
        }

    def build(self, input_text: str, input_format: Optional[str] = None,
              csv_delimiter: str = "comma", auto_detect: bool = False,
              sort_keys: bool = False, ensure_ascii: bool = False) -> Union[str, dict]:
        """
        Execute the TOON conversion.

        Args:
            input_text: Input content string
            input_format: Input format (JSON, XML, CSV, HTML)
            csv_delimiter: CSV delimiter (comma, tab, pipe)
            auto_detect: Whether to auto-detect format
            sort_keys: Whether to sort object keys alphabetically
            ensure_ascii: Whether to encode non-ASCII as escape sequences

        Returns:
            Dictionary with conversion results or TOON string
        """
        if not input_text:
            return {
                "toon_output": "",
                "original_tokens": 0,
                "toon_tokens": 0,
                "token_reduction": 0,
                "warnings": "No input provided"
            }

        try:
            # Initialize converter
            converter = ToonConverter()

            # Create config with all options
            config = ConversionConfig(
                delimiter=self._map_delimiter(csv_delimiter),
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii
            )

            # Perform conversion
            result = converter.convert(
                content=input_text,
                input_format=input_format,
                config=config,
                auto_detect=auto_detect
            )

            # Return as dictionary for Langflow
            return {
                "toon_output": result.toon_output,
                "original_tokens": result.original_tokens,
                "toon_tokens": result.toon_tokens,
                "token_reduction": result.token_reduction,
                "warnings": "\\n".join(result.warnings) if result.warnings else None
            }

        except Exception as e:
            # Return error information
            return {
                "toon_output": "",
                "original_tokens": 0,
                "toon_tokens": 0,
                "token_reduction": 0,
                "warnings": f"Conversion error: {str(e)}"
            }

    def _map_delimiter(self, delimiter_str: str) -> Delimiter:
        """Map delimiter string to Delimiter enum."""
        delimiter_map = {
            "comma": Delimiter.COMMA,
            "tab": Delimiter.TAB,
            "pipe": Delimiter.PIPE
        }
        return delimiter_map.get(delimiter_str.lower(), Delimiter.COMMA)
