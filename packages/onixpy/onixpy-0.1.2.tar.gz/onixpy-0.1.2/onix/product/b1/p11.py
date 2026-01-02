"""ONIX Block 1, P.11: Extents and other content.

Measure and Extent composites for product dimensions and extent information.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from onix._base import ONIXModel
from onix.lists import get_code


class Measure(ONIXModel):
    """Measure composite.

    Provides measurement information for the product (e.g., height, width, weight).

    Required fields:
    - measure_type: Code from List 48
    - measurement: Numeric measurement value
    - measure_unit_code: Unit of measurement from List 50
    """

    measure_type: str = Field(
        alias="MeasureType",
        json_schema_extra={"short_tag": "x315"},
    )
    measurement: str = Field(
        alias="Measurement",
        max_length=6,
        json_schema_extra={"short_tag": "c094"},
    )
    measure_unit_code: str = Field(
        alias="MeasureUnitCode",
        json_schema_extra={"short_tag": "c095"},
    )

    @field_validator("measure_type")
    @classmethod
    def validate_measure_type(cls, v: str) -> str:
        """Validate measure_type: fixed length, two digits, List 48."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(f"Invalid measure_type '{v}' - must be exactly 2 digits")
        if get_code(48, v) is None:
            raise ValueError(f"Invalid MeasureType: '{v}' is not a valid List 48 code")
        return v

    @field_validator("measurement")
    @classmethod
    def validate_measurement(cls, v: str) -> str:
        """Validate measurement: positive real number."""
        try:
            measurement_val = float(v)
            if measurement_val < 0:
                raise ValueError(
                    f"measurement must be positive (got {measurement_val})"
                )
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError(f"measurement must be a valid number (got '{v}')")
            raise
        return v

    @field_validator("measure_unit_code")
    @classmethod
    def validate_measure_unit_code(cls, v: str) -> str:
        """Validate measure_unit_code: fixed length, two letters, List 50."""
        if len(v) != 2 or not v.isalpha():
            raise ValueError(
                f"Invalid measure_unit_code '{v}' - must be exactly 2 letters"
            )
        if get_code(50, v) is None:
            raise ValueError(
                f"Invalid MeasureUnitCode: '{v}' is not a valid List 50 code"
            )
        return v


class Extent(ONIXModel):
    """Extent composite.

    Provides extent information (page count, duration, etc.).

    Required fields:
    - extent_type: Code from List 23
    - extent_value: Numeric extent value
    - extent_unit: Unit of extent
    """

    extent_type: str = Field(
        alias="ExtentType",
    )
    extent_value: str = Field(
        alias="ExtentValue",
    )
    extent_unit: str = Field(
        alias="ExtentUnit",
    )
