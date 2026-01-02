"""ONIX Code List 260: Epublication license date role."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "14": CodeListEntry(
        list_number=260,
        code="14",
        heading="Valid from",
        notes="Date on which a license becomes effective",
        added_version=60,
    ),
    "15": CodeListEntry(
        list_number=260,
        code="15",
        heading="Valid until",
        notes="Date on which a license ceases to be effective",
        added_version=60,
    ),
    "24": CodeListEntry(
        list_number=260,
        code="24",
        heading="From... until date",
        notes="Combines From date and Until date to define a period (both dates are inclusive). Use for example with dateformat 06",
        added_version=60,
    ),
}

List260 = CodeList(
    number=260,
    heading="Epublication license date role",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
EpublicationLicenseDateRole = List260
