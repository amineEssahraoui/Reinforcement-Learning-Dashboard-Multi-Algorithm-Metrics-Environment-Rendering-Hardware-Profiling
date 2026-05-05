"""
Metrics Panel — real-time pyqtgraph charts.
Loss chart redesigned with better visibility and auto-ranging.
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QGroupBox, QGridLayout

from ui.theme import (
    BG_SECONDARY, BG_TERTIARY, BG_ELEVATED, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED,
    ACCENT, ACCENT_SECONDARY, SUCCESS, WARNING, DANGER,
    CHART_REWARD, CHART_LOSS_POLICY, CHART_LOSS_VALUE, CHART_LOSS_ENTROPY,
    CHART_EP_LENGTH, CHART_EVAL_BAR, CHART_GRID, CHART_BG, FONT_FAMILY,
)

pg.setConfigOptions(antialias=True, background=QColor(CHART_BG), foreground=QColor(TEXT_SECONDARY))

class MetricsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_data_buffers()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self._container = QWidget()
        self._container.setObjectName("panelContainer")
        cont_layout = QVBoxLayout(self._container)
        cont_layout.setContentsMargins(8,8,8,8)

        title_row = QWidget()
        title_layout = QHBoxLayout(title_row)
        accent = QWidget()
        accent.setFixedSize(3,18)
        accent.setStyleSheet(f"background:{ACCENT}; border-radius:2px;")
        title_layout.addWidget(accent)
        title = QLabel("Metrics Analytics")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-weight:700;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        cont_layout.addWidget(title_row)

        self._tab_widget = QTabWidget()
        self._setup_training_tab()
        self._setup_evaluation_tab()
        cont_layout.addWidget(self._tab_widget)
        layout.addWidget(self._container)

    def _create_plot(self, title, ylabel):
        pw = pg.PlotWidget()
        pw.setBackground(QColor(CHART_BG))
        pw.showGrid(x=True, y=True, alpha=0.2)
        pw.setTitle(title, color=TEXT_PRIMARY, size="11pt")
        pw.setLabel("bottom", "Timesteps", color=TEXT_SECONDARY)
        pw.setLabel("left", ylabel, color=TEXT_SECONDARY)
        pw.setMinimumHeight(180)
        for axis in ("bottom", "left"):
            ax = pw.getPlotItem().getAxis(axis)
            ax.setPen(pg.mkPen(color=CHART_GRID))
            ax.setTextPen(pg.mkPen(color=TEXT_SECONDARY))
        return pw

    def _setup_training_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)

        # Reward
        self._reward_plot = self._create_plot("Episode Reward", "Reward")
        self._reward_line = self._reward_plot.plot(pen=pg.mkPen(color=CHART_REWARD, width=2.5))
        layout.addWidget(self._reward_plot, 3)

        # Loss - amélioré : lignes plus épaisses, auto-range, légende
        self._loss_plot = self._create_plot("Training Loss", "Loss")
        self._loss_lines = {}
        loss_config = [
            ("policy_gradient_loss", CHART_LOSS_POLICY, "Policy Loss"),
            ("value_loss", CHART_LOSS_VALUE, "Value Loss"),
            ("entropy_loss", CHART_LOSS_ENTROPY, "Entropy"),
            ("actor_loss", CHART_LOSS_POLICY, "Actor Loss"),
            ("critic_loss", CHART_LOSS_VALUE, "Critic Loss"),
            ("loss", DANGER, "Total Loss"),
        ]
        for key, col, name in loss_config:
            line = self._loss_plot.plot(pen=pg.mkPen(color=col, width=2), name=name)
            self._loss_lines[key] = line
        self._loss_plot.addLegend(offset=(10,10), labelTextColor=TEXT_SECONDARY, labelTextSize="9pt")
        # Auto-range activé
        self._loss_plot.enableAutoRange(axis=pg.ViewBox.XYAxes)
        layout.addWidget(self._loss_plot, 3)

        # Episode length
        self._ep_len_plot = self._create_plot("Episode Length", "Steps")
        self._ep_len_line = self._ep_len_plot.plot(pen=pg.mkPen(color=CHART_EP_LENGTH, width=2.5))
        layout.addWidget(self._ep_len_plot, 2)

        # Stats
        self._stats_widget = QWidget()
        self._stats_widget.setObjectName("statsContainer")
        stats_layout = QHBoxLayout(self._stats_widget)
        stats_layout.setContentsMargins(8,6,8,6)
        self._stat_labels = {}
        for key, label, default, color in [
            ("timesteps", "Timesteps", "0", ACCENT),
            ("fps", "FPS", "0", ACCENT_SECONDARY),
            ("ep_reward", "Reward", "—", SUCCESS),
            ("time", "Elapsed", "0s", WARNING),
        ]:
            container = QWidget()
            vbox = QVBoxLayout(container)
            vbox.setContentsMargins(4,2,4,2)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:10px; font-weight:600;")
            val = QLabel(default)
            val.setStyleSheet(f"color:{color}; font-size:16px; font-weight:700;")
            vbox.addWidget(lbl); vbox.addWidget(val)
            self._stat_labels[key] = val
            stats_layout.addWidget(container)
        layout.addWidget(self._stats_widget)
        self._tab_widget.addTab(tab, "Training")

    def _setup_evaluation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self._eval_plot = pg.PlotWidget()
        self._eval_plot.setBackground(QColor(CHART_BG))
        self._eval_plot.setTitle("Reward per Episode", color=TEXT_PRIMARY, size="12pt")
        self._eval_plot.setLabel("bottom", "Episode")
        self._eval_plot.setLabel("left", "Total Reward")
        self._eval_bar = pg.BarGraphItem(x=[], height=[], width=0.6, brush=pg.mkBrush(QColor(CHART_EVAL_BAR+"cc")), pen=pg.mkPen(color=CHART_EVAL_BAR))
        self._eval_plot.addItem(self._eval_bar)
        layout.addWidget(self._eval_plot, 3)

        self._summary_group = QGroupBox("Summary Statistics")
        self._summary_group.setStyleSheet(f"QGroupBox{{background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:10px; margin-top:16px;}}")
        grid = QGridLayout(self._summary_group)
        self._eval_stats = {}
        for key, label, row, col, color in [
            ("mean_reward", "Mean Reward", 0,0, SUCCESS),
            ("std_reward", "Std Dev", 0,1, WARNING),
            ("min_reward", "Min Reward", 1,0, DANGER),
            ("max_reward", "Max Reward", 1,1, ACCENT_SECONDARY),
            ("total_episodes", "Episodes", 0,2, ACCENT),
            ("mean_length", "Mean Length", 1,2, TEXT_PRIMARY),
        ]:
            w = QWidget()
            vbox = QVBoxLayout(w)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:10px;")
            val = QLabel("—")
            val.setStyleSheet(f"color:{color}; font-size:14px; font-weight:700;")
            vbox.addWidget(lbl); vbox.addWidget(val)
            self._eval_stats[key] = val
            grid.addWidget(w, row, col)
        layout.addWidget(self._summary_group)
        self._tab_widget.addTab(tab, "Evaluation")

    def _init_data_buffers(self):
        self._reward_x, self._reward_y = [], []
        self._ep_len_x, self._ep_len_y = [], []
        self._loss_data = {}
        self._eval_rewards, self._eval_lengths = [], []

    def update_training_metrics(self, metrics: dict):
        ts = metrics.get("timestep", 0)
        if "ep_rew_mean" in metrics:
            self._reward_x.append(ts); self._reward_y.append(metrics["ep_rew_mean"])
            self._reward_line.setData(np.array(self._reward_x), np.array(self._reward_y))
        if "ep_len_mean" in metrics:
            self._ep_len_x.append(ts); self._ep_len_y.append(metrics["ep_len_mean"])
            self._ep_len_line.setData(np.array(self._ep_len_x), np.array(self._ep_len_y))
        losses = metrics.get("losses", {})
        for k, v in losses.items():
            if k in self._loss_lines:
                if k not in self._loss_data: self._loss_data[k] = ([], [])
                self._loss_data[k][0].append(ts); self._loss_data[k][1].append(v)
                self._loss_lines[k].setData(np.array(self._loss_data[k][0]), np.array(self._loss_data[k][1]))
        self._stat_labels["timesteps"].setText(f"{ts:,}")
        self._stat_labels["fps"].setText(f"{metrics.get('fps',0):.0f}")
        if "ep_rew_mean" in metrics:
            self._stat_labels["ep_reward"].setText(f"{metrics['ep_rew_mean']:.2f}")
        et = metrics.get("time_elapsed",0)
        self._stat_labels["time"].setText(f"{et:.0f}s" if et<60 else f"{et/60:.1f}m" if et<3600 else f"{et/3600:.1f}h")

    def add_eval_episode(self, idx, reward, length):
        self._eval_rewards.append(reward)
        self._eval_lengths.append(length)
        x = np.arange(1, len(self._eval_rewards)+1)
        self._eval_bar.setOpts(x=x, height=np.array(self._eval_rewards), width=0.6)
        r = np.array(self._eval_rewards)
        l = np.array(self._eval_lengths)
        self._eval_stats["mean_reward"].setText(f"{r.mean():.2f}")
        self._eval_stats["std_reward"].setText(f"{r.std():.2f}")
        self._eval_stats["min_reward"].setText(f"{r.min():.2f}")
        self._eval_stats["max_reward"].setText(f"{r.max():.2f}")
        self._eval_stats["total_episodes"].setText(str(len(self._eval_rewards)))
        self._eval_stats["mean_length"].setText(f"{l.mean():.1f}")
        self._tab_widget.setCurrentIndex(1)

    def clear_training_data(self):
        self._reward_x.clear(); self._reward_y.clear()
        self._ep_len_x.clear(); self._ep_len_y.clear()
        self._loss_data.clear()
        self._reward_line.setData([],[])
        self._ep_len_line.setData([],[])
        for line in self._loss_lines.values(): line.setData([],[])
        for lbl in self._stat_labels.values(): lbl.setText("0" if lbl == self._stat_labels["timesteps"] else "—")

    def clear_eval_data(self):
        self._eval_rewards.clear(); self._eval_lengths.clear()
        self._eval_bar.setOpts(x=[], height=[])
        for k, lbl in self._eval_stats.items():
            lbl.setText("0" if k=="total_episodes" else "—")

    def clear_all(self):
        self.clear_training_data()
        self.clear_eval_data()
        self._tab_widget.setCurrentIndex(0)