import gymnasium as gym
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
    QProgressBar, QScrollArea, QGroupBox, QLineEdit, QCheckBox,
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
    def __init__(self, text: str, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_DISABLED};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 8px 0 2px 0;
            }}
        """)

class EnvironmentControls(QWidget):
    start_training_requested = pyqtSignal(dict)
    stop_training_requested = pyqtSignal()
    start_evaluation_requested = pyqtSignal(int)
    reset_requested = pyqtSignal()
    clear_model_requested = pyqtSignal()   # nouveau signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hyperparam_widgets = {}
        self._current_state = "idle"
        self._setup_ui()
        self._populate_environments()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._container = QWidget()
        self._container.setObjectName("panelContainer")
        self._container.setStyleSheet(f"#panelContainer {{ background: {BG_SECONDARY}; border: none; border-radius: 0; }}")
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(14, 12, 14, 14)
        container_layout.setSpacing(10)

        # Titre
        title_row = QWidget()
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        accent_bar = QFrame()
        accent_bar.setFixedSize(3, 18)
        accent_bar.setStyleSheet(f"background: {ACCENT_SECONDARY}; border-radius: 2px;")
        title_layout.addWidget(accent_bar)
        title = QLabel("Configuration")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 700;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        container_layout.addWidget(title_row)

        # Boutons actions
        btn_grid = QGridLayout()
        btn_grid.setSpacing(8)
        self._train_btn = QPushButton("▶  Train")
        self._train_btn.setObjectName("primaryButton")
        self._train_btn.setMinimumHeight(40)
        self._stop_btn = QPushButton("■  Stop")
        self._stop_btn.setObjectName("dangerButton")
        self._stop_btn.setEnabled(False)
        self._eval_btn = QPushButton("◆  Evaluate")
        self._eval_btn.setObjectName("successButton")
        self._eval_btn.setEnabled(False)
        self._reset_btn = QPushButton("↺  Reset")
        self._reset_btn.setMinimumHeight(40)

        btn_grid.addWidget(self._train_btn, 0, 0)
        btn_grid.addWidget(self._stop_btn, 0, 1)
        btn_grid.addWidget(self._eval_btn, 1, 0)
        btn_grid.addWidget(self._reset_btn, 1, 1)
        container_layout.addLayout(btn_grid)

        # Progress + status
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{ background: {BG_ELEVATED}; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
        """)
        container_layout.addWidget(self._progress_bar)

        status_row = QHBoxLayout()
        self._status_dot = QFrame()
        self._status_dot.setFixedSize(6, 6)
        self._status_dot.setStyleSheet(f"background: {TEXT_SECONDARY}; border-radius: 3px;")
        status_row.addWidget(self._status_dot)
        self._status_label = QLabel("Idle")
        self._status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        status_row.addWidget(self._status_label)
        status_row.addStretch()
        container_layout.addLayout(status_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        container_layout.addWidget(sep)

        # Scroll content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)

        # Environment
        scroll_layout.addWidget(_SectionLabel("Environment"))
        env_group = QGroupBox()
        env_form = QFormLayout(env_group)
        self._env_combo = QComboBox()
        self._env_info_label = QLabel("—")
        env_form.addRow("Environment:", self._env_combo)
        env_form.addRow("Action Space:", self._env_info_label)
        scroll_layout.addWidget(env_group)

        # Algorithm
        scroll_layout.addWidget(_SectionLabel("Algorithm"))
        algo_group = QGroupBox()
        algo_form = QFormLayout(algo_group)
        self._algo_combo = QComboBox()
        self._algo_info_label = QLabel("—")
        self._algo_category_label = QLabel("")
        algo_form.addRow("Algorithm:", self._algo_combo)
        algo_form.addRow("Info:", self._algo_info_label)
        algo_form.addRow("Category:", self._algo_category_label)
        scroll_layout.addWidget(algo_group)

        # Training
        scroll_layout.addWidget(_SectionLabel("Training"))
        train_group = QGroupBox()
        train_form = QFormLayout(train_group)
        self._timesteps_spin = QSpinBox()
        self._timesteps_spin.setRange(1000, 10_000_000)
        self._timesteps_spin.setValue(100_000)
        self._eval_episodes_spin = QSpinBox()
        self._eval_episodes_spin.setRange(1, 100)
        self._eval_episodes_spin.setValue(5)
        self._seed_spin = QSpinBox()
        self._seed_spin.setRange(0, 999999)
        self._seed_spin.setValue(42)
        train_form.addRow("Total Timesteps:", self._timesteps_spin)
        train_form.addRow("Eval Episodes:", self._eval_episodes_spin)
        train_form.addRow("Seed:", self._seed_spin)
        scroll_layout.addWidget(train_group)

        # Hyperparams
        scroll_layout.addWidget(_SectionLabel("Hyperparameters"))
        self._hp_group = QGroupBox()
        self._hp_layout = QFormLayout(self._hp_group)
        scroll_layout.addWidget(self._hp_group)

        # Model Persistence
        scroll_layout.addWidget(_SectionLabel("Model Persistence"))
        save_group = QGroupBox()
        save_form = QFormLayout(save_group)
        self._save_dir_edit = QLineEdit("saved_models")
        save_form.addRow("Save Dir:", self._save_dir_edit)
        load_row = QHBoxLayout()
        self._load_btn = QPushButton("↥  Load Model")
        self._clear_model_btn = QPushButton("🗑  Clear Model")   # NOUVEAU
        self._clear_model_btn.setToolTip("Delete the currently loaded model")
        self._clear_model_btn.setEnabled(False)
        load_row.addWidget(self._load_btn)
        load_row.addWidget(self._clear_model_btn)
        save_form.addRow(load_row)

        # Option render pendant training
        self._render_check = QCheckBox("Render environment during training")
        self._render_check.setChecked(True)
        save_form.addRow(self._render_check)

        scroll_layout.addWidget(save_group)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        container_layout.addWidget(scroll, 1)
        layout.addWidget(self._container)

    def _populate_environments(self):
        self._env_combo.clear()
        try:
            env_categories = get_environment_list()
            for cat, envs in env_categories.items():
                self._env_combo.addItem(f"  {cat.upper()}")
                idx = self._env_combo.count() - 1
                self._env_combo.model().item(idx).setEnabled(False)
                for env_id in envs:
                    self._env_combo.addItem(env_id)
                    self._env_combo.model().item(self._env_combo.count()-1).setData(env_id, Qt.ItemDataRole.UserRole)
        except:
            for env_id in ["CartPole-v1", "LunarLander-v3", "Pendulum-v1"]:
                self._env_combo.addItem(env_id)
                self._env_combo.model().item(self._env_combo.count()-1).setData(env_id, Qt.ItemDataRole.UserRole)

    def _populate_algorithms(self, env_id: str):
        self._algo_combo.clear()
        compatible = get_compatible_algorithms(env_id)
        if not compatible:
            self._algo_combo.addItem("No compatible algorithms")
            return
        for cat, algos in {k: v for k, v in ALGORITHM_REGISTRY.items() if k in compatible}.items():
            self._algo_combo.addItem(f"  {ALGORITHM_REGISTRY[cat]['category'].upper()}")
            self._algo_combo.model().item(self._algo_combo.count()-1).setEnabled(False)
            for algo in [a for a in algos if a in compatible]:
                self._algo_combo.addItem(algo)
                self._algo_combo.model().item(self._algo_combo.count()-1).setData(algo, Qt.ItemDataRole.UserRole)

    def _populate_hyperparams(self, algo_name: str):
        while self._hp_layout.rowCount() > 0:
            self._hp_layout.removeRow(0)
        self._hyperparam_widgets.clear()
        if algo_name not in ALGORITHM_REGISTRY: return
        for key, cfg in ALGORITHM_REGISTRY[algo_name].get("hyperparams", {}).items():
            hp_type = cfg.get("type", "float")
            if hp_type == "float":
                w = QDoubleSpinBox()
                w.setRange(cfg.get("min", 0.0), cfg.get("max", 1.0))
                w.setValue(cfg.get("default", 0.0))
            elif hp_type == "int":
                w = QSpinBox()
                w.setRange(cfg.get("min", 0), cfg.get("max", 10000000))
                w.setValue(cfg.get("default", 0))
            else:
                w = QLineEdit(str(cfg.get("default", "")))
            self._hyperparam_widgets[key] = w
            self._hp_layout.addRow(key.replace("_", " ").title() + ":", w)

    def get_selected_env_id(self) -> str:
        return self._env_combo.currentData(Qt.ItemDataRole.UserRole) or ""

    def get_selected_algorithm(self) -> str:
        return self._algo_combo.currentData(Qt.ItemDataRole.UserRole) or ""

    def get_render_during_training(self) -> bool:
        return self._render_check.isChecked()

    def get_hyperparams(self) -> dict:
        return {k: w.value() if hasattr(w, "value") else w.text() for k, w in self._hyperparam_widgets.items()}

    def get_training_config(self) -> dict:
        seed = self._seed_spin.value()
        return {
            "env_id": self.get_selected_env_id(),
            "algo_name": self.get_selected_algorithm(),
            "total_timesteps": self._timesteps_spin.value(),
            "n_eval_episodes": self._eval_episodes_spin.value(),
            "seed": seed if seed > 0 else None,
            "hyperparams": self.get_hyperparams(),
            "save_dir": self._save_dir_edit.text().strip() or "saved_models",
            "render_training": self.get_render_during_training(),
        }

    def set_state(self, state: str):
        self._current_state = state
        colors = {"idle": TEXT_SECONDARY, "training": WARNING, "evaluating": ACCENT_SECONDARY,
                  "done": SUCCESS, "eval_done": SUCCESS, "error": DANGER}
        labels = {"idle": "Idle", "training": "Training...", "evaluating": "Evaluating...",
                  "done": "Done", "eval_done": "Evaluation complete", "error": "Error"}
        self._status_dot.setStyleSheet(f"background: {colors.get(state, TEXT_SECONDARY)}; border-radius: 3px;")
        self._status_label.setText(labels.get(state, state.capitalize()))
        self._status_label.setStyleSheet(f"color: {colors.get(state, TEXT_SECONDARY)}; font-weight: 600;")

        self._train_btn.setEnabled(state in ("idle", "done", "eval_done", "error"))
        self._stop_btn.setEnabled(state in ("training", "evaluating"))
        self._eval_btn.setEnabled(state in ("done", "eval_done"))
        self._reset_btn.setEnabled(state not in ("training", "evaluating"))
        self._env_combo.setEnabled(state not in ("training", "evaluating"))
        self._algo_combo.setEnabled(state not in ("training", "evaluating"))
        self._clear_model_btn.setEnabled(state in ("done", "eval_done") and self._current_state != "training")
        if state == "training":
            self._progress_bar.setValue(0)

    def update_progress(self, val: int):
        self._progress_bar.setValue(val)

    def _connect_signals(self):
        self._env_combo.currentTextChanged.connect(lambda: self._on_env_changed())
        self._algo_combo.currentTextChanged.connect(lambda: self._on_algo_changed())
        self._train_btn.clicked.connect(self._on_train_clicked)
        self._stop_btn.clicked.connect(self.stop_training_requested.emit)
        self._eval_btn.clicked.connect(lambda: self.start_evaluation_requested.emit(self._eval_episodes_spin.value()))
        self._reset_btn.clicked.connect(self.reset_requested.emit)
        self._load_btn.clicked.connect(lambda: None)  # connecté depuis main_window
        self._clear_model_btn.clicked.connect(self.clear_model_requested.emit)

    def _on_env_changed(self):
        env_id = self.get_selected_env_id()
        if env_id:
            try:
                self._env_info_label.setText(get_action_space_name(env_id))
            except:
                self._env_info_label.setText("?")
            self._populate_algorithms(env_id)

    def _on_algo_changed(self):
        algo = self.get_selected_algorithm()
        if algo and algo in ALGORITHM_REGISTRY:
            meta = ALGORITHM_REGISTRY[algo]
            self._algo_info_label.setText(meta.get("description", ""))
            self._algo_category_label.setText(meta.get("category", ""))
            self._populate_hyperparams(algo)
        else:
            self._algo_info_label.setText("—")
            self._algo_category_label.setText("")

    def _on_train_clicked(self):
        cfg = self.get_training_config()
        if not cfg["env_id"] or not cfg["algo_name"]:
            QMessageBox.warning(self, "Invalid", "Please select environment and algorithm.")
            return
        self.start_training_requested.emit(cfg)