# genanki-next

A Python library for programmatically generating Anki flashcard decks using schema v18.

## Features

- **Schema v18 support**: Generates `.apkg` files compatible with modern Anki versions
- **ZSTD compression**: Uses the `.anki21b` format with ZSTD-compressed SQLite databases
- **Protocol Buffers**: Proper encoding of configuration blobs using protobuf wire format
- **Pydantic models**: Type-safe data validation with Pydantic v2
- **Simple API**: Create decks with just a few lines of code

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

## Requirements

- Python 3.10+
- Anki 2.1.55+ (for v18 schema support)

## Comparison with genanki

This library is a modern reimplementation focused on schema v18 only:

| Feature | genanki | genanki-next |
|---------|---------|--------------|
| Schema v11 | Yes | No |
| Schema v18 | No | Yes |
| ZSTD compression | No | Yes |
| Protobuf blobs | No | Yes |
| Type hints | Partial | Full |
| Pydantic validation | No | Yes |

## License

MIT
