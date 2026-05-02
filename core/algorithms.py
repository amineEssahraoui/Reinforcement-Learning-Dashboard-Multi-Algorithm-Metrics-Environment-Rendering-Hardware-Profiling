"""
Algorithm registry for Stable Baselines3 and SB3-Contrib.
Provides metadata, compatibility filtering, hyperparameter configs,
and model creation utilities.
"""

import gymnasium as gym
from typing import Any


# ─── Algorithm Metadata ──────────────────────────────────────────────────────

ALGORITHM_REGISTRY: dict[str, dict[str, Any]] = {
    # ── Stable Baselines3 (core) ──────────────────────────────────
    "A2C": {
        "module": "stable_baselines3",
        "class_name": "A2C",
        "category": "On-Policy",
        "action_spaces": ["Box", "Discrete", "MultiDiscrete", "MultiBinary"],
        "policy": "MlpPolicy",
        "description": "Advantage Actor-Critic — synchronous, deterministic variant of A3C",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 7e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "n_steps": {"type": "int", "default": 5, "min": 1, "max": 10000},
            "gae_lambda": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "ent_coef": {"type": "float", "default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "vf_coef": {"type": "float", "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "max_grad_norm": {"type": "float", "default": 0.5, "min": 0.0, "max": 10.0, "step": 0.1, "decimals": 2},
        },
    },
    "PPO": {
        "module": "stable_baselines3",
        "class_name": "PPO",
        "category": "On-Policy",
        "action_spaces": ["Box", "Discrete", "MultiDiscrete", "MultiBinary"],
        "policy": "MlpPolicy",
        "description": "Proximal Policy Optimization — clipped surrogate objective",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 3e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "n_steps": {"type": "int", "default": 2048, "min": 1, "max": 100000},
            "batch_size": {"type": "int", "default": 64, "min": 1, "max": 10000},
            "n_epochs": {"type": "int", "default": 10, "min": 1, "max": 100},
            "gae_lambda": {"type": "float", "default": 0.95, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "clip_range": {"type": "float", "default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "ent_coef": {"type": "float", "default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "vf_coef": {"type": "float", "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "max_grad_norm": {"type": "float", "default": 0.5, "min": 0.0, "max": 10.0, "step": 0.1, "decimals": 2},
        },
    },
    "DQN": {
        "module": "stable_baselines3",
        "class_name": "DQN",
        "category": "Off-Policy",
        "action_spaces": ["Discrete"],
        "policy": "MlpPolicy",
        "description": "Deep Q-Network — value-based with experience replay",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 1e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 32, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 50000, "min": 0, "max": 1000000},
            "tau": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "train_freq": {"type": "int", "default": 4, "min": 1, "max": 1000},
            "target_update_interval": {"type": "int", "default": 10000, "min": 1, "max": 100000},
            "exploration_fraction": {"type": "float", "default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "exploration_final_eps": {"type": "float", "default": 0.05, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
        },
    },
    "DDPG": {
        "module": "stable_baselines3",
        "class_name": "DDPG",
        "category": "Off-Policy",
        "action_spaces": ["Box"],
        "policy": "MlpPolicy",
        "description": "Deep Deterministic Policy Gradient — continuous action off-policy",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 1e-3, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 256, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 100, "min": 0, "max": 1000000},
            "tau": {"type": "float", "default": 0.005, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "train_freq": {"type": "int", "default": 1, "min": 1, "max": 1000},
        },
    },
    "SAC": {
        "module": "stable_baselines3",
        "class_name": "SAC",
        "category": "Off-Policy",
        "action_spaces": ["Box"],
        "policy": "MlpPolicy",
        "description": "Soft Actor-Critic — maximum entropy off-policy",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 3e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 256, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 100, "min": 0, "max": 1000000},
            "tau": {"type": "float", "default": 0.005, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "train_freq": {"type": "int", "default": 1, "min": 1, "max": 1000},
            "ent_coef": {"type": "str", "default": "auto", "options": ["auto"]},
        },
    },
    "TD3": {
        "module": "stable_baselines3",
        "class_name": "TD3",
        "category": "Off-Policy",
        "action_spaces": ["Box"],
        "policy": "MlpPolicy",
        "description": "Twin Delayed DDPG — addresses overestimation bias in DDPG",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 1e-3, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 256, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 100, "min": 0, "max": 1000000},
            "tau": {"type": "float", "default": 0.005, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "train_freq": {"type": "int", "default": 1, "min": 1, "max": 1000},
            "policy_delay": {"type": "int", "default": 2, "min": 1, "max": 100},
        },
    },

    # ── SB3-Contrib ───────────────────────────────────────────────
    "TRPO": {
        "module": "sb3_contrib",
        "class_name": "TRPO",
        "category": "On-Policy",
        "action_spaces": ["Box", "Discrete", "MultiDiscrete", "MultiBinary"],
        "policy": "MlpPolicy",
        "description": "Trust Region Policy Optimization — KL-constrained policy updates",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 1e-3, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "n_steps": {"type": "int", "default": 2048, "min": 1, "max": 100000},
            "batch_size": {"type": "int", "default": 128, "min": 1, "max": 10000},
            "gae_lambda": {"type": "float", "default": 0.95, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "target_kl": {"type": "float", "default": 0.01, "min": 0.001, "max": 1.0, "step": 0.001, "decimals": 4},
        },
    },
    "RecurrentPPO": {
        "module": "sb3_contrib",
        "class_name": "RecurrentPPO",
        "category": "On-Policy",
        "action_spaces": ["Box", "Discrete", "MultiDiscrete", "MultiBinary"],
        "policy": "MlpLstmPolicy",
        "description": "PPO with LSTM — handles partial observability",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 3e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "n_steps": {"type": "int", "default": 128, "min": 1, "max": 100000},
            "batch_size": {"type": "int", "default": 128, "min": 1, "max": 10000},
            "n_epochs": {"type": "int", "default": 10, "min": 1, "max": 100},
            "gae_lambda": {"type": "float", "default": 0.95, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
            "clip_range": {"type": "float", "default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
        },
    },
    "MaskablePPO": {
        "module": "sb3_contrib",
        "class_name": "MaskablePPO",
        "category": "On-Policy",
        "action_spaces": ["Discrete", "MultiDiscrete", "MultiBinary"],
        "policy": "MlpPolicy",
        "description": "PPO with invalid action masking",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 3e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "n_steps": {"type": "int", "default": 2048, "min": 1, "max": 100000},
            "batch_size": {"type": "int", "default": 64, "min": 1, "max": 10000},
            "n_epochs": {"type": "int", "default": 10, "min": 1, "max": 100},
            "clip_range": {"type": "float", "default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
        },
    },
    "ARS": {
        "module": "sb3_contrib",
        "class_name": "ARS",
        "category": "Population",
        "action_spaces": ["Box", "Discrete"],
        "policy": "LinearPolicy",
        "description": "Augmented Random Search — gradient-free evolutionary method",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 0.02, "min": 1e-6, "max": 1.0, "step": 0.001, "decimals": 4},
            "n_delta": {"type": "int", "default": 8, "min": 1, "max": 1000},
            "n_top": {"type": "int", "default": 1, "min": 1, "max": 1000},
            "delta_std": {"type": "float", "default": 0.05, "min": 0.001, "max": 1.0, "step": 0.001, "decimals": 4},
        },
    },
    "QR-DQN": {
        "module": "sb3_contrib",
        "class_name": "QRDQN",
        "category": "Off-Policy",
        "action_spaces": ["Discrete"],
        "policy": "MlpPolicy",
        "description": "Quantile Regression DQN — distributional value function",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 5e-5, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 32, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 50000, "min": 0, "max": 1000000},
            "target_update_interval": {"type": "int", "default": 10000, "min": 1, "max": 100000},
            "exploration_fraction": {"type": "float", "default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "decimals": 3},
        },
    },
    "TQC": {
        "module": "sb3_contrib",
        "class_name": "TQC",
        "category": "Off-Policy",
        "action_spaces": ["Box"],
        "policy": "MlpPolicy",
        "description": "Truncated Quantile Critics — distributional SAC variant",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 3e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 256, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 100, "min": 0, "max": 1000000},
            "tau": {"type": "float", "default": 0.005, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "top_quantiles_to_drop_per_net": {"type": "int", "default": 2, "min": 0, "max": 100},
        },
    },
    "CrossQ": {
        "module": "sb3_contrib",
        "class_name": "CrossQ",
        "category": "Off-Policy",
        "action_spaces": ["Box"],
        "policy": "MlpPolicy",
        "description": "CrossQ — batch-normalised critic for improved sample efficiency",
        "hyperparams": {
            "learning_rate": {"type": "float", "default": 1e-4, "min": 1e-6, "max": 1.0, "step": 1e-5, "decimals": 6},
            "gamma": {"type": "float", "default": 0.99, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
            "batch_size": {"type": "int", "default": 256, "min": 1, "max": 10000},
            "buffer_size": {"type": "int", "default": 1000000, "min": 1000, "max": 10000000},
            "learning_starts": {"type": "int", "default": 100, "min": 0, "max": 1000000},
            "tau": {"type": "float", "default": 0.005, "min": 0.0, "max": 1.0, "step": 0.001, "decimals": 4},
        },
    },
}


def get_action_space_name(env_id: str) -> str:
    """Get the action space type name for a given environment."""
    try:
        spec = gym.spec(env_id)
        env = gym.make(env_id)
        space_name = type(env.action_space).__name__
        env.close()
        return space_name
    except Exception:
        return "Unknown"


def get_compatible_algorithms(env_id: str) -> list[str]:
    """Return algorithm names compatible with the given environment's action space."""
    space_name = get_action_space_name(env_id)
    compatible = []
    for name, meta in ALGORITHM_REGISTRY.items():
        if space_name in meta["action_spaces"]:
            compatible.append(name)
    return compatible


def import_algorithm_class(algo_name: str):
    """Lazily import and return the algorithm class."""
    meta = ALGORITHM_REGISTRY[algo_name]
    module_name = meta["module"]
    class_name = meta["class_name"]
    
    if module_name == "stable_baselines3":
        import stable_baselines3
        return getattr(stable_baselines3, class_name)
    elif module_name == "sb3_contrib":
        import sb3_contrib
        return getattr(sb3_contrib, class_name)
    else:
        raise ValueError(f"Unknown module: {module_name}")


def create_model(algo_name: str, env, seed: int = None, **overrides):
    """
    Create a model instance for the given algorithm and environment.
    
    Args:
        algo_name: Key from ALGORITHM_REGISTRY
        env: Gymnasium environment (already wrapped with Monitor)
        seed: Optional random seed for reproducibility
        overrides: Hyperparameter overrides from the UI
    """
    meta = ALGORITHM_REGISTRY[algo_name]
    cls = import_algorithm_class(algo_name)
    policy = meta["policy"]
    
    # Build hyperparams dict from defaults, then apply overrides
    hyperparams = {}
    for key, cfg in meta["hyperparams"].items():
        if key in overrides:
            hyperparams[key] = overrides[key]
        else:
            hyperparams[key] = cfg["default"]
    
    # Remove special string-type params that need special handling
    if "ent_coef" in hyperparams and hyperparams["ent_coef"] == "auto":
        hyperparams["ent_coef"] = "auto"
    
    if seed is not None:
        hyperparams["seed"] = seed
    
    model = cls(policy, env, verbose=0, **hyperparams)
    return model


def get_environment_list() -> dict[str, list[str]]:
    """
    Get categorised list of Gymnasium environments that support rgb_array.
    Returns dict mapping category name -> list of env IDs.
    """
    categories = {
        "Classic Control": [],
        "Box2D": [],
        "MuJoCo": [],
        "Toy Text": [],
        "Other": [],
    }
    
    for env_id in sorted(gym.envs.registry.keys()):
        try:
            spec = gym.spec(env_id)
            # Skip older versions and internal envs
            if "/" in env_id and not env_id.startswith("ALE"):
                continue
            
            # Try to categorise
            namespace = spec.namespace
            entry_point = str(spec.entry_point) if spec.entry_point else ""
            
            if "classic_control" in entry_point:
                categories["Classic Control"].append(env_id)
            elif "box2d" in entry_point:
                categories["Box2D"].append(env_id)
            elif "mujoco" in entry_point:
                categories["MuJoCo"].append(env_id)
            elif "toy_text" in entry_point:
                categories["Toy Text"].append(env_id)
            else:
                categories["Other"].append(env_id)
        except Exception:
            continue
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}
