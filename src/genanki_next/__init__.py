"""genanki-next: Library for programmatically generating Anki decks with schema v18 support."""

from genanki_next.api import Package
from genanki_next.exceptions import (
    CompressionError,
    DatabaseError,
    GenAnkiError,
    PackageError,
    ValidationError,
)
from genanki_next.models import (
    Card,
    Collection,
    Deck,
    DeckConfig,
    Field,
    Note,
    Notetype,
    Template,
)


__all__ = [
    "Card",
    "Collection",
    "CompressionError",
    "DatabaseError",
    "Deck",
    "DeckConfig",
    "Field",
    "GenAnkiError",
    "Note",
    "Notetype",
    "Package",
    "PackageError",
    "Template",
    "ValidationError",
]

__version__ = "0.1.0"
