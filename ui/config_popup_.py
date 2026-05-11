from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QFileDialog, QFormLayout, QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from core.algorithms import (
    get_environment_list,
    get_compatible_algorithms,
    get_algorithm_metadata,
)

class ConfigModal(QDialog):
    train_requested = pyqtSignal(dict)
    stop_requested = pyqtSignal()
    eval_requested = pyqtSignal()
    load_model_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Training Configuration")
        self.setModal(True)
        self.setFixedSize(600, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #27272A;
                border: 1px solid #3F3F46;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("⚙ Training Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #6366F1;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                border: none;
                font-weight: bold;
                font-size: 18px;
                color: #A1A1AA;
                background: transparent;
            }
            QPushButton:hover {
                color: #EF4444;
            }
        """)
        self.btn_close.clicked.connect(self.reject)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_close)
        layout.addLayout(header)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: #3F3F46;")
        layout.addWidget(sep1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background-color: #27272A;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #52525B;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #71717A;
            }
        """)

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        env_section = self._create_section("Environment Selection", [
            ("Environment", self._create_environment_combo())
        ])
        content_layout.addWidget(env_section)

        algo_section = self._create_section("Algorithm Selection", [
            ("Algorithm", self._create_algorithm_combo())
        ])
        content_layout.addWidget(algo_section)

        self.lbl_algo_details = QLabel("")
        self.lbl_algo_details.setWordWrap(True)
        self.lbl_algo_details.setStyleSheet("font-size: 11px; color: #A1A1AA; margin: 8px 12px;")
        content_layout.addWidget(self.lbl_algo_details)

        self.hyperparams_container = QWidget()
        self.hyperparams_container.setStyleSheet("background-color: transparent;")
        self.hyperparams_form = QFormLayout(self.hyperparams_container)
        self.hyperparams_form.setContentsMargins(12, 12, 12, 12)
        self.hyperparams_form.setHorizontalSpacing(12)
        self.hyperparams_form.setVerticalSpacing(8)

        hyperparams_frame = self._wrap_in_frame(self.hyperparams_container, "Hyperparameters")
        content_layout.addWidget(hyperparams_frame)

        self.hyperparam_inputs = {}

        ts_seed_layout = QHBoxLayout()
        ts_seed_layout.setSpacing(12)

        self.input_timesteps = QLineEdit("100000")
        self.input_timesteps.setPlaceholderText("Total Timesteps")
        self.input_timesteps.setStyleSheet(self._get_input_style())
        self.input_timesteps.setMinimumHeight(40)

        self.input_seed = QLineEdit("")
        self.input_seed.setPlaceholderText("Seed (optional)")
        self.input_seed.setStyleSheet(self._get_input_style())
        self.input_seed.setMinimumHeight(40)

        ts_seed_layout.addWidget(self.input_timesteps, stretch=2)
        ts_seed_layout.addWidget(self.input_seed, stretch=1)

        ts_frame = QFrame()
        ts_frame.setFrameShape(QFrame.Shape.StyledPanel)
        ts_frame.setStyleSheet("QFrame { background-color: #18181B; border: 1px solid #3F3F46; border-radius: 4px; padding: 12px; }")
        ts_inner = QVBoxLayout(ts_frame)
        ts_inner.setContentsMargins(0, 0, 0, 0)
        ts_inner.addLayout(ts_seed_layout)
        
        ts_label = QLabel("Training Parameters")
        ts_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #D4D4D8; margin-bottom: 8px;")
        ts_container = QWidget()
        ts_layout = QVBoxLayout(ts_container)
        ts_layout.setContentsMargins(12, 12, 12, 12)
        ts_layout.addWidget(ts_label)
        ts_layout.addWidget(ts_frame)
        content_layout.addWidget(ts_container)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #3F3F46;")
        layout.addWidget(sep2)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        self.btn_train = QPushButton("▶ Train")
        self.btn_train.setProperty("class", "btn-primary")
        self.btn_train.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_train.setMinimumHeight(44)
        self.btn_train.setStyleSheet(self._get_primary_button_style())
        self.btn_train.clicked.connect(self._on_train_clicked)
        buttons.addWidget(self.btn_train)

        self.btn_stop = QPushButton("■ Stop")
        self.btn_stop.setProperty("class", "btn-danger")
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setMinimumHeight(44)
        self.btn_stop.setStyleSheet(self._get_danger_button_style())
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        buttons.addWidget(self.btn_stop)

        layout.addLayout(buttons)

        buttons2 = QHBoxLayout()
        buttons2.setSpacing(12)

        self.btn_eval = QPushButton("👁 Eval")
        self.btn_eval.setProperty("class", "btn-info")
        self.btn_eval.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eval.setMinimumHeight(44)
        self.btn_eval.setStyleSheet(self._get_info_button_style())
        self.btn_eval.clicked.connect(self.eval_requested.emit)
        buttons2.addWidget(self.btn_eval)

        self.btn_load = QPushButton("📁 Load Model")
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setMinimumHeight(44)
        self.btn_load.setStyleSheet(self._get_secondary_button_style())
        self.btn_load.clicked.connect(self._on_load_clicked)
        buttons2.addWidget(self.btn_load)

        layout.addLayout(buttons2)

        self._populate_environments()
        self._update_algorithms()

    def _create_section(self, title: str, fields: list) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #18181B; border: 1px solid #3F3F46; border-radius: 4px; padding: 12px; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #D4D4D8; text-transform: uppercase; letter-spacing: 0.5px;")
        layout.addWidget(lbl)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)

        for label_text, widget in fields:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 11px; color: #A1A1AA;")
            form.addRow(lbl, widget)

        layout.addLayout(form)
        return frame

    def _wrap_in_frame(self, widget: QWidget, title: str) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #18181B; border: 1px solid #3F3F46; border-radius: 4px; padding: 12px; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #D4D4D8; text-transform: uppercase; letter-spacing: 0.5px;")
        layout.addWidget(lbl)

        layout.addWidget(widget)
        return frame

    def _create_environment_combo(self) -> QComboBox:
        self.combo_env = QComboBox()
        self.combo_env.setStyleSheet(self._get_combo_style())
        self.combo_env.setMinimumHeight(36)
        self.combo_env.currentTextChanged.connect(self._update_algorithms)
        return self.combo_env

    def _create_algorithm_combo(self) -> QComboBox:
        self.combo_algo = QComboBox()
        self.combo_algo.setStyleSheet(self._get_combo_style())
        self.combo_algo.setMinimumHeight(36)
        self.combo_algo.currentTextChanged.connect(self._on_algorithm_changed)
        return self.combo_algo

    def _populate_environments(self):
        envs = get_environment_list()
        for category, env_list in envs.items():
            for env_id in env_list:
                self.combo_env.addItem(f"{env_id} ({category})", env_id)

    def _update_algorithms(self):
        env_id = self.combo_env.currentData()
        if not env_id:
            return
        self.combo_algo.clear()
        compatible_algos = get_compatible_algorithms(env_id)
        for algo in compatible_algos:
            self.combo_algo.addItem(algo)
        self._on_algorithm_changed()

    def _on_algorithm_changed(self):
        algo_name = self.combo_algo.currentText()
        meta = get_algorithm_metadata(algo_name)

        description = meta.get("description", "No description")
        category = meta.get("category", "Unknown")
        policy = meta.get("policy", "Unknown")
        self.lbl_algo_details.setText(f"<b>{category}</b> • {policy}<br/>{description}")

        self._clear_hyperparams_form()
        for key, cfg in meta.get("hyperparams", {}).items():
            field = self._create_hyperparam_field(cfg)
            self.hyperparam_inputs[key] = field
            label = QLabel(key)
            label.setStyleSheet("font-size: 11px; color: #D4D4D8;")
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
            combo.setStyleSheet(self._get_combo_style())
            combo.setMinimumHeight(32)
            for opt in options:
                combo.addItem(str(opt))
            idx = combo.findText(str(default_value))
            if idx >= 0:
                combo.setCurrentIndex(idx)
            return combo

        field = QLineEdit(str(default_value))
        field.setStyleSheet(self._get_input_style())
        field.setMinimumHeight(32)
        if value_type == "int":
            field.setPlaceholderText("Integer value")
        elif value_type == "float":
            field.setPlaceholderText("Float value")
        else:
            field.setPlaceholderText("Value")
        return field

    def _collect_hyperparams(self) -> dict:
        algo_name = self.combo_algo.currentText()
        meta = get_algorithm_metadata(algo_name)
        config = meta.get("hyperparams", {})
        values = {}

        for key, cfg in config.items():
            widget = self.hyperparam_inputs.get(key)
            if widget is None:
                continue

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
            try:
                return int(text)
            except ValueError:
                return default_value
        if value_type == "float":
            try:
                return float(text)
            except ValueError:
                return default_value
        return text

    def _on_train_clicked(self):
        try:
            timesteps = int(self.input_timesteps.text())
        except ValueError:
            timesteps = 100000

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
        self.accept()  # Close the modal after training starts

    def _on_load_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Model",
            "saved_models",
            "Model Files (*.zip)"
        )
        if file_path:
            self.load_model_requested.emit(file_path)

    def _get_input_style(self) -> str:
        return """
            QLineEdit {
                background-color: #18181B;
                color: #F4F4F5;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #6366F1;
            }
        """

    def _get_combo_style(self) -> str:
        return """
            QComboBox {
                background-color: #18181B;
                color: #F4F4F5;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
            }
            QComboBox:focus {
                border: 1px solid #6366F1;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #27272A;
                color: #F4F4F5;
                selection-background-color: #6366F1;
            }
        """

    def _get_primary_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4F46E5;
            }
            QPushButton:pressed {
                background-color: #4338CA;
            }
        """

    def _get_danger_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """

    def _get_info_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #0EA5E9;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0284C7;
            }
        """

    def _get_secondary_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #3F3F46;
                color: #F4F4F5;
                border: 1px solid #52525B;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #52525B;
            }
        """
