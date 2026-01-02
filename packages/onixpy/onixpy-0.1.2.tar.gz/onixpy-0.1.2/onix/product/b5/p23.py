"""ONIX Block 5, P.23: Related products.

RelatedMaterial composite with RelatedProduct.
Note: This currently contains all Block 5 composites. Will split P.22 (Related works)
when that section is implemented.
"""

from __future__ import annotations

from pydantic import Field

from onix._base import ONIXModel


class RelatedProduct(ONIXModel):
    """RelatedProduct composite.

    Identifies a related product and its relationship type.

    Elements:
    - RelationCode (B.031): Code from List 51 indicating relationship - required
    - ProductIdentifier (0…n): Identifiers of the related product
    - ProductForm (B.012): Product form code if not the same as main product
    """

    relation_code: str = Field(
        alias="RelationCode",
    )
    product_identifiers: list[dict] = Field(
        default_factory=list,
        alias="ProductIdentifier",
    )
    product_form: str | None = Field(
        default=None,
        alias="ProductForm",
    )


class RelatedMaterial(ONIXModel):
    """RelatedMaterial composite (Product Block 7).

    Contains information about materials related to the product including
    related products, websites, and other resources.

    Elements:
    - RelatedProduct (0…n): Related product information
    - RelatedWork (0…n): Related work information
    """

    related_products: list[RelatedProduct] = Field(
        default_factory=list,
        alias="RelatedProduct",
    )
