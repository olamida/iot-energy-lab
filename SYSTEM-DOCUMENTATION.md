# SYSTEM-DOCUMENTATION — iot-energy-lab

Deep technical / developer documentation. For running instructions see
`USER-GUIDE.md`; for the work ledger see `PENDING-TASKS.md`.

## 1. Purpose and scope

Portable integer-C reporting policy driven by a Python energy simulator; simulation only, no hardware.

Research question: **How much battery life does a smarter reporting policy buy, and what does it cost in data quality and responsiveness?**

This is a simulation study. No hardware measurements, external datasets or
proprietary data are involved. The repository is intentionally small enough to
be read end-to-end by a reviewer in one sitting.

## 2. Architecture

| Component | Responsibility |
|---|---|
| `c/report_policy.{h,c}` | Portable integer decision logic; no division, no heap. |
| `src/iotlab/policy.py` | ctypes binding plus ReferencePolicy with identical behaviour. |
| `src/iotlab/energy.py` | PowerProfile, synthetic Signal and charge-based simulate(). |
| `experiments/run_experiments.py` | Policy comparison and sensitivity sweeps. |
| `experiments/measure_footprint.py` | clang -Os target footprint measurement. |

Dependencies flow one way: configuration/scenario → model/algorithm →
experiment runner → results → figures/animation. The simulator does not read
its own results; results are an output only.

## 3. Data flow

1. A seeded scenario, task set, signal or topology is constructed.
2. The core model advances in discrete steps (ticks or control steps).
3. Metrics are accumulated independently of the decision logic where possible
   (for example, a ground-truth collision checker rather than the agents' beliefs).
4. `experiments/` writes machine-readable results under `results/`.
5. `make_figures.py` and `make_animation.py` read those results or re-run the
   seeded simulator to produce visual artefacts.

## 4. Algorithms / numerical methods

See `README.md` for the high-level description and, where present,
`docs/DESIGN.md` or `DEVELOPMENT_GUIDE.md` for the full derivation. The
implementation is the authoritative reference: start at the module table in
section 2 and follow the entry point used by `PYTHONPATH=src python -m pytest -q tests`.

Reproducibility rules:
- Every stochastic component is driven by an explicit seed.
- Experiment parameters are recorded in the result rows.
- A change to a result number requires regenerating the CSV/JSON, not editing prose.

## 5. Results and evidence

- Battery life: periodic-10s 2.40 y, periodic-60s 6.16 y, periodic-300s 8.23 y, change-trigger 5.01 y, adaptive(10–120 s) 8.08 y, adaptive(10–300 s) 8.44 y — `results/summary.md`.
- adaptive(10–120 s) has 2.6x lower event latency than periodic-300s (59 s vs 151 s) at similar mean error (10.8 vs 10.0 centi-deg) — `results/summary.md`.
- change-trigger sends about 8x fewer packets than periodic-60s yet lives shorter (5.01 vs 6.16 y) because it still wakes every 10 s — `results/summary.md`.
- Sensitivity: varying sleep current ±50% moves periodic-60s from 9.4 y to 4.6 y; radio current/time moves it by less than 1 y — `results/summary.md`.
- Footprint: 218 B Cortex-M33, 204 B Cortex-M0+, 392 B AVR, zero library calls — `results/footprint.csv`.

## 6. Animation pipeline

`python experiments/make_animation.py` renders `figures/demo_policy.gif`. It uses the project's own simulator
(or an explicitly documented pure-Python reference of the same controller) and
Matplotlib's Pillow writer. Frames are subsampled to keep the GIF small; the
underlying trajectory is not resampled or smoothed. Two-day window comparing adaptive and periodic reporting: true temperature, diurnal baseline and the reports actually delivered to the gateway.

## 7. Build, test and CI

```bash
pip install -r requirements.txt   # a C compiler (gcc) is required to build the policy
PYTHONPATH=src python -m pytest -q tests
python experiments/run_experiments.py && python experiments/summarize.py && python experiments/make_figures.py && python experiments/measure_footprint.py
python experiments/make_animation.py
```

CI (`.github/workflows/ci.yml`) runs on push and pull request. Jobs install the
documented dependencies, set `PYTHONPATH=src` where required, and run the test
suite. Repositories that call C code install a system compiler in CI; footprint
measurement with cross-compilers is deliberately optional.

## 8. Extension points

- Add a new scenario/policy by extending the corresponding factory or registry
  and a seeded test, then re-run the full experiment suite.
- Add a new metric by writing it into the result row and updating
  `experiments/summarize.py` and the README table together.
- Add a new animation by recording the relevant simulator state (prefer an
  optional `record` flag over duplicating the stepping logic) and saving via
  `FuncAnimation`/`PillowWriter` in `experiments/`.

## 9. Known limitations

- All current/time numbers are illustrative placeholders, not any vendor's specification.
- No battery self-discharge, temperature, voltage droop or radio protocol details.
- One synthetic signal family; event detection defined as a delivered report >= 1 C from baseline within 15 min.
- Footprint is compile-only; no cycle counts. Confidence intervals exclude parameter uncertainty.

## 10. Relation to the rest of the portfolio

Same embedded/resource-constrained thread as `embedded-autonomy-sim`; network side is studied in `mesh-routing-sim`.

## 11. Release metadata

`CITATION.cff` carries title, author (Yusuf Ndanusa Yahaya), version 0.1.0,
release date, repository URL and MIT license. No DOI or ORCID is claimed.
