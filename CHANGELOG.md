# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Initial implementation of Anki schema v18 support
- `Package` class for high-level deck creation API
- Pydantic models for all Anki entities (Note, Card, Deck, Notetype, etc.)
- Protobuf encoding for configuration blobs
- SQLite database builder with all v18 tables
- ZSTD compression for `.anki21b` format
- APKG package builder
- Support for custom notetypes with multiple fields and templates
- Tag support for notes
- Comprehensive test suite

### Known Limitations

- Media file support not yet implemented
- Filtered decks not yet supported
- Only basic card generation (no cloze deletion support yet)
