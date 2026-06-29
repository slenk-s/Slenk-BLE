"""src/ui/tabs/log_tab.py"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout


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