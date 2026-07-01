"""src/ui/tabs/ota_tab.py"""

import asyncio
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QProgressBar, QFileDialog, QHBoxLayout)

from src.utils.logger import setup_logger
from src.ui.styles import button_primary


class OtaTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        self._firmware_path = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("🔄 OTA 固件升级")
        header.setStyleSheet("color: #2c3e50; font-size: 15px; font-weight: 700;")
        layout.addWidget(header)

        self.btn_select = QPushButton("📁 选择固件文件")
        self.btn_select.setProperty("type", "primary")
        self.btn_select.setStyleSheet(button_primary())
        layout.addWidget(self.btn_select)

        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("固件:"))
        self.lbl_file = QLabel("未选择文件")
        self.lbl_file.setStyleSheet("color: #9098b8; font-size: 13px; padding: 4px 8px;")
        file_row.addWidget(self.lbl_file)
        file_row.addStretch()
        layout.addLayout(file_row)

        layout.addSpacing(8)

        self.btn_start = QPushButton("🚀 开始升级")
        self.btn_start.setEnabled(False)
        self.btn_start.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #00e676,stop:1 #00c853); color: #ffffff; border: none; border-radius: 6px; padding: 10px 24px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #33ff99,stop:1 #00e676); }
            QPushButton:disabled { background: #1e2040; color: #555577; }
        """)
        layout.addWidget(self.btn_start)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_output = QLabel("就绪")
        self.log_output.setStyleSheet("color: #9098b8; font-size: 12px; padding: 4px 0px;")
        layout.addWidget(self.log_output)

        layout.addStretch()

        self.btn_select.clicked.connect(self._select_file)
        self.btn_start.clicked.connect(self._start_ota)

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择固件文件", "", "固件文件 (*.bin *.hex);;所有文件 (*)")
        if path:
            self._firmware_path = path
            self.lbl_file.setText(Path(path).name)
            self.lbl_file.setStyleSheet("color: #00e676; font-size: 13px; padding: 4px 8px;")
            self.btn_start.setEnabled(True)

    def _start_ota(self):
        from src.app_layer.ota_service import OTAService

        log = setup_logger(__name__)

        if not self._firmware_path:
            log.warning("OTA 未选择固件文件")
            return

        self.btn_start.setEnabled(False)
        self.log_output.setText("OTA 升级中...")
        self.log_output.setStyleSheet("color: #ff9100; font-size: 12px; padding: 4px 0px;")

        async def _run_ota():
            service = OTAService(self.ble.gatt.write_characteristic)
            result = await service.start_update("", "", self._firmware_path)
            sent = result["sent"]
            total = result["total_packets"]
            self.progress.setValue(100 if sent >= total else int(sent / total * 100))
            self.log_output.setText(f"OTA 完成: {sent}/{total} 包发送")
            self.log_output.setStyleSheet("color: #00e676; font-size: 12px; padding: 4px 0px;")

        asyncio.ensure_future(_run_ota())