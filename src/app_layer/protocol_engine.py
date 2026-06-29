"""协议引擎 —— 按设备地址管理协议解析器实例（策略模式）。"""

from src.app_layer.protocols.base import ParsedData, ProtocolParser


class ProtocolEngine:
    """按设备管理协议解析器实例。

    用法::

        engine = ProtocolEngine()
        engine.register_parser("my_proto", MyParser)
        engine.set_parser("AA:BB:CC:DD:EE:FF", "my_proto")
        result = engine.parse("AA:BB:CC:DD:EE:FF", b"\\x01\\x02")
    """

    def __init__(self) -> None:
        self._parsers: dict[str, ProtocolParser] = {}
        self._available: dict[str, type[ProtocolParser]] = {}

    def register_parser(self, name: str, parser_cls: type[ProtocolParser]) -> None:
        """注册一种协议解析器类，后续可通过 set_parser 按名实例化。"""
        self._available[name] = parser_cls

    def set_parser(self, address: str, parser_name: str) -> bool:
        """为指定设备地址设置解析器。

        返回 True 表示成功，False 表示 parser_name 未注册。
        """
        cls = self._available.get(parser_name)
        if not cls:
            return False
        self._parsers[address] = cls()
        return True

    def parse(self, address: str, raw_data: bytes) -> ParsedData:
        """解析原始数据。

        若该设备有注册解析器则使用之，否则返回无字段的基本 ParsedData。
        """
        parser = self._parsers.get(address)
        if parser:
            return parser.parse(raw_data)
        return ParsedData(
            raw=raw_data,
            hex_str=raw_data.hex(" ").upper(),
            ascii_str=raw_data.decode("ascii", errors="replace"),
        )

    def serialize(self, address: str, data: dict) -> bytes:
        """将结构化数据序列化为字节。

        若该设备无解析器则抛出 ValueError。
        """
        parser = self._parsers.get(address)
        if parser:
            return parser.serialize(data)
        raise ValueError(f"设备 {address} 未设置协议解析器")