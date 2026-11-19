"""Policy comparison, link-quality sweep, sensitivity (tornado). 30 seeds x 7 days."""
import csv, os, sys
from dataclasses import replace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from iotlab import Policy, PowerProfile, Signal, simulate
OUT = os.path.join(os.path.dirname(__file__), "..", "results"); os.makedirs(OUT, exist_ok=True)
QUICK = "--quick" in sys.argv
SEEDS, DAYS = (3, 2) if QUICK else (30, 7)
POL = {
    "periodic-10s": "periodic:10", "periodic-60s": "periodic:60", "periodic-300s": "periodic:300",
    "change-trigger(10s)": lambda: Policy(period_min=10, period_max=10, adaptive=False),
    "adaptive(10-120s)": lambda: Policy(period_min=10, period_max=120, adaptive=True),
    "adaptive(10-300s)": lambda: Policy(period_min=10, period_max=300, adaptive=True),
}
sigs = [Signal.make(DAYS, s) for s in range(SEEDS)]
rows = []
for name, f in POL.items():
    for s, sig in enumerate(sigs):
        r = simulate(f, PowerProfile(), sig, s); rows.append(dict(exp="policy", policy=name, param="", value="", seed=s, **r))
    print(name, flush=True)
# link quality sweep (adaptive vs periodic-60)
for ls in (0.5, 0.7, 0.9, 0.99):
    for name in ("periodic-60s", "adaptive(10-120s)"):
        for s, sig in enumerate(sigs[: max(3, SEEDS // 3)]):
            r = simulate(POL[name], replace(PowerProfile(), link_success=ls), sig, s)
            rows.append(dict(exp="link", policy=name, param="link_success", value=ls, seed=s, **r))
# sensitivity: +-50 % of each power parameter (link: 0.7 / 0.98), battery life only
base = PowerProfile()
params = ["sleep_uA", "wake_mA", "wake_ms", "sample_mA", "sample_ms", "tx_mA", "tx_ms", "rx_mA", "rx_ms", "usable_frac", "link_success"]
for name in ("periodic-60s", "adaptive(10-120s)"):
    for p in params:
        lo, hi = ((0.7, 0.98) if p == "link_success" else (getattr(base, p) * 0.5, min(getattr(base, p) * 1.5, 1.0) if p == "usable_frac" else getattr(base, p) * 1.5))
        for tag, v in (("lo", lo), ("hi", hi)):
            for s, sig in enumerate(sigs[: max(3, SEEDS // 3)]):
                r = simulate(POL[name], replace(base, **{p: v}), sig, s)
                rows.append(dict(exp="sens", policy=name, param=p, value=f"{tag}:{v}", seed=s, **r))
    print("sens", name, flush=True)
dest = f"{OUT}/{'quick' if QUICK else 'iot'}.csv"
with open(dest, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote", dest, len(rows))
