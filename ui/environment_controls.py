"""
Environment Controls Panel — environment selector, algorithm picker,
hyperparameter editing, training/evaluation launch buttons, and status.
"""

import gymnasium as gym
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
    QProgressBar, QScrollArea, QGroupBox, QLineEdit,
    QSizePolicy, QMessageBox, QFrame,
)

from ui.theme import (
    BG_SECONDARY, BG_TERTIARY, BG_ELEVATED, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED,
    ACCENT, ACCENT_SECONDARY, SUCCESS, WARNING, DANGER,
    FONT_FAMILY,
)
from core.algorithms import (
    ALGORITHM_REGISTRY, get_environment_list, get_compatible_algorithms,
    get_action_space_name,
)


class EnvironmentControls(QWidget):
    """
    Control panel for configuring and launching training/evaluation.

    Signals:
        start_training_requested(dict)  – emitted with full config dict
        stop_training_requested()       – user pressed stop
        start_evaluation_requested(int) – emitted with n_eval_episodes
        reset_requested()               – user pressed reset
    """

    start_training_requested = pyqtSignal(dict)
    stop_training_requested = pyqtSignal()
    start_evaluation_requested = pyqtSignal(int)
    reset_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hyperparam_widgets = {}
        self._current_state = "idle"  # idle, training, evaluating
        self._setup_ui()
        self._populate_environments()
        self._connect_signals()

    # ─── UI Setup ─────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Outer container
        self._container = QWidget()
        self._container.setObjectName("configContainer")
        self._container.setStyleSheet(f"""
            #configContainer {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(12, 8, 12, 12)
        container_layout.setSpacing(8)

        # ── Title ──
        title_row = QWidget()
        title_row.setStyleSheet("background: transparent; border: none;")
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(10)

        accent_bar = QFrame()
        accent_bar.setFixedSize(3, 18)
        accent_bar.setStyleSheet(f"background-color: {ACCENT_SECONDARY}; border-radius: 2px; border: none;")
        title_row_layout.addWidget(accent_bar)

        title = QLabel("Configuration")
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

        # ── Scrollable content ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent; border: none;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 4, 0)
        scroll_layout.setSpacing(8)

        # ── Environment Section ──
        env_group = QGroupBox("Environment")
        env_form = QFormLayout(env_group)
        env_form.setSpacing(8)

        self._env_combo = QComboBox()
        self._env_combo.setMinimumHeight(32)
        self._env_combo.setToolTip("Select a Gymnasium environment")
        env_form.addRow("Environment:", self._env_combo)

        self._env_info_label = QLabel("—")
        self._env_info_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        self._env_info_label.setWordWrap(True)
        env_form.addRow("Action Space:", self._env_info_label)
        scroll_layout.addWidget(env_group)

        # ── Algorithm Section ──
        algo_group = QGroupBox("Algorithm")
        algo_form = QFormLayout(algo_group)
        algo_form.setSpacing(8)

        self._algo_combo = QComboBox()
        self._algo_combo.setMinimumHeight(32)
        self._algo_combo.setToolTip("Select an RL algorithm")
        algo_form.addRow("Algorithm:", self._algo_combo)

        self._algo_info_label = QLabel("—")
        self._algo_info_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        self._algo_info_label.setWordWrap(True)
        algo_form.addRow("Info:", self._algo_info_label)

        self._algo_category_label = QLabel("")
        self._algo_category_label.setStyleSheet(f"""
            color: {ACCENT_SECONDARY};
            font-size: 10px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        algo_form.addRow("Category:", self._algo_category_label)
        scroll_layout.addWidget(algo_group)

        # ── Training Configuration ──
        train_group = QGroupBox("Training")
        train_form = QFormLayout(train_group)
        train_form.setSpacing(8)

        self._timesteps_spin = QSpinBox()
        self._timesteps_spin.setRange(1_000, 10_000_000)
        self._timesteps_spin.setValue(100_000)
        self._timesteps_spin.setSingleStep(10_000)
        self._timesteps_spin.setToolTip("Total training timesteps")
        self._timesteps_spin.setMinimumHeight(32)
        train_form.addRow("Total Timesteps:", self._timesteps_spin)

        self._eval_episodes_spin = QSpinBox()
        self._eval_episodes_spin.setRange(1, 100)
        self._eval_episodes_spin.setValue(5)
        self._eval_episodes_spin.setToolTip("Number of episodes to evaluate with rendering")
        self._eval_episodes_spin.setMinimumHeight(32)
        train_form.addRow("Eval Episodes:", self._eval_episodes_spin)

        self._seed_spin = QSpinBox()
        self._seed_spin.setRange(0, 999999)
        self._seed_spin.setValue(42)
        self._seed_spin.setSpecialValueText("None")
        self._seed_spin.setToolTip("Random seed (0 = no seed)")
        self._seed_spin.setMinimumHeight(32)
        train_form.addRow("Seed:", self._seed_spin)
        scroll_layout.addWidget(train_group)

        # ── Hyperparameters Section ──
        self._hp_group = QGroupBox("Hyperparameters")
        self._hp_layout = QFormLayout(self._hp_group)
        self._hp_layout.setSpacing(6)
        scroll_layout.addWidget(self._hp_group)

        # ── Save/Load Section ──
        save_group = QGroupBox("Model Persistence")
        save_form = QFormLayout(save_group)
        save_form.setSpacing(8)

        save_dir_row = QHBoxLayout()
        self._save_dir_edit = QLineEdit("saved_models")
        self._save_dir_edit.setMinimumHeight(32)
        self._save_dir_edit.setToolTip("Directory to save/load trained models")
        save_dir_row.addWidget(self._save_dir_edit)
        save_form.addRow("Save Dir:", save_dir_row)

        load_row = QHBoxLayout()
        self._load_btn = QPushButton("Load Model")
        self._load_btn.setMinimumHeight(32)
        self._load_btn.setToolTip("Load a previously saved model")
        load_row.addWidget(self._load_btn)
        save_form.addRow(load_row)
        scroll_layout.addWidget(save_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        container_layout.addWidget(scroll, 1)

        # ── Action Buttons — 2×2 grid so labels never get clipped ──
        btn_grid = QGridLayout()
        btn_grid.setSpacing(6)

        self._train_btn = QPushButton("Train")
        self._train_btn.setProperty("cssClass", "primary")
        self._train_btn.setMinimumHeight(36)
        self._train_btn.setToolTip("Start training")
        btn_grid.addWidget(self._train_btn, 0, 0)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setProperty("cssClass", "danger")
        self._stop_btn.setMinimumHeight(36)
        self._stop_btn.setEnabled(False)
        self._stop_btn.setToolTip("Stop training / evaluation")
        btn_grid.addWidget(self._stop_btn, 0, 1)

        self._eval_btn = QPushButton("Evaluate")
        self._eval_btn.setProperty("cssClass", "success")
        self._eval_btn.setMinimumHeight(36)
        self._eval_btn.setEnabled(False)
        self._eval_btn.setToolTip("Run evaluation episodes with rendering")
        btn_grid.addWidget(self._eval_btn, 1, 0)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setMinimumHeight(36)
        self._reset_btn.setToolTip("Clear model, metrics, and render")
        btn_grid.addWidget(self._reset_btn, 1, 1)

        container_layout.addLayout(btn_grid)

        # ── Progress Bar ──
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(20)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("Idle")
        container_layout.addWidget(self._progress_bar)

        # ── Status ──
        self._status_label = QLabel("Idle")
        self._status_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 4px 0;
        """)
        container_layout.addWidget(self._status_label)

        layout.addWidget(self._container)

    # ─── Theme ────────────────────────────────────────────────────────

    def refresh_theme(self):
        """Re-apply inline styles for the current theme."""
        import ui.theme as t
        self._container.setStyleSheet(f"""
            #configContainer {{
                background-color: {t.BG_SECONDARY};
                border: 1px solid {t.BORDER};
                border-radius: 12px;
            }}
        """)

    # ─── Population ───────────────────────────────────────────────────────────

    def _populate_environments(self):
        """Fill the environment combo box with categorised environment IDs."""
        self._env_combo.clear()
        try:
            env_categories = get_environment_list()
            for category, env_ids in env_categories.items():
                # Category header — disabled, no UserRole data
                self._env_combo.addItem(f"  {category.upper()}")
                idx = self._env_combo.count() - 1
                item = self._env_combo.model().item(idx)
                item.setEnabled(False)
                item.setData(None, Qt.ItemDataRole.UserRole)

                for env_id in env_ids:
                    self._env_combo.addItem(env_id)
                    self._env_combo.model().item(
                        self._env_combo.count() - 1
                    ).setData(env_id, Qt.ItemDataRole.UserRole)
        except Exception:
            for env_id in ["CartPole-v1", "MountainCar-v0", "Pendulum-v1",
                           "Acrobot-v1", "LunarLander-v3"]:
                self._env_combo.addItem(env_id)
                self._env_combo.model().item(
                    self._env_combo.count() - 1
                ).setData(env_id, Qt.ItemDataRole.UserRole)

    def _populate_algorithms(self, env_id: str):
        """Fill the algorithm combo with algorithms compatible with the env."""
        self._algo_combo.clear()
        compatible = get_compatible_algorithms(env_id)

        if not compatible:
            self._algo_combo.addItem("No compatible algorithms")
            return

        # Group by category
        categories = {}
        for name in compatible:
            cat = ALGORITHM_REGISTRY[name]["category"]
            categories.setdefault(cat, []).append(name)

        for cat, algos in categories.items():
            # Category header — disabled, no UserRole data
            self._algo_combo.addItem(f"  {cat.upper()}")
            idx = self._algo_combo.count() - 1
            item = self._algo_combo.model().item(idx)
            item.setEnabled(False)
            item.setData(None, Qt.ItemDataRole.UserRole)

            for algo in algos:
                self._algo_combo.addItem(algo)
                self._algo_combo.model().item(
                    self._algo_combo.count() - 1
                ).setData(algo, Qt.ItemDataRole.UserRole)

    def _populate_hyperparams(self, algo_name: str):
        """Build hyperparameter input widgets for the selected algorithm."""
        # Clear existing widgets
        while self._hp_layout.rowCount() > 0:
            self._hp_layout.removeRow(0)
        self._hyperparam_widgets.clear()

        if algo_name not in ALGORITHM_REGISTRY:
            return

        meta = ALGORITHM_REGISTRY[algo_name]
        hyperparams = meta.get("hyperparams", {})

        for key, cfg in hyperparams.items():
            hp_type = cfg.get("type", "float")

            if hp_type == "float":
                widget = QDoubleSpinBox()
                widget.setRange(cfg.get("min", 0.0), cfg.get("max", 1.0))
                widget.setValue(cfg.get("default", 0.0))
                widget.setSingleStep(cfg.get("step", 0.001))
                widget.setDecimals(cfg.get("decimals", 4))
                widget.setMinimumHeight(28)
            elif hp_type == "int":
                widget = QSpinBox()
                widget.setRange(cfg.get("min", 0), cfg.get("max", 10000000))
                widget.setValue(cfg.get("default", 0))
                widget.setMinimumHeight(28)
            elif hp_type == "str":
                widget = QLineEdit(str(cfg.get("default", "")))
                widget.setMinimumHeight(28)
            else:
                continue

            self._hyperparam_widgets[key] = widget
            
            # Clean label formatting
            label = key.replace("_", " ").title()
            self._hp_layout.addRow(f"{label}:", widget)

    # ─── Getters ──────────────────────────────────────────────────────────────

    def get_selected_env_id(self) -> str:
        """Return the currently selected environment ID."""
        data = self._env_combo.currentData(Qt.ItemDataRole.UserRole)
        return data or ""

    def get_selected_algorithm(self) -> str:
        """Return the currently selected algorithm name."""
        data = self._algo_combo.currentData(Qt.ItemDataRole.UserRole)
        return data or ""

    def get_hyperparams(self) -> dict:
        """Return current hyperparameter values from the UI widgets."""
        params = {}
        for key, widget in self._hyperparam_widgets.items():
            if isinstance(widget, QDoubleSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QLineEdit):
                params[key] = widget.text()
        return params

    def get_training_config(self) -> dict:
        """Return the full training configuration dict."""
        seed_val = self._seed_spin.value()
        return {
            "env_id": self.get_selected_env_id(),
            "algo_name": self.get_selected_algorithm(),
            "total_timesteps": self._timesteps_spin.value(),
            "n_eval_episodes": self._eval_episodes_spin.value(),
            "seed": seed_val if seed_val > 0 else None,
            "hyperparams": self.get_hyperparams(),
            "save_dir": self._save_dir_edit.text().strip() or "saved_models",
        }

    # ─── State Management ─────────────────────────────────────────────────────

    def set_state(self, state: str):
        """
        Update the UI state: 'idle', 'training', 'evaluating', 'done', 'error'.
        Enables/disables buttons accordingly.
        """
        self._current_state = state

        if state == "idle":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(0)
            self._progress_bar.setFormat("Idle")
            self._status_label.setText("Idle")
            self._status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600; background: transparent; border: none;")

        elif state == "training":
            self._train_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(False)
            self._env_combo.setEnabled(False)
            self._algo_combo.setEnabled(False)
            self._progress_bar.setFormat("Training...  %p%")
            self._status_label.setText("Training in progress")
            self._status_label.setStyleSheet(f"color: {WARNING}; font-size: 11px; font-weight: 600; background: transparent; border: none;")

        elif state == "evaluating":
            self._train_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(False)
            self._progress_bar.setFormat("Evaluating...")
            self._status_label.setText("Evaluating agent")
            self._status_label.setStyleSheet(f"color: {ACCENT_SECONDARY}; font-size: 11px; font-weight: 600; background: transparent; border: none;")

        elif state == "done":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(True)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(100)
            self._progress_bar.setFormat("Done")
            self._status_label.setText("Done — ready to evaluate")
            self._status_label.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; font-weight: 600; background: transparent; border: none;")

        elif state == "error":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(0)
            self._progress_bar.setFormat("Error")
            self._status_label.setText("Error occurred")
            self._status_label.setStyleSheet(f"color: {DANGER}; font-size: 11px; font-weight: 600; background: transparent; border: none;")

        elif state == "eval_done":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(True)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(100)
            self._progress_bar.setFormat("Evaluation Complete")
            self._status_label.setText("Evaluation complete")
            self._status_label.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; font-weight: 600; background: transparent; border: none;")

    def update_progress(self, value: int):
        """Update the progress bar (0-100)."""
        self._progress_bar.setValue(value)

    # ─── Signal Connections ───────────────────────────────────────────────────

    def _connect_signals(self):
        self._env_combo.currentTextChanged.connect(self._on_env_changed)
        self._algo_combo.currentTextChanged.connect(self._on_algo_changed)
        self._train_btn.clicked.connect(self._on_train_clicked)
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        self._eval_btn.clicked.connect(self._on_eval_clicked)
        self._reset_btn.clicked.connect(self._on_reset_clicked)

    def _on_env_changed(self, _text: str):
        env_id = self._env_combo.currentData(Qt.ItemDataRole.UserRole)
        if not env_id:
            return

        # Update action space info
        try:
            space_name = get_action_space_name(env_id)
            self._env_info_label.setText(space_name)
        except Exception:
            self._env_info_label.setText("Unknown")

        # Update compatible algorithms
        self._populate_algorithms(env_id)

    def _on_algo_changed(self, _text: str):
        algo_name = self._algo_combo.currentData(Qt.ItemDataRole.UserRole)
        if not algo_name:
            return

        if algo_name in ALGORITHM_REGISTRY:
            meta = ALGORITHM_REGISTRY[algo_name]
            self._algo_info_label.setText(meta.get("description", ""))
            self._algo_category_label.setText(meta.get("category", ""))
            self._populate_hyperparams(algo_name)
        else:
            self._algo_info_label.setText("—")
            self._algo_category_label.setText("")

    def _on_train_clicked(self):
        config = self.get_training_config()

        # Validate — UserRole returns "" for category headers
        if not config["env_id"]:
            QMessageBox.warning(self, "Invalid Config", "Please select an environment.")
            return
        if not config["algo_name"]:
            QMessageBox.warning(self, "Invalid Config", "Please select an algorithm.")
            return
        
        self.start_training_requested.emit(config)

    def _on_stop_clicked(self):
        self.stop_training_requested.emit()

    def _on_eval_clicked(self):
        n = self._eval_episodes_spin.value()
        self.start_evaluation_requested.emit(n)

    def _on_reset_clicked(self):
        self.reset_requested.emit()
