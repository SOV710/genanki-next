"""ZSTD compression utilities for Anki collection files."""

from genanki_next.compression.zstd import compress_sqlite, decompress_sqlite


__all__ = ["compress_sqlite", "decompress_sqlite"]
