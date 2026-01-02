"""ONIX Code List 9: Product classification type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=9,
        code="01",
        heading="WCO Harmonized System",
        notes="World Customs Organization Harmonized Commodity Coding and Description System, the basis of most other commodity code schemes. Use 6 digits, without punctuation. See https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition.aspx and https://www.wcotradetools.org/en/harmonized-system",
    ),
    "02": CodeListEntry(
        list_number=9,
        code="02",
        heading="UNSPSC",
        notes="UN Standard Product and Service Classification, including national versions adopted without any additions or changes to the codes or their meaning. Use 8 (or occasionally 10) digits, without punctuation",
    ),
    "03": CodeListEntry(
        list_number=9,
        code="03",
        heading="HMRC",
        notes="UK Revenue and Customs classifications, based on the Harmonized System (8 or 10 digits, without punctuation, for exports from and imports into the UK respectively). See https://www.gov.uk/trade-tariff",
        added_version=1,
    ),
    "04": CodeListEntry(
        list_number=9,
        code="04",
        heading="Warenverzeichnis für die Außenhandelsstatistik",
        notes="German export trade classification, based on the Harmonised System",
        added_version=5,
    ),
    "05": CodeListEntry(
        list_number=9,
        code="05",
        heading="TARIC",
        notes="EU TARIC codes, an extended version of the Harmonized System primarily for imports into the EU. Use 10 digits (very occasionally 11), without punctuation. See https://taxation-customs.ec.europa.eu/customs-4/calculation-customs-duties/customs-tariff/eu-customs-tariff-taric_en",
        added_version=5,
    ),
    "06": CodeListEntry(
        list_number=9,
        code="06",
        heading="Fondsgroep",
        notes="Centraal Boekhuis free classification field for publishers",
        added_version=8,
    ),
    "07": CodeListEntry(
        list_number=9,
        code="07",
        heading="Sender’s product category",
        notes="A product category (not a subject classification) assigned by the sender",
        added_version=10,
    ),
    "08": CodeListEntry(
        list_number=9,
        code="08",
        heading="GAPP Product Class",
        notes="Product classification maintained by the Chinese General Administration of Press and Publication (http://www.gapp.gov.cn)",
        added_version=15,
    ),
    "09": CodeListEntry(
        list_number=9,
        code="09",
        heading="CPA",
        notes="Statistical Classification of Products by Activity in the European Economic Community, see http://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=CPA_2008. Use 6 digits, without punctuation. For example, printed children’s books are ‘58.11.13’, but the periods are normally ommited in ONIX",
        added_version=16,
    ),
    "10": CodeListEntry(
        list_number=9,
        code="10",
        heading="NCM",
        notes="Mercosur/Mercosul Common Nomenclature, based on the Harmonised System. Use 8 digits, without punctuation",
        added_version=23,
    ),
    "11": CodeListEntry(
        list_number=9,
        code="11",
        heading="CPV",
        notes="Common Procurement Vocabulary (2008), used to describe products and services for public tendering and procurement within the EU. Code is a nine digit number (including the check digit), and may also include a space plus an alphanumeric code of two letters and three digits (including the supplementary check digit) from the Supplementary Vocabulary. See https://simap.ted.europa.eu/web/simap/cpv",
        added_version=33,
    ),
    "12": CodeListEntry(
        list_number=9,
        code="12",
        heading="PKWiU",
        notes="Polish Classification of Products and Services (2015). Use a single letter followed by 2 to 7 digits, without punctuation. Only for use in ONIX 3.0 or later",
        added_version=47,
    ),
    "13": CodeListEntry(
        list_number=9,
        code="13",
        heading="HTSUS",
        notes="US HTS (or HTSA) commodity codes for import of goods into USA (10 digits including the ‘statistical suffix’, and without punctuation). Only for use in ONIX 3.0 or later. See https://hts.usitc.gov/current",
        added_version=52,
    ),
    "14": CodeListEntry(
        list_number=9,
        code="14",
        heading="US Schedule B",
        notes="US Schedule B commodity codes for export from USA (10 digits, without punctuation). Only for use in ONIX 3.0 or later. See http://uscensus.prod.3ceonline.com",
        added_version=52,
    ),
    "15": CodeListEntry(
        list_number=9,
        code="15",
        heading="Clave SAT",
        notes="Mexican SAT classification, based on UN SPSC with later modifications (8 digits, without punctuation). Only for use in ONIX 3.0 or later. See https://www.sat.gob.mx/consultas/53693/catalogo-de-productos-y-servicios",
        added_version=58,
    ),
    "16": CodeListEntry(
        list_number=9,
        code="16",
        heading="CN (EU Combined Nomenclature)",
        notes="EU Combined Nomenclature commodity codes, an extended version of the Harmonized System primarily for exports from the EU. Use 8 digits, without punctuation. Only for use in ONIX 3.0 or later. See https://trade.ec.europa.eu/access-to-markets/en/content/combined-nomenclature-0",
        added_version=63,
    ),
    "17": CodeListEntry(
        list_number=9,
        code="17",
        heading="CCT",
        notes="Canadian Customs Tariff scheme, 8 or 10 digits for imports into and exports from Canada. Only for use in ONIX 3.0 or later. See https://www.cbsa-asfc.gc.ca/trade-commerce/tariff-tarif/menu-eng.html",
        added_version=64,
    ),
    "18": CodeListEntry(
        list_number=9,
        code="18",
        heading="CACT",
        notes="Australian ‘Working tariff’. Combined Australian Customs Tariff Nomenclature and Statistical Classification. Only for use in ONIX 3.0 or later. See https://www.abf.gov.au/importing-exporting-and-manufacturing/tariff-classification",
        added_version=64,
    ),
    "19": CodeListEntry(
        list_number=9,
        code="19",
        heading="NICO",
        notes="Mexican Número de Identificación Comercial, 10 digits for imports into and exports from Mexico. Only for use in ONIX 3.0 or later. See https://www.snice.gob.mx/cs/avi/snice/nico.ligie.html",
        added_version=64,
    ),
    "20": CodeListEntry(
        list_number=9,
        code="20",
        heading="TARIC additional code",
        notes="EU TARIC Document codes, 4 alphanumeric characters (usually 1 letter, 3 digits), eg Y129 (for goods outside the scope of EUDR). Only for use in ONIX 3.0 or later",
        added_version=70,
    ),
    "21": CodeListEntry(
        list_number=9,
        code="21",
        heading="HTSUS additional code",
        notes="HTSUS code for special classification provisions, or temporary legislation and restrictions, particularly from HTSUS chapters 98 and 99 (8 digits, or 10 where a statistical suffix is appropriate), and without punctuation). Only for use in ONIX 3.0 or later. See https://hts.usitc.gov/current",
        added_version=71,
    ),
    "22": CodeListEntry(
        list_number=9,
        code="22",
        heading="CPPAP",
        notes="Commission paritaire des publications et agences de presse, identifier used in France (mostly for serial publications). 10 characters (4 digits, one letter, then five digits). The initial four digits indicate the month and year of expiry of the CPPAP registration. Only for use in ONIX 3.0 or later",
        added_version=71,
    ),
    "50": CodeListEntry(
        list_number=9,
        code="50",
        heading="Electre genre",
        notes="Typologie de marché géré par Electre (Market segment code maintained by Electre)",
        added_version=24,
    ),
}

List9 = CodeList(
    number=9,
    heading="Product classification type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
ProductClassificationType = List9
