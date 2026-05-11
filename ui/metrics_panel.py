from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot, Qt
import pyqtgraph as pg

from ui.theme import get_pyqtgraph_color

class MetricsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MetricsPanel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        self.data_timesteps = []
        self.data_reward = []
        self.data_loss = []
        self.data_len = []
        
        # Episode Reward
        layout.addWidget(self._create_title("Episode Reward"))
        self.plot_reward = self._create_plot()
        self.curve_reward = self.plot_reward.plot(pen=pg.mkPen(color=get_pyqtgraph_color("chart_reward"), width=2))
        layout.addWidget(self.plot_reward)
        
        # Training Loss
        layout.addWidget(self._create_title("Training Loss"))
        self.plot_loss = self._create_plot()
        self.curve_loss = self.plot_loss.plot(pen=pg.mkPen(color=get_pyqtgraph_color("chart_loss"), width=2))
        layout.addWidget(self.plot_loss)
        
        # Episode Length
        layout.addWidget(self._create_title("Episode Length"))
        self.plot_len = self._create_plot()
        self.curve_len = self.plot_len.plot(pen=pg.mkPen(color=get_pyqtgraph_color("chart_len"), width=2))
        layout.addWidget(self.plot_len)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)
        
        self.lbl_fps = self._create_stat_badge("FPS: 0", "chart_len")
        self.lbl_rew = self._create_stat_badge("Rew: 0.0", "chart_reward")
        self.lbl_prog = self._create_stat_badge("0%", "text_muted")
        
        stats_layout.addWidget(self.lbl_fps)
        stats_layout.addWidget(self.lbl_rew)
        stats_layout.addWidget(self.lbl_prog)
        layout.addLayout(stats_layout)
