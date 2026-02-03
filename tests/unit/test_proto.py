"""Unit tests for protobuf encoding."""


from genanki_next.models import DeckConfig, Field, Notetype, Template
from genanki_next.proto import (
    build_deck_config_blob,
    build_field_config_blob,
    build_notetype_config_blob,
    build_template_config_blob,
)
from genanki_next.proto.messages import (
    MessageBuilder,
    encode_varint,
)


class TestVarintEncoding:
    """Tests for varint encoding."""

    def test_encode_small_int(self) -> None:
        """Test encoding small integers."""
        assert encode_varint(0) == b"\x00"
        assert encode_varint(1) == b"\x01"
        assert encode_varint(127) == b"\x7f"

    def test_encode_larger_int(self) -> None:
        """Test encoding larger integers."""
        assert encode_varint(128) == b"\x80\x01"
        assert encode_varint(300) == b"\xac\x02"


class TestMessageBuilder:
    """Tests for MessageBuilder."""

    def test_empty_message(self) -> None:
        """Test building empty message."""
        builder = MessageBuilder()
        assert builder.build() == b""

    def test_add_uint32(self) -> None:
        """Test adding uint32 field."""
        builder = MessageBuilder()
        builder.add_uint32(1, 150)
        result = builder.build()
        # Field 1, wire type 0 (varint) = tag 0x08
        # 150 = 0x96 0x01 (varint)
        assert result == b"\x08\x96\x01"

    def test_add_bool_true(self) -> None:
        """Test adding true boolean."""
        builder = MessageBuilder()
        builder.add_bool(1, True)
        result = builder.build()
        assert result == b"\x08\x01"

    def test_add_bool_false(self) -> None:
        """Test adding false boolean (omitted)."""
        builder = MessageBuilder()
        builder.add_bool(1, False)
        result = builder.build()
        assert result == b""  # Default value omitted

    def test_add_string(self) -> None:
        """Test adding string field."""
        builder = MessageBuilder()
        builder.add_string(1, "test")
        result = builder.build()
        # Field 1, wire type 2 (length-delimited) = tag 0x0a
        # Length 4, then "test"
        assert result == b"\x0a\x04test"


class TestBlobBuilders:
    """Tests for high-level blob builders."""

    def test_build_deck_config_blob(self) -> None:
        """Test building deck config protobuf."""
        config = DeckConfig()
        blob = build_deck_config_blob(config)
        assert isinstance(blob, bytes)
        assert len(blob) > 0

    def test_build_notetype_config_blob(self, basic_notetype: Notetype) -> None:
        """Test building notetype config protobuf."""
        blob = build_notetype_config_blob(basic_notetype)
        assert isinstance(blob, bytes)
        # Should contain CSS
        assert len(blob) > 0

    def test_build_field_config_blob(self) -> None:
        """Test building field config protobuf."""
        field = Field(name="Test")
        blob = build_field_config_blob(field)
        assert isinstance(blob, bytes)
        # Should contain font_name "Arial"
        assert b"Arial" in blob

    def test_build_template_config_blob(self) -> None:
        """Test building template config protobuf."""
        template = Template(name="Card 1")
        blob = build_template_config_blob(template)
        assert isinstance(blob, bytes)
        # Should contain template format
        assert b"{{Front}}" in blob
