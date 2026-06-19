"""
G4 — Synthetic Lifecycle Seed Generator
PulseGuard · 30-Day Serving Batch Simulation

Generates 30 daily serving batches simulating a 30-day post-deployment monitoring window.
Drift is injected into EXT_SOURCE_2 on Day 7 (WARN-level) and Day 14 (ALERT-level).

Drift injection (SYNTHETIC — clearly labeled):
  Days 1–6:    No drift.  EXT_SOURCE_2 unmodified.  PSI ≈ 0.00–0.01 (OK)
  Days 7–13:   WARN-level drift. EXT_SOURCE_2 shifted −0.07.  PSI ≈ 0.10–0.16 (WARN)
  Days 14–30:  ALERT-level drift. EXT_SOURCE_2 shifted −0.12.  PSI ≈ 0.25–0.33 (ALERT)

Drift simulates an adversarial credit population shift: applicants with lower bureau scores
becoming more prevalent in the serving population — the type of shift that would indicate
model reliability may be degrading.

All batches are labeled:
  - data_type: "synthetic_home_credit_like"
  - drift_injected: True/False
  - drift_magnitude: float
  - drift_feature: "EXT_SOURCE_2"

Run: python3 scripts/seed_lifecycle.py  (saves batches to data/lifecycle/)
Import: from scripts.seed_lifecycle import generate_batches
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.generate_synthetic_data import generate, DATASET_LABEL

# ── Configuration ──────────────────────────────────────────────────────────────
N_DAYS          = 30
BATCH_SIZE      = 2_000
SEED_BASE       = 1_000          # day d uses seed SEED_BASE + d
DATA_DIR        = "data/lifecycle"
DRIFT_FEATURE   = "EXT_SOURCE_2"

# Drift schedule (SYNTHETIC — injected for monitoring demonstration)
WARN_START_DAY  = 7
ALERT_START_DAY = 14
WARN_SHIFT      = -0.07   # → PSI ≈ 0.11–0.16 (WARN band 0.10–0.20)
ALERT_SHIFT     = -0.12   # → PSI ≈ 0.25–0.33 (ALERT band > 0.20)


def get_drift_shift(day: int) -> float:
    """Return the EXT_SOURCE_2 additive shift for a given day."""
    if day >= ALERT_START_DAY:
        return ALERT_SHIFT
    elif day >= WARN_START_DAY:
        return WARN_SHIFT
    return 0.0


def generate_batch(day: int) -> pd.DataFrame:
    """
    Generate one day's serving batch.
    - Same DGP as training (calibrated intercept -4.20703)
    - Drift injected via additive shift on EXT_SOURCE_2
    - Labeled with batch metadata
    """
    seed = SEED_BASE + day
    df = generate(n=BATCH_SIZE, seed=seed)

    shift = get_drift_shift(day)
    drift_injected = shift != 0.0

    if drift_injected:
        df[DRIFT_FEATURE] = np.clip(df[DRIFT_FEATURE] + shift, 0.0, 1.0)

    # Batch metadata (not model features — informational only)
    df["BATCH_DAY"]             = day
    df["BATCH_SEED"]            = seed
    df["DATA_TYPE"]             = "synthetic_home_credit_like"
    df["DRIFT_INJECTED"]        = drift_injected
    df["DRIFT_FEATURE"]         = DRIFT_FEATURE if drift_injected else "none"
    df["DRIFT_SHIFT_MAGNITUDE"] = shift
    df["DRIFT_REGIME"]          = (
        "ALERT_INJECTED" if day >= ALERT_START_DAY
        else "WARN_INJECTED" if day >= WARN_START_DAY
        else "BASELINE"
    )

    return df


def generate_batches(n_days: int = N_DAYS) -> dict[int, pd.DataFrame]:
    """
    Generate all daily batches. Returns dict {day: DataFrame}.
    Suppress verbose output from generate() by redirecting stdout.
    """
    import io, contextlib
    batches = {}
    for day in range(1, n_days + 1):
        with contextlib.redirect_stdout(io.StringIO()):
            df = generate_batch(day)
        batches[day] = df
    return batches


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[seed_lifecycle] Generating {N_DAYS} daily batches (batch_size={BATCH_SIZE})…")
    print(f"  Drift schedule:")
    print(f"    Days 1–{WARN_START_DAY-1}: baseline (no drift)")
    print(f"    Days {WARN_START_DAY}–{ALERT_START_DAY-1}: WARN drift (EXT_SOURCE_2 shift={WARN_SHIFT:+.2f})")
    print(f"    Days {ALERT_START_DAY}–{N_DAYS}: ALERT drift (EXT_SOURCE_2 shift={ALERT_SHIFT:+.2f})")
    print()

    import io, contextlib
    for day in range(1, N_DAYS + 1):
        with contextlib.redirect_stdout(io.StringIO()):
            df = generate_batch(day)
        path = os.path.join(DATA_DIR, f"day_{day:02d}.parquet")
        df.to_parquet(path, index=False)
        regime = df["DRIFT_REGIME"].iloc[0]
        shift  = df["DRIFT_SHIFT_MAGNITUDE"].iloc[0]
        dr     = df["TARGET"].mean()
        print(f"  Day {day:2d}  regime={regime:<20s}  shift={shift:+.2f}  "
              f"default_rate={dr:.3f}  → {path}")

    print(f"\n[seed_lifecycle] Done. {N_DAYS} batches saved to {DATA_DIR}/")


if __name__ == "__main__":
    main()
