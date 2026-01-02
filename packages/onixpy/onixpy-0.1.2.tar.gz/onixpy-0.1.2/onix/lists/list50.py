"""ONIX Code List 50: Measure unit."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "cm": CodeListEntry(
        list_number=50,
        code="cm",
        heading="Centimeters",
        notes="Millimeters are the preferred metric unit of length",
        added_version=6,
    ),
    "gr": CodeListEntry(
        list_number=50,
        code="gr",
        heading="Grams",
    ),
    "in": CodeListEntry(
        list_number=50,
        code="in",
        heading="Inches (US)",
    ),
    "kg": CodeListEntry(
        list_number=50,
        code="kg",
        heading="Kilograms",
        notes="Grams are the preferred metric unit of weight",
        added_version=9,
    ),
    "lb": CodeListEntry(
        list_number=50,
        code="lb",
        heading="Pounds (US)",
        notes="Ounces are the preferred US customary unit of weight",
    ),
    "mm": CodeListEntry(
        list_number=50,
        code="mm",
        heading="Millimeters",
    ),
    "oz": CodeListEntry(
        list_number=50,
        code="oz",
        heading="Ounces (US)",
    ),
    "px": CodeListEntry(
        list_number=50,
        code="px",
        heading="Pixels",
        added_version=9,
    ),
}

List50 = CodeList(
    number=50,
    heading="Measure unit",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
MeasureUnit = List50
