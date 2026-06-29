"""BLE 层与 UI 层之间的 Qt 信号桥接"""

from PySide6.QtCore import QObject, Signal


class BleSignals(QObject):
    """BLE 事件信号 —— 在 asyncio 线程发射，UI 线程安全接收。"""

    device_found = Signal(object)              # device_info dict
    device_connected = Signal(str)             # address
    device_disconnected = Signal(str)          # address
    data_received = Signal(str, bytes)         # (address, raw_data)
    connection_failed = Signal(str, str)       # (address, reason)
    scan_started = Signal()
    scan_finished = Signal()
    error_occurred = Signal(str)               # error_message
    service_discovered = Signal(str, list)     # (address, services)