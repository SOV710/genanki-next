"""Pytest fixtures for genanki-next tests."""

import pytest

from genanki_next.models import (
    Deck,
    DeckConfig,
    Field,
    Note,
    Notetype,
    Template,
    create_basic_notetype,
    create_default_deck,
    create_default_deck_config,
)


@pytest.fixture
def basic_notetype() -> Notetype:
    """Create a basic notetype for testing."""
    return create_basic_notetype(notetype_id=1234567890)


@pytest.fixture
def default_deck() -> Deck:
    """Create the default deck for testing."""
    return create_default_deck()


@pytest.fixture
def default_deck_config() -> DeckConfig:
    """Create the default deck config for testing."""
    return create_default_deck_config()


@pytest.fixture
def custom_notetype() -> Notetype:
    """Create a custom notetype with 3 fields for testing."""
    fields = [
        Field(name="Question"),
        Field(name="Answer"),
        Field(name="Extra"),
    ]
    templates = [
        Template(name="Card 1"),
    ]
    return Notetype(
        id=9876543210,
        name="Custom",
        fields=fields,
        templates=templates,
    )


@pytest.fixture
def sample_note(basic_notetype: Notetype) -> Note:
    """Create a sample note for testing."""
    return Note(
        id=1111111111,
        notetype_id=basic_notetype.id,
        fields=["What is Python?", "A programming language"],
        tags=["programming", "basics"],
    )
