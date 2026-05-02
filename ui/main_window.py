"""
Main Window — assembles all panels into a split-pane layout.
Handles wiring between controls, workers, and display panels.
"""

import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QFileDialog, QStatusBar, QLabel,
)

from ui.theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, SUCCESS, FONT_FAMILY,
)
from ui.metrics_panel import MetricsPanel
from ui.hardware_panel import HardwarePanel
from ui.environment_render import EnvironmentRenderWidget
from ui.environment_controls import EnvironmentControls
from core.training_worker import TrainingWorker
from core.evaluation_worker import EvaluationWorker
from core.algorithms import import_algorithm_class, ALGORITHM_REGISTRY


class MainWindow(QMainWindow):
    """
    Main application window for the RL Dashboard.
    
    Layout:
        ┌─────────────────┬──────────────────────┐
        │  Left Panel      │  Right Panel          │
        │  ┌─────────────┐ │  ┌──────────────────┐ │
        │  │ Metrics      │ │  │ Controls          │ │
        │  │ Panel        │ │  │                  │ │
        │  │ (65%)        │ │  ├──────────────────┤ │
        │  │             │ │  │ Environment       │ │
        │  ├─────────────┤ │  │ Render           │ │
        │  │ Hardware     │ │  │                  │ │
        │  │ Panel (35%)  │ │  │                  │ │
        │  └─────────────┘ │  └──────────────────┘ │
        └─────────────────┴──────────────────────┘
    """

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
        """Configure the main window properties."""
        self.setWindowTitle("RL Dashboard — Reinforcement Learning Prototyping Tool")
        self.setMinimumSize(1200, 700)
        self.resize(1600, 900)
        
        # Status bar
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar_label = QLabel("Ready")
        self._statusbar.addPermanentWidget(self._statusbar_label)

    def _setup_workers(self):
        """Create background worker threads."""
        self._training_worker = TrainingWorker(self)
        self._evaluation_worker = EvaluationWorker(self)

    def _setup_ui(self):
        """Build the main layout with splitter panels."""
        central = QWidget()
        central.setStyleSheet(f"background-color: {BG_PRIMARY}; border: none;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 6)
        main_layout.setSpacing(0)

        # ── Header ──
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet(f"""
            background-color: {BG_SECONDARY};
            border: 1px solid {BORDER};
            border-radius: 12px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        app_title = QLabel("🧠  RL Dashboard")
        app_title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(app_title)

        subtitle = QLabel("Reinforcement Learning Prototyping Tool")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 400;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()

        # Version badge
        version_badge = QLabel("v1.0")
        version_badge.setStyleSheet(f"""
            color: {ACCENT};
            background-color: {ACCENT}22;
            border: 1px solid {ACCENT}44;
            border-radius: 6px;
            padding: 2px 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        header_layout.addWidget(version_badge)

        main_layout.addWidget(header)
        main_layout.addSpacing(8)

        # ── Main Splitter ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {BORDER};
                margin: 4px 2px;
                border-radius: 1px;
            }}
            QSplitter::handle:hover {{
                background-color: {ACCENT};
            }}
        """)

        # ── Left Panel ──
        left_panel = QWidget()
        left_panel.setStyleSheet("background: transparent; border: none;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(8)

        self._metrics_panel = MetricsPanel()
        left_layout.addWidget(self._metrics_panel, 65)

        self._hardware_panel = HardwarePanel()
        left_layout.addWidget(self._hardware_panel, 35)

        splitter.addWidget(left_panel)

        # ── Right Panel ──
        right_panel = QWidget()
        right_panel.setStyleSheet("background: transparent; border: none;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(8)

        self._controls = EnvironmentControls()
        right_layout.addWidget(self._controls, 45)

        self._render_widget = EnvironmentRenderWidget()
        right_layout.addWidget(self._render_widget, 55)

        splitter.addWidget(right_panel)

        # Set initial splitter proportions (45% left, 55% right)
        splitter.setSizes([720, 880])
        main_layout.addWidget(splitter, 1)

    # ─── Signal Wiring ────────────────────────────────────────────────────────

    def _connect_signals(self):
        """Wire all signals between controls, workers, and display panels."""
        
        # Controls → Main Window
        self._controls.start_training_requested.connect(self._start_training)
        self._controls.stop_training_requested.connect(self._stop_all)
        self._controls.start_evaluation_requested.connect(self._start_evaluation)
        self._controls.reset_requested.connect(self._reset)
        self._controls._load_btn.clicked.connect(self._load_model)

        # Training Worker → UI
        self._training_worker.metrics_updated.connect(
            self._metrics_panel.update_training_metrics
        )
        self._training_worker.progress_updated.connect(
            self._controls.update_progress
        )
        self._training_worker.training_complete.connect(self._on_training_complete)
        self._training_worker.training_error.connect(self._on_training_error)
        self._training_worker.training_stopped.connect(self._on_training_stopped)

        # Evaluation Worker → UI
        self._evaluation_worker.frame_ready.connect(
            self._render_widget.update_frame
        )
        self._evaluation_worker.eval_step_info.connect(self._on_eval_step)
        self._evaluation_worker.eval_episode_complete.connect(
            self._on_eval_episode_complete
        )
        self._evaluation_worker.evaluation_complete.connect(
            self._on_evaluation_complete
        )
        self._evaluation_worker.evaluation_error.connect(self._on_eval_error)
        self._evaluation_worker.evaluation_stopped.connect(
            self._on_eval_stopped
        )

    # ─── Actions ──────────────────────────────────────────────────────────────

    def _start_training(self, config: dict):
        """Start training with the given configuration."""
        self._current_env_id = config["env_id"]
        self._current_algo_name = config["algo_name"]

        # Clear previous data
        self._metrics_panel.clear_training_data()
        self._metrics_panel.clear_eval_data()
        self._render_widget.show_placeholder(config["env_id"])
        self._trained_model = None

        # Configure worker
        self._training_worker.configure(
            env_id=config["env_id"],
            algo_name=config["algo_name"],
            total_timesteps=config["total_timesteps"],
            seed=config.get("seed"),
            hyperparams=config.get("hyperparams", {}),
            save_dir=config.get("save_dir", "saved_models"),
        )

        # Update UI state
        self._controls.set_state("training")
        self._statusbar_label.setText(
            f"Training {config['algo_name']} on {config['env_id']}..."
        )

        # Start training thread
        self._training_worker.start()

    def _start_evaluation(self, n_episodes: int):
        """Start evaluation with the trained model."""
        if self._trained_model is None:
            QMessageBox.warning(
                self, "No Model",
                "No trained model available. Please train first or load a model."
            )
            return

        # Clear previous eval data
        self._metrics_panel.clear_eval_data()
        self._render_widget.clear_hud()

        # Configure worker
        seed_val = self._controls._seed_spin.value()
        self._evaluation_worker.configure(
            model=self._trained_model,
            env_id=self._current_env_id,
            n_eval_episodes=n_episodes,
            seed=seed_val if seed_val > 0 else None,
            render_delay_ms=16,
        )

        # Update UI state
        self._controls.set_state("evaluating")
        self._statusbar_label.setText(
            f"Evaluating {self._current_algo_name} for {n_episodes} episodes..."
        )

        # Start evaluation thread
        self._evaluation_worker.start()

    def _stop_all(self):
        """Stop any running training or evaluation."""
        self._training_worker.stop()
        self._evaluation_worker.stop()
        self._statusbar_label.setText("Stopping...")

    def _reset(self):
        """Reset everything to initial state."""
        self._stop_all()
        self._trained_model = None
        self._current_env_id = ""
        self._current_algo_name = ""
        self._metrics_panel.clear_all()
        self._render_widget.show_placeholder("")
        self._render_widget.clear_hud()
        self._controls.set_state("idle")
        self._statusbar_label.setText("Ready")

    def _load_model(self):
        """Load a previously saved model from disk."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Trained Model",
            "saved_models",
            "SB3 Model (*.zip);;All Files (*)",
        )
        if not file_path:
            return

        # Determine which algorithm to use for loading
        algo_name = self._controls.get_selected_algorithm()
        if algo_name not in ALGORITHM_REGISTRY:
            QMessageBox.warning(
                self, "Algorithm Required",
                "Please select the algorithm that was used to train this model."
            )
            return

        try:
            cls = import_algorithm_class(algo_name)
            self._trained_model = cls.load(file_path)
            self._current_env_id = self._controls.get_selected_env_id()
            self._current_algo_name = algo_name
            self._controls.set_state("done")
            self._statusbar_label.setText(f"Loaded model from {os.path.basename(file_path)}")
            QMessageBox.information(
                self, "Model Loaded",
                f"Successfully loaded {algo_name} model.\nYou can now evaluate it."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Load Error",
                f"Failed to load model:\n{str(e)}"
            )

    # ─── Callbacks ────────────────────────────────────────────────────────────

    def _on_training_complete(self, model_path: str):
        """Called when training finishes successfully."""
        self._trained_model = self._training_worker.trained_model
        self._controls.set_state("done")
        self._statusbar_label.setText(
            f"Training complete! Model saved to {model_path}"
        )

    def _on_training_error(self, error_msg: str):
        """Called when training encounters an error."""
        self._controls.set_state("error")
        self._statusbar_label.setText("Training failed!")
        QMessageBox.critical(
            self, "Training Error",
            f"Training encountered an error:\n\n{error_msg[:500]}"
        )

    def _on_training_stopped(self):
        """Called when training is cancelled by the user."""
        # Still keep the partially trained model if available
        if self._training_worker.trained_model is not None:
            self._trained_model = self._training_worker.trained_model
            self._controls.set_state("done")
            self._statusbar_label.setText("Training stopped — partial model available")
        else:
            self._controls.set_state("idle")
            self._statusbar_label.setText("Training stopped")

    def _on_eval_step(self, step_info: dict):
        """Update the render widget HUD during evaluation."""
        self._render_widget.update_hud(**step_info)

    def _on_eval_episode_complete(self, idx: int, reward: float, length: int):
        """Called after each evaluation episode completes."""
        self._metrics_panel.add_eval_episode(idx, reward, length)
        self._statusbar_label.setText(
            f"Evaluation episode {idx} complete — Reward: {reward:.2f}"
        )

    def _on_evaluation_complete(self, results: list):
        """Called when all evaluation episodes are done."""
        self._controls.set_state("eval_done")
        total = len(results)
        mean_reward = sum(r["reward"] for r in results) / total if total else 0
        self._statusbar_label.setText(
            f"Evaluation complete — {total} episodes, Mean Reward: {mean_reward:.2f}"
        )

    def _on_eval_error(self, error_msg: str):
        """Called when evaluation encounters an error."""
        self._controls.set_state("error")
        self._statusbar_label.setText("Evaluation failed!")
        QMessageBox.critical(
            self, "Evaluation Error",
            f"Evaluation encountered an error:\n\n{error_msg[:500]}"
        )

    def _on_eval_stopped(self):
        """Called when evaluation is cancelled by the user."""
        self._controls.set_state("done")
        self._statusbar_label.setText("Evaluation stopped")

    # ─── Cleanup ──────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        """Ensure workers are stopped before closing."""
        self._stop_all()
        self._training_worker.wait(2000)
        self._evaluation_worker.wait(2000)
        super().closeEvent(event)
