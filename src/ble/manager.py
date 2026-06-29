"""BLE Manager — 统一编排 Scanner / Connector / GattService"""

from src.ble.signals import BleSignals
from src.ble.scanner import Scanner
from src.ble.connector import Connector
from src.ble.gatt_service import GattService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BLEManager:
    """与 BLE 通信层之间的统一入口。"""

    def __init__(self, signals: BleSignals | None = None):
        self.signals = signals or BleSignals()
        self.scanner = Scanner(self.signals)
        self.connector = Connector(self.signals)
        self.gatt = GattService(self.signals, self.connector)
        logger.info("BLE Manager 初始化完成")

    async def shutdown(self):
        await self.connector.disconnect_all()
        if self.scanner.is_scanning:
            await self.scanner.stop()
        logger.info("BLE Manager 已关闭")