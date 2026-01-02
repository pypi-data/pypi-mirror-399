"""XML to TOON converter."""

from typing import Any, Optional

try:
    import xmltodict
except ImportError:
    xmltodict = None

from ..converters.base import BaseConverter, ConversionConfig
from ..models.data import ConversionResult, TokenStatistics
from ..models.errors import ConversionError
from ..utils.error_formatter import format_parse_error


class XmlConverter(BaseConverter):
    """Converter for XML input format."""

    def convert(self, content: str, config: ConversionConfig) -> ConversionResult:
        """
        Convert XML content to TOON format.

        Args:
            content: XML string content
            config: Conversion configuration

        Returns:
            ConversionResult with TOON output and statistics

        Raises:
            ConversionError: If XML parsing fails or xmltodict not available
        """
        if xmltodict is None:
            raise ConversionError(
                message="xmltodict library is required for XML conversion. Install with: pip install xmltodict",
                error_type="MISSING_DEPENDENCY"
            )

        try:
            # Parse XML to dict
            parsed_data = xmltodict.parse(content)

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

        except Exception as e:
            error_dict = format_parse_error(e, content)
            raise ConversionError(
                message=f"XML conversion failed: {error_dict['message']}",
                line=error_dict.get("line"),
                column=error_dict.get("column"),
                error_type=error_dict.get("error_type", "XML_PARSE_ERROR"),
                example=error_dict.get("corrected_example")
            )

    def _validate_parsed_data(self, data: Any) -> None:
        """Validate parsed XML data structure."""
        # Depth and size validation inherited from BaseConverter
        super()._validate_parsed_data(data)

        # XML-specific: check for common XML-to-dict issues
        if isinstance(data, dict):
            # xmltodict wraps single elements in dicts, check for excessive nesting
            pass
