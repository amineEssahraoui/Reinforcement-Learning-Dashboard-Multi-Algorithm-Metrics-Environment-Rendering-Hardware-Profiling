"""
Main Window — floating config drawer, improved hardware collapsible,
rendering during training, clear model button.
"""

import os
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QFileDialog, QStatusBar, QLabel, QFrame,
    QPushButton, QApplication,
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

class StatusPill(QWidget):
    _STATE_COLORS = {
        "idle": TEXT_SECONDARY, "training": WARNING, "evaluating": ACCENT_SECONDARY,
        "done": SUCCESS, "eval_done": SUCCESS, "error": DANGER,
    }
    _STATE_LABELS = {
        "idle": "Idle", "training": "Training", "evaluating": "Evaluating",
        "done": "Done", "eval_done": "Done", "error": "Error",
    }
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = "idle"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10,0,10,0)
        self._dot = QFrame()
        self._dot.setFixedSize(8,8)
        self._dot.setStyleSheet(f"background:{TEXT_SECONDARY}; border-radius:4px;")
        self._lbl = QLabel("Idle")
        self._lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-weight:600;")
        layout.addWidget(self._dot)
        layout.addWidget(self._lbl)
        self.setStyleSheet(f"background:{BG_TERTIARY}; border:1px solid {BORDER}; border-radius:12px;")
        self.setFixedHeight(26)
    def set_state(self, state: str):
        self._state = state
        color = self._STATE_COLORS.get(state, TEXT_SECONDARY)
        label = self._STATE_LABELS.get(state, state.capitalize())
        self._dot.setStyleSheet(f"background:{color}; border-radius:4px;")
        self._lbl.setStyleSheet(f"color:{color}; font-weight:600;")
        self._lbl.setText(label)

class ConfigDrawer(QWidget):
    def __init__(self, controls: EnvironmentControls, parent: QWidget):
        super().__init__(parent)
        self._controls = controls
        self._visible = False
        self.setFixedWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"#configDrawer{{background:{BG_SECONDARY}; border-left:1px solid {BORDER};}}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(controls)
        self.hide()
    def toggle(self):
        if self._visible: self.close_drawer()
        else: self.open_drawer()
    def open_drawer(self):
        if self._visible: return
        self._visible = True
        parent = self.parent()
        pw, ph = parent.width(), parent.height()
        self.setGeometry(pw, 0, self.width(), ph)
        self.show()
        self._run_anim(pw, pw - self.width())
    def close_drawer(self):
        if not self._visible: return
        self._visible = False
        pw = self.parent().width()
        self._run_anim(pw - self.width(), pw, on_done=self.hide)
    def _run_anim(self, start, end, on_done=None):
        if hasattr(self, "_anim") and self._anim: self._anim.stop()
        anim = QPropertyAnimation(self, b"geometry", self)
        anim.setDuration(260)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(QRect(start, 0, self.width(), self.parent().height()))
        anim.setEndValue(QRect(end, 0, self.width(), self.parent().height()))
        if on_done: anim.finished.connect(on_done)
        anim.start()
        self._anim = anim
    def is_open(self): return self._visible
    def ensure_geometry(self):
        if not self._visible: return
        p = self.parent()
        self.setGeometry(p.width() - self.width(), 0, self.width(), p.height())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._trained_model = None
        self._current_env_id = ""
        self._current_algo_name = ""
        self._setup_window()
        self._setup_workers()
        self._setup_ui()
        self._connect_signals()

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

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10,10,10,6)
        self._header = self._build_header()
        main_layout.addWidget(self._header)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0,0,4,0)
        self._metrics_panel = MetricsPanel()
        self._hardware_panel = HardwarePanel()
        left_layout.addWidget(self._metrics_panel, 65)
        left_layout.addWidget(self._hardware_panel, 35)
        self._splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self._render_widget = EnvironmentRenderWidget()
        right_layout.addWidget(self._render_widget)
        self._splitter.addWidget(right_panel)
        self._splitter.setSizes([480, 760])
        main_layout.addWidget(self._splitter, 1)

        self._controls = EnvironmentControls()
        self._drawer = ConfigDrawer(self._controls, central)

    def _build_header(self):
        header = QWidget()
        header.setFixedHeight(54)
        header.setObjectName("appHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16,0,16,0)
        accent = QFrame()
        accent.setFixedSize(4,28)
        accent.setStyleSheet(f"background:{ACCENT}; border-radius:2px;")
        layout.addWidget(accent)
        title = QLabel("RL Dashboard")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-weight:700; font-size:16px;")
        layout.addWidget(title)
        layout.addSpacing(12)
        sep = QFrame()
        sep.setFixedSize(1,20)
        sep.setStyleSheet(f"background:{BORDER};")
        layout.addWidget(sep)
        subtitle = QLabel("Reinforcement Learning Prototyping Tool")
        subtitle.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px;")
        layout.addWidget(subtitle)
        layout.addStretch()
        self._status_pill = StatusPill()
        layout.addWidget(self._status_pill)
        self._config_btn = QPushButton("⚙  Config")
        self._config_btn.setCheckable(True)
        self._config_btn.clicked.connect(self._on_config_btn_clicked)
        layout.addWidget(self._config_btn)
        self._theme_btn = QPushButton("Light Mode")
        self._theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self._theme_btn)
        version = QLabel("v1.0")
        version.setStyleSheet(f"color:{TEXT_DISABLED}; font-size:11px;")
        layout.addWidget(version)
        return header

    def _on_config_btn_clicked(self, checked):
        if checked: self._drawer.open_drawer()
        else: self._drawer.close_drawer()

    def _toggle_theme(self):
        new = "light" if _theme.get_current_mode() == "dark" else "dark"
        _theme.set_theme(new)
        QApplication.instance().setStyleSheet(_theme.get_stylesheet())
        self._theme_btn.setText("Light Mode" if new == "dark" else "Dark Mode")

    def _connect_signals(self):
        self._controls.start_training_requested.connect(self._start_training)
        self._controls.stop_training_requested.connect(self._stop_all)
        self._controls.start_evaluation_requested.connect(self._start_evaluation)
        self._controls.reset_requested.connect(self._reset)
        self._controls.clear_model_requested.connect(self._clear_model)
        self._controls._load_btn.clicked.connect(self._load_model)

        self._training_worker.metrics_updated.connect(self._metrics_panel.update_training_metrics)
        self._training_worker.progress_updated.connect(self._controls.update_progress)
        self._training_worker.training_complete.connect(self._on_training_complete)
        self._training_worker.training_error.connect(self._on_training_error)
        self._training_worker.training_stopped.connect(self._on_training_stopped)
        # Frame pendant training
        if hasattr(self._training_worker, "frame_ready"):
            self._training_worker.frame_ready.connect(self._render_widget.update_frame)

        self._evaluation_worker.frame_ready.connect(self._render_widget.update_frame)
        self._evaluation_worker.eval_step_info.connect(self._on_eval_step)
        self._evaluation_worker.eval_episode_complete.connect(self._on_eval_episode_complete)
        self._evaluation_worker.evaluation_complete.connect(self._on_evaluation_complete)
        self._evaluation_worker.evaluation_error.connect(self._on_eval_error)
        self._evaluation_worker.evaluation_stopped.connect(self._on_eval_stopped)

    def _start_training(self, config):
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
            render=config.get("render_training", False),
        )
        self._set_app_state("training")
        self._statusbar_label.setText(f"Training {config['algo_name']} on {config['env_id']}...")
        self._drawer.close_drawer()
        self._training_worker.start()

    def _start_evaluation(self, n_episodes):
        if self._trained_model is None:
            QMessageBox.warning(self, "No Model", "No trained model. Train or load first.")
            return
        self._metrics_panel.clear_eval_data()
        self._render_widget.clear_hud()
        seed = self._controls._seed_spin.value()
        self._evaluation_worker.configure(
            model=self._trained_model,
            env_id=self._current_env_id,
            n_eval_episodes=n_episodes,
            seed=seed if seed>0 else None,
            render_delay_ms=16,
        )
        self._set_app_state("evaluating")
        self._statusbar_label.setText(f"Evaluating {self._current_algo_name}...")
        self._drawer.close_drawer()
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

    def _clear_model(self):
        self._trained_model = None
        self._render_widget.clear_hud()
        self._set_app_state("idle")
        self._statusbar_label.setText("Model cleared")
        QMessageBox.information(self, "Model Cleared", "The trained model has been deleted.")

    def _load_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Model", "saved_models", "SB3 (*.zip)")
        if not path: return
        algo = self._controls.get_selected_algorithm()
        if algo not in ALGORITHM_REGISTRY:
            QMessageBox.warning(self, "Algorithm", "Select the algorithm first.")
            return
        try:
            cls = import_algorithm_class(algo)
            self._trained_model = cls.load(path)
            self._current_env_id = self._controls.get_selected_env_id()
            self._current_algo_name = algo
            self._controls.set_state("done")
            self._set_app_state("done")
            self._statusbar_label.setText(f"Loaded {os.path.basename(path)}")
            QMessageBox.information(self, "Model Loaded", f"Successfully loaded {algo} model.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _set_app_state(self, state):
        self._controls.set_state(state)
        self._status_pill.set_state(state)

    def _on_training_complete(self, model_path):
        self._trained_model = self._training_worker.trained_model
        self._set_app_state("done")
        self._statusbar_label.setText(f"Training done. Model saved to {model_path}")

    def _on_training_error(self, err):
        self._set_app_state("error")
        self._statusbar_label.setText("Training failed")
        QMessageBox.critical(self, "Error", err)

    def _on_training_stopped(self):
        if self._training_worker.trained_model:
            self._trained_model = self._training_worker.trained_model
            self._set_app_state("done")
            self._statusbar_label.setText("Training stopped (partial model)")
        else:
            self._set_app_state("idle")
            self._statusbar_label.setText("Stopped")

    def _on_eval_step(self, info):
        self._render_widget.update_hud(**info)

    def _on_eval_episode_complete(self, idx, reward, length):
        self._metrics_panel.add_eval_episode(idx, reward, length)
        self._statusbar_label.setText(f"Episode {idx} reward: {reward:.2f}")

    def _on_evaluation_complete(self, results):
        self._set_app_state("eval_done")
        mean_r = sum(r["reward"] for r in results)/len(results) if results else 0
        self._statusbar_label.setText(f"Eval complete — mean reward: {mean_r:.2f}")

    def _on_eval_error(self, err):
        self._set_app_state("error")
        QMessageBox.critical(self, "Eval error", err)

    def _on_eval_stopped(self):
        self._set_app_state("done")
        self._statusbar_label.setText("Evaluation stopped")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "_drawer"): self._drawer.ensure_geometry()

    def closeEvent(self, e):
        self._stop_all()
        self._training_worker.wait(2000)
        self._evaluation_worker.wait(2000)
        e.accept()