"""ONIX Code List 98: Binding or page edge color."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "BLK": CodeListEntry(
        list_number=98,
        code="BLK",
        heading="Black",
        added_version=1,
    ),
    "BLU": CodeListEntry(
        list_number=98,
        code="BLU",
        heading="Blue",
        added_version=1,
    ),
    "BRN": CodeListEntry(
        list_number=98,
        code="BRN",
        heading="Brown",
        added_version=1,
    ),
    "BUR": CodeListEntry(
        list_number=98,
        code="BUR",
        heading="Burgundy/Maroon",
        added_version=1,
    ),
    "CEL": CodeListEntry(
        list_number=98,
        code="CEL",
        heading="Celadon/Pale green",
        notes="Only for use in ONIX 3.0 or later",
        added_version=44,
    ),
    "CPR": CodeListEntry(
        list_number=98,
        code="CPR",
        heading="Copper",
        notes="Only for use in ONIX 3.0 or later",
        added_version=61,
    ),
    "CRE": CodeListEntry(
        list_number=98,
        code="CRE",
        heading="Cream",
        added_version=1,
    ),
    "FCO": CodeListEntry(
        list_number=98,
        code="FCO",
        heading="Four-color",
        notes="Use <ProductFormFeatureDescription> to add brief details if required",
        added_version=8,
    ),
    "FCS": CodeListEntry(
        list_number=98,
        code="FCS",
        heading="Four-color and spot-color",
        notes="Use <ProductFormFeatureDescription> to add brief details if required",
        added_version=8,
    ),
    "GLD": CodeListEntry(
        list_number=98,
        code="GLD",
        heading="Gold",
        added_version=1,
    ),
    "GRN": CodeListEntry(
        list_number=98,
        code="GRN",
        heading="Green",
        added_version=1,
    ),
    "GRY": CodeListEntry(
        list_number=98,
        code="GRY",
        heading="Grey",
        added_version=1,
    ),
    "HOL": CodeListEntry(
        list_number=98,
        code="HOL",
        heading="Holographic",
        notes="Generally semi-transparent or reflective silver, with holographic or ‘special effect patterning. Use <ProductFormFeatureDescription> to add brief details if required. Only for use in ONIX 3.0 or later",
        added_version=71,
    ),
    "MUL": CodeListEntry(
        list_number=98,
        code="MUL",
        heading="Multicolor",
        notes="Use <ProductFormFeatureDescription> to add brief details if required",
        added_version=1,
    ),
    "NAV": CodeListEntry(
        list_number=98,
        code="NAV",
        heading="Navy/Dark blue",
        added_version=1,
    ),
    "ORG": CodeListEntry(
        list_number=98,
        code="ORG",
        heading="Orange",
        added_version=6,
    ),
    "PNK": CodeListEntry(
        list_number=98,
        code="PNK",
        heading="Pink",
        added_version=1,
    ),
    "PUR": CodeListEntry(
        list_number=98,
        code="PUR",
        heading="Purple",
        added_version=1,
    ),
    "RED": CodeListEntry(
        list_number=98,
        code="RED",
        heading="Red",
        added_version=1,
    ),
    "SKY": CodeListEntry(
        list_number=98,
        code="SKY",
        heading="Sky/Pale blue",
        added_version=24,
    ),
    "SLV": CodeListEntry(
        list_number=98,
        code="SLV",
        heading="Silver",
        added_version=1,
    ),
    "TAN": CodeListEntry(
        list_number=98,
        code="TAN",
        heading="Tan/Light brown",
        added_version=1,
    ),
    "TEA": CodeListEntry(
        list_number=98,
        code="TEA",
        heading="Teal/Turquoise green",
        added_version=24,
    ),
    "WHI": CodeListEntry(
        list_number=98,
        code="WHI",
        heading="White",
        added_version=1,
    ),
    "YEL": CodeListEntry(
        list_number=98,
        code="YEL",
        heading="Yellow",
        added_version=1,
    ),
    "ZZZ": CodeListEntry(
        list_number=98,
        code="ZZZ",
        heading="Other",
        notes="Use <ProductFormFeatureDescription> to add brief details if required",
        added_version=1,
    ),
}

List98 = CodeList(
    number=98,
    heading="Binding or page edge color",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
BindingOrPageEdgeColor = List98
