"""Field mapping utilities for ONIX XML tag/field name conversion.

This module provides dynamic mapping between XML tag names (CamelCase) and
Python field names (snake_case) by introspecting Pydantic model aliases.

The Field(alias=...) on each model field is the source of truth for the
tag name. This module builds lookup tables from those aliases.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

# Special cases where field name differs from simple snake_case conversion
# of the alias (e.g., list fields that need pluralization)
_FIELD_OVERRIDES: dict[str, str] = {
    # XML tag -> Python field name
    # List elements use singular XML tags but plural field names
}

_TAG_OVERRIDES: dict[str, str] = {
    # Python field name -> XML tag
    # Inverse of FIELD_OVERRIDES
}


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case.

    Handles consecutive capitals like IDType -> id_type.
    """
    # Insert underscore before uppercase letters preceded by lowercase
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # Insert underscore before uppercase followed by lowercase (handles acronyms)
    s2 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s1)
    return s2.lower()


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to CamelCase.

    Special handling for common patterns like id -> ID.
    """
    parts = name.split("_")
    result = []
    for i, part in enumerate(parts):
        # Handle special abbreviations
        if part.lower() in ("id", "xml", "url", "isbn", "isni", "ean", "gtin"):
            result.append(part.upper())
        else:
            result.append(part.title())
    return "".join(result)


@lru_cache(maxsize=256)
def tag_to_field_name(tag: str) -> str:
    """Convert XML tag to Python field name.

    Uses model aliases if available, otherwise falls back to snake_case conversion.

    Args:
        tag: The XML tag name (CamelCase reference name)

    Returns:
        The Python field name (snake_case)
    """
    # Check overrides first
    if tag in _FIELD_OVERRIDES:
        return _FIELD_OVERRIDES[tag]

    # Check if we have a cached mapping from model registration
    if tag in _tag_to_field_cache:
        return _tag_to_field_cache[tag]

    # Fall back to simple conversion
    return _camel_to_snake(tag)


@lru_cache(maxsize=256)
def field_name_to_tag(field_name: str) -> str:
    """Convert Python field name to XML tag.

    Uses model aliases if available, otherwise falls back to CamelCase conversion.

    Args:
        field_name: The Python field name (snake_case)

    Returns:
        The XML tag name (CamelCase reference name)
    """
    # Check overrides first
    if field_name in _TAG_OVERRIDES:
        return _TAG_OVERRIDES[field_name]

    # Check if we have a cached mapping from model registration
    if field_name in _field_to_tag_cache:
        return _field_to_tag_cache[field_name]

    # Fall back to simple conversion
    return _snake_to_camel(field_name)


# Caches populated by register_model
_tag_to_field_cache: dict[str, str] = {}
_field_to_tag_cache: dict[str, str] = {}
_list_field_names: set[str] = set()  # Fields that should always be lists


def register_model(model_class: type["BaseModel"]) -> None:
    """Register a Pydantic model's field aliases for tag mapping.

    Extracts alias information from model fields and populates the
    tag/field name caches.

    Args:
        model_class: A Pydantic BaseModel subclass with Field(alias=...) definitions
    """
    for field_name, field_info in model_class.model_fields.items():
        alias = field_info.alias
        if alias:
            _tag_to_field_cache[alias] = field_name
            _field_to_tag_cache[field_name] = alias


def register_plural_mapping(tag: str, field_name: str) -> None:
    """Register a mapping for list fields where XML uses singular tags.

    For fields like `products` where the XML uses `<Product>` tags,
    we need an explicit mapping since the alias can't capture pluralization.

    Args:
        tag: The singular XML tag name (e.g., "Product")
        field_name: The plural Python field name (e.g., "products")
    """
    _tag_to_field_cache[tag] = field_name
    _field_to_tag_cache[field_name] = tag
    _list_field_names.add(field_name)


def is_list_field(field_name: str) -> bool:
    """Check if a field should always be a list.

    Args:
        field_name: The Python field name

    Returns:
        True if the field should always be a list
    """
    return field_name in _list_field_names


def clear_caches() -> None:
    """Clear all tag/field mapping caches.

    Useful for testing or when models need to be re-registered.
    """
    _tag_to_field_cache.clear()
    _field_to_tag_cache.clear()
    _list_field_names.clear()
    tag_to_field_name.cache_clear()
    field_name_to_tag.cache_clear()
