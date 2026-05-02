"""
Evaluation worker — runs trained model in a Gymnasium environment
with rgb_array rendering, streaming frames to the GUI.
"""

import traceback
import numpy as np

import gymnasium as gym
from PyQt6.QtCore import QThread, pyqtSignal


class EvaluationWorker(QThread):
    """
    Background thread for evaluating a trained RL model.
    
    Renders each step and emits frames for the GUI.

    Signals:
        frame_ready(ndarray)              – RGB frame HxWx3
        eval_step_info(dict)              – per-step info (reward, step #, episode #)
        eval_episode_complete(int, float, int) – (episode_idx, total_reward, ep_length)
        evaluation_complete(list)          – list of per-episode result dicts
        evaluation_error(str)              – error message
        evaluation_stopped()               – emitted on cancellation
    """

    frame_ready = pyqtSignal(np.ndarray)
    eval_step_info = pyqtSignal(dict)
    eval_episode_complete = pyqtSignal(int, float, int)
    evaluation_complete = pyqtSignal(list)
    evaluation_error = pyqtSignal(str)
    evaluation_stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False
        self._model = None
        self._env_id: str = ""
        self._n_eval_episodes: int = 5
        self._seed: int | None = None
        self._render_delay_ms: int = 16  # ~60 FPS pacing

    def configure(
        self,
        model,
        env_id: str,
        n_eval_episodes: int = 5,
        seed: int | None = None,
        render_delay_ms: int = 16,
    ):
        """Set evaluation parameters before calling start()."""
        self._model = model
        self._env_id = env_id
        self._n_eval_episodes = n_eval_episodes
        self._seed = seed
        self._render_delay_ms = render_delay_ms
        self._stop_flag = False

    def stop(self):
        """Request graceful stop of evaluation."""
        self._stop_flag = True

    def run(self):
        """Execute the evaluation loop (called by QThread.start())."""
        env = None
        try:
            # Create environment with rgb_array render mode
            env = gym.make(self._env_id, render_mode="rgb_array")
            results = []

            for ep_idx in range(self._n_eval_episodes):
                if self._stop_flag:
                    self.evaluation_stopped.emit()
                    return

                obs, info = env.reset(
                    seed=(self._seed + ep_idx) if self._seed is not None else None
                )
                total_reward = 0.0
                step_count = 0
                terminated = False
                truncated = False

                while not (terminated or truncated):
                    if self._stop_flag:
                        self.evaluation_stopped.emit()
                        return

                    # Get action from trained model
                    action, _ = self._model.predict(obs, deterministic=True)
                    obs, reward, terminated, truncated, info = env.step(action)
                    total_reward += reward
                    step_count += 1

                    # Render and emit frame
                    frame = env.render()
                    if frame is not None:
                        self.frame_ready.emit(frame)

                    # Emit step info for HUD overlay
                    self.eval_step_info.emit({
                        "episode": ep_idx + 1,
                        "total_episodes": self._n_eval_episodes,
                        "step": step_count,
                        "cumulative_reward": round(total_reward, 2),
                    })

                    # Pacing delay
                    QThread.msleep(self._render_delay_ms)

                # Episode complete
                ep_result = {
                    "episode": ep_idx + 1,
                    "reward": total_reward,
                    "length": step_count,
                }
                results.append(ep_result)
                self.eval_episode_complete.emit(
                    ep_idx + 1, total_reward, step_count
                )

            self.evaluation_complete.emit(results)

        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            self.evaluation_error.emit(err_msg)
        finally:
            if env is not None:
                try:
                    env.close()
                except Exception:
                    pass
