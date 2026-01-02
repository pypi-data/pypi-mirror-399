"""JSON parsing and serialization for ONIX messages.

Supports loading ONIXMessage from:
- Path-like string (file path)
- dict object
- Iterable of dict objects (combined into single message)

Supports dumping ONIXMessage to:
- dict (via model_dump)
- JSON string
- File path
"""

from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
from typing import Any, Iterable

from onix.message import ONIXMessage


def json_to_message(
    source: str | PathLike[str] | dict[str, Any] | Iterable[dict[str, Any]],
    *,
    short_names: bool = False,
) -> ONIXMessage:
    """Parse an ONIX message from JSON.

    Args:
        source: One of:
            - Path-like string pointing to a JSON file
            - dict object representing a single message
            - Iterable of dict objects (products combined into one message)
        short_names: If True, expect short tag names in input;
            otherwise expect reference names (default).

    Returns:
        Parsed ONIXMessage instance.

    Raises:
        FileNotFoundError: If path doesn't exist
        json.JSONDecodeError: If JSON is invalid
        pydantic.ValidationError: If data doesn't match schema

    Example:
        >>> from onix.parsers import json_to_message
        >>> msg = json_to_message({"header": {}, "products": []})
        >>> msg = json_to_message("/path/to/message.json")
    """
    data = _normalize_input(source)

    if short_names:
        data = _normalize_json_keys(data)

    return ONIXMessage.model_validate(data)


def message_to_json(
    message: ONIXMessage,
    *,
    short_names: bool = False,
    indent: int | None = 2,
) -> str:
    """Serialize an ONIX message to a JSON string.

    Args:
        message: The ONIXMessage to serialize.
        short_names: If True, use short tag names in output;
            otherwise use reference names (default).
        indent: Indentation level for pretty-printing. None for compact.

    Returns:
        JSON string representation of the message.

    Example:
        >>> from onix import ONIXMessage, Header
        >>> from onix.parsers import message_to_json
        >>> msg = ONIXMessage(header=Header(), products=[])
        >>> json_str = message_to_json(msg)
    """
    data = message_to_dict(message, short_names=short_names)
    return json.dumps(data, indent=indent, ensure_ascii=False)


def message_to_dict(
    message: ONIXMessage,
    *,
    short_names: bool = False,
) -> dict[str, Any]:
    """Convert an ONIX message to a dictionary.

    Args:
        message: The ONIXMessage to convert.
        short_names: If True, use short tag names as keys;
            otherwise use reference names (default).

    Returns:
        Dictionary representation of the message.
    """
    # When short_names is requested we need reference tag names so they
    # can be converted to short tags. Otherwise prefer field names.
    if short_names:
        data = message.model_dump(
            by_alias=True, exclude_none=True, exclude_defaults=True
        )
    else:
        data = message.model_dump(
            by_alias=False, exclude_none=True, exclude_defaults=True
        )

    # Always include header even if empty (use field name)
    if "header" not in data:
        data["header"] = {}

    if short_names:
        data = _convert_reference_to_short(data)

    return data


def save_json(
    message: ONIXMessage,
    path: str | PathLike[str],
    *,
    short_names: bool = False,
    indent: int | None = 2,
) -> None:
    """Save an ONIX message to a JSON file.

    Args:
        message: The ONIXMessage to save.
        path: File path to write to.
        short_names: If True, use short tag names;
            otherwise use reference names (default).
        indent: Indentation level for pretty-printing.
    """
    json_str = message_to_json(message, short_names=short_names, indent=indent)
    Path(path).write_text(json_str, encoding="utf-8")


def _normalize_input(
    source: str | PathLike[str] | dict[str, Any] | Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Normalize various input types to a single dict."""
    # Handle string input (file path)
    if isinstance(source, str):
        path = Path(source)
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        raise FileNotFoundError(f"JSON file not found: {path}")

    # Handle PathLike input (file path)
    if isinstance(source, PathLike):
        path = Path(source)  # type: ignore[arg-type]  # ty can't narrow PathLike from Iterable
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        raise FileNotFoundError(f"JSON file not found: {path}")

    # Single dict
    if isinstance(source, dict):
        return source  # type: ignore[return-value]  # ty doesn't narrow dict properly

    # Iterable of dicts - combine products from multiple messages
    messages = list(source)
    if not messages:
        return {"header": {}, "products": []}

    # Use first message as base, combine products from all
    combined = dict(messages[0])
    combined_products: list[dict[str, Any]] = list(combined.get("products", []))

    for msg in messages[1:]:
        combined_products.extend(msg.get("products", []))

    combined["products"] = combined_products
    return combined


def _normalize_json_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Convert short tag names to reference names for Pydantic parsing.

    When short_names=True, we receive short tags (e.g., 'x507') which need to be
    converted to reference names (e.g., 'NoProduct') that Pydantic can recognize
    via Field(alias=...).
    """
    from onix.parsers.tags import to_reference_tag

    def normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # Convert short tag to reference tag (e.g., x507 -> NoProduct)
                # to_reference_tag returns the input unchanged if not found
                new_key = to_reference_tag(k)
                result[new_key] = normalize(v)
            return result
        if isinstance(obj, list):
            return [normalize(item) for item in obj]
        return obj

    return normalize(data)


def _convert_reference_to_short(data: dict[str, Any]) -> dict[str, Any]:
    """Convert reference tag names to short tags in a dict.

    Uses the tag resolver from tags.py to convert ONIX reference names
    (e.g., 'Header', 'NoProduct') to short tags (e.g., 'header', 'x507').
    """
    from onix.parsers.tags import to_short_tag

    def convert(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {to_short_tag(k): convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(item) for item in obj]
        return obj

    return convert(data)
