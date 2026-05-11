from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QTextEdit, QSizeGrip
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui import theme
from core.ai.chat_worker import AIChatWorker

class ChatMessage(QWidget):
    def __init__(self, text: str, is_user: bool = False, is_typing: bool = False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        colors = theme.COLORS
        if is_user: layout.addStretch()
        
        self.message_label = QLabel(text)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 10))
        
        bg_color = colors['accent'] if is_user else colors['bg_hover']
        text_color = "#FFFFFF" if is_user else colors['text_main']
        style = "letter-spacing: 2px; font-weight: bold;" if is_typing else ""
        
        self.message_label.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; padding: 10px 14px; border-radius: 8px; {style}")
        self.message_label.setMaximumWidth(260)
        
        layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft)
        if not is_user: layout.addStretch()

class ChatWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.resize(340, 500)
        self.drag_position = None
        self.typing_widget = None
        
        self.ai_worker = AIChatWorker(model_name="llama3.2:latest")
        self.ai_worker.response_ready.connect(self.add_assistant_message)
        self.ai_worker.error_occurred.connect(self.add_assistant_message)
        self.ai_worker.start()
        
        self._setup_ui()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        colors = theme.COLORS
        self.setStyleSheet(f"QDialog {{ background-color: {colors['bg_app']}; border: 1px solid {colors['border']}; border-radius: 10px; }}")
        
        header = QWidget()
        header.setStyleSheet(f"background-color: {colors['bg_surface']}; border-bottom: 1px solid {colors['border']}; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        h_layout = QHBoxLayout(header)
        title = QLabel("🤖 AI Assistant")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"QPushButton {{ border: none; color: {colors['text_muted']}; }} QPushButton:hover {{ color: #EF4444; }}")
        btn_close.clicked.connect(self.hide)
        h_layout.addWidget(title); h_layout.addStretch(); h_layout.addWidget(btn_close)
        main_layout.addWidget(header)
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.msg_layout = QVBoxLayout(self.container)
        self.msg_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.welcome = QLabel("Your AI assistant to help you understand these algorithms and environments.")
        self.welcome.setWordWrap(True); self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome.setStyleSheet(f"color: {colors['text_muted']}; font-style: italic; margin-top: 40px;")
        self.msg_layout.addWidget(self.welcome)
        
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll, stretch=1)
        
        # Input
        input_box = QWidget()
        input_box.setStyleSheet(f"background-color: {colors['bg_surface']}; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        i_layout = QHBoxLayout(input_box)
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Ask a question...")
        self.input_field.setMaximumHeight(40)
        btn_send = QPushButton("Send")
        btn_send.setFixedSize(60, 40)
        btn_send.setStyleSheet(f"QPushButton {{ background-color: {colors['accent']}; color: white; border-radius: 6px; font-weight: bold; }}")
        btn_send.clicked.connect(self._handle_send)
        
        i_layout.addWidget(self.input_field)
        i_layout.addWidget(btn_send)
        main_layout.addWidget(input_box)
        
        QSizeGrip(self).setFixedSize(15, 15)

    def _handle_send(self):
        text = self.input_field.toPlainText().strip()
        if text:
            if self.welcome.isVisible(): self.welcome.hide()
            self._add_message(text, is_user=True)
            self.input_field.clear()
            self.typing_widget = self._add_message("...", is_user=False, is_typing=True)
            self.ai_worker.ask_question(text)

    def _add_message(self, text, is_user=False, is_typing=False):
        msg = ChatMessage(text, is_user, is_typing)
        self.msg_layout.addWidget(msg)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum() + 50)
        return msg

    def add_assistant_message(self, text):
        if self.typing_widget:
            self.msg_layout.removeWidget(self.typing_widget)
            self.typing_widget.deleteLater()
            self.typing_widget = None
        self._add_message(text, is_user=False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 50:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def closeEvent(self, event):
        self.ai_worker.stop()
        self.ai_worker.wait()
        super().closeEvent(event)