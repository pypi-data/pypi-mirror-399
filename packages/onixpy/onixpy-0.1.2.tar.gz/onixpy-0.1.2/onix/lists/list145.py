"""ONIX Code List 145: Usage type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=145,
        code="00",
        heading="No constraints",
        notes="Allows positive indication that there are no particular constraints (that can be specified in <EpubUsageConstraint>). By convention, use 01 in <EpubUsageStatus>",
        added_version=52,
    ),
    "01": CodeListEntry(
        list_number=145,
        code="01",
        heading="Preview",
        notes="Preview before purchase. Allows a retail customer, account holder or patron to view or listen to a proportion of the book before purchase. Also applies to borrowers making use of ‘acquisition on demand’ models in libraries, and to ‘subscription’ models where the purchase is made on behalf of the reader. Note that any Sales embargo date (in <PublishingDate> or <MarketDate>) also applies to provision of previews, unless an explicit date is provided for the preview",
        added_version=9,
    ),
    "02": CodeListEntry(
        list_number=145,
        code="02",
        heading="Print",
        notes="Make physical copy of extract",
        added_version=9,
    ),
    "03": CodeListEntry(
        list_number=145,
        code="03",
        heading="Copy / paste",
        notes="Make digital copy of extract",
        added_version=9,
    ),
    "04": CodeListEntry(
        list_number=145,
        code="04",
        heading="Share",
        notes="Share product across multiple concurrent devices. Allows a retail customer, account holder or patron to read the book across multiple devices linked to the same account. Also applies to readers in library borrowing and ‘subscription’ models",
        added_version=9,
    ),
    "05": CodeListEntry(
        list_number=145,
        code="05",
        heading="Text to speech",
        notes="‘Read aloud’ with text to speech functionality",
        added_version=9,
    ),
    "06": CodeListEntry(
        list_number=145,
        code="06",
        heading="Lend",
        notes="Lendable by the purchaser to another device owner or account holder or patron, eg ‘Lend-to-a-friend’, or library lending (where the library product has a separate <ProductIdentifier> from the consumer product - but for this prefer code 16). The ‘primary’ copy becomes unusable while the secondary copy is ‘lent’ unless a number of concurrent borrowers is also specified",
        added_version=12,
    ),
    "07": CodeListEntry(
        list_number=145,
        code="07",
        heading="Time-limited license",
        notes="E-publication license is time-limited. Use with code 02 from List 146 and either a time period in days, weeks or months in <EpubUsageLimit>, or a Valid until date in <EpubUsageLimit>. The purchased copy becomes unusable when the license expires. For clarity, a perpetual license is the default, but may be specified explicitly with code 01 from list 146, or with code 02 and a limit <Quantity> of 0 days",
        added_version=13,
    ),
    "08": CodeListEntry(
        list_number=145,
        code="08",
        heading="Library loan renewal",
        notes="Maximum number of consecutive loans or loan extensions (usually from a library) to a single device owner or account holder or patron. Note that a limit of 1 indicates that a loan cannot be renewed or extended",
        added_version=32,
    ),
    "09": CodeListEntry(
        list_number=145,
        code="09",
        heading="Multi-user license",
        notes="E-publication license is multi-user. Maximum number of concurrent users licensed to use the product should be given in <EpubUsageLimit>. For clarity, unlimited concurrency is the default, but may be specified explicitly with code 01 from list 146, or with code 02 and a limit <Quantity> of 0 users",
        added_version=36,
    ),
    "10": CodeListEntry(
        list_number=145,
        code="10",
        heading="Preview on premises",
        notes="Preview locally before purchase. Allows a retail customer, account holder or patron to view a proportion of the book (or the whole book, if no proportion is specified) before purchase, but ONLY while located physically in the retailer’s store (eg while logged on to the store or library wifi). Also applies to patrons making use of ‘acquisition on demand’ models in libraries",
        added_version=44,
    ),
    "11": CodeListEntry(
        list_number=145,
        code="11",
        heading="Text and data mining",
        notes="Make use of the content of the product (text, images, audio etc) or the product metadata or supporting resources for extraction of useful (and possibly new) information through automated computer analysis, or for training of tools for such analysis (including training of generative AI models). By convention, use 01 or 03 in <EpubUsageStatus>. Note 03 should be regarded as ‘prohibited to the full extent allowed by law’, or otherwise expressly reserved by the rightsholder, as in some jurisdictions, TDM may be subject to copyright exception (eg for not-for-profit purposes), subject to optional reservation, or allowed under ‘fair use’ doctrine",
        added_version=63,
    ),
    "16": CodeListEntry(
        list_number=145,
        code="16",
        heading="Library loan",
        notes="Loanable by the purchaser (usually a library) to other device owner or account holder or patron, eg library lending (whether or not the library product has a separate <ProductIdentifier> from the consumer product). The ‘primary’ copy becomes unusable while the secondary copy is ‘on loan’ unless a number of concurrent borrowers is also specified. Use code 08 to specify any limit on loan renewals",
        added_version=70,
    ),
}

List145 = CodeList(
    number=145,
    heading="Usage type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
UsageType = List145
