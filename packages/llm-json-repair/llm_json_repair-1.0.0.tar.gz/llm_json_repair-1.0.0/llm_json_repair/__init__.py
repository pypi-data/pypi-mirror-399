"""
LLM JSON Repair - Robust JSON parsing for LLM outputs

This library provides utilities for parsing JSON from LLM outputs,
handling common formatting issues like trailing commas, unquoted keys,
and partial/truncated responses.
"""

from .extractors import (
    FieldExtractor,
    extract_array,
    extract_field,
    extract_object,
)
from .parser import (
    ParseError,
    ParseResult,
    extract_json_from_text,
    parse_json,
    repair_json,
)

__version__ = "1.0.0"
__all__ = [
    # Core parsing
    "parse_json",
    "repair_json",
    "extract_json_from_text",
    "ParseResult",
    "ParseError",
    # Field extraction
    "extract_field",
    "extract_array",
    "extract_object",
    "FieldExtractor",
]
