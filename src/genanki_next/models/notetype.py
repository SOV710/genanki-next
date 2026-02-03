"""Notetype model defining note schemas and card generation."""

import time

from pydantic import BaseModel, Field, field_validator

from genanki_next.enums import CardRequirementKind, NoteKind
from genanki_next.models.field import Field as FieldModel
from genanki_next.models.template import Template


# Default CSS for card styling
DEFAULT_CSS = """.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}"""

# Default LaTeX preamble
DEFAULT_LATEX_PRE = r"""\documentclass[12pt]{article}
\special{papersize=3in,5in}
\usepackage[utf8]{inputenc}
\usepackage{amssymb,amsmath}
\pagestyle{empty}
\setlength{\parindent}{0in}
\begin{document}
"""

DEFAULT_LATEX_POST = r"\end{document}"


class CardRequirement(BaseModel):
    """Defines conditions for card generation from a template.

    Attributes:
        card_ord: Template ordinal this requirement applies to.
        kind: Type of requirement (NONE, ANY, ALL).
        field_ords: Field ordinals to check for non-empty content.
    """

    card_ord: int = Field(default=0, ge=0)
    kind: CardRequirementKind = Field(default=CardRequirementKind.NONE)
    field_ords: list[int] = Field(default_factory=list)


class NotetypeConfig(BaseModel):
    """Configuration for a notetype.

    Corresponds to the protobuf blob stored in notetypes.config.
    """

    kind: NoteKind = Field(default=NoteKind.NORMAL)
    sort_field_idx: int = Field(default=0, ge=0)
    css: str = Field(default=DEFAULT_CSS)
    latex_pre: str = Field(default=DEFAULT_LATEX_PRE)
    latex_post: str = Field(default=DEFAULT_LATEX_POST)
    latex_svg: bool = False
    reqs: list[CardRequirement] = Field(default_factory=list)


class Notetype(BaseModel):
    """Definition of a note type (model) for creating notes.

    Notetypes define the schema for notes, including fields and templates.
    Each note belongs to exactly one notetype.

    Attributes:
        id: Unique identifier (millisecond timestamp).
        name: Display name (e.g., "Basic", "Cloze").
        fields: List of field definitions.
        templates: List of card template definitions.
        config: Notetype configuration (CSS, LaTeX, card requirements).
        mtime_secs: Last modification timestamp (seconds).
        usn: Update sequence number for sync.
    """

    id: int = Field(default_factory=lambda: int(time.time() * 1000))
    name: str = Field(min_length=1)
    fields: list[FieldModel] = Field(min_length=1)
    templates: list[Template] = Field(min_length=1)
    config: NotetypeConfig = Field(default_factory=NotetypeConfig)
    mtime_secs: int = Field(default_factory=lambda: int(time.time()))
    usn: int = Field(default=-1)

    @field_validator("fields")
    @classmethod
    def set_field_ordinals(cls, v: list[FieldModel]) -> list[FieldModel]:
        """Ensure field ordinals are sequential starting from 0."""
        for i, field in enumerate(v):
            field.ordinal = i
        return v

    @field_validator("templates")
    @classmethod
    def set_template_ordinals(cls, v: list[Template]) -> list[Template]:
        """Ensure template ordinals are sequential starting from 0."""
        for i, template in enumerate(v):
            template.ordinal = i
        return v


def create_basic_notetype(notetype_id: int | None = None) -> Notetype:
    """Create a standard Basic notetype with Front and Back fields.

    Args:
        notetype_id: Optional ID to use. Auto-generated if not provided.

    Returns:
        A Basic notetype ready for use.
    """
    fields = [
        FieldModel(name="Front"),
        FieldModel(name="Back"),
    ]
    templates = [
        Template(name="Card 1"),
    ]
    if notetype_id is not None:
        return Notetype(
            id=notetype_id,
            name="Basic",
            fields=fields,
            templates=templates,
        )
    return Notetype(
        name="Basic",
        fields=fields,
        templates=templates,
    )
