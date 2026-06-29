"""Modbus RTU protocol parser — Modbus RTU 协议解析器。"""

import struct

from .base import ProtocolParser, ParsedData


class ModbusProtocol(ProtocolParser):
    """Modbus RTU protocol — parses Modbus frames with CRC16 validation."""

    name = "Modbus RTU"

    def _crc16(self, data: bytes) -> int:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def parse(self, raw_data: bytes) -> ParsedData:
        if len(raw_data) < 5:
            return ParsedData(
                raw=raw_data,
                hex_str=raw_data.hex(" ").upper(),
                ascii_str="",
                errors=["帧长度不足 (< 5 bytes)"],
            )
        calc_crc = self._crc16(raw_data[:-2])
        recv_crc = struct.unpack("<H", raw_data[-2:])[0]
        crc_ok = calc_crc == recv_crc
        errors = []
        if not crc_ok:
            errors.append("CRC 校验失败")
        return ParsedData(
            raw=raw_data,
            hex_str=raw_data.hex(" ").upper(),
            ascii_str="",
            fields={
                "address": raw_data[0],
                "function_code": raw_data[1],
                "data": raw_data[2:-2].hex(" ").upper(),
                "crc_ok": crc_ok,
            },
            description=(
                f"Addr={raw_data[0]:#04x} Func={raw_data[1]:#04x} "
                f"CRC={'OK' if crc_ok else 'FAIL'}"
            ),
            errors=errors,
        )

    def serialize(self, data: dict) -> bytes:
        addr = data.get("address", 1)
        func = data.get("function_code", 3)
        payload = data.get("data", "")
        raw = bytes([addr, func]) + bytes.fromhex(payload.replace(" ", ""))
        crc = self._crc16(raw)
        return raw + struct.pack("<H", crc)
