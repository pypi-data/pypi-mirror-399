"""ONIX code list data models.

Provides dataclasses for representing ONIX code lists and their entries.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CodeListEntry:
    """A single entry in an ONIX code list.

    Attributes:
        list_number: The code list number (e.g., 44)
        code: The code value (e.g., "16")
        heading: Human-readable description (e.g., "ISNI")
        notes: Additional usage notes (optional)
        added_version: ONIX version when code was added (optional)
        modified_version: ONIX version when code was modified (optional)
        deprecated_version: ONIX version when code was deprecated (optional)
    """

    list_number: int
    code: str
    heading: str
    notes: str | None = None
    added_version: int | None = None
    modified_version: int | None = None
    deprecated_version: int | None = None

    @property
    def is_deprecated(self) -> bool:
        """Check if this code is deprecated."""
        return self.deprecated_version is not None


@dataclass
class CodeList:
    """An ONIX code list.

    Attributes:
        number: The list number (e.g., 44)
        heading: Human-readable name (e.g., "Name identifier type")
        scope_note: Usage information about which elements use this list
        entries: Dict mapping code values to CodeListEntry objects
    """

    number: int
    heading: str
    scope_note: str
    entries: dict[str, CodeListEntry]

    def get(self, code: str) -> CodeListEntry | None:
        """Get an entry by code value."""
        return self.entries.get(code)

    def __contains__(self, code: str) -> bool:
        """Check if a code exists in this list."""
        return code in self.entries

    def __iter__(self):
        """Iterate over entries."""
        return iter(self.entries.values())

    def __len__(self) -> int:
        """Number of entries in the list."""
        return len(self.entries)
