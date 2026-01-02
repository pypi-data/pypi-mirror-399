"""ONIX Block 1, P.3: Product form.

Group P.3 carries elements that describe the form of a product, its key content
type (text, audio, etc) and, in the case of digital products, any usage constraints
that are enforced through DRM protection or otherwise.

This module contains composites that describe product form:
- ProductFormFeature: Specific aspects of product form (color, material, etc)
- EpubUsageLimit: Quantitative limit on digital product usage
- EpubUsageConstraint: Usage constraints for digital products
- EpubLicenseDate: Date associated with a digital product license
- EpubLicenseExpression: Link to license terms
- EpubLicense: License governing use of a digital product
- ProductClassification: Trade classification (commodity codes)
- DescriptiveDetail: Container for P.3 product form elements

Simple elements like ProductComposition, ProductForm, TradeCategory, etc. are
fields in the DescriptiveDetail composite, not separate models.

Note: Measure composite is imported from p11.py where it's defined.
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from onix._base import ONIXModel
from onix.lists import get_code
from onix.product.b1.p11 import Measure  # Import Measure from p11


class ProductFormFeature(ONIXModel):
    """Product form feature composite.

    An optional group of data elements which together describe an aspect of
    product form that is too specific to be covered in the <ProductForm> and
    <ProductFormDetail> elements.

    Required fields:
    - product_form_feature_type: Code from List 79 specifying the feature type

    Optional fields:
    - product_form_feature_value: Controlled value (depends on feature type)
    - product_form_feature_description: Free text description (repeatable, with language)

    Example:
        >>> ProductFormFeature(
        ...     product_form_feature_type="02",  # Page edge color
        ...     product_form_feature_value="BLK",  # Black
        ... )
    """

    product_form_feature_type: str = Field(
        alias="ProductFormFeatureType",
        json_schema_extra={"short_tag": "b334"},
    )
    product_form_feature_value: str | None = Field(
        default=None,
        alias="ProductFormFeatureValue",
        json_schema_extra={"short_tag": "b335"},
    )
    product_form_feature_description: list[str] = Field(
        default_factory=list,
        alias="ProductFormFeatureDescription",
        max_length=10000,
        json_schema_extra={"short_tag": "b336"},
    )

    @field_validator("product_form_feature_type")
    @classmethod
    def _validate_product_form_feature_type(cls, v: str) -> str:
        """Validate product_form_feature_type: fixed length, two digits, List 79."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid product_form_feature_type '{v}' - must be exactly 2 digits"
            )
        if get_code(79, v) is None:
            raise ValueError(
                f"Invalid product_form_feature_type '{v}' - must be from List 79"
            )
        return v

    @field_validator("product_form_feature_description")
    @classmethod
    def _validate_product_form_feature_description(cls, v: list[str]) -> list[str]:
        """Validate product_form_feature_description: max 10,000 characters each."""
        for desc in v:
            if len(desc) > 10000:
                raise ValueError(
                    f"product_form_feature_description exceeds maximum length of 10,000 characters (got {len(desc)})"
                )
        return v


class EpubUsageLimit(ONIXModel):
    """Usage limit composite (digital products).

    An optional group of data elements which together specify a quantitative
    limit on a particular type of usage of a digital product.

    Required fields:
    - quantity: Maximum permitted quantity
    - epub_usage_unit: Code from List 147 indicating the unit

    Example:
        >>> EpubUsageLimit(
        ...     quantity="10",
        ...     epub_usage_unit="07",  # Maximum number of concurrent users
        ... )
    """

    quantity: str = Field(
        alias="Quantity",
        json_schema_extra={"short_tag": "x320"},
    )
    epub_usage_unit: str = Field(
        alias="EpubUsageUnit",
        json_schema_extra={"short_tag": "x321"},
    )

    @field_validator("epub_usage_unit")
    @classmethod
    def _validate_epub_usage_unit(cls, v: str) -> str:
        """Validate epub_usage_unit: fixed length, two digits, List 147."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid epub_usage_unit '{v}' - must be exactly 2 digits"
            )
        if get_code(147, v) is None:
            raise ValueError(f"Invalid epub_usage_unit '{v}' - must be from List 147")
        return v


class EpubUsageConstraint(ONIXModel):
    """Usage constraint composite (digital products).

    An optional group of data elements which together describe a usage constraint
    on a digital product (or the absence of such a constraint), whether enforced
    by DRM technical protection, inherent in the platform used, or specified by
    license agreement.

    Required fields:
    - epub_usage_type: Code from List 145 specifying the usage type
    - epub_usage_status: Code from List 146 specifying the status (permitted/prohibited)

    Optional fields:
    - epub_usage_limit: List of quantitative limits on usage

    Example:
        >>> EpubUsageConstraint(
        ...     epub_usage_type="05",  # Text-to-speech
        ...     epub_usage_status="03",  # Prohibited
        ... )
    """

    epub_usage_type: str = Field(
        alias="EpubUsageType",
        json_schema_extra={"short_tag": "x318"},
    )
    epub_usage_status: str = Field(
        alias="EpubUsageStatus",
        json_schema_extra={"short_tag": "x319"},
    )
    epub_usage_limit: list[EpubUsageLimit] = Field(
        default_factory=list,
        alias="EpubUsageLimit",
        json_schema_extra={"short_tag": "epubusagelimit"},
    )

    @field_validator("epub_usage_type")
    @classmethod
    def _validate_epub_usage_type(cls, v: str) -> str:
        """Validate epub_usage_type: fixed length, two digits, List 145."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid epub_usage_type '{v}' - must be exactly 2 digits"
            )
        if get_code(145, v) is None:
            raise ValueError(f"Invalid epub_usage_type '{v}' - must be from List 145")
        return v

    @field_validator("epub_usage_status")
    @classmethod
    def _validate_epub_usage_status(cls, v: str) -> str:
        """Validate epub_usage_status: fixed length, two digits, List 146."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid epub_usage_status '{v}' - must be exactly 2 digits"
            )
        if get_code(146, v) is None:
            raise ValueError(f"Invalid epub_usage_status '{v}' - must be from List 146")
        return v


class EpubLicenseDate(ONIXModel):
    """Digital product license date composite (new in 3.1).

    An optional group of date elements which together specify a date associated
    with the license in an occurrence of the <EpubLicense> composite.

    Required fields:
    - epub_license_date_role: Code from List 260 indicating the date significance
    - date: The date (YYYYMMDD format or with dateformat attribute)

    Example:
        >>> EpubLicenseDate(
        ...     epub_license_date_role="14",  # License becomes effective
        ...     date="20221028",
        ... )
    """

    epub_license_date_role: str = Field(
        alias="EpubLicenseDateRole",
        json_schema_extra={"short_tag": "x585"},
    )
    date: str = Field(
        alias="Date",
        json_schema_extra={"short_tag": "b306"},
    )

    @field_validator("epub_license_date_role")
    @classmethod
    def _validate_epub_license_date_role(cls, v: str) -> str:
        """Validate epub_license_date_role: fixed length, two digits, List 260."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid epub_license_date_role '{v}' - must be exactly 2 digits"
            )
        if get_code(260, v) is None:
            raise ValueError(
                f"Invalid epub_license_date_role '{v}' - must be from List 260"
            )
        return v


class EpubLicenseExpression(ONIXModel):
    """Digital product license expression composite (new in 3.0.2).

    An optional composite that carries details of a link to an expression of
    the license terms, which may be in human-readable or machine-readable form.

    Required fields:
    - epub_license_expression_type: Code from List 218 identifying the format
    - epub_license_expression_link: URI for the license expression

    Optional fields:
    - epub_license_expression_type_name: Name of proprietary encoding scheme

    Example:
        >>> EpubLicenseExpression(
        ...     epub_license_expression_type="10",  # ONIX-PL
        ...     epub_license_expression_link="http://example.com/license.xml",
        ... )
    """

    epub_license_expression_type: str = Field(
        alias="EpubLicenseExpressionType",
        json_schema_extra={"short_tag": "x508"},
    )
    epub_license_expression_type_name: str | None = Field(
        default=None,
        alias="EpubLicenseExpressionTypeName",
        max_length=50,
        json_schema_extra={"short_tag": "x509"},
    )
    epub_license_expression_link: str = Field(
        alias="EpubLicenseExpressionLink",
        max_length=300,
        json_schema_extra={"short_tag": "x510"},
    )

    @field_validator("epub_license_expression_type")
    @classmethod
    def _validate_epub_license_expression_type(cls, v: str) -> str:
        """Validate epub_license_expression_type: fixed length, two digits, List 218."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid epub_license_expression_type '{v}' - must be exactly 2 digits"
            )
        if get_code(218, v) is None:
            raise ValueError(
                f"Invalid epub_license_expression_type '{v}' - must be from List 218"
            )
        return v

    @model_validator(mode="after")
    def _validate_proprietary_type_name(self) -> "EpubLicenseExpression":
        """Ensure proprietary types have type name."""
        # List 218 code "01" is "Proprietary"
        if self.epub_license_expression_type == "01":
            if not self.epub_license_expression_type_name:
                raise ValueError(
                    "epub_license_expression_type_name is required when "
                    "epub_license_expression_type is '01' (Proprietary)"
                )
        return self


class EpubLicense(ONIXModel):
    """Digital product license composite (new in 3.0.2).

    An optional composite carrying the name or title of the license governing
    use of the product, a link to the license terms in eye-readable or
    machine-readable form, and optional dates when the license is valid.

    Required fields:
    - epub_license_name: Name/title of the license (repeatable for multiple languages)

    Optional fields:
    - epub_license_expression: List of links to license expressions
    - epub_license_date: List of dates associated with the license

    Example:
        >>> EpubLicense(
        ...     epub_license_name=["Elsevier e-book EULA v5"],
        ... )
    """

    epub_license_name: list[str] = Field(
        min_length=1,
        alias="EpubLicenseName",
        max_length=100,
        json_schema_extra={"short_tag": "x511"},
    )
    epub_license_expression: list[EpubLicenseExpression] = Field(
        default_factory=list,
        alias="EpubLicenseExpression",
        json_schema_extra={"short_tag": "epublicenseexpression"},
    )
    epub_license_date: list[EpubLicenseDate] = Field(
        default_factory=list,
        alias="EpubLicenseDate",
        json_schema_extra={"short_tag": "epublicensedate"},
    )

    @field_validator("epub_license_name")
    @classmethod
    def _validate_epub_license_name(cls, v: list[str]) -> list[str]:
        """Validate epub_license_name: max 100 characters each."""
        for name in v:
            if len(name) > 100:
                raise ValueError(
                    f"epub_license_name exceeds maximum length of 100 characters (got {len(name)})"
                )
        return v


class ProductClassification(ONIXModel):
    """Product classification composite.

    An optional group of data elements which together define a product classification
    (not to be confused with a subject classification). The intended use is to enable
    national or international trade classifications (commodity codes) to be carried
    in an ONIX record.

    Required fields:
    - product_classification_type: Code from List 9 identifying the scheme
    - product_classification_code: Classification code from the specified scheme

    Optional fields:
    - product_classification_type_name: Name of proprietary scheme
    - percent: Percentage of product value assignable to this classification

    Example:
        >>> ProductClassification(
        ...     product_classification_type="02",  # UNSPSC
        ...     product_classification_code="55101514",  # Sheet music
        ... )
    """

    product_classification_type: str = Field(
        alias="ProductClassificationType",
        json_schema_extra={"short_tag": "b274"},
    )
    product_classification_type_name: str | None = Field(
        default=None,
        alias="ProductClassificationTypeName",
        max_length=50,
        json_schema_extra={"short_tag": "x555"},
    )
    product_classification_code: str = Field(
        alias="ProductClassificationCode",
        json_schema_extra={"short_tag": "b275"},
    )
    percent: str | None = Field(
        default=None,
        alias="Percent",
        max_length=7,
        json_schema_extra={"short_tag": "b337"},
    )

    @field_validator("product_classification_type")
    @classmethod
    def _validate_product_classification_type(cls, v: str) -> str:
        """Validate product_classification_type: fixed length, two digits, List 9."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid product_classification_type '{v}' - must be exactly 2 digits"
            )
        if get_code(9, v) is None:
            raise ValueError(
                f"Invalid product_classification_type '{v}' - must be from List 9"
            )
        return v

    @field_validator("percent")
    @classmethod
    def _validate_percent(cls, v: str | None) -> str | None:
        """Validate percent: real number 0-100."""
        if v is not None:
            try:
                percent_val = float(v)
                if percent_val < 0 or percent_val > 100:
                    raise ValueError(
                        f"percent must be between 0 and 100 (got {percent_val})"
                    )
            except ValueError as e:
                if "could not convert" in str(e):
                    raise ValueError(f"percent must be a valid number (got '{v}')")
                raise
        return v

    @model_validator(mode="after")
    def _validate_proprietary_type_name(self) -> "ProductClassification":
        """Ensure proprietary types have type name."""
        # List 9 code "01" is "Proprietary"
        if self.product_classification_type == "01":
            if not self.product_classification_type_name:
                raise ValueError(
                    "product_classification_type_name is required when "
                    "product_classification_type is '01' (Proprietary)"
                )
        return self


class DescriptiveDetail(ONIXModel):
    """Descriptive detail composite.

    The descriptive detail block covers data Groups P.3 to P.13, all of which are
    essentially part of the factual description of the form and content of a product.
    The block as a whole is non-repeating. It is mandatory in any <Product> record
    unless the <NotificationType> in Group P.1 indicates that the record is an update
    notice which carries only those blocks in which changes have occurred.

    Required fields (P.3 Product form):
    - product_composition: Code from List 2 (single/multiple items)
    - product_form: Code from List 150 (primary form)

    Optional fields (P.3 Product form):
    - product_form_details: List of codes from List 175 (added detail)
    - product_form_features: List of ProductFormFeature composites
    - product_packaging: Code from List 80 (packaging type)
    - product_form_descriptions: List of text descriptions (with language)
    - trade_category: Code from List 12 (trade category)
    - primary_content_type: Code from List 81 (primary content type)
    - product_content_types: List of codes from List 81 (other content types)
    - measures: List of Measure composites (dimensions, weight, etc)
    - country_of_manufacture: Code from List 91 (ISO 3166-1 country code)
    - epub_technical_protections: List of codes from List 144 (DRM types)
    - epub_usage_constraints: List of EpubUsageConstraint composites
    - epub_licenses: List of EpubLicense composites
    - map_scales: List of map scale values
    - product_classifications: List of ProductClassification composites

    Example:
        >>> DescriptiveDetail(
        ...     product_composition="00",  # Single-item product
        ...     product_form="BB",  # Hardback book
        ...     product_form_details=["B206"],  # Pop-up book
        ...     measures=[
        ...         Measure(measure_type="01", measurement="8.25", measure_unit_code="in"),
        ...     ],
        ... )
    """

    # P.3.1 Product composition (mandatory)
    product_composition: str = Field(
        alias="ProductComposition",
        json_schema_extra={"short_tag": "x314"},
    )
    # P.3.2 Product form code (mandatory)
    product_form: str = Field(
        alias="ProductForm",
        json_schema_extra={"short_tag": "b012"},
    )
    # P.3.3 Product form detail (optional, repeatable)
    product_form_details: list[str] = Field(
        default_factory=list,
        alias="ProductFormDetail",
        json_schema_extra={"short_tag": "b333"},
    )
    # P.3.4-P.3.6 Product form feature composite (optional, repeatable)
    product_form_features: list[ProductFormFeature] = Field(
        default_factory=list,
        alias="ProductFormFeature",
        json_schema_extra={"short_tag": "productformfeature"},
    )
    # P.3.7 Product packaging type code (optional)
    product_packaging: str | None = Field(
        default=None,
        alias="ProductPackaging",
        json_schema_extra={"short_tag": "b225"},
    )
    # P.3.8 Product form description (optional, repeatable)
    product_form_descriptions: list[str] = Field(
        default_factory=list,
        alias="ProductFormDescription",
        max_length=200,
        json_schema_extra={"short_tag": "b014"},
    )
    # P.3.9 Trade category code (optional)
    trade_category: str | None = Field(
        default=None,
        alias="TradeCategory",
        json_schema_extra={"short_tag": "b384"},
    )
    # P.3.10 Primary content type code (optional)
    primary_content_type: str | None = Field(
        default=None,
        alias="PrimaryContentType",
        json_schema_extra={"short_tag": "x416"},
    )
    # P.3.11 Product content type code (optional, repeatable)
    product_content_types: list[str] = Field(
        default_factory=list,
        alias="ProductContentType",
        json_schema_extra={"short_tag": "b385"},
    )
    # P.3.12-P.3.14 Measure composite (optional, repeatable)
    measures: list[Measure] = Field(
        default_factory=list,
        alias="Measure",
        json_schema_extra={"short_tag": "measure"},
    )
    # P.3.15 Country of manufacture (optional)
    country_of_manufacture: str | None = Field(
        default=None,
        alias="CountryOfManufacture",
        json_schema_extra={"short_tag": "x316"},
    )
    # P.3.16 Digital product technical protection (optional, repeatable)
    epub_technical_protections: list[str] = Field(
        default_factory=list,
        alias="EpubTechnicalProtection",
        json_schema_extra={"short_tag": "x317"},
    )
    # P.3.17-P.3.20 Usage constraint composite (optional, repeatable)
    epub_usage_constraints: list[EpubUsageConstraint] = Field(
        default_factory=list,
        alias="EpubUsageConstraint",
        json_schema_extra={"short_tag": "epubusageconstraint"},
    )
    # P.3.20a-P.3.20f Digital product license composite (optional, repeatable)
    epub_licenses: list[EpubLicense] = Field(
        default_factory=list,
        alias="EpubLicense",
        json_schema_extra={"short_tag": "epublicense"},
    )
    # P.3.21 Map scale (optional, repeatable)
    map_scales: list[str] = Field(
        default_factory=list,
        alias="MapScale",
        max_length=8,
        json_schema_extra={"short_tag": "b063"},
    )
    # P.3.22-P.3.24 Product classification composite (optional, repeatable)
    product_classifications: list[ProductClassification] = Field(
        default_factory=list,
        alias="ProductClassification",
        json_schema_extra={"short_tag": "productclassification"},
    )

    @field_validator("product_composition")
    @classmethod
    def _validate_product_composition(cls, v: str) -> str:
        """Validate product_composition: fixed length, two digits, List 2."""
        if not v.isdigit() or len(v) != 2:
            raise ValueError(
                f"Invalid product_composition '{v}' - must be exactly 2 digits"
            )
        if get_code(2, v) is None:
            raise ValueError(f"Invalid product_composition '{v}' - must be from List 2")
        return v

    @field_validator("product_form")
    @classmethod
    def _validate_product_form(cls, v: str) -> str:
        """Validate product_form: fixed length, two letters or digits 00, List 150."""
        if len(v) != 2:
            raise ValueError(
                f"Invalid product_form '{v}' - must be exactly 2 characters"
            )
        if v != "00" and not (v.isalpha() and v.isupper()):
            raise ValueError(
                f"Invalid product_form '{v}' - must be two uppercase letters or '00'"
            )
        if get_code(150, v) is None:
            raise ValueError(f"Invalid product_form '{v}' - must be from List 150")
        return v

    @field_validator("product_form_details")
    @classmethod
    def _validate_product_form_details(cls, v: list[str]) -> list[str]:
        """Validate product_form_details: fixed length, one letter + three digits, List 175."""
        for code in v:
            if len(code) != 4 or not (code[0].isalpha() and code[1:].isdigit()):
                raise ValueError(
                    f"Invalid product_form_detail '{code}' - must be one letter followed by three digits"
                )
            if get_code(175, code) is None:
                raise ValueError(
                    f"Invalid product_form_detail '{code}' - must be from List 175"
                )
        return v

    @field_validator("product_form_descriptions")
    @classmethod
    def _validate_product_form_descriptions(cls, v: list[str]) -> list[str]:
        """Validate product_form_descriptions: max 200 characters each."""
        for desc in v:
            if len(desc) > 200:
                raise ValueError(
                    f"product_form_description exceeds maximum length of 200 characters (got {len(desc)})"
                )
        return v

    @field_validator("product_packaging")
    @classmethod
    def _validate_product_packaging(cls, v: str | None) -> str | None:
        """Validate product_packaging: fixed length, two digits, List 80."""
        if v is not None:
            if not v.isdigit() or len(v) != 2:
                raise ValueError(
                    f"Invalid product_packaging '{v}' - must be exactly 2 digits"
                )
            if get_code(80, v) is None:
                raise ValueError(
                    f"Invalid product_packaging '{v}' - must be from List 80"
                )
        return v

    @field_validator("trade_category")
    @classmethod
    def _validate_trade_category(cls, v: str | None) -> str | None:
        """Validate trade_category: fixed length, two digits, List 12."""
        if v is not None:
            if not v.isdigit() or len(v) != 2:
                raise ValueError(
                    f"Invalid trade_category '{v}' - must be exactly 2 digits"
                )
            if get_code(12, v) is None:
                raise ValueError(f"Invalid trade_category '{v}' - must be from List 12")
        return v

    @field_validator("primary_content_type")
    @classmethod
    def _validate_primary_content_type(cls, v: str | None) -> str | None:
        """Validate primary_content_type: fixed length, two digits, List 81."""
        if v is not None:
            if not v.isdigit() or len(v) != 2:
                raise ValueError(
                    f"Invalid primary_content_type '{v}' - must be exactly 2 digits"
                )
            if get_code(81, v) is None:
                raise ValueError(
                    f"Invalid primary_content_type '{v}' - must be from List 81"
                )
        return v

    @field_validator("product_content_types")
    @classmethod
    def _validate_product_content_types(cls, v: list[str]) -> list[str]:
        """Validate product_content_types: fixed length, two digits each, List 81."""
        for code in v:
            if not code.isdigit() or len(code) != 2:
                raise ValueError(
                    f"Invalid product_content_type '{code}' - must be exactly 2 digits"
                )
            if get_code(81, code) is None:
                raise ValueError(
                    f"Invalid product_content_type '{code}' - must be from List 81"
                )
        return v

    @field_validator("country_of_manufacture")
    @classmethod
    def _validate_country_of_manufacture(cls, v: str | None) -> str | None:
        """Validate country_of_manufacture: fixed length, two uppercase letters, List 91."""
        if v is not None:
            if len(v) != 2 or not (v.isalpha() and v.isupper()):
                raise ValueError(
                    f"Invalid country_of_manufacture '{v}' - must be exactly 2 uppercase letters"
                )
            if get_code(91, v) is None:
                raise ValueError(
                    f"Invalid country_of_manufacture '{v}' - must be from List 91"
                )
        return v

    @field_validator("epub_technical_protections")
    @classmethod
    def _validate_epub_technical_protections(cls, v: list[str]) -> list[str]:
        """Validate epub_technical_protections: fixed length, two digits each, List 144."""
        for code in v:
            if not code.isdigit() or len(code) != 2:
                raise ValueError(
                    f"Invalid epub_technical_protection '{code}' - must be exactly 2 digits"
                )
            if get_code(144, code) is None:
                raise ValueError(
                    f"Invalid epub_technical_protection '{code}' - must be from List 144"
                )
        return v

    @field_validator("map_scales")
    @classmethod
    def _validate_map_scales(cls, v: list[str]) -> list[str]:
        """Validate map_scales: positive integer, max 8 digits each."""
        for scale in v:
            if not scale.isdigit():
                raise ValueError(
                    f"Invalid map_scale '{scale}' - must be a positive integer"
                )
            if len(scale) > 8:
                raise ValueError(
                    f"map_scale exceeds maximum length of 8 digits (got {len(scale)})"
                )
        return v
