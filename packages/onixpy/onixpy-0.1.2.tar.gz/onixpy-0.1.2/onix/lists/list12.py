"""ONIX Code List 12: Trade category."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "01": CodeListEntry(
        list_number=12,
        code="01",
        heading="UK open market edition",
        notes="An edition from a UK publisher sold only in territories where exclusive rights are not held. Rights details should be carried in PR.21 (in ONIX 2.1) OR P.21 (in ONIX 3.0 or later) as usual",
        added_version=2,
    ),
    "02": CodeListEntry(
        list_number=12,
        code="02",
        heading="Airport edition",
        notes="In UK, an edition intended primarily for airside sales in UK airports, though it may be available for sale in other territories where exclusive rights are not held. Rights details should be carried in PR.21 (in ONIX 2.1) OR P.21 (in ONIX 3.0 or later) as usual",
        added_version=2,
    ),
    "03": CodeListEntry(
        list_number=12,
        code="03",
        heading="Sonderausgabe",
        notes="In Germany, a special printing sold at a lower price than the regular hardback",
        added_version=2,
    ),
    "04": CodeListEntry(
        list_number=12,
        code="04",
        heading="Pocket book",
        notes="In countries where recognized as a distinct trade category, eg France « livre de poche », Germany ,Taschenbuch‘, Italy «tascabile», Spain «libro de bolsillo»",
        added_version=2,
    ),
    "05": CodeListEntry(
        list_number=12,
        code="05",
        heading="International edition (US)",
        notes="Edition produced solely for sale in designated export markets",
        added_version=2,
    ),
    "06": CodeListEntry(
        list_number=12,
        code="06",
        heading="Library audio edition",
        notes="Audio product sold in special durable packaging and with a replacement guarantee for the contained cassettes or CDs for a specified shelf-life",
        added_version=2,
    ),
    "07": CodeListEntry(
        list_number=12,
        code="07",
        heading="US open market edition",
        notes="An edition from a US publisher sold only in territories where exclusive rights are not held. Rights details should be carried in PR.21 (in ONIX 2.1) OR P.21 (in ONIX 3.0 or later) as usual",
        added_version=3,
    ),
    "08": CodeListEntry(
        list_number=12,
        code="08",
        heading="Livre scolaire, déclaré par l’éditeur",
        notes="In France, a category of book that has a particular legal status, claimed by the publisher",
        added_version=5,
    ),
    "09": CodeListEntry(
        list_number=12,
        code="09",
        heading="Livre scolaire (non spécifié)",
        notes="In France, a category of book that has a particular legal status, designated independently of the publisher",
        added_version=5,
    ),
    "10": CodeListEntry(
        list_number=12,
        code="10",
        heading="Supplement to newspaper",
        notes="Edition published for sale only with a newspaper or periodical",
        added_version=7,
    ),
    "11": CodeListEntry(
        list_number=12,
        code="11",
        heading="Precio libre textbook",
        notes="In Spain, a school textbook for which there is no fixed or suggested retail price and which is supplied by the publisher on terms individually agreed with the bookseller",
        added_version=8,
    ),
    "12": CodeListEntry(
        list_number=12,
        code="12",
        heading="News outlet edition",
        notes="For editions sold only through newsstands/newsagents",
        added_version=14,
    ),
    "13": CodeListEntry(
        list_number=12,
        code="13",
        heading="US textbook",
        notes="In the US and Canada, a book that is published primarily for use by students in school or college education as a basis for study. Textbooks published for the elementary and secondary school markets are generally purchased by school districts for the use of students. Textbooks published for the higher education market are generally adopted for use in particular classes by the instructors of those classes. Textbooks are usually not marketed to the general public, which distinguishes them from trade books. Note that trade books adopted for course use are not considered to be textbooks (though a specific education edition of a trade title may be)",
        added_version=17,
    ),
    "14": CodeListEntry(
        list_number=12,
        code="14",
        heading="E-book short",
        notes="‘Short’ e-book (sometimes also called a ‘single’), typically containing a single short story, an essay or piece of long-form journalism",
        added_version=27,
    ),
    "15": CodeListEntry(
        list_number=12,
        code="15",
        heading="Superpocket book",
        notes="In countries where recognized as a distinct trade category, eg Italy «supertascabile». Only for use in ONIX 3.0 or later",
        added_version=39,
    ),
    "16": CodeListEntry(
        list_number=12,
        code="16",
        heading="Beau-livre",
        notes="Category of books, usually hardcover and of a large format (A4 or larger) and printed on high-quality paper, where the primary features are illustrations, and these are more important than text. Sometimes called ‘coffee-table books’ or ‘art books’ in English. Only for use in ONIX 3.0 or later",
        added_version=42,
    ),
    "17": CodeListEntry(
        list_number=12,
        code="17",
        heading="Podcast",
        notes="Category of audio products typically distinguished by being free of charge (but which may be monetized through advertising content) and episodic. Only for use in ONIX 3.0 or later",
        added_version=44,
    ),
    "18": CodeListEntry(
        list_number=12,
        code="18",
        heading="Periodical",
        notes="Category of books or e-books which are single issues of a periodical publication, sold as independent products. Only for use in ONIX 3.0 or later",
        added_version=44,
    ),
    "19": CodeListEntry(
        list_number=12,
        code="19",
        heading="Catalog",
        notes="Publisher’s or supplier’s catalog (when treated as a product in its own right). Only for use in ONIX 3.0 or later",
        added_version=58,
    ),
    "20": CodeListEntry(
        list_number=12,
        code="20",
        heading="Atlas",
        notes="Category of books containing a linked group of plates, tables, diagrams, lists, often but not always combined with maps or a geographical theme or approach. Only for use in ONIX 3.0 or later",
        added_version=60,
    ),
    "21": CodeListEntry(
        list_number=12,
        code="21",
        heading="Newspaper",
        notes="Daily or weekly. Only for use in ONIX 3.0 or later",
        added_version=67,
    ),
}

List12 = CodeList(
    number=12,
    heading="Trade category",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
TradeCategory = List12
