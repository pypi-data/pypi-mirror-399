"""ONIX Code List 1: Notification or update type."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=1,
        code="01",
        heading="Early notification",
        notes="Use for a complete record issued earlier than approximately six months before publication",
    ),
    "02": CodeListEntry(
        list_number=1,
        code="02",
        heading="Advance notification (confirmed)",
        notes="Use for a complete record issued to confirm advance information approximately six months before publication; or for a complete record issued after that date and before information has been confirmed from the book-in-hand",
    ),
    "03": CodeListEntry(
        list_number=1,
        code="03",
        heading="Notification confirmed on publication",
        notes="Use for a complete record issued to confirm advance information at or just before actual publication date, usually from the book-in-hand, or for a complete record issued at any later date",
    ),
    "04": CodeListEntry(
        list_number=1,
        code="04",
        heading="Update (partial)",
        notes="In ONIX 3.0 or later only, use when sending a ‘block update’ record. A block update implies using the supplied block(s) to update the existing record for the product, replacing only the blocks included in the block update, and leaving other blocks unchanged - for example, replacing old information from Blocks 4 and 6 with the newly-received data while retaining information from Blocks 1-3, 5 and 7-8 untouched. In previous ONIX releases, and for ONIX 3.0 or later using other notification types, updating is by replacing the complete record with the newly-received data",
    ),
    "05": CodeListEntry(
        list_number=1,
        code="05",
        heading="Delete",
        notes="Use when sending an instruction to delete a record which was previously issued. Note that a Delete instruction should NOT be used when a product is cancelled, put out of print, or otherwise withdrawn from sale: this should be handled as a change of Publishing status, leaving the receiver to decide whether to retain or delete the record. A Delete instruction is used ONLY when there is a particular reason to withdraw a record completely, eg because it was issued in error",
    ),
    "08": CodeListEntry(
        list_number=1,
        code="08",
        heading="Notice of sale",
        notes="Notice of sale of a product, from one publisher to another: sent by the publisher disposing of the product",
        added_version=2,
    ),
    "09": CodeListEntry(
        list_number=1,
        code="09",
        heading="Notice of acquisition",
        notes="Notice of acquisition of a product, by one publisher from another: sent by the acquiring publisher",
        added_version=2,
    ),
    "88": CodeListEntry(
        list_number=1,
        code="88",
        heading="Test update (partial)",
        notes="Only for use in ONIX 3.0 or later. Record may be processed for test purposes, but data should be discarded when testing is complete. Sender must ensure the <RecordReference> matches a previously-sent Test record",
        added_version=26,
    ),
    "89": CodeListEntry(
        list_number=1,
        code="89",
        heading="Test record",
        notes="Record may be processed for test purposes, but data should be discarded when testing is complete. Sender must ensure the <RecordReference> does not match any previously-sent live product record",
        added_version=26,
    ),
}

List1 = CodeList(
    number=1,
    heading="Notification or update type",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
NotificationOrUpdateType = List1
