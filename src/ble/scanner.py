"""BLE 设备扫描器"""

import asyncio
from bleak import BleakScanner
from src.utils.logger import setup_logger
from src.ble.signals import BleSignals

logger = setup_logger(__name__)


class Scanner:
    """BLE 设备扫描器，封装 BleakScanner，通过 Qt 信号通知 UI。"""

    def __init__(self, ble_signals: BleSignals):
        self._signals = ble_signals
        self._scanner: BleakScanner | None = None
        self._discovered: list[dict] = []
        self._is_scanning = False

    @property
    def discovered_devices(self) -> list[dict]:
        return list(self._discovered)

    @property
    def is_scanning(self) -> bool:
        return self._is_scanning

    async def start(self, timeout: int = 10) -> None:
        """启动扫描，timeout 秒后自动停止。"""
        self._discovered.clear()
        self._is_scanning = True
        self._signals.scan_started.emit()
        logger.info("BLE scan started (timeout=%ds)", timeout)

        def _callback(device, advertisement_data):
            info = {
                "name": device.name or "Unknown",
                "address": device.address,
                "rssi": advertisement_data.rssi if advertisement_data else -100,
            }
            # 去重更新
            for i, d in enumerate(self._discovered):
                if d["address"] == info["address"]:
                    self._discovered[i] = info
                    break
            else:
                self._discovered.append(info)
            self._signals.device_found.emit(info)

        self._scanner = BleakScanner(detection_callback=_callback)
        await self._scanner.start()

        async def _auto_stop():
            await asyncio.sleep(timeout)
            self.stop()

        asyncio.create_task(_auto_stop())

    def stop(self) -> None:
        """停止扫描。"""
        if self._scanner:
            asyncio.ensure_future(self._scanner.stop())
        self._is_scanning = False
        self._signals.scan_finished.emit()
        logger.info("BLE scan finished, %d devices found", len(self._discovered))
