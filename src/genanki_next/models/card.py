"""Card model for flashcard instances and scheduling state."""

import time

from pydantic import BaseModel, Field

from genanki_next.enums import CardQueue, CardType


class Card(BaseModel):
    """A flashcard instance with scheduling state.

    Cards are generated from notes based on templates. Each card tracks
    its own scheduling state (due date, interval, ease factor, etc.).

    Attributes:
        id: Unique identifier (millisecond timestamp).
        note_id: Reference to the parent note.
        deck_id: Reference to the deck containing this card.
        template_ord: Template ordinal (0-based) that generated this card.
        mod: Last modification timestamp (seconds).
        usn: Update sequence number for sync.
        card_type: Learning state (new, learning, review, relearning).
        queue: Scheduling queue.
        due: Due position/time (interpretation varies by queue).
        interval: Review interval in days.
        ease_factor: Ease factor * 1000 (e.g., 2500 = 2.5x).
        reps: Number of reviews completed.
        lapses: Number of times the card was forgotten.
        left: Remaining learning steps.
        original_due: Original due value (for filtered decks).
        original_deck_id: Original deck ID (for filtered decks).
        flags: User flag bitmask.
    """

    id: int = Field(default_factory=lambda: int(time.time() * 1000))
    note_id: int = Field(description="Reference to notes.id")
    deck_id: int = Field(description="Reference to decks.id")
    template_ord: int = Field(default=0, ge=0)
    mod: int = Field(default_factory=lambda: int(time.time()))
    usn: int = Field(default=-1)

    # Scheduling state
    card_type: CardType = Field(default=CardType.NEW)
    queue: CardQueue = Field(default=CardQueue.NEW)
    due: int = Field(default=0, description="Due position/time")
    interval: int = Field(default=0, ge=0, description="Interval in days")
    ease_factor: int = Field(default=0, ge=0, description="Ease * 1000")
    reps: int = Field(default=0, ge=0)
    lapses: int = Field(default=0, ge=0)
    left: int = Field(default=0, ge=0, description="Remaining learning steps")

    # Filtered deck support
    original_due: int = Field(default=0)
    original_deck_id: int = Field(default=0)

    # Metadata
    flags: int = Field(default=0, ge=0)

    @classmethod
    def create_new(
        cls,
        note_id: int,
        deck_id: int,
        template_ord: int = 0,
        due_position: int = 0,
    ) -> "Card":
        """Create a new card in the new queue.

        Args:
            note_id: ID of the parent note.
            deck_id: ID of the containing deck.
            template_ord: Template ordinal (0-based).
            due_position: Position in the new card queue.

        Returns:
            A new Card instance ready for insertion.
        """
        return cls(
            note_id=note_id,
            deck_id=deck_id,
            template_ord=template_ord,
            card_type=CardType.NEW,
            queue=CardQueue.NEW,
            due=due_position,
        )
