"""
Core JSON parsing with recovery for LLM outputs.

LLMs often produce malformed JSON due to:
- Trailing commas in arrays/objects
- Unquoted property names
- Truncated output (context length limits)
- Missing closing brackets
- Extra text before/after JSON

This module provides robust parsing that recovers from these issues.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional


class ParseError(Exception):
    """Raised when JSON cannot be parsed even after repair attempts."""

    def __init__(self, message: str, original_text: str, attempts: list[str]):
        super().__init__(message)
        self.original_text = original_text
        self.attempts = attempts


@dataclass
class ParseResult:
    """Result of a JSON parse attempt with metadata about repairs."""

    data: Any
    """The parsed JSON data."""

    was_repaired: bool = False
    """Whether repairs were needed to parse the JSON."""

    repair_actions: list[str] = field(default_factory=list)
    """List of repairs that were applied."""

    original_text: str = ""
    """The original text before any repairs."""

    repaired_text: str = ""
    """The text after repairs (same as original if no repairs needed)."""


def repair_json(text: str) -> tuple[str, list[str]]:
    """
    Attempt to repair common JSON formatting issues from LLM output.

    Args:
        text: The potentially malformed JSON string

    Returns:
        Tuple of (repaired_text, list_of_repairs_applied)

    Common issues fixed:
    - Trailing commas: `[1, 2, 3,]` -> `[1, 2, 3]`
    - Unquoted keys: `{foo: "bar"}` -> `{"foo": "bar"}`
    - Single quotes: `{'foo': 'bar'}` -> `{"foo": "bar"}`
    - Missing closing brackets (adds them)
    - JavaScript literals: `undefined`, `NaN` -> `null`
    """
    repairs = []
    result = text.strip()

    # Fix trailing commas in arrays and objects
    # Match comma followed by whitespace and closing bracket
    trailing_comma_pattern = r",(\s*[\]\}])"
    if re.search(trailing_comma_pattern, result):
        result = re.sub(trailing_comma_pattern, r"\1", result)
        repairs.append("removed_trailing_commas")

    # Fix unquoted property names
    # Match: start of object or comma, optional whitespace, unquoted identifier, colon
    unquoted_key_pattern = r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)"
    if re.search(unquoted_key_pattern, result):
        result = re.sub(unquoted_key_pattern, r'\1"\2"\3', result)
        repairs.append("quoted_property_names")

    # Fix single quotes (but be careful with apostrophes in strings)
    # Only do this if we can detect it's using single quotes for strings
    if result.startswith("{'") or "': '" in result or "': {" in result:
        # Simple approach: replace single quotes that look like JSON delimiters
        result = re.sub(r"'(\s*:\s*)'", r'"\1"', result)
        result = re.sub(r"'(\s*:\s*)\[", r'"\1[', result)
        result = re.sub(r"'(\s*:\s*)\{", r'"\1{', result)
        result = re.sub(r"'(\s*:\s*)([0-9])", r'"\1\2', result)
        result = re.sub(r"'(\s*:\s*)(true|false|null)", r'"\1\2', result)
        result = re.sub(r"\[(\s*)'", r'[\1"', result)
        result = re.sub(r"'(\s*)\]", r'"\1]', result)
        result = re.sub(r"\{(\s*)'", r'{\1"', result)
        result = re.sub(r"'(\s*)\}", r'"\1}', result)
        result = re.sub(r"'(\s*),", r'"\1,', result)
        result = re.sub(r",(\s*)'", r',\1"', result)
        if "single_quotes_to_double" not in repairs:
            repairs.append("single_quotes_to_double")

    # Fix JavaScript literals
    js_literals = [
        (r"\bundefined\b", "null"),
        (r"\bNaN\b", "null"),
        (r"\bInfinity\b", "null"),
        (r"\b-Infinity\b", "null"),
    ]
    for pattern, replacement in js_literals:
        if re.search(pattern, result):
            result = re.sub(pattern, replacement, result)
            repairs.append(f"replaced_{pattern[2:-2]}_with_null")

    # Try to fix unbalanced brackets by adding missing closers
    open_brackets = result.count("[") - result.count("]")
    open_braces = result.count("{") - result.count("}")

    if open_brackets > 0:
        result = result + "]" * open_brackets
        repairs.append(f"added_{open_brackets}_closing_brackets")

    if open_braces > 0:
        result = result + "}" * open_braces
        repairs.append(f"added_{open_braces}_closing_braces")

    return result, repairs


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that may contain other content.

    LLMs often wrap JSON in markdown code blocks or add explanatory text.
    This function finds and extracts the JSON portion.

    Args:
        text: Text that may contain JSON

    Returns:
        The extracted JSON string, or None if no JSON found
    """
    # Try to find JSON in markdown code blocks first
    code_block_patterns = [
        r"```json\s*([\s\S]*?)\s*```",  # ```json ... ```
        r"```\s*([\s\S]*?)\s*```",  # ``` ... ```
    ]

    for pattern in code_block_patterns:
        match = re.search(pattern, text)
        if match:
            content = match.group(1).strip()
            if content.startswith("{") or content.startswith("["):
                return content

    # Try to find raw JSON (object or array)
    # Find the first { or [ and try to match its closing bracket
    json_patterns = [
        r"(\{[\s\S]*\})",  # Object
        r"(\[[\s\S]*\])",  # Array
    ]

    for pattern in json_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None


def parse_json(
    text: str,
    *,
    strict: bool = False,
    extract_from_text: bool = True,
) -> ParseResult:
    """
    Parse JSON from LLM output with automatic repair.

    This is the main entry point for parsing JSON from LLM outputs.
    It will:
    1. Optionally extract JSON from surrounding text
    2. Attempt direct parsing
    3. If that fails, apply repairs and retry
    4. Return detailed results about what was parsed and how

    Args:
        text: The text containing JSON to parse
        strict: If True, raise ParseError instead of returning partial results
        extract_from_text: If True, try to extract JSON from markdown/prose

    Returns:
        ParseResult with the parsed data and repair metadata

    Raises:
        ParseError: If strict=True and parsing fails after all attempts

    Example:
        >>> result = parse_json('{"items": [1, 2, 3,]}')  # trailing comma
        >>> result.data
        {'items': [1, 2, 3]}
        >>> result.was_repaired
        True
        >>> result.repair_actions
        ['removed_trailing_commas']
    """
    original_text = text
    json_text = text.strip()

    # Step 1: Try to extract JSON from surrounding text
    if extract_from_text:
        extracted = extract_json_from_text(json_text)
        if extracted:
            json_text = extracted

    # Step 2: Try direct parsing
    try:
        data = json.loads(json_text)
        return ParseResult(
            data=data,
            was_repaired=False,
            repair_actions=[],
            original_text=original_text,
            repaired_text=json_text,
        )
    except json.JSONDecodeError:
        pass  # Continue to repair attempts

    # Step 3: Try parsing with repairs
    attempts = ["direct_parse"]
    repaired_text, repairs = repair_json(json_text)

    try:
        data = json.loads(repaired_text)
        return ParseResult(
            data=data,
            was_repaired=True,
            repair_actions=repairs,
            original_text=original_text,
            repaired_text=repaired_text,
        )
    except json.JSONDecodeError as e:
        attempts.append(f"repair_attempt: {repairs}")

        if strict:
            raise ParseError(
                f"Failed to parse JSON after repair attempts: {e}",
                original_text=original_text,
                attempts=attempts,
            )

        # Return None result for non-strict mode
        return ParseResult(
            data=None,
            was_repaired=False,
            repair_actions=[],
            original_text=original_text,
            repaired_text=repaired_text,
        )
