"""Tests for ProtocolParser base and ProtocolEngine — 协议引擎 + 基类。"""

from dataclasses import dataclass

import pytest

from src.app_layer.protocols.base import ParsedData, ProtocolParser
from src.app_layer.protocol_engine import ProtocolEngine


# ── helpers ──────────────────────────────────────────────────────────────

class MockSensorParser(ProtocolParser):
    """Fake parser that splits raw bytes into "temperature-like" fields."""

    @property
    def name(self) -> str:
        return "mock_sensor"

    def parse(self, raw_data: bytes) -> ParsedData:
        fields = {
            "length": len(raw_data),
            "first_byte": raw_data[0] if raw_data else 0,
        }
        return ParsedData(
            raw=raw_data,
            hex_str=raw_data.hex(" ").upper(),
            ascii_str=raw_data.decode("ascii", errors="replace"),
            fields=fields,
            description="Mock sensor data",
        )

    def serialize(self, data: dict) -> bytes:
        return bytes([data.get("first_byte", 0)])


# ── ParsedData ───────────────────────────────────────────────────────────

class TestParsedData:
    def test_minimal_construction(self) -> None:
        pd = ParsedData(raw=b"\x01\x02", hex_str="01 02", ascii_str="..")
        assert pd.raw == b"\x01\x02"
        assert pd.hex_str == "01 02"
        assert pd.ascii_str == ".."
        assert pd.fields == {}
        assert pd.description == ""
        assert pd.errors == []

    def test_full_construction(self) -> None:
        pd = ParsedData(
            raw=b"hello",
            hex_str="68 65 6C 6C 6F",
            ascii_str="hello",
            fields={"key": "val"},
            description="test",
            errors=["err1"],
        )
        assert pd.fields == {"key": "val"}
        assert pd.description == "test"
        assert pd.errors == ["err1"]

    def test_immutable_like(self) -> None:
        pd = ParsedData(raw=b"\x00", hex_str="00", ascii_str=".")
        with pytest.raises(AttributeError):
            pd.raw = b"\x01"


class TestProtocolParserABC:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            ProtocolParser()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        parser = MockSensorParser()
        assert parser.name == "mock_sensor"


class TestMockParser:
    def test_parse_returns_parsed_data(self) -> None:
        parser = MockSensorParser()
        result = parser.parse(b"\x41\x42")
        assert isinstance(result, ParsedData)
        assert result.fields["length"] == 2
        assert result.fields["first_byte"] == 0x41
        assert result.description == "Mock sensor data"

    def test_serialize(self) -> None:
        parser = MockSensorParser()
        assert parser.serialize({"first_byte": 0x42}) == b"\x42"

    def test_parse_empty_bytes(self) -> None:
        parser = MockSensorParser()
        result = parser.parse(b"")
        assert result.fields["length"] == 0
        assert result.fields["first_byte"] == 0


# ── ProtocolEngine ──────────────────────────────────────────────────────

class TestProtocolEngine:
    def test_register_and_set_parser(self) -> None:
        engine = ProtocolEngine()
        engine.register_parser("mock", MockSensorParser)
        assert engine.set_parser("AA:BB:CC:DD:EE:FF", "mock") is True

    def test_set_parser_unknown_name(self) -> None:
        engine = ProtocolEngine()
        assert engine.set_parser("AA:BB:CC:DD:EE:FF", "nonexistent") is False

    def test_parse_with_parser(self) -> None:
        engine = ProtocolEngine()
        engine.register_parser("mock", MockSensorParser)
        engine.set_parser("11:22:33:44:55:66", "mock")

        result = engine.parse("11:22:33:44:55:66", b"\x41\x42")
        assert result.fields["first_byte"] == 0x41
        assert result.description == "Mock sensor data"

    def test_parse_without_parser_returns_basic(self) -> None:
        engine = ProtocolEngine()
        result = engine.parse("unregistered", b"\xDE\xAD")
        assert result.raw == b"\xDE\xAD"
        assert "DE AD" in result.hex_str
        assert result.fields == {}
        assert result.errors == []

    def test_serialize_with_parser(self) -> None:
        engine = ProtocolEngine()
        engine.register_parser("mock", MockSensorParser)
        engine.set_parser("AA:BB:CC:DD:EE:FF", "mock")
        assert engine.serialize("AA:BB:CC:DD:EE:FF", {"first_byte": 0x99}) == b"\x99"

    def test_serialize_without_parser_raises(self) -> None:
        engine = ProtocolEngine()
        with pytest.raises(ValueError, match="未设置协议解析器"):
            engine.serialize("nobody", {})

    def test_multiple_devices_independent_parsers(self) -> None:
        engine = ProtocolEngine()
        engine.register_parser("mock", MockSensorParser)
        engine.set_parser("dev-a", "mock")
        engine.set_parser("dev-b", "mock")

        result_a = engine.parse("dev-a", b"\x01")
        result_b = engine.parse("dev-b", b"\x02")
        assert result_a.fields["first_byte"] == 0x01
        assert result_b.fields["first_byte"] == 0x02

    def test_set_parser_replaces_existing(self) -> None:
        engine = ProtocolEngine()
        engine.register_parser("mock", MockSensorParser)
        engine.set_parser("addr", "mock")
        # Set again — should replace without error
        assert engine.set_parser("addr", "mock") is True
        result = engine.parse("addr", b"\xFF")
        assert result.fields["first_byte"] == 0xFF
