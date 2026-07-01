"""src/ui/tabs/log_tab.py"""

import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtGui import QFont


class LogHandler(logging.Handler):
    def __init__(self, log_view):
        super().__init__()
        self.log_view = log_view

    def emit(self, record):
        msg = self.format(record)
        self.log_view.appendPlainText(msg)


class LogTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QLabel("📋 运行日志")
        header.setStyleSheet("QLabel { color: #2c3e50; font-size: 14px; font-weight: 600; padding: 2px 0px; }")
        layout.addWidget(header)

        btn_row = QHBoxLayout()
        self.btn_clear = QPushButton("🗑 清空日志")
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 11))
        self.log_view.setStyleSheet("""
            QPlainTextEdit { background-color: #12132a; color: #c8c8e0; border: 1px solid #3a3d5c; border-radius: 8px; padding: 8px; }
        """)
        layout.addWidget(self.log_view)
        self.btn_clear.clicked.connect(self.log_view.clear)

        handler = LogHandler(self.log_view)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
        logging.getLogger("BLE-Monitor").addHandler(handler)