"""ONIX code lists.

Provides access to ONIX code lists used throughout the specification.
Code lists define allowed values for various fields (e.g., List 44 for
Name Identifier Type).

Import lists by number or name:
    >>> from onix.lists import List44
    >>> from onix.lists import NameIdentifierType  # Alias for List44

Access list data:
    >>> from onix.lists import get_list, get_code
    >>> list_44 = get_list(44)
    >>> code = get_code(44, "16")
    >>> code.heading
    'ISNI'

This is a placeholder implementation with minimal data. The full code lists
will be imported from the ONIX specification later.
"""

from __future__ import annotations

from onix.lists.list1 import List1, NotificationOrUpdateType
from onix.lists.list2 import List2, ProductComposition
from onix.lists.list5 import List5, ProductIdentifierType
from onix.lists.list9 import List9, ProductClassificationType
from onix.lists.list12 import List12, TradeCategory
from onix.lists.list15 import List15, TitleType
from onix.lists.list17 import ContributorRole, List17
from onix.lists.list18 import List18, NameType
from onix.lists.list19 import List19, UnnamedPersons
from onix.lists.list44 import List44, NameIdentifierType
from onix.lists.list45 import List45, PublishingRole
from onix.lists.list48 import List48, MeasureType
from onix.lists.list49 import List49, RegionCode
from onix.lists.list50 import List50, MeasureUnit
from onix.lists.list58 import List58, PriceType
from onix.lists.list73 import List73, WebsiteRole
from onix.lists.list74 import LanguageCode, List74
from onix.lists.list75 import ContributorDateRole, List75
from onix.lists.list79 import List79, ProductFormFeatureType
from onix.lists.list80 import List80, ProductPackagingType
from onix.lists.list81 import List81, ProductContentType
from onix.lists.list91 import CountryBasedOnIso31661, List91
from onix.lists.list96 import CurrencyCode, List96
from onix.lists.list98 import BindingOrPageEdgeColor, List98
from onix.lists.list99 import List99, SpecialCoverMaterial
from onix.lists.list144 import EpublicationTechnicalProtection, List144
from onix.lists.list145 import List145, UsageType
from onix.lists.list146 import List146, UsageStatus
from onix.lists.list147 import List147, UnitOfUsage
from onix.lists.list148 import CollectionType, List148
from onix.lists.list149 import List149, TitleElementLevel
from onix.lists.list150 import List150, ProductForm
from onix.lists.list151 import ContributorPlaceRelator, List151
from onix.lists.list175 import List175, ProductFormDetail
from onix.lists.list218 import LicenseExpressionType, List218
from onix.lists.list260 import EpublicationLicenseDateRole, List260
from onix.lists.models import CodeList, CodeListEntry

# Registry of all code lists (by number)
_CODE_LISTS: dict[int, CodeList] = {
    1: List1,
    2: List2,
    5: List5,
    9: List9,
    12: List12,
    15: List15,
    17: List17,
    18: List18,
    19: List19,
    44: List44,
    45: List45,
    48: List48,
    49: List49,
    50: List50,
    58: List58,
    73: List73,
    74: List74,
    75: List75,
    79: List79,
    80: List80,
    81: List81,
    91: List91,
    96: List96,
    98: List98,
    99: List99,
    144: List144,
    145: List145,
    146: List146,
    147: List147,
    148: List148,
    149: List149,
    150: List150,
    151: List151,
    175: List175,
    218: List218,
    260: List260,
}


def get_list(list_number: int) -> CodeList | None:
    """Get a code list by number.

    Args:
        list_number: The ONIX code list number (e.g., 44)

    Returns:
        The CodeList if found, None otherwise.

    Example:
        >>> list_44 = get_list(44)
        >>> list_44.heading
        'Name identifier type'
    """
    return _CODE_LISTS.get(list_number)


def get_code(list_number: int, code: str) -> CodeListEntry | None:
    """Get a specific code entry from a list.

    Args:
        list_number: The ONIX code list number (e.g., 44)
        code: The code value (e.g., "16")

    Returns:
        The CodeListEntry if found, None otherwise.

    Example:
        >>> entry = get_code(44, "16")
        >>> entry.heading
        'ISNI'
    """
    code_list = get_list(list_number)
    if code_list is None:
        return None
    return code_list.get(code)


def list_available() -> list[int]:
    """Get list of available code list numbers.

    Returns:
        Sorted list of available code list numbers.
    """
    return sorted(_CODE_LISTS.keys())


__all__ = [
    # Models
    "CodeList",
    "CodeListEntry",
    # Lists by number
    "List1",
    "List2",
    "List5",
    "List9",
    "List12",
    "List15",
    "List17",
    "List18",
    "List19",
    "List44",
    "List45",
    "List48",
    "List49",
    "List50",
    "List58",
    "List73",
    "List74",
    "List75",
    "List79",
    "List80",
    "List81",
    "List91",
    "List96",
    "List98",
    "List99",
    "List144",
    "List145",
    "List146",
    "List147",
    "List148",
    "List149",
    "List150",
    "List151",
    "List175",
    "List218",
    "List260",
    # Lists by name
    "NotificationOrUpdateType",
    "ProductComposition",
    "ProductIdentifierType",
    "ProductClassificationType",
    "TradeCategory",
    "TitleType",
    "ContributorRole",
    "NameType",
    "UnnamedPersons",
    "NameIdentifierType",
    "PublishingRole",
    "MeasureType",
    "RegionCode",
    "MeasureUnit",
    "PriceType",
    "WebsiteRole",
    "LanguageCode",
    "ContributorDateRole",
    "ProductFormFeatureType",
    "ProductPackagingType",
    "ProductContentType",
    "CountryBasedOnIso31661",
    "CurrencyCode",
    "BindingOrPageEdgeColor",
    "SpecialCoverMaterial",
    "EpublicationTechnicalProtection",
    "UsageType",
    "UsageStatus",
    "UnitOfUsage",
    "CollectionType",
    "TitleElementLevel",
    "ProductForm",
    "ContributorPlaceRelator",
    "ProductFormDetail",
    "LicenseExpressionType",
    "EpublicationLicenseDateRole",
    # Functions
    "get_list",
    "get_code",
    "list_available",
]
