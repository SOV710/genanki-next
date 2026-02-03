"""Collection model for database-level metadata."""

import time

from pydantic import BaseModel, Field


class Collection(BaseModel):
    """Collection-level metadata stored in the col table.

    The col table is a singleton (exactly one row) containing metadata
    about the entire collection.

    Attributes:
        id: Always 1 (singleton table).
        creation_time: Collection creation timestamp (seconds).
        mod_time: Last modification timestamp (milliseconds).
        schema_mod_time: Schema modification timestamp (milliseconds).
        version: Schema version (18 for v18).
        dirty: Dirty flag (0 = clean).
        usn: Update sequence number.
        last_sync: Last sync state.
    """

    id: int = Field(default=1, frozen=True)
    creation_time: int = Field(default_factory=lambda: int(time.time()))
    mod_time: int = Field(default_factory=lambda: int(time.time() * 1000))
    schema_mod_time: int = Field(default_factory=lambda: int(time.time() * 1000))
    version: int = Field(default=18, frozen=True)
    dirty: int = Field(default=0, ge=0)
    usn: int = Field(default=-1)
    last_sync: int = Field(default=0, ge=0)


class ConfigEntry(BaseModel):
    """A key-value configuration entry stored in the config table.

    The config table stores global settings as key-value pairs.

    Attributes:
        key: Configuration key name.
        value: Configuration value (stored as blob).
        usn: Update sequence number.
        mtime_secs: Last modification timestamp (seconds).
    """

    key: str = Field(min_length=1)
    value: bytes = Field(default=b"")
    usn: int = Field(default=-1)
    mtime_secs: int = Field(default_factory=lambda: int(time.time()))


def get_default_config_entries() -> list[ConfigEntry]:
    """Get the default configuration entries for a new collection.

    Returns:
        List of ConfigEntry objects with standard defaults.
    """
    import json

    entries = []

    # Scheduler version
    entries.append(ConfigEntry(key="schedVer", value=json.dumps(2).encode("utf-8")))

    # Scheduler 2021 mode
    entries.append(ConfigEntry(key="sched2021", value=json.dumps(True).encode("utf-8")))

    # Default sort type
    entries.append(ConfigEntry(key="sortType", value=json.dumps("noteFld").encode("utf-8")))

    # New card spread
    entries.append(ConfigEntry(key="newSpread", value=json.dumps(0).encode("utf-8")))

    # Column state (browser)
    entries.append(ConfigEntry(key="collapseTime", value=json.dumps(1200).encode("utf-8")))

    # Active decks
    entries.append(ConfigEntry(key="activeDecks", value=json.dumps([1]).encode("utf-8")))

    # Current deck
    entries.append(ConfigEntry(key="curDeck", value=json.dumps(1).encode("utf-8")))

    # Current model
    entries.append(ConfigEntry(key="curModel", value=json.dumps(None).encode("utf-8")))

    # Last unburied day
    entries.append(ConfigEntry(key="lastUnburied", value=json.dumps(0).encode("utf-8")))

    # Creation offset (timezone)
    entries.append(ConfigEntry(key="creationOffset", value=json.dumps(0).encode("utf-8")))

    # Local offset (timezone)
    entries.append(ConfigEntry(key="localOffset", value=json.dumps(0).encode("utf-8")))

    # Rollover hour (next day start)
    entries.append(ConfigEntry(key="rollover", value=json.dumps(4).encode("utf-8")))

    return entries
