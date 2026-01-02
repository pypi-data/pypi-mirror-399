"""ONIX Code List 218: License expression type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=218,
        code="01",
        heading="Human readable",
        notes="Document (eg Word file, PDF or web page) intended for the lay reader",
        added_version=24,
    ),
    "02": CodeListEntry(
        list_number=218,
        code="02",
        heading="Professional readable",
        notes="Document (eg Word file, PDF or web page) intended for the legal specialist reader",
        added_version=24,
    ),
    "03": CodeListEntry(
        list_number=218,
        code="03",
        heading="Human readable additional license",
        notes="Document (eg Word file, PDF or web page) intended for the lay reader, expressing an additional license that may be separately obtained covering uses of the content that are not granted by the intrinsic product license (the license expressed by code 01)",
        added_version=70,
    ),
    "04": CodeListEntry(
        list_number=218,
        code="04",
        heading="Professional readable additional license",
        notes="Document (eg Word file, PDF or web page) intended for the legal specialist reader, expressing an additional license that may be separately obtained covering uses of the content that are not granted by the intrinsic product license (the license expressed by code 02)",
        added_version=70,
    ),
    "10": CodeListEntry(
        list_number=218,
        code="10",
        heading="ONIX-PL",
        added_version=24,
    ),
    "20": CodeListEntry(
        list_number=218,
        code="20",
        heading="ODRL",
        notes="Open Digital Rights Language (ODRL) in JSON-LD format. Used for example to express TDM licenses using the W3C TDM Reservation Protocol",
        added_version=65,
    ),
    "21": CodeListEntry(
        list_number=218,
        code="21",
        heading="ODRL additional license",
        notes="Open Digital Rights Language (ODRL) in JSON-LD format. Used for example to express additional TDM licenses that may be separately obtained covering uses of the content that are not granted by the intrinsic product license (the license expressed by code 20), using the W3C TDM Reservation Protocol",
        added_version=70,
    ),
}

List218 = CodeList(
    number=218,
    heading="License expression type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
LicenseExpressionType = List218
