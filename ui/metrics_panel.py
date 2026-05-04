"""
Metrics Panel — real-time pyqtgraph charts for training and evaluation metrics.
Uses tabbed layout with Training and Evaluation tabs.
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QGroupBox, QGridLayout, QSizePolicy,
)

from ui.theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_ELEVATED, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED,
    ACCENT, ACCENT_SECONDARY, SUCCESS, WARNING, DANGER,
    CHART_REWARD, CHART_LOSS_POLICY, CHART_LOSS_VALUE,
    CHART_LOSS_ENTROPY, CHART_EP_LENGTH, CHART_EVAL_BAR,
    CHART_GRID, CHART_BG, FONT_FAMILY,
)


# ── Configure pyqtgraph defaults ─────────────────────────────────────────────
pg.setConfigOptions(
    antialias=True,
    background=QColor(CHART_BG),
    foreground=QColor(TEXT_SECONDARY),
)


class MetricsPanel(QWidget):
    """
    Tabbed panel for displaying training and evaluation metrics.
    
    Tab 1 — Training: reward, loss, episode length charts
    Tab 2 — Evaluation: bar chart of per-episode rewards + summary stats
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._init_data_buffers()

    # ─── UI Setup ─────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container
        self._container = QWidget()
        self._container.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(6)

        # Title row
        title_row = QWidget()
        title_row.setStyleSheet("background: transparent; border: none;")
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(10)

        accent_bar = QWidget()
        accent_bar.setFixedSize(3, 18)
        accent_bar.setStyleSheet(f"background-color: {ACCENT}; border-radius: 2px; border: none;")
        title_row_layout.addWidget(accent_bar)

        title = QLabel("Metrics Analytics")
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 700;
                padding: 4px 0px;
                background: transparent;
                border: none;
            }}
        """)
        title_row_layout.addWidget(title)
        title_row_layout.addStretch()
        container_layout.addWidget(title_row)

        # Tab widget
        self._tab_widget = QTabWidget()
        container_layout.addWidget(self._tab_widget)

        # Training tab
        training_tab = QWidget()
        training_tab.setStyleSheet("background: transparent; border: none;")
        self._setup_training_tab(training_tab)
        self._tab_widget.addTab(training_tab, "Training")

        # Evaluation tab
        eval_tab = QWidget()
        eval_tab.setStyleSheet("background: transparent; border: none;")
        self._setup_evaluation_tab(eval_tab)
        self._tab_widget.addTab(eval_tab, "Evaluation")

        layout.addWidget(self._container)

    def _create_plot_widget(self, title: str, y_label: str) -> pg.PlotWidget:
        """Create a styled PlotWidget."""
        pw = pg.PlotWidget()
        pw.setBackground(QColor(CHART_BG))
        pw.showGrid(x=True, y=True, alpha=0.15)
        pw.setTitle(title, color=TEXT_PRIMARY, size="11pt")
        pw.setLabel("bottom", "Timesteps", color=TEXT_SECONDARY, units=None)
        pw.setLabel("left", y_label, color=TEXT_SECONDARY, units=None)
        pw.setMinimumHeight(160)
        sp = pw.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        pw.setSizePolicy(sp)
        
        # Style the axes
        for axis_name in ["bottom", "left"]:
            axis = pw.getPlotItem().getAxis(axis_name)
            axis.setPen(pg.mkPen(color=CHART_GRID, width=1))
            axis.setTextPen(pg.mkPen(color=TEXT_SECONDARY))
        
        return pw

    def _setup_training_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # ── Reward Chart ──
        self._reward_plot = self._create_plot_widget("Episode Reward", "Reward")
        self._reward_line = self._reward_plot.plot(
            pen=pg.mkPen(color=CHART_REWARD, width=2),
            name="ep_rew_mean",
        )
        # Fill under curve
        self._reward_fill = pg.FillBetweenItem(
            self._reward_line,
            pg.PlotDataItem([0], [0]),
            brush=pg.mkBrush(QColor(CHART_REWARD + "30")),
        )
        self._reward_plot.addItem(self._reward_fill)
        layout.addWidget(self._reward_plot, 3)

        # ── Loss Chart ──
        self._loss_plot = self._create_plot_widget("Training Loss", "Loss")
        self._loss_lines = {}
        loss_configs = [
            ("policy_gradient_loss", CHART_LOSS_POLICY, "Policy Loss"),
            ("value_loss", CHART_LOSS_VALUE, "Value Loss"),
            ("entropy_loss", CHART_LOSS_ENTROPY, "Entropy Loss"),
            ("loss", DANGER, "Total Loss"),
            ("actor_loss", CHART_LOSS_POLICY, "Actor Loss"),
            ("critic_loss", CHART_LOSS_VALUE, "Critic Loss"),
        ]
        for key, color, name in loss_configs:
            line = self._loss_plot.plot(
                pen=pg.mkPen(color=color, width=1.5),
                name=name,
            )
            self._loss_lines[key] = line
        self._loss_plot.addLegend(
            offset=(10, 10),
            labelTextColor=TEXT_SECONDARY,
            labelTextSize="9pt",
        )
        layout.addWidget(self._loss_plot, 3)

        # ── Episode Length Chart ──
        self._ep_len_plot = self._create_plot_widget("Episode Length", "Steps")
        self._ep_len_line = self._ep_len_plot.plot(
            pen=pg.mkPen(color=CHART_EP_LENGTH, width=2),
            name="ep_len_mean",
        )
        layout.addWidget(self._ep_len_plot, 2)

        # ── Live Stats Row ──
        self._stats_widget = QWidget()
        self._stats_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_ELEVATED};
                border-radius: 8px;
                border: 1px solid {BORDER};
            }}
        """)
        stats_layout = QHBoxLayout(self._stats_widget)
        stats_layout.setContentsMargins(8, 6, 8, 6)
        stats_layout.setSpacing(4)

        self._stat_labels = {}
        stat_items = [
            ("timesteps", "Timesteps", "0", ACCENT),
            ("fps", "FPS", "0", ACCENT_SECONDARY),
            ("ep_reward", "Reward", "—", SUCCESS),
            ("time", "Elapsed", "0s", WARNING),
        ]
        for i, (key, label_text, default_val, color) in enumerate(stat_items):
            if i > 0:
                sep = QWidget()
                sep.setFixedSize(1, 30)
                sep.setStyleSheet(f"background-color: {BORDER}; border: none;")
                stats_layout.addWidget(sep)

            stat_container = QWidget()
            stat_container.setStyleSheet("background: transparent; border: none;")
            sl = QVBoxLayout(stat_container)
            sl.setContentsMargins(8, 2, 8, 2)
            sl.setSpacing(2)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px; font-weight: 600; border: none; letter-spacing: 0.5px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(lbl)

            val = QLabel(default_val)
            val.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700; border: none;")
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(val)

            self._stat_labels[key] = val
            stats_layout.addWidget(stat_container, 1)

        layout.addWidget(self._stats_widget)

    def _setup_evaluation_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # ── Evaluation Bar Chart ──
        self._eval_plot = pg.PlotWidget()
        self._eval_plot.setBackground(QColor(CHART_BG))
        self._eval_plot.showGrid(x=False, y=True, alpha=0.15)
        self._eval_plot.setTitle("Reward per Episode", color=TEXT_PRIMARY, size="12pt")
        self._eval_plot.setLabel("bottom", "Episode", color=TEXT_SECONDARY)
        self._eval_plot.setLabel("left", "Total Reward", color=TEXT_SECONDARY)
        for axis_name in ["bottom", "left"]:
            axis = self._eval_plot.getPlotItem().getAxis(axis_name)
            axis.setPen(pg.mkPen(color=CHART_GRID, width=1))
            axis.setTextPen(pg.mkPen(color=TEXT_SECONDARY))
        self._eval_bar_item = pg.BarGraphItem(
            x=[], height=[], width=0.6,
            brush=pg.mkBrush(QColor(CHART_EVAL_BAR + "cc")),
            pen=pg.mkPen(color=CHART_EVAL_BAR, width=1),
        )
        self._eval_plot.addItem(self._eval_bar_item)
        layout.addWidget(self._eval_plot, 3)

        # ── Summary Statistics Card ──
        self._summary_group = QGroupBox("Summary Statistics")
        self._summary_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {BG_ELEVATED};
                border: 1px solid {BORDER};
                border-radius: 10px;
                margin-top: 18px;
                padding: 14px 12px 12px 12px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 12px;
                color: {TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 700;
            }}
        """)
        summary_layout = QGridLayout(self._summary_group)
        summary_layout.setSpacing(10)

        self._eval_stat_labels = {}
        eval_stats = [
            ("mean_reward", "Mean Reward", "—", 0, 0, SUCCESS),
            ("std_reward", "Std Dev", "—", 0, 1, WARNING),
            ("min_reward", "Min Reward", "—", 1, 0, DANGER),
            ("max_reward", "Max Reward", "—", 1, 1, ACCENT_SECONDARY),
            ("total_episodes", "Episodes", "0", 0, 2, ACCENT),
            ("mean_length", "Mean Length", "—", 1, 2, TEXT_PRIMARY),
        ]
        for key, label_text, default_val, row, col, color in eval_stats:
            cell = QWidget()
            cell.setStyleSheet("background: transparent; border: none;")
            cl = QVBoxLayout(cell)
            cl.setContentsMargins(4, 4, 4, 4)
            cl.setSpacing(2)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px; font-weight: 600; border: none;")
            cl.addWidget(lbl)
            
            val = QLabel(default_val)
            val.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700; border: none;")
            cl.addWidget(val)
            
            self._eval_stat_labels[key] = val
            summary_layout.addWidget(cell, row, col)

        layout.addWidget(self._summary_group)

    # ─── Theme ────────────────────────────────────────────────────────────────

    def refresh_theme(self):
        """Re-apply all inline styles to match the current theme."""
        import ui.theme as t

        self._container.setStyleSheet(f"""
            QWidget {{
                background-color: {t.BG_SECONDARY};
                border: 1px solid {t.BORDER};
                border-radius: 12px;
            }}
        """)
        self._stats_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {t.BG_ELEVATED};
                border-radius: 8px;
                border: 1px solid {t.BORDER};
            }}
        """)
        self._summary_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {t.BG_ELEVATED};
                border: 1px solid {t.BORDER};
                border-radius: 10px;
                margin-top: 18px;
                padding: 14px 12px 12px 12px;
                font-weight: 600;
                color: {t.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 12px;
                color: {t.TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 700;
            }}
        """)
        plot_defs = [
            (self._reward_plot,  "Episode Reward",      "Reward",       "Timesteps", "11pt"),
            (self._loss_plot,    "Training Loss",       "Loss",         "Timesteps", "11pt"),
            (self._ep_len_plot,  "Episode Length",      "Steps",        "Timesteps", "11pt"),
            (self._eval_plot,    "Reward per Episode",  "Total Reward", "Episode",   "12pt"),
        ]
        for plot, title, ylabel, xlabel, size in plot_defs:
            plot.setBackground(pg.mkColor(t.CHART_BG))
            plot.setTitle(title, color=t.TEXT_PRIMARY, size=size)
            plot.setLabel("bottom", xlabel, color=t.TEXT_SECONDARY, units=None)
            plot.setLabel("left", ylabel, color=t.TEXT_SECONDARY, units=None)
            for axis_name in ["bottom", "left"]:
                axis = plot.getPlotItem().getAxis(axis_name)
                axis.setPen(pg.mkPen(color=t.CHART_GRID, width=1))
                axis.setTextPen(pg.mkPen(color=t.TEXT_SECONDARY))

    # ─── Data Buffers ─────────────────────────────────────────────────────────

    def _init_data_buffers(self):
        """Initialize data arrays for training charts."""
        self._reward_x = []
        self._reward_y = []
        self._ep_len_x = []
        self._ep_len_y = []
        self._loss_data = {}  # key -> (x_list, y_list)
        self._eval_rewards = []
        self._eval_lengths = []

    # ─── Public API ───────────────────────────────────────────────────────────

    def update_training_metrics(self, metrics: dict):
        """
        Update training charts with new metrics from the DashboardCallback.
        
        Args:
            metrics: dict with keys like timestep, ep_rew_mean, losses, fps, etc.
        """
        timestep = metrics.get("timestep", 0)

        # Update reward chart
        if "ep_rew_mean" in metrics:
            self._reward_x.append(timestep)
            self._reward_y.append(metrics["ep_rew_mean"])
            x = np.array(self._reward_x)
            y = np.array(self._reward_y)
            self._reward_line.setData(x, y)
            # Update fill
            zero_line = pg.PlotDataItem(x, np.zeros_like(y))
            self._reward_fill.setCurves(self._reward_line, zero_line)

        # Update episode length chart
        if "ep_len_mean" in metrics:
            self._ep_len_x.append(timestep)
            self._ep_len_y.append(metrics["ep_len_mean"])
            self._ep_len_line.setData(
                np.array(self._ep_len_x),
                np.array(self._ep_len_y),
            )

        # Update loss charts
        losses = metrics.get("losses", {})
        for key, value in losses.items():
            if key not in self._loss_data:
                self._loss_data[key] = ([], [])
            self._loss_data[key][0].append(timestep)
            self._loss_data[key][1].append(value)
            if key in self._loss_lines:
                self._loss_lines[key].setData(
                    np.array(self._loss_data[key][0]),
                    np.array(self._loss_data[key][1]),
                )

        # Update stat labels
        self._stat_labels["timesteps"].setText(f"{timestep:,}")
        self._stat_labels["fps"].setText(f"{metrics.get('fps', 0):.0f}")
        if "ep_rew_mean" in metrics:
            self._stat_labels["ep_reward"].setText(f"{metrics['ep_rew_mean']:.2f}")
        elapsed = metrics.get("time_elapsed", 0)
        if elapsed >= 3600:
            self._stat_labels["time"].setText(f"{elapsed/3600:.1f}h")
        elif elapsed >= 60:
            self._stat_labels["time"].setText(f"{elapsed/60:.1f}m")
        else:
            self._stat_labels["time"].setText(f"{elapsed:.0f}s")

    def add_eval_episode(self, episode_idx: int, reward: float, length: int):
        """Add a completed evaluation episode result."""
        self._eval_rewards.append(reward)
        self._eval_lengths.append(length)

        # Update bar chart
        x = np.arange(1, len(self._eval_rewards) + 1)
        heights = np.array(self._eval_rewards)
        self._eval_bar_item.setOpts(x=x, height=heights, width=0.6)

        # Update summary stats
        rewards = np.array(self._eval_rewards)
        lengths = np.array(self._eval_lengths)
        self._eval_stat_labels["mean_reward"].setText(f"{rewards.mean():.2f}")
        self._eval_stat_labels["std_reward"].setText(f"{rewards.std():.2f}")
        self._eval_stat_labels["min_reward"].setText(f"{rewards.min():.2f}")
        self._eval_stat_labels["max_reward"].setText(f"{rewards.max():.2f}")
        self._eval_stat_labels["total_episodes"].setText(str(len(self._eval_rewards)))
        self._eval_stat_labels["mean_length"].setText(f"{lengths.mean():.1f}")

        # Switch to evaluation tab
        self._tab_widget.setCurrentIndex(1)

    def clear_training_data(self):
        """Clear all training chart data."""
        self._reward_x.clear()
        self._reward_y.clear()
        self._ep_len_x.clear()
        self._ep_len_y.clear()
        self._loss_data.clear()
        
        self._reward_line.setData([], [])
        self._ep_len_line.setData([], [])
        for line in self._loss_lines.values():
            line.setData([], [])
        
        self._stat_labels["timesteps"].setText("0")
        self._stat_labels["fps"].setText("0")
        self._stat_labels["ep_reward"].setText("—")
        self._stat_labels["time"].setText("0s")

    def clear_eval_data(self):
        """Clear all evaluation data."""
        self._eval_rewards.clear()
        self._eval_lengths.clear()
        self._eval_bar_item.setOpts(x=[], height=[], width=0.6)
        for lbl in self._eval_stat_labels.values():
            lbl.setText("—")
        self._eval_stat_labels["total_episodes"].setText("0")

    def clear_all(self):
        """Clear all data from both tabs."""
        self.clear_training_data()
        self.clear_eval_data()
        self._tab_widget.setCurrentIndex(0)
