"""src/ui/main_window.py"""

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QTabWidget, QStatusBar
from src.ui.device_panel import DevicePanel
from src.ui.tabs.data_tab import DataTab
from src.ui.tabs.chart_tab import ChartTab
from src.ui.tabs.log_tab import LogTab
from src.ui.tabs.protocol_tab import ProtocolTab
from src.ui.tabs.ota_tab import OtaTab
from src.ble.manager import BLEManager


class MainWindow(QMainWindow):
    def __init__(self, ble_manager: BLEManager | None = None):
        super().__init__()
        self.ble = ble_manager or BLEManager()
        self._init_ui()
        self._setup_signals()

    def _init_ui(self):
        self.setWindowTitle("蓝牙上位机 v0.1")
        self.resize(1200, 800)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        self.device_panel = DevicePanel(self.ble)
        layout.addWidget(self.device_panel, 1)

        self.tabs = QTabWidget()
        self.tabs.addTab(DataTab(self.ble), "数据")
        self.tabs.addTab(ChartTab(self.ble), "图表")
        self.tabs.addTab(LogTab(self.ble), "日志")
        self.tabs.addTab(ProtocolTab(self.ble), "协议")
        self.tabs.addTab(OtaTab(self.ble), "OTA")
        layout.addWidget(self.tabs, 3)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("BLE: 就绪")

    def _setup_signals(self):
        self.ble.signals.scan_started.connect(lambda: self.status.showMessage("扫描中..."))
        self.ble.signals.scan_finished.connect(
            lambda: self.status.showMessage(f"扫描完成，发现 {len(self.ble.scanner.discovered_devices)} 个设备")
        )
