"""src/ui/tabs/protocol_tab.py"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QComboBox, QPushButton,
                               QHBoxLayout, QLabel, QTextEdit)

from src.utils.logger import setup_logger


class ProtocolTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("选择协议解析器:"))
        self.parser_select = QComboBox()
        self.parser_select.addItems(["Raw HEX", "JSON", "Modbus RTU"])
        layout.addWidget(self.parser_select)
        self.btn_apply = QPushButton("应用到设备")
        layout.addWidget(self.btn_apply)
        layout.addWidget(QLabel("自定义脚本:"))
        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("在此编写自定义协议解析脚本...")
        layout.addWidget(self.script_editor)

        self.btn_apply.clicked.connect(self._apply_parser)

    def _apply_parser(self):
        parser_name = self.parser_select.currentText()
        log = setup_logger(__name__)
        log.info("协议解析器已选择: %s", parser_name)