"""多设备 BLE 连接管理器"""

from bleak import BleakClient
from src.utils.logger import setup_logger
from src.ble.signals import BleSignals

logger = setup_logger(__name__)


class Connector:
    """BLE 连接池 —— 管理多个设备连接。"""

    def __init__(self, ble_signals: BleSignals, max_connections: int = 5):
        self._signals = ble_signals
        self.max_connections = max_connections
        self._clients: dict[str, BleakClient] = {}

    @property
    def connected_devices(self) -> list[dict]:
        return [
            {"address": addr, "name": client.address}
            for addr, client in self._clients.items()
        ]

    def is_connected(self, address: str) -> bool:
        return address in self._clients and self._clients[address].is_connected

    def _at_max_capacity(self) -> bool:
        return len(self._clients) >= self.max_connections

    async def connect(self, address: str, timeout: float = 10.0) -> bool:
        if self._at_max_capacity():
            msg = f"已达最大连接数 ({self.max_connections})，无法连接 {address}"
            self._signals.error_occurred.emit(msg)
            logger.warning(msg)
            return False
        if self.is_connected(address):
            return True
        try:
            client = BleakClient(address, timeout=timeout)
            await client.connect()
            self._clients[address] = client
            self._signals.device_connected.emit(address)
            return True
        except Exception as e:
            self._signals.connection_failed.emit(address, str(e))
            logger.error("连接设备 %s 失败: %s", address, e)
            return False

    async def disconnect(self, address: str) -> bool:
        client = self._clients.pop(address, None)
        if client is None:
            return False
        try:
            await client.disconnect()
        except Exception as e:
            logger.warning("断开 %s 时发生异常: %s", address, e)
        self._signals.device_disconnected.emit(address)
        return True

    async def disconnect_all(self) -> None:
        for addr in list(self._clients.keys()):
            await self.disconnect(addr)

    def get_client(self, address: str) -> BleakClient | None:
        return self._clients.get(address)