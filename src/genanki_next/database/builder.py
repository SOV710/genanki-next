"""SQLite database builder for Anki v18 collections."""

import logging
import sqlite3
import time

from genanki_next.database.indexes import INDEXES
from genanki_next.database.inserter import (
    insert_card,
    insert_collection,
    insert_config_entry,
    insert_deck,
    insert_deck_config,
    insert_note,
    insert_notetype,
    insert_tag,
)
from genanki_next.database.schema import TABLES
from genanki_next.exceptions import DatabaseError
from genanki_next.models.card import Card
from genanki_next.models.collection import Collection, get_default_config_entries
from genanki_next.models.deck import Deck, create_default_deck
from genanki_next.models.deck_config import DeckConfig, create_default_deck_config
from genanki_next.models.note import Note
from genanki_next.models.notetype import Notetype


logger = logging.getLogger(__name__)


class SQLiteBuilder:
    """Builds Anki collection SQLite database from models.

    This class manages the construction of an in-memory SQLite database
    containing all the tables and data for an Anki collection.

    Example:
        builder = SQLiteBuilder()
        builder.add_notetype(basic_notetype)
        builder.add_deck(my_deck)
        builder.add_note(note, deck_id=1)
        db_bytes = builder.build()
    """

    def __init__(self, collection: Collection | None = None) -> None:
        """Initialize the builder.

        Args:
            collection: Optional collection metadata. Defaults to new collection.
        """
        self._collection = collection or Collection()
        self._deck_configs: dict[int, DeckConfig] = {}
        self._decks: dict[int, Deck] = {}
        self._notetypes: dict[int, Notetype] = {}
        self._notes: list[Note] = []
        self._cards: list[Card] = []
        self._tags: set[str] = set()
        self._next_card_position: dict[int, int] = {}  # deck_id -> next position

        # Add defaults
        default_config = create_default_deck_config()
        self._deck_configs[default_config.id] = default_config

        default_deck = create_default_deck()
        self._decks[default_deck.id] = default_deck
        self._next_card_position[default_deck.id] = 0

    def add_deck_config(self, deck_config: DeckConfig) -> None:
        """Add a deck configuration.

        Args:
            deck_config: DeckConfig model to add.
        """
        self._deck_configs[deck_config.id] = deck_config

    def add_deck(self, deck: Deck) -> None:
        """Add a deck.

        Args:
            deck: Deck model to add.
        """
        self._decks[deck.id] = deck
        if deck.id not in self._next_card_position:
            self._next_card_position[deck.id] = 0

    def add_notetype(self, notetype: Notetype) -> None:
        """Add a notetype with its fields and templates.

        Args:
            notetype: Notetype model to add.
        """
        self._notetypes[notetype.id] = notetype

    def add_note(
        self,
        note: Note,
        deck_id: int = 1,
        generate_cards: bool = True,
    ) -> list[Card]:
        """Add a note and optionally generate cards.

        Args:
            note: Note model to add.
            deck_id: Target deck ID for generated cards.
            generate_cards: Whether to auto-generate cards from templates.

        Returns:
            List of generated cards (empty if generate_cards=False).

        Raises:
            DatabaseError: If notetype not found or deck not found.
        """
        if note.notetype_id not in self._notetypes:
            raise DatabaseError(f"Notetype {note.notetype_id} not found. Add it first.")
        if deck_id not in self._decks:
            raise DatabaseError(f"Deck {deck_id} not found. Add it first.")

        self._notes.append(note)

        # Collect tags
        for tag in note.tags:
            self._tags.add(tag)

        if not generate_cards:
            return []

        # Generate cards from templates
        notetype = self._notetypes[note.notetype_id]
        cards = []
        for template in notetype.templates:
            position = self._next_card_position.get(deck_id, 0)
            card = Card.create_new(
                note_id=note.id,
                deck_id=deck_id,
                template_ord=template.ordinal,
                due_position=position,
            )
            # Ensure unique card ID
            card.id = int(time.time() * 1000) + len(self._cards)
            cards.append(card)
            self._cards.append(card)
            self._next_card_position[deck_id] = position + 1

        return cards

    def add_card(self, card: Card) -> None:
        """Add a card directly (without auto-generation).

        Args:
            card: Card model to add.
        """
        self._cards.append(card)

    def build(self) -> bytes:
        """Generate SQLite database bytes.

        Returns:
            Raw SQLite database file contents.

        Raises:
            DatabaseError: If database generation fails.
        """
        logger.info("Building SQLite database for collection")

        conn: sqlite3.Connection | None = None
        try:
            conn = sqlite3.connect(":memory:")
            conn.execute("PRAGMA foreign_keys = ON")

            # Create tables
            for table_name, create_sql in TABLES:
                logger.debug("Creating table: %s", table_name)
                conn.execute(create_sql)

            # Create indexes
            for index_sql in INDEXES:
                conn.execute(index_sql)

            # Insert collection metadata
            insert_collection(conn, self._collection)

            # Insert config entries
            for entry in get_default_config_entries():
                insert_config_entry(conn, entry)

            # Insert deck configs
            for deck_config in self._deck_configs.values():
                insert_deck_config(conn, deck_config)

            # Insert decks
            for deck in self._decks.values():
                insert_deck(conn, deck)

            # Insert notetypes
            for notetype in self._notetypes.values():
                insert_notetype(conn, notetype)

            # Insert notes
            for note in self._notes:
                insert_note(conn, note)

            # Insert cards
            for card in self._cards:
                insert_card(conn, card)

            # Insert tags
            for tag in self._tags:
                insert_tag(conn, tag)

            conn.commit()

            # Serialize database to bytes
            db_bytes = _serialize_connection(conn)

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to build SQLite database: {e}") from e
        finally:
            if conn is not None:
                conn.close()

        logger.info(
            "Database built: %d notetypes, %d decks, %d notes, %d cards",
            len(self._notetypes),
            len(self._decks),
            len(self._notes),
            len(self._cards),
        )

        return db_bytes


def _serialize_connection(conn: sqlite3.Connection) -> bytes:
    """Serialize an in-memory SQLite connection to bytes.

    Args:
        conn: SQLite connection.

    Returns:
        Raw SQLite database file contents.
    """
    # Use backup API to copy to a bytes buffer

    # Create a new in-memory database and backup to it
    target = sqlite3.connect(":memory:")
    conn.backup(target)

    # Serialize to bytes using iterdump
    script = "\n".join(target.iterdump())
    target.close()

    # Re-execute the dump into a fresh database and serialize
    fresh = sqlite3.connect(":memory:")
    fresh.executescript(script)

    # Use the serialize method (Python 3.11+) or backup workaround
    try:
        return fresh.serialize()  # type: ignore[attr-defined, no-any-return]
    except AttributeError:
        # Fallback for older Python: write to temp file
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            temp_path = Path(f.name)

        try:
            backup_conn = sqlite3.connect(str(temp_path))
            fresh.backup(backup_conn)
            backup_conn.close()
            with temp_path.open("rb") as f:
                return f.read()
        finally:
            temp_path.unlink()
