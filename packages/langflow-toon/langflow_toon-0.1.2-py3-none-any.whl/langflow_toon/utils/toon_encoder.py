"""TOON encoder implementation for Python."""

from typing import Any, List, Union, Optional
from io import StringIO


class ToonEncoder:
    """Encodes Python data structures to TOON format."""

    # Delimiter symbols for TOON format (per spec)
    DELIMITER_SYMBOLS = {
        ",": "",      # Comma is default, no symbol needed
        "\t": " ",    # Tab uses space character in header
        "|": "|"      # Pipe uses pipe character in header
    }

    def __init__(self, indent: int = 2, delimiter: str = ","):
        """Initialize encoder.

        Args:
            indent: Number of spaces for indentation (default: 2)
            delimiter: Delimiter for tabular arrays (comma, tab, or pipe)
        """
        self.indent = indent
        self.delimiter = delimiter

    def encode(self, data: Any) -> str:
        """
        Encode Python data to TOON format string.

        Args:
            data: Python data structure (dict, list, or primitive)

        Returns:
            TOON format string
        """
        output = StringIO()
        self._encode_value(data, output, 0)
        return output.getvalue().strip()

    def _encode_value(self, value: Any, output: StringIO, depth: int) -> None:
        """Encode a value to TOON format."""
        if isinstance(value, dict):
            self._encode_dict(value, output, depth)
        elif isinstance(value, list):
            self._encode_list(value, output, depth)
        elif isinstance(value, str):
            output.write(self._encode_string(value))
        elif isinstance(value, bool):
            output.write('true' if value else 'false')
        elif value is None:
            output.write('null')
        else:
            output.write(str(value))

    def _encode_dict(self, data: dict, output: StringIO, depth: int) -> None:
        """Encode dictionary to TOON format."""
        indent_str = ' ' * (depth * self.indent)

        # Separate attributes (keys starting with @) and regular keys
        attr_keys = {k: v for k, v in data.items() if k.startswith('@')}
        regular_keys = {k: v for k, v in data.items() if not k.startswith('@')}

        # Write regular keys first
        for key, value in regular_keys.items():
            # Write key with colon
            output.write(f"\n{indent_str}{key}:")

            # Handle value
            if isinstance(value, dict):
                # Nested dict - continue with indentation
                self._encode_dict(value, output, depth + 1)
            elif isinstance(value, list):
                # Array - check if uniform objects for tabular format
                if self._is_uniform_object_array(value):
                    self._encode_tabular_array(key, value, output, depth)
                else:
                    # Simple array - inline (no spaces after delimiter per TOON spec)
                    items = ','.join([self._encode_simple_item(item) for item in value])
                    output.write(f"[{len(value)}]: {items}")
            else:
                # Primitive value - inline
                output.write(' ')
                self._encode_value(value, output, 0)

        # Write attributes (keys with @) in a cleaner format
        if attr_keys and regular_keys:
            # If we have both regular keys and attributes, group attributes
            output.write(f"\n{indent_str}attrs:")
            attr_indent = ' ' * ((depth + 1) * self.indent)
            for key, value in attr_keys.items():
                # Remove @ prefix for cleaner output
                clean_key = key[1:]  # Remove @
                output.write(f"\n{attr_indent}{clean_key}: {value}")

    def _encode_list(self, data: list, output: StringIO, depth: int) -> None:
        """Encode list to TOON format."""
        if not data:
            output.write('[]')
            return

        # Check if uniform object array for tabular format
        if self._is_uniform_object_array(data):
            # Use tabular format for root-level uniform arrays
            self._encode_tabular_array("items", data, output, depth)
        else:
            # Simple array - inline TOON style (no spaces after delimiter per TOON spec)
            items = ','.join([self._encode_simple_item(item) for item in data])
            output.write(f"[{len(data)}]: {items}")

    def _encode_tabular_array(self, key: str, data: list, output: StringIO, depth: int) -> None:
        """Encode uniform object array in tabular TOON format."""
        if not data:
            return

        # Get field names from first object
        fields = list(data[0].keys())

        # Get delimiter symbol for header (per TOON spec)
        delim_symbol = self.DELIMITER_SYMBOLS.get(self.delimiter, "")

        # Write header: key[N<delim>]{field1<delim>field2,...}:
        # For tab/pipe, delimiter appears in brackets: [2|]{field|name}:
        # For comma (default), no symbol: [2]{field,name}:
        indent_str = ' ' * (depth * self.indent)
        field_delim = self.delimiter if self.delimiter != "," else ""
        output.write(f"[{len(data)}{delim_symbol}]{{{field_delim.join(fields)}}}:")

        # Write each row using the configured delimiter
        row_indent = ' ' * ((depth + 1) * self.indent)
        for item in data:
            values = []
            for field in fields:
                val = item.get(field)
                if val is None:
                    values.append('')
                elif isinstance(val, str):
                    # Quote strings with special characters (including delimiter)
                    if self.delimiter in val or '\n' in val or '"' in val:
                        values.append(f'"{val.replace('"', '\\"')}"')
                    else:
                        values.append(val)
                elif isinstance(val, bool):
                    values.append('true' if val else 'false')
                else:
                    values.append(str(val))

            output.write(f"\n{row_indent}{self.delimiter.join(values)}")

    def _encode_string(self, value: str) -> str:
        """Encode string value."""
        # Don't quote simple strings without special characters
        if not value or any(c in value for c in [' ', ',', '\n', '\t', ':', '{', '}', '[', ']']):
            return f'"{value.replace('"', '\\"')}"'
        return value

    def _encode_simple_item(self, item: Any) -> str:
        """Encode simple item for inline arrays."""
        if isinstance(item, str):
            return f'"{item}"'
        elif isinstance(item, bool):
            return 'true' if item else 'false'
        elif item is None:
            return 'null'
        else:
            return str(item)

    def _is_uniform_object_array(self, data: list) -> bool:
        """Check if list is uniform array of objects with same fields."""
        if not data or not isinstance(data[0], dict):
            return False

        first_keys = set(data[0].keys())

        for item in data[1:]:
            if not isinstance(item, dict):
                return False

            # Check same fields
            if set(item.keys()) != first_keys:
                return False

            # Check primitive values only
            for val in item.values():
                if isinstance(val, (dict, list)):
                    return False

        return len(data) > 1 or len(first_keys) > 0


def encode_toon(data: Any, indent: int = 2, delimiter: str = ",") -> str:
    """
    Encode Python data to TOON format.

    Args:
        data: Python data structure
        indent: Indentation spaces (default: 2)
        delimiter: Delimiter for tabular arrays - comma, tab, or pipe (default: comma)

    Returns:
        TOON format string
    """
    encoder = ToonEncoder(indent, delimiter)
    return encoder.encode(data)
