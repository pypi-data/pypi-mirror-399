# Claude Code Instructions for LLM JSON Repair

## What This Library Does

This library provides robust JSON parsing for LLM (Large Language Model) outputs. When Claude, GPT, or other LLMs generate JSON, they often produce malformed output due to:

- Trailing commas (`[1, 2, 3,]`)
- Unquoted property names (`{foo: "bar"}`)
- Truncated responses (context limit hit mid-JSON)
- Markdown code block wrapping
- JavaScript-isms (`undefined`, `NaN`)

This library fixes all of these automatically.

## When to Use This Library

**Use this when:**
1. Parsing JSON from any LLM API response
2. Handling user-pasted LLM output
3. Processing JSON that may have been copy-pasted from chat interfaces
4. Building resilient pipelines that process LLM-generated structured data

**Import pattern:**
```python
from llm_json_repair import parse_json, extract_field, FieldExtractor
```

## Common Usage Patterns

### Pattern 1: Basic LLM Response Parsing

```python
from llm_json_repair import parse_json

def process_llm_response(response_text: str) -> dict:
    """Parse JSON from an LLM response, handling common issues."""
    result = parse_json(response_text)

    if result.data is None:
        raise ValueError(f"Could not parse LLM response as JSON")

    if result.was_repaired:
        # Log that we had to fix the output
        print(f"Fixed JSON issues: {result.repair_actions}")

    return result.data
```

### Pattern 2: Extracting Specific Fields from Broken JSON

When the LLM response is too broken to parse completely, but you need specific fields:

```python
from llm_json_repair import parse_json, FieldExtractor

def extract_analysis(llm_output: str) -> dict:
    """Extract analysis fields, even from truncated responses."""

    # Try full parsing first
    result = parse_json(llm_output)
    if result.data is not None:
        return result.data

    # Fall back to field extraction
    extractor = FieldExtractor()
    extractor.add_string_array("facts")
    extractor.add_string_array("concepts")
    extractor.add_number("confidence")
    extractor.add_string("summary")

    return extractor.extract(llm_output)
```

### Pattern 3: Strict Mode for Critical Operations

```python
from llm_json_repair import parse_json, ParseError

def parse_critical_response(response: str) -> dict:
    """Parse JSON, failing loudly if it can't be repaired."""
    try:
        result = parse_json(response, strict=True)
        return result.data
    except ParseError as e:
        # Log the failure details
        print(f"JSON parse failed after attempts: {e.attempts}")
        print(f"Original text: {e.original_text[:200]}...")
        raise
```

### Pattern 4: Processing Markdown-Wrapped JSON

LLMs often wrap JSON in markdown code blocks. This is handled automatically:

```python
from llm_json_repair import parse_json

# All of these work:
parse_json('```json\n{"key": "value"}\n```')
parse_json('Here is the result: {"key": "value"}')
parse_json('{"key": "value"}')  # Plain JSON
```

## Architecture Notes

The library has two layers:

1. **Parser Layer** (`parser.py`):
   - `parse_json()` - Main entry point, tries repair strategies
   - `repair_json()` - Low-level repair without parsing
   - `extract_json_from_text()` - Finds JSON in mixed content

2. **Extractor Layer** (`extractors.py`):
   - `FieldExtractor` - Regex-based field extraction from broken JSON
   - Works even when JSON is completely unparseable
   - Use when you know what fields you need

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test class
pytest tests/test_parser.py::TestParseJson
```

## Dependencies

None! This library uses only Python's standard library (`json`, `re`, `dataclasses`).

## Common Modifications

### Adding a New Repair Strategy

Edit `parser.py` and add to the `repair_json()` function:

```python
def repair_json(text: str) -> tuple[str, List[str]]:
    repairs = []
    result = text.strip()

    # Add your new repair here:
    if some_condition:
        result = result.replace(old, new)
        repairs.append("your_repair_name")

    # ... rest of function
```

### Adding a New Field Type to Extractor

Edit `extractors.py` and add a method to `FieldExtractor`:

```python
def add_your_type(self, field_name: str) -> "FieldExtractor":
    """Add your custom type field."""
    self._fields.append((field_name, "your_type", self._extract_your_type))
    return self

def _extract_your_type(self, text: str, field_name: str) -> Optional[YourType]:
    """Extract your custom type."""
    pattern = rf'"{field_name}"\s*:\s*(your_pattern)'
    match = re.search(pattern, text)
    if not match:
        return None
    return parse_your_type(match.group(1))
```

## Integration Examples

### With Anthropic SDK

```python
import anthropic
from llm_json_repair import parse_json

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Return a JSON object with..."}],
)

# Handle any JSON formatting issues from the response
result = parse_json(response.content[0].text)
data = result.data
```

### With OpenAI SDK

```python
from openai import OpenAI
from llm_json_repair import parse_json

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Return JSON..."}],
)

result = parse_json(response.choices[0].message.content)
data = result.data
```

### With LangChain

```python
from langchain.llms import Anthropic
from llm_json_repair import parse_json

llm = Anthropic()
response = llm.invoke("Return JSON with...")
result = parse_json(response)
```
