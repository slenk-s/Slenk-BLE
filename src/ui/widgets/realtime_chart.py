"""src/ui/widgets/realtime_chart.py - VOFA+ style waveform widget."""

import pyqtgraph as pg
from PySide6.QtWidgets import QMenu

CHANNEL_COLORS = [
    (255, 68, 68),
    (68, 136, 255),
    (68, 187, 68),
    (255, 136, 0),
    (170, 68, 255),
    (0, 204, 204),
    (255, 200, 0),
    (255, 80, 160),
]


class WaveformWidget(pg.PlotWidget):
    """Multi-channel waveform plot, inspired by VOFA+ wave widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground("#ffffff")
        self.setLabel("left", "数值", color="#555555")
        self.setLabel("bottom", "采样点", color="#555555")
        self.showGrid(x=True, y=True, alpha=0.2)
        self.getAxis("left").setTextPen(pg.mkPen(color="#888888"))
        self.getAxis("bottom").setTextPen(pg.mkPen(color="#888888"))
        self.getAxis("left").setPen(pg.mkPen(color="#cccccc"))
        self.getAxis("bottom").setPen(pg.mkPen(color="#cccccc"))

        self._curves: dict[str, pg.PlotDataItem] = {}
        self._buffers: dict[str, list[float]] = {}
        self._color_index: dict[str, int] = {}
        self._next_color = 0
        self.max_points = 500
        self._paused = False

    def toggle_pause(self):
        self._paused = not self._paused
        return self._paused

    def add_channel(self, name: str) -> None:
        if name in self._curves:
            return
        idx = self._next_color % len(CHANNEL_COLORS)
        self._next_color += 1
        self._color_index[name] = idx
        pen = pg.mkPen(color=CHANNEL_COLORS[idx], width=1.5)
        self._curves[name] = self.plot(pen=pen, name=name)
        self._buffers[name] = []

    def push(self, channel: str, value: float) -> None:
        if self._paused:
            return
        if channel not in self._buffers:
            self.add_channel(channel)
        buf = self._buffers[channel]
        buf.append(value)
        if len(buf) > self.max_points:
            buf.pop(0)
        self._curves[channel].setData(buf)

    def clear_all(self):
        for name in self._curves:
            self._buffers[name] = []
            self._curves[name].setData([])

    def get_channel_info(self):
        result = []
        for name in self._curves:
            idx = self._color_index.get(name, 0) % len(CHANNEL_COLORS)
            result.append((name, CHANNEL_COLORS[idx]))
        return result

    # ── Chinese context menu ──

    def raiseContextMenu(self, ev):
        """Override pyqtgraph default context menu with Chinese menu."""
        menu = QMenu(self)
        act_pause = menu.addAction("⏸ 暂停" if not self._paused else "▶ 继续")
        act_clear = menu.addAction("🗑 清空波形")
        menu.addSeparator()
        act_view_all = menu.addAction("📐 自适应缩放")
        act_reset = menu.addAction("↩ 重置视图")
        menu.addSeparator()
        act_export = menu.addAction("💾 导出数据")

        action = menu.exec(ev.screenPos())
        if action == act_pause:
            self.toggle_pause()
        elif action == act_clear:
            self.clear_all()
        elif action == act_view_all:
            self.autoRange()
        elif action == act_reset:
            self.enableAutoRange()
            self.autoRange()
        elif action == act_export:
            self._export_data()

    def _export_data(self):
        """Export waveform data to CSV."""
        import csv
        from pathlib import Path
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(self, "导出波形数据", str(Path.home() / "波形数据.csv"), "CSV 文件 (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["通道", "采样点", "数值"])
            for name, buf in self._buffers.items():
                for i, val in enumerate(buf):
                    w.writerow([name, i, val])