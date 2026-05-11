from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QEvent

from ui.header_bar import HeaderBar
from ui.metrics_panel import MetricsPanel
from ui.environment_render import RenderPanel
from ui.config_popup_new import ConfigModal
from ui.hardware_monitor_modal import HardwareMonitorModal
from ui import theme

from core.training_worker import TrainingWorker
from core.evaluation_worker import EvaluationWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RL Dashboard — Multi-Algorithm")
        self.resize(1100, 700)
        self.setMinimumSize(800, 500)

        self.training_worker = TrainingWorker()
        self.eval_worker = EvaluationWorker()

        self._setup_ui()
        self._setup_popups()
        self._connect_signals()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = HeaderBar()
        main_layout.addWidget(self.header)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.metrics_panel = MetricsPanel()
        self.render_panel = RenderPanel()
        
        self.splitter.addWidget(self.metrics_panel)
        self.splitter.addWidget(self.render_panel)
        
        self.splitter.setSizes([450, 650]) 
        
        main_layout.addWidget(self.splitter, stretch=1)

    def _setup_popups(self):
        self.config_modal = ConfigModal(self)
        self.hardware_modal = HardwareMonitorModal(self)

    def _connect_signals(self):
        self.header.config_toggled.connect(self._toggle_config_modal)
        self.header.hardware_toggled.connect(self._toggle_hardware_modal)
        self.header.theme_toggled.connect(self._toggle_theme)

        self.config_modal.train_requested.connect(self._start_training)
        self.config_modal.stop_requested.connect(self._stop_all)
        self.config_modal.load_model_requested.connect(self._load_model)
        self.config_modal.eval_requested.connect(self._start_evaluation)

        self.training_worker.metrics_updated.connect(self.metrics_panel.update_metrics)
        self.training_worker.metrics_updated.connect(self._update_progress)
        self.training_worker.training_finished.connect(self._on_training_finished)
        self.training_worker.training_error.connect(self._show_error)

        self.eval_worker.frame_ready.connect(self.render_panel.receive_frame)
        self.eval_worker.eval_step_info.connect(self.render_panel.update_hud)
        self.eval_worker.evaluation_error.connect(self._show_error)

    def _toggle_config_modal(self, show: bool):
        if show:
            self.header.hardware_toggled.emit(False)
            self.config_modal.exec()
            self.header.btn_config.setChecked(False)
        else:
            self.config_modal.reject()

    def _toggle_hardware_modal(self, show: bool):
        if show:
            self.header.config_toggled.emit(False)
            self.hardware_modal.exec()
            self.header.btn_hardware.setChecked(False)
        else:
            self.hardware_modal.reject()


    def _start_training(self, config: dict):
        self._stop_all() 
        self.metrics_panel.clear_data()
        self.render_panel.set_info(config["algo_name"], config["env_id"])
        
        self.training_worker.configure(**config)
        self.training_worker.start()

    def _load_model(self, path: str):
        algo_name = self.config_modal.combo_algo.currentText()
        self.training_worker.load_model(algo_name, path)
        QMessageBox.information(self, "Success", f"Model {algo_name} loaded successfully!\nYou can now launch an evaluation or continue training.")

    def _start_evaluation(self):
        if self.training_worker.model is None:
            QMessageBox.warning(self, "Warning", "No model is loaded or trained. Please first load a model or launch a training.")
            return

        self._stop_all()
        self.render_panel.clear_video()
        env_id = self.config_modal.combo_env.currentData()
        
        self.eval_worker.configure(
            model=self.training_worker.model,
            env_id=env_id,
            n_eval_episodes=5
        )
        self.eval_worker.start()

    def _stop_all(self):
        if self.training_worker.isRunning():
            self.training_worker.stop()
            self.training_worker.wait()
        if self.eval_worker.isRunning():
            self.eval_worker.stop()
            self.eval_worker.wait()

    def _update_progress(self, metrics: dict):
        progress = int(metrics.get("progress", 0.0) * 100)
        self.render_panel.update_progress(progress)

    def _on_training_finished(self, save_path: str):
        self.render_panel.update_progress(100)
        QMessageBox.information(self, "Training Complete", f"Model saved at:\n{save_path}")

    def _show_error(self, err_msg: str):
        QMessageBox.critical(self, "Error", err_msg)

    def _toggle_theme(self):
        app = QApplication.instance()
        if app is None:
            return
        theme.toggle_theme()
        app.setStyleSheet(theme.get_stylesheet())
        self.header.sync_theme_icon()

    def closeEvent(self, event):
        self._stop_all()
        event.accept()
