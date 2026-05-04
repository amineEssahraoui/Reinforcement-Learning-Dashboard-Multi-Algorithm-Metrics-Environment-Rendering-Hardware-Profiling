# Project State — RL Dashboard

> Last updated: May 4, 2026  
> Purpose: Handoff document so a collaborator can understand exactly what is done, what is broken, and what to build next.

---

## What This App Does

A PyQt6 desktop application for training and evaluating reinforcement learning agents locally. It wraps Stable Baselines3 in a GUI with:

- A **configuration panel** (right) to pick environment + algorithm + hyperparameters
- A **metrics panel** (left) with live pyqtgraph charts updating during training
- An **environment render panel** (center) showing the agent playing after evaluation
- A **hardware profiling panel** (left, below metrics) — placeholder only for now
- A **light / dark theme toggle** in the header

Run with: `python main.py`

---

## ✅ Implemented and Working

### Core Training Pipeline
- `core/training_worker.py` — Runs `model.learn()` in a `QThread` so the UI never freezes
- `core/callbacks.py` — `DashboardCallback` reads `model.ep_info_buffer` (the SB3 Monitor deque) to get reliable episode reward and episode length. Falls back to `logger.name_to_value` for loss values
- Model is **always saved before checking the stop flag** — so even if the user clicks Stop mid-training, the partial model is written to disk and available for evaluation
- `core/evaluation_worker.py` — Runs the saved model in a `QThread` with `rgb_array` rendering, streams frames to the center panel

### Algorithm Registry (`core/algorithms.py`)
13 algorithms fully registered with hyperparameter configs and action-space compatibility metadata:

| Algorithm | Library | Category | Action Spaces |
|-----------|---------|----------|---------------|
| A2C | SB3 | On-Policy | Box, Discrete, MultiDiscrete, MultiBinary |
| PPO | SB3 | On-Policy | Box, Discrete, MultiDiscrete, MultiBinary |
| TRPO | SB3-Contrib | On-Policy | Box, Discrete, MultiDiscrete, MultiBinary |
| RecurrentPPO | SB3-Contrib | On-Policy | Box, Discrete, MultiDiscrete, MultiBinary |
| MaskablePPO | SB3-Contrib | On-Policy | Discrete, MultiDiscrete, MultiBinary |
| DQN | SB3 | Off-Policy | Discrete |
| DDPG | SB3 | Off-Policy | Box |
| SAC | SB3 | Off-Policy | Box |
| TD3 | SB3 | Off-Policy | Box |
| QR-DQN | SB3-Contrib | Off-Policy | Discrete |
| TQC | SB3-Contrib | Off-Policy | Box |
| CrossQ | SB3-Contrib | Off-Policy | Box |
| ARS | SB3-Contrib | Population | Box, Discrete |

The combo boxes in the UI auto-filter to only show algorithms compatible with the selected environment.

### Configuration Panel (`ui/environment_controls.py`)
- Environment combo box: categorised list (Classic Control, Box2D, MuJoCo, etc.) with disabled header rows
- Algorithm combo box: same pattern, also filtered by compatibility
- Both combos store the real ID in `Qt.ItemDataRole.UserRole` — category headers return `None` so they can never be accidentally submitted as a selection
- Hyperparameter section: dynamically rebuilt on algorithm change. Supports `float` (QDoubleSpinBox), `int` (QSpinBox), `str` (QLineEdit)
- Training config: total timesteps, eval episodes, random seed
- Model persistence: save directory field + Load Model button
- Button layout: 2×2 grid (Train | Stop / Evaluate | Reset) so labels never get clipped

### Metrics Panel (`ui/metrics_panel.py`)
- **Training tab**: Episode Reward chart, Training Loss chart, Episode Length chart
- **Evaluation tab**: Reward per Episode bar chart
- Stats bar below charts: Timesteps (accent), FPS (cyan), Reward (green), Elapsed (yellow)
- Summary Statistics groupbox with best/mean/std values updated at the end of training
- Charts use `pyqtgraph` PlotWidget with custom styling

### Environment Render Panel (`ui/environment_render.py`)
- Shows a dot-grid placeholder before evaluation starts
- Displays the environment name once selected
- Renders `rgb_array` frames from the evaluation worker as a scaled `QPixmap`
- HUD overlay shows step/episode/reward during live evaluation

### Hardware Panel (`ui/hardware_panel.py`)
- 4 cards: CPU Usage, RAM Usage, GPU Usage, Threads
- Each card has a colored top border, a pill badge ("Soon"), a value label, and a mini pyqtgraph sparkline chart
- **All values are static placeholders** — no actual hardware polling is connected

### Theme System (`ui/theme.py`)
- Two palettes: `"dark"` (default) and `"light"` — stored in `_THEME_PALETTE` dict
- `set_theme(mode)` updates the module-level color token globals (e.g. `BG_PRIMARY`, `TEXT_PRIMARY`) and saves the active mode
- `get_current_mode()` returns `"dark"` or `"light"`
- `get_stylesheet()` is an f-string function — re-calling it after `set_theme()` produces the correct stylesheet for the new mode
- Toggle button in header calls `QApplication.instance().setStyleSheet(theme.get_stylesheet())` then cascades `refresh_theme()` to every panel

### `refresh_theme()` on all panels
All panels have `refresh_theme()` wired to the header toggle:
- `MetricsPanel.refresh_theme()` — updates container borders, stats bar, and all pyqtgraph chart backgrounds/pens
- `HardwarePanel.refresh_theme()` / `HardwareCard.refresh_theme()` — updates container and all 4 cards
- `EnvironmentControls.refresh_theme()` — updates container (uses `#configContainer` object-name selector to avoid bleeding into child widgets)
- `EnvironmentRenderWidget.refresh_theme()` — updates container, title label, accent bar; re-renders placeholder if no live frame

---

## ⚠️ Known Limitations / Partial Issues

### Hardware Profiling — Placeholder Only
The 4 hardware cards show `— %` and `— / — GB` with no live data.  
`psutil` and `GPUtil` are listed in `requirements.txt` but never imported.  
A polling `QTimer` needs to be added inside `HardwarePanel` to call `psutil.cpu_percent()`, `psutil.virtual_memory()`, etc. and push values to the cards.

### pyqtgraph charts flicker on theme change
The `refresh_theme()` call on charts works correctly but triggers a brief white flash because `setBackground()` forces a repaint. Not a bug, but noticeable.

### Evaluation only works with a freshly trained model in the same session
The "Load Model" button opens a file dialog but the loaded model is **not yet connected** to the evaluation worker. The evaluation flow currently only works via `training_worker.trained_model`. See `main_window.py` → `_on_load_model()`.

### MuJoCo environments require a separate install
`pip install "gymnasium[mujoco]"` — not in the base `requirements.txt`. If an environment fails to load, the algo combo will be blank.

### No persistent config across sessions
Hyperparameter edits, selected environment/algorithm, and seed are not saved between app launches.

---

## 🔲 Left To Build

### High Priority

1. **Hardware Panel — Live Data**  
   File: `ui/hardware_panel.py`  
   Add a `QTimer` in `HardwarePanel.__init__` polling `psutil` every second:
   ```python
   import psutil
   self._timer = QTimer(self)
   self._timer.timeout.connect(self._update_hardware)
   self._timer.start(1000)
   ```
   Push CPU % to `self._cards[0]._value_label`, RAM to `[1]`, etc.  
   For GPU, try `import GPUtil; GPUtil.getGPUs()` — if unavailable, show "N/A".  
   Feed values into the mini sparkline charts with `PlotDataItem.setData()`.

2. **Load Model → Connect to Evaluation**  
   File: `ui/main_window.py` → `_on_load_model()`  
   After the file dialog returns a path, use `ALGORITHM_REGISTRY` to detect the algo from the filename or ask the user, then call `algo_class.load(path)` and store it so `_start_evaluation()` can use it the same way it uses `training_worker.trained_model`.

3. **Persist Last Session Config**  
   File: `main.py` or a new `core/config.py`  
   Use `QSettings` (wraps the OS registry on Windows, a plist on macOS, an INI on Linux) to save/restore the last selected env ID, algo name, hyperparams, seed, save dir, and theme mode. Call save on close (`closeEvent`) and restore on startup.

### Medium Priority

4. **Multi-Run Comparison**  
   Allow training the same environment with two different algorithms and overlay their reward curves on the same chart for side-by-side comparison.

5. **TensorBoard Integration**  
   Pass `tensorboard_log="tb_logs/"` to `model.learn()` (already supported by SB3). Add a "Open TensorBoard" button that launches `tensorboard --logdir tb_logs` in a subprocess.

6. **Custom Environment Builder**  
   A tab inside the config panel where the user can paste a custom Gymnasium `Env` subclass and register it at runtime with `gym.register(...)`.

### Low Priority / Nice To Have

7. **Export Charts**  
   Add a right-click context menu on each pyqtgraph chart to export as PNG/SVG.

8. **Training History Log**  
   A collapsible text area below the progress bar showing timestamped log lines (mirrors what SB3 prints to stdout).

9. **Seed Sweep**  
   Run the same config N times with different seeds and compute a mean ± std reward band.

---

## File Map (with current responsibility)

```
main.py                     Entry point. Creates QApplication, applies stylesheet.
requirements.txt            All Python deps.
STATE.md                    This file.
README.md                   Install + quick-start guide.

core/
  algorithms.py             ALGORITHM_REGISTRY dict + helper fns (get_environment_list,
                            get_compatible_algorithms, get_action_space_name, create_model)
  callbacks.py              DashboardCallback — throttled metric emission during training
  training_worker.py        QThread wrapper around model.learn(); emits metrics + saves model
  evaluation_worker.py      QThread wrapper around model.predict() loop; streams rgb frames

ui/
  theme.py                  Color tokens, set_theme(), get_current_mode(), get_stylesheet()
  main_window.py            3-column layout, signal wiring, _toggle_theme(), _apply_inline_styles()
  metrics_panel.py          Training + Evaluation tabs with live pyqtgraph charts
  hardware_panel.py         4-card hardware display (placeholder — no live data yet)
  environment_controls.py   Config form, hyperparameter widgets, action buttons, state machine
  environment_render.py     Frame viewer with HUD overlay for evaluation playback

saved_models/               Auto-created. SB3 saves here as <ALGO>_<ENV>.zip
```

---

## Key Technical Decisions (for context)

- **Episode metrics source**: `model.ep_info_buffer` (a `deque` populated by SB3's `Monitor` wrapper on every episode end) — NOT `logger.name_to_value` which only flushes at rollout boundaries and is empty during most steps.
- **Container stylesheet**: Each panel's outer container uses an **object-name CSS selector** (`#configContainer { }`) instead of `QWidget { }` to avoid the rule bleeding into child widgets (combos, spinboxes, etc.) and overriding the global app stylesheet.
- **Theme tokens**: Module-level globals in `theme.py` (e.g. `BG_PRIMARY = "#0d0f18"`) are re-assigned by `set_theme()` via `globals()`. Re-calling `get_stylesheet()` after `set_theme()` produces the correct colors because `get_stylesheet()` is a plain f-string function, not a cached string.
- **pyqtgraph color update**: On theme toggle, chart backgrounds are updated via `plot.setBackground(pg.mkColor(t.CHART_BG))` and axis pens via `axis.setPen(pg.mkPen(color=..., width=1))`. The `setBackground` call is the reliable method — setting it via QSS does not work with pyqtgraph.
