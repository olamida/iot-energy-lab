"""ctypes binding to the C report policy + an independent pure-Python reference."""
from __future__ import annotations
import ctypes as C, os, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(ROOT, "build", "libpolicy.so")


def build_library(force: bool = False) -> str:
    if os.path.exists(LIB) and not force:
        return LIB
    os.makedirs(os.path.dirname(LIB), exist_ok=True)
    src = os.path.join(ROOT, "c", "report_policy.c")
    for cc in ("gcc", "cc", "clang"):
        try:
            subprocess.run([cc, "-O2", "-Wall", "-shared", "-fPIC", src, "-o", LIB], check=True, capture_output=True)
            return LIB
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise RuntimeError("no C compiler")


class _Rp(C.Structure):
    _fields_ = [("deadband", C.c_int16), ("min_gap", C.c_uint16), ("max_gap", C.c_uint16),
                ("period_min", C.c_uint16), ("period_max", C.c_uint16), ("adaptive", C.c_uint8),
                ("ewma", C.c_int16), ("last_sent", C.c_int16), ("since_sent", C.c_uint16),
                ("period", C.c_uint16), ("primed", C.c_uint8)]


_lib = None


def _l():
    global _lib
    if _lib is None:
        _lib = C.CDLL(build_library())
        _lib.rp_init.argtypes = [C.POINTER(_Rp), C.c_int16, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint8]
        _lib.rp_step.argtypes = [C.POINTER(_Rp), C.c_int16]
        _lib.rp_step.restype = C.c_int
    return _lib


class Policy:
    """C implementation. step(sample) -> (transmit: bool, next_period_ticks)."""

    def __init__(self, deadband=50, min_gap=10, max_gap=600, period_min=10, period_max=120, adaptive=True):
        self.s = _Rp()
        _l().rp_init(C.byref(self.s), deadband, min_gap, max_gap, period_min, period_max, int(adaptive))

    def step(self, sample: int):
        tx = _l().rp_step(C.byref(self.s), int(sample))
        return bool(tx), int(self.s.period)


class ReferencePolicy:
    """Independent Python transcription of the same rules (used by the tests)."""

    def __init__(self, deadband=50, min_gap=10, max_gap=600, period_min=10, period_max=120, adaptive=True):
        self.db, self.mg, self.xg, self.pmin, self.pmax, self.ad = deadband, min_gap, max_gap, period_min, period_max, adaptive
        self.ewma = self.last = 0
        self.since = 0
        self.period = period_min
        self.primed = False

    def step(self, sample: int):
        self.since = min(65535, self.since + self.period)
        if not self.primed:
            self.ewma = self.last = sample
            self.since, self.primed, self.period = 0, True, self.pmin
            return True, self.period
        self.ewma = self.ewma + ((sample - self.ewma) >> 2)       # arithmetic shift, same as C
        adev = abs(self.ewma - self.last)
        send = self.since >= self.xg or (adev >= self.db and self.since >= self.mg)
        if send:
            self.last, self.since, adev = self.ewma, 0, 0
        if self.ad:
            self.period = self.pmin if adev >= (self.db >> 1) else min(self.pmax, self.period << 1)
        else:
            self.period = self.pmin
        return send, self.period
