"""ONIX Code List 144: E-publication technical protection."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "00": CodeListEntry(
        list_number=144,
        code="00",
        heading="None",
        notes="Has no technical protection",
        added_version=9,
    ),
    "01": CodeListEntry(
        list_number=144,
        code="01",
        heading="DRM",
        notes="Has DRM protection",
        added_version=9,
    ),
    "02": CodeListEntry(
        list_number=144,
        code="02",
        heading="Digital watermarking",
        notes="Has digital watermarking",
        added_version=9,
    ),
    "03": CodeListEntry(
        list_number=144,
        code="03",
        heading="Adobe DRM",
        notes="Has DRM protection applied by the Adobe CS4 Content Server Package or by the Adobe ADEPT hosted service",
        added_version=10,
    ),
    "04": CodeListEntry(
        list_number=144,
        code="04",
        heading="Apple DRM",
        notes="Has FairPlay DRM protection applied via Apple proprietary online store",
        added_version=12,
    ),
    "05": CodeListEntry(
        list_number=144,
        code="05",
        heading="OMA DRM",
        notes="Has OMA v2 DRM protection applied, as used to protect some mobile phone content",
        added_version=12,
    ),
    "06": CodeListEntry(
        list_number=144,
        code="06",
        heading="Readium LCP DRM",
        notes="Has Licensed Content Protection DRM applied by a Readium License Server. See https://readium.org/lcp-specs/",
        added_version=34,
    ),
    "07": CodeListEntry(
        list_number=144,
        code="07",
        heading="Sony DRM",
        notes="Has Sony DADC User Rights Management (URMS) DRM protection applied",
        added_version=34,
    ),
}

List144 = CodeList(
    number=144,
    heading="E-publication technical protection",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
EpublicationTechnicalProtection = List144
