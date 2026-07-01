"""src/ui/widgets/realtime_chart.py - VOFA+ style waveform widget."""

import pyqtgraph as pg

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

        # Translate pyqtgraph default context menu to Chinese
        self._patch_viewbox_menu()

    def _patch_viewbox_menu(self):
        """Translate the ViewBox context menu items to Chinese."""
        vb = self.plotItem.vb
        orig_get_menu = vb.getMenu

        def translated_get_menu(ev):
            menu = orig_get_menu(ev)
            if menu is None:
                return None
            _MAP = {
                "View All": "自适应缩放",
                "Mouse Mode": "鼠标模式",
                "1D Magnify": "一维放大",
                "2D Pan": "二维平移",
                "3D Box": "三维框选",
                "Transforms": "变换",
                "Normal": "正常",
                "Flip Horizontal": "水平翻转",
                "Flip Vertical": "垂直翻转",
                "Export": "导出数据",
            }
            for action in menu.actions():
                t = action.text()
                if t in _MAP:
                    action.setText(_MAP[t])
                sub = action.menu()
                if sub:
                    for sa in sub.actions():
                        st = sa.text()
                        if st in _MAP:
                            sa.setText(_MAP[st])
            return menu

        vb.getMenu = translated_get_menu

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
        """Show pyqtgraph default menu (translated to Chinese) + custom items."""
        vb = self.plotItem.vb
        menu = vb.getMenu(ev)
        if menu is None:
            return
        menu.addSeparator()
        act_pause = menu.addAction("⏸ 暂停" if not self._paused else "▶ 继续")
        act_clear = menu.addAction("🗑 清空波形")
        menu.addSeparator()
        act_reset = menu.addAction("↩ 重置视图")

        action = menu.exec(ev.screenPos())
        if action == act_pause:
            self.toggle_pause()
        elif action == act_clear:
            self.clear_all()
        elif action == act_reset:
            self.enableAutoRange()
            self.autoRange()

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