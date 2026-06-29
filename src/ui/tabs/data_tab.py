"""src/ui/tabs/data_tab.py"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QComboBox
from PySide6.QtCore import QDateTime


class DataTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        layout = QVBoxLayout(self)
        filter_row = QHBoxLayout()
        self.device_filter = QComboBox()
        self.device_filter.addItem("全部设备")
        filter_row.addWidget(self.device_filter)
        self.btn_clear = QPushButton("清空")
        filter_row.addWidget(self.btn_clear)
        layout.addLayout(filter_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["时间", "设备", "HEX", "解析值"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.btn_clear.clicked.connect(self.table.setRowCount(0))
        self.ble.signals.data_received.connect(self._on_data)

    def _on_data(self, address: str, data: bytes):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(QDateTime.currentDateTime().toString("HH:mm:ss.zzz")))
        self.table.setItem(row, 1, QTableWidgetItem(address))
        self.table.setItem(row, 2, QTableWidgetItem(data.hex(" ").upper()))
        self.table.setItem(row, 3, QTableWidgetItem(data.decode("ascii", errors="replace")))
        self.table.scrollToBottom()