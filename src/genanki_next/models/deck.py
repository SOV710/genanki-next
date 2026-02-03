"""Deck model for organizing cards."""

import time

from pydantic import BaseModel, Field


class DeckCommon(BaseModel):
    """Common deck metadata shared by Normal and Filtered decks.

    Corresponds to the protobuf blob stored in decks.common.
    """

    study_collapsed: bool = False
    browser_collapsed: bool = False
    last_day_studied: int = Field(default=0, ge=0)
    new_studied: int = Field(default=0, ge=0)
    review_studied: int = Field(default=0, ge=0)
    learning_studied: int = Field(default=0, ge=0)
    milliseconds_studied: int = Field(default=0, ge=0)


class DayLimit(BaseModel):
    """Daily limit tracking for a deck."""

    limit: int = Field(default=0, ge=0)
    today: int = Field(default=0, ge=0)


class DeckNormal(BaseModel):
    """Configuration specific to normal (non-filtered) decks.

    Corresponds to the protobuf blob stored in decks.kind when kind=normal.
    """

    config_id: int = Field(default=1, ge=1, description="Reference to deck_config.id")
    extend_new: int = Field(default=0, ge=0)
    extend_review: int = Field(default=0, ge=0)
    description: str = ""
    markdown_description: bool = False
    review_limit: int | None = None
    new_limit: int | None = None
    review_limit_today: DayLimit = Field(default_factory=DayLimit)
    new_limit_today: DayLimit = Field(default_factory=DayLimit)
    desired_retention: float | None = None


class Deck(BaseModel):
    """A deck for organizing flashcards.

    Decks form a hierarchy using :: separator in names (e.g., "Japanese::Kanji").
    Each deck is either a Normal deck (references a DeckConfig) or a Filtered
    deck (temporary, based on search query).

    Attributes:
        id: Unique identifier (millisecond timestamp). Default deck has id=1.
        name: Display name with hierarchy (e.g., "Languages::Spanish").
        common: Shared metadata (study stats, collapse state).
        normal: Normal deck configuration (None for filtered decks).
        mtime_secs: Last modification timestamp (seconds).
        usn: Update sequence number for sync.
    """

    id: int = Field(default_factory=lambda: int(time.time() * 1000))
    name: str = Field(min_length=1)
    common: DeckCommon = Field(default_factory=DeckCommon)
    normal: DeckNormal | None = Field(default_factory=DeckNormal)
    mtime_secs: int = Field(default_factory=lambda: int(time.time()))
    usn: int = Field(default=-1)

    @property
    def is_filtered(self) -> bool:
        """Check if this is a filtered deck."""
        return self.normal is None


def create_default_deck() -> Deck:
    """Create the default deck.

    Returns:
        The default Deck with id=1 and name="Default".
    """
    return Deck(id=1, name="Default")
