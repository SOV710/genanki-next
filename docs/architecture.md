# Architecture

## Build Pipeline

The flow from user API to `.apkg` output:

```
Package (api.py)
  │
  ├── SQLiteBuilder (database/builder.py)
  │     ├── schema.py    — 12 CREATE TABLE statements
  │     ├── indexes.py   — 13 CREATE INDEX statements
  │     ├── inserter.py  — Row insertion functions
  │     │     └── proto/builders.py — Serializes config models to protobuf BLOB bytes
  │     │           └── proto/messages.py — Wire format primitives (varint, string, embedded msg)
  │     └── Returns raw SQLite bytes via _serialize_connection()
  │
  ├── APKGBuilder (package/builder.py)
  │     ├── compress_sqlite() (compression/zstd.py) — ZSTD compression
  │     ├── create_empty_media() (package/stubs.py) — Empty JSON manifest
  │     └── Writes ZIP archive: collection.anki21b + media
  │
  └── output.apkg
```

## Database Schema (v18)

The SQLite database contains 12 tables, defined in `database/schema.py`:

| Table | Description | Key columns |
|-------|-------------|-------------|
| `col` | Collection metadata (singleton) | `id=1`, `ver=18`, `crt`, `mod`, `scm` |
| `config` | Key-value settings | `key` (TEXT PK), `val` (BLOB) |
| `notetypes` | Note type definitions | `id`, `name`, `config` (protobuf BLOB) |
| `fields` | Field definitions per notetype | `ntid`, `ord`, `name`, `config` (protobuf BLOB) |
| `templates` | Card templates per notetype | `ntid`, `ord`, `name`, `config` (protobuf BLOB) |
| `decks` | Deck hierarchy | `id`, `name`, `common` (BLOB), `kind` (BLOB) |
| `deck_config` | Scheduling configurations | `id`, `name`, `config` (protobuf BLOB) |
| `notes` | Note content | `id`, `guid`, `mid` (notetype), `flds`, `tags` |
| `cards` | Card scheduling state | `id`, `nid`, `did`, `type`, `queue`, `due` |
| `tags` | Tag registry | `tag` (TEXT PK) |
| `revlog` | Review history | `id`, `cid`, `ease`, `ivl`, `type` |
| `graves` | Deleted entity tracking | `oid`, `type` |

13 indexes are defined in `database/indexes.py` for notes, cards, notetypes, fields, templates, and decks.

The `col` table uses `COLLATE NOCASE` (substituting Anki's `COLLATE unicase`).

## Protobuf Encoding

Protobuf encoding is entirely hand-rolled in `proto/messages.py`. The `protobuf` pip package is listed as a dependency but is not imported anywhere in the source code.

`proto/messages.py` implements:
- Wire type encoders: `encode_varint`, `encode_uint32`, `encode_int32`, `encode_int64`, `encode_bool`, `encode_enum`, `encode_float`, `encode_double`, `encode_string`, `encode_bytes`, `encode_embedded_message`, `encode_packed_floats`, `encode_packed_uint32`
- `MessageBuilder` class with chainable `add_*` methods

`proto/builders.py` provides 6 high-level blob builders:
- `build_deck_config_blob()` — `deck_config.config` column
- `build_notetype_config_blob()` — `notetypes.config` column
- `build_field_config_blob()` — `fields.config` column
- `build_template_config_blob()` — `templates.config` column
- `build_deck_common_blob()` — `decks.common` column
- `build_deck_kind_blob()` — `decks.kind` column (Normal variant only; Filtered returns empty bytes)

Reference protobuf field number mappings are documented in `reference/proto/`.

## SQLite Serialization

`_serialize_connection()` in `database/builder.py` converts an in-memory SQLite database to bytes:

1. Backup the connection to a new in-memory database
2. Dump via `iterdump()` and re-execute into a fresh connection
3. Try `sqlite3.Connection.serialize()` (available in Python 3.11+)
4. Fall back to writing to a temp file for Python 3.10

## ZSTD Compression

`compression/zstd.py` provides:
- `compress_sqlite(data, level=3)` — Compress raw SQLite bytes using ZSTD (levels 1-22)
- `decompress_sqlite(data)` — Decompress ZSTD-compressed bytes

The compressed bytes are stored as `collection.anki21b` inside the `.apkg` ZIP archive. The ZIP itself uses `ZIP_STORED` (no additional compression).

## APKG Package Format

An `.apkg` file is a ZIP archive containing:
- `collection.anki21b` — ZSTD-compressed SQLite database
- `media` — JSON manifest mapping media IDs to filenames (currently always `{}`)

`APKGBuilder` in `package/builder.py` handles construction. The `.apkg` extension is automatically added if missing. Parent directories are created as needed.

A convenience function `build_apkg(sqlite_bytes, output_path, compress=True)` is also exported.
