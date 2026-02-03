"""Unit tests for ZSTD compression."""

import pytest

from genanki_next.compression import compress_sqlite, decompress_sqlite
from genanki_next.exceptions import CompressionError


class TestCompression:
    """Tests for ZSTD compression."""

    def test_compress_decompress_roundtrip(self) -> None:
        """Test that compression and decompression are inverse operations."""
        original = b"Hello, World! This is a test of ZSTD compression."
        compressed = compress_sqlite(original)
        decompressed = decompress_sqlite(compressed)
        assert decompressed == original

    def test_compress_reduces_size(self) -> None:
        """Test that compression reduces data size for compressible content."""
        # Create some repetitive content that compresses well
        original = b"The quick brown fox " * 100
        compressed = compress_sqlite(original)
        assert len(compressed) < len(original)

    def test_compress_empty_raises(self) -> None:
        """Test that compressing empty data raises error."""
        with pytest.raises(CompressionError):
            compress_sqlite(b"")

    def test_decompress_empty_raises(self) -> None:
        """Test that decompressing empty data raises error."""
        with pytest.raises(CompressionError):
            decompress_sqlite(b"")

    def test_decompress_invalid_raises(self) -> None:
        """Test that decompressing invalid data raises error."""
        with pytest.raises(CompressionError):
            decompress_sqlite(b"not valid zstd data")

    def test_compression_levels(self) -> None:
        """Test different compression levels."""
        original = b"Test data " * 100

        # Level 1 (fastest)
        compressed_1 = compress_sqlite(original, level=1)

        # Level 10 (better compression)
        compressed_10 = compress_sqlite(original, level=10)

        # Both should decompress correctly
        assert decompress_sqlite(compressed_1) == original
        assert decompress_sqlite(compressed_10) == original

        # Higher level should generally compress better
        # (though not guaranteed for all inputs)
        assert len(compressed_10) <= len(compressed_1)
