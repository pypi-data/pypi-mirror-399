"""ONIX Product Block 5: Related material.

Exports all Block 5 (Related material) composites.
"""

from onix.product.b5.p23 import RelatedMaterial, RelatedProduct

__all__ = [
    # P.23 Related products
    "RelatedMaterial",
    "RelatedProduct",
]
