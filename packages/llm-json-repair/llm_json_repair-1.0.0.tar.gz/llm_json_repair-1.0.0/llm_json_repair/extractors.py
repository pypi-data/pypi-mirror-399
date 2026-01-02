"""
Field extraction utilities for partially parseable JSON.

When JSON is too malformed to parse completely, these utilities
can extract specific fields using regex patterns. This is useful
for recovering partial data from truncated or corrupted LLM responses.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union


@dataclass
class FieldExtractor:
    """
    Configurable field extractor for recovering data from malformed JSON.

    Use this when you know the structure you're expecting and want to
    extract specific fields even if the overall JSON is invalid.

    Example:
        >>> extractor = FieldExtractor()
        >>> extractor.add_string_array("facts")
        >>> extractor.add_number("confidence")
        >>> result = extractor.extract(malformed_json_text)
        >>> result.get("facts")  # ["fact1", "fact2"]
        >>> result.get("confidence")  # 0.85
    """

    def __init__(self):
        self._fields: list[tuple[str, str, Callable]] = []

    def add_string_array(self, field_name: str) -> "FieldExtractor":
        """Add a string array field to extract."""
        self._fields.append((field_name, "string_array", self._extract_string_array))
        return self

    def add_object_array(self, field_name: str) -> "FieldExtractor":
        """Add an object array field to extract."""
        self._fields.append((field_name, "object_array", self._extract_object_array))
        return self

    def add_number(self, field_name: str) -> "FieldExtractor":
        """Add a number field to extract."""
        self._fields.append((field_name, "number", self._extract_number))
        return self

    def add_string(self, field_name: str) -> "FieldExtractor":
        """Add a string field to extract."""
        self._fields.append((field_name, "string", self._extract_string))
        return self

    def add_boolean(self, field_name: str) -> "FieldExtractor":
        """Add a boolean field to extract."""
        self._fields.append((field_name, "boolean", self._extract_boolean))
        return self

    def add_object(self, field_name: str) -> "FieldExtractor":
        """Add an object field to extract."""
        self._fields.append((field_name, "object", self._extract_object_field))
        return self

    def extract(self, text: str) -> dict[str, Any]:
        """
        Extract all configured fields from the text.

        Returns a dict with field names as keys. Fields that couldn't
        be extracted will not be present in the result.
        """
        result = {}
        for field_name, field_type, extractor in self._fields:
            value = extractor(text, field_name)
            if value is not None:
                result[field_name] = value
        return result

    def _extract_string_array(self, text: str, field_name: str) -> Optional[list[str]]:
        """Extract a string array field."""
        # Pattern: "fieldName": ["item1", "item2", ...]
        pattern = rf'"{field_name}"\s*:\s*\[([\s\S]*?)\]'
        match = re.search(pattern, text)
        if not match:
            return None

        array_content = match.group(1).strip()
        if not array_content:
            return []

        # Try to parse as JSON array first
        try:
            # Fix trailing comma and parse
            fixed = f"[{array_content.rstrip(',')}]"
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Fall back to regex extraction of quoted strings
        strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', array_content)
        return strings if strings else None

    def _extract_object_array(self, text: str, field_name: str) -> Optional[list[dict]]:
        """Extract an array of objects field."""
        pattern = rf'"{field_name}"\s*:\s*\[([\s\S]*?)\](?=\s*[,\}}])'
        match = re.search(pattern, text)
        if not match:
            return None

        array_content = match.group(1).strip()
        if not array_content:
            return []

        # Try to parse as JSON array
        try:
            fixed = f"[{array_content.rstrip(',')}]"
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Try to extract individual objects
        objects = []
        obj_pattern = r"\{[^{}]*\}"
        for obj_match in re.finditer(obj_pattern, array_content):
            try:
                obj = json.loads(obj_match.group())
                objects.append(obj)
            except json.JSONDecodeError:
                continue

        return objects if objects else None

    def _extract_number(self, text: str, field_name: str) -> Optional[Union[int, float]]:
        """Extract a number field."""
        pattern = rf'"{field_name}"\s*:\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)'
        match = re.search(pattern, text)
        if not match:
            return None

        num_str = match.group(1)
        try:
            if "." in num_str or "e" in num_str.lower():
                return float(num_str)
            return int(num_str)
        except ValueError:
            return None

    def _extract_string(self, text: str, field_name: str) -> Optional[str]:
        """Extract a string field."""
        pattern = rf'"{field_name}"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"'
        match = re.search(pattern, text)
        if not match:
            return None
        return match.group(1)

    def _extract_boolean(self, text: str, field_name: str) -> Optional[bool]:
        """Extract a boolean field."""
        pattern = rf'"{field_name}"\s*:\s*(true|false)'
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None
        return match.group(1).lower() == "true"

    def _extract_object_field(self, text: str, field_name: str) -> Optional[dict]:
        """Extract a nested object field."""
        # Find the field and try to match balanced braces
        pattern = rf'"{field_name}"\s*:\s*\{{'
        match = re.search(pattern, text)
        if not match:
            return None

        start = match.end() - 1  # Include the opening brace
        depth = 0
        end = start

        for i, char in enumerate(text[start:], start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if depth != 0:
            return None  # Unbalanced braces

        obj_str = text[start:end]
        try:
            # Try to parse, potentially with repairs
            from .parser import repair_json

            repaired, _ = repair_json(obj_str)
            return json.loads(repaired)
        except (json.JSONDecodeError, Exception):
            return None


def extract_field(text: str, field_name: str, field_type: str = "auto") -> Any:
    """
    Convenience function to extract a single field.

    Args:
        text: The JSON text to extract from
        field_name: Name of the field to extract
        field_type: One of "auto", "string", "number", "boolean",
                   "string_array", "object_array", "object"

    Returns:
        The extracted value, or None if not found
    """
    extractor = FieldExtractor()

    if field_type == "auto":
        # Try all types and return first match
        for ftype in ["number", "boolean", "string", "string_array", "object_array", "object"]:
            result = extract_field(text, field_name, ftype)
            if result is not None:
                return result
        return None

    method_map = {
        "string": extractor.add_string,
        "number": extractor.add_number,
        "boolean": extractor.add_boolean,
        "string_array": extractor.add_string_array,
        "object_array": extractor.add_object_array,
        "object": extractor.add_object,
    }

    if field_type not in method_map:
        raise ValueError(f"Unknown field type: {field_type}")

    method_map[field_type](field_name)
    result = extractor.extract(text)
    return result.get(field_name)


def extract_array(text: str, field_name: str) -> Optional[list]:
    """Convenience function to extract an array field (auto-detects string vs object)."""
    # Try object array first (more specific)
    result = extract_field(text, field_name, "object_array")
    if result:
        return result
    return extract_field(text, field_name, "string_array")


def extract_object(text: str, field_name: str) -> Optional[dict]:
    """Convenience function to extract an object field."""
    return extract_field(text, field_name, "object")
