"""
Training worker — runs SB3 model.learn() in a background QThread.
Emits real-time metrics via Qt signals and supports graceful cancellation.
"""

import os
import traceback

import gymnasium as gym
from PyQt6.QtCore import QThread, pyqtSignal
from stable_baselines3.common.monitor import Monitor

from core.algorithms import create_model
from core.callbacks import DashboardCallback


class TrainingWorker(QThread):
    """
    Background thread for training an RL model.
    
    Signals:
        metrics_updated(dict)    – live training metrics (throttled)
        progress_updated(int)    – training progress percentage 0-100
        training_complete(str)   – path to saved model on success
        training_error(str)      – error message on failure
        training_stopped()       – emitted if user cancelled
    """

    metrics_updated = pyqtSignal(dict)
    progress_updated = pyqtSignal(int)
    training_complete = pyqtSignal(str)
    training_error = pyqtSignal(str)
    training_stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False
        self._env_id: str = ""
        self._algo_name: str = ""
        self._total_timesteps: int = 100_000
        self._seed: int | None = None
        self._hyperparams: dict = {}
        self._save_dir: str = "saved_models"
        
        # Exposed after training for the evaluation worker
        self.trained_model = None

    def configure(
        self,
        env_id: str,
        algo_name: str,
        total_timesteps: int,
        seed: int | None = None,
        hyperparams: dict | None = None,
        save_dir: str = "saved_models",
    ):
        """Set training parameters before calling start()."""
        self._env_id = env_id
        self._algo_name = algo_name
        self._total_timesteps = total_timesteps
        self._seed = seed
        self._hyperparams = hyperparams or {}
        self._save_dir = save_dir
        self._stop_flag = False

    def stop(self):
        """Request graceful stop of training."""
        self._stop_flag = True

    def _is_stopped(self) -> bool:
        return self._stop_flag

    def run(self):
        """Execute the training loop (called by QThread.start())."""
        self.trained_model = None  # Reset before each run
        env = None
        try:
            # Create environment (headless for speed)
            env = gym.make(self._env_id)
            env = Monitor(env)
            
            if self._seed is not None:
                env.reset(seed=self._seed)

            # Create model
            model = create_model(
                self._algo_name,
                env,
                seed=self._seed,
                **self._hyperparams,
            )

            # Setup callback
            callback = DashboardCallback(
                emit_fn=self._on_metrics,
                total_timesteps=self._total_timesteps,
                stop_flag_fn=self._is_stopped,
                throttle_seconds=0.25,
            )

            # Train
            model.learn(
                total_timesteps=self._total_timesteps,
                callback=callback,
                progress_bar=False,
            )

            # Save model (always — so evaluation works even after a stop)
            os.makedirs(self._save_dir, exist_ok=True)
            model_path = os.path.join(
                self._save_dir,
                f"{self._algo_name}_{self._env_id}".replace("/", "_")
            )
            model.save(model_path)
            self.trained_model = model

            if self._stop_flag:
                self.training_stopped.emit()
                return

            self.training_complete.emit(model_path)

        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            self.training_error.emit(err_msg)
        finally:
            if env is not None:
                try:
                    env.close()
                except Exception:
                    pass

    def _on_metrics(self, metrics: dict):
        """Called by the DashboardCallback (from the training thread)."""
        self.metrics_updated.emit(metrics)
        progress_pct = int(metrics.get("progress", 0) * 100)
        self.progress_updated.emit(progress_pct)
