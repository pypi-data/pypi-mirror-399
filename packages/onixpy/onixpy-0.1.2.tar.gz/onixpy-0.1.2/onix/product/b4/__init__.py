"""ONIX Product Block 4: Publishing detail.

Exports all Block 4 (Publishing detail) composites.
"""

from onix.product.b4.p19 import Publisher, PublishingDate, PublishingDetail

__all__ = [
    # P.19 Publisher (and related)
    "PublishingDetail",
    "Publisher",
    "PublishingDate",
]
