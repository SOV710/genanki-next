"""SQL CREATE TABLE statements for Anki v18 schema."""

# Note: COLLATE unicase is Anki-specific and not available in standard SQLite.
# We use COLLATE NOCASE as a compatible alternative.

COL_TABLE = """
CREATE TABLE col (
    id INTEGER PRIMARY KEY,
    crt INTEGER NOT NULL,
    mod INTEGER NOT NULL,
    scm INTEGER NOT NULL,
    ver INTEGER NOT NULL,
    dty INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    ls INTEGER NOT NULL,
    conf TEXT NOT NULL,
    models TEXT NOT NULL,
    decks TEXT NOT NULL,
    dconf TEXT NOT NULL,
    tags TEXT NOT NULL
)
"""

CONFIG_TABLE = """
CREATE TABLE config (
    key TEXT NOT NULL PRIMARY KEY,
    val BLOB NOT NULL,
    usn INTEGER NOT NULL,
    mtime_secs INTEGER NOT NULL
) WITHOUT ROWID
"""

NOTES_TABLE = """
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    guid TEXT NOT NULL,
    mid INTEGER NOT NULL,
    mod INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    tags TEXT NOT NULL,
    flds TEXT NOT NULL,
    sfld INTEGER NOT NULL,
    csum INTEGER NOT NULL,
    flags INTEGER NOT NULL,
    data TEXT NOT NULL
)
"""

CARDS_TABLE = """
CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    nid INTEGER NOT NULL,
    did INTEGER NOT NULL,
    ord INTEGER NOT NULL,
    mod INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    type INTEGER NOT NULL,
    queue INTEGER NOT NULL,
    due INTEGER NOT NULL,
    ivl INTEGER NOT NULL,
    factor INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    lapses INTEGER NOT NULL,
    left INTEGER NOT NULL,
    odue INTEGER NOT NULL,
    odid INTEGER NOT NULL,
    flags INTEGER NOT NULL,
    data TEXT NOT NULL
)
"""

NOTETYPES_TABLE = """
CREATE TABLE notetypes (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE,
    mtime_secs INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    config BLOB NOT NULL
)
"""

FIELDS_TABLE = """
CREATE TABLE fields (
    ntid INTEGER NOT NULL,
    ord INTEGER NOT NULL,
    name TEXT NOT NULL COLLATE NOCASE,
    config BLOB NOT NULL,
    PRIMARY KEY (ntid, ord)
) WITHOUT ROWID
"""

TEMPLATES_TABLE = """
CREATE TABLE templates (
    ntid INTEGER NOT NULL,
    ord INTEGER NOT NULL,
    name TEXT NOT NULL COLLATE NOCASE,
    mtime_secs INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    config BLOB NOT NULL,
    PRIMARY KEY (ntid, ord)
) WITHOUT ROWID
"""

DECKS_TABLE = """
CREATE TABLE decks (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL COLLATE NOCASE,
    mtime_secs INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    common BLOB NOT NULL,
    kind BLOB NOT NULL
)
"""

DECK_CONFIG_TABLE = """
CREATE TABLE deck_config (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL COLLATE NOCASE,
    mtime_secs INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    config BLOB NOT NULL
)
"""

TAGS_TABLE = """
CREATE TABLE tags (
    tag TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
    usn INTEGER NOT NULL,
    collapsed INTEGER NOT NULL,
    config BLOB
) WITHOUT ROWID
"""

REVLOG_TABLE = """
CREATE TABLE revlog (
    id INTEGER PRIMARY KEY,
    cid INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    ease INTEGER NOT NULL,
    ivl INTEGER NOT NULL,
    lastIvl INTEGER NOT NULL,
    factor INTEGER NOT NULL,
    time INTEGER NOT NULL,
    type INTEGER NOT NULL
)
"""

GRAVES_TABLE = """
CREATE TABLE graves (
    oid INTEGER NOT NULL,
    type INTEGER NOT NULL,
    usn INTEGER NOT NULL,
    PRIMARY KEY (oid, type)
) WITHOUT ROWID
"""

# Table creation order (respects dependencies)
TABLES = [
    ("col", COL_TABLE),
    ("config", CONFIG_TABLE),
    ("deck_config", DECK_CONFIG_TABLE),
    ("decks", DECKS_TABLE),
    ("notetypes", NOTETYPES_TABLE),
    ("fields", FIELDS_TABLE),
    ("templates", TEMPLATES_TABLE),
    ("notes", NOTES_TABLE),
    ("cards", CARDS_TABLE),
    ("tags", TAGS_TABLE),
    ("revlog", REVLOG_TABLE),
    ("graves", GRAVES_TABLE),
]
