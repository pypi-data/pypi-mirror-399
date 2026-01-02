"""ONIX Code List 80: Product packaging type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=80,
        code="00",
        heading="No outer packaging",
        notes="No packaging, or all smaller items enclosed inside largest item",
        added_version=13,
    ),
    "01": CodeListEntry(
        list_number=80,
        code="01",
        heading="Slip-sleeve",
        notes="Thin card or soft plastic sleeve, much less rigid than a slip case",
        added_version=1,
    ),
    "02": CodeListEntry(
        list_number=80,
        code="02",
        heading="Clamshell",
        notes="Packaging consisting of formed plastic sealed around each side of the product. Not to be confused with single-sided Blister pack",
        added_version=1,
    ),
    "03": CodeListEntry(
        list_number=80,
        code="03",
        heading="Keep case",
        notes="Typical DVD-style packaging, sometimes known as an ‘Amaray’ case",
        added_version=1,
    ),
    "05": CodeListEntry(
        list_number=80,
        code="05",
        heading="Jewel case",
        notes="Typical CD-style packaging",
        added_version=1,
    ),
    "06": CodeListEntry(
        list_number=80,
        code="06",
        heading="Digipak",
        notes="Common CD-style packaging, a card folder with one or more panels incorporating a tray, hub or pocket to hold the disc(s)",
        added_version=21,
    ),
    "08": CodeListEntry(
        list_number=80,
        code="08",
        heading="Shrink-wrapped (biodegradable)",
        notes="Use for products or product bundles supplied for retail sale in shrink-wrapped packaging, where the shrink-wrap film is biodegradable. For non-degradable film, see code 21. Only for use in ONIX 3.0 or later",
        added_version=63,
    ),
    "09": CodeListEntry(
        list_number=80,
        code="09",
        heading="In box (with lid)",
        notes="Individual item, items or set in card box with separate or hinged lid: not to be confused with the commonly-used ‘boxed set’ which is more likely to be packaged in a slip case",
        added_version=2,
    ),
    "10": CodeListEntry(
        list_number=80,
        code="10",
        heading="Slip-cased",
        notes="Slip-case for single item only (de: ‘Schuber’)",
        added_version=2,
    ),
    "11": CodeListEntry(
        list_number=80,
        code="11",
        heading="Slip-cased set",
        notes="Slip-case for multi-volume set, also commonly referred to as ‘boxed set’ (de: ‘Kassette’)",
        added_version=2,
    ),
    "12": CodeListEntry(
        list_number=80,
        code="12",
        heading="Tube",
        notes="Rolled in tube or cylinder: eg sheet map or poster",
        added_version=2,
    ),
    "13": CodeListEntry(
        list_number=80,
        code="13",
        heading="Binder",
        notes="Use for miscellaneous items such as slides, microfiche, when presented in a binder",
        added_version=2,
    ),
    "14": CodeListEntry(
        list_number=80,
        code="14",
        heading="In wallet or folder",
        notes="Use for miscellaneous items such as slides, microfiche, when presented in a wallet or folder",
        added_version=2,
    ),
    "15": CodeListEntry(
        list_number=80,
        code="15",
        heading="Long triangular package",
        notes="Long package with triangular cross-section used for rolled sheet maps, posters etc",
        added_version=7,
    ),
    "16": CodeListEntry(
        list_number=80,
        code="16",
        heading="Long square package",
        notes="Long package with square cross-section used for rolled sheet maps, posters, etc",
        added_version=7,
    ),
    "17": CodeListEntry(
        list_number=80,
        code="17",
        heading="Softbox (for DVD)",
        added_version=8,
    ),
    "18": CodeListEntry(
        list_number=80,
        code="18",
        heading="Pouch",
        notes="In pouch, eg teaching materials in a plastic bag or pouch",
        added_version=8,
    ),
    "19": CodeListEntry(
        list_number=80,
        code="19",
        heading="Rigid plastic case",
        notes="In duroplastic or other rigid plastic case, eg for a class set",
        added_version=8,
    ),
    "20": CodeListEntry(
        list_number=80,
        code="20",
        heading="Cardboard case",
        notes="In cardboard case, eg for a class set",
        added_version=8,
    ),
    "21": CodeListEntry(
        list_number=80,
        code="21",
        heading="Shrink-wrapped",
        notes="Use for products or product bundles supplied for retail sale in shrink-wrapped packaging. For biodegradable shrink-wrap film, prefer code 08. For shrink-wrapped packs of multiple products for trade supply only, see code XL in List 7",
        added_version=8,
    ),
    "22": CodeListEntry(
        list_number=80,
        code="22",
        heading="Blister pack",
        notes="A pack comprising a pre-formed plastic blister and a printed card with a heat-seal coating",
        added_version=8,
    ),
    "23": CodeListEntry(
        list_number=80,
        code="23",
        heading="Carry case",
        notes="A case with carrying handle, typically for a set of educational books and/or learning materials",
        added_version=8,
    ),
    "24": CodeListEntry(
        list_number=80,
        code="24",
        heading="In tin",
        notes="Individual item, items or set in metal box or can with separate or hinged lid",
        added_version=34,
    ),
    "25": CodeListEntry(
        list_number=80,
        code="25",
        heading="With browse-prevention tape",
        notes="(ja: koguchi tome) Peelable sticker or tape sealing the foredge of a book to prevent pre-purchase reading of the content. Only for use in ONIX 3.0 or later",
        added_version=62,
    ),
}

List80 = CodeList(
    number=80,
    heading="Product packaging type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
ProductPackagingType = List80
