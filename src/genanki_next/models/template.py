"""Card template model for notetypes."""

from pydantic import BaseModel, Field


class TemplateConfig(BaseModel):
    """Configuration for a card template.

    Corresponds to the protobuf blob stored in templates.config.
    """

    q_format: str = "{{Front}}"
    a_format: str = "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
    q_format_browser: str = ""
    a_format_browser: str = ""
    target_deck_id: int = 0
    browser_font_name: str = ""
    browser_font_size: int = 0


class Template(BaseModel):
    """Definition of a card template within a notetype.

    Templates define how cards are generated from notes. Each template
    produces one card per note, with the question and answer formatted
    according to the template's HTML.

    Attributes:
        name: Display name for the template (e.g., "Card 1", "Forward").
        ordinal: Position of the template (0-based). Determines card order.
        config: Template HTML and display configuration.
        mtime_secs: Last modification timestamp (seconds).
        usn: Update sequence number for sync.
    """

    name: str = Field(min_length=1, description="Template display name")
    ordinal: int = Field(default=0, ge=0, description="Template position (0-based)")
    config: TemplateConfig = Field(default_factory=TemplateConfig)
    mtime_secs: int = Field(default=0, ge=0, description="Last modification time (seconds)")
    usn: int = Field(default=-1, description="Update sequence number")
