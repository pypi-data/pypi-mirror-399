"""ONIX Code List 48: Measure type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=48,
        code="01",
        heading="Height",
        notes="For a book, the overall height when standing on a shelf. For a folded map, the height when folded. For packaged products, the height of the retail packaging, and for trade-only products, the height of the trade packaging. In general, the height of a product in the form in which it is presented or packaged for retail sale",
    ),
    "02": CodeListEntry(
        list_number=48,
        code="02",
        heading="Width",
        notes="For a book, the overall horizontal dimension of the cover when standing upright. For a folded map, the width when folded. For packaged products, the width of the retail packaging, and for trade-only products, the width of the trade packaging. In general, the width of a product in the form in which it is presented or packaged for retail sale",
    ),
    "03": CodeListEntry(
        list_number=48,
        code="03",
        heading="Thickness",
        notes="For a book, the overall thickness of the spine. For a folded map, the thickness when folded. For packaged products, the depth of the retail packaging, and for trade-only products, the depth of the trade packaging. In general, the thickness or depth of a product in the form in which it is presented or packaged for retail sale",
    ),
    "04": CodeListEntry(
        list_number=48,
        code="04",
        heading="Page trim height",
        notes="Overall height (code 01) is preferred for general use, as it includes the board overhang for hardbacks",
    ),
    "05": CodeListEntry(
        list_number=48,
        code="05",
        heading="Page trim width",
        notes="Overall width (code 02) is preferred for general use, as it includes the board overhang and spine thickness for hardbacks",
    ),
    "06": CodeListEntry(
        list_number=48,
        code="06",
        heading="Unit volume",
        notes="The volume of the product, including any retail packaging. Note the <MeasureUnit> is interpreted as a volumetric unit - for example code cm = cubic centimetres (ie millilitres), and code oz = (US) fluid ounces. Only for use in ONIX 3.0 or later",
        added_version=46,
    ),
    "07": CodeListEntry(
        list_number=48,
        code="07",
        heading="Unit capacity",
        notes="Volume of the internal (fluid) contents of a product (eg of paint in a can). Note the <MeasureUnit> is interpreted as a volumetric unit - for example code cm = cubic centimetres (ie millilitres), and code oz = (US) fluid ounces. Only for use in ONIX 3.0 or later",
        added_version=46,
    ),
    "08": CodeListEntry(
        list_number=48,
        code="08",
        heading="Unit weight",
        notes="The overall weight of the product, including any retail packaging",
    ),
    "09": CodeListEntry(
        list_number=48,
        code="09",
        heading="Diameter (sphere)",
        notes="Of a globe, for example",
        added_version=1,
    ),
    "10": CodeListEntry(
        list_number=48,
        code="10",
        heading="Unfolded/unrolled sheet height",
        notes="The height of a folded or rolled sheet map, poster etc when unfolded",
        added_version=7,
    ),
    "11": CodeListEntry(
        list_number=48,
        code="11",
        heading="Unfolded/unrolled sheet width",
        notes="The width of a folded or rolled sheet map, poster etc when unfolded",
        added_version=7,
    ),
    "12": CodeListEntry(
        list_number=48,
        code="12",
        heading="Diameter (tube or cylinder)",
        notes="The diameter of the cross-section of a tube or cylinder, usually carrying a rolled sheet product. Use 01 ‘Height’ for the height or length of the tube",
        added_version=7,
    ),
    "13": CodeListEntry(
        list_number=48,
        code="13",
        heading="Rolled sheet package side measure",
        notes="The length of a side of the cross-section of a long triangular or square package, usually carrying a rolled sheet product. Use 01 ‘Height’ for the height or length of the package",
        added_version=7,
    ),
    "14": CodeListEntry(
        list_number=48,
        code="14",
        heading="Unpackaged height",
        notes="As height, but of the product without packaging (use only for products supplied in retail packaging, must also supply overall size when packaged using code 01). Only for use in ONIX 3.0 or later",
        added_version=38,
    ),
    "15": CodeListEntry(
        list_number=48,
        code="15",
        heading="Unpackaged width",
        notes="As width, but of the product without packaging (use only for products supplied in retail packaging, must also supply overall size when packaged using code 02). Only for use in ONIX 3.0 or later",
        added_version=38,
    ),
    "16": CodeListEntry(
        list_number=48,
        code="16",
        heading="Unpackaged thickness",
        notes="As thickness, but of the product without packaging (use only for products supplied in retail packaging, must also supply overall size when packaged using code 03). Only for use in ONIX 3.0 or later",
        added_version=38,
    ),
    "17": CodeListEntry(
        list_number=48,
        code="17",
        heading="Total battery weight",
        notes="Weight of batteries built-in, pre-installed or supplied with the product. Details of the batteries should be provided using <ProductFormFeature>. A per-battery unit weight may be calculated from the number of batteries if required. Only for use in ONIX 3.0 or later",
        added_version=45,
    ),
    "18": CodeListEntry(
        list_number=48,
        code="18",
        heading="Total weight of Lithium",
        notes="Mass or equivalent mass of elemental Lithium within the batteries built-in, pre-installed or supplied with the product (eg a Lithium Iron phosphate battery with 160g of cathode material would have a total of around 7g of Lithium). Details of the batteries must be provided using <ProductFormFeature>. A per-battery unit mass of Lithium may be calculated from the number of batteries if required. Only for use in ONIX 3.0 or later",
        added_version=45,
    ),
    "19": CodeListEntry(
        list_number=48,
        code="19",
        heading="Assembled length",
        notes="For use where product or part of product requires assembly, for example the size of a completed kit, puzzle or assembled display piece. The assembled dimensions may be larger than the product size as supplied. Use only when the unassembled dimensions as supplied (including any retail or trade packaging) are also provided using codes 01, 02 and 03. Only for use in ONIX 3.0 or later",
        added_version=50,
    ),
    "20": CodeListEntry(
        list_number=48,
        code="20",
        heading="Assembled width",
        added_version=50,
    ),
    "21": CodeListEntry(
        list_number=48,
        code="21",
        heading="Assembled height",
        added_version=50,
    ),
    "22": CodeListEntry(
        list_number=48,
        code="22",
        heading="Unpackaged unit weight",
        notes="Overall unit weight (code 08) is preferred for general use, as it includes the weight of any packaging. Use Unpackaged unit weight only for products supplied in retail packaging, and must also supply overall unit weight. Only for use in ONIX 3.0 or later",
        added_version=61,
    ),
    "23": CodeListEntry(
        list_number=48,
        code="23",
        heading="Carton length",
        notes="Includes packaging. See <PackQuantity> for number of copies of the product per pack, and used only when dimensions of individual copies (codes 01, 02, 03) AND <PackQuantity> are supplied. Note that neither orders nor deliveries have to be aligned with multiples of the pack quantity, but such orders and deliveries may be more convenient to handle. Only for use in ONIX 3.0 or later",
        added_version=50,
    ),
    "24": CodeListEntry(
        list_number=48,
        code="24",
        heading="Carton width",
        added_version=50,
    ),
    "25": CodeListEntry(
        list_number=48,
        code="25",
        heading="Carton height",
        added_version=50,
    ),
    "26": CodeListEntry(
        list_number=48,
        code="26",
        heading="Carton weight",
        notes="Includes the weight of product(s) within the carton. See <PackQuantity> for number of copies per pack, and used only when the weight of individual copies (code 08) AND <PackQuantity> are supplied. Only for use in ONIX 3.0 or later",
        added_version=50,
    ),
    "27": CodeListEntry(
        list_number=48,
        code="27",
        heading="Pallet length",
        notes="Includes pallet and packaging. See <PalletQuantity> for number of copies of the product per pallet, and used only when dimensions of individual copies (codes 01, 02, 03) AND <PalletQuantity> are supplied. Note that neither orders nor deliveries have to be aligned with multiples of the pallet quantity, but such orders and deliveries may be more convenient to handle. Only for use in ONIX 3.0 or later",
        added_version=50,
    ),
    "28": CodeListEntry(
        list_number=48,
        code="28",
        heading="Pallet width",
        added_version=50,
    ),
    "29": CodeListEntry(
        list_number=48,
        code="29",
        heading="Pallet height",
        added_version=50,
    ),
    "30": CodeListEntry(
        list_number=48,
        code="30",
        heading="Pallet weight",
        notes="Includes the weight of product(s) and cartons stacked on the pallet. See <PalletQuantity> for the number of copies per pallet, and used only when the weight of individual copies (code 08) AND <PalletQuantity> are supplied. Only for use in ONIX 3.0 or later",
        added_version=50,
    ),
}

List48 = CodeList(
    number=48,
    heading="Measure type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
MeasureType = List48
