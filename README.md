# genanki-next

A Python library for programmatically generating Anki flashcard decks using schema v18.

## Features

- **Schema v18 support**: Generates `.apkg` files using the `.anki21b` format with normalized database tables
- **ZSTD compression**: Collection databases are ZSTD-compressed inside the `.apkg` archive
- **Protobuf wire format**: Configuration blobs are encoded using hand-rolled protobuf serialization
- **Pydantic models**: Type-safe data validation with Pydantic v2 for all Anki entities
- **Simple API**: Create decks with just a few lines of code via the `Package` class

## Installation

```bash
pip install genanki-next
```

Or with uv:

```bash
uv add genanki-next
```

## Quick Start

```python
from genanki_next import Package

# Create a package with a deck
pkg = Package("My Vocabulary")

# Add notes (uses Basic notetype by default)
pkg.create_note(fields=["Hello", "Hola"], tags=["greetings"])
pkg.create_note(fields=["Goodbye", "Adiós"], tags=["greetings"])
pkg.create_note(fields=["Thank you", "Gracias"], tags=["polite"])

# Write to file
pkg.write_to_file("vocabulary.apkg")
```

## Custom Notetypes

```python
from genanki_next import Package

pkg = Package("Programming")

# Create a custom notetype
notetype = pkg.create_notetype(
    name="Code Example",
    fields=["Question", "Code", "Explanation"],
    templates=[{
        "name": "Card 1",
        "qfmt": "{{Question}}",
        "afmt": "{{FrontSide}}<hr>{{Code}}<br>{{Explanation}}",
    }]
)

# Create notes with the custom notetype
pkg.create_note(
    fields=["What does print() do?", "print('Hello')", "Outputs text to console"],
    notetype=notetype,
)

pkg.write_to_file("programming.apkg")
```

## Multiple Decks

```python
from genanki_next import Package

pkg = Package("Main Deck")

# Create additional decks (use :: for hierarchy)
spanish_deck = pkg.create_deck("Languages::Spanish")

# Add notes to specific decks
pkg.create_note(fields=["Hello", "Hola"], deck_id=spanish_deck.id)
```

## Requirements

- Python 3.10+

## Public API

The following are exported from `genanki_next`:

- `Package` — High-level API for creating decks and writing `.apkg` files
- `Card`, `Collection`, `Deck`, `DeckConfig`, `Field`, `Note`, `Notetype`, `Template` — Pydantic models
- `GenAnkiError`, `ValidationError`, `DatabaseError`, `CompressionError`, `PackageError` — Exception hierarchy

## Current Limitations

- Media file support is not yet implemented (media manifest is always empty)
- Filtered decks are not yet supported
- Only basic card generation (no cloze deletion support yet)

## License

MIT
