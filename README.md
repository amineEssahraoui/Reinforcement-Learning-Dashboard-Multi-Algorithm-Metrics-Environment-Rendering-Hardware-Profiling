# RL Dashboard

RL Dashboard is a PyQt6 desktop application for experimenting with reinforcement learning agents built with Gymnasium, Stable Baselines3, and SB3-Contrib. It provides a local GUI for selecting an environment, configuring hyperparameters, training a model, visualizing metrics, running evaluation rollouts, checking hardware usage, and optionally querying an embedded AI assistant.

## What the application does

- Trains and evaluates RL agents from a desktop interface.
- Discovers installed Gymnasium environments and groups them by category.
- Filters algorithms automatically based on the selected environment's action space.
- Displays live training metrics with pyqtgraph.
- Streams evaluation frames into the main render panel.
- Saves trained models to `saved_models/` and lets you reload existing `.zip` models.
- Opens separate resizable dialogs for training configuration and hardware monitoring.
- Includes a floating AI chat assistant backed by a local retrieval pipeline and Ollama.

## Supported algorithms

The current registry includes 13 algorithms.

- On-policy: `A2C`, `PPO`, `TRPO`, `RecurrentPPO`, `MaskablePPO`
- Off-policy: `DQN`, `DDPG`, `SAC`, `TD3`, `QR-DQN`, `TQC`, `CrossQ`
- Population-based: `ARS`

Each algorithm exposes a UI-driven hyperparameter form generated from the registry in `core/algorithms.py`.

## Main interface

The current application layout is composed of:

- A top header bar with buttons for configuration, hardware monitoring, and theme switching.
- A metrics panel with live plots for episode reward, training loss, and episode length, plus FPS and progress badges.
- A render panel that shows evaluation frames, episode HUD information, and training progress.
- A floating chat button that opens a local AI assistant window.

Training configuration and hardware monitoring are opened as modal dialogs and are resizable.

## Environment handling

Environment discovery is based on the installed Gymnasium registry. The UI groups environments into these categories when available:

- Classic Control
- Box2D
- MuJoCo
- Toy Text
- Other

Algorithm availability is filtered by action space compatibility (`Box`, `Discrete`, `MultiDiscrete`, `MultiBinary`).

Important note: the current training and evaluation workers create environments with `render_mode="rgb_array"`. In practice, the safest choice is to use environments that support `rgb_array` rendering. If an installed environment does not support that render mode, training or evaluation can fail even if it appears in the environment list.

## AI assistant

The project includes an optional embedded AI assistant.

- UI entry points: `ui/floating_chat_button.py` and `ui/chat_window.py`
- Worker and retrieval stack: `core/ai/chat_worker.py`, `core/ai/knowledge_base.py`, `core/ai/rag_engine.py`
- Knowledge source: JSON files in `core/ai/data/`
- LLM backend: local Ollama model `llama3.2:latest`

The AI assistant uses:

- HuggingFace embeddings
- FAISS vector search
- LangChain orchestration
- A local Ollama server for generation

If Ollama is not running or the model is not available locally, the dashboard can still open, but chat responses will fail.

## Hardware monitor

The hardware monitor dialog shows rolling CPU, RAM, and GPU charts.

- Real CPU and RAM values come from `psutil` when installed.
- Real GPU values come from `GPUtil` when installed.
- If those packages are missing, the dialog falls back to placeholder random values rather than failing.

Because `psutil` and `GPUtil` are not listed in `requirements.txt`, install them manually if you want real telemetry.

## Installation

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS and Linux:

```bash
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs the desktop UI, reinforcement learning libraries, and the AI assistant dependencies defined in `requirements.txt`.

### 3. Optional dependencies

For real hardware telemetry:

```bash
pip install psutil gputil
```

For MuJoCo environments:

```bash
pip install "gymnasium[mujoco]"
```

If `gymnasium[box2d]` fails to install on your platform, install SWIG first and then retry the dependency installation.

### 4. Optional Ollama setup for the AI assistant

Install Ollama, start the local service, then pull the model used by the chat window:

```bash
ollama pull llama3.2:latest
```

## Running the application

Start the desktop app with:

```bash
python main.py
```

To test the AI stack separately from the GUI:

```bash
python core/ai/test_ai.py
```

## Typical workflow

1. Launch the application with `python main.py`.
2. Open the configuration dialog from the header.
3. Select a Gymnasium environment.
4. Select one of the algorithms compatible with that environment.
5. Adjust hyperparameters, total timesteps, and optional seed.
6. Start training.
7. Monitor reward, loss, episode length, FPS, and progress in the main window.
8. Evaluate the trained or loaded model. The current default is 5 evaluation episodes.
9. Review the rendered rollout in the render panel.
10. Load existing models from `saved_models/` when needed.

Models are saved automatically after successful training using the pattern:

```text
saved_models/<algorithm>_<environment>.zip
```

## Project structure

```text
.
|-- main.py
|-- requirements.txt
|-- README.md
|-- STATE.md
|-- saved_models/
|-- core/
|   |-- algorithms.py
|   |-- callbacks.py
|   |-- evaluation_worker.py
|   |-- training_worker.py
|   `-- ai/
|       |-- chat_worker.py
|       |-- knowledge_base.py
|       |-- rag_engine.py
|       |-- test_ai.py
|       `-- data/
`-- ui/
    |-- chat_window.py
    |-- config_popup_.py
    |-- environment_render.py
    |-- floating_chat_button.py
    |-- hardware_monitor_modal.py
    |-- header_bar.py
    |-- main_window.py
    |-- metrics_panel.py
    `-- theme.py
```

## Implementation notes

- `core/training_worker.py` handles model creation, training, stopping, and model persistence.
- `core/callbacks.py` emits throttled live metrics from Stable Baselines3 during training.
- `core/evaluation_worker.py` runs evaluation episodes in a separate thread and streams frames to the render panel.
- `ui/config_popup_.py` builds the environment, algorithm, hyperparameter, timestep, seed, and model-load controls.
- `ui/hardware_monitor_modal.py` manages the hardware telemetry dialog.
- `ui/theme.py` contains the dark/light palettes and application stylesheet.

## Troubleshooting

### Hardware values look artificial

Install `psutil` and `gputil`. Without them, the hardware dialog uses placeholder values.

### The AI assistant does not answer

Make sure Ollama is installed, running locally, and that `llama3.2:latest` has been pulled.

### Box2D dependencies fail during installation

Install SWIG first, then rerun `pip install -r requirements.txt`.

### Evaluation does not render correctly

Use an environment that supports `render_mode="rgb_array"`.
