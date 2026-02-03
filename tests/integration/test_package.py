"""Integration tests for APKG package building."""

import sqlite3
import tempfile
import zipfile
from pathlib import Path

from genanki_next import Package
from genanki_next.compression import decompress_sqlite


class TestPackageIntegration:
    """Integration tests for the Package API."""

    def test_simple_package_creation(self, tmp_path: Path) -> None:
        """Test creating a simple package with one note."""
        pkg = Package("Test Deck")
        pkg.create_note(fields=["Question", "Answer"])

        output_path = tmp_path / "test.apkg"
        result_path = pkg.write_to_file(output_path)

        assert result_path.exists()
        assert result_path.suffix == ".apkg"

    def test_package_is_valid_zip(self, tmp_path: Path) -> None:
        """Test that package is a valid ZIP file."""
        pkg = Package("Test Deck")
        pkg.create_note(fields=["Q", "A"])

        output_path = tmp_path / "test.apkg"
        pkg.write_to_file(output_path)

        # Should be a valid ZIP
        assert zipfile.is_zipfile(output_path)

        with zipfile.ZipFile(output_path, "r") as zf:
            names = zf.namelist()
            assert "collection.anki21b" in names
            assert "media" in names

    def test_package_collection_is_valid_sqlite(self, tmp_path: Path) -> None:
        """Test that collection.anki21b contains valid SQLite after decompression."""
        pkg = Package("Test Deck")
        pkg.create_note(fields=["Q", "A"])

        output_path = tmp_path / "test.apkg"
        pkg.write_to_file(output_path)

        with zipfile.ZipFile(output_path, "r") as zf:
            compressed_data = zf.read("collection.anki21b")

        # Decompress and verify it's valid SQLite
        sqlite_data = decompress_sqlite(compressed_data)
        assert sqlite_data.startswith(b"SQLite format 3")

    def test_package_with_multiple_notes(self, tmp_path: Path) -> None:
        """Test package with multiple notes."""
        pkg = Package("Vocabulary")

        words = [
            ("Hello", "Hola"),
            ("Goodbye", "Adiós"),
            ("Thank you", "Gracias"),
        ]

        for front, back in words:
            pkg.create_note(fields=[front, back])

        output_path = tmp_path / "vocab.apkg"
        pkg.write_to_file(output_path)

        # Verify notes are in database
        with zipfile.ZipFile(output_path, "r") as zf:
            compressed_data = zf.read("collection.anki21b")

        sqlite_data = decompress_sqlite(compressed_data)

        # Write to temp file and query
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            f.write(sqlite_data)
            temp_db = f.name

        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.execute("SELECT COUNT(*) FROM notes")
            count = cursor.fetchone()[0]
            conn.close()
            assert count == 3
        finally:
            Path(temp_db).unlink()

    def test_package_with_tags(self, tmp_path: Path) -> None:
        """Test package with tagged notes."""
        pkg = Package("Tagged")
        pkg.create_note(fields=["Q1", "A1"], tags=["easy", "chapter1"])
        pkg.create_note(fields=["Q2", "A2"], tags=["hard", "chapter2"])

        output_path = tmp_path / "tagged.apkg"
        pkg.write_to_file(output_path)

        # Verify tags in database
        with zipfile.ZipFile(output_path, "r") as zf:
            compressed_data = zf.read("collection.anki21b")

        sqlite_data = decompress_sqlite(compressed_data)

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            f.write(sqlite_data)
            temp_db = f.name

        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.execute("SELECT COUNT(*) FROM tags")
            count = cursor.fetchone()[0]
            conn.close()
            # Should have 4 unique tags
            assert count == 4
        finally:
            Path(temp_db).unlink()

    def test_custom_notetype(self, tmp_path: Path) -> None:
        """Test package with custom notetype."""
        pkg = Package("Custom")

        notetype = pkg.create_notetype(
            name="Vocabulary",
            fields=["Word", "Definition", "Example"],
            templates=[{
                "name": "Card 1",
                "qfmt": "{{Word}}",
                "afmt": "{{FrontSide}}<hr>{{Definition}}<br><i>{{Example}}</i>",
            }],
        )

        pkg.create_note(
            fields=["Python", "A programming language", "print('Hello')"],
            notetype=notetype,
        )

        output_path = tmp_path / "custom.apkg"
        pkg.write_to_file(output_path)

        assert output_path.exists()

    def test_database_schema_version(self, tmp_path: Path) -> None:
        """Test that database has correct schema version."""
        pkg = Package("Test")
        pkg.create_note(fields=["Q", "A"])

        output_path = tmp_path / "test.apkg"
        pkg.write_to_file(output_path)

        with zipfile.ZipFile(output_path, "r") as zf:
            compressed_data = zf.read("collection.anki21b")

        sqlite_data = decompress_sqlite(compressed_data)

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            f.write(sqlite_data)
            temp_db = f.name

        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.execute("SELECT ver FROM col WHERE id = 1")
            version = cursor.fetchone()[0]
            conn.close()
            assert version == 18
        finally:
            Path(temp_db).unlink()
