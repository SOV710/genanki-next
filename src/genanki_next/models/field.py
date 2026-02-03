"""Field definition model for notetypes."""

from pydantic import BaseModel
from pydantic import Field as PydanticField


class FieldConfig(BaseModel):
    """Configuration for a field's display and behavior.

    Corresponds to the protobuf blob stored in fields.config.
    """

    sticky: bool = False
    rtl: bool = False
    font_name: str = "Arial"
    font_size: int = 20
    description: str = ""
    plain_text: bool = False
    collapsed: bool = False
    exclude_from_search: bool = False
    prevent_deletion: bool = False


class Field(BaseModel):
    """Definition of a field within a notetype.

    Fields define the schema for note content. Each notetype has one or more
    fields that determine what data can be stored in notes of that type.

    Attributes:
        name: Display name for the field (e.g., "Front", "Back").
        ordinal: Position of the field (0-based). Determines order in note.
        config: Display and behavior configuration.
    """

    name: str = PydanticField(min_length=1, description="Field display name")
    ordinal: int = PydanticField(default=0, ge=0, description="Field position (0-based)")
    config: FieldConfig = PydanticField(default_factory=FieldConfig)
