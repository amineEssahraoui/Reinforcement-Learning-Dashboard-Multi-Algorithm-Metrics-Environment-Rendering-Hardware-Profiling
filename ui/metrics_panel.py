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

    def _create_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 11px; color: #A1A1AA; text-transform: uppercase; font-weight: bold;")
        return lbl

    def _create_plot(self) -> pg.PlotWidget:
        plot = pg.PlotWidget()
        plot.setBackground(None) 
        plot.showGrid(x=True, y=True, alpha=0.15) 
        plot.getAxis('left').setPen('#3F3F46')
        plot.getAxis('left').setTextPen('#A1A1AA')
        plot.getAxis('bottom').setPen('#3F3F46')
        plot.getAxis('bottom').setTextPen('#A1A1AA')
        
        return plot
    
    def _create_stat_badge(self, text: str, color_key: str) -> QLabel:
        """Crée un petit badge pour afficher une métrique clé."""
        color = get_pyqtgraph_color(color_key)
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            background-color: #18181B; 
            border: 1px solid #3F3F46; 
            border-radius: 4px; 
            padding: 4px 8px; 
            font-size: 11px; 
            font-weight: bold; 
            color: {color};
        """)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    @pyqtSlot(dict)
    def update_metrics(self, metrics: dict):
        ts = metrics.get("timestep", 0)
        self.data_timesteps.append(ts)
        
        # Update Reward
        rew = metrics.get("ep_rew_mean", 0.0)
        self.data_reward.append(rew)
        self.curve_reward.setData(self.data_timesteps, self.data_reward)
        
        # Update Loss (diffère selon l'algo, on essaie de prendre 'loss' ou 'policy_gradient_loss')
        losses = metrics.get("losses", {})
        loss_val = losses.get("loss", losses.get("policy_gradient_loss", 0.0))
        self.data_loss.append(loss_val)
        self.curve_loss.setData(self.data_timesteps, self.data_loss)
        
        # Update Length
        ep_len = metrics.get("ep_len_mean", 0.0)
        self.data_len.append(ep_len)
        self.curve_len.setData(self.data_timesteps, self.data_len)
        
        # Update Badges
        fps = metrics.get("fps", 0)
        prog = metrics.get("progress", 0.0) * 100
        
        self.lbl_fps.setText(f"FPS: {int(fps)}")
        self.lbl_rew.setText(f"Rew: {rew:.1f}")
        self.lbl_prog.setText(f"{int(prog)}%")

    def clear_data(self):
        self.data_timesteps.clear()
        self.data_reward.clear()
        self.data_loss.clear()
        self.data_len.clear()
        
        self.curve_reward.setData([], [])
        self.curve_loss.setData([], [])
        self.curve_len.setData([], [])
        
        self.lbl_fps.setText("FPS: 0")
        self.lbl_rew.setText("Rew: 0.0")
        self.lbl_prog.setText("0%")