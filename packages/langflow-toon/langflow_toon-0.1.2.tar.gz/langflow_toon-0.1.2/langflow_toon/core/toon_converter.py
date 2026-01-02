"""Main TOON converter orchestrator."""

from typing import List, Optional

from ..config.constants import DELIMITER_MAP
from ..converters.base import BaseConverter
from ..converters.csv_converter import CsvConverter
from ..converters.html_converter import HtmlConverter
from ..converters.json_converter import JsonConverter
from ..converters.xml_converter import XmlConverter
from ..detectors.format_detector import FormatDetector
from ..models.data import ConversionConfig, ConversionResult, Delimiter, InputFormat
from ..models.errors import ConversionError, ErrorDetail, ErrorSeverity
from ..utils.memory_estimator import MemoryEstimate
from ..validators.input_validator import InputValidator
from ..validators.toon_validator import ToonValidator


class ToonConverter:
    """
    Main converter class that orchestrates format detection, conversion,
    and validation for TOON format output.
    """

    def __init__(self):
        """Initialize converter with available format converters."""
        self._converters = {
            InputFormat.JSON.value: JsonConverter(),
            InputFormat.XML.value: XmlConverter(),
            InputFormat.CSV.value: CsvConverter(),
            InputFormat.HTML.value: HtmlConverter(),
        }
        self.detector = FormatDetector()
        self.input_validator = InputValidator()
        self.toon_validator = ToonValidator()

    def convert(
        self,
        content: str,
        input_format: Optional[str] = None,
        config: Optional[ConversionConfig] = None,
        delimiter: Optional[str] = None,
        auto_detect: bool = False
    ) -> ConversionResult:
        """
        Convert input content to TOON format.

        Args:
            content: Input content string
            input_format: Input format (JSON, XML, CSV, HTML). If None, attempts detection
            config: ConversionConfig with delimiter, sort_keys, ensure_ascii options
            delimiter: (Deprecated) Use config.delimiter instead
            auto_detect: Whether to auto-detect format if not specified

        Returns:
            ConversionResult with TOON output and statistics

        Raises:
            ConversionError: If conversion fails
        """
        # Validate content
        self.input_validator.validate_content(content)

        # Handle legacy delimiter parameter for backward compatibility
        if delimiter and config is None:
            delimiter_map = {"comma": Delimiter.COMMA, "tab": Delimiter.TAB, "pipe": Delimiter.PIPE}
            delimiter_obj = delimiter_map.get(delimiter.lower(), Delimiter.COMMA)
            config = ConversionConfig(delimiter=delimiter_obj)
        elif config is None:
            config = ConversionConfig()

        # Determine format
        if not input_format:
            if auto_detect:
                input_format = self.detector.detect(content)
                if not input_format:
                    raise ConversionError(
                        message="Could not auto-detect input format. Please specify format explicitly.",
                        error_type="FORMAT_DETECTION_FAILED"
                    )
            else:
                raise ConversionError(
                    message="Input format must be specified or auto_detect=True",
                    error_type="MISSING_FORMAT"
                )

        # Validate format
        normalized_format = self.input_validator.validate_format(input_format)

        # Validate config
        config_errors = self.input_validator.validate_config(config)
        warnings = []
        for error in config_errors:
            warnings.append(error.format_message())

        # Get appropriate converter
        converter = self._converters.get(normalized_format)
        if not converter:
            raise ConversionError(
                message=f"No converter available for format: {normalized_format}",
                error_type="NO_CONVERTER"
            )

        # Perform conversion
        result = converter.convert(content, config)
        result.warnings.extend(warnings)

        # Validate TOON output
        toon_error = self.toon_validator.validate_toon_output(result.toon_output)
        if toon_error:
            warnings.append(toon_error.format_message())

        # Validate token reduction
        token_error = self.toon_validator.validate_token_reduction(
            result.original_tokens,
            result.toon_tokens
        )
        if token_error:
            warnings.append(token_error.format_message())

        return result

    def estimate_memory(self, content: str) -> MemoryEstimate:
        """
        Estimate memory usage for content processing.

        Args:
            content: Input content string

        Returns:
            MemoryEstimate with usage information
        """
        return MemoryEstimate.calculate(len(content), None)

    def detect_format(self, content: str) -> Optional[str]:
        """
        Detect input format from content.

        Args:
            content: Input content string

        Returns:
            Detected format string or None
        """
        return self.detector.detect(content)
