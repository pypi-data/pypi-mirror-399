"""Format detection for automatic input format detection."""

import json
from typing import Optional

from ..models.data import InputFormat


class FormatDetector:
    """Detects input format from content string."""

    @staticmethod
    def detect(content: str) -> Optional[str]:
        """
        Detect input format from content.

        Args:
            content: Input content string

        Returns:
            Detected format string (JSON, XML, CSV, HTML) or None if uncertain
        """
        if not content or not content.strip():
            return None

        content = content.strip()

        # Check JSON first (most specific)
        if FormatDetector._is_json(content):
            return InputFormat.JSON.value

        # Check XML
        if FormatDetector._is_xml(content):
            return InputFormat.XML.value

        # Check HTML
        if FormatDetector._is_html(content):
            return InputFormat.HTML.value

        # Check CSV (least specific - check last)
        if FormatDetector._is_csv(content):
            return InputFormat.CSV.value

        return None

    @staticmethod
    def _is_json(content: str) -> bool:
        """Check if content is valid JSON."""
        content = content.strip()
        if not (content.startswith('{') or content.startswith('[')):
            return False

        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    @staticmethod
    def _is_xml(content: str) -> bool:
        """Check if content appears to be XML."""
        content = content.strip()
        # XML should start with angle bracket
        if not content.startswith('<'):
            return False

        # Common XML starting patterns
        xml_patterns = [
            '<?xml',          # XML declaration
            '<![CDATA[',      # CDATA section
        ]

        for pattern in xml_patterns:
            if content.startswith(pattern):
                return True

        # Check for proper XML tag opening (not HTML specific tags)
        # XML must have a closing tag or be self-closing
        first_bracket = content.find('>')
        if first_bracket > 0:
            opening = content[:first_bracket + 1]
            # Self-closing tag
            if opening.endswith('/>'):
                return True
            # Check for tag name only (alphanumeric after <)
            tag_name = content[1:first_bracket].split()[0]
            if tag_name and tag_name.replace('_', '').replace('-', '').replace(':', '').isalnum():
                # Not HTML-specific
                if tag_name.lower() not in {'html', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'table', 'tr', 'td', 'th'}:
                    return True

        return False

    @staticmethod
    def _is_html(content: str) -> bool:
        """Check if content appears to be HTML."""
        content_lower = content.strip().lower()

        # Check for HTML-specific tags
        html_indicators = [
            '<html', '<head', '<body', '<div', '<span',
            '<!doctype html', '<table', '<br>', '<br/',
        ]

        for indicator in html_indicators:
            if indicator in content_lower:
                return True

        return False

    @staticmethod
    def _is_csv(content: str) -> bool:
        """Check if content appears to be CSV."""
        lines = content.strip().split('\n')

        if len(lines) < 2:
            return False

        # Check first few lines for CSV pattern
        # CSV has consistent delimiter-separated values
        for line in lines[:min(5, len(lines))]:
            line = line.strip()
            if not line:
                continue

            # Check for common delimiters
            has_comma = ',' in line
            has_tab = '\t' in line
            has_pipe = '|' in line

            # At least one delimiter should be present
            if not (has_comma or has_tab or has_pipe):
                return False

            # Check for quote-enclosed fields (common in CSV)
            if '"' in line:
                # Basic check for balanced quotes
                if line.count('"') % 2 != 0:
                    return False

        return True
