"""src/ui/device_panel.py"""

import asyncio
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                                QHBoxLayout, QListWidget, QLabel)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt
from src.ui.styles import button_primary, button_danger


class DevicePanel(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        self._scan_animation = None
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header
        header = QLabel("🔗 设备面板")
        header.setObjectName("panelHeader")
        header.setStyleSheet("QLabel#panelHeader { color: #2c3e50; font-size: 15px; font-weight: 700; padding: 4px 0px; letter-spacing: 1px; }")
        layout.addWidget(header)

        # Scan status row with animated LED
        status_row = QHBoxLayout()
        self.scan_led = QLabel("●")
        self.scan_led.setFixedSize(16, 16)
        self.scan_led.setStyleSheet("color: #555577; font-size: 18px;")
        self.scan_led.setAlignment(Qt.AlignCenter)
        self.lbl_scan_status = QLabel("空闲")
        self.lbl_scan_status.setStyleSheet("color: #7f8c9b; font-size: 12px;")
        status_row.addWidget(self.scan_led)
        status_row.addWidget(self.lbl_scan_status)
        status_row.addStretch()
        layout.addLayout(status_row)

        # Scan buttons
        btn_row = QHBoxLayout()
        self.btn_scan = QPushButton("🔍 开始扫描")
        self.btn_scan.setProperty("type", "primary")
        self.btn_scan.setStyleSheet(button_primary())
        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_stop.setProperty("type", "danger")
        self.btn_stop.setStyleSheet(button_danger())
        self.btn_stop.setEnabled(False)
        btn_row.addWidget(self.btn_scan)
        btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        # Device list
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet("""
            QListWidget { background-color: #ffffff; border: 1px solid #d0d4dc; border-radius: 8px; padding: 4px; font-size: 12px; color: #2c3e50; }
            QListWidget::item { padding: 8px 12px; border-radius: 4px; margin: 2px 0px; }
            QListWidget::item:hover { background-color: #eef1f8; border: 1px solid rgba(0,153,255,0.3); }
            QListWidget::item:selected { background-color: rgba(0,153,255,0.12); color: #0099ff; border: 1px solid rgba(0,153,255,0.3); }
            QListWidget::item:alternate { background-color: #fafbfd; }
        """)
        layout.addWidget(self.list_widget)

        # Connection buttons
        self.btn_connect = QPushButton("🔗 连接")
        self.btn_connect.setProperty("type", "primary")
        self.btn_connect.setStyleSheet(button_primary())
        self.btn_disconnect = QPushButton("❌ 断开")
        self.btn_disconnect.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:1 #f0f1f5); color: #2c3e50; border: 1px solid #d0d4dc; border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: 500; }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #fff5f5,stop:1 #ffeaea); border: 1px solid #ff5252; color: #e53935; }
            QPushButton:disabled { background: #e8eaef; color: #bbbbbb; border: 1px solid #e0e0e0; }
        """)
        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(self.btn_connect)
        btn_row2.addWidget(self.btn_disconnect)
        layout.addLayout(btn_row2)
        layout.addStretch()

    def _start_scan_animation(self):
        """Pulsing dot animation for scanning state."""
        self._scan_animation = QPropertyAnimation(self.scan_led, b"geometry")
        self._scan_animation.setDuration(800)
        self._scan_animation.setLoopCount(-1)
        geom = self.scan_led.geometry()
        self._scan_animation.setKeyValueAt(0, QRect(geom.x(), geom.y(), 16, 16))
        self._scan_animation.setKeyValueAt(0.5, QRect(geom.x() - 2, geom.y() - 2, 20, 20))
        self._scan_animation.setKeyValueAt(1, QRect(geom.x(), geom.y(), 16, 16))
        self._scan_animation.setEasingCurve(QEasingCurve.InOutSine)
        self._scan_animation.start()

    def _stop_scan_animation(self):
        if self._scan_animation:
            self._scan_animation.stop()
            self._scan_animation = None

    def _connect_signals(self):
        self.btn_scan.clicked.connect(self._start_scan)
        self.btn_stop.clicked.connect(self._stop_scan)
        self.ble.signals.device_found.connect(self._on_device_found)
        self.ble.signals.scan_started.connect(self._on_scan_started)
        self.ble.signals.scan_finished.connect(self._on_scan_finished)
        self.btn_connect.clicked.connect(self._connect_device)
        self.btn_disconnect.clicked.connect(self._disconnect_device)

    def _on_scan_started(self):
        self.btn_scan.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.scan_led.setStyleSheet("color: #00e676; font-size: 18px;")
        self.lbl_scan_status.setText("扫描中...")
        self._start_scan_animation()

    def _on_scan_finished(self):
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.scan_led.setStyleSheet("color: #555577; font-size: 18px;")
        count = len(self.ble.scanner.discovered_devices)
        self.lbl_scan_status.setText(f"发现 {count} 个设备")
        self._stop_scan_animation()

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
        for i in range(self.list_widget.count()):
            if device_info["address"] in self.list_widget.item(i).text():
                self.list_widget.takeItem(i)
                break
        self.list_widget.addItem(text)

    def _connect_device(self):
        selected = self.list_widget.currentItem()
        if selected is None:
            return
        text = selected.text()
        address = text.split("  ")[-1] if "  " in text else ""
        if address:
            asyncio.ensure_future(self.ble.connector.connect(address))

    def _disconnect_device(self):
        selected = self.list_widget.currentItem()
        if selected is None:
            return
        text = selected.text()
        address = text.split("  ")[-1] if "  " in text else ""
        if address:
            asyncio.ensure_future(self.ble.connector.disconnect(address))