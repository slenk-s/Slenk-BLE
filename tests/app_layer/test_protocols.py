"""Tests for built-in protocol parsers: Raw/JSON/Modbus. 内置协议解析器测试。"""

import json
import struct

import pytest

from src.app_layer.protocols.base import ParsedData
from src.app_layer.protocols.json_proto import JSONProtocol
from src.app_layer.protocols.modbus import ModbusProtocol
from src.app_layer.protocols.raw import RawProtocol


# ── RawProtocol ──────────────────────────────────────────────────────────


class TestRawProtocol:
    def test_name(self) -> None:
        assert RawProtocol.name == "Raw HEX"

    def test_parse_simple(self) -> None:
        p = RawProtocol()
        result = p.parse(b"\x01\x02\x03")
        assert isinstance(result, ParsedData)
        assert result.hex_str == "01 02 03"
        assert result.description == "3 bytes"

    def test_parse_empty(self) -> None:
        p = RawProtocol()
        result = p.parse(b"")
        assert result.hex_str == ""
        assert result.description == "0 bytes"

    def test_parse_ascii_decode(self) -> None:
        p = RawProtocol()
        result = p.parse(b"hello")
        assert result.ascii_str == "hello"

    def test_parse_non_ascii_replaced(self) -> None:
        p = RawProtocol()
        result = p.parse(b"\xff\xfe")
        assert "�" in result.ascii_str or "?" in result.ascii_str

    def test_serialize(self) -> None:
        p = RawProtocol()
        assert p.serialize({"hex": "01 02 03"}) == b"\x01\x02\x03"

    def test_serialize_no_spaces(self) -> None:
        p = RawProtocol()
        assert p.serialize({"hex": "010203"}) == b"\x01\x02\x03"

    def test_serialize_empty(self) -> None:
        p = RawProtocol()
        assert p.serialize({"hex": ""}) == b""


# ── JSONProtocol ─────────────────────────────────────────────────────────


class TestJSONProtocol:
    def test_name(self) -> None:
        assert JSONProtocol.name == "JSON"

    def test_parse_valid_object(self) -> None:
        p = JSONProtocol()
        result = p.parse(b'{"key": "value", "num": 42}')
        assert result.fields == {"key": "value", "num": 42}
        assert "key" in result.description

    def test_parse_valid_array(self) -> None:
        p = JSONProtocol()
        result = p.parse(b'[1, 2, 3]')
        assert result.fields == {"value": [1, 2, 3]}

    def test_parse_valid_scalar(self) -> None:
        p = JSONProtocol()
        result = p.parse(b'"hello"')
        assert result.fields == {"value": "hello"}

    def test_parse_invalid_json(self) -> None:
        p = JSONProtocol()
        result = p.parse(b"not json")
        assert len(result.errors) == 1

    def test_parse_non_utf8(self) -> None:
        p = JSONProtocol()
        result = p.parse(b"\xff\xfe")
        assert len(result.errors) >= 1

    def test_serialize(self) -> None:
        p = JSONProtocol()
        result = p.serialize({"a": 1, "b": "two"})
        assert json.loads(result) == {"a": 1, "b": "two"}

    def test_hex_str_on_valid(self) -> None:
        p = JSONProtocol()
        result = p.parse(b'"x"')
        assert len(result.hex_str) > 0


# ── ModbusProtocol ───────────────────────────────────────────────────────


def _crc16(data: bytes) -> int:
    """Reference CRC16-Modbus implementation for test assertions."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


class TestModbusProtocol:
    def test_name(self) -> None:
        assert ModbusProtocol.name == "Modbus RTU"

    def test_parse_valid_frame(self) -> None:
        """Address=0x11, Function=0x03, data=0x00 0x6B, proper CRC."""
        addr_func_data = bytes([0x11, 0x03, 0x00, 0x6B])
        crc = _crc16(addr_func_data)
        frame = addr_func_data + struct.pack("<H", crc)

        p = ModbusProtocol()
        result = p.parse(frame)
        assert result.fields["address"] == 0x11
        assert result.fields["function_code"] == 0x03
        assert result.fields["crc_ok"] is True
        assert result.errors == []

    def test_parse_with_crc_fail(self) -> None:
        # Frame with deliberately wrong CRC (all zeros instead of computed value)
        frame = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])
        p = ModbusProtocol()
        result = p.parse(frame)
        assert result.fields["crc_ok"] is False
        assert len(result.errors) == 1
        assert "CRC" in result.errors[0]

    def test_parse_too_short(self) -> None:
        p = ModbusProtocol()
        result = p.parse(b"\x01\x02\x03")
        assert len(result.errors) == 1
        assert "bytes" in result.errors[0]

    def test_parse_empty(self) -> None:
        p = ModbusProtocol()
        result = p.parse(b"")
        assert len(result.errors) == 1

    def test_serialize(self) -> None:
        p = ModbusProtocol()
        result = p.serialize({"address": 0x11, "function_code": 0x03, "data": "00 6B"})
        assert len(result) == 6
        assert result[0] == 0x11
        assert result[1] == 0x03
        assert result[2] == 0x00
        assert result[3] == 0x6B
        # Verify CRC
        calc_crc = _crc16(result[:-2])
        recv_crc = struct.unpack("<H", result[-2:])[0]
        assert calc_crc == recv_crc

    def test_serialize_defaults(self) -> None:
        p = ModbusProtocol()
        result = p.serialize({"data": ""})
        assert result[0] == 1  # default address
        assert result[1] == 3  # default function code

    def test_roundtrip(self) -> None:
        p = ModbusProtocol()
        original = {"address": 0x0A, "function_code": 0x10, "data": "12 34 AB CD"}
        serialized = p.serialize(original)
        parsed = p.parse(serialized)
        assert parsed.fields["address"] == 0x0A
        assert parsed.fields["function_code"] == 0x10
        assert parsed.fields["crc_ok"] is True

