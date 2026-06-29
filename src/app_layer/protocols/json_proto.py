"""JSON protocol parser — JSON 协议解析器。"""

import json

from .base import ProtocolParser, ParsedData


class JSONProtocol(ProtocolParser):
    """JSON protocol — parses UTF-8 JSON payloads into structured fields."""

    name = "JSON"

    def parse(self, raw_data: bytes) -> ParsedData:
        try:
            obj = json.loads(raw_data.decode("utf-8"))
            fields = obj if isinstance(obj, dict) else {"value": obj}
            description = json.dumps(obj, ensure_ascii=False)
            return ParsedData(
                raw=raw_data,
                hex_str=raw_data.hex(" ").upper(),
                ascii_str="",
                fields=fields,
                description=description,
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return ParsedData(
                raw=raw_data,
                hex_str=raw_data.hex(" ").upper(),
                ascii_str="",
                errors=[str(e)],
            )

    def serialize(self, data: dict) -> bytes:
        return json.dumps(data).encode("utf-8")
