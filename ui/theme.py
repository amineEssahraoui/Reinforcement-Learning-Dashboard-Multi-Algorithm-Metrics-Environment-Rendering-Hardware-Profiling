"""
Dark theme configuration for the RL Dashboard.
Defines color tokens, fonts, and global QSS stylesheets.
"""

# ─── Color Tokens ────────────────────────────────────────────────────────────

BG_PRIMARY = "#0f1117"
BG_SECONDARY = "#1a1d27"
BG_TERTIARY = "#252830"
BG_ELEVATED = "#2a2d38"

ACCENT = "#6c5ce7"
ACCENT_HOVER = "#7f70f0"
ACCENT_PRESSED = "#5a4bd6"
ACCENT_SECONDARY = "#00cec9"
ACCENT_SECONDARY_HOVER = "#00e0db"

SUCCESS = "#00b894"
WARNING = "#fdcb6e"
DANGER = "#e17055"

TEXT_PRIMARY = "#e8e8e8"
TEXT_SECONDARY = "#8b8d97"
TEXT_DISABLED = "#555860"

BORDER = "#2d303a"
BORDER_FOCUS = "#6c5ce7"

# Chart colors
CHART_REWARD = "#6c5ce7"
CHART_LOSS_POLICY = "#e17055"
CHART_LOSS_VALUE = "#fdcb6e"
CHART_LOSS_ENTROPY = "#00cec9"
CHART_EP_LENGTH = "#00b894"
CHART_EVAL_BAR = "#6c5ce7"
CHART_GRID = "#2d303a"
CHART_BG = "#13151d"

# ─── Font ─────────────────────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI, Inter, Roboto, sans-serif"
FONT_SIZE_SM = "11px"
FONT_SIZE_MD = "13px"
FONT_SIZE_LG = "16px"
FONT_SIZE_XL = "22px"
FONT_SIZE_TITLE = "28px"

# ─── Global Stylesheet ───────────────────────────────────────────────────────

def get_stylesheet() -> str:
    """Return the global QSS stylesheet for the entire application."""
    return f"""
    /* ── Global ────────────────────────────────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_MD};
    }}

    /* ── Scroll Areas ──────────────────────────────────────────────── */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background: {BG_SECONDARY};
        width: 8px;
        border-radius: 4px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BG_TERTIARY};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_SECONDARY};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {BG_SECONDARY};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {BG_TERTIARY};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {TEXT_SECONDARY};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ── Splitter ──────────────────────────────────────────────────── */
    QSplitter::handle {{
        background-color: {BORDER};
        width: 2px;
    }}
    QSplitter::handle:hover {{
        background-color: {ACCENT};
    }}

    /* ── Tab Widget ────────────────────────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 8px;
        background-color: {BG_SECONDARY};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: {BG_TERTIARY};
        color: {TEXT_SECONDARY};
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 600;
        font-size: {FONT_SIZE_MD};
    }}
    QTabBar::tab:selected {{
        background-color: {BG_SECONDARY};
        color: {ACCENT};
        border-bottom: 2px solid {ACCENT};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
    }}

    /* ── Group Box ─────────────────────────────────────────────────── */
    QGroupBox {{
        background-color: {BG_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 10px;
        margin-top: 14px;
        padding: 16px 12px 12px 12px;
        font-weight: 600;
        font-size: {FONT_SIZE_MD};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 12px;
        color: {TEXT_PRIMARY};
    }}

    /* ── Labels ────────────────────────────────────────────────────── */
    QLabel {{
        color: {TEXT_PRIMARY};
        background: transparent;
    }}

    /* ── Combo Box ─────────────────────────────────────────────────── */
    QComboBox {{
        background-color: {BG_TERTIARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 12px;
        font-size: {FONT_SIZE_MD};
        min-height: 24px;
    }}
    QComboBox:hover {{
        border-color: {ACCENT};
    }}
    QComboBox:focus {{
        border-color: {ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {TEXT_SECONDARY};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG_TERTIARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        selection-background-color: {ACCENT};
        selection-color: white;
        padding: 4px;
    }}

    /* ── Spin Box ──────────────────────────────────────────────────── */
    QSpinBox, QDoubleSpinBox {{
        background-color: {BG_TERTIARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {FONT_SIZE_MD};
        min-height: 24px;
    }}
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {ACCENT};
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {ACCENT};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid {BORDER};
        border-top-right-radius: 6px;
        background-color: {BG_TERTIARY};
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        border-left: 1px solid {BORDER};
        border-bottom-right-radius: 6px;
        background-color: {BG_TERTIARY};
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {TEXT_SECONDARY};
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY};
    }}

    /* ── Push Button ───────────────────────────────────────────────── */
    QPushButton {{
        background-color: {BG_TERTIARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: {FONT_SIZE_MD};
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: {BG_ELEVATED};
        border-color: {ACCENT};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_PRESSED};
        border-color: {ACCENT};
    }}
    QPushButton:disabled {{
        background-color: {BG_SECONDARY};
        color: {TEXT_DISABLED};
        border-color: {BORDER};
    }}

    /* ── Primary Button ────────────────────────────────────────────── */
    QPushButton[cssClass="primary"] {{
        background-color: {ACCENT};
        color: white;
        border: none;
    }}
    QPushButton[cssClass="primary"]:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton[cssClass="primary"]:pressed {{
        background-color: {ACCENT_PRESSED};
    }}

    /* ── Danger Button ─────────────────────────────────────────────── */
    QPushButton[cssClass="danger"] {{
        background-color: {DANGER};
        color: white;
        border: none;
    }}
    QPushButton[cssClass="danger"]:hover {{
        background-color: #e8836e;
    }}

    /* ── Success Button ────────────────────────────────────────────── */
    QPushButton[cssClass="success"] {{
        background-color: {SUCCESS};
        color: white;
        border: none;
    }}
    QPushButton[cssClass="success"]:hover {{
        background-color: #00d4a8;
    }}

    /* ── Progress Bar ──────────────────────────────────────────────── */
    QProgressBar {{
        background-color: {BG_TERTIARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        text-align: center;
        color: {TEXT_PRIMARY};
        font-weight: 600;
        min-height: 18px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {ACCENT}, stop:1 {ACCENT_SECONDARY}
        );
        border-radius: 5px;
    }}

    /* ── Line Edit ─────────────────────────────────────────────────── */
    QLineEdit {{
        background-color: {BG_TERTIARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {FONT_SIZE_MD};
    }}
    QLineEdit:focus {{
        border-color: {ACCENT};
    }}

    /* ── Tool Tip ──────────────────────────────────────────────────── */
    QToolTip {{
        background-color: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: {FONT_SIZE_SM};
    }}

    /* ── Menu Bar ──────────────────────────────────────────────────── */
    QMenuBar {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        border-bottom: 1px solid {BORDER};
        padding: 2px;
    }}
    QMenuBar::item:selected {{
        background-color: {BG_TERTIARY};
        border-radius: 4px;
    }}
    QMenu {{
        background-color: {BG_SECONDARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 4px;
    }}
    QMenu::item:selected {{
        background-color: {ACCENT};
        color: white;
        border-radius: 4px;
    }}

    /* ── Status Bar ────────────────────────────────────────────────── */
    QStatusBar {{
        background-color: {BG_SECONDARY};
        color: {TEXT_SECONDARY};
        border-top: 1px solid {BORDER};
        font-size: {FONT_SIZE_SM};
    }}
    """
