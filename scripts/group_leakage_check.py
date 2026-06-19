"""
G3 — Group Leakage Check (PulseGuard-specific)
PulseGuard · Entity Contamination Check for SK_ID_CURR

FeatureLeakageLens does not check for entity (group) contamination across folds.
This script fills that gap.

What it checks:
  If the same SK_ID_CURR (applicant ID) appears in BOTH the train and validation/test
  sets, the model can memorize applicant-level information during training and appear
  to generalize when it is actually overfitting to known entities.

  In Home Credit, SK_ID_CURR is unique per row (one row per applicant).
  In the synthetic dataset, the same is true — SK_ID_CURR is assigned uniquely.
  Therefore, a random stratified 60/20/20 split produces NO entity contamination.

Two checks run:
  1. CLEAN SPLIT CHECK — stratified 60/20/20 split on unique SK_ID_CURR rows → PASS
  2. CONTAMINATED SPLIT CHECK — artificially duplicates 500 applicants into both
     train and val to demonstrate the FAIL path
     (labeled INJECTED_CONTAMINATION; not used for any other purpose)

Output: outputs/evidence/group_leakage_report.json

Run: python3 scripts/group_leakage_check.py
"""

import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.generate_synthetic_data import generate, DATASET_LABEL

TARGET_COL = "TARGET"
ID_COL     = "SK_ID_CURR"
SEED       = 42
N_ROWS     = 50_000
OUTPUT_DIR = "outputs/evidence"


def check_entity_contamination(
    df_train: pd.DataFrame,
    df_val:   pd.DataFrame,
    split_name: str = "clean",
) -> dict:
    """
    Check whether any SK_ID_CURR appears in both df_train and df_val.
    Returns a result dict with PASS/FAIL status and contamination details.
    """
    train_ids = set(df_train[ID_COL].unique())
    val_ids   = set(df_val[ID_COL].unique())
    overlap   = train_ids & val_ids
    contaminated = len(overlap) > 0

    result = {
        "split_name":             split_name,
        "n_train":                len(df_train),
        "n_val":                  len(df_val),
        "unique_ids_train":       len(train_ids),
        "unique_ids_val":         len(val_ids),
        "overlapping_ids":        len(overlap),
        "contaminated":           contaminated,
        "status":                 "FAIL" if contaminated else "PASS",
        "severity":               "HIGH" if contaminated else "NONE",
        "contamination_rate_pct": round(100 * len(overlap) / len(val_ids), 3) if val_ids else 0.0,
        "example_contaminated_ids": sorted(overlap)[:10],
        "detail": (
            f"{len(overlap)} applicant ID(s) appear in both train and val sets "
            f"({round(100*len(overlap)/len(val_ids),1)}% of val IDs contaminated). "
            f"Model can memorize entity-level patterns → inflated validation metrics."
            if contaminated else
            f"No SK_ID_CURR overlap between train and val. Entity contamination: none."
        ),
        "recommendation": (
            "Use GroupShuffleSplit or GroupKFold with groups=SK_ID_CURR to ensure "
            "entity-level isolation across folds. Drop duplicate applicants before splitting."
            if contaminated else
            "No action required. Entity isolation confirmed."
        ),
    }
    return result


def run_clean_split(df: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Run check on a proper stratified 60/20/20 split (expected: PASS)."""
    y   = df[TARGET_COL].to_numpy()
    idx = df.index.to_numpy()

    idx_tr, idx_val = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val, _      = train_test_split(idx_val, test_size=0.50,
                                        stratify=y[idx_val], random_state=SEED)

    df_train = df.loc[idx_tr]
    df_val   = df.loc[idx_val]

    result = check_entity_contamination(df_train, df_val, split_name="clean_split")
    return result, df_train, df_val


def run_contaminated_split(df: pd.DataFrame) -> dict:
    """
    Inject contamination: copy 500 training rows into val set with same SK_ID_CURR.
    This demonstrates the FAIL path.
    Label: INJECTED_CONTAMINATION — not used for any real training purpose.
    """
    y   = df[TARGET_COL].to_numpy()
    idx = df.index.to_numpy()

    idx_tr, idx_val = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val, _      = train_test_split(idx_val, test_size=0.50,
                                        stratify=y[idx_val], random_state=SEED)

    df_train = df.loc[idx_tr]
    df_val   = df.loc[idx_val]

    # Inject 500 training applicants into val (same SK_ID_CURR — entity contamination)
    rng         = np.random.default_rng(SEED + 1)
    contaminate = df_train.sample(500, random_state=SEED + 1)
    df_val_contaminated = pd.concat([df_val, contaminate], ignore_index=True)

    result = check_entity_contamination(
        df_train, df_val_contaminated, split_name="contaminated_split__INJECTED"
    )
    result["injected_contamination"] = True
    result["injected_contamination_n"] = 500
    result["injected_contamination_note"] = (
        "500 training applicants deliberately duplicated into val to demonstrate FAIL path. "
        "INJECTED for testing only — not used for any modeling purpose."
    )
    return result


def main():
    run_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    print("\n[group_leakage_check] Generating synthetic dataset…")
    df = generate(n=N_ROWS, seed=SEED)

    print("[group_leakage_check] Checking SK_ID_CURR uniqueness in full dataset…")
    n_unique_ids   = df[ID_COL].nunique()
    id_unique      = n_unique_ids == len(df)
    id_check = {
        "check": "SK_ID_CURR uniqueness",
        "n_rows": len(df),
        "n_unique_ids": n_unique_ids,
        "all_unique": id_unique,
        "status": "PASS" if id_unique else "WARN",
        "detail": (
            f"All {n_unique_ids:,} SK_ID_CURR values are unique (one row per applicant)."
            if id_unique else
            f"SK_ID_CURR has duplicates: {len(df) - n_unique_ids:,} duplicate rows."
        ),
    }
    print(f"  SK_ID_CURR unique: {id_unique} → {id_check['status']}")

    print("[group_leakage_check] Check 1: Clean split (expected PASS)…")
    clean_result, _, _ = run_clean_split(df)
    print(f"  Clean split: {clean_result['status']} | overlap={clean_result['overlapping_ids']}")

    print("[group_leakage_check] Check 2: Contaminated split (expected FAIL — INJECTED)…")
    contaminated_result = run_contaminated_split(df)
    print(f"  Contaminated split: {contaminated_result['status']} | "
          f"overlap={contaminated_result['overlapping_ids']} "
          f"({contaminated_result['contamination_rate_pct']}% of val IDs)")

    # ── Assemble output ───────────────────────────────────────────────────
    overall_status = "PASS" if clean_result["status"] == "PASS" else "FAIL"

    output = {
        "pulseguard_gate":    "G3",
        "check_name":         "group_leakage_check",
        "run_timestamp":      run_ts,
        "dataset_label":      DATASET_LABEL,
        "n_rows":             len(df),
        "overall_status":     overall_status,
        "fll_gap_note": (
            "FeatureLeakageLens does not include an entity contamination check. "
            "This script fills that gap as a PulseGuard-specific extension."
        ),
        "id_column":          ID_COL,
        "id_uniqueness_check": id_check,
        "clean_split_check":  clean_result,
        "contaminated_split_check__INJECTED": contaminated_result,
        "summary": {
            "clean_split_status":        clean_result["status"],
            "contaminated_split_status": contaminated_result["status"],
            "action_required":           overall_status == "FAIL",
            "recommendation": (
                "No action required. Use stratified split with unique SK_ID_CURR. "
                "If future data contains multiple rows per applicant, switch to "
                "GroupShuffleSplit(groups=SK_ID_CURR) to maintain entity isolation."
            ),
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "group_leakage_report.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print("  G3 GROUP LEAKAGE CHECK REPORT")
    print("=" * 60)
    print(f"  Overall status:  {overall_status}")
    print(f"  SK_ID_CURR:      {id_check['status']} — {id_check['detail']}")
    print(f"  Clean split:     {clean_result['status']} — {clean_result['detail']}")
    print(f"  Contaminated:    {contaminated_result['status']} (INJECTED) — "
          f"{contaminated_result['injected_contamination_n']} IDs duplicated")
    print(f"\n  Output: {out_path}")


if __name__ == "__main__":
    main()
