import csv, collections, os, statistics as st
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = os.path.dirname(__file__); rows = list(csv.DictReader(open(f"{H}/../results/iot.csv")))
d = collections.defaultdict(list)
for r in rows:
    if r["exp"] == "policy": d[r["policy"]].append(r)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for k, v in d.items():
    x = st.mean(float(r["event_latency_s"]) for r in v); y = st.mean(float(r["life_years"]) for r in v)
    ax[0].scatter(x, y, s=60, color="#c0392b" if k.startswith("adaptive") else "#2a6f97")
    ax[0].annotate(k, (x, y), textcoords="offset points", xytext=(5, 4), fontsize=7)
ax[0].set_xscale("log"); ax[0].set_xlabel("mean event-detection latency (s, log)"); ax[0].set_ylabel("battery life (years)")
ax[0].set_title("Lifetime vs responsiveness (illustrative power profile)")
s = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    if r["exp"] == "sens" and r["policy"] == "periodic-60s": s[r["param"]][r["value"].split(":")[0]].append(float(r["life_years"]))
ps = sorted(s, key=lambda p: abs(st.mean(s[p]["hi"]) - st.mean(s[p]["lo"])))
base = st.mean(float(r["life_years"]) for r in d["periodic-60s"])
for i, p in enumerate(ps):
    lo, hi = st.mean(s[p]["lo"]), st.mean(s[p]["hi"])
    ax[1].barh(i, hi - base, left=base, color="#e67e73", height=.6); ax[1].barh(i, lo - base, left=base, color="#61a5c2", height=.6)
ax[1].set_yticks(range(len(ps))); ax[1].set_yticklabels(ps, fontsize=8); ax[1].axvline(base, color="k", lw=1)
ax[1].set_xlabel("battery life (years), periodic-60s"); ax[1].set_title("Sensitivity: each parameter -50% (blue) / +50% (red)")
plt.tight_layout(); os.makedirs(f"{H}/../figures", exist_ok=True); plt.savefig(f"{H}/../figures/fig_iot.png", dpi=160)
