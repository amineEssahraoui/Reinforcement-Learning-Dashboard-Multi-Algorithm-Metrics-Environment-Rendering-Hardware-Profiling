import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import pyqtSlot, Qt

class RenderPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RenderPanel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        self.lbl_badge = QLabel("Aucun environnement chargé")
        self.lbl_badge.setStyleSheet("font-size: 11px; color: #A1A1AA; font-weight: bold; text-transform: uppercase;")
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_badge)
        
        self.video_container = QFrame()
        self.video_container.setStyleSheet("background-color: #18181B; border-radius: 6px; border: 1px solid #3F3F46;")
        v_layout = QVBoxLayout(self.video_container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_video = QLabel("Aucun rendu\n(Lancez une évaluation)")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setStyleSheet("color: #3F3F46; font-size: 14px;")
        v_layout.addWidget(self.lbl_video)
        
        layout.addWidget(self.video_container, stretch=1)
        
        self.lbl_hud = QLabel("Ep -/- · Step - · Reward -")
        self.lbl_hud.setStyleSheet("font-size: 12px; color: #10B981; font-weight: bold;")
        self.lbl_hud.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_hud)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #27272A; border-radius: 2px; border: none; }
            QProgressBar::chunk { background-color: #6366F1; border-radius: 2px; }
        """)
        layout.addWidget(self.progress_bar)

    @pyqtSlot(np.ndarray)
    def receive_frame(self, frame: np.ndarray):
        """
        Reçoit un tableau NumPy (H, W, 3) depuis l'EvaluationWorker.
        Le convertit en QImage puis en QPixmap pour l'affichage.
        """
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        scaled_pixmap = pixmap.scaled(
            self.lbl_video.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_video.setPixmap(scaled_pixmap)

    @pyqtSlot(dict)
    def update_hud(self, info: dict):
        ep = info.get("episode", "-")
        tot = info.get("total_episodes", "-")
        step = info.get("step", "-")
        rew = info.get("cumulative_reward", "-")
        self.lbl_hud.setText(f"Ep {ep}/{tot} · Step {step} · Reward {rew}")
        
    def set_info(self, algo_name: str, env_id: str):
        self.lbl_badge.setText(f"{algo_name} · {env_id}")
        
    def update_progress(self, progress_percent: int):
        self.progress_bar.setValue(progress_percent)
        
    def clear_video(self):
        self.lbl_video.clear()
        self.lbl_video.setText("Rendu terminé")
        self.lbl_hud.setText("Ep -/- · Step - · Reward -")