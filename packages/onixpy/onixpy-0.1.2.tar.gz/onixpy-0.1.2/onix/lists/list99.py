"""ONIX Code List 99: Special cover material."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=99,
        code="01",
        heading="Berkshire leather",
        notes="Pigskin",
        added_version=2,
    ),
    "02": CodeListEntry(
        list_number=99,
        code="02",
        heading="Calfskin",
        added_version=2,
    ),
    "03": CodeListEntry(
        list_number=99,
        code="03",
        heading="French Morocco",
        notes="Calf split or sheep split",
        added_version=2,
    ),
    "04": CodeListEntry(
        list_number=99,
        code="04",
        heading="Morocco",
        notes="Goatskin",
        added_version=2,
    ),
    "05": CodeListEntry(
        list_number=99,
        code="05",
        heading="Bonded buffalo grain",
        added_version=2,
    ),
    "06": CodeListEntry(
        list_number=99,
        code="06",
        heading="Bonded calf grain",
        added_version=2,
    ),
    "07": CodeListEntry(
        list_number=99,
        code="07",
        heading="Bonded Cordova",
        added_version=2,
    ),
    "08": CodeListEntry(
        list_number=99,
        code="08",
        heading="Bonded eelskin",
        added_version=2,
    ),
    "09": CodeListEntry(
        list_number=99,
        code="09",
        heading="Bonded Ostraleg",
        added_version=2,
    ),
    "10": CodeListEntry(
        list_number=99,
        code="10",
        heading="Bonded ostrich",
        added_version=2,
    ),
    "11": CodeListEntry(
        list_number=99,
        code="11",
        heading="Bonded reptile grain",
        added_version=2,
    ),
    "12": CodeListEntry(
        list_number=99,
        code="12",
        heading="Bonded leather",
        added_version=2,
    ),
    "13": CodeListEntry(
        list_number=99,
        code="13",
        heading="Cowhide",
        added_version=2,
    ),
    "14": CodeListEntry(
        list_number=99,
        code="14",
        heading="Eelskin",
        notes="Usually hagfish skin",
        added_version=2,
    ),
    "15": CodeListEntry(
        list_number=99,
        code="15",
        heading="Kivar",
        added_version=2,
    ),
    "16": CodeListEntry(
        list_number=99,
        code="16",
        heading="Leatherflex",
        notes="An imitation leather binding material",
        added_version=2,
    ),
    "17": CodeListEntry(
        list_number=99,
        code="17",
        heading="Moleskin",
        added_version=2,
    ),
    "18": CodeListEntry(
        list_number=99,
        code="18",
        heading="Softhide leather",
        added_version=2,
    ),
    "19": CodeListEntry(
        list_number=99,
        code="19",
        heading="Metal",
        added_version=2,
    ),
    "20": CodeListEntry(
        list_number=99,
        code="20",
        heading="Velvet",
        notes="(de: ‘Samt’)",
        added_version=6,
    ),
    "21": CodeListEntry(
        list_number=99,
        code="21",
        heading="Mother-of-pearl",
        notes="(es: ‘nácar’)",
        added_version=6,
    ),
    "22": CodeListEntry(
        list_number=99,
        code="22",
        heading="Papyrus",
        added_version=6,
    ),
    "23": CodeListEntry(
        list_number=99,
        code="23",
        heading="Géltex / Wibalin",
        notes="Proprietary imitation cloth binding material, cellulose-based, usually embossed / textured",
        added_version=6,
    ),
    "24": CodeListEntry(
        list_number=99,
        code="24",
        heading="Guaflex / Skivertex",
        notes="Proprietary imitation leather binding material, cellulose-based, usually embossed / textured",
        added_version=6,
    ),
    "25": CodeListEntry(
        list_number=99,
        code="25",
        heading="Imitation leather",
        notes="An imitation made of any non-leather material",
        added_version=28,
    ),
    "26": CodeListEntry(
        list_number=99,
        code="26",
        heading="Pigskin",
        added_version=28,
    ),
    "27": CodeListEntry(
        list_number=99,
        code="27",
        heading="Goatskin",
        added_version=28,
    ),
    "28": CodeListEntry(
        list_number=99,
        code="28",
        heading="Rubber",
        notes="Smooth or textured synthetic rubber. Only for use in ONIX 3.0 or later",
        added_version=70,
    ),
    "29": CodeListEntry(
        list_number=99,
        code="29",
        heading="Padded or quilted fabric",
        notes="Only for use in ONIX 3.0 or later",
        added_version=70,
    ),
}

List99 = CodeList(
    number=99,
    heading="Special cover material",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
SpecialCoverMaterial = List99
