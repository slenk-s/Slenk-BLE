"""src/app.py"""

import sys
from PySide6.QtWidgets import QApplication
from src.ble.manager import BLEManager
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BLEApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("蓝牙上位机")
        self.ble = BLEManager()
        self.window = MainWindow(self.ble)

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())