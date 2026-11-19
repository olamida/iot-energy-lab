# APP-GUIDE — iot-energy-lab

**Question:** How much battery life does a smarter reporting policy buy, and what does it cost in data quality and responsiveness?

**One-line summary:** Portable integer-C reporting policy driven by a Python energy simulator; simulation only, no hardware.

This guide records what the application/project has already done and what is still
to be done. It is the session-to-session entry point: read this first, then
`USER-GUIDE.md` to run it, `SYSTEM-DOCUMENTATION.md` to change it, and
`PENDING-TASKS.md` for the live work ledger.

## Work already executed

- Implemented `c/report_policy.c`, an integer policy with deadband, min/max gap, heartbeat and adaptive wake-up; compiled for host and cross-compiled for three targets.
- Bound the C policy to Python with ctypes and added an independent pure-Python reference implementation.
- Built a synthetic temperature signal (diurnal swing, noise, door-open events) and a charge-based energy model with up to 3 TX retries.
- Compared periodic (10/60/300 s), change-trigger and adaptive (10–120 s, 10–300 s) policies over 7 days x 30 seeds.
- Ran a parameter sensitivity analysis and measured footprint: 218 B on Cortex-M33 with zero helper calls.
- Wrote 9 tests (C/Python agreement, heartbeat, min gap, step response, deterministic runs) and CI with gcc.
- Rendered `figures/demo_policy.gif` from two recorded simulations (adaptive vs periodic-60s).

## Work to be executed (next)

- Replace every illustrative power number with datasheet or energy-profiler measurements, citing document and page.
- Port `rp_step()` into a vendor SDK sleeptimer/event-driven example and measure on a dev kit.
- Add battery self-discharge, temperature, voltage droop and real radio duty-cycle/protocol effects.
- Test more signal families and event-detection definitions.

## High-level flow

1. Configure a seeded scenario / task set / signal.
2. Run the simulator or experiment script in this repository.
3. Metrics are written to `results/`; figures to `figures/`.
4. The animation in `figures/demo_policy.gif` is rendered from the same simulator state.

## Commands at a glance

| Purpose | Command |
|---|---|
| Install | `pip install -r requirements.txt   # a C compiler (gcc) is required to build the policy` |
| Verify | `PYTHONPATH=src python -m pytest -q tests` |
| Experiments | `python experiments/run_experiments.py && python experiments/summarize.py && python experiments/make_figures.py && python experiments/measure_footprint.py` |
| Animation | `python experiments/make_animation.py` |

## Where this connects

Same embedded/resource-constrained thread as `embedded-autonomy-sim`; network side is studied in `mesh-routing-sim`.

## Honesty notes

All numbers quoted in this repository come from files under `results/`.
Simulation-only results are not hardware measurements, and the documented
limitations in `README.md` are part of the deliverable.
