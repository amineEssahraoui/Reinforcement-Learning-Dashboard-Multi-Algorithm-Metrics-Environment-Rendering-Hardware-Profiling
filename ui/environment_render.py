"""
Environment Render Widget — displays Gymnasium rgb_array frames
in a QLabel with an overlay HUD showing episode stats.
"""

import numpy as np
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QPen, QLinearGradient
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGraphicsOpacityEffect

from ui.theme import (
    BG_SECONDARY, BG_TERTIARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, ACCENT_SECONDARY, SUCCESS, FONT_FAMILY,
)


class EnvironmentRenderWidget(QWidget):
    """
    Widget that displays Gymnasium environment frames with HUD overlay.
    
    Usage:
        widget.update_frame(numpy_rgb_array)
        widget.update_hud(episode=1, total_episodes=5, step=42, reward=195.0)
        widget.show_placeholder("CartPole-v1")
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hud_info = {}
        self._has_frame = False
        self._env_name = ""
        self._setup_ui()

    def _setup_ui(self):
        self.setMinimumSize(320, 240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container with rounded border
        self._container = QWidget()
        self._container.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(0)

        # Title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("background: transparent; border: none;")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 8, 10, 4)
        title_bar_layout.setSpacing(10)

        self._title_accent_bar = QFrame()
        self._title_accent_bar.setFixedSize(3, 16)
        self._title_accent_bar.setStyleSheet(f"background-color: {SUCCESS}; border-radius: 2px; border: none;")
        title_bar_layout.addWidget(self._title_accent_bar)

        self._title_label = QLabel("Environment Render")
        self._title_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 700;
                background-color: transparent;
                border: none;
            }}
        """)
        title_bar_layout.addWidget(self._title_label)
        title_bar_layout.addStretch()
        container_layout.addWidget(title_bar)

        # Frame display area
        self._frame_label = QLabel()
        self._frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._frame_label.setMinimumSize(300, 200)
        self._frame_label.setStyleSheet(f"""
            QLabel {{
                background-color: #0a0c12;
                border-radius: 8px;
                border: none;
                margin: 4px;
            }}
        """)
        container_layout.addWidget(self._frame_label, 1)

        # Opacity effect for fade-in
        self._opacity_effect = QGraphicsOpacityEffect(self._frame_label)
        self._opacity_effect.setOpacity(1.0)
        self._frame_label.setGraphicsEffect(self._opacity_effect)

        layout.addWidget(self._container)

        # Show initial placeholder
        self.show_placeholder("")

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
        self._title_label.setStyleSheet(f"""
            QLabel {{
                color: {t.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 700;
                background-color: transparent;
                border: none;
            }}
        """)
        if self._has_frame:
            return
        self.show_placeholder(self._env_name)

    def show_placeholder(self, env_name: str = ""):
        """Show a styled placeholder when no frames are being displayed."""
        self._env_name = env_name
        self._has_frame = False

        name_display = env_name if env_name else "No Environment Selected"

        w = self._frame_label.width() or 400
        h = self._frame_label.height() or 300
        pixmap = QPixmap(w, h)
        pixmap.fill(QColor("#0a0c14"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Subtle dot grid pattern
        dot_pen = QPen(QColor(BORDER))
        dot_pen.setWidth(1)
        painter.setPen(dot_pen)
        spacing = 24
        for x in range(0, w, spacing):
            for y in range(0, h, spacing):
                painter.drawPoint(x, y)

        # Center card background
        card_w, card_h = 260, 110
        card_x = (w - card_w) // 2
        card_y = (h - card_h) // 2
        card_color = QColor(BG_TERTIARY)
        card_color.setAlpha(220)
        painter.setBrush(card_color)
        painter.setPen(QPen(QColor(BORDER)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 10, 10)

        # Accent top stripe on card
        stripe_color = QColor(ACCENT)
        stripe_color.setAlpha(180)
        painter.setBrush(stripe_color)
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawRoundedRect(card_x, card_y, card_w, 3, 2, 2)

        # Environment name text
        painter.setPen(QColor(TEXT_PRIMARY))
        font = QFont(FONT_FAMILY.split(",")[0].strip(), 12)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            card_x, card_y + 20, card_w, 30,
            Qt.AlignmentFlag.AlignCenter,
            name_display,
        )

        # Subtitle text
        painter.setPen(QColor(TEXT_SECONDARY))
        font2 = QFont(FONT_FAMILY.split(",")[0].strip(), 9)
        painter.setFont(font2)
        painter.drawText(
            card_x, card_y + 52, card_w, 24,
            Qt.AlignmentFlag.AlignCenter,
            "Awaiting evaluation",
        )

        painter.end()
        self._frame_label.setPixmap(pixmap)

    def update_frame(self, frame: np.ndarray):
        """
        Display a new frame from the environment.
        
        Args:
            frame: numpy array of shape (H, W, 3), dtype uint8, RGB format
        """
        if frame is None:
            return

        # Fade-in on first frame
        if not self._has_frame:
            self._has_frame = True
            self._animate_fade_in()

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        
        # Ensure contiguous memory
        frame = np.ascontiguousarray(frame)
        
        q_img = QImage(
            frame.data, w, h, bytes_per_line,
            QImage.Format.Format_RGB888
        )
        
        # Scale to fit the label while preserving aspect ratio
        label_size = self._frame_label.size()
        pixmap = QPixmap.fromImage(q_img).scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Draw HUD overlay
        if self._hud_info:
            pixmap = self._draw_hud(pixmap)

        self._frame_label.setPixmap(pixmap)

    def update_hud(self, episode: int = 0, total_episodes: int = 0,
                   step: int = 0, cumulative_reward: float = 0.0):
        """Update the HUD overlay data."""
        self._hud_info = {
            "episode": episode,
            "total_episodes": total_episodes,
            "step": step,
            "reward": cumulative_reward,
        }

    def clear_hud(self):
        """Clear the HUD overlay."""
        self._hud_info = {}

    def _draw_hud(self, pixmap: QPixmap) -> QPixmap:
        """Draw semi-transparent HUD overlay on the frame."""
        result = pixmap.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        info = self._hud_info
        ep_text = f"Episode {info.get('episode', '?')}/{info.get('total_episodes', '?')}"
        step_text = f"Step: {info.get('step', 0)}"
        reward_text = f"Reward: {info.get('reward', 0):.2f}"

        # Background bar at top
        bar_height = 36
        painter.fillRect(0, 0, result.width(), bar_height,
                         QColor(0, 0, 0, 160))

        # Episode info (left)
        painter.setPen(QColor(ACCENT_SECONDARY))
        font = QFont(FONT_FAMILY.split(",")[0].strip(), 11)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(12, 24, ep_text)

        # Step info (center)
        painter.setPen(QColor(TEXT_PRIMARY))
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        step_w = metrics.horizontalAdvance(step_text)
        painter.drawText((result.width() - step_w) // 2, 24, step_text)

        # Reward (right)
        reward_color = SUCCESS if info.get("reward", 0) > 0 else "#e17055"
        painter.setPen(QColor(reward_color))
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        reward_w = metrics.horizontalAdvance(reward_text)
        painter.drawText(result.width() - reward_w - 12, 24, reward_text)

        painter.end()
        return result

    def _animate_fade_in(self):
        """Smooth fade-in animation when the first frame arrives."""
        self._opacity_effect.setOpacity(0.0)
        anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        # Keep reference so it isn't garbage collected
        self._fade_anim = anim
