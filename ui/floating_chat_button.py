from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from ui import theme

class FloatingChatButton(QPushButton):
    
    def __init__(self, parent=None):
        super().__init__("💬", parent)
        self.setFixedSize(48, 48) 
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.drag_position = None
        self.is_dragging = False
        self._apply_style()

    def _apply_style(self):
        colors = theme.COLORS
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent']};
                border: none;
                border-radius: 24px;
                font-size: 20px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_hover']};
            }}
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.is_dragging = False
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.drag_position is not None:
            current_pos = event.globalPosition().toPoint()
            if (current_pos - self.drag_position).manhattanLength() > 5:
                self.is_dragging = True
                delta = current_pos - self.drag_position
                self.move(self.pos() + delta)
                self.drag_position = current_pos
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.setDown(False) 
                event.ignore()
                self.drag_position = None
                return
            self.drag_position = None
        super().mouseReleaseEvent(event)