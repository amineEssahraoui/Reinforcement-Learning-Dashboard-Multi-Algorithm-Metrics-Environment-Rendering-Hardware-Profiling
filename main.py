"""
RL Dashboard — Entry Point
Reinforcement Learning Prototyping Tool

Launch the PyQt6 desktop application.
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme import get_stylesheet
from ui.main_window import MainWindow


def main():
    # High-DPI support
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("RL Dashboard")
    app.setOrganizationName("RLDashboard")
    app.setApplicationVersion("1.0.0")

    # Apply global dark theme
    app.setStyleSheet(get_stylesheet())

    # Set default font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
