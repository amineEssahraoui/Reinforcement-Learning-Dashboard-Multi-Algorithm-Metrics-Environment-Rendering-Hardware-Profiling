"""
Popup de configuration.
Permet de sélectionner l'environnement, l'algorithme, les paramètres, 
et de contrôler l'entraînement (Train, Stop, Eval, Load).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QFileDialog,
    QFormLayout, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
from core.algorithms import (
    get_environment_list,
    get_compatible_algorithms,
    ALGORITHM_REGISTRY
)

class ConfigPopup(QWidget):
    train_requested = pyqtSignal(dict)
    stop_requested = pyqtSignal()
    eval_requested = pyqtSignal()
    load_model_requested = pyqtSignal(str)
    closed_signal = pyqtSignal() # Signal pour prévenir que la fenêtre est fermée

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OverlayPopup")
        self.setFixedSize(340, 560) 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- Header avec bouton [X] ---
        header = QHBoxLayout()
        title = QLabel("⚙ Configuration")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #6366F1;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("QPushButton { border: none; font-weight: bold; color: #A1A1AA; background: transparent; } QPushButton:hover { color: #EF4444; }")
        self.btn_close.clicked.connect(self._on_close)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_close)
        layout.addLayout(header)

        # --- Environnement ---
        layout.addWidget(self._create_label("Environment"))
        self.combo_env = QComboBox()
        self._populate_environments()
        self.combo_env.currentTextChanged.connect(self._update_algorithms)
        layout.addWidget(self.combo_env)

        # --- Algorithme ---
        layout.addWidget(self._create_label("Algorithm"))
        self.combo_algo = QComboBox()
        self.combo_algo.currentTextChanged.connect(self._on_algorithm_changed)
        layout.addWidget(self.combo_algo)

        self.lbl_algo_details = QLabel("")
        self.lbl_algo_details.setWordWrap(True)
        self.lbl_algo_details.setStyleSheet("font-size: 10px; color: #A1A1AA; font-style: italic;")
        layout.addWidget(self.lbl_algo_details)

        # --- Hyperparamètres dynamiques ---
        layout.addWidget(self._create_label("Hyperparameters"))
        
        self.hyperparams_container = QWidget()
        self.hyperparams_form = QFormLayout(self.hyperparams_container)
        self.hyperparams_form.setContentsMargins(4, 4, 12, 4)
        self.hyperparams_form.setHorizontalSpacing(12)
        self.hyperparams_form.setVerticalSpacing(8)

        self.hyperparams_scroll = QScrollArea()
        self.hyperparams_scroll.setWidgetResizable(True)
        self.hyperparams_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.hyperparams_scroll.setFixedHeight(180)
        self.hyperparams_scroll.setStyleSheet("background: transparent;")
        self.hyperparams_scroll.setWidget(self.hyperparams_container)
        layout.addWidget(self.hyperparams_scroll)

        self.hyperparam_inputs: dict[str, QWidget] = {}

        # --- Timesteps & Seed ---
        layout.addWidget(self._create_label("Timesteps · Seed"))
        row_ts_seed = QHBoxLayout()
        row_ts_seed.setSpacing(8)
        
        self.input_timesteps = QLineEdit("100000")
        self.input_timesteps.setPlaceholderText("Timesteps")
        row_ts_seed.addWidget(self.input_timesteps, stretch=2)
        
        self.input_seed = QLineEdit("")
        self.input_seed.setPlaceholderText("Seed (opt)")
        row_ts_seed.addWidget(self.input_seed, stretch=1)
        
        layout.addLayout(row_ts_seed)
        layout.addSpacing(4)

        # --- Boutons d'action ---
        row_actions = QHBoxLayout()
        row_actions.setSpacing(8)
        
        self.btn_train = QPushButton("▶ Train")
        self.btn_train.setProperty("class", "btn-primary")
        self.btn_train.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_train.clicked.connect(self._on_train_clicked)
        row_actions.addWidget(self.btn_train)

        self.btn_stop = QPushButton("■ Stop")
        self.btn_stop.setProperty("class", "btn-danger")
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        row_actions.addWidget(self.btn_stop)
        
        layout.addLayout(row_actions)

        row_actions_2 = QHBoxLayout()
        row_actions_2.setSpacing(8)
        
        self.btn_eval = QPushButton("👁 Eval")
        self.btn_eval.setProperty("class", "btn-info")
        self.btn_eval.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eval.clicked.connect(self.eval_requested.emit)
        row_actions_2.addWidget(self.btn_eval)

        self.btn_load = QPushButton("Load")
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.clicked.connect(self._on_load_clicked)
        row_actions_2.addWidget(self.btn_load)
        
        layout.addLayout(row_actions_2)

        self._update_algorithms()

    def _create_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 11px; color: #A1A1AA; text-transform: uppercase; font-weight: bold;")
        return lbl

    def _populate_environments(self):
        envs = get_environment_list()
        for category, env_list in envs.items():
            for env_id in env_list:
                self.combo_env.addItem(f"{env_id} ({category})", env_id)

    def _update_algorithms(self):
        env_id = self.combo_env.currentData()
        if not env_id: return
            
        self.combo_algo.clear()
        compatible_algos = get_compatible_algorithms(env_id)
        for algo in compatible_algos:
            self.combo_algo.addItem(algo)

        self._on_algorithm_changed()

    def _on_algorithm_changed(self):
        algo_name = self.combo_algo.currentText()
        if not algo_name or algo_name not in ALGORITHM_REGISTRY: return
            
        meta = ALGORITHM_REGISTRY[algo_name]
        self.lbl_algo_details.setText(f"{meta.get('category', 'Unknown')} • {meta.get('policy', 'Unknown')}\n{meta.get('description', 'No description')}")

        self._clear_hyperparams_form()
        
        for key, cfg in meta.get("hyperparams", {}).items():
            field = self._create_hyperparam_field(cfg)
            self.hyperparam_inputs[key] = field
            label = QLabel(key)
            label.setStyleSheet("font-size: 11px;") 
            self.hyperparams_form.addRow(label, field)

    def _clear_hyperparams_form(self):
        while self.hyperparams_form.rowCount() > 0:
            self.hyperparams_form.removeRow(0)
        self.hyperparam_inputs.clear()

    def _create_hyperparam_field(self, cfg: dict) -> QWidget:
        value_type = cfg.get("type", "str")
        options = cfg.get("options")
        default_value = cfg.get("default", "")

        if options:
            combo = QComboBox()
            for opt in options: combo.addItem(str(opt))
            idx = combo.findText(str(default_value))
            if idx >= 0: combo.setCurrentIndex(idx)
            return combo

        field = QLineEdit(str(default_value))
        field.setPlaceholderText("Integer" if value_type == "int" else "Float" if value_type == "float" else "Value")
        return field

    def _collect_hyperparams(self) -> dict:
        algo_name = self.combo_algo.currentText()
        if not algo_name or algo_name not in ALGORITHM_REGISTRY: return {}
            
        config = ALGORITHM_REGISTRY[algo_name].get("hyperparams", {})
        values = {}

        for key, cfg in config.items():
            widget = self.hyperparam_inputs.get(key)
            if widget is None: continue

            if isinstance(widget, QComboBox):
                values[key] = widget.currentText()
                continue

            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
                default_value = cfg.get("default")
                if text == "":
                    values[key] = default_value
                    continue
                values[key] = self._parse_hyperparam_value(text, cfg, default_value)

        return values

    def _parse_hyperparam_value(self, text: str, cfg: dict, default_value):
        value_type = cfg.get("type", "str")
        if value_type == "int":
            try: return int(text)
            except ValueError: return default_value
        if value_type == "float":
            try: return float(text)
            except ValueError: return default_value
        return text

    def _on_train_clicked(self):
        try: timesteps = int(self.input_timesteps.text())
        except ValueError: timesteps = 100000 
            
        seed_text = self.input_seed.text()
        seed = int(seed_text) if seed_text.isdigit() else None

        config = {
            "algo_name": self.combo_algo.currentText(),
            "env_id": self.combo_env.currentData(),
            "total_timesteps": timesteps,
            "seed": seed,
            "hyperparams": self._collect_hyperparams()
        }
        self.train_requested.emit(config)

    def _on_load_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Charger un modèle", "saved_models", "Modèles Zip (*.zip)")
        if file_path: self.load_model_requested.emit(file_path)

    def _on_close(self):
        self.hide()
        self.closed_signal.emit()