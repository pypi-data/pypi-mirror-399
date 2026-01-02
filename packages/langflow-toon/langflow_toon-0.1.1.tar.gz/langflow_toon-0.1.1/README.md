# TOON Converter for Langflow

A custom Langflow component that converts structured data (JSON, XML, CSV, HTML) into [TOON (Token-Oriented Object Notation)](https://github.com/toon-format/toon) format to optimize token usage for LLM prompts.

## Features

- **Multi-format Support**: Convert JSON, XML, CSV, and HTML to TOON format
- **Token Optimization**: Achieve 30%+ token reduction compared to formatted JSON
- **Configurable Delimiters**: Choose between comma, tab, or pipe separators
- **Token Statistics**: View before/after token counts and savings percentage
- **Memory Warnings**: Get alerts for large datasets before processing
- **Detailed Error Messages**: Get location-specific error messages with corrected examples

## Installation

### From Source

```bash
git clone https://github.com/faisolp/langflow-toon-component.git
cd toon
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `tiktoken>=0.5.0` - Token counting for optimization analysis
- `xmltodict>=0.13.0` - XML parsing and conversion
- `pytest>=7.0.0` - Testing framework (development only)
- `pytest-cov>=4.0.0` - Test coverage reporting (development only)

## Usage

### Python API Usage

```python
from langflow_toon import ToonConverter
from langflow_toon.models.data import ConversionConfig, Delimiter

# Initialize converter
converter = ToonConverter()

# Convert JSON to TOON
json_data = '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}'
result = converter.convert(json_data, input_format='JSON')

print(result.toon_output)
# Output:
# users[2]{id,name}:
#   1,Alice
#   2,Bob

print(f"Token reduction: {result.token_reduction} ({result.token_reduction/result.original_tokens*100:.1f}%)")
```

### Basic Usage in Langflow

1. Add the "TOON Converter" component to your Langflow flow
2. Connect your data source to the `input_text` port
3. Configure the `input_format` (or enable `auto_detect` for automatic detection)
4. Choose your preferred `csv_delimiter` (comma, tab, or pipe)
5. Toggle `sort_keys` to alphabetically sort object keys
6. Toggle `ensure_ascii` to encode non-ASCII characters
7. Connect the `toon_output` to your LLM prompt
8. View `original_tokens`, `toon_tokens`, and `token_reduction` statistics

### Example: JSON to TOON

**Input (JSON)**:
```json
{
  "users": [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"}
  ]
}
```

**Output (TOON)**:
```toon
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
```

**Token Savings**: 85 → 42 tokens (50.6% reduction)

### Example: CSV with Tab Delimiter

**Input (CSV)**:
```csv
name,age,city
Alice,30,NYC
Bob,25,LA
```

**Output (TOON with tab delimiter)**:
```toon
data[2 ]{name	age	city}:
  Alice	30	NYC
  Bob	25	LA
```

### Example: Complete Langflow Workflow

```
[HTTP Request] → [TOON Converter] → [LLM Prompt]
                    ↓
              [Token Stats Display]
```

**Flow Configuration**:
1. **HTTP Request**: Fetch JSON data from an API
2. **TOON Converter**:
   - `input_text`: Connect from HTTP Request output
   - `input_format`: JSON
   - `csv_delimiter`: comma (default)
   - `auto_detect`: false (format known)
   - `sort_keys`: false (preserve order)
   - `ensure_ascii`: false (keep Unicode)
3. **LLM Prompt**: Use `{{toon_output}}` variable in prompt template
4. **Token Stats Display**: Show `{{original_tokens}}`, `{{toon_tokens}}`, `{{token_reduction}}`

### Example: Multi-Format Processing Pipeline

```
                    ┌─────────────┐
                    │ Format      │
                    │ Detector    │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
     │   JSON  │     │   XML   │     │   CSV   │
     │ Source  │     │ Source  │     │ Source  │
     └────┬────┘     └────┬────┘     └────┬────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                   ┌──────▼──────┐
                   │  TOON       │
                   │  Converter  │
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │  LLM        │
                   │  Processing │
                   └─────────────┘
```

## Component API

### Inputs

| Port | Type | Description |
|------|------|-------------|
| `input_data` | string | Raw data to convert (JSON, XML, CSV, or HTML) |
| `input_format` | enum | Data format: `AUTO`, `JSON`, `XML`, `CSV`, `HTML` |
| `delimiter` | enum | TOON field delimiter: `COMMA`, `TAB`, `PIPE` |
| `sort_keys` | boolean | Sort object keys alphabetically (default: false) |

### Outputs

| Port | Type | Description |
|------|------|-------------|
| `toon_output` | string | TOON formatted data |
| `token_stats` | object | Token usage statistics |
| `error` | string | Error message (if conversion fails) |

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=langflow_toon tests/
```

### Project Structure

```
langflow_toon/
├── __init__.py
├── component.py         # Main Langflow custom component
├── converters/          # Format-specific converters
├── validators/          # Input and TOON validation
├── utils/               # Token counting, memory estimation, error formatting
└── config/              # Constants and configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Links

- [TOON Format Specification](https://github.com/toon-format/toon)
- [Langflow Documentation](https://langflow.org)

