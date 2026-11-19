"""Render the reporting-policy comparison as an animation.

Run from the repository root:
    PYTHONPATH=src python experiments/make_animation.py

Truth, delivered reports and energy figures all come from ``iotlab.energy``.
The controller used here is ``ReferencePolicy`` (pure Python, identical to the
portable C policy) so no compiler is needed to regenerate the animation.

All power numbers are ILLUSTRATIVE PLACEHOLDERS, as stated in README.md.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from iotlab.energy import PowerProfile, Signal, simulate  # noqa: E402
from iotlab.policy import ReferencePolicy  # noqa: E402


def main() -> None:
    sig = Signal.make(days=2.0, seed=0)          # two simulated days
    prof = PowerProfile()
    adaptive = simulate(lambda: ReferencePolicy(deadband=50, min_gap=10,
                                                max_gap=600, period_min=10,
                                                period_max=120, adaptive=True),
                        prof, sig, 0, record=True)
    periodic = simulate("periodic:60", prof, sig, 0, record=True)

    hours = sig.t.astype(float) / 3600.0
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
    axes[0].plot(hours, sig.base / 100.0, color="#999", lw=1, label="diurnal baseline")
    axes[0].plot(hours, sig.value / 100.0, color="#333", lw=0.8, label="true temperature")
    axes[0].set_ylabel("deg C")
    axes[0].legend(fontsize=8, loc="upper left")

    lines, marks, titles = [], [], []
    for ax, res, label in ((axes[1], adaptive, "adaptive 10-120 s"),
                           (axes[1], periodic, "periodic 60 s")):
        (line,) = ax.plot([], [], lw=1.2, label=label)
        (mark,) = ax.plot([], [], "|", ms=4, alpha=0.4)
        lines.append(line); marks.append(mark)
    axes[1].set_xlabel("hours (2-day window)")
    axes[1].set_ylabel("gateway estimate (deg C)")
    axes[1].legend(fontsize=8, loc="lower left")
    title = fig.text(0.5, 0.985, "", ha="center", fontsize=10)

    def frame(h):
        end = min(len(sig.t), int(h * 3600))
        # The top axis shows the full synthetic signal as context; reports are revealed.
        for res, line, mark in ((adaptive, lines[0], marks[0]),
                                (periodic, lines[1], marks[1])):
            rt, rv = res["rx_t"], res["rx_v"]
            sel = rt <= end
            rt, rv = rt[sel], rv[sel]
            if len(rt):
                pos = np.searchsorted(sig.t, rt, side="right") - 1
                xt = hours[np.clip(pos, 0, len(hours) - 1)]
                line.set_data(xt, rv / 100.0)
                mark.set_data(xt, rv / 100.0)
            else:
                line.set_data([], []); mark.set_data([], [])
        title.set_text(f"t = {h:4.1f} h   adaptive life {adaptive['life_years']:.2f} y  |  "
                       f"periodic-60s life {periodic['life_years']:.2f} y  (placeholder profile)")
        return lines + marks

    out = os.path.join(ROOT, "figures", "demo_policy.gif")
    anim = FuncAnimation(fig, frame, frames=[i * 0.5 for i in range(48)], blit=False)
    anim.save(out, writer=PillowWriter(fps=10), dpi=80)
    plt.close(fig)
    print(f"wrote {out}")
    print(f"adaptive: {adaptive['life_years']:.2f} y, {adaptive['tx_attempts']/2:.0f} TX/day")
    print(f"periodic-60s: {periodic['life_years']:.2f} y, {periodic['tx_attempts']/2:.0f} TX/day")


if __name__ == "__main__":
    main()
