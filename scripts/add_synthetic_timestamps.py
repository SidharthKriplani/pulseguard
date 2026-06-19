"""
G3 — Synthetic Timestamp Injection
PulseGuard · Adds timestamp columns to enable FeatureLeakageLens temporal checks

Home Credit Default Risk has NO feature-level timestamps natively.
This script adds them synthetically to demonstrate the FAIL path for FLL Checks 6 and 7.

Three columns added (all SYNTHETIC):
  APPLICATION_DATE                    — when the application was received (outcome time)
  FEATURE_TIMESTAMP_EXT_SOURCE_2      — same as APPLICATION_DATE (clean; PASS path)
  FEATURE_TIMESTAMP_INJECTED_LEAK     — APPLICATION_DATE + 1–30 days (future; FAIL path)

One injected leakage feature added (SYNTHETIC):
  EXTERNAL_BUREAU_QUERY_RESULT__INJECTED
      — simulates a post-application credit bureau query result
      — NOT available at application time (future-timestamped)
      — a feature that would exist in reality but cannot be used: bureau was queried after
        the application date, so using it for training creates temporal leakage.

Run standalone:  python3 scripts/add_synthetic_timestamps.py --in data/synthetic_home_credit_like.csv
Or import:       from scripts.add_synthetic_timestamps import add_timestamps
"""

import argparse
import os
import numpy as np
import pandas as pd


REFERENCE_DATE = pd.Timestamp("2024-01-01")


def add_timestamps(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Add synthetic timestamp columns to df.

    All added columns are SYNTHETIC — not from real data.
    Returns a new DataFrame with additional columns.
    """
    rng = np.random.default_rng(seed)
    n = len(df)
    df = df.copy()

    # APPLICATION_DATE — outcome/reference time
    # Spread across 2024; each applicant has a unique application date
    APPLICATION_DATE = REFERENCE_DATE + pd.to_timedelta(
        rng.integers(0, 365, n), unit="D"
    )
    df["APPLICATION_DATE"] = APPLICATION_DATE                                   # SYNTHETIC

    # FEATURE_TIMESTAMP_EXT_SOURCE_2 — available at application time (PASS path)
    # EXT_SOURCE_2 is a bureau score pulled on the same day as the application.
    df["FEATURE_TIMESTAMP_EXT_SOURCE_2"] = APPLICATION_DATE                    # SYNTHETIC; == APPLICATION_DATE → PASS

    # INJECTED LEAKAGE FEATURE — post-application bureau query result
    # This feature was NOT available when the application was submitted.
    # In a real system, this could happen if someone accidentally used data from
    # a follow-up bureau pull done after the decision was made.
    leak_days = rng.integers(1, 31, n)                                         # 1–30 days after application
    FEATURE_TIMESTAMP_INJECTED_LEAK = APPLICATION_DATE + pd.to_timedelta(
        leak_days, unit="D"
    )
    df["FEATURE_TIMESTAMP_INJECTED_LEAK"] = FEATURE_TIMESTAMP_INJECTED_LEAK   # SYNTHETIC; > APPLICATION_DATE → FAIL

    # The injected feature itself — plausible credit score from a future bureau query
    # Value is random (not predictive) because in a real system the feature being
    # future-timestamped is the problem, not the value itself.
    df["EXTERNAL_BUREAU_QUERY_RESULT__INJECTED"] = rng.beta(2, 4, n).astype(  # SYNTHETIC feature; future-dated
        np.float32
    )

    print("[add_synthetic_timestamps] Columns added:")
    print("  APPLICATION_DATE                        (SYNTHETIC — outcome reference time)")
    print("  FEATURE_TIMESTAMP_EXT_SOURCE_2          (SYNTHETIC — == APPLICATION_DATE → PASS)")
    print("  FEATURE_TIMESTAMP_INJECTED_LEAK         (SYNTHETIC — > APPLICATION_DATE → FAIL)")
    print("  EXTERNAL_BUREAU_QUERY_RESULT__INJECTED  (SYNTHETIC — injected leakage feature)")
    print(f"  Mean leak offset: {leak_days.mean():.1f} days after application date")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path",
                        default="data/synthetic_home_credit_like.csv")
    parser.add_argument("--out", dest="out_path",
                        default="data/synthetic_home_credit_like_with_timestamps.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.in_path)
    df_out = add_timestamps(df, seed=args.seed)
    os.makedirs(os.path.dirname(args.out_path), exist_ok=True)
    df_out.to_csv(args.out_path, index=False)
    print(f"[add_synthetic_timestamps] Saved → {args.out_path}")
