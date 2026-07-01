"""src/ui/tabs/protocol_tab.py"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QComboBox, QPushButton,
                               QHBoxLayout, QLabel, QTextEdit)

from src.utils.logger import setup_logger
from src.ui.styles import button_base


class ProtocolTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("⚙️ 协议配置")
        header.setStyleSheet("color: #2c3e50; font-size: 15px; font-weight: 700;")
        layout.addWidget(header)

        select_row = QHBoxLayout()
        select_row.addWidget(QLabel("解析器:"))
        self.parser_select = QComboBox()
        self.parser_select.addItems(["原始 HEX", "JSON", "Modbus RTU"])
        select_row.addWidget(self.parser_select, 1)
        layout.addLayout(select_row)

        self.btn_apply = QPushButton("✅ 应用到设备")
        self.btn_apply.setStyleSheet(button_base())
        layout.addWidget(self.btn_apply)

        layout.addSpacing(8)

        script_label = QLabel("自定义脚本:")
        script_label.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 600;")
        layout.addWidget(script_label)

        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("在此编写自定义协议解析脚本...")
        self.script_editor.setMinimumHeight(120)
        layout.addWidget(self.script_editor, 1)

        tip = QLabel("💡 提示: 选择解析器后点击应用，设备数据将按所选协议解析")
        tip.setStyleSheet("color: #7f8c9b; font-size: 11px;")
        layout.addWidget(tip)

        self.btn_apply.clicked.connect(self._apply_parser)

    def _apply_parser(self):
        parser_name = self.parser_select.currentText()
        log = setup_logger(__name__)
        log.info("协议解析器已选择: %s", parser_name)
        self.btn_apply.setText("✅ 已应用")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.btn_apply.setText("✅ 应用到设备"))