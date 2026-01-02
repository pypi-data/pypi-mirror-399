# LLM JSON Repair

[![CI](https://github.com/gcrabtree/llm-json-repair/actions/workflows/ci.yml/badge.svg)](https://github.com/gcrabtree/llm-json-repair/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Robust JSON parsing for LLM outputs with automatic repair and field extraction.

LLMs (like Claude, GPT, etc.) often produce malformed JSON due to:

- **Trailing commas** in arrays and objects
- **Unquoted property names**
- **Truncated output** from context length limits
- **Markdown wrapping** (` ```json ` blocks)
- **JavaScript literals** (undefined, NaN)

This library handles all of these issues automatically.

## Installation

```bash
pip install llm-json-repair
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

```python
from llm_json_repair import parse_json

# Handles trailing commas
result = parse_json('{"items": [1, 2, 3,]}')
print(result.data)  # {'items': [1, 2, 3]}

# Extracts from markdown code blocks
text = '```json\n{"status": "ok"}\n```'
result = parse_json(text)
print(result.data)  # {'status': 'ok'}

# Reports what was fixed
print(result.was_repaired)      # True
print(result.repair_actions)    # ['removed_trailing_commas']
```

## Features

### Automatic Repair

The `parse_json()` function automatically fixes common issues:

```python
from llm_json_repair import parse_json

# Trailing commas
parse_json('{"a": 1,}').data  # {'a': 1}

# Unquoted keys
parse_json('{foo: "bar"}').data  # {'foo': 'bar'}

# Missing closing brackets
parse_json('{"items": [1, 2').data  # {'items': [1, 2]}

# JavaScript undefined/NaN
parse_json('{"x": undefined}').data  # {'x': None}
```

### Field Extraction for Truncated Responses

When JSON is too broken to parse, extract specific fields:

```python
from llm_json_repair import FieldExtractor, extract_field

# LLM response was truncated mid-JSON
malformed = '''{"facts": ["fact1", "fact2"],
                "confidence": 0.8,
                "reasoning": "Based on the ana'''

# Extract what we can
extractor = FieldExtractor()
extractor.add_string_array("facts")
extractor.add_number("confidence")

result = extractor.extract(malformed)
print(result["facts"])       # ['fact1', 'fact2']
print(result["confidence"])  # 0.8

# Or use convenience function
facts = extract_field(malformed, "facts", "string_array")
```

### Strict Mode

Raise an exception instead of returning None for unparseable input:

```python
from llm_json_repair import parse_json, ParseError

try:
    result = parse_json("not json", strict=True)
except ParseError as e:
    print(f"Failed: {e}")
    print(f"Tried: {e.attempts}")
```

## API Reference

### `parse_json(text, *, strict=False, extract_from_text=True)`

Main entry point for parsing JSON from LLM output.

**Parameters:**

- `text`: The text containing JSON to parse
- `strict`: If True, raise `ParseError` on failure instead of returning None
- `extract_from_text`: If True, try to extract JSON from markdown/prose

**Returns:** `ParseResult` with:

- `data`: The parsed JSON data (or None if parsing failed)
- `was_repaired`: Whether repairs were needed
- `repair_actions`: List of repairs applied
- `original_text`: The original input
- `repaired_text`: The text after repairs

### `repair_json(text)`

Low-level function to apply repairs without parsing.

**Returns:** Tuple of (repaired\_text, list\_of\_repairs)

### `extract_json_from_text(text)`

Extract JSON from text that may contain markdown or prose.

**Returns:** The extracted JSON string, or None

### `FieldExtractor`

Builder for extracting specific fields from malformed JSON.

```python
extractor = FieldExtractor()
extractor.add_string("name")
extractor.add_number("count")
extractor.add_boolean("active")
extractor.add_string_array("tags")
extractor.add_object_array("items")
extractor.add_object("metadata")

result = extractor.extract(text)
```

### Convenience Functions

```python
extract_field(text, field_name, field_type="auto")
extract_array(text, field_name)
extract_object(text, field_name)
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=llm_json_repair
```

## License

MIT
