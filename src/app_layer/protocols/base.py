"""协议解析器基类 —— ProtocolParser ABC & ParsedData 数据类。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParsedData:
    """解析结果数据类。"""

    raw: bytes
    hex_str: str
    ascii_str: str
    fields: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    errors: list[str] = field(default_factory=list)


class ProtocolParser(ABC):
    """协议解析器抽象基类。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """解析器唯一名称。"""

    @abstractmethod
    def parse(self, raw_data: bytes) -> ParsedData:
        """将原始字节解析为结构化数据。"""

    @abstractmethod
    def serialize(self, data: dict[str, Any]) -> bytes:
        """将结构化数据序列化为原始字节。"""