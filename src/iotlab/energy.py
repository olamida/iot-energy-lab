"""Energy / information-quality simulation of one battery node.

POWER NUMBERS ARE ILLUSTRATIVE PLACEHOLDERS, not any vendor's specification.
Replace them with values measured (e.g. with an energy profiler) or taken from
your target SoC's datasheet. The *structure* (sleep / wake / sample / TX / RX
window / retries) is what the study is about; the sensitivity analysis shows how
much the conclusions depend on the numbers.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np


@dataclass(frozen=True)
class PowerProfile:
    sleep_uA: float = 2.0            # deep-sleep current (EM2-like)
    wake_mA: float = 5.0             # MCU active while awake
    wake_ms: float = 2.0
    sample_mA: float = 1.0           # sensor + ADC
    sample_ms: float = 5.0
    tx_mA: float = 8.0               # radio transmit
    tx_ms: float = 3.0
    rx_mA: float = 8.0               # ack listen window
    rx_ms: float = 1.5
    battery_mAh: float = 225.0       # coin cell nominal
    usable_frac: float = 0.7         # derating for pulse load / cutoff
    link_success: float = 0.9        # per-attempt delivery probability
    max_retries: int = 3

    # charge per event in micro-coulombs (uA*s)
    def q_wake(self): return self.wake_mA * 1e3 * self.wake_ms * 1e-3
    def q_sample(self): return self.sample_mA * 1e3 * self.sample_ms * 1e-3
    def q_tx(self): return self.tx_mA * 1e3 * self.tx_ms * 1e-3 + self.rx_mA * 1e3 * self.rx_ms * 1e-3


@dataclass
class Signal:
    """Diurnal temperature (centi-degC) + sensor noise + door-open style events."""
    t: np.ndarray
    value: np.ndarray                # noise-free truth, centi-degC
    base: np.ndarray                 # diurnal baseline, centi-degC
    events: list                     # (t_start, amplitude_cC)

    @staticmethod
    def make(days: float, seed: int, events_per_day: float = 6.0) -> "Signal":
        rng = np.random.default_rng(seed)
        n = int(days * 86400)
        t = np.arange(n)
        base = 2000 + 300 * np.sin(2 * np.pi * t / 86400 + rng.uniform(0, 6.28))
        val = base.copy()
        events = []
        for _ in range(rng.poisson(events_per_day * days)):
            t0 = int(rng.integers(0, n - 3600))
            amp = float(rng.choice([-1, 1]) * rng.uniform(200, 500))
            events.append((t0, amp))
            tail = np.arange(n - t0)
            val[t0:] += amp * np.exp(-tail / 600.0)
        return Signal(t, val, base, events)


def simulate(policy_factory, prof: PowerProfile, sig: Signal, seed: int,
             noise_cC: float = 5.0, record: bool = False):
    """Run one policy over the signal. policy_factory() -> object with step(sample)->(tx, period),
    or the string 'periodic:<seconds>' for the always-transmit baseline."""
    rng = np.random.default_rng(seed + 12345)
    n = len(sig.t)
    q = 0.0
    rx_t, rx_v = [], []
    wakes = tx_attempts = tx_lost = 0
    periodic = isinstance(policy_factory, str)
    if periodic:
        period = int(policy_factory.split(":")[1])
        pol = None
    else:
        pol = policy_factory()
    t = 0
    while t < n:
        wakes += 1
        q += prof.q_wake() + prof.q_sample()
        sample = int(round(sig.value[t] + rng.normal(0, noise_cC)))
        if periodic:
            tx, nxt = True, period
        else:
            tx, nxt = pol.step(sample)
        if tx:
            delivered = False
            for _ in range(prof.max_retries + 1):
                tx_attempts += 1
                q += prof.q_tx()
                if rng.random() < prof.link_success:
                    delivered = True
                    break
            if delivered:
                rx_t.append(t)
                rx_v.append(sample)
            else:
                tx_lost += 1
        t += max(1, nxt)
    q += prof.sleep_uA * n                         # sleep floor (uA*s) over the whole run
    avg_uA = q / n
    life_years = prof.battery_mAh * 1e3 * prof.usable_frac / avg_uA / 8766.0
    # information quality at the gateway: forward-filled last received value
    if rx_t:
        idx = np.searchsorted(np.array(rx_t), sig.t, side="right") - 1
        gw = np.where(idx >= 0, np.array(rx_v)[np.clip(idx, 0, None)], np.nan)
        err = np.abs(gw - sig.value)
        mean_err = float(np.nanmean(err[idx >= 0]))
    else:
        mean_err = float("nan")
    # events: detected if a delivered report deviates >= 100 cC from baseline while event is active
    lat, missed = [], 0
    rxt, rxv = np.array(rx_t), np.array(rx_v)
    for t0, amp in sig.events:
        win_end = min(n - 1, t0 + 900)
        if len(rxt) == 0:
            missed += 1
            continue
        m = (rxt >= t0) & (rxt <= win_end) & (np.abs(rxv - sig.base[rxt.clip(0, n - 1)]) >= 100) if len(rxt) else None
        hit = np.where(m)[0]
        if len(hit) == 0:
            missed += 1
        else:
            lat.append(float(rxt[hit[0]] - t0))
    ne = max(1, len(sig.events))
    out = dict(avg_uA=avg_uA, life_years=life_years, wakes=wakes, tx_attempts=tx_attempts,
               reports_lost=tx_lost, mean_err_cC=mean_err,
               event_latency_s=float(np.mean(lat)) if lat else float("nan"),
               missed_event_frac=missed / ne, n_events=len(sig.events))
    if record:                      # used by experiments/make_animation.py only
        out["rx_t"] = np.asarray(rx_t, dtype=int)
        out["rx_v"] = np.asarray(rx_v)
    return out
