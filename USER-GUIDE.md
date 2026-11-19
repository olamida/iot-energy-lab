# USER-GUIDE — iot-energy-lab

End-user manual. You do not need to edit code to follow this guide.

## 1. What you can do with it

Portable integer-C reporting policy driven by a Python energy simulator; simulation only, no hardware.

The research question is: *How much battery life does a smarter reporting policy buy, and what does it cost in data quality and responsiveness?*

## 2. Install

```bash
git clone https://github.com/olamida/iot-energy-lab.git
cd iot-energy-lab
pip install -r requirements.txt   # a C compiler (gcc) is required to build the policy
```

Python 3.10+ is assumed. On Windows use `.venv\Scripts\activate` instead of
`source .venv/bin/activate` if you create a virtual environment.

## 3. Watch the animation

Open `figures/demo_policy.gif` directly on GitHub or in any image viewer; GitHub plays
GIFs inline. The animation shows: Two-day window comparing adaptive and periodic reporting: true temperature, diurnal baseline and the reports actually delivered to the gateway.

To regenerate it from source:

```bash
python experiments/make_animation.py
```

## 4. Verify the installation

```bash
PYTHONPATH=src python -m pytest -q tests
```

A passing run prints a test summary with no failures. If a C compiler is
mentioned as missing, install a system C compiler (gcc on Linux, Xcode command
line tools on macOS, MinGW/MSVC on Windows) and rerun.

## 5. Run the full experiments

```bash
python experiments/run_experiments.py && python experiments/summarize.py && python experiments/make_figures.py && python experiments/measure_footprint.py
```

Outputs appear in `results/` (CSV/JSON/Markdown tables) and `figures/`
(PNG/GIF). Re-running with the shipped seeds should reproduce the shipped
numbers; small differences can occur with different library versions.

## 6. How to read the outputs

- Battery life: periodic-10s 2.40 y, periodic-60s 6.16 y, periodic-300s 8.23 y, change-trigger 5.01 y, adaptive(10–120 s) 8.08 y, adaptive(10–300 s) 8.44 y — `results/summary.md`.
- adaptive(10–120 s) has 2.6x lower event latency than periodic-300s (59 s vs 151 s) at similar mean error (10.8 vs 10.0 centi-deg) — `results/summary.md`.
- change-trigger sends about 8x fewer packets than periodic-60s yet lives shorter (5.01 vs 6.16 y) because it still wakes every 10 s — `results/summary.md`.
- Sensitivity: varying sleep current ±50% moves periodic-60s from 9.4 y to 4.6 y; radio current/time moves it by less than 1 y — `results/summary.md`.
- Footprint: 218 B Cortex-M33, 204 B Cortex-M0+, 392 B AVR, zero library calls — `results/footprint.csv`.

## 7. Known limitations (please read)

- All current/time numbers are illustrative placeholders, not any vendor's specification.
- No battery self-discharge, temperature, voltage droop or radio protocol details.
- One synthetic signal family; event detection defined as a delivered report >= 1 C from baseline within 15 min.
- Footprint is compile-only; no cycle counts. Confidence intervals exclude parameter uncertainty.

## 8. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `ModuleNotFoundError` | Running from the wrong directory or missing `PYTHONPATH=src` | Run from the repository root and use the exact command in section 4. |
| Build fails with "gcc not found" | No system C compiler | Install gcc/Xcode CLT/MinGW; the pure-Python reference is only for the animation. |
| Animation script cannot find sibling repo | `stc-corridors` not beside `stc-formal` | Clone both repositories side by side, or install `stc` into the environment. |
| Numbers differ from README | Different seeds or library versions | Use the command in section 5 and compare against `results/` in the repo. |

## 9. Getting help

Open an issue with the exact command, your OS/Python version and the last 20
lines of output. Please do not attach private or employer data.
