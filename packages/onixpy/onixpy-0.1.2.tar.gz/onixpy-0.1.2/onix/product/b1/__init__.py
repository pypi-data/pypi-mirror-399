"""ONIX Product Block 1: Product description.

Exports all Block 1 (Product description) composites.
"""

from onix.product.b1.p3 import (
    DescriptiveDetail,
    EpubLicense,
    EpubLicenseDate,
    EpubLicenseExpression,
    EpubUsageConstraint,
    EpubUsageLimit,
    ProductClassification,
    ProductFormFeature,
)
from onix.product.b1.p5 import Collection
from onix.product.b1.p6 import TitleDetail, TitleElement
from onix.product.b1.p7 import (
    AffiliationIdentifier,
    AlternativeName,
    Contributor,
    ContributorDate,
    ContributorPlace,
    NameIdentifier,
    Prize,
    ProfessionalAffiliation,
    Website,
)
from onix.product.b1.p11 import Extent, Measure

__all__ = [
    # P.3 Product form composites
    "DescriptiveDetail",
    "ProductFormFeature",
    "EpubUsageLimit",
    "EpubUsageConstraint",
    "EpubLicenseDate",
    "EpubLicenseExpression",
    "EpubLicense",
    "ProductClassification",
    # P.5 Collection
    "Collection",
    # P.6 Product title detail
    "TitleDetail",
    "TitleElement",
    # P.7 Authorship
    "Contributor",
    "NameIdentifier",
    "AlternativeName",
    "ContributorDate",
    "ProfessionalAffiliation",
    "AffiliationIdentifier",
    "Prize",
    "Website",
    "ContributorPlace",
    # P.11 Extents and other content
    "Measure",
    "Extent",
]
