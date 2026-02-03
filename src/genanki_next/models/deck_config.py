"""Deck configuration model for scheduling parameters."""

import time

from pydantic import BaseModel, Field

from genanki_next.enums import (
    LeechAction,
    NewCardGatherPriority,
    NewCardInsertOrder,
    NewCardSortOrder,
    ReviewCardOrder,
    ReviewMix,
)


class DeckConfigSettings(BaseModel):
    """Scheduling algorithm parameters.

    Corresponds to the protobuf blob stored in deck_config.config.
    """

    # Learning steps (in minutes)
    learn_steps: list[float] = Field(default_factory=lambda: [1.0, 10.0])
    relearn_steps: list[float] = Field(default_factory=list)

    # Daily limits
    new_per_day: int = Field(default=20, ge=0)
    reviews_per_day: int = Field(default=200, ge=0)
    new_per_day_minimum: int = Field(default=0, ge=0)

    # Ease/interval multipliers
    initial_ease: float = Field(default=2.5, ge=1.3)
    easy_multiplier: float = Field(default=1.3, ge=1.0)
    hard_multiplier: float = Field(default=1.2, ge=1.0)
    lapse_multiplier: float = Field(default=1.0, ge=0.0)
    interval_multiplier: float = Field(default=1.0, ge=0.0)

    # Interval bounds
    maximum_review_interval: int = Field(default=36500, ge=1)
    minimum_lapse_interval: int = Field(default=1, ge=1)
    graduating_interval_good: int = Field(default=1, ge=1)
    graduating_interval_easy: int = Field(default=4, ge=1)

    # Card ordering
    new_card_insert_order: NewCardInsertOrder = Field(default=NewCardInsertOrder.DUE)
    new_card_gather_priority: NewCardGatherPriority = Field(default=NewCardGatherPriority.DECK)
    new_card_sort_order: NewCardSortOrder = Field(default=NewCardSortOrder.TEMPLATE)
    review_order: ReviewCardOrder = Field(default=ReviewCardOrder.DAY)
    new_mix: ReviewMix = Field(default=ReviewMix.MIX_WITH_REVIEWS)
    interday_learning_mix: ReviewMix = Field(default=ReviewMix.MIX_WITH_REVIEWS)

    # Leech handling
    leech_action: LeechAction = Field(default=LeechAction.TAG_ONLY)
    leech_threshold: int = Field(default=8, ge=1)

    # Burying options
    bury_new: bool = False
    bury_reviews: bool = False
    bury_interday_learning: bool = False

    # Audio/timer options
    disable_autoplay: bool = False
    cap_answer_time_to_secs: int = Field(default=60, ge=0)
    show_timer: bool = False
    skip_question_when_replaying_answer: bool = False
    stop_timer_on_answer: bool = False
    wait_for_audio: bool = True
    seconds_to_show_question: float = Field(default=0.0, ge=0.0)
    seconds_to_show_answer: float = Field(default=0.0, ge=0.0)

    # FSRS parameters (empty by default)
    fsrs_params_4: list[float] = Field(default_factory=list)
    fsrs_params_5: list[float] = Field(default_factory=list)
    fsrs_params_6: list[float] = Field(default_factory=list)
    easy_days_percentages: list[float] = Field(default_factory=list)

    # FSRS retention
    desired_retention: float = Field(default=0.9, ge=0.0, le=1.0)
    historical_retention: float = Field(default=0.9, ge=0.0, le=1.0)


class DeckConfig(BaseModel):
    """Deck configuration defining scheduling behavior.

    Deck configs are shared across decks. Multiple decks can reference
    the same configuration.

    Attributes:
        id: Unique identifier. Default config has id=1.
        name: Display name for the config.
        settings: Scheduling algorithm parameters.
        mtime_secs: Last modification timestamp (seconds).
        usn: Update sequence number for sync.
    """

    id: int = Field(default=1, ge=1)
    name: str = Field(default="Default", min_length=1)
    settings: DeckConfigSettings = Field(default_factory=DeckConfigSettings)
    mtime_secs: int = Field(default_factory=lambda: int(time.time()))
    usn: int = Field(default=0)


def create_default_deck_config() -> DeckConfig:
    """Create the default deck configuration.

    Returns:
        The default DeckConfig with id=1.
    """
    return DeckConfig(id=1, name="Default")
