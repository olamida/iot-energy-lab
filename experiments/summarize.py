import csv, collections, math, os, statistics as st
R = os.path.join(os.path.dirname(__file__), "..", "results")
rows = list(csv.DictReader(open(f"{R}/iot.csv")))
def ms(v): 
    v = [x for x in v if x == x]
    return (st.mean(v), 1.96 * st.stdev(v) / math.sqrt(len(v))) if len(v) > 1 else (st.mean(v), 0)
out = ["| policy | battery life (years) | avg current (uA) | mean error at gateway (0.01 C) | event latency (s) | missed events | TX attempts / day |", "|---|---|---|---|---|---|---|"]
d = collections.defaultdict(list)
for r in rows:
    if r["exp"] == "policy": d[r["policy"]].append(r)
for k, v in d.items():
    g = lambda c: [float(x[c]) for x in v]
    days = float(v[0]["wakes"]) * 0 + 7
    out.append(f"| {k} | {ms(g('life_years'))[0]:.2f} ± {ms(g('life_years'))[1]:.2f} | {ms(g('avg_uA'))[0]:.2f} | {ms(g('mean_err_cC'))[0]:.1f} | {ms(g('event_latency_s'))[0]:.0f} | {100*st.mean(g('missed_event_frac')):.1f}% | {st.mean(g('tx_attempts'))/days:.0f} |")
out += ["", "Sensitivity of battery life (years) to each parameter varied -50%/+50% (link_success 0.7/0.98):", "", "| parameter | periodic-60s lo..hi | adaptive(10-120s) lo..hi |", "|---|---|---|"]
s = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    if r["exp"] == "sens": s[(r["policy"], r["param"])][r["value"].split(":")[0]].append(float(r["life_years"]))
params = sorted({p for _, p in s}, key=lambda p: -abs(st.mean(s[("periodic-60s", p)]["hi"]) - st.mean(s[("periodic-60s", p)]["lo"])))
for p in params:
    a, b = s[("periodic-60s", p)], s[("adaptive(10-120s)", p)]
    out.append(f"| {p} | {st.mean(a['lo']):.2f}..{st.mean(a['hi']):.2f} | {st.mean(b['lo']):.2f}..{st.mean(b['hi']):.2f} |")
open(f"{R}/summary.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
