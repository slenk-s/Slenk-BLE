"""src/ui/tabs/ota_tab.py"""

import asyncio
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QProgressBar, QFileDialog, QHBoxLayout)

from src.utils.logger import setup_logger


class OtaTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        self._firmware_path = None
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

        self.btn_select.clicked.connect(self._select_file)
        self.btn_start.clicked.connect(self._start_ota)

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择固件文件", "", "固件文件 (*.bin *.hex);;所有文件 (*)")
        if path:
            self._firmware_path = path
            self.lbl_file.setText(f"已选择: {Path(path).name}")
            self.btn_start.setEnabled(True)

    def _start_ota(self):
        from src.app_layer.ota_service import OTAService

        log = setup_logger(__name__)

        if not self._firmware_path:
            log.warning("OTA 未选择固件文件")

            return
        self.btn_start.setEnabled(False)
        self.log_output.setText("OTA 升级中...")

        async def _run_ota():
            service = OTAService(self.ble.gatt.write_characteristic)
            result = await service.start_update("", "", self._firmware_path)  # address/char would come from device selection
            self.log_output.setText(f"OTA 完成: {result['sent']}/{result['total_packets']} 包发送")

        asyncio.ensure_future(_run_ota())