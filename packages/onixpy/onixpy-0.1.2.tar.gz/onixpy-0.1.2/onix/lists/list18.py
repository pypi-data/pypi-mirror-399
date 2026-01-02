"""ONIX Code List 18: Person / organization name type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=18,
        code="00",
        heading="Unspecified",
        notes="Usually the name as it is presented on the book",
    ),
    "01": CodeListEntry(
        list_number=18,
        code="01",
        heading="Pseudonym",
        notes="May be used to give a well-known pseudonym, where the primary name is a ‘real’ name",
    ),
    "02": CodeListEntry(
        list_number=18,
        code="02",
        heading="Authority-controlled name",
    ),
    "03": CodeListEntry(
        list_number=18,
        code="03",
        heading="Earlier name",
        notes="Use only within <AlternativeName>",
        added_version=11,
    ),
    "04": CodeListEntry(
        list_number=18,
        code="04",
        heading="‘Real’ name",
        notes="May be used to identify a well-known ‘real’ name, where the primary name is a pseudonym or is unnamed",
        added_version=12,
    ),
    "05": CodeListEntry(
        list_number=18,
        code="05",
        heading="Transliterated / translated form of primary name",
        notes="Use only within <AlternativeName>, when the primary name type is unspecified, for names in a different script or language",
        added_version=16,
    ),
    "06": CodeListEntry(
        list_number=18,
        code="06",
        heading="Later name",
        notes="Use only within <AlternativeName>",
        added_version=33,
    ),
    "07": CodeListEntry(
        list_number=18,
        code="07",
        heading="Fictional character name",
        notes="Use only within <NameAsSubject> to indicate the subject is fictional, or in <AlternativeName> alongside <UnnamedPersons> to indicate a human-like name for a synthetic voice or AI. Only for use in ONIX 3.0 or later",
        added_version=49,
    ),
    "08": CodeListEntry(
        list_number=18,
        code="08",
        heading="Acronym / initialism",
        notes="Use only within <AlternativeName> with a corporate name to indicate the name is an acronym, initialism or short abbreviation for the full name. Only for use in ONIX 3.0 or later",
        added_version=68,
    ),
}

List18 = CodeList(
    number=18,
    heading="Person / organization name type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
PersonOrganizationNameType = List18
NameType = List18  # Shorter alias
