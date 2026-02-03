"""Stub implementations for media and meta files.

These are placeholder implementations that will be expanded
when media file support is added.
"""


def create_empty_media() -> bytes:
    """Create an empty media manifest.

    The media file is a JSON object mapping media IDs to filenames.
    An empty collection has no media files.

    Returns:
        UTF-8 encoded empty JSON object.
    """
    return b"{}"


def create_empty_meta() -> bytes:
    """Create an empty meta file stub.

    The meta file contains package metadata. For basic packages,
    this can be empty or omitted entirely.

    Returns:
        Empty bytes (meta file is optional for basic import).
    """
    return b""
