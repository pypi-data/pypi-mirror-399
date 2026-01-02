"""ONIX Code List 2: Product composition."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=2,
        code="00",
        heading="Single-component retail product",
        added_version=9,
    ),
    "01": CodeListEntry(
        list_number=2,
        code="01",
        heading="Single-component, not available separately",
        notes="Used only when an ONIX record is required for a component-as-an-item, even though it is not currently available as such",
        added_version=53,
    ),
    "10": CodeListEntry(
        list_number=2,
        code="10",
        heading="Multiple-component retail product",
        notes="Multiple-component product retailed as a whole",
        added_version=9,
    ),
    "11": CodeListEntry(
        list_number=2,
        code="11",
        heading="Multiple-item collection, retailed as separate parts",
        notes="Used only when an ONIX record is required for a collection-as-a-whole, even though it is not currently retailed as such",
        added_version=9,
    ),
    "20": CodeListEntry(
        list_number=2,
        code="20",
        heading="Trade-only product",
        notes="Product available to the book trade, but not for retail sale, and not carrying retail items, eg empty dumpbin, empty counterpack, promotional material",
        added_version=9,
    ),
    "30": CodeListEntry(
        list_number=2,
        code="30",
        heading="Multiple-item trade-only pack",
        notes="Product available to the book trade, but not for general retail sale as a whole. It carries multiple components for retailing as separate items, eg shrink-wrapped trade pack, filled dumpbin, filled counterpack",
        added_version=9,
    ),
    "31": CodeListEntry(
        list_number=2,
        code="31",
        heading="Multiple-item pack",
        notes="Carrying multiple components, primarily for retailing as separate items. The pack may be split and retailed as separate items OR retailed as a single item. Use instead of Multiple-item trade-only pack (code 30) if the data provider specifically wishes to make explicit that the pack may optionally be retailed as a whole",
        added_version=21,
    ),
}

List2 = CodeList(
    number=2,
    heading="Product composition",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
ProductComposition = List2
