"""src/ui/widgets/realtime_chart.py"""

import pyqtgraph as pg
from collections import defaultdict


class RealtimeChart(pg.PlotWidget):
    """多通道实时曲线图。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLabel("left", "数值")
        self.setLabel("bottom", "采样点")
        self.showGrid(x=True, y=True, alpha=0.3)
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._buffers: dict[str, list[float]] = {}
        self.max_points = 500

    def add_channel(self, name: str, color: tuple = (0, 255, 0)) -> None:
        pen = pg.mkPen(color=color, width=1.5)
        self._curves[name] = self.plot(pen=pen, name=name)
        self._buffers[name] = []

    def push(self, channel: str, value: float) -> None:
        if channel not in self._buffers:
            self.add_channel(channel)
        buf = self._buffers[channel]
        buf.append(value)
        if len(buf) > self.max_points:
            buf.pop(0)
        self._curves[channel].setData(buf)