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
        self.ble.signals.data_received.connect(self._on_data)

    def _on_data(self, address: str, data: bytes):
        # Try to extract a numeric value from data
        if len(data) >= 1:
            value = data[0]  # Use first byte as simple numeric value
            self.chart.push(address, value)