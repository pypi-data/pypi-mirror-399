"""ONIX Code List 15: Title type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=15,
        code="00",
        heading="Undefined",
    ),
    "01": CodeListEntry(
        list_number=15,
        code="01",
        heading="Distinctive title (book); Cover title (serial); Title of content item, collection, or resource",
        notes="The full text of the distinctive title of the item, without abbreviation or abridgement. For books, generally taken from the title page (see codes 11-15 where an alternative title is provided on cover or spine). Where the item is an omnibus edition containing two or more works by the same author, and there is no separate combined title, a distinctive title may be constructed (by the sender) by concatenating the individual titles, with suitable punctuation, as in ‘Pride and prejudice / Sense and sensibility / Northanger Abbey’. Where the title alone is not distinctive, recipients may add elements taken from a collection title and part number etc to create a distinctive title - but these elements should be provided separately by the sender",
    ),
    "02": CodeListEntry(
        list_number=15,
        code="02",
        heading="ISSN key title of serial",
        notes="Serials only",
    ),
    "03": CodeListEntry(
        list_number=15,
        code="03",
        heading="Title in original language",
        notes="Where the subject of the ONIX record is a translated item",
    ),
    "04": CodeListEntry(
        list_number=15,
        code="04",
        heading="Title acronym or initialism",
        notes="For serials: an acronym or initialism of Title Type 01, eg ‘JAMA’, ‘JACM’",
    ),
    "05": CodeListEntry(
        list_number=15,
        code="05",
        heading="Abbreviated title",
        notes="An abbreviated form of Title Type 01",
    ),
    "06": CodeListEntry(
        list_number=15,
        code="06",
        heading="Title in other language",
        notes="A translation of Title Type 01 or 03, or an independent title, used when the work is translated into another language, sometimes termed a ‘parallel title’",
    ),
    "07": CodeListEntry(
        list_number=15,
        code="07",
        heading="Thematic title of journal issue",
        notes="Serials only: when a journal issue is explicitly devoted to a specified topic",
    ),
    "08": CodeListEntry(
        list_number=15,
        code="08",
        heading="Former title",
        notes="Books or serials: when an item was previously published under another title",
    ),
    "10": CodeListEntry(
        list_number=15,
        code="10",
        heading="Distributor’s title",
        notes="For books: the title carried in a book distributor’s title file: frequently incomplete, and may include elements not properly part of the title. Usually limited in length and character set (eg to about 30 ASCII characters) for use on other e-commerce documentation",
        added_version=4,
    ),
    "11": CodeListEntry(
        list_number=15,
        code="11",
        heading="Alternative title on cover",
        notes="An alternative title that appears on the cover of a book",
        added_version=7,
    ),
    "12": CodeListEntry(
        list_number=15,
        code="12",
        heading="Alternative title on back",
        notes="An alternative title that appears on the back of a book",
        added_version=7,
    ),
    "13": CodeListEntry(
        list_number=15,
        code="13",
        heading="Expanded title",
        notes="An expanded form of the title, eg the title of a school text book with grade and type and other details added to make the title meaningful, where otherwise it would comprise only the curriculum subject. This title type is required for submissions to the Spanish ISBN Agency",
        added_version=7,
    ),
    "14": CodeListEntry(
        list_number=15,
        code="14",
        heading="Alternative title",
        notes="An alternative title that the book is widely known by, whether it appears on the book or not (including a title used in another market - but see code 06 for translations - or a working title previously used in metadata but replaced before publication)",
        added_version=25,
    ),
    "15": CodeListEntry(
        list_number=15,
        code="15",
        heading="Alternative title on spine",
        notes="An alternative title that appears on the spine of a book. Only for use in ONIX 3.0 or later",
        added_version=61,
    ),
    "16": CodeListEntry(
        list_number=15,
        code="16",
        heading="Translated from title",
        notes="Where the subject of the ONIX record is a translated item, but has been translated via some intermediate language. Title type 16 is distinct from title type 03. Only for use in ONIX 3.0 or later",
        added_version=66,
    ),
}

List15 = CodeList(
    number=15,
    heading="Title type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
TitleType = List15
