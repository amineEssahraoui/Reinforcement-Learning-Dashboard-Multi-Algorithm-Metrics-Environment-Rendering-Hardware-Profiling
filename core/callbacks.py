import time
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

class DashboardCallback(BaseCallback):
    def __init__(self, emit_fn, total_timesteps, stop_flag_fn=None, throttle_seconds=0.25, frame_emit_fn=None, verbose=0):
        super().__init__(verbose)
        self._emit_fn = emit_fn
        self._total_timesteps = total_timesteps
        self._stop_flag_fn = stop_flag_fn
        self._throttle_seconds = throttle_seconds
        self._frame_emit_fn = frame_emit_fn  # Nouveau : pour la vidéo
        self._last_emit_time = 0.0
        self._last_frame_time = 0.0
        self._start_time = None

    def _on_training_start(self):
        self._start_time = time.time()

    def _on_step(self) -> bool:
        if self._stop_flag_fn and self._stop_flag_fn():
            return False

        now = time.time()
        
        # --- NOUVEAU : Capture vidéo pendant l'entraînement (~10 FPS max) ---
        if self._frame_emit_fn and (now - self._last_frame_time > 0.1):
            try:
                # Récupère l'image depuis l'environnement d'entraînement
                frame = self.training_env.render(mode="rgb_array")
                if frame is not None:
                    self._frame_emit_fn(frame)
            except Exception:
                pass
            self._last_frame_time = now

        # --- Envoi des métriques ---
        if now - self._last_emit_time > self._throttle_seconds:
            self._emit_fn(self._collect_metrics())
            self._last_emit_time = now

        return True

    def _collect_metrics(self) -> dict:
        timestep = self.num_timesteps
        elapsed = time.time() - self._start_time if self._start_time else 0
        fps = timestep / elapsed if elapsed > 0 else 0
        progress = min(timestep / self._total_timesteps, 1.0)

        metrics = {"timestep": timestep, "progress": progress, "fps": round(fps, 1), "time_elapsed": round(elapsed, 1)}

        ep_info_buffer = getattr(self.model, "ep_info_buffer", None)
        if ep_info_buffer and len(ep_info_buffer) > 0:
            metrics["ep_rew_mean"] = float(np.mean([ep["r"] for ep in ep_info_buffer]))
            metrics["ep_len_mean"] = float(np.mean([ep["l"] for ep in ep_info_buffer]))

        losses = {}
        if hasattr(self, "logger") and self.logger is not None:
            name_to_value = getattr(self.logger, "name_to_value", {})
            for key in ["train/loss", "train/policy_gradient_loss", "train/value_loss"]:
                if key in name_to_value: losses[key.split("/")[-1]] = name_to_value[key]
        metrics["losses"] = losses

        return metrics