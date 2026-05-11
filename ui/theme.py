from PyQt6.QtWidgets import QApplication

_THEME_PALETTES = {
    "dark": {
        "bg_app": "#18181B",
        "bg_surface": "#27272A",
        "bg_hover": "#3F3F46",
        "border": "#3F3F46",
        "text_main": "#F4F4F5",
        "text_muted": "#A1A1AA",
        "accent": "#6366F1",
        "accent_hover": "#4F46E5",
        "chart_reward": "#10B981",
        "chart_loss": "#F43F5E",
        "chart_len": "#0EA5E9",
        "chart_cpu": "#8B5CF6",
        "chart_ram": "#F59E0B",
        "btn_stop": "#EF4444",
        "btn_eval": "#0EA5E9",
    },
    "light": {
        "bg_app": "#F4F4F5",
        "bg_surface": "#FFFFFF",
        "bg_hover": "#E4E4E7",
        "border": "#D4D4D8",
        "text_main": "#18181B",
        "text_muted": "#52525B",
        "accent": "#4F46E5",
        "accent_hover": "#4338CA",
        "chart_reward": "#059669",
        "chart_loss": "#E11D48",
        "chart_len": "#0284C7",
        "chart_cpu": "#7C3AED",
        "chart_ram": "#D97706",
        "btn_stop": "#DC2626",
        "btn_eval": "#0284C7",
    },
}

_current_mode = "dark"
COLORS = dict(_THEME_PALETTES[_current_mode])

def get_pyqtgraph_color(key: str) -> str:
    return COLORS.get(key, "#FFFFFF")


def set_theme(mode: str):
    global _current_mode
    if mode not in _THEME_PALETTES:
        return
    _current_mode = mode
    COLORS.clear()
    COLORS.update(_THEME_PALETTES[mode])


def get_current_mode() -> str:
    return _current_mode


def toggle_theme() -> str:
    new_mode = "light" if _current_mode == "dark" else "dark"
    set_theme(new_mode)
    return new_mode

def get_stylesheet() -> str:
    return f"""
        QWidget {{
            background-color: {COLORS["bg_app"]};
            color: {COLORS["text_main"]};
            font-family: "Segoe UI", "San Francisco", "Helvetica Neue", sans-serif;
            font-size: 12px;
        }}
        
        #MetricsPanel, #RenderPanel {{
            background-color: {COLORS["bg_surface"]};
            border-radius: 8px;
            border: 1px solid {COLORS["border"]};
        }}
        
        #HeaderBar {{
            background-color: {COLORS["bg_surface"]};
            border-bottom: 1px solid {COLORS["border"]};
        }}
        
        QPushButton {{
            background-color: {COLORS["bg_surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 6px 12px;
            color: {COLORS["text_muted"]};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {COLORS["bg_hover"]};
            color: {COLORS["text_main"]};
        }}
        QPushButton:checked {{
            background-color: {COLORS["accent"]};
            color: #FFFFFF;
            border: 1px solid {COLORS["accent"]};
        }}

        QToolButton {{
            background-color: {COLORS["bg_surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 14px;
            padding: 4px 8px;
            color: {COLORS["text_main"]};
        }}
        QToolButton:hover {{
            background-color: {COLORS["bg_hover"]};
        }}
        
        /* Boutons d'action spécifiques (avec des classes dynamiques) */
        QPushButton.btn-primary {{
            background-color: {COLORS["accent"]};
            color: white;
            border: none;
        }}
        QPushButton.btn-primary:hover {{ background-color: {COLORS["accent_hover"]}; }}
        
        QPushButton.btn-danger {{ background-color: {COLORS["btn_stop"]}; color: white; border: none; }}
        QPushButton.btn-info {{ background-color: {COLORS["btn_eval"]}; color: white; border: none; }}
        
        /* Combobox (Menus déroulants) */
        QComboBox {{
            background-color: {COLORS["bg_app"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 4px 8px;
            color: {COLORS["text_main"]};
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{
            background-color: {COLORS["bg_surface"]};
            color: {COLORS["text_main"]};
            selection-background-color: {COLORS["accent"]};
        }}
        
        #OverlayPopup {{
            background-color: {COLORS["bg_surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 8px;
        }}
        
        QSplitter::handle {{
            background-color: {COLORS["bg_app"]};
        }}
    """

def apply_theme(app: QApplication):
    app.setStyleSheet(get_stylesheet())
