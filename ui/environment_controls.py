"""
Environment Controls Panel — environment selector, algorithm picker,
hyperparameter editing, training/evaluation launch buttons, and status.

Redesigned for use as a floating drawer:
  - Action buttons (Train / Stop / Eval / Reset) pinned at the TOP for quick access
  - Configuration sections below in a scrollable area
  - Progress bar + status label at the bottom
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


class _SectionLabel(QLabel):
    """Styled section separator label inside the config drawer."""
    def __init__(self, text: str, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_DISABLED};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
                background: transparent;
                border: none;
                padding: 6px 0 2px 0;
            }}
        """)


class EnvironmentControls(QWidget):
    """
    Configuration drawer panel for RL Dashboard.

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
        self._current_state = "idle"
        self._setup_ui()
        self._populate_environments()
        self._connect_signals()

    # ─── UI Setup ─────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Outer panel container
        self._container = QWidget()
        self._container.setObjectName("panelContainer")
        self._container.setStyleSheet(f"""
            #panelContainer {{
                background-color: {BG_SECONDARY};
                border: none;
                border-radius: 0px;
            }}
        """)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(14, 12, 14, 14)
        container_layout.setSpacing(10)

        # ── Drawer Title ──────────────────────────────────────────────────────
        title_row = QWidget()
        title_row.setStyleSheet("background: transparent; border: none;")
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(10)

        accent_bar = QFrame()
        accent_bar.setFixedSize(3, 18)
        accent_bar.setStyleSheet(
            f"background-color: {ACCENT_SECONDARY}; border-radius: 2px; border: none;"
        )
        title_row_layout.addWidget(accent_bar)

        title = QLabel("Configuration")
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 15px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        title_row_layout.addWidget(title)
        title_row_layout.addStretch()
        container_layout.addWidget(title_row)

        # ── Action Buttons (pinned at top, always visible) ────────────────────
        btn_grid = QGridLayout()
        btn_grid.setSpacing(8)
        btn_grid.setContentsMargins(0, 0, 0, 0)

        self._train_btn = QPushButton("▶  Train")
        self._train_btn.setObjectName("primaryButton")
        self._train_btn.setMinimumHeight(40)
        self._train_btn.setToolTip("Start training with current configuration")
        self._train_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background-color: #7d6df0; }}
            QPushButton:pressed {{ background-color: #5a4bd6; }}
            QPushButton:disabled {{
                background-color: {BG_ELEVATED};
                color: {TEXT_DISABLED};
                border: 1px solid {BORDER};
            }}
        """)
        btn_grid.addWidget(self._train_btn, 0, 0)

        self._stop_btn = QPushButton("■  Stop")
        self._stop_btn.setObjectName("dangerButton")
        self._stop_btn.setMinimumHeight(40)
        self._stop_btn.setEnabled(False)
        self._stop_btn.setToolTip("Stop training or evaluation")
        self._stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background-color: #e8816b; }}
            QPushButton:pressed {{ background-color: #c55f45; }}
            QPushButton:disabled {{
                background-color: {BG_ELEVATED};
                color: {TEXT_DISABLED};
                border: 1px solid {BORDER};
            }}
        """)
        btn_grid.addWidget(self._stop_btn, 0, 1)

        self._eval_btn = QPushButton("◆  Evaluate")
        self._eval_btn.setObjectName("successButton")
        self._eval_btn.setMinimumHeight(40)
        self._eval_btn.setEnabled(False)
        self._eval_btn.setToolTip("Run evaluation episodes with environment rendering")
        self._eval_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background-color: #00cc9e; }}
            QPushButton:pressed {{ background-color: #009a78; }}
            QPushButton:disabled {{
                background-color: {BG_ELEVATED};
                color: {TEXT_DISABLED};
                border: 1px solid {BORDER};
            }}
        """)
        btn_grid.addWidget(self._eval_btn, 1, 0)

        self._reset_btn = QPushButton("↺  Reset")
        self._reset_btn.setMinimumHeight(40)
        self._reset_btn.setToolTip("Clear model, metrics, and render view")
        self._reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_ELEVATED};
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {BG_TERTIARY};
                color: {TEXT_PRIMARY};
                border-color: {ACCENT};
            }}
            QPushButton:pressed {{ background-color: {ACCENT}; color: white; }}
        """)
        btn_grid.addWidget(self._reset_btn, 1, 1)

        container_layout.addLayout(btn_grid)

        # ── Progress Bar ──────────────────────────────────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_ELEVATED};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT};
                border-radius: 3px;
            }}
        """)
        container_layout.addWidget(self._progress_bar)

        # ── Status Label ──────────────────────────────────────────────────────
        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)

        self._status_dot = QFrame()
        self._status_dot.setFixedSize(6, 6)
        self._status_dot.setStyleSheet(
            f"background-color: {TEXT_SECONDARY}; border-radius: 3px; border: none;"
        )
        status_row.addWidget(self._status_dot)
        status_row.addSpacing(6)

        self._status_label = QLabel("Idle")
        self._status_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        status_row.addWidget(self._status_label)
        status_row.addStretch()
        container_layout.addLayout(status_row)

        # ── Horizontal separator ──────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER}; border: none; max-height: 1px;")
        container_layout.addWidget(sep)

        # ── Scrollable Config Content ─────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent; border: none;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 4, 0)
        scroll_layout.setSpacing(6)

        # ── Environment ──────────────────────────────────────────────────────
        scroll_layout.addWidget(_SectionLabel("Environment"))

        env_group = QGroupBox()
        env_form = QFormLayout(env_group)
        env_form.setSpacing(8)
        env_form.setContentsMargins(10, 12, 10, 12)

        self._env_combo = QComboBox()
        self._env_combo.setMinimumHeight(32)
        self._env_combo.setToolTip("Select a Gymnasium environment")
        env_form.addRow("Environment:", self._env_combo)

        self._env_info_label = QLabel("—")
        self._env_info_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY}; font-size: 11px;
            background: transparent; border: none;
        """)
        self._env_info_label.setWordWrap(True)
        env_form.addRow("Action Space:", self._env_info_label)
        scroll_layout.addWidget(env_group)

        # ── Algorithm ────────────────────────────────────────────────────────
        scroll_layout.addWidget(_SectionLabel("Algorithm"))

        algo_group = QGroupBox()
        algo_form = QFormLayout(algo_group)
        algo_form.setSpacing(8)
        algo_form.setContentsMargins(10, 12, 10, 12)

        self._algo_combo = QComboBox()
        self._algo_combo.setMinimumHeight(32)
        self._algo_combo.setToolTip("Select an RL algorithm compatible with the environment")
        algo_form.addRow("Algorithm:", self._algo_combo)

        self._algo_info_label = QLabel("—")
        self._algo_info_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY}; font-size: 11px;
            background: transparent; border: none;
        """)
        self._algo_info_label.setWordWrap(True)
        algo_form.addRow("Info:", self._algo_info_label)

        self._algo_category_label = QLabel("")
        self._algo_category_label.setStyleSheet(f"""
            color: {ACCENT_SECONDARY}; font-size: 10px; font-weight: 700;
            background: transparent; border: none;
        """)
        algo_form.addRow("Category:", self._algo_category_label)
        scroll_layout.addWidget(algo_group)

        # ── Training Config ───────────────────────────────────────────────────
        scroll_layout.addWidget(_SectionLabel("Training"))

        train_group = QGroupBox()
        train_form = QFormLayout(train_group)
        train_form.setSpacing(8)
        train_form.setContentsMargins(10, 12, 10, 12)

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
        self._eval_episodes_spin.setToolTip("Number of evaluation episodes to run with rendering")
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

        # ── Hyperparameters ───────────────────────────────────────────────────
        scroll_layout.addWidget(_SectionLabel("Hyperparameters"))

        self._hp_group = QGroupBox()
        self._hp_layout = QFormLayout(self._hp_group)
        self._hp_layout.setSpacing(6)
        self._hp_layout.setContentsMargins(10, 12, 10, 12)
        scroll_layout.addWidget(self._hp_group)

        # ── Model Persistence ─────────────────────────────────────────────────
        scroll_layout.addWidget(_SectionLabel("Model Persistence"))

        save_group = QGroupBox()
        save_form = QFormLayout(save_group)
        save_form.setSpacing(8)
        save_form.setContentsMargins(10, 12, 10, 12)

        save_dir_row = QHBoxLayout()
        self._save_dir_edit = QLineEdit("saved_models")
        self._save_dir_edit.setMinimumHeight(32)
        self._save_dir_edit.setToolTip("Directory to save / load trained models")
        save_dir_row.addWidget(self._save_dir_edit)
        save_form.addRow("Save Dir:", save_dir_row)

        load_row = QHBoxLayout()
        self._load_btn = QPushButton("↥  Load Model")
        self._load_btn.setMinimumHeight(34)
        self._load_btn.setToolTip("Load a previously saved model (.zip)")
        load_row.addWidget(self._load_btn)
        save_form.addRow(load_row)
        scroll_layout.addWidget(save_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        container_layout.addWidget(scroll, 1)

        layout.addWidget(self._container)

    # ─── Population ───────────────────────────────────────────────────────────

    def _populate_environments(self):
        self._env_combo.clear()
        try:
            env_categories = get_environment_list()
            for category, env_ids in env_categories.items():
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
        self._algo_combo.clear()
        compatible = get_compatible_algorithms(env_id)
        if not compatible:
            self._algo_combo.addItem("No compatible algorithms")
            return
        categories = {}
        for name in compatible:
            cat = ALGORITHM_REGISTRY[name]["category"]
            categories.setdefault(cat, []).append(name)
        for cat, algos in categories.items():
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
            label = key.replace("_", " ").title()
            self._hp_layout.addRow(f"{label}:", widget)

    # ─── Getters ──────────────────────────────────────────────────────────────

    def get_selected_env_id(self) -> str:
        data = self._env_combo.currentData(Qt.ItemDataRole.UserRole)
        return data or ""

    def get_selected_algorithm(self) -> str:
        data = self._algo_combo.currentData(Qt.ItemDataRole.UserRole)
        return data or ""

    def get_hyperparams(self) -> dict:
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
        Update UI controls for the given state:
        'idle' | 'training' | 'evaluating' | 'done' | 'eval_done' | 'error'
        """
        self._current_state = state

        _COLOR = {
            "idle":       TEXT_SECONDARY,
            "training":   WARNING,
            "evaluating": ACCENT_SECONDARY,
            "done":       SUCCESS,
            "eval_done":  SUCCESS,
            "error":      DANGER,
        }
        _LABEL = {
            "idle":       "Idle",
            "training":   "Training in progress",
            "evaluating": "Evaluating agent",
            "done":       "Done — ready to evaluate",
            "eval_done":  "Evaluation complete",
            "error":      "Error occurred",
        }

        color = _COLOR.get(state, TEXT_SECONDARY)
        label = _LABEL.get(state, state.capitalize())

        self._status_dot.setStyleSheet(
            f"background-color: {color}; border-radius: 3px; border: none;"
        )
        self._status_label.setText(label)
        self._status_label.setStyleSheet(f"""
            color: {color}; font-size: 11px; font-weight: 600;
            background: transparent; border: none;
        """)

        if state == "idle":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(0)

        elif state == "training":
            self._train_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(False)
            self._env_combo.setEnabled(False)
            self._algo_combo.setEnabled(False)

        elif state == "evaluating":
            self._train_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(False)

        elif state == "done":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(True)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(100)

        elif state == "error":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(False)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(0)

        elif state == "eval_done":
            self._train_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._eval_btn.setEnabled(True)
            self._reset_btn.setEnabled(True)
            self._env_combo.setEnabled(True)
            self._algo_combo.setEnabled(True)
            self._progress_bar.setValue(100)

    def update_progress(self, value: int):
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
        try:
            space_name = get_action_space_name(env_id)
            self._env_info_label.setText(space_name)
        except Exception:
            self._env_info_label.setText("Unknown")
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