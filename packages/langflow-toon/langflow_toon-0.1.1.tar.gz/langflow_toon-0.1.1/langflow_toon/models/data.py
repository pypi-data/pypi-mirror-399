"""Data model definitions for TOON Converter."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any


class InputFormat(Enum):
    """Supported input formats."""
    JSON = "JSON"
    XML = "XML"
    CSV = "CSV"
    HTML = "HTML"
    AUTO = "AUTO"


class Delimiter(Enum):
    """CSV delimiter options."""
    COMMA = "comma"
    TAB = "tab"
    PIPE = "pipe"


@dataclass
class InputData:
    """Represents raw input data provided by the user."""
    content: str
    format: InputFormat
    source: Optional[str] = None

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("Input content cannot be empty")


@dataclass
class ConversionConfig:
    """Configuration options for TOON conversion process."""
    delimiter: Optional[Delimiter] = None
    sort_keys: bool = False
    ensure_ascii: bool = False


@dataclass
class TokenStatistics:
    """Statistics about token usage before and after conversion."""
    input_tokens: int
    output_tokens: int
    savings_count: int
    savings_percent: float
    encoding: str = "o200k_base"

    @classmethod
    def calculate(cls, text: str, encoding: str = "o200k_base") -> int:
        """
        Calculate token count for text using specified encoding.

        Args:
            text: Text to count tokens for
            encoding: Token encoding to use (default: o200k_base for GPT-5)

        Returns:
            Number of tokens in the text
        """
        try:
            import tiktoken
            encoder = tiktoken.get_encoding(encoding)
            return len(encoder.encode(text))
        except Exception:
            # Fallback if tiktoken unavailable
            return len(text) if text else 0


@dataclass
class ConversionResult:
    """The output of the conversion process."""
    toon_output: str
    original_tokens: int
    toon_tokens: int
    token_reduction: int
    warnings: List[str] = field(default_factory=list)
