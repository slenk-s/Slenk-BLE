"""src/ui/tabs/chart_tab.py"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from src.ui.widgets.realtime_chart import RealtimeChart


class ChartTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        layout = QVBoxLayout(self)
        self.chart = RealtimeChart()
        layout.addWidget(self.chart)