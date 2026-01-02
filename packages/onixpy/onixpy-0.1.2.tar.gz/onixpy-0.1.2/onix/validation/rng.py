"""RELAX NG schema validation for ONIX messages.

Validates XML output against the official ONIX for Books 3.1 RNG schemas.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from lxml import etree

if TYPE_CHECKING:
    from lxml.etree import RelaxNG, _Element

# Path to RNG schema files
_SCHEMA_DIR = Path(__file__).parent.parent.parent.parent / "tests" / "rng"
_REFERENCE_SCHEMA = _SCHEMA_DIR / "ONIX_BookProduct_3.1_reference.rng"


class RNGValidationError(Exception):
    """Raised when XML fails RNG validation."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


def _get_rng_validator(schema_path: Path | None = None) -> RelaxNG:
    """Load and return an RNG validator.

    Args:
        schema_path: Path to the RNG schema file. If None, uses the default
            reference schema for ONIX 3.1.

    Returns:
        Compiled RelaxNG validator.

    Raises:
        FileNotFoundError: If schema file doesn't exist.
        etree.RelaxNGParseError: If schema is invalid.
    """
    if schema_path is None:
        schema_path = _REFERENCE_SCHEMA

    if not schema_path.exists():
        raise FileNotFoundError(f"RNG schema not found: {schema_path}")

    # Parse with base_url to allow RNG includes to resolve
    with open(schema_path, "rb") as f:
        base_url = f"file://{schema_path.parent.absolute()}/"
        schema_doc = etree.parse(f, base_url=base_url)

    return etree.RelaxNG(schema_doc)


def validate_xml_element(
    element: _Element,
    schema_path: Path | None = None,
) -> None:
    """Validate an XML element against an RNG schema.

    Args:
        element: lxml Element to validate.
        schema_path: Path to RNG schema. If None, uses default reference schema.

    Raises:
        RNGValidationError: If validation fails.

    Example:
        >>> from lxml import etree
        >>> from onix.validation import validate_xml_element
        >>> element = etree.fromstring("<ONIXMessage>...</ONIXMessage>")
        >>> validate_xml_element(element)
    """
    validator = _get_rng_validator(schema_path)

    if not validator.validate(element):
        error_log = validator.error_log
        errors = [str(error) for error in error_log]
        raise RNGValidationError(
            f"XML validation failed with {len(errors)} error(s)",
            errors=errors,
        )


def validate_xml_string(
    xml_string: str,
    schema_path: Path | None = None,
) -> None:
    """Validate an XML string against an RNG schema.

    Args:
        xml_string: XML string to validate.
        schema_path: Path to RNG schema. If None, uses default reference schema.

    Raises:
        RNGValidationError: If validation fails.
        etree.XMLSyntaxError: If XML is malformed.

    Example:
        >>> from onix.validation import validate_xml_string
        >>> xml = '<?xml version="1.0"?><ONIXMessage>...</ONIXMessage>'
        >>> validate_xml_string(xml)
    """
    element = etree.fromstring(xml_string.encode("utf-8"))
    validate_xml_element(element, schema_path)


def validate_xml_file(
    file_path: str | Path,
    schema_path: Path | None = None,
) -> None:
    """Validate an XML file against an RNG schema.

    Args:
        file_path: Path to XML file to validate.
        schema_path: Path to RNG schema. If None, uses default reference schema.

    Raises:
        RNGValidationError: If validation fails.
        FileNotFoundError: If XML file doesn't exist.
        etree.XMLSyntaxError: If XML is malformed.

    Example:
        >>> from onix.validation import validate_xml_file
        >>> validate_xml_file("/path/to/message.xml")
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"XML file not found: {path}")

    with open(path, "rb") as f:
        doc = etree.parse(f)

    validate_xml_element(doc.getroot(), schema_path)
