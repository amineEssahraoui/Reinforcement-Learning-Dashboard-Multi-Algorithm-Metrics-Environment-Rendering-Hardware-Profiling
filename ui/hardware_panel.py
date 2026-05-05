"""
Hardware Panel — avec toggle pour cacher/afficher les cartes.
"""

import pyqtgraph as pg
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame

from ui.theme import (
    BG_SECONDARY, BG_TERTIARY, BG_ELEVATED, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED,
    ACCENT, ACCENT_SECONDARY, SUCCESS, WARNING,
    CHART_BG, FONT_FAMILY,
)

class HardwareCard(QWidget):
    def __init__(self, title: str, subtitle: str, color: str, abbrev: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._setup_ui(title, subtitle, abbrev)

    def _setup_ui(self, title, subtitle, abbrev):
        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_TERTIARY};
                border: 1px solid {BORDER};
                border-top: 2px solid {self._color};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        header = QHBoxLayout()
        tag = QLabel(abbrev)
        tag.setFixedSize(36, 20)
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(f"color: {self._color}; background: {self._color}1a; border:1px solid {self._color}33; border-radius:4px; font-weight:800;")
        header.addWidget(tag)
        self._title_lbl = QLabel(title)
        self._title_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-weight:700;")
        header.addWidget(self._title_lbl)
        header.addStretch()
        self._badge = QLabel("Soon")
        self._badge.setStyleSheet(f"color:{TEXT_DISABLED}; background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:5px; padding:2px 8px; font-size:9px;")
        header.addWidget(self._badge)
        layout.addLayout(header)
        self._value_label = QLabel(subtitle)
        self._value_label.setStyleSheet(f"color:{self._color}; font-size:18px; font-weight:700;")
        layout.addWidget(self._value_label)
        self._mini_chart = pg.PlotWidget()
        self._mini_chart.setBackground(QColor(CHART_BG))
        self._mini_chart.setFixedHeight(46)
        self._mini_chart.hideAxis("bottom")
        self._mini_chart.hideAxis("left")
        self._mini_chart.setMouseEnabled(False, False)
        import numpy as np
        x = np.linspace(0,10,50)
        y = np.zeros(50)
        self._mini_chart.plot(x, y, pen=pg.mkPen(color=self._color+"80", width=1.5))
        layout.addWidget(self._mini_chart)

class HardwarePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self._container = QWidget()
        self._container.setObjectName("panelContainer")
        cont_layout = QVBoxLayout(self._container)
        cont_layout.setContentsMargins(8,8,8,8)

        # Header avec toggle
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0,0,0,0)
        accent = QFrame()
        accent.setFixedSize(3,18)
        accent.setStyleSheet(f"background:{ACCENT}; border-radius:2px;")
        header_layout.addWidget(accent)
        title = QLabel("Hardware Profiling")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-weight:700;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self._toggle_btn = QPushButton("▼")
        self._toggle_btn.setFixedSize(28,28)
        self._toggle_btn.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px; font-weight:bold;")
        self._toggle_btn.clicked.connect(self._toggle)
        header_layout.addWidget(self._toggle_btn)
        cont_layout.addWidget(header)

        # Contenu repliable
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0,8,0,0)
        grid = QGridLayout()
        grid.setSpacing(8)
        cards = [
            ("CPU Usage", "— %", ACCENT, "CPU", 0,0),
            ("RAM Usage", "— / — GB", ACCENT_SECONDARY, "MEM", 0,1),
            ("GPU Usage", "— %", SUCCESS, "GPU", 1,0),
            ("Threads", "—", WARNING, "THR", 1,1),
        ]
        self._cards = []
        for t, sub, col, abbr, r, c in cards:
            card = HardwareCard(t, sub, col, abbr)
            self._cards.append(card)
            grid.addWidget(card, r, c)
        self._content_layout.addLayout(grid)
        cont_layout.addWidget(self._content)
        layout.addWidget(self._container)

    def _toggle(self):
        self._collapsed = not self._collapsed
        self._content.setVisible(not self._collapsed)
        self._toggle_btn.setText("▶" if self._collapsed else "▼")