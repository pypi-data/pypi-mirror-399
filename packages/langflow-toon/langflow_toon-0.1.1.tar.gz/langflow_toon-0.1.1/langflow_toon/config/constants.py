"""Constants for TOON Converter component."""

from enum import Enum
from typing import Dict

# Maximum limits
MAX_NESTING_DEPTH = 20
MAX_ROWS = 100_000
MEMORY_WARNING_THRESHOLD_MB = 100
MEMORY_CONFIRMATION_THRESHOLD_MB = 500

# Supported formats
SUPPORTED_FORMATS = {
    "JSON": ["application/json", ".json"],
    "XML": ["application/xml", "text/xml", ".xml"],
    "CSV": ["text/csv", ".csv"],
    "HTML": ["text/html", ".html", ".htm"]
}

# Delimiter mapping
class Delimiter(Enum):
    COMMA = ","
    TAB = "\t"
    PIPE = "|"

DELIMITER_MAP = {
    Delimiter.COMMA: ",",
    Delimiter.TAB: "\t",
    Delimiter.PIPE: "|"
}
