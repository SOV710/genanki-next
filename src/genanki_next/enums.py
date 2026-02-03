"""Enumerations for Anki schema v18 data types."""

from enum import IntEnum


class CardType(IntEnum):
    """Card learning state type."""

    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


class CardQueue(IntEnum):
    """Card scheduling queue."""

    BURIED = -2
    SUSPENDED = -1
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    DAY_LEARNING = 3


class NoteKind(IntEnum):
    """Notetype kind discriminator."""

    NORMAL = 0
    CLOZE = 1


class NewCardInsertOrder(IntEnum):
    """Order for inserting new cards into the queue."""

    DUE = 0
    RANDOM = 1


class NewCardGatherPriority(IntEnum):
    """Priority for gathering new cards."""

    DECK = 0
    LOWEST_POSITION = 1
    HIGHEST_POSITION = 2
    RANDOM_NOTES = 3
    RANDOM_CARDS = 4
    DECK_THEN_RANDOM_NOTES = 5


class NewCardSortOrder(IntEnum):
    """Sort order for new cards."""

    TEMPLATE = 0
    NO_SORT = 1
    TEMPLATE_THEN_RANDOM = 2
    RANDOM_NOTE_THEN_TEMPLATE = 3
    RANDOM_CARD = 4


class ReviewCardOrder(IntEnum):
    """Sort order for review cards."""

    DAY = 0
    DAY_THEN_DECK = 1
    DECK_THEN_DAY = 2
    INTERVALS_ASCENDING = 3
    INTERVALS_DESCENDING = 4
    EASE_ASCENDING = 5
    EASE_DESCENDING = 6
    RETRIEVABILITY_ASCENDING = 7
    RANDOM = 8
    ADDED = 9
    REVERSE_ADDED = 10
    RETRIEVABILITY_DESCENDING = 11


class ReviewMix(IntEnum):
    """How to mix different card types during review."""

    MIX_WITH_REVIEWS = 0
    AFTER_REVIEWS = 1
    BEFORE_REVIEWS = 2


class LeechAction(IntEnum):
    """Action to take when a card becomes a leech."""

    SUSPEND = 0
    TAG_ONLY = 1


class CardRequirementKind(IntEnum):
    """Requirement type for card generation."""

    NONE = 0
    ANY = 1
    ALL = 2


class FilteredDeckOrder(IntEnum):
    """Sort order for filtered deck search terms."""

    OLDEST_REVIEWED_FIRST = 0
    RANDOM = 1
    INTERVALS_ASCENDING = 2
    INTERVALS_DESCENDING = 3
    LAPSES = 4
    ADDED = 5
    DUE = 6
    REVERSE_ADDED = 7
    RETRIEVABILITY_ASCENDING = 8
    RETRIEVABILITY_DESCENDING = 9
