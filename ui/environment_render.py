"""
Environment Render Widget — displays Gymnasium rgb_array frames
with an overlay HUD showing episode stats.
"""

import numpy as np
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGraphicsOpacityEffect

from ui.theme import (
    BG_SECONDARY, BG_TERTIARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, ACCENT_SECONDARY, SUCCESS, FONT_FAMILY,
)

class EnvironmentRenderWidget(QWidget):
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

        self._container = QWidget()
        self._container.setObjectName("panelContainer")
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(2, 2, 2, 2)

        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 8, 10, 4)
        self._title_accent = QFrame()
        self._title_accent.setFixedSize(3, 16)
        self._title_accent.setStyleSheet(f"background: {SUCCESS}; border-radius: 2px;")
        title_layout.addWidget(self._title_accent)
        self._title_label = QLabel("Environment Render")
        self._title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 700;")
        title_layout.addWidget(self._title_label)
        title_layout.addStretch()
        container_layout.addWidget(title_bar)

        self._frame_label = QLabel()
        self._frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._frame_label.setMinimumSize(300, 200)
        self._frame_label.setStyleSheet(f"background: #0a0c12; border-radius: 8px; margin: 4px;")
        container_layout.addWidget(self._frame_label, 1)

        self._opacity_effect = QGraphicsOpacityEffect(self._frame_label)
        self._frame_label.setGraphicsEffect(self._opacity_effect)
        layout.addWidget(self._container)
        self.show_placeholder("")

    def show_placeholder(self, env_name: str = ""):
        self._env_name = env_name
        self._has_frame = False
        w = self._frame_label.width() or 400
        h = self._frame_label.height() or 300
        pix = QPixmap(w, h)
        pix.fill(QColor("#0a0c14"))
        painter = QPainter(pix)
        painter.setPen(QPen(QColor(BORDER), 1))
        for x in range(0, w, 24):
            for y in range(0, h, 24):
                painter.drawPoint(x, y)
        card_w, card_h = 260, 110
        card_x = (w - card_w)//2
        card_y = (h - card_h)//2
        painter.setBrush(QColor(BG_TERTIARY))
        painter.setPen(QPen(QColor(BORDER)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 10, 10)
        painter.setPen(QColor(TEXT_PRIMARY))
        painter.setFont(QFont(FONT_FAMILY.split(",")[0], 12, QFont.Weight.Bold))
        painter.drawText(card_x, card_y+20, card_w, 30, Qt.AlignmentFlag.AlignCenter, env_name or "No Environment")
        painter.setPen(QColor(TEXT_SECONDARY))
        painter.setFont(QFont(FONT_FAMILY.split(",")[0], 9))
        painter.drawText(card_x, card_y+52, card_w, 24, Qt.AlignmentFlag.AlignCenter, "Awaiting evaluation or training")
        painter.end()
        self._frame_label.setPixmap(pix)

    def update_frame(self, frame: np.ndarray):
        if frame is None: return
        if not self._has_frame:
            self._has_frame = True
            anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
            anim.setDuration(400)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch*w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(self._frame_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        if self._hud_info:
            pix = self._draw_hud(pix)
        self._frame_label.setPixmap(pix)

    def update_hud(self, episode=0, total_episodes=0, step=0, cumulative_reward=0.0):
        self._hud_info = {"episode": episode, "total": total_episodes, "step": step, "reward": cumulative_reward}

    def clear_hud(self):
        self._hud_info = {}

    def _draw_hud(self, pixmap: QPixmap) -> QPixmap:
        result = pixmap.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        info = self._hud_info
        ep_text = f"Episode {info.get('episode', '?')}/{info.get('total', '?')}"
        step_text = f"Step: {info.get('step', 0)}"
        reward_text = f"Reward: {info.get('reward', 0):.2f}"
        painter.fillRect(0, 0, result.width(), 36, QColor(0,0,0,180))
        painter.setPen(QColor(ACCENT_SECONDARY))
        painter.setFont(QFont(FONT_FAMILY.split(",")[0], 11, QFont.Weight.Bold))
        painter.drawText(12, 24, ep_text)
        painter.setPen(QColor(TEXT_PRIMARY))
        sw = painter.fontMetrics().horizontalAdvance(step_text)
        painter.drawText((result.width()-sw)//2, 24, step_text)
        rw = painter.fontMetrics().horizontalAdvance(reward_text)
        painter.setPen(QColor(SUCCESS if info.get('reward',0)>=0 else DANGER))
        painter.drawText(result.width()-rw-12, 24, reward_text)
        painter.end()
        return result