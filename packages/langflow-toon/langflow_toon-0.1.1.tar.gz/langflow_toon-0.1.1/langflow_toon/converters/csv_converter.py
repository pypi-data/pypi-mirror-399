"""CSV to TOON converter."""

import csv
import json
from io import StringIO
from typing import Any, List, Optional

from ..converters.base import BaseConverter, ConversionConfig
from ..models.data import ConversionResult, TokenStatistics
from ..models.errors import ConversionError
from ..config.constants import DELIMITER_MAP


class CsvConverter(BaseConverter):
    """Converter for CSV input format."""

    def convert(self, content: str, config: ConversionConfig) -> ConversionResult:
        """
        Convert CSV content to TOON format.

        Args:
            content: CSV string content
            config: Conversion configuration

        Returns:
            ConversionResult with TOON output and statistics

        Raises:
            ConversionError: If CSV parsing fails
        """
        try:
            # Map Delimiter enum (from models/data.py) to actual delimiter character
            # Delimiter enum has values: "comma", "tab", "pipe"
            from ..models.data import Delimiter
            delimiter_char_map = {
                Delimiter.COMMA: ",",
                Delimiter.TAB: "\t",
                Delimiter.PIPE: "|"
            }
            delimiter = delimiter_char_map.get(config.delimiter, ",")

            # Parse CSV
            f = StringIO(content.strip())
            reader = csv.reader(f, delimiter=delimiter)

            headers = next(reader, [])
            if not headers:
                raise ConversionError(
                    message="CSV file is empty or has no headers",
                    error_type="CSV_EMPTY"
                )

            rows = []
            for i, row in enumerate(reader, start=2):
                # Handle inconsistent column counts
                if len(row) < len(headers):
                    row.extend([""] * (len(headers) - len(row)))
                elif len(row) > len(headers):
                    row = row[:len(headers)]
                rows.append(dict(zip(headers, row)))

            parsed_data = rows

            # Validate parsed data
            self._validate_parsed_data(parsed_data)

            # Convert to TOON using custom encoder
            # Wrap CSV data in a dict for proper TOON formatting
            from ..utils.toon_encoder import encode_toon

            csv_dict = {"data": parsed_data}  # Wrap in dict for tabular format
            toon_string = encode_toon(csv_dict, delimiter=delimiter)

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

        except csv.Error as e:
            raise ConversionError(
                message=f"CSV parsing error: {str(e)}",
                error_type="CSV_PARSE_ERROR"
            )
        except Exception as e:
            raise ConversionError(
                message=f"CSV conversion failed: {str(e)}",
                error_type="CSV_CONVERSION_ERROR"
            )

    def _validate_parsed_data(self, data: Any) -> None:
        """Validate parsed CSV data structure."""
        # Depth and size validation inherited from BaseConverter
        super()._validate_parsed_data(data)

        # CSV-specific: validate tabular structure
        if isinstance(data, list) and data:
            if not all(isinstance(row, dict) for row in data):
                raise ConversionError(
                    message="CSV data must be a list of dictionaries",
                    error_type="CSV_INVALID_STRUCTURE"
                )
