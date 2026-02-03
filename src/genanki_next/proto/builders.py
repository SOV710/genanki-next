"""High-level protobuf builders for Anki v18 BLOB columns.

This module provides functions to build protobuf blobs for each BLOB column
in the Anki v18 schema.
"""

from genanki_next.models.deck import DayLimit, Deck, DeckCommon, DeckNormal
from genanki_next.models.deck_config import DeckConfig, DeckConfigSettings
from genanki_next.models.field import Field, FieldConfig
from genanki_next.models.notetype import CardRequirement, Notetype, NotetypeConfig
from genanki_next.models.template import Template, TemplateConfig
from genanki_next.proto.messages import MessageBuilder


def build_deck_config_blob(config: DeckConfig | DeckConfigSettings) -> bytes:
    """Build protobuf blob for deck_config.config column.

    Args:
        config: DeckConfig model or DeckConfigSettings.

    Returns:
        Serialized protobuf bytes.
    """
    settings = config.settings if isinstance(config, DeckConfig) else config

    builder = MessageBuilder()

    # Repeated float fields (learning steps)
    builder.add_packed_floats(1, settings.learn_steps)
    builder.add_packed_floats(2, settings.relearn_steps)
    builder.add_packed_floats(3, settings.fsrs_params_4)
    builder.add_packed_floats(4, settings.easy_days_percentages)
    builder.add_packed_floats(5, settings.fsrs_params_5)
    builder.add_packed_floats(6, settings.fsrs_params_6)

    # Daily limits
    builder.add_uint32(9, settings.new_per_day)
    builder.add_uint32(10, settings.reviews_per_day)

    # Ease/interval multipliers
    builder.add_float(11, settings.initial_ease)
    builder.add_float(12, settings.easy_multiplier)
    builder.add_float(13, settings.hard_multiplier)
    builder.add_float(14, settings.lapse_multiplier)
    builder.add_float(15, settings.interval_multiplier)

    # Interval bounds
    builder.add_uint32(16, settings.maximum_review_interval)
    builder.add_uint32(17, settings.minimum_lapse_interval)
    builder.add_uint32(18, settings.graduating_interval_good)
    builder.add_uint32(19, settings.graduating_interval_easy)

    # Card ordering enums
    builder.add_enum(20, settings.new_card_insert_order)
    builder.add_enum(21, settings.leech_action)
    builder.add_uint32(22, settings.leech_threshold)

    # Audio/timer booleans
    builder.add_bool(23, settings.disable_autoplay)
    builder.add_uint32(24, settings.cap_answer_time_to_secs)
    builder.add_bool(25, settings.show_timer)
    builder.add_bool(26, settings.skip_question_when_replaying_answer)

    # Burying options
    builder.add_bool(27, settings.bury_new)
    builder.add_bool(28, settings.bury_reviews)
    builder.add_bool(29, settings.bury_interday_learning)

    # More ordering enums
    builder.add_enum(30, settings.new_mix)
    builder.add_enum(31, settings.interday_learning_mix)
    builder.add_enum(32, settings.new_card_sort_order)
    builder.add_enum(33, settings.review_order)
    builder.add_enum(34, settings.new_card_gather_priority)
    builder.add_uint32(35, settings.new_per_day_minimum)

    # FSRS retention
    builder.add_float(37, settings.desired_retention)
    builder.add_bool(38, settings.stop_timer_on_answer)
    builder.add_float(40, settings.historical_retention)
    builder.add_float(41, settings.seconds_to_show_question)
    builder.add_float(42, settings.seconds_to_show_answer)

    builder.add_bool(44, settings.wait_for_audio)

    return builder.build()


def build_notetype_config_blob(notetype: Notetype | NotetypeConfig) -> bytes:
    """Build protobuf blob for notetypes.config column.

    Args:
        notetype: Notetype model or NotetypeConfig.

    Returns:
        Serialized protobuf bytes.
    """
    config = notetype.config if isinstance(notetype, Notetype) else notetype

    builder = MessageBuilder()

    # Kind enum
    builder.add_enum(1, config.kind)

    # Sort field index
    builder.add_uint32(2, config.sort_field_idx)

    # CSS and LaTeX
    builder.add_string(3, config.css)
    builder.add_string(5, config.latex_pre)
    builder.add_string(6, config.latex_post)
    builder.add_bool(7, config.latex_svg)

    # Card requirements
    for req in config.reqs:
        req_bytes = _build_card_requirement(req)
        builder.add_message(8, req_bytes)

    return builder.build()


def _build_card_requirement(req: CardRequirement) -> bytes:
    """Build protobuf for a CardRequirement submessage."""
    builder = MessageBuilder()
    builder.add_uint32(1, req.card_ord)
    builder.add_enum(2, req.kind)
    builder.add_packed_uint32(3, req.field_ords)
    return builder.build()


def build_field_config_blob(field: Field | FieldConfig) -> bytes:
    """Build protobuf blob for fields.config column.

    Args:
        field: Field model or FieldConfig.

    Returns:
        Serialized protobuf bytes.
    """
    config = field.config if isinstance(field, Field) else field

    builder = MessageBuilder()

    builder.add_bool(1, config.sticky)
    builder.add_bool(2, config.rtl)
    builder.add_string(3, config.font_name)
    builder.add_uint32(4, config.font_size)
    builder.add_string(5, config.description)
    builder.add_bool(6, config.plain_text)
    builder.add_bool(7, config.collapsed)
    builder.add_bool(8, config.exclude_from_search)
    builder.add_bool(11, config.prevent_deletion)

    return builder.build()


def build_template_config_blob(template: Template | TemplateConfig) -> bytes:
    """Build protobuf blob for templates.config column.

    Args:
        template: Template model or TemplateConfig.

    Returns:
        Serialized protobuf bytes.
    """
    config = template.config if isinstance(template, Template) else template

    builder = MessageBuilder()

    builder.add_string(1, config.q_format)
    builder.add_string(2, config.a_format)
    builder.add_string(3, config.q_format_browser)
    builder.add_string(4, config.a_format_browser)
    builder.add_int64(5, config.target_deck_id)
    builder.add_string(6, config.browser_font_name)
    builder.add_uint32(7, config.browser_font_size)

    return builder.build()


def build_deck_common_blob(deck: Deck | DeckCommon) -> bytes:
    """Build protobuf blob for decks.common column.

    Args:
        deck: Deck model or DeckCommon.

    Returns:
        Serialized protobuf bytes.
    """
    common = deck.common if isinstance(deck, Deck) else deck

    builder = MessageBuilder()

    builder.add_bool(1, common.study_collapsed)
    builder.add_bool(2, common.browser_collapsed)
    builder.add_uint32(3, common.last_day_studied)
    builder.add_int32(4, common.new_studied)
    builder.add_int32(5, common.review_studied)
    builder.add_int32(6, common.learning_studied)
    builder.add_int32(7, common.milliseconds_studied)

    return builder.build()


def build_deck_kind_blob(deck: Deck) -> bytes:
    """Build protobuf blob for decks.kind column.

    Args:
        deck: Deck model.

    Returns:
        Serialized protobuf bytes (Normal or Filtered variant).
    """
    if deck.normal is not None:
        # Normal deck - field number 6
        normal_bytes = _build_deck_normal(deck.normal)
        builder = MessageBuilder()
        builder.add_message(6, normal_bytes)
        return builder.build()
    # Filtered deck would use field number 7
    # Not implemented for now - return empty
    return b""


def _build_deck_normal(normal: DeckNormal) -> bytes:
    """Build protobuf for Normal deck submessage."""
    builder = MessageBuilder()

    builder.add_int64(1, normal.config_id)
    builder.add_uint32(2, normal.extend_new)
    builder.add_uint32(3, normal.extend_review)
    builder.add_string(4, normal.description)
    builder.add_bool(5, normal.markdown_description)

    # Optional limits (only include if set)
    if normal.review_limit is not None:
        builder.add_uint32(6, normal.review_limit)
    if normal.new_limit is not None:
        builder.add_uint32(7, normal.new_limit)

    # Day limits
    review_limit_today = _build_day_limit(normal.review_limit_today)
    if review_limit_today:
        builder.add_message(8, review_limit_today)

    new_limit_today = _build_day_limit(normal.new_limit_today)
    if new_limit_today:
        builder.add_message(9, new_limit_today)

    # Optional retention
    if normal.desired_retention is not None:
        builder.add_float(10, normal.desired_retention)

    return builder.build()


def _build_day_limit(day_limit: DayLimit) -> bytes:
    """Build protobuf for DayLimit submessage."""

    if day_limit.limit == 0 and day_limit.today == 0:
        return b""  # Default, omit

    builder = MessageBuilder()
    builder.add_uint32(1, day_limit.limit)
    builder.add_uint32(2, day_limit.today)
    return builder.build()
