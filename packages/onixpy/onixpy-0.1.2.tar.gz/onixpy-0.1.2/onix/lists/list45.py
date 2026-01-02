"""ONIX Code List 45: Publishing role."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=45,
        code="01",
        heading="Publisher",
    ),
    "02": CodeListEntry(
        list_number=45,
        code="02",
        heading="Co-publisher",
        notes="Use where two or more publishers co-publish the exact same product, either under a single ISBN (in which case both publishers are co-publishers), or under different ISBNs (in which case the publisher of THIS ISBN is the publisher and the publishers of OTHER ISBNs are co-publishers. Note this is different from publication of ‘co-editions’",
    ),
    "03": CodeListEntry(
        list_number=45,
        code="03",
        heading="Sponsor",
    ),
    "04": CodeListEntry(
        list_number=45,
        code="04",
        heading="Publisher of original-language version",
        notes="Of a translated work",
    ),
    "05": CodeListEntry(
        list_number=45,
        code="05",
        heading="Host/distributor of electronic content",
    ),
    "06": CodeListEntry(
        list_number=45,
        code="06",
        heading="Published for/on behalf of",
        added_version=1,
    ),
    "07": CodeListEntry(
        list_number=45,
        code="07",
        heading="Published in association with",
        notes="Use also for ‘Published in cooperation with’",
        added_version=2,
    ),
    "09": CodeListEntry(
        list_number=45,
        code="09",
        heading="New or acquiring publisher",
        notes="When ownership of a product is transferred from one publisher to another",
        added_version=2,
    ),
    "10": CodeListEntry(
        list_number=45,
        code="10",
        heading="Publishing group",
        notes="The group to which a publisher (publishing role 01) belongs: use only if a publisher has been identified with role code 01",
        added_version=8,
    ),
    "11": CodeListEntry(
        list_number=45,
        code="11",
        heading="Publisher of facsimile original",
        notes="The publisher of the edition of which a product is a facsimile",
        added_version=9,
    ),
    "12": CodeListEntry(
        list_number=45,
        code="12",
        heading="Repackager of prebound edition",
        notes="The repackager of a prebound edition that has been assigned its own identifier. (In the US, a ‘prebound edition’ is a book that was previously bound, normally as a paperback, and has been rebound with a library-quality hardcover binding by a supplier other than the original publisher.) Required when the <EditionType> is coded PRB. The original publisher should be named as the ‘publisher’",
        added_version=9,
    ),
    "13": CodeListEntry(
        list_number=45,
        code="13",
        heading="Former publisher",
        notes="When ownership of a product is transferred from one publisher to another (complement of code 09)",
        added_version=12,
    ),
    "14": CodeListEntry(
        list_number=45,
        code="14",
        heading="Publication funder",
        notes="Body funding publication fees, if different from the body funding the underlying research. Intended primarily for use with open access publications",
        added_version=22,
    ),
    "15": CodeListEntry(
        list_number=45,
        code="15",
        heading="Research funder",
        notes="Body funding the research on which publication is based, if different from the body funding the publication. Intended primarily for use with open access publications",
        added_version=22,
    ),
    "16": CodeListEntry(
        list_number=45,
        code="16",
        heading="Funding body",
        notes="Body funding research and publication. Intended primarily for use with open access publications",
        added_version=22,
    ),
    "17": CodeListEntry(
        list_number=45,
        code="17",
        heading="Printer",
        notes="Organization responsible for printing a printed product. Supplied primarily to meet legal deposit requirements, and may apply only to the first impression. The organization may also be responsible for binding, when a separate binder is not specified",
        added_version=24,
    ),
    "18": CodeListEntry(
        list_number=45,
        code="18",
        heading="Binder",
        notes="Organization responsible for binding a printed product (where distinct from the printer). Supplied primarily to meet legal deposit requirements, and may apply only to the first impression",
        added_version=24,
    ),
    "19": CodeListEntry(
        list_number=45,
        code="19",
        heading="Manufacturer",
        notes="Organization primarily responsible for physical manufacture of a product, when neither Printer nor Binder is directly appropriate (for example, with disc or tape products, or digital products on a physical carrier)",
        added_version=29,
    ),
    "21": CodeListEntry(
        list_number=45,
        code="21",
        heading="Previous publisher",
        notes="Use for the publisher of earlier manifestations of the work. Only for use in ONIX 3.0 or later",
        added_version=69,
    ),
}

List45 = CodeList(
    number=45,
    heading="Publishing role",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
PublishingRole = List45
