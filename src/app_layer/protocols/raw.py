"""Raw HEX protocol parser — 原始十六进制解析器。"""

from .base import ProtocolParser, ParsedData


class RawProtocol(ProtocolParser):
    """Raw HEX protocol — treats any bytes as raw hex and ASCII display."""

    name = "Raw HEX"

    def parse(self, raw_data: bytes) -> ParsedData:
        return ParsedData(
            raw=raw_data,
            hex_str=raw_data.hex(" ").upper(),
            ascii_str=raw_data.decode("ascii", errors="replace"),
            description=f"{len(raw_data)} bytes",
        )

    def serialize(self, data: dict) -> bytes:
        hex_str = data.get("hex", "")
        return bytes.fromhex(hex_str.replace(" ", ""))
