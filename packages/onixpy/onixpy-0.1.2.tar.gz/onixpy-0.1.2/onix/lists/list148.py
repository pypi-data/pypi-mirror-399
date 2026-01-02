"""ONIX Code List 148: Collection type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=148,
        code="00",
        heading="Unspecified (default)",
        notes="Collection type is not determined",
        added_version=9,
    ),
    "10": CodeListEntry(
        list_number=148,
        code="10",
        heading="Publisher collection",
        notes="The collection is a bibliographic collection (eg a series or set (Fr. série)) defined and identified by a publisher, either on the product itself or in product information supplied by the publisher. The books in the collection generally share a subject, narrative, design style or authorship. They may have a specific order, or the collection may be unordered",
        added_version=9,
    ),
    "11": CodeListEntry(
        list_number=148,
        code="11",
        heading="Collection éditoriale",
        notes="The collection is a bibliographic collection defined and identified by a publisher, either on the product itself or in product information supplied by the publisher, where the books in the collection have no specific order (other than order of publication), shared subject, narrative, style or shared authorship, and are grouped by the publisher largely for marketing purposes. The collection has many of the characteristics of an imprint or marque. Used primarily in French book publishing, to distinguish between ‘série’ (using the normal code 10) and ‘collection’ (code 11), and where the collection éditoriale is not an imprint",
        added_version=27,
    ),
    "20": CodeListEntry(
        list_number=148,
        code="20",
        heading="Ascribed collection",
        notes="The collection has been defined and identified by a party in the metadata supply chain other than the publisher, typically an aggregator",
        added_version=9,
    ),
}

List148 = CodeList(
    number=148,
    heading="Collection type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
CollectionType = List148
