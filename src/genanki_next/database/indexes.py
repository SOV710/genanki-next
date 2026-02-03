"""SQL CREATE INDEX statements for Anki v18 schema."""

# Notes indexes
IDX_NOTES_MID = "CREATE INDEX idx_notes_mid ON notes (mid)"
IDX_NOTES_CSUM = "CREATE INDEX ix_notes_csum ON notes (csum)"
IDX_NOTES_USN = "CREATE INDEX ix_notes_usn ON notes (usn)"

# Cards indexes
IDX_CARDS_ODID = "CREATE INDEX idx_cards_odid ON cards (odid)"
IDX_CARDS_SCHED = "CREATE INDEX ix_cards_sched ON cards (did, queue, due)"
IDX_CARDS_NID = "CREATE INDEX ix_cards_nid ON cards (nid)"
IDX_CARDS_USN = "CREATE INDEX ix_cards_usn ON cards (usn)"

# Notetypes indexes
IDX_NOTETYPES_USN = "CREATE INDEX idx_notetypes_usn ON notetypes (usn)"
IDX_NOTETYPES_NAME = "CREATE UNIQUE INDEX idx_notetypes_name ON notetypes (name)"

# Fields indexes
IDX_FIELDS_NAME_NTID = "CREATE UNIQUE INDEX idx_fields_name_ntid ON fields (name, ntid)"

# Templates indexes
IDX_TEMPLATES_USN = "CREATE INDEX idx_templates_usn ON templates (usn)"
IDX_TEMPLATES_NAME_NTID = "CREATE UNIQUE INDEX idx_templates_name_ntid ON templates (name, ntid)"

# Decks indexes
IDX_DECKS_NAME = "CREATE UNIQUE INDEX idx_decks_name ON decks (name)"

# All indexes in creation order
INDEXES = [
    IDX_NOTES_MID,
    IDX_NOTES_CSUM,
    IDX_NOTES_USN,
    IDX_CARDS_ODID,
    IDX_CARDS_SCHED,
    IDX_CARDS_NID,
    IDX_CARDS_USN,
    IDX_NOTETYPES_USN,
    IDX_NOTETYPES_NAME,
    IDX_FIELDS_NAME_NTID,
    IDX_TEMPLATES_USN,
    IDX_TEMPLATES_NAME_NTID,
    IDX_DECKS_NAME,
]
