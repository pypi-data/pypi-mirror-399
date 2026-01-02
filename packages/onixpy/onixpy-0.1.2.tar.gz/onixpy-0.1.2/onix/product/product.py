"""ONIX Product model.

The Product composite is the central element of an ONIX message,
containing all metadata for a single product.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from onix._base import ONIXModel
from onix.lists import List1, List5


class ProductIdentifier(ONIXModel):
    """Product identifier composite.

    Identifies a product using a standard or proprietary scheme.

    Required fields:
    - product_id_type: Code from List 5 indicating the identifier type
    - id_value: The identifier value

    Optional fields:
    - id_type_name: Name of proprietary identifier scheme (required if type is "01")

    Example:
        >>> from onix.product.product import ProductIdentifier
        >>> isbn = ProductIdentifier(
        ...     product_id_type="15",  # ISBN-13
        ...     id_value="9780007232833",
        ... )
    """

    product_id_type: str = Field(
        alias="ProductIDType",
        json_schema_extra={"short_tag": "b221"},
        max_length=2,
    )
    id_type_name: str | None = Field(
        default=None,
        alias="IDTypeName",
        json_schema_extra={"short_tag": "b233"},
        max_length=100,
    )
    id_value: str = Field(
        alias="IDValue",
        json_schema_extra={"short_tag": "b244"},
        max_length=300,
    )

    @field_validator("product_id_type")
    @classmethod
    def validate_product_id_type(cls, v: str) -> str:
        """Validate product_id_type is in List 5."""
        if v not in List5:
            raise ValueError(f"Invalid product_id_type '{v}': must be from List 5")
        return v


class ProductBase(ONIXModel):
    """ONIX product record base.

    Contains minimal required metadata for a product.
    Extended in product/__init__.py with block fields after imports.

    Required fields for a minimal valid Product:
    - record_reference: Unique identifier for this record
    - notification_type: Code from List 1 (e.g., "03" for confirmed)
    - product_identifiers: At least one ProductIdentifier

    ONIX 3.0 Product structure (blocks):
    - Block 1: Product description (identifiers, form, extent, etc.)
    - Block 2: DescriptiveDetail (titles, contributors, subjects)
    - Block 3: PublishingDetail (publisher, imprint, dates)
    - Block 4: RelatedMaterial (related products, works)
    - Block 5: ProductSupply (availability, pricing)
    - Block 6: MarketingDetail (promotional info)
    - Block 7: ProductionDetail (manufacturing info)

    Example:
        >>> from onix import Product
        >>> from onix.product.product import ProductIdentifier
        >>> product = Product(
        ...     record_reference="com.example.product.001",
        ...     notification_type="03",
        ...     product_identifiers=[
        ...         ProductIdentifier(
        ...             product_id_type="15",
        ...             id_value="9780000000001",
        ...         )
        ...     ],
        ... )
    """

    # Record metadata (gp.record_metadata)
    record_reference: str = Field(
        alias="RecordReference",
        json_schema_extra={"short_tag": "a001"},
        max_length=100,
    )
    notification_type: str = Field(
        alias="NotificationType",
        json_schema_extra={"short_tag": "a002"},
        max_length=2,
    )

    # Product identifiers (gp.product_numbers)
    product_identifiers: list[ProductIdentifier] = Field(
        alias="ProductIdentifier",
        json_schema_extra={"short_tag": "productidentifier"},
        min_length=1,
    )

    @field_validator("notification_type")
    @classmethod
    def validate_notification_type(cls, v: str) -> str:
        """Validate notification_type is in List 1."""
        if v not in List1:
            raise ValueError(f"Invalid notification_type '{v}': must be from List 1")
        return v
