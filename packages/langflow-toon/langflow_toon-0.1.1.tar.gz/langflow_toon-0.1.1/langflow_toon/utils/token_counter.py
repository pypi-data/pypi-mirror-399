"""Token counting utilities using tiktoken."""

from functools import lru_cache

try:
    import tiktoken

    @lru_cache(maxsize=1000)
    def count_tokens(text: str, encoding: str = "o200k_base") -> int:
        """
        Count tokens in a text string using the specified encoding.

        Args:
            text: The text to count tokens for
            encoding: The token encoding to use (default: o200k_base for GPT-5)

        Returns:
            Number of tokens in the text
        """
        if not text:
            return 0
        try:
            encoder = tiktoken.get_encoding(encoding)
            return len(encoder.encode(text))
        except Exception:
            # Fallback: approximate tokens as characters
            return len(text)
except ImportError:
    # tiktoken not available, use simple approximation
    def count_tokens(text: str, encoding: str = "o200k_base") -> int:
        """Fallback token counter when tiktoken is not available."""
        return len(text) if text else 0
