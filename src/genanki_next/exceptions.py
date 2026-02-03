"""Custom exception hierarchy for genanki-next."""


class GenAnkiError(Exception):
    """Base exception for all genanki-next errors."""


class ValidationError(GenAnkiError):
    """Raised when data validation fails."""


class DatabaseError(GenAnkiError):
    """Raised when SQLite database generation fails."""


class CompressionError(GenAnkiError):
    """Raised when ZSTD compression or decompression fails."""


class PackageError(GenAnkiError):
    """Raised when APKG package building fails."""
