from langflow.custom.custom_component.component import Component
from langflow.io import MessageTextInput, Output, DropdownInput, BoolInput
from langflow.schema.data import Data
from langflow.schema.message import Message


from langflow_toon.detectors.format_detector import FormatDetector
from langflow_toon.converters.json_converter import JsonConverter
from langflow_toon.converters.xml_converter import XmlConverter
from langflow_toon.converters.csv_converter import CsvConverter
from langflow_toon.converters.html_converter import HtmlConverter
from langflow_toon.models.data import ConversionConfig, Delimiter
from langflow_toon.models.errors import ConversionError
MODULES_AVAILABLE = True


class ToonConverterComponent(Component):
    display_name = "TOON Converter"
    description = "Convert JSON, XML, CSV, or HTML to TOON format for token optimization"
    documentation = "https://github.com/toon-format/toon"
    icon = "code"
    name = "ToonConverter"

    inputs = [
        MessageTextInput(
            name="input_text",
            display_name="Input Content",
            info="The content to convert to TOON format (JSON, XML, CSV, or HTML)",
            value='{ "name": "Faisolp", "age": 30, "isStudent": false, "courses": ["Math", "Science"] }',
            tool_mode=True,
        ),DropdownInput(
            name="input_format",
            display_name="Input Format",
            info="Format of input content. Leave as AUTO for automatic detection.",
            options=["AUTO", "JSON", "XML", "CSV", "HTML"],
            value="AUTO",
        ),DropdownInput(
            name="csv_delimiter",
            display_name="CSV Delimiter",
            info="Delimiter for CSV files (only used when format is CSV)",
            options=["comma", "tab", "pipe"],
            value="comma",
        ),BoolInput(
            name="auto_detect",
            display_name="Auto Detect Format",
            info="Automatically detect input format",
            value=True,
        ),BoolInput(
            name="sort_keys",
            display_name="Sort Keys",
            info="Sort object keys alphabetically in TOON output",
            value=False,
        ),BoolInput(
            name="ensure_ascii",
            display_name="Ensure ASCII",
            info="Encode non-ASCII characters as escape sequences",
            value=False,
        ),DropdownInput(
            name="output_format",
            display_name="Output Format",
            info="Choose output format: Data (for chaining) or Message (for display)",
            options=["Data", "Message"],
            value="Data",
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data_output", method="convert_to_toon"),
        Output(display_name="Message", name="text_output", method="get_text_output"),
    ]

   
        
    def convert_to_toon(self) -> Data:
        """Convert input content to TOON format."""
        input_text = self.input_text
        input_format = self.input_format
        csv_delimiter = self.csv_delimiter
        auto_detect = self.auto_detect
        sort_keys = self.sort_keys
        ensure_ascii = self.ensure_ascii
        
        if not input_text or not input_text.strip():
            result = {
                "toon_output": "",
                "original_tokens": 0,
                "toon_tokens": 0,
                "token_reduction": 0,
                "warnings": ["No input provided"]
            }
            return Data(value=result)

        try:
            # Initialize detector
            detector = FormatDetector()
            
            # Detect format if auto_detect is enabled or format is AUTO
            if auto_detect or input_format == "AUTO":
                detected_format = detector.detect(input_text)
            else:
                detected_format = input_format
            
            # Create configuration
            if MODULES_AVAILABLE:
                delimiter_map = {
                    "comma": Delimiter.COMMA,
                    "tab": Delimiter.TAB,
                    "pipe": Delimiter.PIPE
                }
                config = ConversionConfig(
                    delimiter=delimiter_map.get(csv_delimiter, Delimiter.COMMA),
                    sort_keys=sort_keys,
                    ensure_ascii=ensure_ascii
                )
            else:
                config = ConversionConfig()
            
            # Select appropriate converter
            converter_result = None
            text_result=""
            
            if detected_format == "JSON":
                converter = JsonConverter()
                converter_result = converter.convert(input_text, config)
            elif detected_format == "XML" and MODULES_AVAILABLE:
                converter = XmlConverter()
                converter_result = converter.convert(input_text, config)
            elif detected_format == "CSV" and MODULES_AVAILABLE:
                converter = CsvConverter()
                converter_result = converter.convert(input_text, config)
            elif detected_format == "HTML" and MODULES_AVAILABLE:
                converter = HtmlConverter()
                converter_result = converter.convert(input_text, config)
            else:
                # Fallback to JSON converter for unsupported formats
                converter = JsonConverter()
                try:
                    converter_result = converter.convert(input_text, config)
                    
                except:
                    text_result=input_text
                    converter_result = {
                        "toon_output": input_text,
                        "original_tokens": len(input_text.split()),
                        "toon_tokens": len(input_text.split()),
                        "token_reduction": 0,
                        "warnings": [f"Unsupported format: {detected_format}. Returning original text."]
                    }
            
            # Convert ConversionResult object to dictionary if needed
            if hasattr(converter_result, 'toon_output'):
                # It's a ConversionResult object
                text_result=converter_result.toon_output
                result = {
                    "toon_output": converter_result.toon_output,
                    "original_tokens": converter_result.original_tokens,
                    "toon_tokens": converter_result.toon_tokens,
                    "token_reduction": converter_result.token_reduction,
                    "warnings": list(converter_result.warnings) if converter_result.warnings else []
                }
            else:
                # It's already a dictionary
                result = converter_result
            
            # Ensure result has all required fields
            if not isinstance(result, dict):
                result = {
                    "toon_output": str(result),
                    "original_tokens": len(input_text.split()),
                    "toon_tokens": len(str(result).split()),
                    "token_reduction": len(input_text.split()) - len(str(result).split()),
                    "warnings": []
                }
            
            # Add format detection info to warnings if it was detected
            if auto_detect or input_format == "AUTO":
                if "warnings" not in result:
                    result["warnings"] = []
                result["warnings"].append(f"Detected format: {detected_format}")

        except Exception as e:
            # Return error information
            result = {
                "toon_output": "",
                "original_tokens": 0,
                "toon_tokens": 0,
                "token_reduction": 0,
                "warnings": [f"Conversion error: {str(e)}"]
            }
        
        # Store result for both outputs  
        self._conversion_result = result
        self._text_result = text_result

        data = Data(value=result)
        self.status = data
        return data
    
    
    def get_text_output(self) -> Message:
        """Get text output as Message for display."""
        # If conversion hasn't been run, run it first
        if not hasattr(self, '_text_result'):
            self.convert_to_toon()
        
        return Message(
            text=getattr(self, '_text_result', ''),
            data=getattr(self, '_conversion_result', {})
        )
    