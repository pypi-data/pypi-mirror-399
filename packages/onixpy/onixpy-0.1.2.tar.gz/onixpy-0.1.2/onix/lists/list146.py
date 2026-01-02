"""ONIX Code List 146: Usage status."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=146,
        code="01",
        heading="Permitted unlimited",
        added_version=9,
    ),
    "02": CodeListEntry(
        list_number=146,
        code="02",
        heading="Permitted subject to limit",
        notes="Limit should be specified in <EpubUsageLimit> or <PriceConstraintLimit>",
        added_version=9,
    ),
    "03": CodeListEntry(
        list_number=146,
        code="03",
        heading="Prohibited",
        added_version=9,
    ),
}

List146 = CodeList(
    number=146,
    heading="Usage status",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
UsageStatus = List146
