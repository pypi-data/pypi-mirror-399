"""ONIX parsers for JSON and XML formats.

This module provides functions to parse and serialize ONIX messages
from/to JSON and XML formats.

Parsing functions:
- json_to_message: Parse ONIX from JSON (path, dict, or iterable)
- xml_to_message: Parse ONIX from XML (path, string, Element, or iterable)

Serialization functions:
- message_to_json: Serialize ONIX to JSON string
- message_to_dict: Convert ONIX to dictionary
- save_json: Save ONIX to JSON file
- message_to_xml: Convert ONIX to XML Element
- message_to_xml_string: Serialize ONIX to XML string
- save_xml: Save ONIX to XML file

Tag resolution:
- to_short_tag: Convert reference tag to short tag
- to_reference_tag: Convert short tag to reference tag

Field mapping:
- tag_to_field_name: Convert XML tag to Python field name
- field_name_to_tag: Convert Python field name to XML tag

All parse/serialize functions accept a `short_names=True` flag to work
with short tag names instead of the default reference names.

Note: For RNG schema validation, see onix.validation module.
"""

from onix.parsers.fields import (
    field_name_to_tag,
    tag_to_field_name,
)
from onix.parsers.json import (
    json_to_message,
    message_to_dict,
    message_to_json,
    save_json,
)
from onix.parsers.tags import (
    is_reference_tag,
    is_short_tag,
    to_reference_tag,
    to_short_tag,
)
from onix.parsers.xml import (
    message_to_xml,
    message_to_xml_string,
    save_xml,
    xml_to_message,
)

__all__ = [
    # JSON
    "json_to_message",
    "message_to_json",
    "message_to_dict",
    "save_json",
    # XML
    "xml_to_message",
    "message_to_xml",
    "message_to_xml_string",
    "save_xml",
    # Tags
    "to_short_tag",
    "to_reference_tag",
    "is_short_tag",
    "is_reference_tag",
    # Fields
    "tag_to_field_name",
    "field_name_to_tag",
]
