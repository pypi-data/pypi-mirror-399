# onixpy - ONIX for Books Library

[![License: LGPL-3.0-or-later](https://img.shields.io/badge/License-LGPL--3.0--or--later-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)
[![CI](https://github.com/hodeinavarro/onixpy/actions/workflows/ci.yml/badge.svg)](https://github.com/hodeinavarro/onixpy/actions) [![Codecov](https://codecov.io/gh/hodeinavarro/onixpy/branch/main/graph/badge.svg)](https://codecov.io/gh/hodeinavarro/onixpy) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

A Python library for parsing and working with ONIX for Books metadata (publishing industry standard). Built with Pydantic for type-safe data models.

## Features

- **ONIX 3.1 Support** - Parse and create ONIX 3.1 messages with full specification coverage
- **Type-Safe Models** - Pydantic v2 models with comprehensive type annotations
- **Dual Format Support** - Parse from and serialize to both XML and JSON formats
- **Reference & Short Tags** - Support for both reference names (`ONIXMessage`) and short tags (`ONIXmessage`)
- **Smart Model Behavior** - Constructors accept snake_case field names, validate by field name, and serialize using XML aliases
- **Code List Validation** - 30+ built-in ONIX code lists with automatic validation
- **RNG Schema Validation** - Validate messages against RELAX NG schema
- **Comprehensive Block Coverage** - Models for all major ONIX blocks (DescriptiveDetail, PublishingDetail, RelatedMaterial, etc.)

## Installation

```bash
pip install onixpy
```

## Quick Start

### Creating an ONIX Message

```python
from onix import ONIXMessage, Header, Product, ProductIdentifier, Sender

# Create a complete message
message = ONIXMessage(
    release="3.1",
    Header=Header(
        Sender=Sender(sender_name="MyPublisher"),
        SentDateTime="20231201T120000Z",
    ),
    Product=[
        Product(
            RecordReference="com.mypublisher.001",
            NotificationType="03",  # Notification confirmed
            ProductIdentifier=[
                ProductIdentifier(
                    ProductIDType="15",  # ISBN-13
                    IDValue="9780000000001"
                )
            ],
        ),
    ],
)
```

### Parsing ONIX

```python
from onix.parsers import json_to_message, xml_to_message

# From JSON (file path, dict, or iterable)
message = json_to_message("/path/to/message.json")
message = json_to_message({"header": {...}, "products": [...]})

# From XML (file path, string, Element, or iterable)
message = xml_to_message("/path/to/message.xml")
message = xml_to_message("<ONIXMessage>...</ONIXMessage>")

# Using short tag names
message = json_to_message(data, short_names=True)
message = xml_to_message(xml_string, short_names=True)
```

### Serializing ONIX

```python
from onix.parsers import message_to_json, message_to_xml_string, save_xml, save_json

# To JSON string
json_str = message_to_json(message)
json_str = message_to_json(message, short_names=True)  # Use short tags

# To XML string
xml_str = message_to_xml_string(message)
xml_str = message_to_xml_string(message, short_names=True)  # Use short tags

# Save to files
save_json(message, "/path/to/output.json")
save_xml(message, "/path/to/output.xml")
```

### Working with Code Lists

```python
from onix.lists import get_list, get_code, list_available

# Get all available list numbers
available = list_available()  # [1, 2, 5, 9, 12, 15, ...]

# Get a complete code list
list_5 = get_list(5)  # Product identifier type
print(list_5.heading)  # "Product identifier type"

# Get a specific code entry
isbn_13 = get_code(5, "15")
print(isbn_13.heading)  # "ISBN-13"
print(isbn_13.notes)  # Additional information about the code

# Access code lists by name
from onix.lists import ProductIdentifierType, NameIdentifierType
```

### RNG Schema Validation

```python
from onix.validation import validate_onix_message, validate_xml_element
from onix.parsers import message_to_xml

# Validate a message
message = ONIXMessage(...)
is_valid, errors = validate_onix_message(message)
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")

# Validate raw XML
xml_element = message_to_xml(message)
is_valid, errors = validate_xml_element(xml_element)
```

## Project Structure

```
onixpy/
├── src/onix/
│   ├── __init__.py          # Public API
│   ├── message.py           # ONIXMessage, ONIXAttributes
│   ├── header/              # Header composites
│   │   ├── header.py        # Header, Sender, Addressee
│   │   └── __init__.py
│   ├── product/             # Product models
│   │   ├── product.py       # Product, ProductIdentifier
│   │   ├── b1/              # Block 1: Product description
│   │   ├── b4/              # Block 4: Publishing detail
│   │   ├── b5/              # Block 5: Related material
│   │   └── __init__.py
│   ├── parsers/             # JSON/XML parsing
│   │   ├── json.py          # JSON parser
│   │   ├── xml.py           # XML parser
│   │   ├── tags.py          # Tag name resolution
│   │   └── fields.py        # Field name mapping
│   ├── lists/               # ONIX code lists
│   │   ├── models.py        # CodeList, CodeListEntry
│   │   ├── list1.py         # Notification type
│   │   ├── list5.py         # Product identifier type
│   │   └── ...              # 30+ code lists
│   └── validation/          # RNG schema validation
│       └── rng.py
└── tests/                   # Comprehensive test suite
```

## Requirements

- Python 3.10+
- pydantic >= 2.12.5
- lxml >= 4.8.0

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/hodeinavarro/onixpy.git
cd onixpy

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests with coverage
uv run pytest --cov=src/onix --cov-report=term-missing --cov-report=html

# Run specific test categories
uv run pytest tests/core/         # Core model tests
uv run pytest tests/parsers/      # Parser tests
uv run pytest tests/validation/   # Validation tests

# Run with markers
uv run pytest -m "not slow"       # Skip slow tests
```

### Code Quality

```bash
# Lint and format with ruff
uv run ruff check .
uv run ruff format .

# Type checking with ty (experimental)
uv run ty check
```

### Generating Code Lists

```bash
# Generate a new code list from ONIX specification
cd scripts
uv run python generate_codelist.py <list_number>

# Example
uv run python generate_codelist.py 44
```

## API Design Principles

- **Reference names by default**: All parsers/serializers use ONIX reference tag names (e.g., `ONIXMessage`, `Header`). Short names require explicit `short_names=True`.
- **Strict validation**: Code list values are validated against their respective lists. Invalid codes raise `ValidationError`.
- **Field aliases**: Pydantic `Field(alias=...)` definitions are the single source of truth for XML tag/field name mapping.

## Contributing

Contributions are welcome! Please follow the full guidelines in [CONTRIBUTING.md](CONTRIBUTING.md), which includes our AI assistance disclosure policy and PR checklist.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the project conventions (see `.github/copilot-instructions.md`)
4. Run tests and linting
5. Submit a pull request (use the PR template and disclose any AI assistance)

## License

Licensed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**. See [LICENSE.md](LICENSE.md) for details.
