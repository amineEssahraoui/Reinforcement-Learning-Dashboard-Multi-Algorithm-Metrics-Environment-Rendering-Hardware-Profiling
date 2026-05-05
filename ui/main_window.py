"""
Main Window — redesigned with floating config drawer overlay.

Layout (2-column):
    ┌──────────────────────────────────────────────────────┐
    │  Header: title | status pill | [⚙ Config] [theme]   │
    ├─────────────────────┬────────────────────────────────┤
    │  Left: Metrics(65%) │  Center: Environment Render    │
    │  + Hardware (35%)   │          (full height)         │
    └─────────────────────┴────────────────────────────────┘
    
    Config panel = floating overlay (right side), shown/hidden
    by the ⚙ Config button. Auto-hides when training starts,
    auto-shows when idle/done.
"""

import os
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QFileDialog, QStatusBar, QLabel, QFrame,
    QPushButton, QSizePolicy, QApplication, QGraphicsOpacityEffect,
)

import ui.theme as _theme
from ui.theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_ELEVATED, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_SECONDARY, SUCCESS,
    WARNING, DANGER, TEXT_DISABLED, FONT_FAMILY,
)
from ui.metrics_panel import MetricsPanel
from ui.hardware_panel import HardwarePanel
from ui.environment_render import EnvironmentRenderWidget
from ui.environment_controls import EnvironmentControls
from core.training_worker import TrainingWorker
from core.evaluation_worker import EvaluationWorker
from core.algorithms import import_algorithm_class, ALGORITHM_REGISTRY


# ─── Status Pill ──────────────────────────────────────────────────────────────

class StatusPill(QWidget):
    """
    Compact status indicator shown in the header.
    Displays a colored dot + label: Idle / Training / Evaluating / Done / Error.
    """

    _STATE_COLORS = {
        "idle":       TEXT_SECONDARY,
        "training":   WARNING,
        "evaluating": ACCENT_SECONDARY,
        "done":       SUCCESS,
        "eval_done":  SUCCESS,
        "error":      DANGER,
    }
    _STATE_LABELS = {
        "idle":       "Idle",
        "training":   "Training",
        "evaluating": "Evaluating",
        "done":       "Done",
        "eval_done":  "Done",
        "error":      "Error",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = "idle"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)

        self._dot = QFrame()
        self._dot.setFixedSize(8, 8)
        self._dot.setStyleSheet(
            f"background-color: {TEXT_SECONDARY}; border-radius: 4px; border: none;"
        )
        layout.addWidget(self._dot)

        self._lbl = QLabel("Idle")
        self._lbl.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;"
            " background: transparent; border: none;"
        )
        layout.addWidget(self._lbl)

        self.setStyleSheet(
            f"background-color: {BG_TERTIARY}; border: 1px solid {BORDER};"
            " border-radius: 12px;"
        )
        self.setFixedHeight(26)

    def set_state(self, state: str):
        self._state = state
        color = self._STATE_COLORS.get(state, TEXT_SECONDARY)
        label = self._STATE_LABELS.get(state, state.capitalize())
        self._dot.setStyleSheet(
            f"background-color: {color}; border-radius: 4px; border: none;"
        )
        self._lbl.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 600;"
            " background: transparent; border: none;"
        )
        self._lbl.setText(label)


# ─── Floating Config Drawer ───────────────────────────────────────────────────

class ConfigDrawer(QWidget):
    """
    Floating overlay that holds EnvironmentControls.
    Slides in/out from the right edge of the central widget.
    """

    def __init__(self, controls: EnvironmentControls, parent: QWidget):
        super().__init__(parent)
        self._controls = controls
        self._visible = False
        self._anim = None

        # Panel styling
        self.setObjectName("configDrawer")
        self.setFixedWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            #configDrawer {{
                background-color: {BG_SECONDARY};
                border-left: 1px solid {BORDER};
                border-radius: 0px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(controls)

        # Start hidden (off-screen to the right)
        self.hide()

    def toggle(self):
        """Toggle drawer open/closed with smooth slide animation."""
        if self._visible:
            self.close_drawer()
        else:
            self.open_drawer()

    def open_drawer(self):
        if self._visible:
            return
        self._visible = True
        parent = self.parent()
        ph = parent.height()
        pw = parent.width()
        w = self.width()

        # Position: full height, right side
        self.setGeometry(pw, 0, w, ph)
        self.show()
        self.raise_()

        self._run_anim(pw, pw - w)

    def close_drawer(self):
        if not self._visible:
            return
        self._visible = False
        parent = self.parent()
        pw = parent.width()
        w = self.width()
        start_x = pw - w

        def _on_done():
            self.hide()

        self._run_anim(start_x, pw, on_done=_on_done)

    def _run_anim(self, start_x: int, end_x: int, on_done=None):
        """Animate the x position of this widget."""
        if self._anim:
            self._anim.stop()

        anim = QPropertyAnimation(self, b"geometry", self)
        anim.setDuration(260)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        parent = self.parent()
        ph = parent.height()
        w = self.width()

        anim.setStartValue(QRect(start_x, 0, w, ph))
        anim.setEndValue(QRect(end_x, 0, w, ph))
        if on_done:
            anim.finished.connect(on_done)
        anim.start()
        self._anim = anim

    def is_open(self) -> bool:
        return self._visible

    def resizeEvent(self, event):
        """Re-anchor drawer when parent resizes."""
        super().resizeEvent(event)

    def ensure_geometry(self):
        """Called after parent resize to keep drawer anchored correctly."""
        if not self._visible:
            return
        parent = self.parent()
        ph = parent.height()
        pw = parent.width()
        w = self.width()
        self.setGeometry(pw - w, 0, w, ph)


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    Main application window for the RL Dashboard.

    Two-column layout:
        Left  → Metrics (65%) + Hardware (35%)
        Right → Environment Render (full height)

    Config panel is a floating drawer overlay, accessible via
    the ⚙ Config button in the header. Auto-hides on train start.
    """

    def __init__(self):
        super().__init__()
        self._trained_model = None
        self._current_env_id = ""
        self._current_algo_name = ""
        self._config_user_opened = False  # Track if user manually opened config

        self._setup_window()
        self._setup_workers()
        self._setup_ui()
        self._connect_signals()

    # ─── Window Setup ─────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("RL Dashboard — Reinforcement Learning Prototyping Tool")
        self.setMinimumSize(900, 600)
        self.resize(1400, 860)

        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar_label = QLabel("Ready")
        self._statusbar.addPermanentWidget(self._statusbar_label)

    def _setup_workers(self):
        self._training_worker = TrainingWorker(self)
        self._evaluation_worker = EvaluationWorker(self)

    # ─── UI Assembly ──────────────────────────────────────────────────────────

    def _setup_ui(self):
        self._central = QWidget()
        self.setCentralWidget(self._central)

        main_layout = QVBoxLayout(self._central)
        main_layout.setContentsMargins(10, 10, 10, 6)
        main_layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        self._header = self._build_header()
        main_layout.addWidget(self._header)
        main_layout.addSpacing(8)

        # ── 2-Column Splitter ────────────────────────────────────────────────
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(3)
        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {BORDER};
                margin: 4px 2px;
                border-radius: 1px;
            }}
            QSplitter::handle:hover {{
                background-color: {ACCENT};
            }}
        """)

        # Left column: Metrics + Hardware
        left_panel = QWidget()
        left_panel.setStyleSheet("background: transparent; border: none;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(8)

        self._metrics_panel = MetricsPanel()
        left_layout.addWidget(self._metrics_panel, 65)

        self._hardware_panel = HardwarePanel()
        left_layout.addWidget(self._hardware_panel, 35)

        self._splitter.addWidget(left_panel)

        # Right column: Environment render (full height)
        center_panel = QWidget()
        center_panel.setStyleSheet("background: transparent; border: none;")
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(4, 0, 0, 0)
        center_layout.setSpacing(0)

        self._render_widget = EnvironmentRenderWidget()
        center_layout.addWidget(self._render_widget)

        self._splitter.addWidget(center_panel)

        # Equal initial split — left slightly narrower
        self._splitter.setSizes([480, 760])
        main_layout.addWidget(self._splitter, 1)

        # ── Floating Config Drawer ───────────────────────────────────────────
        # Controls are created first (not added to any layout)
        self._controls = EnvironmentControls()
        self._drawer = ConfigDrawer(self._controls, self._central)

    def _build_header(self) -> QWidget:
        """Build the top header bar."""
        header = QWidget()
        header.setFixedHeight(54)
        header.setObjectName("appHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        # Accent bar
        accent_bar = QFrame()
        accent_bar.setFixedSize(4, 28)
        accent_bar.setStyleSheet(
            f"background-color: {ACCENT}; border-radius: 2px; border: none;"
        )
        layout.addWidget(accent_bar)
        layout.addSpacing(12)

        # Title
        title = QLabel("RL Dashboard")
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: 700;"
            " background: transparent; border: none;"
        )
        layout.addWidget(title)
        layout.addSpacing(12)

        # Divider
        div = QFrame()
        div.setFixedSize(1, 20)
        div.setStyleSheet(f"background-color: {BORDER}; border: none;")
        layout.addWidget(div)
        layout.addSpacing(12)

        # Subtitle
        subtitle = QLabel("Reinforcement Learning Prototyping Tool")
        subtitle.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px;"
            " background: transparent; border: none;"
        )
        layout.addWidget(subtitle)
        layout.addStretch()

        # Status pill
        self._status_pill = StatusPill()
        layout.addWidget(self._status_pill)
        layout.addSpacing(10)

        # Config toggle button
        self._config_btn = QPushButton("⚙  Config")
        self._config_btn.setObjectName("configToggleBtn")
        self._config_btn.setFixedHeight(30)
        self._config_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._config_btn.setToolTip("Show / hide configuration panel")
        self._config_btn.setStyleSheet(f"""
            QPushButton#configToggleBtn {{
                background-color: {BG_TERTIARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 4px 14px;
                font-size: 12px;
                font-weight: 600;
                min-height: 28px;
            }}
            QPushButton#configToggleBtn:hover {{
                background-color: {ACCENT};
                border-color: {ACCENT};
                color: white;
            }}
            QPushButton#configToggleBtn:checked {{
                background-color: {ACCENT};
                border-color: {ACCENT};
                color: white;
            }}
        """)
        self._config_btn.setCheckable(True)
        self._config_btn.clicked.connect(self._on_config_btn_clicked)
        layout.addWidget(self._config_btn)
        layout.addSpacing(10)

        # Theme toggle
        self._theme_btn = QPushButton("Light Mode")
        self._theme_btn.setFixedHeight(30)
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self._theme_btn)
        layout.addSpacing(10)

        # Version
        version = QLabel("v1.0")
        version.setStyleSheet(
            f"color: {TEXT_DISABLED}; font-size: 11px;"
            " background: transparent; border: none;"
        )
        layout.addWidget(version)

        return header

    # ─── Config Drawer ────────────────────────────────────────────────────────

    def _on_config_btn_clicked(self, checked: bool):
        """Toggle the config drawer open/closed."""
        self._config_user_opened = checked
        if checked:
            self._drawer.open_drawer()
        else:
            self._drawer.close_drawer()

    def _open_config(self):
        """Programmatically open the config drawer."""
        if not self._drawer.is_open():
            self._config_btn.setChecked(True)
            self._drawer.open_drawer()

    def _close_config(self):
        """Programmatically close the config drawer."""
        if self._drawer.is_open():
            self._config_btn.setChecked(False)
            self._drawer.close_drawer()

    def resizeEvent(self, event):
        """Keep the drawer anchored on resize."""
        super().resizeEvent(event)
        if hasattr(self, "_drawer"):
            self._drawer.ensure_geometry()

    # ─── Theme ────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        new_mode = "light" if _theme.get_current_mode() == "dark" else "dark"
        _theme.set_theme(new_mode)
        QApplication.instance().setStyleSheet(_theme.get_stylesheet())
        self._theme_btn.setText("Light Mode" if new_mode == "dark" else "Dark Mode")

    # ─── Signal Wiring ────────────────────────────────────────────────────────

    def _connect_signals(self):
        self._controls.start_training_requested.connect(self._start_training)
        self._controls.stop_training_requested.connect(self._stop_all)
        self._controls.start_evaluation_requested.connect(self._start_evaluation)
        self._controls.reset_requested.connect(self._reset)
        self._controls._load_btn.clicked.connect(self._load_model)

        # Training Worker
        self._training_worker.metrics_updated.connect(
            self._metrics_panel.update_training_metrics
        )
        self._training_worker.progress_updated.connect(
            self._controls.update_progress
        )
        self._training_worker.training_complete.connect(self._on_training_complete)
        self._training_worker.training_error.connect(self._on_training_error)
        self._training_worker.training_stopped.connect(self._on_training_stopped)

        # Evaluation Worker
        self._evaluation_worker.frame_ready.connect(self._render_widget.update_frame)
        self._evaluation_worker.eval_step_info.connect(self._on_eval_step)
        self._evaluation_worker.eval_episode_complete.connect(
            self._on_eval_episode_complete
        )
        self._evaluation_worker.evaluation_complete.connect(self._on_evaluation_complete)
        self._evaluation_worker.evaluation_error.connect(self._on_eval_error)
        self._evaluation_worker.evaluation_stopped.connect(self._on_eval_stopped)

    # ─── Actions ──────────────────────────────────────────────────────────────

    def _start_training(self, config: dict):
        self._current_env_id = config["env_id"]
        self._current_algo_name = config["algo_name"]

        self._metrics_panel.clear_training_data()
        self._metrics_panel.clear_eval_data()
        self._render_widget.show_placeholder(config["env_id"])
        self._trained_model = None

        self._training_worker.configure(
            env_id=config["env_id"],
            algo_name=config["algo_name"],
            total_timesteps=config["total_timesteps"],
            seed=config.get("seed"),
            hyperparams=config.get("hyperparams", {}),
            save_dir=config.get("save_dir", "saved_models"),
        )

        self._set_app_state("training")
        self._statusbar_label.setText(
            f"Training {config['algo_name']} on {config['env_id']}..."
        )

        # Auto-hide config drawer to give full space to metrics + render
        self._close_config()

        self._training_worker.start()

    def _start_evaluation(self, n_episodes: int):
        if self._trained_model is None:
            QMessageBox.warning(
                self, "No Model",
                "No trained model available. Please train first or load a model."
            )
            return

        self._metrics_panel.clear_eval_data()
        self._render_widget.clear_hud()

        seed_val = self._controls._seed_spin.value()
        self._evaluation_worker.configure(
            model=self._trained_model,
            env_id=self._current_env_id,
            n_eval_episodes=n_episodes,
            seed=seed_val if seed_val > 0 else None,
            render_delay_ms=16,
        )

        self._set_app_state("evaluating")
        self._statusbar_label.setText(
            f"Evaluating {self._current_algo_name} for {n_episodes} episodes..."
        )
        # Close config during evaluation too
        self._close_config()
        self._evaluation_worker.start()

    def _stop_all(self):
        self._training_worker.stop()
        self._evaluation_worker.stop()
        self._statusbar_label.setText("Stopping...")

    def _reset(self):
        self._stop_all()
        self._trained_model = None
        self._current_env_id = ""
        self._current_algo_name = ""
        self._metrics_panel.clear_all()
        self._render_widget.show_placeholder("")
        self._render_widget.clear_hud()
        self._controls.set_state("idle")
        self._set_app_state("idle")
        self._statusbar_label.setText("Ready")

    def _load_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Trained Model",
            "saved_models",
            "SB3 Model (*.zip);;All Files (*)",
        )
        if not file_path:
            return

        algo_name = self._controls.get_selected_algorithm()
        if algo_name not in ALGORITHM_REGISTRY:
            QMessageBox.warning(
                self, "Algorithm Required",
                "Please select the algorithm used to train this model."
            )
            return

        try:
            cls = import_algorithm_class(algo_name)
            self._trained_model = cls.load(file_path)
            self._current_env_id = self._controls.get_selected_env_id()
            self._current_algo_name = algo_name
            self._controls.set_state("done")
            self._set_app_state("done")
            self._statusbar_label.setText(
                f"Loaded model from {os.path.basename(file_path)}"
            )
            QMessageBox.information(
                self, "Model Loaded",
                f"Successfully loaded {algo_name} model.\nYou can now evaluate it."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Load Error", f"Failed to load model:\n{str(e)}"
            )

    # ─── State Management ─────────────────────────────────────────────────────

    def _set_app_state(self, state: str):
        """Update both the controls state and the header status pill."""
        self._controls.set_state(state)
        self._status_pill.set_state(state)

        # Re-enable the config button label when not running
        if state in ("idle", "done", "eval_done", "error"):
            self._config_btn.setEnabled(True)
        else:
            # Still allow opening config during training if user really wants to
            self._config_btn.setEnabled(True)

    # ─── Callbacks ────────────────────────────────────────────────────────────

    def _on_training_complete(self, model_path: str):
        self._trained_model = self._training_worker.trained_model
        self._set_app_state("done")
        self._statusbar_label.setText(
            f"Training complete! Model saved to {model_path}"
        )

    def _on_training_error(self, error_msg: str):
        self._set_app_state("error")
        self._statusbar_label.setText("Training failed!")
        QMessageBox.critical(
            self, "Training Error",
            f"Training encountered an error:\n\n{error_msg[:500]}"
        )

    def _on_training_stopped(self):
        if self._training_worker.trained_model is not None:
            self._trained_model = self._training_worker.trained_model
            self._set_app_state("done")
            self._statusbar_label.setText("Training stopped — partial model available")
        else:
            self._set_app_state("idle")
            self._statusbar_label.setText("Training stopped")

    def _on_eval_step(self, step_info: dict):
        self._render_widget.update_hud(**step_info)

    def _on_eval_episode_complete(self, idx: int, reward: float, length: int):
        self._metrics_panel.add_eval_episode(idx, reward, length)
        self._statusbar_label.setText(
            f"Evaluation episode {idx} — Reward: {reward:.2f}"
        )

    def _on_evaluation_complete(self, results: list):
        self._set_app_state("eval_done")
        total = len(results)
        mean_reward = sum(r["reward"] for r in results) / total if total else 0
        self._statusbar_label.setText(
            f"Evaluation complete — {total} episodes, Mean Reward: {mean_reward:.2f}"
        )

    def _on_eval_error(self, error_msg: str):
        self._set_app_state("error")
        self._statusbar_label.setText("Evaluation failed!")
        QMessageBox.critical(
            self, "Evaluation Error",
            f"Evaluation encountered an error:\n\n{error_msg[:500]}"
        )

    def _on_eval_stopped(self):
        self._set_app_state("done")
        self._statusbar_label.setText("Evaluation stopped")

    # ─── Cleanup ──────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._stop_all()
        self._training_worker.wait(2000)
        self._evaluation_worker.wait(2000)
        super().closeEvent(event)