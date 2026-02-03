"""Note model for storing flashcard content."""

import hashlib
import itertools
import time
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator


# Field separator used in notes.flds column
FIELD_SEPARATOR = "\x1f"

# Global counter to ensure unique IDs within the same millisecond
_id_counter = itertools.count()


def _generate_unique_id() -> int:
    """Generate a unique ID based on current time and a counter."""
    base_id = int(time.time() * 1000)
    return base_id + next(_id_counter) % 1000


def _generate_guid() -> str:
    """Generate a globally unique identifier for a note.

    Uses base91 encoding of random bytes for compact representation.
    """
    import random
    import string

    # Base91 character set (excluding some problematic chars)
    chars = string.ascii_letters + string.digits + "!#$%&()*+,-./:;<=>?@[]^_`{|}~"
    return "".join(random.choice(chars) for _ in range(10))


def _compute_checksum(text: str) -> int:
    """Compute SHA-1 checksum of text for duplicate detection.

    Returns first 8 hex digits as integer.
    """
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


class Note(BaseModel):
    """A note containing flashcard content.

    Notes store the actual content (fields) that cards display. Each note
    belongs to a notetype and can generate one or more cards based on
    the notetype's templates.

    Attributes:
        id: Unique identifier (millisecond timestamp).
        guid: Globally unique Base91 string for sync.
        notetype_id: Reference to the notetype this note uses.
        fields: Content for each field defined in the notetype.
        tags: List of tags for organization.
        mod: Last modification timestamp (seconds).
        usn: Update sequence number for sync.
        flags: Note-level flags.
    """

    FIELD_SEPARATOR: ClassVar[str] = FIELD_SEPARATOR

    id: int = Field(default_factory=_generate_unique_id)
    guid: str = Field(default_factory=_generate_guid)
    notetype_id: int = Field(description="Reference to notetypes.id")
    fields: list[str] = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    mod: int = Field(default_factory=lambda: int(time.time()))
    usn: int = Field(default=-1)
    flags: int = Field(default=0, ge=0)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        """Normalize tags by stripping whitespace."""
        return [tag.strip() for tag in v if tag.strip()]

    @property
    def sort_field(self) -> str:
        """Get the first field value used for sorting."""
        return self.fields[0] if self.fields else ""

    @property
    def checksum(self) -> int:
        """Compute checksum of first field for duplicate detection."""
        return _compute_checksum(self.sort_field)

    def fields_joined(self) -> str:
        """Join fields with the Anki field separator."""
        return FIELD_SEPARATOR.join(self.fields)

    def tags_string(self) -> str:
        """Format tags as space-separated string with leading/trailing space.

        Returns " tag1 tag2 " format required by Anki.
        """
        if not self.tags:
            return " "
        return " " + " ".join(self.tags) + " "
