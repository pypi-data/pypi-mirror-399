"""ONIX Block 1, P.5: Collection.

Collection composite for grouping products into collections or series.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from onix._base import ONIXModel
from onix.lists import get_code


class Collection(ONIXModel):
    """Collection composite.

    Groups products into a collection or series.

    Required fields:
    - collection_type: Code from List 148

    Optional fields:
    - collection_sequence_number: Position in collection
    - collection_title: Name of the collection
    """

    collection_type: str = Field(
        alias="CollectionType",
    )
    collection_sequence_number: str | None = Field(
        default=None,
        alias="CollectionSequenceNumber",
    )
    collection_title: str | None = Field(
        default=None,
        alias="CollectionTitle",
    )

    @field_validator("collection_type")
    @classmethod
    def validate_collection_type(cls, v: str) -> str:
        """Validate collection_type is a valid List 148 code."""
        if get_code(148, v) is None:
            raise ValueError(
                f"Invalid CollectionType: '{v}' is not a valid List 148 code"
            )
        return v
