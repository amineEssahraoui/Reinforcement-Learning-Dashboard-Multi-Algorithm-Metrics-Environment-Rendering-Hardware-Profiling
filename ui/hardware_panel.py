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
    """Individual hardware metric card with colored indicator, label, and mini chart."""

    def __init__(self, title: str, subtitle: str, color: str, abbrev: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._setup_ui(title, subtitle, abbrev)

    def _setup_ui(self, title: str, subtitle: str, abbrev: str):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_TERTIARY};
                border: 1px solid {BORDER};
                border-top: 2px solid {self._color};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        # Colored abbreviation tag
        tag = QLabel(abbrev)
        tag.setFixedWidth(36)
        tag.setFixedHeight(20)
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(f"""
            color: {self._color};
            background-color: {self._color}1a;
            border: 1px solid {self._color}33;
            border-radius: 4px;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 0.5px;
        """)
        header.addWidget(tag)

        self._title_lbl = QLabel(title)
        self._title_lbl.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        header.addWidget(self._title_lbl)
        header.addStretch()

        # "Soon" badge
        self._badge = QLabel("Soon")
        self._badge.setStyleSheet(f"""
            color: {TEXT_DISABLED};
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER};
            border-radius: 5px;
            padding: 2px 8px;
            font-size: 9px;
            font-weight: 600;
        """)
        header.addWidget(self._badge)
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
        self._mini_chart.setFixedHeight(46)
        self._mini_chart.hideAxis("bottom")
        self._mini_chart.hideAxis("left")
        self._mini_chart.setMouseEnabled(x=False, y=False)
        self._mini_chart.setMenuEnabled(False)
        self._mini_chart.setStyleSheet("border: none; border-radius: 6px;")

        import numpy as np
        x = np.linspace(0, 10, 50)
        y = np.zeros(50)
        self._mini_chart.plot(
            x, y,
            pen=pg.mkPen(color=self._color + "50", width=1.5),
        )
        # Fill area under flat line
        fill_item = pg.FillBetweenItem(
            self._mini_chart.getPlotItem().listDataItems()[0],
            pg.PlotDataItem(x, y - 0.01),
            brush=pg.mkBrush(QColor(self._color + "18")),
        )
        self._mini_chart.addItem(fill_item)
        layout.addWidget(self._mini_chart)

    def refresh_theme(self):
        """Re-apply inline styles for the current theme."""
        import ui.theme as t
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {t.BG_TERTIARY};
                border: 1px solid {t.BORDER};
                border-top: 2px solid {self._color};
                border-radius: 10px;
            }}
        """)
        self._title_lbl.setStyleSheet(f"""
            color: {t.TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        self._badge.setStyleSheet(f"""
            color: {t.TEXT_DISABLED};
            background-color: {t.BG_ELEVATED};
            border: 1px solid {t.BORDER};
            border-radius: 5px;
            padding: 2px 8px;
            font-size: 9px;
            font-weight: 600;
        """)
        self._mini_chart.setBackground(pg.mkColor(t.CHART_BG))


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
        self._container = QWidget()
        self._container.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(6)

        # Title row
        title_row = QWidget()
        title_row.setStyleSheet("background: transparent; border: none;")
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(10)

        accent_bar = QWidget()
        accent_bar.setFixedSize(3, 18)
        accent_bar.setStyleSheet(f"background-color: {ACCENT}; border-radius: 2px; border: none;")
        title_row_layout.addWidget(accent_bar)

        title = QLabel("Hardware Profiling")
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

        # Grid of cards
        self._cards = []
        grid = QGridLayout()
        grid.setSpacing(8)

        cards = [
            ("CPU Usage", "— %", ACCENT, "CPU", 0, 0),
            ("RAM Usage", "— / — GB", ACCENT_SECONDARY, "MEM", 0, 1),
            ("GPU Usage", "— %", SUCCESS, "GPU", 1, 0),
            ("Threads", "—", WARNING, "THR", 1, 1),
        ]
        for title_text, subtitle, color, abbrev, row, col in cards:
            card = HardwareCard(title_text, subtitle, color, abbrev)
            self._cards.append(card)
            grid.addWidget(card, row, col)

        container_layout.addLayout(grid)
        layout.addWidget(self._container)

    def refresh_theme(self):
        """Re-apply inline styles for the current theme."""
        import ui.theme as t
        self._container.setStyleSheet(f"""
            QWidget {{
                background-color: {t.BG_SECONDARY};
                border: 1px solid {t.BORDER};
                border-radius: 12px;
            }}
        """)
        for card in self._cards:
            card.refresh_theme()
