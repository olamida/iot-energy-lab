import random
import pytest
from iotlab import Policy, PowerProfile, ReferencePolicy, Signal, simulate

CFGS = [dict(), dict(adaptive=False, period_min=10, period_max=10), dict(deadband=20, min_gap=5, max_gap=100, period_min=2, period_max=64)]


@pytest.mark.parametrize("cfg", CFGS)
def test_c_matches_python_reference_on_random_and_extreme_samples(cfg):
    rng = random.Random(7)
    c, p = Policy(**cfg), ReferencePolicy(**cfg)
    for i in range(20000):
        x = rng.choice([rng.randint(-32768, 32767), rng.randint(1900, 2100), -32768, 32767])
        assert c.step(x) == p.step(x), i


def test_heartbeat_fires_for_a_constant_signal():
    p = Policy(max_gap=600, period_min=10, period_max=120)
    t, last, gaps = 0, 0, []
    for _ in range(2000):
        tx, per = p.step(2000)
        if tx:
            gaps.append(t - last); last = t
        t += per
    assert max(gaps[1:]) <= 600 + 120 and len(gaps) > 3      # heartbeat late by at most one period


def test_never_transmits_faster_than_min_gap():
    p = Policy(min_gap=30, period_min=5, period_max=5, adaptive=False, deadband=10)
    rng = random.Random(1)
    t, last = 0, None
    for _ in range(3000):
        tx, per = p.step(rng.randint(0, 3000))
        if tx:
            if last is not None:
                assert t - last >= 30
            last = t
        t += per


def test_period_stays_in_bounds():
    p = Policy(period_min=10, period_max=120)
    rng = random.Random(3)
    for _ in range(5000):
        _, per = p.step(rng.randint(-32768, 32767))
        assert 10 <= per <= 120


def test_step_change_is_reported_quickly_by_adaptive_policy():
    p = Policy(deadband=50, period_min=10, period_max=120)
    t = 0
    for _ in range(100):
        p.step(2000); t += 1
    sent_at = None
    for k in range(60):
        tx, per = p.step(2500)
        if tx:
            sent_at = k
            break
    assert sent_at is not None and sent_at <= 8


def test_energy_model_sanity():
    sig = Signal.make(1, 0)
    prof = PowerProfile()
    a = simulate("periodic:10", prof, sig, 0)
    b = simulate("periodic:100", prof, sig, 0)
    assert a["avg_uA"] > b["avg_uA"] > prof.sleep_uA          # more wake-ups cost more; sleep is the floor
    assert b["life_years"] > a["life_years"]
    z = simulate("periodic:10", PowerProfile(link_success=0.0), sig, 0)
    assert z["reports_lost"] == z["wakes"]


def test_deterministic():
    sig = Signal.make(1, 2)
    assert simulate(lambda: Policy(), PowerProfile(), sig, 3) == simulate(lambda: Policy(), PowerProfile(), sig, 3)
