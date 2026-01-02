"""ONIX Code List 151: Contributor place relator."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=151,
        code="00",
        heading="Associated with",
        notes="To express unknown relationship types (for use when expressing legacy ONIX 2.1 data in ONIX 3.0)",
        added_version=50,
    ),
    "01": CodeListEntry(
        list_number=151,
        code="01",
        heading="Born in",
        added_version=9,
    ),
    "02": CodeListEntry(
        list_number=151,
        code="02",
        heading="Died in",
        added_version=9,
    ),
    "03": CodeListEntry(
        list_number=151,
        code="03",
        heading="Formerly resided in",
        added_version=9,
    ),
    "04": CodeListEntry(
        list_number=151,
        code="04",
        heading="Currently resides in",
        added_version=9,
    ),
    "05": CodeListEntry(
        list_number=151,
        code="05",
        heading="Educated in",
        added_version=9,
    ),
    "06": CodeListEntry(
        list_number=151,
        code="06",
        heading="Worked in",
        added_version=9,
    ),
    "07": CodeListEntry(
        list_number=151,
        code="07",
        heading="Flourished in",
        notes="(‘Floruit’)",
        added_version=9,
    ),
    "08": CodeListEntry(
        list_number=151,
        code="08",
        heading="Citizen of",
        notes="Or nationality. For use with country codes only",
        added_version=20,
    ),
    "09": CodeListEntry(
        list_number=151,
        code="09",
        heading="Registered in",
        notes="The place of legal registration of an organization",
        added_version=46,
    ),
    "10": CodeListEntry(
        list_number=151,
        code="10",
        heading="Operating from",
        notes="The place an organization or part of an organization is based or operates from",
        added_version=46,
    ),
    "11": CodeListEntry(
        list_number=151,
        code="11",
        heading="Eligible for geographical marketing programs",
        notes="Contributor is eligible for national, regional or local marketing support. Use with country code, region code or country/region plus location, as appropriate",
        added_version=59,
    ),
    "12": CodeListEntry(
        list_number=151,
        code="12",
        heading="Indigenous to (Indigenous geographies or territorialities)",
        notes="Use to indicate that an Indigenous contributor has chosen to be publicly identified as an Indigenous person associated with a particular territory or geography. Used with <LocationName> (in addition to country or region) to indicate an Indigenous territoriality or geography",
        added_version=71,
    ),
}

List151 = CodeList(
    number=151,
    heading="Contributor place relator",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
ContributorPlaceRelator = List151
