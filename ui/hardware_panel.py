"""
Hardware Panel — STUB placeholder for future CPU/GPU/RAM monitoring.
Shows styled placeholder cards with no real data collection.
"""

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel,
)

from ui.theme import (
    BG_SECONDARY, BG_TERTIARY, BG_ELEVATED, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED,
    ACCENT, ACCENT_SECONDARY, SUCCESS, WARNING, DANGER,
    CHART_BG, CHART_GRID, FONT_FAMILY,
)


class HardwareCard(QWidget):
    """Individual hardware metric card with icon, label, and mini chart."""

    def __init__(self, icon: str, title: str, subtitle: str,
                 color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._setup_ui(icon, title, subtitle)

    def _setup_ui(self, icon: str, title: str, subtitle: str):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_TERTIARY};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"""
            font-size: 20px;
            background: transparent;
            border: none;
        """)
        header.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        header.addWidget(title_lbl)
        header.addStretch()

        # "Coming Soon" badge
        badge = QLabel("Soon")
        badge.setStyleSheet(f"""
            color: {TEXT_DISABLED};
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 9px;
            font-weight: 600;
        """)
        header.addWidget(badge)
        layout.addLayout(header)

        # Value
        self._value_label = QLabel(subtitle)
        self._value_label.setStyleSheet(f"""
            color: {self._color};
            font-size: 18px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._value_label)

        # Mini chart placeholder
        self._mini_chart = pg.PlotWidget()
        self._mini_chart.setBackground(QColor(CHART_BG))
        self._mini_chart.setFixedHeight(50)
        self._mini_chart.hideAxis("bottom")
        self._mini_chart.hideAxis("left")
        self._mini_chart.setMouseEnabled(x=False, y=False)
        self._mini_chart.setMenuEnabled(False)
        
        # Draw a flat line as placeholder
        import numpy as np
        x = np.linspace(0, 10, 50)
        y = np.zeros(50)
        self._mini_chart.plot(
            x, y,
            pen=pg.mkPen(color=self._color + "60", width=1.5),
        )
        layout.addWidget(self._mini_chart)


class HardwarePanel(QWidget):
    """
    Placeholder hardware monitoring panel.
    
    Shows 4 cards (CPU, RAM, GPU, Threads) with "Coming Soon" badges.
    No real data collection — ready for future psutil/GPUtil integration.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(6)

        # Title
        title = QLabel("🖥️  Hardware Profiling")
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 700;
                padding: 4px 8px;
                background: transparent;
                border: none;
            }}
        """)
        container_layout.addWidget(title)

        # Grid of cards
        grid = QGridLayout()
        grid.setSpacing(8)

        cards = [
            ("🔲", "CPU Usage", "— %", ACCENT, 0, 0),
            ("💾", "RAM Usage", "— / — GB", ACCENT_SECONDARY, 0, 1),
            ("🎮", "GPU Usage", "— %", SUCCESS, 1, 0),
            ("🧵", "Threads", "—", WARNING, 1, 1),
        ]
        for icon, title_text, subtitle, color, row, col in cards:
            card = HardwareCard(icon, title_text, subtitle, color)
            grid.addWidget(card, row, col)

        container_layout.addLayout(grid)
        layout.addWidget(container)
