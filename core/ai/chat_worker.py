import queue
import traceback
from PyQt6.QtCore import QThread, pyqtSignal

from core.ai.knowledge_base import KnowledgeBase
from core.ai.rag_engine import RAGEngine

class AIChatWorker(QThread):
    engine_ready = pyqtSignal()           
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, data_dir: str = "core/ai/data", model_name: str = "llama3:8b", parent=None):
        super().__init__(parent)
        self.data_dir = data_dir
        self.model_name = model_name
        
        self.engine = None
        self._queue = queue.Queue()
        self._is_running = True

    def ask_question(self, question: str):
        self._queue.put(question)

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            kb = KnowledgeBase(data_dir=self.data_dir)
            retriever = kb.get_retriever(top_k=3)
            self.engine = RAGEngine(retriever=retriever, model_name=self.model_name)
            self.engine_ready.emit()
            
        except Exception as e:
            err_msg = f"Failed to initialize AI Engine: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(err_msg)
            return 

        while self._is_running:
            try:
                question = self._queue.get(timeout=0.5)
                response = self.engine.ask(question)
                self.response_ready.emit(response)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.error_occurred.emit(f"AI Generation Error: {str(e)}")