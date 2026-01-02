"""HTML to TOON converter."""

from typing import Any, Optional

try:
    from html.parser import HTMLParser
except ImportError:
    HTMLParser = None

from ..converters.base import BaseConverter, ConversionConfig
from ..models.data import ConversionResult, TokenStatistics
from ..models.errors import ConversionError


class HtmlConverter(BaseConverter):
    """Converter for HTML input format."""

    def convert(self, content: str, config: ConversionConfig) -> ConversionResult:
        """
        Convert HTML content to TOON format.

        Args:
            content: HTML string content
            config: Conversion configuration

        Returns:
            ConversionResult with TOON output and statistics

        Raises:
            ConversionError: If HTML parsing fails
        """
        if HTMLParser is None:
            raise ConversionError(
                message="HTML parser not available",
                error_type="MISSING_DEPENDENCY"
            )

        try:
            # Parse HTML to structured format
            parsed_data = self._parse_html(content)

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
            raise ConversionError(
                message=f"HTML conversion failed: {str(e)}",
                error_type="HTML_CONVERSION_ERROR"
            )

    def _parse_html(self, content: str) -> dict:
        """
        Parse HTML content into structured dictionary suitable for TOON format.

        Creates a simplified nested structure with meaningful keys.

        Args:
            content: HTML string

        Returns:
            Dictionary with parsed HTML structure
        """
        class HtmlToToonParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.structure = {}
                self.stack = [self.structure]
                self.tag_count = {}  # Track tag occurrence for naming

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs) if attrs else {}

                # Skip certain container tags for cleaner structure
                if tag in ("html", "head"):
                    return

                # Create meaningful key based on tag
                tag_count = self.tag_count.get(tag, 0) + 1
                self.tag_count[tag] = tag_count

                if tag == "body":
                    key = "content"  # Use "content" instead of "body"
                elif tag_count > 1:
                    key = f"{tag}_{tag_count}"
                else:
                    key = tag

                # Create node
                node = {}
                if attrs_dict:
                    # Only include important attributes
                    important_attrs = {"id", "class", "href", "src"}
                    for attr in important_attrs:
                        if attr in attrs_dict:
                            node[attr] = attrs_dict[attr]

                # Add to current level
                self.stack[-1][key] = node
                self.stack.append(node)

            def handle_endtag(self, tag):
                if tag in ("html", "head"):
                    return
                if len(self.stack) > 1:
                    self.stack.pop()

            def handle_data(self, data):
                text = data.strip()
                if text and self.stack:
                    # Add text directly to current node
                    current = self.stack[-1]
                    # Use "text" key, but if already exists, append
                    if "text" in current:
                        current["text"] += " " + text
                    else:
                        current["text"] = text

        parser = HtmlToToonParser()
        parser.feed(content)

        return parser.structure if parser.structure else {"empty": True}

    def _validate_parsed_data(self, data: Any) -> None:
        """Validate parsed HTML data structure."""
        # Depth and size validation inherited from BaseConverter
        super()._validate_parsed_data(data)

        # HTML-specific validation - check for html key
        if not isinstance(data, dict):
            raise ConversionError(
                message="HTML data must be a dictionary",
                error_type="HTML_INVALID_STRUCTURE"
            )
