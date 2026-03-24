# Data Models

All models are Pydantic v2 `BaseModel` subclasses defined in `src/genanki_next/models/`.

## Package (`api.py`)

The `Package` class is the high-level entry point. It wraps `SQLiteBuilder` and `APKGBuilder`.

### Constructor

```python
Package(deck_name: str = "Default")
```

- Creates a `Collection` and `SQLiteBuilder`
- If `deck_name != "Default"`, creates a new `Deck` with that name
- Always creates a Basic notetype (Front/Back fields, one template)

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `create_deck(name)` | `Deck` | Create an additional deck. Use `::` for hierarchy. |
| `create_notetype(name, fields, templates)` | `Notetype` | Create a custom notetype. `fields` is a list of field name strings. `templates` is a list of dicts with keys `name`, `qfmt`, `afmt`. |
| `create_note(fields, tags=None, notetype=None, deck_id=None)` | `Note` | Create a note with content. Uses default notetype/deck if not specified. |
| `add_note(note, deck_id=None)` | `list[Card]` | Add an existing `Note` model. Returns generated cards. |
| `write_to_file(path)` | `Path` | Build and write the `.apkg` file. Adds `.apkg` extension if missing. |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `deck_id` | `int` | Primary deck ID |
| `default_notetype` | `Notetype` | The auto-created Basic notetype |

## Note (`models/note.py`)

```python
Note(
    id: int,                    # Auto-generated (millisecond timestamp + counter)
    guid: str,                  # Auto-generated (10-char random Base91-like string)
    notetype_id: int,           # Required — reference to Notetype.id
    fields: list[str],          # Required — min 1 element
    tags: list[str] = [],       # Whitespace-stripped, empty strings removed
    mod: int,                   # Auto-generated (seconds timestamp)
    usn: int = -1,
    flags: int = 0,
)
```

Key members:
- `FIELD_SEPARATOR` (class var): `"\x1f"` — used to join fields in the database
- `sort_field` (property): First field value
- `checksum` (property): SHA-1 of first field (first 8 hex digits as int)
- `fields_joined()`: Fields joined with `\x1f`
- `tags_string()`: Tags as `" tag1 tag2 "` (Anki format)

## Notetype (`models/notetype.py`)

```python
Notetype(
    id: int,                          # Auto-generated (millisecond timestamp)
    name: str,                        # Required, min 1 char
    fields: list[Field],              # Required, min 1 — ordinals auto-set
    templates: list[Template],        # Required, min 1 — ordinals auto-set
    config: NotetypeConfig = ...,     # Default: NoteKind.NORMAL, default CSS/LaTeX
    mtime_secs: int,                  # Auto-generated (seconds timestamp)
    usn: int = -1,
)
```

`NotetypeConfig` fields: `kind` (NoteKind enum), `sort_field_idx`, `css`, `latex_pre`, `latex_post`, `latex_svg`, `reqs` (list of `CardRequirement`).

Factory: `create_basic_notetype(notetype_id=None)` — Basic type with Front/Back fields and one Card 1 template.

## Field (`models/field.py`)

```python
Field(
    name: str,                  # Required, min 1 char
    ordinal: int = 0,           # Auto-set by Notetype validator
    config: FieldConfig = ...,  # Default: Arial 20px, no RTL/sticky
)
```

`FieldConfig` fields: `sticky`, `rtl`, `font_name` ("Arial"), `font_size` (20), `description`, `plain_text`, `collapsed`, `exclude_from_search`, `prevent_deletion`.

## Template (`models/template.py`)

```python
Template(
    name: str,                      # Required, min 1 char
    ordinal: int = 0,               # Auto-set by Notetype validator
    config: TemplateConfig = ...,   # Default: {{Front}} / {{Back}}
    mtime_secs: int = 0,
    usn: int = -1,
)
```

`TemplateConfig` fields: `q_format` ("{{Front}}"), `a_format` ("{{FrontSide}}...{{Back}}"), `q_format_browser`, `a_format_browser`, `target_deck_id`, `browser_font_name`, `browser_font_size`.

## Card (`models/card.py`)

```python
Card(
    id: int,                    # Auto-generated (millisecond timestamp)
    note_id: int,               # Required
    deck_id: int,               # Required
    template_ord: int = 0,
    mod: int,                   # Auto-generated
    usn: int = -1,
    card_type: CardType = NEW,
    queue: CardQueue = NEW,
    due: int = 0,
    interval: int = 0,
    ease_factor: int = 0,       # Ease * 1000
    reps: int = 0,
    lapses: int = 0,
    left: int = 0,
    original_due: int = 0,
    original_deck_id: int = 0,
    flags: int = 0,
)
```

Factory: `Card.create_new(note_id, deck_id, template_ord=0, due_position=0)` — Creates a card in the NEW queue.

## Deck (`models/deck.py`)

```python
Deck(
    id: int,                    # Auto-generated (millisecond timestamp)
    name: str,                  # Required, min 1 char — use :: for hierarchy
    common: DeckCommon = ...,   # Study stats, collapse state
    normal: DeckNormal | None,  # None = filtered deck (not yet supported)
    mtime_secs: int,            # Auto-generated
    usn: int = -1,
)
```

- `is_filtered` (property): `True` if `normal is None`
- `DeckCommon`: `study_collapsed`, `browser_collapsed`, `last_day_studied`, `new_studied`, etc.
- `DeckNormal`: `config_id` (default 1), `extend_new`, `extend_review`, `description`, `review_limit`, `new_limit`, `desired_retention`, etc.

Factory: `create_default_deck()` — Deck with id=1, name="Default".

## DeckConfig (`models/deck_config.py`)

```python
DeckConfig(
    id: int = 1,
    name: str = "Default",
    settings: DeckConfigSettings = ...,
    mtime_secs: int,
    usn: int = 0,
)
```

`DeckConfigSettings` contains all scheduling parameters:
- Learning steps: `learn_steps` ([1.0, 10.0]), `relearn_steps` ([])
- Daily limits: `new_per_day` (20), `reviews_per_day` (200)
- Ease/interval: `initial_ease` (2.5), `easy_multiplier` (1.3), `hard_multiplier` (1.2), etc.
- Interval bounds: `maximum_review_interval` (36500), `graduating_interval_good` (1), etc.
- Card ordering: `new_card_insert_order`, `new_card_gather_priority`, `review_order`, etc.
- Leech: `leech_action` (TAG_ONLY), `leech_threshold` (8)
- Burying: `bury_new`, `bury_reviews`, `bury_interday_learning` (all False)
- Audio/timer: `disable_autoplay`, `show_timer`, `wait_for_audio`, etc.
- FSRS: `fsrs_params_4`, `fsrs_params_5`, `fsrs_params_6`, `desired_retention` (0.9)

Factory: `create_default_deck_config()` — DeckConfig with id=1.

## Collection (`models/collection.py`)

```python
Collection(
    id: int = 1,                # Frozen (singleton)
    creation_time: int,         # Auto-generated (seconds)
    mod_time: int,              # Auto-generated (milliseconds)
    schema_mod_time: int,       # Auto-generated (milliseconds)
    version: int = 18,          # Frozen
    dirty: int = 0,
    usn: int = -1,
    last_sync: int = 0,
)
```

`ConfigEntry`: Key-value pair for the `config` table (`key`, `value` as bytes, `usn`, `mtime_secs`).

`get_default_config_entries()`: Returns 12 default entries including `schedVer=2`, `sched2021=true`, `sortType="noteFld"`, `rollover=4`, etc.

## Enums (`enums.py`)

All enums are `IntEnum` subclasses:

| Enum | Values |
|------|--------|
| `CardType` | NEW(0), LEARNING(1), REVIEW(2), RELEARNING(3) |
| `CardQueue` | BURIED(-2), SUSPENDED(-1), NEW(0), LEARNING(1), REVIEW(2), DAY_LEARNING(3) |
| `NoteKind` | NORMAL(0), CLOZE(1) |
| `NewCardInsertOrder` | DUE(0), RANDOM(1) |
| `NewCardGatherPriority` | DECK(0), LOWEST_POSITION(1), HIGHEST_POSITION(2), RANDOM_NOTES(3), RANDOM_CARDS(4), DECK_THEN_RANDOM_NOTES(5) |
| `NewCardSortOrder` | TEMPLATE(0), NO_SORT(1), TEMPLATE_THEN_RANDOM(2), RANDOM_NOTE_THEN_TEMPLATE(3), RANDOM_CARD(4) |
| `ReviewCardOrder` | DAY(0), DAY_THEN_DECK(1), ..., RETRIEVABILITY_DESCENDING(11) |
| `ReviewMix` | MIX_WITH_REVIEWS(0), AFTER_REVIEWS(1), BEFORE_REVIEWS(2) |
| `LeechAction` | SUSPEND(0), TAG_ONLY(1) |
| `CardRequirementKind` | NONE(0), ANY(1), ALL(2) |
| `FilteredDeckOrder` | OLDEST_REVIEWED_FIRST(0), RANDOM(1), ..., RETRIEVABILITY_DESCENDING(9) |

## Exceptions (`exceptions.py`)

```
GenAnkiError (base)
├── ValidationError    — Data validation failures
├── DatabaseError      — SQLite database generation failures
├── CompressionError   — ZSTD compression/decompression failures
└── PackageError       — APKG package building failures
```
