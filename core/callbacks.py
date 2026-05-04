"""
Custom SB3 callback for streaming live training metrics to the PyQt6 GUI.
Throttled to avoid flooding the event loop.
"""

import time
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback


class DashboardCallback(BaseCallback):
    """
    SB3 callback that emits training metrics via a signal emitter function.

    Metrics emitted:
        - timestep: current training step
        - ep_rew_mean: mean episode reward (from Monitor wrapper)
        - ep_len_mean: mean episode length
        - loss: dict of loss components (varies by algorithm)
        - fps: training speed in frames per second
        - time_elapsed: seconds since training started
        - progress: training progress as 0.0-1.0 float
    """

    def __init__(
        self,
        emit_fn: callable,
        total_timesteps: int,
        stop_flag_fn: callable = None,
        throttle_seconds: float = 0.25,
        verbose: int = 0,
    ):
        super().__init__(verbose)
        self._emit_fn = emit_fn
        self._total_timesteps = total_timesteps
        self._stop_flag_fn = stop_flag_fn
        self._throttle_seconds = throttle_seconds
        self._last_emit_time = 0.0
        self._start_time = None

    def _on_training_start(self):
        self._start_time = time.time()

    def _on_step(self) -> bool:
        # Check cancellation
        if self._stop_flag_fn and self._stop_flag_fn():
            return False

        # Throttle emissions
        now = time.time()
        if now - self._last_emit_time < self._throttle_seconds:
            return True
        self._last_emit_time = now

        # Gather metrics
        metrics = self._collect_metrics()
        self._emit_fn(metrics)
        return True

    def _collect_metrics(self) -> dict:
        """Collect all available metrics from the training loop."""
        timestep = self.num_timesteps
        elapsed = time.time() - self._start_time if self._start_time else 0
        fps = timestep / elapsed if elapsed > 0 else 0
        progress = min(timestep / self._total_timesteps, 1.0)

        metrics = {
            "timestep": timestep,
            "progress": progress,
            "fps": round(fps, 1),
            "time_elapsed": round(elapsed, 1),
        }

        # ── Episode stats from ep_info_buffer (populated by Monitor wrapper) ──
        # This is the most reliable source — updated whenever an episode ends.
        ep_info_buffer = getattr(self.model, "ep_info_buffer", None)
        if ep_info_buffer and len(ep_info_buffer) > 0:
            rewards = [ep["r"] for ep in ep_info_buffer]
            lengths = [ep["l"] for ep in ep_info_buffer]
            metrics["ep_rew_mean"] = float(np.mean(rewards))
            metrics["ep_len_mean"] = float(np.mean(lengths))
        else:
            # Fallback: try logger (may lag behind by one rollout)
            if hasattr(self, "logger") and self.logger is not None:
                name_to_value = getattr(self.logger, "name_to_value", {})
                if "rollout/ep_rew_mean" in name_to_value:
                    metrics["ep_rew_mean"] = name_to_value["rollout/ep_rew_mean"]
                if "rollout/ep_len_mean" in name_to_value:
                    metrics["ep_len_mean"] = name_to_value["rollout/ep_len_mean"]

        # ── Loss values (algorithm-dependent) ────────────────────
        losses = {}
        if hasattr(self, "logger") and self.logger is not None:
            name_to_value = getattr(self.logger, "name_to_value", {})
            loss_keys = [
                "train/loss",
                "train/policy_gradient_loss",
                "train/value_loss",
                "train/entropy_loss",
                "train/actor_loss",
                "train/critic_loss",
                "train/approx_kl",
                "train/clip_fraction",
                "train/explained_variance",
            ]
            for key in loss_keys:
                if key in name_to_value:
                    short_key = key.split("/")[-1]
                    losses[short_key] = name_to_value[key]
        metrics["losses"] = losses

        return metrics
