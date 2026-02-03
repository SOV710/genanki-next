"""Low-level protobuf message construction utilities.

This module provides primitive encoding functions for protobuf wire format.
Wire types:
  0 = Varint (int32, int64, uint32, uint64, sint32, sint64, bool, enum)
  1 = 64-bit (fixed64, sfixed64, double)
  2 = Length-delimited (string, bytes, embedded messages, packed repeated)
  5 = 32-bit (fixed32, sfixed32, float)
"""

import struct
from io import BytesIO


def encode_varint(value: int) -> bytes:
    """Encode an integer as a varint.

    Args:
        value: Non-negative integer to encode.

    Returns:
        Varint-encoded bytes.
    """
    if value < 0:
        # Handle negative values as unsigned 64-bit
        value = value & 0xFFFFFFFFFFFFFFFF

    result = bytearray()
    while value > 127:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


def encode_tag(field_number: int, wire_type: int) -> bytes:
    """Encode a field tag (field_number << 3 | wire_type).

    Args:
        field_number: Protobuf field number.
        wire_type: Wire type (0=varint, 1=64-bit, 2=length-delimited, 5=32-bit).

    Returns:
        Tag encoded as varint.
    """
    return encode_varint((field_number << 3) | wire_type)


def encode_uint32(field_number: int, value: int) -> bytes:
    """Encode a uint32 field.

    Args:
        field_number: Protobuf field number.
        value: Unsigned 32-bit integer value.

    Returns:
        Encoded field bytes.
    """
    if value == 0:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 0) + encode_varint(value)


def encode_int32(field_number: int, value: int) -> bytes:
    """Encode an int32 field.

    Args:
        field_number: Protobuf field number.
        value: Signed 32-bit integer value.

    Returns:
        Encoded field bytes.
    """
    if value == 0:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 0) + encode_varint(value)


def encode_int64(field_number: int, value: int) -> bytes:
    """Encode an int64 field.

    Args:
        field_number: Protobuf field number.
        value: Signed 64-bit integer value.

    Returns:
        Encoded field bytes.
    """
    if value == 0:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 0) + encode_varint(value)


def encode_bool(field_number: int, value: bool) -> bytes:
    """Encode a bool field.

    Args:
        field_number: Protobuf field number.
        value: Boolean value.

    Returns:
        Encoded field bytes.
    """
    if not value:
        return b""  # Default value (false), omit from wire
    return encode_tag(field_number, 0) + b"\x01"


def encode_enum(field_number: int, value: int) -> bytes:
    """Encode an enum field (same as int32).

    Args:
        field_number: Protobuf field number.
        value: Enum value (integer).

    Returns:
        Encoded field bytes.
    """
    if value == 0:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 0) + encode_varint(value)


def encode_float(field_number: int, value: float) -> bytes:
    """Encode a float field (wire type 5, 32-bit).

    Args:
        field_number: Protobuf field number.
        value: Float value.

    Returns:
        Encoded field bytes.
    """
    if value == 0.0:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 5) + struct.pack("<f", value)


def encode_double(field_number: int, value: float) -> bytes:
    """Encode a double field (wire type 1, 64-bit).

    Args:
        field_number: Protobuf field number.
        value: Double value.

    Returns:
        Encoded field bytes.
    """
    if value == 0.0:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 1) + struct.pack("<d", value)


def encode_string(field_number: int, value: str) -> bytes:
    """Encode a string field (length-delimited).

    Args:
        field_number: Protobuf field number.
        value: String value.

    Returns:
        Encoded field bytes.
    """
    if not value:
        return b""  # Default value, omit from wire
    encoded = value.encode("utf-8")
    return encode_tag(field_number, 2) + encode_varint(len(encoded)) + encoded


def encode_bytes(field_number: int, value: bytes) -> bytes:
    """Encode a bytes field (length-delimited).

    Args:
        field_number: Protobuf field number.
        value: Bytes value.

    Returns:
        Encoded field bytes.
    """
    if not value:
        return b""  # Default value, omit from wire
    return encode_tag(field_number, 2) + encode_varint(len(value)) + value


def encode_embedded_message(field_number: int, message_bytes: bytes) -> bytes:
    """Encode an embedded message (length-delimited).

    Args:
        field_number: Protobuf field number.
        message_bytes: Already-serialized message bytes.

    Returns:
        Encoded field bytes.
    """
    if not message_bytes:
        return b""  # Empty message, omit from wire
    return encode_tag(field_number, 2) + encode_varint(len(message_bytes)) + message_bytes


def encode_packed_floats(field_number: int, values: list[float]) -> bytes:
    """Encode a packed repeated float field.

    Args:
        field_number: Protobuf field number.
        values: List of float values.

    Returns:
        Encoded field bytes.
    """
    if not values:
        return b""  # Empty list, omit from wire
    packed = b"".join(struct.pack("<f", v) for v in values)
    return encode_tag(field_number, 2) + encode_varint(len(packed)) + packed


def encode_packed_uint32(field_number: int, values: list[int]) -> bytes:
    """Encode a packed repeated uint32 field.

    Args:
        field_number: Protobuf field number.
        values: List of uint32 values.

    Returns:
        Encoded field bytes.
    """
    if not values:
        return b""  # Empty list, omit from wire
    packed = b"".join(encode_varint(v) for v in values)
    return encode_tag(field_number, 2) + encode_varint(len(packed)) + packed


class MessageBuilder:
    """Helper class for building protobuf messages."""

    def __init__(self) -> None:
        """Initialize an empty message builder."""
        self._buffer = BytesIO()

    def add_uint32(self, field_number: int, value: int) -> "MessageBuilder":
        """Add a uint32 field."""
        self._buffer.write(encode_uint32(field_number, value))
        return self

    def add_int32(self, field_number: int, value: int) -> "MessageBuilder":
        """Add an int32 field."""
        self._buffer.write(encode_int32(field_number, value))
        return self

    def add_int64(self, field_number: int, value: int) -> "MessageBuilder":
        """Add an int64 field."""
        self._buffer.write(encode_int64(field_number, value))
        return self

    def add_bool(self, field_number: int, value: bool) -> "MessageBuilder":
        """Add a bool field."""
        self._buffer.write(encode_bool(field_number, value))
        return self

    def add_enum(self, field_number: int, value: int) -> "MessageBuilder":
        """Add an enum field."""
        self._buffer.write(encode_enum(field_number, value))
        return self

    def add_float(self, field_number: int, value: float) -> "MessageBuilder":
        """Add a float field."""
        self._buffer.write(encode_float(field_number, value))
        return self

    def add_double(self, field_number: int, value: float) -> "MessageBuilder":
        """Add a double field."""
        self._buffer.write(encode_double(field_number, value))
        return self

    def add_string(self, field_number: int, value: str) -> "MessageBuilder":
        """Add a string field."""
        self._buffer.write(encode_string(field_number, value))
        return self

    def add_bytes(self, field_number: int, value: bytes) -> "MessageBuilder":
        """Add a bytes field."""
        self._buffer.write(encode_bytes(field_number, value))
        return self

    def add_message(self, field_number: int, message_bytes: bytes) -> "MessageBuilder":
        """Add an embedded message field."""
        self._buffer.write(encode_embedded_message(field_number, message_bytes))
        return self

    def add_packed_floats(self, field_number: int, values: list[float]) -> "MessageBuilder":
        """Add a packed repeated float field."""
        self._buffer.write(encode_packed_floats(field_number, values))
        return self

    def add_packed_uint32(self, field_number: int, values: list[int]) -> "MessageBuilder":
        """Add a packed repeated uint32 field."""
        self._buffer.write(encode_packed_uint32(field_number, values))
        return self

    def build(self) -> bytes:
        """Build the final message bytes."""
        return self._buffer.getvalue()
