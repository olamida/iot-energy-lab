"""Cross-compile the policy (compile only, no hardware) and report size + helper calls."""
import csv, os, re, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "c", "report_policy.c")
T = {"Cortex-M33": ["--target=thumbv8m.main-none-eabi", "-mcpu=cortex-m33"],
     "Cortex-M0+ (no div hardware)": ["--target=thumbv6m-none-eabi", "-mcpu=cortex-m0plus"],
     "ATmega328P (8-bit AVR)": ["--target=avr", "-mmcu=atmega328p"]}
rows = []
with tempfile.TemporaryDirectory() as d:
    for n, fl in T.items():
        o = os.path.join(d, "p.o")
        try:
            subprocess.run(["clang", *fl, "-Os", "-ffreestanding", "-Wall", "-c", SRC, "-o", o], check=True, capture_output=True)
        except Exception as e:
            print("skip", n, e); continue
        size = subprocess.run(["llvm-size", o], capture_output=True, text=True).stdout.strip().splitlines()[-1].split()
        rel = subprocess.run(["llvm-objdump", "-r", o], capture_output=True, text=True).stdout
        h = re.findall(r"R_\w+\s+(__\w+)", rel)
        rows.append(dict(target=n, text_bytes=int(size[0]), data_bss_bytes=int(size[1]) + int(size[2]),
                         helper_call_sites=len(h), helpers=" ".join(sorted(set(h)))))
with open(os.path.join(ROOT, "results", "footprint.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
