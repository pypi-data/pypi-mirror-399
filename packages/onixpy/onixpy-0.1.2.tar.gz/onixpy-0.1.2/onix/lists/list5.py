"""ONIX Code List 5: Product identifier type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=5,
        code="01",
        heading="Proprietary product ID scheme",
        notes="For example, a publisher’s or wholesaler’s product number or SKU. Note that a distinctive <IDTypeName> is required with proprietary identifiers",
    ),
    "02": CodeListEntry(
        list_number=5,
        code="02",
        heading="ISBN-10",
        notes="International Standard Book Number, pre-2007 (10 digits, or 9 digits plus X, without spaces or hyphens) - now Deprecated in ONIX for Books, except where providing historical information for compatibility with legacy systems. It should only be used in relation to products published before 2007 - when ISBN-13 superseded it - and should never be used as the ONLY identifier (it should always be accompanied by the correct GTIN-13 / ISBN-13)",
        deprecated_version=11,
    ),
    "03": CodeListEntry(
        list_number=5,
        code="03",
        heading="GTIN-13",
        notes="GS1 Global Trade Item Number, formerly known as EAN article number (13 digits, without spaces or hyphens)",
    ),
    "04": CodeListEntry(
        list_number=5,
        code="04",
        heading="UPC",
        notes="UPC product number (12 digits, without spaces or hyphens)",
    ),
    "05": CodeListEntry(
        list_number=5,
        code="05",
        heading="ISMN-10",
        notes="International Standard Music Number, pre-2008 (M plus nine digits, without spaces or hyphens) - now Deprecated in ONIX for Books, except where providing historical information for compatibility with legacy systems. It should only be used in relation to products published before 2008 - when ISMN-13 superseded it - and should never be used as the ONLY identifier (it should always be accompanied by the correct GTIN-12 / ISMN-13)",
        deprecated_version=12,
    ),
    "06": CodeListEntry(
        list_number=5,
        code="06",
        heading="DOI",
        notes="Digital Object Identifier (variable length and character set, beginning ‘10.’ and without https://doi.org/ or the older http://dx.doi.org/)",
    ),
    "13": CodeListEntry(
        list_number=5,
        code="13",
        heading="LCCN",
        notes="Library of Congress Control Number in normalized form (up to 12 characters, alphanumeric)",
        added_version=1,
    ),
    "14": CodeListEntry(
        list_number=5,
        code="14",
        heading="GTIN-14",
        notes="GS1 Global Trade Item Number (14 digits, without spaces or hyphens)",
        added_version=1,
    ),
    "15": CodeListEntry(
        list_number=5,
        code="15",
        heading="ISBN-13",
        notes="International Standard Book Number, from 2007 (13 digits starting 978 or 9791-9799, without spaces or hyphens)",
        added_version=4,
    ),
    "17": CodeListEntry(
        list_number=5,
        code="17",
        heading="Legal deposit number",
        notes="The number assigned to a publication as part of a national legal deposit process",
        added_version=7,
    ),
    "22": CodeListEntry(
        list_number=5,
        code="22",
        heading="URN",
        notes="Uniform Resource Name: note that in trade applications an ISBN must be sent as a GTIN-13 and, where required, as an ISBN-13 - it should not be sent as a URN",
        added_version=8,
    ),
    "23": CodeListEntry(
        list_number=5,
        code="23",
        heading="OCLC number",
        notes="A unique number assigned to a bibliographic item by OCLC",
        added_version=9,
    ),
    "24": CodeListEntry(
        list_number=5,
        code="24",
        heading="Co-publisher’s ISBN-13",
        notes="An ISBN-13 assigned by a co-publisher. The ‘main’ ISBN sent with <ProductIDType> codes 03 and/or 15 should always be the ISBN that is used for ordering from the supplier identified in <SupplyDetail>. However, ISBN rules allow a co-published title to carry more than one ISBN. The co-publisher should be identified in an instance of the <Publisher> composite, with the applicable <PublishingRole> code",
        added_version=9,
    ),
    "25": CodeListEntry(
        list_number=5,
        code="25",
        heading="ISMN-13",
        notes="International Standard Music Number, from 2008 (13-digit number starting 9790, without spaces or hyphens)",
        added_version=12,
    ),
    "26": CodeListEntry(
        list_number=5,
        code="26",
        heading="ISBN-A",
        notes="Actionable ISBN, in fact a special DOI incorporating the ISBN-13 within the DOI syntax. Begins ‘10.978.’ or ‘10.979.’ and includes a / character between the registrant element (publisher prefix) and publication element of the ISBN, eg 10.978.000/1234567. Note the ISBN-A should always be accompanied by the ISBN itself, using <ProductIDType> codes 03 and/or 15",
        added_version=17,
    ),
    "27": CodeListEntry(
        list_number=5,
        code="27",
        heading="JP e-code",
        notes="E-publication identifier controlled by JPOIID’s Committee for Research and Management of Electronic Publishing Codes. 20 alphanumeric characters, without spaces, beginning with the ISBN ‘registrant element’",
        added_version=17,
    ),
    "28": CodeListEntry(
        list_number=5,
        code="28",
        heading="OLCC number",
        notes="Unique number assigned by the Chinese Online Library Cataloging Center (see http://olcc.nlc.gov.cn)",
        added_version=18,
    ),
    "29": CodeListEntry(
        list_number=5,
        code="29",
        heading="JP Magazine ID",
        notes="Japanese magazine identifier, similar in scope to ISSN but identifying a specific issue of a serial publication. Five digits to identify the periodical, plus a hyphen and two digits to identify the issue",
        added_version=21,
    ),
    "30": CodeListEntry(
        list_number=5,
        code="30",
        heading="UPC-12+5",
        notes="Used only with comic books and other products which use the UPC extension to identify individual issues or products. Do not use where the UPC-12 itself identifies the specific product, irrespective of any 5-digit extension - use code 04 instead",
        added_version=29,
    ),
    "31": CodeListEntry(
        list_number=5,
        code="31",
        heading="BNF Control number",
        notes="Numéro de la notice bibliographique BNF",
        added_version=31,
    ),
    "34": CodeListEntry(
        list_number=5,
        code="34",
        heading="ISSN-13",
        notes="International Standard Serial Number expressed as a GTIN-13, with optional 2- or 5-digit barcode extension (ie 13, 15 or 18 digits starting 977, without spaces or hyphens, with <BarcodeType> codes 02, 12 or 05), and only when the extended ISSN is used specifically as a product identifier (ie when the two publisher-defined ‘variant’ digits within the ISSN-13 itself and/or the 2- or 5-digit barcode extension are used to identify a single issue of a serial publication for separate sale). Only for use in ONIX 3.0 or later",
        added_version=66,
    ),
    "35": CodeListEntry(
        list_number=5,
        code="35",
        heading="ARK",
        notes="Archival Resource Key, as a URL (including the address of the ARK resolver provided by eg a national library)",
        added_version=36,
    ),
}

List5 = CodeList(
    number=5,
    heading="Product identifier type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
ProductIdentifierType = List5
