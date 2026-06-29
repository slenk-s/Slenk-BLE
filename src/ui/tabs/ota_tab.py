"""src/ui/tabs/ota_tab.py"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QProgressBar, QFileDialog, QHBoxLayout)


class OtaTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        layout = QVBoxLayout(self)
        self.btn_select = QPushButton("选择固件文件")
        layout.addWidget(self.btn_select)
        self.lbl_file = QLabel("未选择文件")
        layout.addWidget(self.lbl_file)
        self.btn_start = QPushButton("开始升级")
        self.btn_start.setEnabled(False)
        layout.addWidget(self.btn_start)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.log_output = QLabel("就绪")
        layout.addWidget(self.log_output)
        layout.addStretch()