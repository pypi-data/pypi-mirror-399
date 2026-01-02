"""ONIX Header models.

The Header composite contains information about the sender and addressee(s)
of an ONIX message, along with message metadata.

Structure:
- Header
  - Sender (required)
    - SenderIdentifier (0…n)
    - SenderName, ContactName, EmailAddress, etc.
  - Addressee (0…n)
    - AddresseeIdentifier (0…n)
    - AddresseeName, ContactName, EmailAddress, etc.
  - MessageNumber, MessageRepeat, SentDateTime
  - DefaultLanguageOfText, DefaultPriceType, DefaultCurrencyCode
"""

from onix.header.header import (
    Addressee,
    AddresseeIdentifier,
    Header,
    Sender,
    SenderIdentifier,
)

__all__ = [
    "Header",
    "Sender",
    "SenderIdentifier",
    "Addressee",
    "AddresseeIdentifier",
]
