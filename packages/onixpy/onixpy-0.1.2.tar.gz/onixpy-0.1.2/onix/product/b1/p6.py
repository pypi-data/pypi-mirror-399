"""ONIX Block 1, P.6: Product title detail.

TitleDetail composite and TitleElement for representing product titles.
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from onix._base import ONIXModel
from onix.lists import get_code


class TitleElement(ONIXModel):
    """Title element component (part of TitleDetail).

    A group of data elements which together represent an element of a collection title.
    At least one title element is mandatory in each occurrence of the <TitleDetail> composite.

    An instance must include at least one of:
    - part_number
    - year_of_annual
    - title_text
    - no_prefix together with title_without_prefix
    - title_prefix together with title_without_prefix

    Required fields:
    - title_element_level: Code from List 149 indicating the level (product/collection/subcollection)

    Optional fields:
    - sequence_number: Overall sequence for display order (P.5.6a)
    - part_number: Part designation (e.g., "Volume 3") (P.5.8)
    - year_of_annual: Year for annuals (P.5.9)
    - title_text: Full title text without prefix (P.5.10)
    - title_prefix: Text at beginning to ignore for sorting (P.5.11)
    - no_prefix: Indicator that title has no prefix (P.5.11a)
    - title_without_prefix: Title text without prefix (P.5.12)
    - subtitle: Subtitle text (P.5.13)
    """

    sequence_number: str | None = Field(
        default=None,
        alias="SequenceNumber",
    )
    title_element_level: str = Field(
        alias="TitleElementLevel",
    )
    part_number: str | None = Field(
        default=None,
        alias="PartNumber",
    )
    year_of_annual: str | None = Field(
        default=None,
        alias="YearOfAnnual",
    )
    title_text: str | None = Field(
        default=None,
        alias="TitleText",
    )
    title_prefix: str | None = Field(
        default=None,
        alias="TitlePrefix",
    )
    no_prefix: bool = Field(
        default=False,
        alias="NoPrefix",
    )
    title_without_prefix: str | None = Field(
        default=None,
        alias="TitleWithoutPrefix",
    )
    subtitle: str | None = Field(
        default=None,
        alias="Subtitle",
    )

    @field_validator("title_element_level")
    @classmethod
    def validate_title_element_level(cls, v: str) -> str:
        """Validate title_element_level is a valid List 149 code."""
        if get_code(149, v) is None:
            raise ValueError(
                f"Invalid TitleElementLevel: '{v}' is not a valid List 149 code"
            )
        return v

    @model_validator(mode="after")
    def validate_title_element_requirements(self) -> "TitleElement":
        """Validate that at least one required field combination is present."""
        has_part_number = self.part_number is not None
        has_year = self.year_of_annual is not None
        has_title_text = self.title_text is not None
        has_prefix_combo = (
            self.title_prefix is not None and self.title_without_prefix is not None
        )
        has_no_prefix_combo = self.no_prefix and self.title_without_prefix is not None

        if not (
            has_part_number
            or has_year
            or has_title_text
            or has_prefix_combo
            or has_no_prefix_combo
        ):
            raise ValueError(
                "TitleElement must include at least one of: PartNumber, YearOfAnnual, "
                "TitleText, (NoPrefix with TitleWithoutPrefix), or "
                "(TitlePrefix with TitleWithoutPrefix)"
            )

        # Validate TitleText and prefix combinations are mutually exclusive
        if has_title_text and (self.title_prefix or self.no_prefix):
            raise ValueError(
                "TitleText cannot be used together with TitlePrefix or NoPrefix"
            )

        # Validate title_without_prefix requires either title_prefix or no_prefix
        if self.title_without_prefix and not (self.title_prefix or self.no_prefix):
            raise ValueError(
                "TitleWithoutPrefix can only be used with TitlePrefix or NoPrefix"
            )

        # Validate title_prefix and no_prefix are mutually exclusive
        if self.title_prefix and self.no_prefix:
            raise ValueError("TitlePrefix and NoPrefix cannot both be present")

        return self


class TitleDetail(ONIXModel):
    """Title detail composite (collection).

    A group of data elements which together give the text of a collection title
    and specify its type. Optional, but required unless the only collection title
    is carried in full as part of the product title.

    Required fields:
    - title_type: Code from List 15 indicating the type of title (P.5.6)
    - title_elements: At least one title element (1…n)

    The composite is repeatable with different title types.
    """

    title_type: str = Field(
        alias="TitleType",
    )
    title_elements: list[TitleElement] = Field(
        default_factory=list,
        alias="TitleElement",
    )

    @field_validator("title_type")
    @classmethod
    def validate_title_type(cls, v: str) -> str:
        """Validate title_type is a valid List 15 code."""
        if get_code(15, v) is None:
            raise ValueError(f"Invalid TitleType: '{v}' is not a valid List 15 code")
        return v

    @model_validator(mode="after")
    def validate_title_elements_required(self) -> "TitleDetail":
        """Ensure at least one title element is present."""
        if not self.title_elements:
            raise ValueError(
                "TitleDetail must include at least one TitleElement composite"
            )
        return self
