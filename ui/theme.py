"""
Dark theme configuration for the RL Dashboard.
Defines color tokens, fonts, and global QSS stylesheets.
"""

# ─── Color Tokens ────────────────────────────────────────────────────────────

BG_PRIMARY = "#0d0f18"
BG_SECONDARY = "#151823"
BG_TERTIARY = "#1e2130"
BG_ELEVATED = "#252838"
BG_CARD = "#1b1e2b"

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
CHART_GRID = "#252838"
CHART_BG = "#0f1119"

# ─── Font ─────────────────────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI, Inter, Roboto, sans-serif"
FONT_SIZE_SM = "11px"
FONT_SIZE_MD = "13px"
FONT_SIZE_LG = "16px"
FONT_SIZE_XL = "22px"
FONT_SIZE_TITLE = "28px"

# ─── Theme Registry ──────────────────────────────────────────────────────────

_THEME_PALETTE: dict = {
    "dark": {
        "BG_PRIMARY":     "#0d0f18",
        "BG_SECONDARY":   "#151823",
        "BG_TERTIARY":    "#1e2130",
        "BG_ELEVATED":    "#252838",
        "BG_CARD":        "#1b1e2b",
        "TEXT_PRIMARY":   "#e8e8e8",
        "TEXT_SECONDARY": "#8b8d97",
        "TEXT_DISABLED":  "#555860",
        "BORDER":         "#2d303a",
        "CHART_BG":       "#0f1119",
        "CHART_GRID":     "#252838",
    },
    "light": {
        "BG_PRIMARY":     "#f4f5fb",
        "BG_SECONDARY":   "#ffffff",
        "BG_TERTIARY":    "#edf0f8",
        "BG_ELEVATED":    "#e5e8f2",
        "BG_CARD":        "#f9fafd",
        "TEXT_PRIMARY":   "#1c1e2d",
        "TEXT_SECONDARY": "#616479",
        "TEXT_DISABLED":  "#b5b8cc",
        "BORDER":         "#d4d7e8",
        "CHART_BG":       "#f8f9fd",
        "CHART_GRID":     "#e5e8f2",
    },
}

_current_mode: str = "dark"


def set_theme(mode: str) -> None:
    """Switch the active theme and update all module-level color tokens."""
    global _current_mode
    if mode not in _THEME_PALETTE:
        raise ValueError(f"Unknown theme: {mode!r}. Choose 'dark' or 'light'.")
    _current_mode = mode
    palette = _THEME_PALETTE[mode]
    g = globals()
    for key, value in palette.items():
        g[key] = value


def get_current_mode() -> str:
    """Return the currently active theme mode ('dark' or 'light')."""
    return _current_mode


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
        border-top: none;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        background-color: {BG_SECONDARY};
    }}
    QTabBar {{
        background: transparent;
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
        padding: 9px 22px;
        margin-right: 2px;
        border: none;
        border-bottom: 2px solid transparent;
        font-weight: 600;
        font-size: {FONT_SIZE_MD};
    }}
    QTabBar::tab:selected {{
        color: {ACCENT};
        border-bottom: 2px solid {ACCENT};
        background-color: transparent;
    }}
    QTabBar::tab:hover:!selected {{
        color: {TEXT_PRIMARY};
        border-bottom: 2px solid {BORDER};
    }}

    /* ── Group Box ─────────────────────────────────────────────────── */
    QGroupBox {{
        background-color: {BG_TERTIARY};
        border: 1px solid {BORDER};
        border-radius: 10px;
        margin-top: 18px;
        padding: 14px 12px 12px 12px;
        font-weight: 600;
        font-size: {FONT_SIZE_MD};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 3px 12px;
        color: {TEXT_SECONDARY};
        font-size: {FONT_SIZE_SM};
        font-weight: 700;
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
        outline: 0;
        padding: 2px;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 28px;
        padding: 0 10px;
        border-radius: 4px;
    }}
    QComboBox QAbstractItemView::item:hover:!disabled {{
        background-color: {BG_ELEVATED};
    }}
    QComboBox QAbstractItemView::item:selected:!disabled {{
        background-color: {ACCENT};
        color: white;
    }}
    QComboBox QAbstractItemView::item:disabled {{
        color: {TEXT_DISABLED};
        background: transparent;
        min-height: 22px;
        padding: 4px 10px 2px 10px;
        font-size: 10px;
        font-weight: 700;
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
        width: 22px;
        height: 50%;
        border-left: 1px solid {BORDER};
        border-top-right-radius: 6px;
        background-color: {BG_ELEVATED};
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 22px;
        height: 50%;
        border-left: 1px solid {BORDER};
        border-bottom-right-radius: 6px;
        background-color: {BG_ELEVATED};
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {ACCENT};
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {TEXT_SECONDARY};
        width: 0;
        height: 0;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY};
        width: 0;
        height: 0;
    }}

    /* ── Push Button Base ──────────────────────────────────────────── */
    QPushButton {{
        background-color: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 600;
        min-height: 28px;
    }}
    QPushButton:hover {{
        background-color: {BG_TERTIARY};
        border-color: {ACCENT};
        color: white;
    }}
    QPushButton:pressed {{
        background-color: {ACCENT};
    }}

    /* ── Action Buttons (Train, Stop, Eval) ────────────────────────── */
    QPushButton#primaryButton {{
        background-color: {ACCENT};
        color: white;
        border: none;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton#dangerButton {{
        background-color: {DANGER};
        color: white;
        border: none;
    }}
    QPushButton#successButton {{
        background-color: {SUCCESS};
        color: white;
        border: none;
    }}

    /* ── Toggle Bar ────────────────────────────────── */
    QPushButton#toggleBar {{
        background-color: {BG_TERTIARY};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 4px;
        font-size: 14px;
    }}
    QPushButton#toggleBar:hover {{
        background-color: {ACCENT};
        color: white;
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
        padding: 2px 8px;
    }}

    /* ── Form Label ────────────────────────────────────────────────── */
    QFormLayout QLabel {{
        color: {TEXT_SECONDARY};
        font-size: {FONT_SIZE_SM};
    }}

    /* ── Custom Containers & Headers ───────────────────────────────── */
    #panelContainer {{
        background-color: {BG_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}
    #statsContainer {{
        background-color: {BG_ELEVATED};
        border-radius: 8px;
        border: 1px solid {BORDER};
    }}
    #appHeader {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {BG_SECONDARY}, stop:1 {BG_PRIMARY}
        );
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    /* ── Centralized Button + Container Overrides (additional) ── */
    QPushButton {{
        border-radius: 6px;
        padding: 6px 16px;
        min-height: 28px;
        border: 1px solid {BORDER};
        background-color: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {BG_TERTIARY};
        border-color: {ACCENT};
        color: white;
    }}

    /* Action button ids */
    QPushButton#primaryButton {{
        background-color: {ACCENT};
        color: white;
        border: 1px solid {BORDER};
    }}
    QPushButton#primaryButton:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton#dangerButton {{
        background-color: {DANGER};
        color: white;
        border: 1px solid {BORDER};
    }}
    QPushButton#successButton {{
        background-color: {SUCCESS};
        color: white;
        border: 1px solid {BORDER};
    }}

    QPushButton#toggleBar {{
        background-color: {BG_TERTIARY};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 4px;
        font-size: 14px;
    }}
    QPushButton#toggleBar:hover {{
        background-color: {ACCENT};
        color: white;
    }}
    """
