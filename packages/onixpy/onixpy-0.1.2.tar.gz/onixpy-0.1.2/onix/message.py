"""ONIX message models.

Core Pydantic models representing an ONIX for Books message structure.
Models use reference tag names via Field(alias=...) which is the single
source of truth for XML tag/field name mapping.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from onix._base import ONIXModel
from onix.header import Header
from onix.product import Product


class ONIXAttributes(ONIXModel):
    """Shared ONIX attributes that may appear on any element.

    These attributes carry metadata about the data itself:
    - datestamp: Date/time the data was created or last updated
    - sourcename: Name of the source of the data
    - sourcetype: Code from List 3 indicating the type of source
    """

    datestamp: str | None = None
    sourcename: str | None = None
    sourcetype: str | None = None


class ONIXMessage(ONIXAttributes):
    """Root ONIX message container.

    An ONIX message contains:
    - A Header with sender/addressee information
    - Zero or more Product records
    - A NoProduct flag (automatically True when no products are included)

    The 'release' attribute indicates the ONIX version (e.g., "3.1").

    Note:
        The `products` list and `no_product` flag are mutually exclusive.
        When `products` is empty, `no_product` is automatically set to True.

    Example usage:
        >>> from onix import ONIXMessage, Header, Product
        >>> message = ONIXMessage(
        ...     release="3.1",
        ...     header=Header(),
        ...     products=[Product(), Product()],
        ... )
    """

    release: str = "3.1"
    header: Header = Field(
        alias="Header",
        json_schema_extra={"short_tag": "header"},
    )
    products: list[Product] = Field(
        default_factory=list,
        alias="Product",
        json_schema_extra={"short_tag": "product"},
    )
    no_product: bool = Field(
        default=False,
        alias="NoProduct",
        json_schema_extra={"short_tag": "x507"},
    )

    @model_validator(mode="after")
    def _validate_products_no_product(self) -> "ONIXMessage":
        """Ensure products and no_product are mutually exclusive."""
        if self.products and self.no_product:
            raise ValueError(
                "Cannot have both 'products' and 'no_product=True'. "
                "Either provide products or set no_product=True, not both."
            )
        if not self.products:
            self.no_product = True
        return self
