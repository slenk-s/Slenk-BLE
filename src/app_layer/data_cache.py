"""src/app_layer/data_cache.py"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DataPoint:
    timestamp: datetime
    address: str
    raw_data: bytes
    parsed: Optional[dict] = None


class DataCache:
    """每个设备一个数据通道的环形缓冲区。"""

    def __init__(self, max_size: int = 10_000):
        self.max_size = max_size
        self._channels: dict[str, list[DataPoint]] = defaultdict(list)

    def push(self, address: str, data: bytes, parsed: dict | None = None) -> None:
        channel = self._channels[address]
        channel.append(
            DataPoint(
                timestamp=datetime.now(),
                address=address,
                raw_data=data,
                parsed=parsed,
            )
        )
        if len(channel) > self.max_size:
            channel.pop(0)

    def get_channel(self, address: str, limit: int = 100) -> list[DataPoint]:
        return self._channels.get(address, [])[-limit:]

    def get_all(self, limit: int = 100) -> list[DataPoint]:
        all_points = []
        for channel in self._channels.values():
            all_points.extend(channel[-limit:])
        return sorted(all_points, key=lambda p: p.timestamp, reverse=True)[:limit]

    def clear(self, address: str | None = None) -> None:
        if address:
            self._channels.pop(address, None)
        else:
            self._channels.clear()

    def device_count(self) -> int:
        return len(self._channels)
