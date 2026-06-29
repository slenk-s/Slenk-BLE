"""src/ui/device_panel.py"""

import asyncio
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                                QHBoxLayout, QListWidget, QListWidgetItem)


class DevicePanel(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        btn_row = QHBoxLayout()
        self.btn_scan = QPushButton("开始扫描")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setEnabled(False)
        btn_row.addWidget(self.btn_scan)
        btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.btn_connect = QPushButton("连接")
        self.btn_disconnect = QPushButton("断开")
        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(self.btn_connect)
        btn_row2.addWidget(self.btn_disconnect)
        layout.addLayout(btn_row2)
        layout.addStretch()

    def _connect_signals(self):
        self.btn_scan.clicked.connect(self._start_scan)
        self.btn_stop.clicked.connect(self._stop_scan)
        self.ble.signals.device_found.connect(self._on_device_found)
        self.ble.signals.scan_started.connect(lambda: self.btn_scan.setEnabled(False))
        self.ble.signals.scan_finished.connect(lambda: self.btn_scan.setEnabled(True))

    def _start_scan(self):
        asyncio.ensure_future(self._do_scan())

    async def _do_scan(self):
        self.list_widget.clear()
        await self.ble.scanner.start(timeout=10)
        self.btn_stop.setEnabled(False)

    def _stop_scan(self):
        asyncio.ensure_future(self.ble.scanner.stop())

    def _on_device_found(self, device_info: dict):
        text = f"{device_info['name']}  {device_info['rssi']}dBm  {device_info['address']}"
        # 去重
        for i in range(self.list_widget.count()):
            if device_info["address"] in self.list_widget.item(i).text():
                self.list_widget.takeItem(i)
                break
        self.list_widget.addItem(text)