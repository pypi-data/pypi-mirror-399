"""ONIX Block 4, P.19: Publisher.

PublishingDetail composite with Publisher and PublishingDate.
Note: This currently contains all Block 4 composites. Will be split into
P.19, P.20, P.21 as those sections are implemented.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from onix._base import ONIXModel
from onix.lists import get_code


class Publisher(ONIXModel):
    """Publisher composite.

    Describes a publisher or imprint.

    Elements:
    - PublishingRole (B.045): Code from List 45 - required
    - PublisherName (B.082): Name of the publisher - required
    """

    publishing_role: str = Field(
        alias="PublishingRole",
    )
    publisher_name: str = Field(
        alias="PublisherName",
    )

    @field_validator("publishing_role")
    @classmethod
    def validate_publishing_role(cls, v: str) -> str:
        """Validate publishing_role is a valid List 45 code."""
        if get_code(45, v) is None:
            raise ValueError(
                f"Invalid PublishingRole: '{v}' is not a valid List 45 code"
            )
        return v


class PublishingDate(ONIXModel):
    """PublishingDate composite.

    Provides publication date information.

    Elements:
    - PublishingDateRole (B.306): Code from List 163 - required
    - Date (B.307): Date value - required
    """

    publishing_date_role: str = Field(
        alias="PublishingDateRole",
    )
    date: str = Field(
        alias="Date",
    )


class PublishingDetail(ONIXModel):
    """PublishingDetail composite (Product Block 3).

    Contains publishing information including publishers, imprints, and
    publication dates.

    Elements:
    - PublishingStatus (B.020): Code from List 64 indicating publication status
    - Publisher (0…n): Publisher(s) - at least one usually required
    - PublishingDate (0…n): Publication dates
    - CopyrightYear (B.087): Copyright year as YYYY
    """

    publishing_status: str | None = Field(
        default=None,
        alias="PublishingStatus",
    )
    publishers: list[Publisher] = Field(
        default_factory=list,
        alias="Publisher",
    )
    publishing_dates: list[PublishingDate] = Field(
        default_factory=list,
        alias="PublishingDate",
    )
    copyright_year: int | None = Field(
        default=None,
        alias="CopyrightYear",
    )
