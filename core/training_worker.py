import os
import time
import gymnasium as gym
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from stable_baselines3 import PPO, SAC, TD3, A2C, DQN
from stable_baselines3.common.callbacks import BaseCallback
from core.algorithms import import_algorithm_class, ALGORITHM_REGISTRY

class DashboardCallback(BaseCallback):
    def __init__(self, verbose=0, render_env=False):
        super().__init__(verbose)
        self.metrics = []
        self.last_timestep = 0
        self.start_time = time.time()
        self.render_env = render_env
        self.last_frame_time = 0

    def _on_step(self):
        t = self.num_timesteps
        # Collect metrics every ~1000 steps
        if t - self.last_timestep >= 1000 or self.last_timestep == 0:
            self.last_timestep = t
            elapsed = time.time() - self.start_time
            fps = t / elapsed if elapsed > 0 else 0
            data = {
                "timestep": t,
                "fps": fps,
                "time_elapsed": elapsed,
            }
            if "ep_rew_mean" in self.model.ep_info_buffer:
                data["ep_rew_mean"] = np.mean([e["r"] for e in self.model.ep_info_buffer])
                data["ep_len_mean"] = np.mean([e["l"] for e in self.model.ep_info_buffer])
            # Losses (if available)
            if hasattr(self.model, "logger") and self.model.logger.name_to_value:
                losses = {}
                for key in ["train/policy_gradient_loss", "train/value_loss", "train/entropy_loss",
                            "train/actor_loss", "train/critic_loss", "train/loss"]:
                    if key in self.model.logger.name_to_value:
                        losses[key.split("/")[-1]] = self.model.logger.name_to_value[key]
                if losses:
                    data["losses"] = losses
            self.metrics.append(data)
            # Émettre via une variable partagée (le worker lira)
            if hasattr(self, "worker_ref"):
                self.worker_ref.metrics_queue.append(data)

        # Rendu optionnel
        if self.render_env and hasattr(self, "worker_ref") and self.worker_ref:
            now = time.time()
            if now - self.last_frame_time >= 0.033:  # ~30 fps
                self.last_frame_time = now
                try:
                    # Récupérer la frame RGB depuis l'environnement
                    if hasattr(self.training_env, "envs") and self.training_env.envs:
                        env = self.training_env.envs[0]
                        if hasattr(env, "render_mode") and env.render_mode == "rgb_array":
                            frame = env.render()
                            if frame is not None:
                                self.worker_ref.frame_queue.append(frame)
                except:
                    pass
        return True

class TrainingWorker(QThread):
    metrics_updated = pyqtSignal(dict)
    progress_updated = pyqtSignal(int)
    training_complete = pyqtSignal(str)
    training_error = pyqtSignal(str)
    training_stopped = pyqtSignal()
    frame_ready = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False
        self._config = None
        self.trained_model = None
        self.metrics_queue = []
        self.frame_queue = []
        self._timer = None

    def configure(self, env_id, algo_name, total_timesteps, seed=None, hyperparams=None, save_dir="saved_models", render=False):
        self._config = {
            "env_id": env_id,
            "algo_name": algo_name,
            "total_timesteps": total_timesteps,
            "seed": seed,
            "hyperparams": hyperparams or {},
            "save_dir": save_dir,
            "render": render,
        }

    def stop(self):
        self._stop_flag = True

    def run(self):
        self._stop_flag = False
        self.metrics_queue.clear()
        self.frame_queue.clear()
        try:
            cfg = self._config
            if cfg["render"]:
                env = gym.make(cfg["env_id"], render_mode="rgb_array")
            else:
                env = gym.make(cfg["env_id"])
            if cfg["seed"] is not None:
                env.reset(seed=cfg["seed"])

            algo_class = import_algorithm_class(cfg["algo_name"])
            model = algo_class("MlpPolicy", env, verbose=0, **cfg["hyperparams"])
            callback = DashboardCallback(render_env=cfg["render"])
            callback.worker_ref = self

            # Timer pour vider les queues
            self._timer = QTimer()
            self._timer.timeout.connect(self._process_queues)
            self._timer.start(100)

            model.learn(total_timesteps=cfg["total_timesteps"], callback=callback)
            self.trained_model = model

            os.makedirs(cfg["save_dir"], exist_ok=True)
            path = os.path.join(cfg["save_dir"], f"{cfg['algo_name']}_{cfg['env_id']}.zip")
            model.save(path)
            self.training_complete.emit(path)
        except Exception as e:
            self.training_error.emit(str(e))
        finally:
            if self._timer:
                self._timer.stop()
            self._process_queues()  # dernier flush
            if self._stop_flag:
                self.training_stopped.emit()

    def _process_queues(self):
        while self.metrics_queue:
            m = self.metrics_queue.pop(0)
            self.metrics_updated.emit(m)
            if "timestep" in m and self._config:
                prog = int(100 * m["timestep"] / self._config["total_timesteps"])
                self.progress_updated.emit(prog)
        while self.frame_queue:
            frame = self.frame_queue.pop(0)
            self.frame_ready.emit(frame)