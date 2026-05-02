# RL Dashboard 🧠

**Reinforcement Learning Prototyping Tool** — A comprehensive PyQt6 desktop application for training, evaluating, and visualizing RL agents.

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green)
![SB3](https://img.shields.io/badge/Stable--Baselines3-2.3%2B-orange)

---

## Features

- **13 RL Algorithms** from Stable Baselines3 + SB3-Contrib
  - On-Policy: A2C, PPO, TRPO, RecurrentPPO, MaskablePPO
  - Off-Policy: DQN, DDPG, SAC, TD3, QR-DQN, TQC, CrossQ
  - Population: ARS
- **Live Training Metrics** — Real-time pyqtgraph charts (reward, loss, episode length)
- **Environment Visualization** — Embedded Gymnasium render via rgb_array
- **Hyperparameter Editing** — Full UI for tweaking algorithm parameters
- **Model Persistence** — Save/load trained models to disk
- **Auto-Compatibility Filtering** — Only shows algorithms compatible with the selected environment
- **Dark Theme** — Modern glassmorphism design

---

## Installation

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)

### Step 1: System Dependencies (for Box2D environments)

Box2D environments (e.g., LunarLander) require **SWIG** to compile.

#### Windows
```bash
# Option A: Using Chocolatey
choco install swig

# Option B: Using Conda
conda install swig

# Option C: Manual install
# Download from https://www.swig.org/download.html
# Add swig.exe to your system PATH
```

#### macOS
```bash
brew install swig
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install swig
```

### Step 2: Create Virtual Environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If you don't need Box2D environments, you can install without them:
> ```bash
> pip install PyQt6 pyqtgraph gymnasium stable-baselines3 sb3-contrib numpy torch
> ```

### Step 4: (Optional) Install additional environment suites

```bash
# MuJoCo environments (requires MuJoCo physics engine)
pip install "gymnasium[mujoco]"

# Atari environments
pip install "gymnasium[atari]"
pip install "gymnasium[accept-rom-license]"
```

---

## Usage

```bash
python main.py
```

### Workflow

1. **Select Environment** — Choose from Classic Control, Box2D, MuJoCo, etc.
2. **Select Algorithm** — Pick from the auto-filtered compatible algorithms
3. **Tune Hyperparameters** — Adjust learning rate, gamma, batch size, etc.
4. **Train** — Click ▶ Train to start headless training (fast, no rendering)
5. **Monitor** — Watch live metrics on the left panel
6. **Evaluate** — Click 👁 Evaluate to watch the trained agent play
7. **Save/Load** — Models are auto-saved; load previous models anytime

---

## Project Structure

```
projet_dekstop/
├── main.py                       # App entry point
├── requirements.txt              # Dependencies
├── README.md                     # This file
│
├── core/
│   ├── __init__.py
│   ├── algorithms.py             # Algorithm registry (13 algorithms)
│   ├── training_worker.py        # QThread for training
│   ├── evaluation_worker.py      # QThread for evaluation + render
│   └── callbacks.py              # SB3 callback for live metrics
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py            # Main application window
│   ├── theme.py                  # Dark theme + QSS
│   ├── metrics_panel.py          # Pyqtgraph live charts
│   ├── environment_render.py     # Gymnasium frame viewer
│   ├── environment_controls.py   # Config + action buttons
│   └── hardware_panel.py         # Hardware monitoring (placeholder)
│
└── saved_models/                 # Auto-created for model persistence
```

---

## Roadmap

- [ ] **v1.1** — Hardware Profiling (CPU, GPU, RAM, Threads via psutil/GPUtil)
- [ ] **v2.0** — AI Assistant Chatbot integration
- [ ] **v2.1** — Multi-agent comparison (train multiple algorithms side by side)
- [ ] **v2.2** — TensorBoard integration
- [ ] **v3.0** — Custom environment builder

---

## License

MIT License
