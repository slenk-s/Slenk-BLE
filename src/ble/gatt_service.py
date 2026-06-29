"""GATT 特征值操作"""

from src.utils.logger import setup_logger
from src.ble.signals import BleSignals
from src.ble.connector import Connector

logger = setup_logger(__name__)


class GattService:
    """BLE GATT 操作封装 —— 发现、读写、通知订阅。"""

    def __init__(self, ble_signals: BleSignals, connector: Connector):
        self._signals = ble_signals
        self._connector = connector
        self._notification_handles: dict[str, set] = {}

    async def discover_services(self, address: str) -> list:
        """发现指定设备的所有服务与特征值。"""
        client = self._connector.get_client(address)
        if not client:
            raise ConnectionError(f"设备 {address} 未连接")
        services = await client.get_services()
        result = []
        for service in services:
            svc = {
                "uuid": str(service.uuid),
                "description": service.description,
                "characteristics": [],
            }
            for char in service.characteristics:
                svc["characteristics"].append({
                    "uuid": str(char.uuid),
                    "description": char.description,
                    "properties": list(char.properties),
                })
            result.append(svc)
        self._signals.service_discovered.emit(address, result)
        return result

    async def read_characteristic(self, address: str, char_uuid: str) -> bytes:
        """读取指定特征值。"""
        client = self._connector.get_client(address)
        if not client:
            raise ConnectionError(f"设备 {address} 未连接")
        return await client.read_gatt_char(char_uuid)

    async def write_characteristic(
        self, address: str, char_uuid: str, data: bytes
    ) -> None:
        """写入指定特征值。"""
        client = self._connector.get_client(address)
        if not client:
            raise ConnectionError(f"设备 {address} 未连接")
        await client.write_gatt_char(char_uuid, data)

    async def subscribe(self, address: str, char_uuid: str) -> None:
        """订阅指定特征值的通知。"""
        client = self._connector.get_client(address)
        if not client:
            raise ConnectionError(f"设备 {address} 未连接")
        if address not in self._notification_handles:
            self._notification_handles[address] = set()
        if char_uuid in self._notification_handles[address]:
            return

        def _callback(_sender: int, data: bytes) -> None:
            self._signals.data_received.emit(address, data)

        await client.start_notify(char_uuid, _callback)
        self._notification_handles[address].add(char_uuid)

    async def unsubscribe(self, address: str, char_uuid: str) -> None:
        """取消订阅指定特征值的通知。"""
        client = self._connector.get_client(address)
        if not client:
            raise ConnectionError(f"设备 {address} 未连接")
        await client.stop_notify(char_uuid)
        self._notification_handles.get(address, set()).discard(char_uuid)
