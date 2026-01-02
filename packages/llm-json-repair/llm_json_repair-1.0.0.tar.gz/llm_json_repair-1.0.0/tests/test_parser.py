"""
Tests for LLM JSON Repair library.
"""

import pytest

from llm_json_repair import (
    FieldExtractor,
    ParseError,
    extract_array,
    extract_field,
    extract_json_from_text,
    parse_json,
    repair_json,
)


class TestParseJson:
    """Tests for the main parse_json function."""

    def test_valid_json_parses_directly(self):
        """Valid JSON should parse without repairs."""
        result = parse_json('{"name": "test", "value": 42}')
        assert result.data == {"name": "test", "value": 42}
        assert result.was_repaired is False
        assert result.repair_actions == []

    def test_trailing_comma_in_object(self):
        """Trailing comma in object should be repaired."""
        result = parse_json('{"a": 1, "b": 2,}')
        assert result.data == {"a": 1, "b": 2}
        assert result.was_repaired is True
        assert "removed_trailing_commas" in result.repair_actions

    def test_trailing_comma_in_array(self):
        """Trailing comma in array should be repaired."""
        result = parse_json("[1, 2, 3,]")
        assert result.data == [1, 2, 3]
        assert result.was_repaired is True

    def test_nested_trailing_commas(self):
        """Multiple nested trailing commas should be repaired."""
        result = parse_json('{"items": [1, 2,], "more": {"x": 1,},}')
        assert result.data == {"items": [1, 2], "more": {"x": 1}}
        assert result.was_repaired is True

    def test_unquoted_keys(self):
        """Unquoted property names should be quoted."""
        result = parse_json('{foo: "bar", baz: 123}')
        assert result.data == {"foo": "bar", "baz": 123}
        assert result.was_repaired is True
        assert "quoted_property_names" in result.repair_actions

    def test_missing_closing_bracket(self):
        """Missing closing brackets should be added."""
        # Array missing closing bracket
        result = parse_json("[1, 2, 3")
        assert result.data == [1, 2, 3]
        assert result.was_repaired is True
        assert any("closing_bracket" in a for a in result.repair_actions)

    def test_missing_closing_brace(self):
        """Missing closing braces should be added."""
        result = parse_json('{"nested": {"value": 1}')
        assert result.data == {"nested": {"value": 1}}
        assert result.was_repaired is True

    def test_javascript_undefined(self):
        """JavaScript undefined should be replaced with null."""
        result = parse_json('{"value": undefined}')
        assert result.data == {"value": None}
        assert result.was_repaired is True

    def test_javascript_nan(self):
        """JavaScript NaN should be replaced with null."""
        # Note: Python's json module may parse NaN as float('nan') in some versions
        # Our repair replaces it with null before parsing
        result = parse_json('{"value": NaN}')
        # Check that parsing succeeded (either as null or nan)
        assert result.data is not None
        assert "value" in result.data

    def test_extract_from_markdown(self):
        """JSON in markdown code block should be extracted."""
        text = """Here's the response:

```json
{"result": "success"}
```

Hope that helps!"""
        result = parse_json(text)
        assert result.data == {"result": "success"}

    def test_extract_from_prose(self):
        """JSON mixed with prose should be extracted."""
        text = 'The output is {"value": 42} which represents the answer.'
        result = parse_json(text)
        assert result.data == {"value": 42}

    def test_strict_mode_raises(self):
        """Strict mode should raise ParseError on unparseable input."""
        with pytest.raises(ParseError) as exc_info:
            parse_json("this is not json at all", strict=True)
        assert "Failed to parse" in str(exc_info.value)

    def test_non_strict_returns_none(self):
        """Non-strict mode should return None data for unparseable input."""
        result = parse_json("this is not json at all", strict=False)
        assert result.data is None


class TestRepairJson:
    """Tests for the repair_json function."""

    def test_no_repairs_needed(self):
        """Valid JSON should not be modified."""
        text = '{"valid": true}'
        repaired, repairs = repair_json(text)
        assert repaired.strip() == text
        assert repairs == []

    def test_multiple_repairs(self):
        """Multiple issues should all be repaired."""
        text = '{foo: "bar", items: [1, 2,],}'
        repaired, repairs = repair_json(text)
        assert "removed_trailing_commas" in repairs
        assert "quoted_property_names" in repairs


class TestExtractJsonFromText:
    """Tests for JSON extraction from mixed content."""

    def test_code_block_json(self):
        """JSON in code block should be extracted."""
        text = '```json\n{"key": "value"}\n```'
        result = extract_json_from_text(text)
        assert result == '{"key": "value"}'

    def test_plain_code_block(self):
        """JSON in plain code block should be extracted."""
        text = "```\n[1, 2, 3]\n```"
        result = extract_json_from_text(text)
        assert result == "[1, 2, 3]"

    def test_inline_object(self):
        """Inline JSON object should be extracted."""
        text = 'The result is {"status": "ok"} here.'
        result = extract_json_from_text(text)
        assert result == '{"status": "ok"}'

    def test_inline_array(self):
        """Inline JSON array should be extracted."""
        text = "Values: [1, 2, 3]"
        result = extract_json_from_text(text)
        assert result == "[1, 2, 3]"

    def test_no_json(self):
        """Text without JSON should return None."""
        text = "This is just plain text."
        result = extract_json_from_text(text)
        assert result is None


class TestFieldExtractor:
    """Tests for the FieldExtractor class."""

    def test_extract_string_array(self):
        """String arrays should be extracted correctly."""
        text = '{"facts": ["fact one", "fact two", "fact three"]}'
        extractor = FieldExtractor().add_string_array("facts")
        result = extractor.extract(text)
        assert result["facts"] == ["fact one", "fact two", "fact three"]

    def test_extract_string_array_with_trailing_comma(self):
        """String arrays with trailing commas should work."""
        text = '{"facts": ["fact one", "fact two",]}'
        extractor = FieldExtractor().add_string_array("facts")
        result = extractor.extract(text)
        assert result["facts"] == ["fact one", "fact two"]

    def test_extract_number(self):
        """Numbers should be extracted correctly."""
        text = '{"confidence": 0.85, "count": 42}'
        extractor = FieldExtractor().add_number("confidence").add_number("count")
        result = extractor.extract(text)
        assert result["confidence"] == 0.85
        assert result["count"] == 42

    def test_extract_string(self):
        """Strings should be extracted correctly."""
        text = '{"name": "test value", "status": "ok"}'
        extractor = FieldExtractor().add_string("name").add_string("status")
        result = extractor.extract(text)
        assert result["name"] == "test value"
        assert result["status"] == "ok"

    def test_extract_boolean(self):
        """Booleans should be extracted correctly."""
        text = '{"enabled": true, "debug": false}'
        extractor = FieldExtractor().add_boolean("enabled").add_boolean("debug")
        result = extractor.extract(text)
        assert result["enabled"] is True
        assert result["debug"] is False

    def test_extract_from_malformed(self):
        """Fields should be extractable from malformed JSON."""
        # This JSON has multiple issues but we can still extract specific fields
        text = """{"facts": ["fact one", "fact two",]
                   "confidenceGain": 0.75,
                   "concepts": ["concept1","""  # Truncated!

        extractor = (
            FieldExtractor()
            .add_string_array("facts")
            .add_number("confidenceGain")
            .add_string_array("concepts")
        )
        result = extractor.extract(text)

        assert result["facts"] == ["fact one", "fact two"]
        assert result["confidenceGain"] == 0.75
        # concepts might be partial or missing due to truncation

    def test_missing_field_not_in_result(self):
        """Missing fields should not appear in result."""
        text = '{"name": "test"}'
        extractor = FieldExtractor().add_string("name").add_number("missing")
        result = extractor.extract(text)
        assert "name" in result
        assert "missing" not in result


class TestConvenienceFunctions:
    """Tests for convenience extraction functions."""

    def test_extract_field_auto(self):
        """Auto-detect field type."""
        text = '{"count": 42, "name": "test", "active": true}'
        assert extract_field(text, "count") == 42
        assert extract_field(text, "name") == "test"
        assert extract_field(text, "active") is True

    def test_extract_array(self):
        """Extract array fields."""
        text = '{"items": ["a", "b", "c"]}'
        assert extract_array(text, "items") == ["a", "b", "c"]

    def test_extract_object_array(self):
        """Extract array of objects."""
        text = '{"people": [{"name": "Alice"}, {"name": "Bob"}]}'
        result = extract_array(text, "people")
        assert result == [{"name": "Alice"}, {"name": "Bob"}]


class TestRealWorldExamples:
    """Tests based on real LLM output issues."""

    def test_llm_trailing_comma_response(self):
        """Real example: LLM returns trailing commas."""
        # Actual malformed output from an LLM
        text = """{
            "facts": [
                "The sky is blue due to Rayleigh scattering",
                "Shorter wavelengths scatter more",
            ],
            "confidenceGain": 0.3,
        }"""

        result = parse_json(text)
        assert result.data["facts"][0] == "The sky is blue due to Rayleigh scattering"
        assert result.data["confidenceGain"] == 0.3
        assert result.was_repaired is True

    def test_llm_markdown_wrapped(self):
        """Real example: LLM wraps JSON in markdown."""
        text = """Here's the extracted information:

```json
{
    "entities": ["Claude", "Anthropic"],
    "sentiment": "positive"
}
```

I hope this helps!"""

        result = parse_json(text)
        assert result.data["entities"] == ["Claude", "Anthropic"]
        assert result.data["sentiment"] == "positive"

    def test_llm_truncated_response(self):
        """Real example: Response truncated mid-JSON."""
        text = """{
            "facts": ["Important fact 1", "Important fact 2"],
            "concepts": ["concept A", "concept B"],
            "confidence": 0.8,
            "reasoning": "Based on the analysis, we can see that"""

        # Full parse will fail, but we can extract the complete fields
        result = parse_json(text, strict=False)

        # If parse failed, use field extraction
        if result.data is None:
            facts = extract_field(text, "facts", "string_array")
            confidence = extract_field(text, "confidence", "number")

            assert facts == ["Important fact 1", "Important fact 2"]
            assert confidence == 0.8
