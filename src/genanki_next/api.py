"""High-level API for creating Anki packages.

This module provides a simple, user-friendly interface for creating
Anki deck packages without needing to understand the underlying
database schema.

Example:
    >>> from genanki_next import Package
    >>> pkg = Package("My Vocabulary")
    >>> pkg.create_note(fields=["Hello", "World"])
    >>> pkg.write_to_file("vocabulary.apkg")
"""

import logging
from pathlib import Path

from genanki_next.database.builder import SQLiteBuilder
from genanki_next.models.card import Card
from genanki_next.models.collection import Collection
from genanki_next.models.deck import Deck
from genanki_next.models.field import Field
from genanki_next.models.note import Note
from genanki_next.models.notetype import Notetype, create_basic_notetype
from genanki_next.models.template import Template, TemplateConfig
from genanki_next.package.builder import APKGBuilder


logger = logging.getLogger(__name__)


class Package:
    """High-level API for creating Anki packages.

    This class provides a simplified interface for the common workflow of
    creating a deck, adding notes, and exporting to an .apkg file.

    Example:
        >>> pkg = Package("Spanish Vocabulary")
        >>> pkg.create_note(
        ...     fields=["Hola", "Hello"],
        ...     tags=["greetings"]
        ... )
        >>> pkg.write_to_file("spanish.apkg")

    For more control, you can create custom notetypes:
        >>> pkg = Package("Programming")
        >>> notetype = pkg.create_notetype(
        ...     name="Code Example",
        ...     fields=["Question", "Code", "Explanation"],
        ...     templates=[{
        ...         "name": "Card 1",
        ...         "qfmt": "{{Question}}",
        ...         "afmt": "{{FrontSide}}<hr>{{Code}}<br>{{Explanation}}",
        ...     }]
        ... )
        >>> pkg.create_note(
        ...     fields=["What does print() do?", "print('Hello')", "Outputs text"],
        ...     notetype=notetype,
        ... )
    """

    def __init__(self, deck_name: str = "Default") -> None:
        """Initialize a new package with a deck.

        Args:
            deck_name: Name for the primary deck. Defaults to "Default".
        """
        self._collection = Collection()
        self._builder = SQLiteBuilder(self._collection)

        # Create primary deck if not "Default"
        if deck_name != "Default":
            deck = Deck(name=deck_name)
            self._builder.add_deck(deck)
            self._primary_deck_id = deck.id
        else:
            self._primary_deck_id = 1  # Default deck

        # Create default notetype
        self._default_notetype = create_basic_notetype()
        self._builder.add_notetype(self._default_notetype)

        self._notetypes: dict[int, Notetype] = {self._default_notetype.id: self._default_notetype}

    @property
    def deck_id(self) -> int:
        """Get the primary deck ID."""
        return self._primary_deck_id

    @property
    def default_notetype(self) -> Notetype:
        """Get the default Basic notetype."""
        return self._default_notetype

    def create_deck(self, name: str) -> Deck:
        """Create an additional deck.

        Args:
            name: Deck name. Use :: for hierarchy (e.g., "Languages::Spanish").

        Returns:
            The created Deck model.
        """
        deck = Deck(name=name)
        self._builder.add_deck(deck)
        return deck

    def create_notetype(
        self,
        name: str,
        fields: list[str],
        templates: list[dict[str, str]],
    ) -> Notetype:
        """Create a custom notetype.

        Args:
            name: Display name for the notetype.
            fields: List of field names (e.g., ["Front", "Back"]).
            templates: List of template definitions. Each template should have:
                - name: Template display name
                - qfmt: Question format HTML with {{FieldName}} placeholders
                - afmt: Answer format HTML with {{FieldName}} placeholders

        Returns:
            The created Notetype model.

        Example:
            >>> notetype = pkg.create_notetype(
            ...     name="Vocabulary",
            ...     fields=["Word", "Definition", "Example"],
            ...     templates=[{
            ...         "name": "Card 1",
            ...         "qfmt": "{{Word}}",
            ...         "afmt": "{{FrontSide}}<hr>{{Definition}}<br><i>{{Example}}</i>",
            ...     }]
            ... )
        """
        # Create Field models
        field_models = [Field(name=f) for f in fields]

        # Create Template models
        template_models = []
        for i, tmpl in enumerate(templates):
            config = TemplateConfig(
                q_format=tmpl.get("qfmt", f"{{{{{fields[0]}}}}}"),
                a_format=tmpl.get("afmt", "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"),
            )
            template_models.append(
                Template(
                    name=tmpl.get("name", f"Card {i + 1}"),
                    config=config,
                )
            )

        notetype = Notetype(
            name=name,
            fields=field_models,
            templates=template_models,
        )
        self._builder.add_notetype(notetype)
        self._notetypes[notetype.id] = notetype
        return notetype

    def create_note(
        self,
        fields: list[str],
        tags: list[str] | None = None,
        notetype: Notetype | None = None,
        deck_id: int | None = None,
    ) -> Note:
        """Create a note and add it to the package.

        Args:
            fields: Content for each field. Must match notetype field count.
            tags: Optional list of tags for organization.
            notetype: Notetype to use. Defaults to Basic notetype.
            deck_id: Target deck ID. Defaults to primary deck.

        Returns:
            The created Note model.

        Example:
            >>> pkg.create_note(
            ...     fields=["What is 2+2?", "4"],
            ...     tags=["math", "basic"]
            ... )
        """
        notetype = notetype or self._default_notetype
        deck_id = deck_id or self._primary_deck_id

        note = Note(
            notetype_id=notetype.id,
            fields=fields,
            tags=tags or [],
        )
        self._builder.add_note(note, deck_id=deck_id)
        return note

    def add_note(
        self,
        note: Note,
        deck_id: int | None = None,
    ) -> list[Card]:
        """Add an existing note to the package.

        Args:
            note: Note model to add.
            deck_id: Target deck ID. Defaults to primary deck.

        Returns:
            List of generated cards.
        """
        deck_id = deck_id or self._primary_deck_id
        return self._builder.add_note(note, deck_id=deck_id)

    def write_to_file(self, path: str | Path) -> Path:
        """Build and write the .apkg file.

        Args:
            path: Output file path. Will add .apkg extension if missing.

        Returns:
            Path to the created .apkg file.
        """
        logger.info("Building package: %s", path)

        # Build SQLite database
        sqlite_bytes = self._builder.build()

        # Build APKG package
        apkg_builder = APKGBuilder()
        apkg_builder.set_collection(sqlite_bytes)
        return apkg_builder.build(path)
