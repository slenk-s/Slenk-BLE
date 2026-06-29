"""src/ui/tabs/log_tab.py"""

import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout


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
        btn_row = QHBoxLayout()
        self.btn_clear = QPushButton("清空日志")
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)
        self.btn_clear.clicked.connect(self.log_view.clear)

        # Bridge Python logging to UI
        handler = LogHandler(self.log_view)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
        logging.getLogger("BLE-Monitor").addHandler(handler)