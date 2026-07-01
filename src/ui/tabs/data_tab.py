"""src/ui/tabs/data_tab.py"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                                QPushButton, QHBoxLayout, QComboBox, QLabel)
from PySide6.QtCore import QDateTime
from src.app_layer.protocol_engine import ProtocolEngine


class DataTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        self.engine = ProtocolEngine()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header_row = QHBoxLayout()
        header = QLabel("📊 实时数据")
        header.setObjectName("tabHeader")
        header.setStyleSheet("QLabel#tabHeader { color: #2c3e50; font-size: 14px; font-weight: 600; padding: 2px 0px; }")
        header_row.addWidget(header)
        header_row.addStretch()
        layout.addLayout(header_row)

        filter_row = QHBoxLayout()
        self.device_filter = QComboBox()
        self.device_filter.addItem("全部设备")
        filter_row.addWidget(QLabel("筛选:"))
        filter_row.addWidget(self.device_filter)
        self.btn_clear = QPushButton("🗑 清空")
        self.btn_clear.setProperty("type", "danger")
        filter_row.addStretch()
        filter_row.addWidget(self.btn_clear)
        layout.addLayout(filter_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["时间", "设备", "十六进制", "解析值"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self.table)
        self.btn_clear.clicked.connect(lambda: self.table.setRowCount(0))
        self.ble.signals.data_received.connect(self._on_data)

    def _on_data(self, address: str, data: bytes):
        parsed = self.engine.parse(address, data)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(QDateTime.currentDateTime().toString("HH:mm:ss.zzz")))
        self.table.setItem(row, 1, QTableWidgetItem(address))
        self.table.setItem(row, 2, QTableWidgetItem(parsed.hex_str))
        self.table.setItem(row, 3, QTableWidgetItem(parsed.description or parsed.ascii_str))
        self.table.scrollToBottom()