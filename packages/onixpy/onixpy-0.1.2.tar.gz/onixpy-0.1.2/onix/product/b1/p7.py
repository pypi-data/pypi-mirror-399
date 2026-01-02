"""ONIX Block 1, P.7: Authorship.

Contributor composite and all nested composites:
- Contributor: Main authorship composite
- NameIdentifier: Person/organization identifiers
- AlternativeName: Pseudonyms, real names, authority-controlled forms
- ContributorDate: Birth/death dates
- ProfessionalAffiliation: Professional positions and affiliations
- AffiliationIdentifier: Organization identifiers
- Prize: Awards won by contributor
- Website: Contributor websites
- ContributorPlace: Geographical associations
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from onix._base import ONIXModel
from onix.lists import get_code

# =============================================================================
# Name Identifier Composite
# =============================================================================


class NameIdentifier(ONIXModel):
    """Name identifier composite.

    Identifies a person or organization using a standard or proprietary scheme.

    Required fields:
    - name_id_type: Code from List 44 identifying the scheme
    - id_value: The identifier value

    Optional fields:
    - id_type_name: Name of proprietary scheme (required if type is "01")
    """

    name_id_type: str = Field(
        alias="NameIDType",
    )
    id_type_name: str | None = Field(
        default=None,
        alias="IDTypeName",
    )
    id_value: str = Field(
        alias="IDValue",
    )

    @field_validator("name_id_type")
    @classmethod
    def validate_name_id_type(cls, v: str) -> str:
        """Validate name_id_type is a valid List 44 code."""
        if get_code(44, v) is None:
            raise ValueError(f"Invalid NameIDType: '{v}' is not a valid List 44 code")
        return v


# =============================================================================
# Alternative Name Composite
# =============================================================================


class AlternativeName(ONIXModel):
    """Alternative name composite.

    Represents an alternative name of a contributor (pseudonym, real name,
    authority-controlled form, etc.).

    Required fields:
    - name_type: Code from List 18 indicating the type of alternative name

    Optional fields:
    - name_identifiers: Name identifiers
    - person_name: Unstructured person name
    - person_name_inverted: Person name in inverted order
    - titles_before_names: Titles preceding names (e.g., 'Professor', 'HRH Prince')
    - names_before_key: Names/initials before key names
    - prefix_to_key: Prefix before key names (e.g., 'van')
    - key_names: Key name(s) for alphabetical sorting
    - names_after_key: Names following key names
    - suffix_to_key: Suffix after key names (e.g., 'Jr', 'III')
    - letters_after_names: Qualifications/honors (e.g., 'CBE FRS')
    - titles_after_names: Titles following names
    - corporate_name: Corporate contributor name (repeatable)
    - corporate_name_inverted: Corporate name in inverted order (repeatable)
    """

    name_type: str = Field(
        alias="NameType",
    )
    name_identifiers: list[NameIdentifier] = Field(
        default_factory=list,
        alias="NameIdentifier",
    )
    person_name: str | None = Field(
        default=None,
        alias="PersonName",
    )
    person_name_inverted: str | None = Field(
        default=None,
        alias="PersonNameInverted",
    )
    titles_before_names: str | None = Field(
        default=None,
        alias="TitlesBeforeNames",
    )
    names_before_key: str | None = Field(
        default=None,
        alias="NamesBeforeKey",
    )
    prefix_to_key: str | None = Field(
        default=None,
        alias="PrefixToKey",
    )
    key_names: str | None = Field(
        default=None,
        alias="KeyNames",
    )
    names_after_key: str | None = Field(
        default=None,
        alias="NamesAfterKey",
    )
    suffix_to_key: str | None = Field(
        default=None,
        alias="SuffixToKey",
    )
    letters_after_names: str | None = Field(
        default=None,
        alias="LettersAfterNames",
    )
    titles_after_names: str | None = Field(
        default=None,
        alias="TitlesAfterNames",
    )
    corporate_name: list[str] = Field(
        default_factory=list,
        alias="CorporateName",
    )
    corporate_name_inverted: list[str] = Field(
        default_factory=list,
        alias="CorporateNameInverted",
    )

    @field_validator("name_type")
    @classmethod
    def validate_name_type(cls, v: str) -> str:
        """Validate name_type is a valid List 18 code."""
        if get_code(18, v) is None:
            raise ValueError(f"Invalid NameType: '{v}' is not a valid List 18 code")
        return v


# =============================================================================
# Contributor Date Composite
# =============================================================================


class ContributorDate(ONIXModel):
    """Contributor date composite.

    Specifies a date associated with a contributor (e.g., birth, death).

    Required fields:
    - contributor_date_role: Code from List 75 indicating date significance
    - date: The date value

    The date field may carry a dateformat attribute; if missing, default is YYYYMMDD.
    """

    contributor_date_role: str = Field(
        alias="ContributorDateRole",
    )
    date: str = Field(
        alias="Date",
    )

    @field_validator("contributor_date_role")
    @classmethod
    def validate_contributor_date_role(cls, v: str) -> str:
        """Validate contributor_date_role is a valid List 75 code."""
        if get_code(75, v) is None:
            raise ValueError(
                f"Invalid ContributorDateRole: '{v}' is not a valid List 75 code"
            )
        return v


# =============================================================================
# Professional Affiliation Composite
# =============================================================================


class AffiliationIdentifier(ONIXModel):
    """Affiliation identifier composite (new in ONIX 3.1).

    Identifies an organization to which the contributor was affiliated.

    Required fields:
    - affiliation_id_type: Code from List 44 identifying the scheme
    - id_value: The identifier value

    Optional fields:
    - id_type_name: Name of proprietary scheme (required if type is "01")
    """

    affiliation_id_type: str = Field(
        alias="AffiliationIDType",
    )
    id_type_name: str | None = Field(
        default=None,
        alias="IDTypeName",
    )
    id_value: str = Field(
        alias="IDValue",
    )

    @field_validator("affiliation_id_type")
    @classmethod
    def validate_affiliation_id_type(cls, v: str) -> str:
        """Validate affiliation_id_type is a valid List 44 code."""
        if get_code(44, v) is None:
            raise ValueError(
                f"Invalid AffiliationIDType: '{v}' is not a valid List 44 code"
            )
        return v


class ProfessionalAffiliation(ONIXModel):
    """Professional affiliation composite.

    Identifies a contributor's professional position and/or affiliation.

    Optional fields:
    - professional_position: Position held (repeatable for multiple languages)
    - affiliation_identifiers: Organization identifiers (repeatable)
    - affiliation: Organization name
    """

    professional_position: list[str] = Field(
        default_factory=list,
        alias="ProfessionalPosition",
    )
    affiliation_identifiers: list[AffiliationIdentifier] = Field(
        default_factory=list,
        alias="AffiliationIdentifier",
    )
    affiliation: str | None = Field(
        default=None,
        alias="Affiliation",
    )


# =============================================================================
# Prize Composite
# =============================================================================


class Prize(ONIXModel):
    """Prize composite (new in ONIX 3.0.3).

    Describes a prize or award won by the contributor for a body of work.

    Note: Elements P.7.41a to P.7.41l are identical to P.17.1 to P.17.5
    as specified in Group P.17. This is a simplified placeholder until
    full prize elements are implemented.

    Optional fields:
    - prize_name: Name of the prize
    - prize_year: Year the prize was awarded
    - prize_country: Country of the prize
    """

    prize_name: str | None = Field(
        default=None,
        alias="PrizeName",
    )
    prize_year: str | None = Field(
        default=None,
        alias="PrizeYear",
    )
    prize_country: str | None = Field(
        default=None,
        alias="PrizeCountry",
    )


# =============================================================================
# Website Composite
# =============================================================================


class Website(ONIXModel):
    """Website composite.

    Identifies and provides a pointer to a website related to the contributor.

    Required fields:
    - website_link: URL for the website (repeatable for multiple languages)

    Optional fields:
    - website_role: Code from List 73 indicating purpose
    - website_description: Free text description (repeatable)
    """

    website_role: str | None = Field(
        default=None,
        alias="WebsiteRole",
    )
    website_description: list[str] = Field(
        default_factory=list,
        alias="WebsiteDescription",
    )
    website_link: list[str] = Field(
        default_factory=list,
        alias="WebsiteLink",
    )

    @field_validator("website_role")
    @classmethod
    def validate_website_role(cls, v: str | None) -> str | None:
        """Validate website_role is a valid List 73 code."""
        if v is not None and get_code(73, v) is None:
            raise ValueError(f"Invalid WebsiteRole: '{v}' is not a valid List 73 code")
        return v

    @model_validator(mode="after")
    def validate_website_link_required(self) -> "Website":
        """Ensure at least one website_link is provided."""
        if not self.website_link:
            raise ValueError("Website composite requires at least one WebsiteLink")
        return self


# =============================================================================
# Contributor Place Composite
# =============================================================================


class ContributorPlace(ONIXModel):
    """Contributor place composite.

    Identifies a geographical location associated with a contributor.

    Required fields:
    - contributor_place_relator: Code from List 151 indicating relationship

    At least one of country_code or region_code must be provided.

    Optional fields:
    - country_code: ISO 3166-1 country code (List 91)
    - region_code: Region code (List 49)
    - location_name: City or town name (repeatable for multiple languages)
    """

    contributor_place_relator: str = Field(
        alias="ContributorPlaceRelator",
    )
    country_code: str | None = Field(
        default=None,
        alias="CountryCode",
    )
    region_code: str | None = Field(
        default=None,
        alias="RegionCode",
    )
    location_name: list[str] = Field(
        default_factory=list,
        alias="LocationName",
    )

    @field_validator("contributor_place_relator")
    @classmethod
    def validate_contributor_place_relator(cls, v: str) -> str:
        """Validate contributor_place_relator is a valid List 151 code."""
        if get_code(151, v) is None:
            raise ValueError(
                f"Invalid ContributorPlaceRelator: '{v}' is not a valid List 151 code"
            )
        return v

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Validate country_code is a valid List 91 code."""
        if v is not None and get_code(91, v) is None:
            raise ValueError(f"Invalid CountryCode: '{v}' is not a valid List 91 code")
        return v

    @field_validator("region_code")
    @classmethod
    def validate_region_code(cls, v: str | None) -> str | None:
        """Validate region_code is a valid List 49 code."""
        if v is not None and get_code(49, v) is None:
            raise ValueError(f"Invalid RegionCode: '{v}' is not a valid List 49 code")
        return v

    @model_validator(mode="after")
    def validate_location_specified(self) -> "ContributorPlace":
        """Ensure either country_code or region_code is provided."""
        if not self.country_code and not self.region_code:
            raise ValueError(
                "ContributorPlace requires either CountryCode or RegionCode"
            )
        return self


# =============================================================================
# Contributor Composite
# =============================================================================


class Contributor(ONIXModel):
    """Contributor composite.

    Describes a personal or corporate contributor to the product.

    Required fields:
    - contributor_role: Code(s) from List 17 (repeatable, min 1)

    At least one name representation must be provided:
    - person_name, person_name_inverted, structured name parts, or
    - corporate_name, corporate_name_inverted, or
    - name_identifiers, or
    - unnamed_persons

    Optional fields:
    - sequence_number: Overall sequence of contributor names
    - from_language: Source language for translators (List 74, repeatable)
    - to_language: Target language for translators (List 74, repeatable)
    - name_type: Type of primary name (List 18)
    - name_identifiers: Name identifiers (repeatable)
    - person_name: Unstructured person name
    - person_name_inverted: Person name in inverted order
    - titles_before_names: Titles preceding names
    - names_before_key: Names/initials before key names
    - prefix_to_key: Prefix before key names
    - key_names: Key name(s) for alphabetical sorting
    - names_after_key: Names following key names
    - suffix_to_key: Suffix after key names
    - letters_after_names: Qualifications/honors
    - titles_after_names: Titles following names
    - corporate_name: Corporate contributor name (repeatable)
    - corporate_name_inverted: Corporate name in inverted order (repeatable)
    - unnamed_persons: Code from List 19 for unknown/anonymous authorship
    - alternative_names: Alternative names (repeatable)
    - contributor_dates: Dates associated with contributor (repeatable)
    - professional_affiliations: Professional positions (repeatable)
    - prizes: Prizes/awards (repeatable)
    - biographical_note: Biographical information (repeatable)
    - websites: Related websites (repeatable)
    - contributor_description: Brief description (repeatable)
    - contributor_places: Geographical associations (repeatable)
    """

    # P.7.1 Sequence number
    sequence_number: str | None = Field(
        default=None,
        alias="SequenceNumber",
    )

    # P.7.2 Contributor role (mandatory, repeatable)
    contributor_role: list[str] = Field(
        alias="ContributorRole",
        min_length=1,
    )

    # P.7.3 From language (for translators)
    from_language: list[str] = Field(
        default_factory=list,
        alias="FromLanguage",
    )

    # P.7.4 To language (for translators)
    to_language: list[str] = Field(
        default_factory=list,
        alias="ToLanguage",
    )

    # P.7.5 Primary name type
    name_type: str | None = Field(
        default=None,
        alias="NameType",
    )

    # P.7.6-8 Name identifiers
    name_identifiers: list[NameIdentifier] = Field(
        default_factory=list,
        alias="NameIdentifier",
    )

    # P.7.9 Person name
    person_name: str | None = Field(
        default=None,
        alias="PersonName",
    )

    # P.7.10 Person name inverted
    person_name_inverted: str | None = Field(
        default=None,
        alias="PersonNameInverted",
    )

    # P.7.11-18 Structured person name parts
    titles_before_names: str | None = Field(
        default=None,
        alias="TitlesBeforeNames",
    )
    names_before_key: str | None = Field(
        default=None,
        alias="NamesBeforeKey",
    )
    prefix_to_key: str | None = Field(
        default=None,
        alias="PrefixToKey",
    )
    key_names: str | None = Field(
        default=None,
        alias="KeyNames",
    )
    names_after_key: str | None = Field(
        default=None,
        alias="NamesAfterKey",
    )
    suffix_to_key: str | None = Field(
        default=None,
        alias="SuffixToKey",
    )
    letters_after_names: str | None = Field(
        default=None,
        alias="LettersAfterNames",
    )
    titles_after_names: str | None = Field(
        default=None,
        alias="TitlesAfterNames",
    )

    # P.7.19 Corporate name (repeatable)
    corporate_name: list[str] = Field(
        default_factory=list,
        alias="CorporateName",
    )

    # P.7.20 Corporate name inverted (repeatable)
    corporate_name_inverted: list[str] = Field(
        default_factory=list,
        alias="CorporateNameInverted",
    )

    # P.7.20a Unnamed persons
    unnamed_persons: str | None = Field(
        default=None,
        alias="UnnamedPersons",
    )

    # P.7.21-36 Alternative names
    alternative_names: list[AlternativeName] = Field(
        default_factory=list,
        alias="AlternativeName",
    )

    # P.7.37-39 Contributor dates
    contributor_dates: list[ContributorDate] = Field(
        default_factory=list,
        alias="ContributorDate",
    )

    # P.7.40-41 Professional affiliations
    professional_affiliations: list[ProfessionalAffiliation] = Field(
        default_factory=list,
        alias="ProfessionalAffiliation",
    )

    # P.7.41a-l Prizes
    prizes: list[Prize] = Field(
        default_factory=list,
        alias="Prize",
    )

    # P.7.42 Biographical note (repeatable)
    biographical_note: list[str] = Field(
        default_factory=list,
        alias="BiographicalNote",
    )

    # P.7.43-45 Websites
    websites: list[Website] = Field(
        default_factory=list,
        alias="Website",
    )

    # P.7.46 Contributor description (repeatable)
    contributor_description: list[str] = Field(
        default_factory=list,
        alias="ContributorDescription",
    )

    # P.7.48-50a Contributor places
    contributor_places: list[ContributorPlace] = Field(
        default_factory=list,
        alias="ContributorPlace",
    )

    @field_validator("contributor_role")
    @classmethod
    def validate_contributor_role(cls, v: list[str]) -> list[str]:
        """Validate all contributor_role codes are valid List 17 codes."""
        for code in v:
            if get_code(17, code) is None:
                raise ValueError(
                    f"Invalid ContributorRole: '{code}' is not a valid List 17 code"
                )
        return v

    @field_validator("from_language")
    @classmethod
    def validate_from_language(cls, v: list[str]) -> list[str]:
        """Validate all from_language codes are valid List 74 codes."""
        for code in v:
            if get_code(74, code) is None:
                raise ValueError(
                    f"Invalid FromLanguage: '{code}' is not a valid List 74 code"
                )
        return v

    @field_validator("to_language")
    @classmethod
    def validate_to_language(cls, v: list[str]) -> list[str]:
        """Validate all to_language codes are valid List 74 codes."""
        for code in v:
            if get_code(74, code) is None:
                raise ValueError(
                    f"Invalid ToLanguage: '{code}' is not a valid List 74 code"
                )
        return v

    @field_validator("name_type")
    @classmethod
    def validate_name_type(cls, v: str | None) -> str | None:
        """Validate name_type is a valid List 18 code."""
        if v is not None and get_code(18, v) is None:
            raise ValueError(f"Invalid NameType: '{v}' is not a valid List 18 code")
        return v

    @field_validator("unnamed_persons")
    @classmethod
    def validate_unnamed_persons(cls, v: str | None) -> str | None:
        """Validate unnamed_persons is a valid List 19 code."""
        if v is not None and get_code(19, v) is None:
            raise ValueError(
                f"Invalid UnnamedPersons: '{v}' is not a valid List 19 code"
            )
        return v

    @model_validator(mode="after")
    def validate_key_names_requirement(self) -> "Contributor":
        """If structured name parts are used, key_names is required."""
        structured_parts = [
            self.titles_before_names,
            self.names_before_key,
            self.prefix_to_key,
            self.names_after_key,
            self.suffix_to_key,
            self.letters_after_names,
            self.titles_after_names,
        ]
        if any(structured_parts) and not self.key_names:
            raise ValueError(
                "KeyNames is required when using structured person name parts"
            )
        return self

    @model_validator(mode="after")
    def validate_translator_languages(self) -> "Contributor":
        """Validate translator language requirements."""
        translator_roles = {"B06", "B08", "B10"}  # Translator role codes
        is_translator = any(role in translator_roles for role in self.contributor_role)

        if not is_translator:
            if self.from_language:
                raise ValueError(
                    "FromLanguage should only be used with translator roles (B06, B08, B10)"
                )
            if self.to_language:
                raise ValueError(
                    "ToLanguage should only be used with translator roles (B06, B08, B10)"
                )

        return self
