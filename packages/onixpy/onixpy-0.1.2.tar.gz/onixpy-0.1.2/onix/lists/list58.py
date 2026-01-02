"""ONIX Code List 58: Price type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=58,
        code="01",
        heading="RRP excluding tax",
        notes="Recommended Retail Price, excluding any sales tax or value-added tax. Price recommended by the publisher or supplier for retail sales to the consumer. Also termed the Suggested Retail Price (SRP) or Maximum Suggested Retail Price (MSRP) in some countries. The retailer may choose to use this recommended price, or may choose to sell to the consumer at a lower (or occasionally, a higher) price which is termed the Actual Selling Price (ASP) in sales reports. The net price charged to the retailer depends on the RRP minus a trade discount (which may be customer-specific). Relevant tax detail must be calculated by the data recipient",
    ),
    "02": CodeListEntry(
        list_number=58,
        code="02",
        heading="RRP including tax",
        notes="Recommended Retail Price, including sales or value-added tax where applicable. The net price charged to the retailer depends on the trade discount. Sales or value-added tax detail is usually supplied in the <Tax> composite",
    ),
    "03": CodeListEntry(
        list_number=58,
        code="03",
        heading="FRP excluding tax",
        notes="Fixed Retail Price, excluding any sales or value-added tax, used in countries where retail price maintenance applies (by law or via trade agreement) to certain products. Price fixed by the publisher or supplier for retail sales to the consumer. The retailer must use this price, or may vary the price only within certain legally-prescribed limits. The net price charged to the retailer depends on the FRP minus a customer-specific trade discount. Relevant tax detail must be calculated by the data recipient",
    ),
    "04": CodeListEntry(
        list_number=58,
        code="04",
        heading="FRP including tax",
        notes="Fixed Retail Price, including any sales or value-added tax where applicable, used in countries where retail price maintenance applies (by law or via trade agreement) to certain products. The net price charged to the retailer depends on the trade discount. Sales or value-added tax detail is usually supplied in the <Tax> composite",
    ),
    "05": CodeListEntry(
        list_number=58,
        code="05",
        heading="Supplier’s Net price excluding tax",
        notes="Net or wholesale price, excluding any sales or value-added tax. Unit price charged by supplier for business-to-business transactions, without any direct relationship to the price for retail sales to the consumer, but sometimes subject to a further customer-specific trade discount based on volume. Relevant tax detail must be calculated by the data recipient",
    ),
    "06": CodeListEntry(
        list_number=58,
        code="06",
        heading="Supplier’s Net price excluding tax: rental goods",
        notes="Unit price charged by supplier to reseller / rental outlet, excluding any sales tax or value-added tax: goods for rental (used for video and DVD)",
    ),
    "07": CodeListEntry(
        list_number=58,
        code="07",
        heading="Supplier’s Net price including tax",
        notes="Net or wholesale price, including any sales or value-added tax where applicable. Unit price charged by supplier for business-to-business transactions, without any direct relationship to the price for retail sales to the consumer, but sometimes subject to a further customer-specific trade discount based on volume. Sales or value-added tax detail is usually supplied in the <Tax> composite",
        added_version=8,
    ),
    "08": CodeListEntry(
        list_number=58,
        code="08",
        heading="Supplier’s alternative Net price excluding tax",
        notes="Net or wholesale price charged by supplier to a specified class of reseller, excluding any sales tax or value-added tax. Relevant tax detail must be calculated by the data recipient. (This value is for use only in countries, eg Finland, where trade practice requires two different Net prices to be listed for different classes of resellers, and where national guidelines specify how the code should be used)",
        added_version=8,
    ),
    "09": CodeListEntry(
        list_number=58,
        code="09",
        heading="Supplier’s alternative net price including tax",
        notes="Net or wholesale price charged by supplier to a specified class of reseller, including any sales tax or value-added tax. Sales or value-added tax detail is usually supplied in the <Tax> composite. (This value is for use only in countries, eg Finland, where trade practice requires two different Net prices to be listed for different classes of resellers, and where national guidelines specify how the code should be used)",
        added_version=8,
    ),
    "11": CodeListEntry(
        list_number=58,
        code="11",
        heading="Special sale RRP excluding tax",
        notes="Special sale RRP excluding any sales tax or value-added tax. Note ‘special sales’ are sales where terms and conditions are different from normal trade sales, when for example products that are normally sold on a sale-or-return basis are sold on firm-sale terms, where a particular product is tailored for a specific retail outlet (often termed a ‘premium’ product), or where other specific conditions or qualifications apply. Further details of the modified terms and conditions should be given in <PriceTypeDescription>",
    ),
    "12": CodeListEntry(
        list_number=58,
        code="12",
        heading="Special sale RRP including tax",
        notes="Special sale RRP including sales or value-added tax if applicable",
    ),
    "13": CodeListEntry(
        list_number=58,
        code="13",
        heading="Special sale fixed retail price excluding tax",
        notes="In countries where retail price maintenance applies by law to certain products: not used in USA",
    ),
    "14": CodeListEntry(
        list_number=58,
        code="14",
        heading="Special sale fixed retail price including tax",
        notes="In countries where retail price maintenance applies by law to certain products: not used in USA",
    ),
    "15": CodeListEntry(
        list_number=58,
        code="15",
        heading="Supplier’s net price for special sale excluding tax",
        notes="Unit price charged by supplier to reseller for special sale excluding any sales tax or value-added tax",
    ),
    "17": CodeListEntry(
        list_number=58,
        code="17",
        heading="Supplier’s net price for special sale including tax",
        notes="Unit price charged by supplier to reseller for special sale including any sales tax or value-added tax",
        added_version=15,
    ),
    "21": CodeListEntry(
        list_number=58,
        code="21",
        heading="Pre-publication RRP excluding tax",
        notes="Pre-publication RRP excluding any sales tax or value-added tax. Use where RRP for pre-orders is different from post-publication RRP",
    ),
    "22": CodeListEntry(
        list_number=58,
        code="22",
        heading="Pre-publication RRP including tax",
        notes="Pre-publication RRP including sales or value-added tax if applicable. Use where RRP for pre-orders is different from post-publication RRP",
    ),
    "23": CodeListEntry(
        list_number=58,
        code="23",
        heading="Pre-publication fixed retail price excluding tax",
        notes="In countries where retail price maintenance applies by law to certain products: not used in USA",
    ),
    "24": CodeListEntry(
        list_number=58,
        code="24",
        heading="Pre-publication fixed retail price including tax",
        notes="In countries where retail price maintenance applies by law to certain products: not used in USA",
    ),
    "25": CodeListEntry(
        list_number=58,
        code="25",
        heading="Supplier’s pre-publication net price excluding tax",
        notes="Unit price charged by supplier to reseller pre-publication excluding any sales tax or value-added tax",
    ),
    "27": CodeListEntry(
        list_number=58,
        code="27",
        heading="Supplier’s pre-publication net price including tax",
        notes="Unit price charged by supplier to reseller pre-publication including any sales tax or value-added tax",
        added_version=15,
    ),
    "31": CodeListEntry(
        list_number=58,
        code="31",
        heading="Freight-pass-through RRP excluding tax",
        notes="In the US, books are sometimes supplied on ‘freight-pass-through’ terms, where a price that is different from the RRP is used as the basis for calculating the supplier’s charge to a reseller. To make it clear when such terms are being invoked, code 31 is used instead of code 01 to indicate the RRP. Code 32 is used for the ‘billing price’",
        added_version=3,
    ),
    "32": CodeListEntry(
        list_number=58,
        code="32",
        heading="Freight-pass-through billing price excluding tax",
        notes="When freight-pass-through terms apply, the price on which the supplier’s charge to a reseller is calculated, ie the price to which trade discount terms are applied. See also code 31",
        added_version=3,
    ),
    "33": CodeListEntry(
        list_number=58,
        code="33",
        heading="Importer’s Fixed retail price excluding tax",
        notes="In countries where retail price maintenance applies by law to certain products, but the price is set by the importer or local sales agent, not the foreign publisher. In France, ‘prix catalogue éditeur étranger’",
        added_version=28,
    ),
    "34": CodeListEntry(
        list_number=58,
        code="34",
        heading="Importer’s Fixed retail price including tax",
        notes="In countries where retail price maintenance applies by law to certain products, but the price is set by the importer or local sales agent, not the foreign publisher. In France, ‘prix catalogue éditeur étranger’",
        added_version=28,
    ),
    "35": CodeListEntry(
        list_number=58,
        code="35",
        heading="Nominal gratis copy value for customs purposes, excluding tax",
        notes="Nominal value of gratis copies (eg review, sample or evaluation copies) for international customs declarations only, when a ‘free of charge’ price cannot be used. Only for use in ONIX 3.0 or later",
        added_version=57,
    ),
    "36": CodeListEntry(
        list_number=58,
        code="36",
        heading="Nominal value for claims purposes, excluding tax",
        notes="Nominal value of copies for claims purposes only (eg to account for copies lost during distribution). Only for use in ONIX 3.0 or later",
        added_version=59,
    ),
    "37": CodeListEntry(
        list_number=58,
        code="37",
        heading="Nominal value for customs purposes, excluding tax",
        notes="Nominal value of copies (Declared Unit Value) for international customs declarations only. Only for use in ONIX 3.0 or later",
        added_version=65,
    ),
    "41": CodeListEntry(
        list_number=58,
        code="41",
        heading="Publishers retail price excluding tax",
        notes="For a product supplied on agency terms, the retail price set by the publisher, excluding any sales tax or value-added tax",
        added_version=11,
    ),
    "42": CodeListEntry(
        list_number=58,
        code="42",
        heading="Publishers retail price including tax",
        notes="For a product supplied on agency terms, the retail price set by the publisher, including sales or value-added tax if applicable",
        added_version=11,
    ),
}

List58 = CodeList(
    number=58,
    heading="Price type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
PriceType = List58
