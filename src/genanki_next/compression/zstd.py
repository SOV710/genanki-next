"""ZSTD compression utilities for Anki collection files.

Anki v18 uses ZSTD compression for the collection.anki21b file format.
"""

import logging

import zstandard as zstd

from genanki_next.exceptions import CompressionError


logger = logging.getLogger(__name__)


def compress_sqlite(data: bytes, level: int = 3) -> bytes:
    """Compress SQLite database using ZSTD.

    Args:
        data: Raw SQLite database bytes.
        level: Compression level (1-22). Default 3 balances speed/size.
               Lower values are faster, higher values compress better.

    Returns:
        Compressed bytes suitable for .anki21b file.

    Raises:
        CompressionError: If compression fails.
    """
    if not data:
        raise CompressionError("Cannot compress empty data")

    try:
        compressor = zstd.ZstdCompressor(level=level)
        compressed = compressor.compress(data)
        logger.debug(
            "Compressed %d bytes to %d bytes (%.1f%% ratio)",
            len(data),
            len(compressed),
            len(compressed) / len(data) * 100,
        )
        return compressed
    except zstd.ZstdError as e:
        raise CompressionError(f"ZSTD compression failed: {e}") from e


def decompress_sqlite(data: bytes) -> bytes:
    """Decompress ZSTD-compressed SQLite database.

    Args:
        data: ZSTD-compressed bytes from .anki21b file.

    Returns:
        Raw SQLite database bytes.

    Raises:
        CompressionError: If decompression fails.
    """
    if not data:
        raise CompressionError("Cannot decompress empty data")

    try:
        decompressor = zstd.ZstdDecompressor()
        decompressed = decompressor.decompress(data)
        logger.debug(
            "Decompressed %d bytes to %d bytes",
            len(data),
            len(decompressed),
        )
        return decompressed
    except zstd.ZstdError as e:
        raise CompressionError(f"ZSTD decompression failed: {e}") from e
