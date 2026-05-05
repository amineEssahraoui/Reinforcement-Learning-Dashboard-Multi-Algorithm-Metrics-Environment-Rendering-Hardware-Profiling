"""
Dark/Light theme configuration for the RL Dashboard.
Colors improved for better contrast and professional look.
"""

# ─── Color Tokens (dark mode default) ──────────────────────────────────────

BG_PRIMARY = "#0a0c12"
BG_SECONDARY = "#12141c"
BG_TERTIARY = "#1a1d2b"
BG_ELEVATED = "#25293a"
BG_CARD = "#1e212f"

ACCENT = "#7c3aed"
ACCENT_HOVER = "#8b5cf6"
ACCENT_PRESSED = "#6d28d9"
ACCENT_SECONDARY = "#06b6d4"
ACCENT_SECONDARY_HOVER = "#22d3ee"

SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"

TEXT_PRIMARY = "#f3f4f6"
TEXT_SECONDARY = "#9ca3af"
TEXT_DISABLED = "#4b5563"

BORDER = "#2d313e"
BORDER_FOCUS = "#7c3aed"

# Chart colors – plus distincts et visibles
CHART_REWARD = "#8b5cf6"
CHART_LOSS_POLICY = "#f97316"
CHART_LOSS_VALUE = "#facc15"
CHART_LOSS_ENTROPY = "#2dd4bf"
CHART_EP_LENGTH = "#10b981"
CHART_EVAL_BAR = "#8b5cf6"
CHART_GRID = "#374151"
CHART_BG = "#0f111a"

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
        "BG_PRIMARY":     "#0a0c12",
        "BG_SECONDARY":   "#12141c",
        "BG_TERTIARY":    "#1a1d2b",
        "BG_ELEVATED":    "#25293a",
        "BG_CARD":        "#1e212f",
        "TEXT_PRIMARY":   "#f3f4f6",
        "TEXT_SECONDARY": "#9ca3af",
        "TEXT_DISABLED":  "#4b5563",
        "BORDER":         "#2d313e",
        "CHART_BG":       "#0f111a",
        "CHART_GRID":     "#374151",
    },
    "light": {
        "BG_PRIMARY":     "#f8fafc",
        "BG_SECONDARY":   "#ffffff",
        "BG_TERTIARY":    "#f1f5f9",
        "BG_ELEVATED":    "#e2e8f0",
        "BG_CARD":        "#f1f5f9",
        "TEXT_PRIMARY":   "#0f172a",
        "TEXT_SECONDARY": "#334155",
        "TEXT_DISABLED":  "#94a3b8",
        "BORDER":         "#cbd5e1",
        "CHART_BG":       "#f8fafc",
        "CHART_GRID":     "#e2e8f0",
    },
}

_current_mode: str = "dark"

def set_theme(mode: str) -> None:
    global _current_mode
    if mode not in _THEME_PALETTE:
        raise ValueError(f"Unknown theme: {mode!r}. Choose 'dark' or 'light'.")
    _current_mode = mode
    palette = _THEME_PALETTE[mode]
    g = globals()
    for key, value in palette.items():
        g[key] = value

def get_current_mode() -> str:
    return _current_mode

# ─── Global Stylesheet ───────────────────────────────────────────────────────

def get_stylesheet() -> str:
    return f"""
    /* Global */
    QMainWindow, QWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_MD};
    }}

    /* Scroll areas */
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: {BG_SECONDARY};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BG_TERTIARY};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {ACCENT};
    }}

    /* Splitter */
    QSplitter::handle {{
        background: {BORDER};
        width: 2px;
    }}
    QSplitter::handle:hover {{
        background: {ACCENT};
    }}

    /* TabWidget */
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-top: none;
        border-radius: 10px;
        background: {BG_SECONDARY};
    }}
    QTabBar::tab {{
        background: transparent;
        color: {TEXT_SECONDARY};
        padding: 8px 20px;
        border-bottom: 2px solid transparent;
        font-weight: 600;
    }}
    QTabBar::tab:selected {{
        color: {ACCENT};
        border-bottom: 2px solid {ACCENT};
    }}
    QTabBar::tab:hover:!selected {{
        color: {TEXT_PRIMARY};
        border-bottom: 2px solid {BORDER};
    }}

    /* GroupBox */
    QGroupBox {{
        background: {BG_TERTIARY};
        border: 1px solid {BORDER};
        border-radius: 10px;
        margin-top: 16px;
        padding-top: 12px;
    }}
    QGroupBox::title {{
        color: {TEXT_SECONDARY};
        font-size: {FONT_SIZE_SM};
        font-weight: 700;
        left: 12px;
        padding: 0 8px;
    }}

    /* ComboBox, SpinBox, LineEdit */
    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
        background: {BG_TERTIARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 6px 10px;
        min-height: 28px;
    }}
    QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{
        border-color: {ACCENT};
    }}
    QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
        border-color: {ACCENT};
    }}

    /* Buttons */
    QPushButton {{
        background: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background: {BG_TERTIARY};
        border-color: {ACCENT};
    }}
    QPushButton:pressed {{
        background: {ACCENT};
        color: white;
    }}

    QPushButton#primaryButton {{
        background: {ACCENT};
        color: white;
        border: none;
    }}
    QPushButton#primaryButton:hover {{
        background: {ACCENT_HOVER};
    }}
    QPushButton#dangerButton {{
        background: {DANGER};
        color: white;
        border: none;
    }}
    QPushButton#successButton {{
        background: {SUCCESS};
        color: white;
        border: none;
    }}

    /* Custom containers */
    #panelContainer {{
        background: {BG_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 16px;
    }}
    #statsContainer {{
        background: {BG_ELEVATED};
        border-radius: 12px;
        border: 1px solid {BORDER};
    }}
    #appHeader {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {BG_SECONDARY}, stop:1 {BG_PRIMARY});
        border: 1px solid {BORDER};
        border-radius: 16px;
    }}
    """