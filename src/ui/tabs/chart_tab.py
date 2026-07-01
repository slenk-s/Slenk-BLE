"""src/ui/tabs/chart_tab.py - VOFA+ style waveform tab."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QFrame, QSizePolicy)
from src.ui.widgets.realtime_chart import WaveformWidget


class ChannelLegend(QFrame):
    """Legend panel showing active channels with colored indicators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ChannelLegend { background: #f8f9fc; border: 1px solid #dde0e8; border-radius: 6px; padding: 6px; }
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 6, 8, 6)
        self._layout.setSpacing(4)
        title = QLabel("通道列表")
        title.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px;")
        self._layout.addWidget(title)
        self._labels: dict[str, QLabel] = {}

    def update_channels(self, channels: list):
        existing = set(self._labels.keys())
        current = {name for name, _ in channels}

        # Remove stale labels
        for name in existing - current:
            self._layout.removeWidget(self._labels[name])
            self._labels[name].deleteLater()
            del self._labels[name]

        # Add/update labels
        for name, color in channels:
            if name not in self._labels:
                dot = QLabel(f"● {name}")
                dot.setStyleSheet(f"color: rgb{color}; font-size: 12px; padding: 2px 4px;")
                self._labels[name] = dot
                self._layout.addWidget(dot)


class ChartTab(QWidget):
    def __init__(self, ble):
        super().__init__()
        self.ble = ble
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header and toolbar
        toolbar = QHBoxLayout()
        header = QLabel("📈 波形图")
        header.setStyleSheet("color: #2c3e50; font-size: 15px; font-weight: 700; padding: 2px 0px;")
        toolbar.addWidget(header)
        info = QLabel("ℹ️")
        info.setToolTip(
            "数据包结构说明\n\n"
            "┌─────────┬─────────┬──────────┬───────────┬────────┐\n"
            "│ 帧头(1B)│ 通道(1B)│ 长度(1B) │ 数据(N B) │ 校验(1B)│\n"
            "│  0xAA   │  ch_id  │   len    │  payload  │  XOR   │\n"
            "└─────────┴─────────┴──────────┴───────────┴────────┘\n\n"
            "第一字节作为波形数值显示\n"
            "协议解析器可在「协议」标签页中切换"
        )
        info.setStyleSheet("color: #7f8c9b; font-size: 16px; padding: 2px 4px;")
        toolbar.addWidget(info)
        toolbar.addStretch()

        self.btn_pause = QPushButton("⏸ 暂停")
        self.btn_pause.setCheckable(True)
        self.btn_pause.setStyleSheet("""
            QPushButton { background: #ffffff; color: #2c3e50; border: 1px solid #d0d4dc; border-radius: 6px; padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background: #eef0f5; border: 1px solid #0099ff; }
            QPushButton:checked { background: #fff3e0; color: #e65100; border: 1px solid #ff9100; }
        """)
        self.btn_clear = QPushButton("🗑 清空")
        self.btn_clear.setStyleSheet("""
            QPushButton { background: #ffffff; color: #2c3e50; border: 1px solid #d0d4dc; border-radius: 6px; padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background: #ffeaea; border: 1px solid #ff4444; }
        """)
        toolbar.addWidget(self.btn_pause)
        toolbar.addWidget(self.btn_clear)
        layout.addLayout(toolbar)

        # Waveform + Legend
        wave_row = QHBoxLayout()
        self.chart = WaveformWidget()
        self.chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        wave_row.addWidget(self.chart, 1)
        self.legend = ChannelLegend()
        self.legend.setFixedWidth(130)
        wave_row.addWidget(self.legend)
        layout.addLayout(wave_row, 1)

        # Status bar
        status_row = QHBoxLayout()
        self.lbl_status = QLabel("等待数据...")
        self.lbl_status.setStyleSheet("color: #888888; font-size: 12px;")
        status_row.addWidget(self.lbl_status)
        status_row.addStretch()
        layout.addLayout(status_row)

        # Connections
        self.btn_pause.clicked.connect(self._toggle_pause)
        self.btn_clear.clicked.connect(self._clear_waveform)
        self.ble.signals.data_received.connect(self._on_data)

        # Timer to update legend periodically
        from PySide6.QtCore import QTimer
        self._legend_timer = QTimer()
        self._legend_timer.timeout.connect(self._refresh_legend)
        self._legend_timer.start(1000)

    def _toggle_pause(self):
        paused = self.chart.toggle_pause()
        self.btn_pause.setText("▶ 继续" if paused else "⏸ 暂停")
        self.lbl_status.setText("已暂停" if paused else "接收中")

    def _clear_waveform(self):
        self.chart.clear_all()
        self.lbl_status.setText("已清空")

    def _refresh_legend(self):
        info = self.chart.get_channel_info()
        self.legend.update_channels(info)
        if info:
            self.lbl_status.setText(f"活跃通道: {len(info)}")

    def _on_data(self, address: str, data: bytes):
        if len(data) >= 1:
            value = data[0]
            self.chart.push(address, value)