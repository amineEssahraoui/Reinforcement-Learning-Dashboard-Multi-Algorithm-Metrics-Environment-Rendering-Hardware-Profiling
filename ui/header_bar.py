from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt

class HeaderBar(QWidget):
    hardware_toggled = pyqtSignal(bool)
    config_toggled = pyqtSignal(bool)
    theme_toggled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        self.title_label = QLabel("⬡ RL Dashboard")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(self.title_label)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        layout.addWidget(spacer)

        self.btn_hardware = QPushButton("🖥 Hardware Usage")
        self.btn_hardware.setCheckable(True)
        self.btn_hardware.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hardware.clicked.connect(self._on_hardware_clicked)
        layout.addWidget(self.btn_hardware)

        self.btn_config = QPushButton("⚙ Config")
        self.btn_config.setCheckable(True)
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_config.clicked.connect(self._on_config_clicked)
        layout.addWidget(self.btn_config)

        self.btn_theme = QPushButton("☀")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setFixedSize(34, 34) # Taille parfaite
        self.btn_theme.clicked.connect(self.theme_toggled.emit)
        layout.addWidget(self.btn_theme)

    def _on_hardware_clicked(self, checked: bool):
        if checked:
            self.btn_config.setChecked(False)
            self.config_toggled.emit(False)
        self.hardware_toggled.emit(checked)

    def _on_config_clicked(self, checked: bool):
        if checked:
            self.btn_hardware.setChecked(False)
            self.hardware_toggled.emit(False)
        self.config_toggled.emit(checked)
        
    def reset_toggles(self):
        self.btn_hardware.setChecked(False)
        self.btn_config.setChecked(False)