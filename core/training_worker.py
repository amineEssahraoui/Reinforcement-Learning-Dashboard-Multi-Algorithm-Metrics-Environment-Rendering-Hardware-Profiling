import os
import traceback
import numpy as np
import gymnasium as gym
from PyQt6.QtCore import QThread, pyqtSignal

from core.algorithms import create_model, import_algorithm_class
from core.callbacks import DashboardCallback

class TrainingWorker(QThread):
    metrics_updated = pyqtSignal(dict)
    training_finished = pyqtSignal(str)
    training_error = pyqtSignal(str)
    training_stopped = pyqtSignal()
    frame_ready = pyqtSignal(np.ndarray) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False
        self.model = None
        self.env = None
        self.config = {}

    def configure(self, algo_name: str, env_id: str, total_timesteps: int, seed: int = None, hyperparams: dict = None):
        self.config = {
            "algo_name": algo_name,
            "env_id": env_id,
            "total_timesteps": total_timesteps,
            "seed": seed,
            "hyperparams": hyperparams or {}
        }
        self._stop_flag = False
        self.model = None 

    def load_model(self, algo_name: str, path: str):
        try:
            cls = import_algorithm_class(algo_name)
            self.model = cls.load(path)
            self.config["algo_name"] = algo_name
        except Exception as e:
            self.training_error.emit(f"Erreur lors du chargement : {str(e)}")

    def stop(self):
        self._stop_flag = True

    def run(self):
        try:
            self.env = gym.make(self.config["env_id"], render_mode="rgb_array")
            
            if self.model is None:
                self.model = create_model(
                    algo_name=self.config["algo_name"],
                    env=self.env,
                    seed=self.config.get("seed"),
                    **self.config.get("hyperparams", {})
                )
            else:
                self.model.set_env(self.env)

            def check_stop(): return self._stop_flag

            callback = DashboardCallback(
                emit_fn=self.metrics_updated.emit,
                total_timesteps=self.config["total_timesteps"],
                stop_flag_fn=check_stop,
                throttle_seconds=0.25,
                frame_emit_fn=self.frame_ready.emit
            )

            self.model.learn(
                total_timesteps=self.config["total_timesteps"],
                callback=callback,
                reset_num_timesteps=False
            )

            if not self._stop_flag:
                save_dir = "saved_models"
                os.makedirs(save_dir, exist_ok=True)
                save_filename = f"{self.config['algo_name']}_{self.config['env_id']}.zip"
                save_path = os.path.join(save_dir, save_filename)
                
                self.model.save(save_path)
                self.training_finished.emit(save_path)
            else:
                self.training_stopped.emit()

        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            self.training_error.emit(err_msg)
        finally:
            if self.env is not None:
                try: self.env.close()
                except Exception: pass