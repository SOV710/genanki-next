"""Row insertion logic for Anki v18 SQLite database."""

import sqlite3

from genanki_next.models.card import Card
from genanki_next.models.collection import Collection, ConfigEntry
from genanki_next.models.deck import Deck
from genanki_next.models.deck_config import DeckConfig
from genanki_next.models.note import Note
from genanki_next.models.notetype import Notetype
from genanki_next.proto.builders import (
    build_deck_common_blob,
    build_deck_config_blob,
    build_deck_kind_blob,
    build_field_config_blob,
    build_notetype_config_blob,
    build_template_config_blob,
)


def insert_collection(conn: sqlite3.Connection, collection: Collection) -> None:
    """Insert collection metadata into col table.

    Args:
        conn: SQLite connection.
        collection: Collection model.
    """
    conn.execute(
        """
        INSERT INTO col (id, crt, mod, scm, ver, dty, usn, ls, conf, models, decks, dconf, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', '', '', '', '')
        """,
        (
            collection.id,
            collection.creation_time,
            collection.mod_time,
            collection.schema_mod_time,
            collection.version,
            collection.dirty,
            collection.usn,
            collection.last_sync,
        ),
    )


def insert_config_entry(conn: sqlite3.Connection, entry: ConfigEntry) -> None:
    """Insert a configuration entry into config table.

    Args:
        conn: SQLite connection.
        entry: ConfigEntry model.
    """
    conn.execute(
        """
        INSERT INTO config (key, val, usn, mtime_secs)
        VALUES (?, ?, ?, ?)
        """,
        (entry.key, entry.value, entry.usn, entry.mtime_secs),
    )


def insert_deck_config(conn: sqlite3.Connection, deck_config: DeckConfig) -> None:
    """Insert deck configuration into deck_config table.

    Args:
        conn: SQLite connection.
        deck_config: DeckConfig model.
    """
    config_blob = build_deck_config_blob(deck_config)
    conn.execute(
        """
        INSERT INTO deck_config (id, name, mtime_secs, usn, config)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            deck_config.id,
            deck_config.name,
            deck_config.mtime_secs,
            deck_config.usn,
            config_blob,
        ),
    )


def insert_deck(conn: sqlite3.Connection, deck: Deck) -> None:
    """Insert deck into decks table.

    Args:
        conn: SQLite connection.
        deck: Deck model.
    """
    common_blob = build_deck_common_blob(deck)
    kind_blob = build_deck_kind_blob(deck)
    conn.execute(
        """
        INSERT INTO decks (id, name, mtime_secs, usn, common, kind)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            deck.id,
            deck.name,
            deck.mtime_secs,
            deck.usn,
            common_blob,
            kind_blob,
        ),
    )


def insert_notetype(conn: sqlite3.Connection, notetype: Notetype) -> None:
    """Insert notetype and its fields/templates into database.

    Args:
        conn: SQLite connection.
        notetype: Notetype model with fields and templates.
    """
    # Insert notetype
    config_blob = build_notetype_config_blob(notetype)
    conn.execute(
        """
        INSERT INTO notetypes (id, name, mtime_secs, usn, config)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            notetype.id,
            notetype.name,
            notetype.mtime_secs,
            notetype.usn,
            config_blob,
        ),
    )

    # Insert fields
    for field in notetype.fields:
        field_config_blob = build_field_config_blob(field)
        conn.execute(
            """
            INSERT INTO fields (ntid, ord, name, config)
            VALUES (?, ?, ?, ?)
            """,
            (notetype.id, field.ordinal, field.name, field_config_blob),
        )

    # Insert templates
    for template in notetype.templates:
        template_config_blob = build_template_config_blob(template)
        conn.execute(
            """
            INSERT INTO templates (ntid, ord, name, mtime_secs, usn, config)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                notetype.id,
                template.ordinal,
                template.name,
                template.mtime_secs,
                template.usn,
                template_config_blob,
            ),
        )


def insert_note(conn: sqlite3.Connection, note: Note) -> None:
    """Insert note into notes table.

    Args:
        conn: SQLite connection.
        note: Note model.
    """
    conn.execute(
        """
        INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '')
        """,
        (
            note.id,
            note.guid,
            note.notetype_id,
            note.mod,
            note.usn,
            note.tags_string(),
            note.fields_joined(),
            note.sort_field,
            note.checksum,
            note.flags,
        ),
    )


def insert_card(conn: sqlite3.Connection, card: Card) -> None:
    """Insert card into cards table.

    Args:
        conn: SQLite connection.
        card: Card model.
    """
    conn.execute(
        """
        INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor,
                          reps, lapses, left, odue, odid, flags, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')
        """,
        (
            card.id,
            card.note_id,
            card.deck_id,
            card.template_ord,
            card.mod,
            card.usn,
            card.card_type,
            card.queue,
            card.due,
            card.interval,
            card.ease_factor,
            card.reps,
            card.lapses,
            card.left,
            card.original_due,
            card.original_deck_id,
            card.flags,
        ),
    )


def insert_tag(conn: sqlite3.Connection, tag: str, usn: int = -1) -> None:
    """Insert tag into tags table.

    Args:
        conn: SQLite connection.
        tag: Tag name.
        usn: Update sequence number.
    """
    conn.execute(
        """
        INSERT OR IGNORE INTO tags (tag, usn, collapsed, config)
        VALUES (?, ?, 0, NULL)
        """,
        (tag, usn),
    )
