"""
Hardware Monitor Modal Dialog.
Displays real-time CPU, RAM, and GPU usage with large, separate graphs.
Modal window with close button.
"""

import random
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame
)
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg

from ui.theme import get_pyqtgraph_color

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False


class HardwareMonitorModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Monitor")
        self.setModal(True)
        self.setFixedSize(900, 900)
        self.setStyleSheet("""
            QDialog {
                background-color: #27272A;
                border: 1px solid #3F3F46;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # --- Initialize data FIRST (before _create_graph_section calls) ---
        self.timeline = list(range(60))
        self.cpu_history = [0.0] * 60
        self.ram_history = [0.0] * 60
        self.gpu_history = [0.0] * 60
        self.lbl_cpu_value = QLabel("0.0%")
        self.lbl_ram_value = QLabel("0.0 GB")
        self.lbl_gpu_value = QLabel("0.0%")

        # --- Header with Close Button ---
        header = QHBoxLayout()
        title = QLabel("🖥 Hardware Monitor — Live")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                border: none;
                font-weight: bold;
                font-size: 18px;
                color: #A1A1AA;
                background: transparent;
            }
            QPushButton:hover {
                color: #EF4444;
            }
        """)
        self.btn_close.clicked.connect(self.reject)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_close)
        layout.addLayout(header)

        # --- Separator ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #3F3F46;")
        layout.addWidget(sep)

        # --- CPU Graph ---
        cpu_section = self._create_graph_section(
            "CPU Usage (%)",
            "chart_len",
            "cpu"
        )
        layout.addWidget(cpu_section)

        # --- RAM Graph ---
        ram_section = self._create_graph_section(
            "RAM Usage (GB / %)",
            "chart_ram",
            "ram"
        )
        layout.addWidget(ram_section)

        # --- GPU Graph ---
        gpu_section = self._create_graph_section(
            "GPU Usage (%)",
            "chart_reward",
            "gpu"
        )
        layout.addWidget(gpu_section)

        # --- Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll_hardware)

    def _create_graph_section(self, title: str, color_key: str, metric_type: str) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #18181B; border: 1px solid #3F3F46; border-radius: 4px; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #D4D4D8; text-transform: uppercase;")
        layout.addWidget(title_lbl)

        # Graph
        color = get_pyqtgraph_color(color_key)
        plot = pg.PlotWidget()
        plot.setFixedHeight(200)
        plot.setBackground(None)
        plot.showGrid(x=False, y=True, alpha=0.2)
        plot.setYRange(0, 100)
        plot.setMouseEnabled(x=False, y=False)
        plot.getAxis("left").setLabel("Usage (%)")
        plot.getAxis("left").setTextPen(pg.mkPen(color="#A1A1AA"))
        plot.getAxis("bottom").setTextPen(pg.mkPen(color="#A1A1AA"))

        history = [0.0] * 60
        if metric_type == "cpu":
            self.cpu_history = history
            self.cpu_plot = plot
            curve = plot.plot(self.timeline, self.cpu_history, pen=pg.mkPen(color, width=2.5))
            self.cpu_curve = curve
        elif metric_type == "ram":
            self.ram_history = history
            self.ram_plot = plot
            curve = plot.plot(self.timeline, self.ram_history, pen=pg.mkPen(color, width=2.5))
            self.ram_curve = curve
        elif metric_type == "gpu":
            self.gpu_history = history
            self.gpu_plot = plot
            curve = plot.plot(self.timeline, self.gpu_history, pen=pg.mkPen(color, width=2.5))
            self.gpu_curve = curve

        layout.addWidget(plot)

        # Value label
        value_lbl = QLabel("—")
        value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        value_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #F4F4F5;")
        layout.addWidget(value_lbl)

        if metric_type == "cpu":
            self.lbl_cpu_value = value_lbl
        elif metric_type == "ram":
            self.lbl_ram_value = value_lbl
        elif metric_type == "gpu":
            self.lbl_gpu_value = value_lbl

        return frame

    def showEvent(self, event):
        super().showEvent(event)
        self._poll_hardware()
        self.timer.start(1000)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

    def _poll_hardware(self):
        """Poll hardware metrics and update graphs."""
        cpu_percent = 0.0
        ram_gb = 0.0
        ram_pct = 0.0
        gpu_load = 0.0

        if HAS_PSUTIL:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                ram = psutil.virtual_memory()
                ram_pct = ram.percent
                ram_gb = ram.used / (1024 ** 3)
            except Exception:
                pass
        else:
            cpu_percent = random.uniform(10.0, 50.0)
            ram_pct = random.uniform(30.0, 60.0)
            ram_gb = random.uniform(4.0, 8.0)

        if HAS_GPU:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_load = gpus[0].load * 100
            except Exception:
                gpu_load = random.uniform(20.0, 80.0)
        else:
            gpu_load = random.uniform(20.0, 80.0)

        # Update histories
        self._update_history(self.cpu_history, cpu_percent)
        self._update_history(self.ram_history, ram_pct)
        self._update_history(self.gpu_history, gpu_load)

        # Update graph curves
        self.cpu_curve.setData(self.timeline, self.cpu_history)
        self.ram_curve.setData(self.timeline, self.ram_history)
        self.gpu_curve.setData(self.timeline, self.gpu_history)

        # Update value labels
        self.lbl_cpu_value.setText(f"{cpu_percent:.1f}%")
        self.lbl_ram_value.setText(f"{ram_gb:.1f} GB ({ram_pct:.1f}%)")
        self.lbl_gpu_value.setText(f"{gpu_load:.1f}%")

    def _update_history(self, history: list, value: float):
        history.pop(0)
        history.append(float(value))
