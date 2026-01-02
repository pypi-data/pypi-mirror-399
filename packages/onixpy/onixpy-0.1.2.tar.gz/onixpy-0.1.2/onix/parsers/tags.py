"""ONIX tag name resolver.

Maps between reference tag names and short tag names.
Reference names are used by default; short names require explicit opt-in.

Tag mappings are dynamically built from Pydantic model field metadata
(json_schema_extra={'short_tag': '...'}) for consistency and maintainability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

# Cache for tag mappings built from model introspection
_REFERENCE_TO_SHORT: dict[str, str] = {}
_SHORT_TO_REFERENCE: dict[str, str] = {}


def _build_tag_mappings() -> None:
    """Build tag mappings from all registered ONIX models.

    Introspects Pydantic models to extract short_tag metadata from
    json_schema_extra on each field.
    """
    # Add root element mapping (can't be in json_schema_extra since it's the class itself)
    _REFERENCE_TO_SHORT["ONIXMessage"] = "ONIXmessage"
    _SHORT_TO_REFERENCE["ONIXmessage"] = "ONIXMessage"

    from onix.header import (
        Addressee,
        AddresseeIdentifier,
        Header,
        Sender,
        SenderIdentifier,
    )
    from onix.message import ONIXMessage
    from onix.product import Product, ProductIdentifier

    # Try to import Block 1 models if they exist
    try:
        from onix.product.b1 import (
            DescriptiveDetail,
            EpubLicense,
            EpubLicenseDate,
            EpubLicenseExpression,
            EpubUsageConstraint,
            EpubUsageLimit,
            ProductClassification,
            ProductFormFeature,
        )
        from onix.product.b1.p11 import Measure

        block1_models = [
            DescriptiveDetail,
            ProductFormFeature,
            EpubUsageLimit,
            EpubUsageConstraint,
            EpubLicenseDate,
            EpubLicenseExpression,
            EpubLicense,
            ProductClassification,
            Measure,
        ]
    except ImportError:
        block1_models = []

    models = [
        ONIXMessage,
        Header,
        Sender,
        Addressee,
        SenderIdentifier,
        AddresseeIdentifier,
        Product,
        ProductIdentifier,
    ] + block1_models

    for model in models:
        _extract_tag_mappings_from_model(model)


def _extract_tag_mappings_from_model(model_class: type["BaseModel"]) -> None:
    """Extract tag mappings from a single Pydantic model.

    Args:
        model_class: A Pydantic BaseModel subclass with Field definitions
    """
    for field_name, field_info in model_class.model_fields.items():
        alias = field_info.alias
        if not alias:
            continue

        # Check for short_tag in json_schema_extra
        short_tag = None
        if field_info.json_schema_extra:
            if isinstance(field_info.json_schema_extra, dict):
                short_tag = field_info.json_schema_extra.get("short_tag")

        if short_tag:
            _REFERENCE_TO_SHORT[alias] = short_tag
            _SHORT_TO_REFERENCE[short_tag] = alias


def _ensure_mappings_loaded() -> None:
    """Ensure tag mappings are loaded (lazy initialization)."""
    if not _REFERENCE_TO_SHORT:
        _build_tag_mappings()


def to_short_tag(reference_name: str) -> str:
    """Convert a reference tag name to its short tag equivalent.

    Args:
        reference_name: The reference tag name (e.g., "Header")

    Returns:
        The short tag name (e.g., "header"), or the original name
        if no mapping exists.

    Example:
        >>> to_short_tag("Header")
        'header'
        >>> to_short_tag("MeasureType")
        'x315'
        >>> to_short_tag("UnknownTag")
        'UnknownTag'
    """
    _ensure_mappings_loaded()
    return _REFERENCE_TO_SHORT.get(reference_name, reference_name)


def to_reference_tag(short_tag: str) -> str:
    """Convert a short tag name to its reference tag equivalent.

    Args:
        short_tag: The short tag name (e.g., "header", "x315")

    Returns:
        The reference tag name (e.g., "Header", "MeasureType"), or the
        original name if no mapping exists.

    Example:
        >>> to_reference_tag("header")
        'Header'
        >>> to_reference_tag("x315")
        'MeasureType'
        >>> to_reference_tag("UnknownTag")
        'UnknownTag'
    """
    _ensure_mappings_loaded()
    return _SHORT_TO_REFERENCE.get(short_tag, short_tag)


def is_short_tag(tag_name: str) -> bool:
    """Check if a tag name is a known short tag.

    Args:
        tag_name: The tag name to check

    Returns:
        True if the tag is a known short tag, False otherwise.
    """
    _ensure_mappings_loaded()
    return tag_name in _SHORT_TO_REFERENCE


def is_reference_tag(tag_name: str) -> bool:
    """Check if a tag name is a known reference tag.

    Args:
        tag_name: The tag name to check

    Returns:
        True if the tag is a known reference tag, False otherwise.
    """
    _ensure_mappings_loaded()
    return tag_name in _REFERENCE_TO_SHORT
