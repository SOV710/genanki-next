"""APKG package builder for creating Anki deck files."""

import logging
import zipfile
from pathlib import Path

from genanki_next.compression import compress_sqlite
from genanki_next.exceptions import PackageError
from genanki_next.package.stubs import create_empty_media


logger = logging.getLogger(__name__)


class APKGBuilder:
    """Builds .apkg package files from collection data.

    An .apkg file is a ZIP archive containing:
    - collection.anki21b: ZSTD-compressed SQLite database
    - media: JSON manifest of media files (empty by default)

    Example:
        builder = APKGBuilder()
        builder.set_collection(sqlite_bytes)
        builder.build("/path/to/output.apkg")
    """

    def __init__(self) -> None:
        """Initialize an empty package builder."""
        self._collection_bytes: bytes | None = None
        self._media_bytes: bytes | None = None

    def set_collection(self, sqlite_bytes: bytes, compress: bool = True) -> None:
        """Set the collection database content.

        Args:
            sqlite_bytes: Raw SQLite database bytes.
            compress: Whether to ZSTD-compress the database. Default True.
        """
        if compress:
            self._collection_bytes = compress_sqlite(sqlite_bytes)
        else:
            self._collection_bytes = sqlite_bytes

    def set_media(self, media_bytes: bytes | None = None) -> None:
        """Set the media manifest.

        Args:
            media_bytes: Media manifest JSON bytes. Default is empty manifest.
        """
        self._media_bytes = media_bytes

    def build(self, output_path: str | Path) -> Path:
        """Build the .apkg file.

        Args:
            output_path: Path for the output .apkg file.

        Returns:
            Path to the created .apkg file.

        Raises:
            PackageError: If collection not set or build fails.
        """
        if self._collection_bytes is None:
            raise PackageError("Collection not set. Call set_collection() first.")

        output_path = Path(output_path)

        # Ensure .apkg extension
        if output_path.suffix.lower() != ".apkg":
            output_path = output_path.with_suffix(".apkg")

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Building APKG package: %s", output_path)

        try:
            with zipfile.ZipFile(
                output_path,
                mode="w",
                compression=zipfile.ZIP_STORED,  # No additional compression
            ) as zf:
                # Add collection database
                zf.writestr("collection.anki21b", self._collection_bytes)

                # Add media manifest
                media_bytes = self._media_bytes or create_empty_media()
                zf.writestr("media", media_bytes)

            logger.info("APKG package created: %s (%d bytes)", output_path, output_path.stat().st_size)

        except (OSError, zipfile.BadZipFile) as e:
            raise PackageError(f"Failed to create APKG package: {e}") from e

        return output_path


def build_apkg(
    sqlite_bytes: bytes,
    output_path: str | Path,
    compress: bool = True,
) -> Path:
    """Convenience function to build an .apkg file.

    Args:
        sqlite_bytes: Raw SQLite database bytes.
        output_path: Path for the output .apkg file.
        compress: Whether to ZSTD-compress the database.

    Returns:
        Path to the created .apkg file.
    """
    builder = APKGBuilder()
    builder.set_collection(sqlite_bytes, compress=compress)
    return builder.build(output_path)
