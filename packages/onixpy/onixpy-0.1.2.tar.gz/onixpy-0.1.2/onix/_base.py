"""Shared ONIX BaseModel with common pydantic configuration.

This central base enforces that constructors must use snake_case field
names (the `Field(alias=...)` values are preserved for XML
serialization). Models are configured to `validate_by_name=True` and
`validate_by_alias=False` so Python field names are used for validation
and typecheckers, and a `before` validator rejects alias (CamelCase)
keys to ensure callers don't pass XML tag names to constructors.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class ONIXModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_strings(cls, values):
        """Before-validation hook.

        Normalize empty-string inputs to None for string fields. Allow
        both snake_case field names and alias names to be passed to
        constructors; pydantic is configured to validate by alias.
        """
        if not isinstance(values, dict):
            return values

        return {k: (None if v == "" else v) for k, v in values.items()}
