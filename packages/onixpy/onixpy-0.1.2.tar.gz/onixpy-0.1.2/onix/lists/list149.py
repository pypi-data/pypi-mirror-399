"""ONIX Code List 149: Title element level."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=149,
        code="01",
        heading="Product",
        notes="The title element refers to an individual product",
        added_version=9,
    ),
    "02": CodeListEntry(
        list_number=149,
        code="02",
        heading="Collection level",
        notes="The title element refers to the top level of a bibliographic collection",
        added_version=9,
    ),
    "03": CodeListEntry(
        list_number=149,
        code="03",
        heading="Subcollection",
        notes="The title element refers to an intermediate level of a bibliographic collection that comprises two or more ‘sub-collections’",
        added_version=9,
    ),
    "04": CodeListEntry(
        list_number=149,
        code="04",
        heading="Content item",
        notes="The title element refers to a content item within a product, eg a work included in a combined or ‘omnibus’ edition, or a chapter in a book. Generally used only for titles within <ContentItem> (Block 3)",
        added_version=10,
    ),
    "05": CodeListEntry(
        list_number=149,
        code="05",
        heading="Master brand",
        notes="The title element names a multimedia franchise, licensed property or master brand where the use of the brand spans multiple collections and product forms, and possibly multiple imprints and publishers. It need not have a hierarchical relationship with title elements at other levels, or with other master brands. Used only for branded media properties carrying, for example, a children’s character brand or film franchise branding",
        added_version=19,
    ),
    "06": CodeListEntry(
        list_number=149,
        code="06",
        heading="Sub-subcollection",
        notes="The title element refers to an intermediate level of a bibliographic collection that is a subdivision of a sub-collection (a third level of collective identity)",
        added_version=27,
    ),
    "07": CodeListEntry(
        list_number=149,
        code="07",
        heading="Universe",
        notes="The title element names a ‘universe’, where parallel or intersecting narratives spanning multiple works and multiple characters occur in the same consistent fictional setting. It need not have a hierarchical relationship with title elements at other levels, in particular with master brands. Used primarily for comic books, but applicable to other fiction where appropriate",
        added_version=65,
    ),
}

List149 = CodeList(
    number=149,
    heading="Title element level",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
TitleElementLevel = List149
