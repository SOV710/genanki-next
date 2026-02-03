"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from genanki_next.enums import CardQueue, CardType
from genanki_next.models import (
    Card,
    Collection,
    Deck,
    DeckConfig,
    DeckConfigSettings,
    Field,
    Note,
    Notetype,
    Template,
)


class TestField:
    """Tests for Field model."""

    def test_field_creation(self) -> None:
        """Test basic field creation."""
        field = Field(name="Front")
        assert field.name == "Front"
        assert field.ordinal == 0
        assert field.config.font_name == "Arial"
        assert field.config.font_size == 20

    def test_field_requires_name(self) -> None:
        """Test that field requires a name."""
        with pytest.raises(ValidationError):
            Field(name="")


class TestTemplate:
    """Tests for Template model."""

    def test_template_creation(self) -> None:
        """Test basic template creation."""
        template = Template(name="Card 1")
        assert template.name == "Card 1"
        assert template.ordinal == 0
        assert "{{Front}}" in template.config.q_format
        assert "{{Back}}" in template.config.a_format


class TestNotetype:
    """Tests for Notetype model."""

    def test_notetype_creation(self, basic_notetype: Notetype) -> None:
        """Test basic notetype creation."""
        assert basic_notetype.name == "Basic"
        assert len(basic_notetype.fields) == 2
        assert len(basic_notetype.templates) == 1

    def test_notetype_field_ordinals(self, basic_notetype: Notetype) -> None:
        """Test that field ordinals are set correctly."""
        assert basic_notetype.fields[0].ordinal == 0
        assert basic_notetype.fields[1].ordinal == 1

    def test_notetype_requires_fields(self) -> None:
        """Test that notetype requires at least one field."""
        with pytest.raises(ValidationError):
            Notetype(name="Empty", fields=[], templates=[Template(name="Card 1")])

    def test_notetype_requires_templates(self) -> None:
        """Test that notetype requires at least one template."""
        with pytest.raises(ValidationError):
            Notetype(name="Empty", fields=[Field(name="Front")], templates=[])


class TestNote:
    """Tests for Note model."""

    def test_note_creation(self, sample_note: Note) -> None:
        """Test basic note creation."""
        assert sample_note.notetype_id == 1234567890
        assert len(sample_note.fields) == 2
        assert "programming" in sample_note.tags

    def test_note_fields_joined(self, sample_note: Note) -> None:
        """Test that fields are joined correctly."""
        joined = sample_note.fields_joined()
        assert "\x1f" in joined
        assert "What is Python?" in joined
        assert "A programming language" in joined

    def test_note_tags_string(self, sample_note: Note) -> None:
        """Test that tags are formatted correctly."""
        tags_str = sample_note.tags_string()
        assert tags_str.startswith(" ")
        assert tags_str.endswith(" ")
        assert "programming" in tags_str
        assert "basics" in tags_str

    def test_note_empty_tags(self) -> None:
        """Test note with empty tags."""
        note = Note(notetype_id=1, fields=["Front"])
        assert note.tags_string() == " "

    def test_note_checksum(self, sample_note: Note) -> None:
        """Test that checksum is computed."""
        assert sample_note.checksum > 0

    def test_note_sort_field(self, sample_note: Note) -> None:
        """Test that sort field is first field."""
        assert sample_note.sort_field == "What is Python?"


class TestCard:
    """Tests for Card model."""

    def test_card_creation(self) -> None:
        """Test basic card creation."""
        card = Card(note_id=1, deck_id=1)
        assert card.card_type == CardType.NEW
        assert card.queue == CardQueue.NEW
        assert card.interval == 0
        assert card.ease_factor == 0

    def test_card_create_new(self) -> None:
        """Test Card.create_new factory method."""
        card = Card.create_new(note_id=123, deck_id=456, due_position=10)
        assert card.note_id == 123
        assert card.deck_id == 456
        assert card.due == 10
        assert card.card_type == CardType.NEW
        assert card.queue == CardQueue.NEW


class TestDeck:
    """Tests for Deck model."""

    def test_deck_creation(self, default_deck: Deck) -> None:
        """Test default deck creation."""
        assert default_deck.id == 1
        assert default_deck.name == "Default"
        assert not default_deck.is_filtered

    def test_deck_hierarchy_name(self) -> None:
        """Test deck with hierarchical name."""
        deck = Deck(name="Languages::Spanish::Verbs")
        assert deck.name == "Languages::Spanish::Verbs"


class TestDeckConfig:
    """Tests for DeckConfig model."""

    def test_deck_config_creation(self, default_deck_config: DeckConfig) -> None:
        """Test default deck config creation."""
        assert default_deck_config.id == 1
        assert default_deck_config.name == "Default"

    def test_deck_config_settings(self) -> None:
        """Test deck config settings defaults."""
        settings = DeckConfigSettings()
        assert settings.new_per_day == 20
        assert settings.reviews_per_day == 200
        assert settings.learn_steps == [1.0, 10.0]
        assert settings.initial_ease == 2.5


class TestCollection:
    """Tests for Collection model."""

    def test_collection_creation(self) -> None:
        """Test collection creation with defaults."""
        collection = Collection()
        assert collection.id == 1
        assert collection.version == 18
        assert collection.dirty == 0
