"""ONIX Product models.

The Product record is the core of an ONIX message, containing all metadata
for a single product (book, ebook, audiobook, etc.).

Product structure follows ONIX 3.0 blocks:
- Block 1: Product description (identifiers, form, extent, etc.)
- Block 2: Marketing collateral detail (descriptions, cover images)
- Block 3: Content detail (contributors, subjects, audience)
- Block 4: Publishing detail (publisher, imprint, dates)
- Block 5: Related material (related products, works)
- Block 6: Product supply (availability, pricing)
- Block 7: Promotion detail (promotional info)
- Block 8: Production detail (manufacturing info)

Example:
    >>> from onix import Product
    >>> from onix.product import Product, ProductIdentifier
    >>>
    >>> product = Product(
    ...     record_reference="com.example.001",
    ...     notification_type="03",
    ...     product_identifiers=[
    ...         ProductIdentifier(product_id_type="15", id_value="9780000000001")
    ...     ],
    ... )
"""

from pydantic import Field

from onix.product.b1 import (
    AffiliationIdentifier,
    AlternativeName,
    Collection,
    Contributor,
    ContributorDate,
    ContributorPlace,
    DescriptiveDetail,
    EpubLicense,
    EpubLicenseDate,
    EpubLicenseExpression,
    EpubUsageConstraint,
    EpubUsageLimit,
    Extent,
    Measure,
    NameIdentifier,
    Prize,
    ProductClassification,
    ProductFormFeature,
    ProfessionalAffiliation,
    TitleDetail,
    TitleElement,
    Website,
)
from onix.product.b4 import Publisher, PublishingDate, PublishingDetail
from onix.product.b5 import RelatedMaterial, RelatedProduct
from onix.product.product import ProductBase, ProductIdentifier


class Product(ProductBase):
    """ONIX Product with all block fields.

    Extends ProductBase with optional fields for each ONIX block.
    """

    # Block 1: DescriptiveDetail (Product form and content)
    descriptive_detail: DescriptiveDetail | None = Field(
        default=None,
        alias="DescriptiveDetail",
        json_schema_extra={"short_tag": "descriptivedetail"},
    )

    # Block 4: PublishingDetail (Publisher, imprint, dates)
    publishing_detail: PublishingDetail | None = Field(
        default=None,
        alias="PublishingDetail",
        json_schema_extra={"short_tag": "publishingdetail"},
    )

    # Block 5: RelatedMaterial (Related products, works)
    related_material: RelatedMaterial | None = Field(
        default=None,
        alias="RelatedMaterial",
        json_schema_extra={"short_tag": "relatedmaterial"},
    )


__all__ = [
    "Product",
    "ProductIdentifier",
    # Block 1 composites
    # P.3 Product form
    "DescriptiveDetail",
    "ProductFormFeature",
    "EpubUsageLimit",
    "EpubUsageConstraint",
    "EpubLicenseDate",
    "EpubLicenseExpression",
    "EpubLicense",
    "ProductClassification",
    # P.5 Collection
    "Collection",
    # P.6 Product title detail
    "TitleDetail",
    "TitleElement",
    # P.7 Authorship
    "Contributor",
    "NameIdentifier",
    "AlternativeName",
    "ContributorDate",
    "ProfessionalAffiliation",
    "AffiliationIdentifier",
    "Prize",
    "Website",
    "ContributorPlace",
    # P.11 Extents and other content
    "Measure",
    "Extent",
    # Block 4: PublishingDetail composites
    "PublishingDetail",
    "Publisher",
    "PublishingDate",
    # Block 5: RelatedMaterial composites
    "RelatedMaterial",
    "RelatedProduct",
]
