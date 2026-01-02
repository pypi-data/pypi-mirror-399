"""ONIX Code List 19: Unnamed person(s)."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=19,
        code="01",
        heading="Unknown",
    ),
    "02": CodeListEntry(
        list_number=19,
        code="02",
        heading="Anonymous",
        notes="Note that Anonymous can be interpreted as singular or plural. A real name can be provided using <AlternativeName> where it is generally known",
    ),
    "03": CodeListEntry(
        list_number=19,
        code="03",
        heading="et al",
        notes="And others. Use when some but not all contributors are listed individually, perhaps because the complete contributor list is impractically long",
    ),
    "04": CodeListEntry(
        list_number=19,
        code="04",
        heading="Various",
        notes="When there are multiple contributors, and none are listed individually. Use for example when the product is a pack of books by different authors",
        added_version=1,
    ),
    "05": CodeListEntry(
        list_number=19,
        code="05",
        heading="Synthesized voice - male",
        notes="Use for example with Contributor role code E07 ‘read by’ for audio books with digital narration having a male-inflected tone. ‘Brand name’ of voice may be provided in <AlternativeName>",
        added_version=8,
    ),
    "06": CodeListEntry(
        list_number=19,
        code="06",
        heading="Synthesized voice - female",
        notes="Use for example with Contributor role code E07 ‘read by’ for audio books with digital narration having a female-inflected tone. ‘Brand name’ of voice may be provided in <AlternativeName>",
        added_version=8,
    ),
    "07": CodeListEntry(
        list_number=19,
        code="07",
        heading="Synthesized voice - unspecified",
        notes="Use for example with Contributor role code E07 ‘read by’ for audio books with digital narration",
        added_version=8,
    ),
    "08": CodeListEntry(
        list_number=19,
        code="08",
        heading="Synthesized voice - based on real voice actor",
        notes="Sometimes termed an ‘Authorized Voice Replica’. Use for example with Contributor role code E07 ‘read by’ for audio books with digital narration, and provide name of voice actor in <AlternativeName>. Only for use in ONIX 3.0 or later",
        added_version=49,
    ),
    "09": CodeListEntry(
        list_number=19,
        code="09",
        heading="AI (Artificial intelligence)",
        notes="Use when the creator (of text, of images etc) is a generative AI model or technique. Note, can also be combined with the role ‘assisted by’. Only for use in ONIX 3.0 or later",
        added_version=62,
    ),
}

List19 = CodeList(
    number=19,
    heading="Unnamed person(s)",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
UnnamedPersonS = List19
UnnamedPersons = List19  # Alias (note: generator created with capital S)
