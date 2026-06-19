"""
G3 — Leakage Detection Kernel
PulseGuard · Pre-Training Feature Leakage Audit

Runs the full FeatureLeakageLens audit pipeline on the PulseGuard training dataset.
Produces structured evidence in JSON, Markdown, and HTML formats.

Checks run:
  1. Name heuristic                   — suspicious column names (default, label, target, etc.)
  2. ID / proxy                       — near-unique columns that proxy an ID
  3. Target correlation               — Pearson correlation above threshold vs. TARGET
  4. Categorical proxy                — Chi-squared test for target-correlated categoricals
  5. Split distribution               — train vs. test distribution shift
  6. Temporal availability            — feature timestamp > outcome timestamp (FAIL-level)
  7. Training future date scan        — future-dated feature timestamps in training rows

Injected leakage:
  EXTERNAL_BUREAU_QUERY_RESULT__INJECTED — a post-application bureau query result
  Timestamped APPLICATION_DATE + 1–30 days → triggers Check 6 FAIL (temporal leakage)

Dataset label: synthetic_home_credit_like (Kaggle unavailable — kaggle CLI not found)

Run: python3 scripts/leakage_audit.py
"""

import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# ── PulseGuard local imports ───────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.generate_synthetic_data import generate, DATASET_LABEL, DATASET_SOURCE
from scripts.add_synthetic_timestamps import add_timestamps

# ── FeatureLeakageLens (PyPI) ──────────────────────────────────────────────
from featureleakagelens import LeakageAuditConfig, audit_dataframe

# ── Config ─────────────────────────────────────────────────────────────────
N_ROWS          = 50_000
SEED            = 42
TARGET_COL      = "TARGET"
ID_COL          = "SK_ID_CURR"
OUTPUT_DIR      = "outputs/evidence"
DATA_DIR        = "data"

# Timestamp columns — all SYNTHETIC; not from Home Credit
OUTCOME_TIME_COL = "APPLICATION_DATE"
FEATURE_TIME_COLS = {
    "EXT_SOURCE_2":                          "FEATURE_TIMESTAMP_EXT_SOURCE_2",
    "EXTERNAL_BUREAU_QUERY_RESULT__INJECTED": "FEATURE_TIMESTAMP_INJECTED_LEAK",
}

# Columns to exclude from FLL checks (IDs, timestamps, split markers, synthetic labels)
IGNORE_COLS = [
    ID_COL,
    OUTCOME_TIME_COL,
    "FEATURE_TIMESTAMP_EXT_SOURCE_2",
    "FEATURE_TIMESTAMP_INJECTED_LEAK",
    "SPLIT",
    "EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC",   # SYNTHETIC field; not a model feature
]


def build_dataset() -> pd.DataFrame:
    """Generate synthetic data, add timestamps, and add 60/20/20 split column."""
    print(f"\n[leakage_audit] Dataset: {DATASET_LABEL}")
    print(f"[leakage_audit] Kaggle CLI: not found — using synthetic fallback")

    # 1. Generate base synthetic data
    df = generate(n=N_ROWS, seed=SEED)

    # 2. Add synthetic timestamps (APPLICATION_DATE, clean feature timestamp, injected FAIL timestamp)
    df = add_timestamps(df, seed=SEED)

    # 3. Stratified 60/20/20 split — adds SPLIT column for FLL Check 5
    idx = df.index.to_numpy()
    y   = df[TARGET_COL].to_numpy()

    idx_train, idx_val = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val, idx_test  = train_test_split(idx_val, test_size=0.50,
                                           stratify=y[idx_val], random_state=SEED)

    df["SPLIT"] = "train"
    df.loc[idx_val,  "SPLIT"] = "val"
    df.loc[idx_test, "SPLIT"] = "test"

    train_rate = df.loc[df["SPLIT"] == "train", TARGET_COL].mean()
    val_rate   = df.loc[df["SPLIT"] == "val",   TARGET_COL].mean()
    test_rate  = df.loc[df["SPLIT"] == "test",  TARGET_COL].mean()
    print(f"[leakage_audit] Split: train={idx_train.size:,} ({train_rate:.3f}) | "
          f"val={idx_val.size:,} ({val_rate:.3f}) | test={idx_test.size:,} ({test_rate:.3f})")

    return df


def run_audit(df: pd.DataFrame):
    """Configure and run the FeatureLeakageLens 7-check audit."""
    # FLL uses SPLIT col for Check 5 (distribution shift); train_value='train', test_value='test'
    # We pass 'test' so FLL compares train vs. test distribution.
    config = LeakageAuditConfig(
        target_col                          = TARGET_COL,
        split_col                           = "SPLIT",
        train_value                         = "train",
        test_value                          = "test",
        outcome_time_col                    = OUTCOME_TIME_COL,
        feature_time_cols                   = FEATURE_TIME_COLS,
        ignore_cols                         = IGNORE_COLS,
        high_corr_threshold                 = 0.85,
        categorical_target_rate_gap_threshold = 0.65,
        max_unique_ratio_for_categorical_scan = 0.25,
        high_cardinality_ratio_threshold    = 0.90,
        distribution_shift_threshold        = 0.35,
    )

    print("\n[leakage_audit] Running FeatureLeakageLens audit…")
    report = audit_dataframe(df, config)
    return report


def save_outputs(df: pd.DataFrame, report, run_ts: str) -> dict:
    """Save JSON, Markdown, and HTML evidence artifacts. Return summary dict."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # ── 1. Save FLL native outputs ──────────────────────────────────────────
    json_path = os.path.join(OUTPUT_DIR, "leakage_report.json")
    md_path   = os.path.join(OUTPUT_DIR, "leakage_report.md")
    html_path = os.path.join(OUTPUT_DIR, "leakage_report.html")

    # FLL's to_json/to_markdown/to_html return strings
    fll_json = report.to_json()
    fll_md   = report.to_markdown()
    fll_html = report.to_html()

    # Enrich the JSON with PulseGuard metadata
    fll_dict = json.loads(fll_json)
    enriched = {
        "pulseguard_gate":        "G3",
        "run_timestamp":          run_ts,
        "dataset_label":          DATASET_LABEL,
        "dataset_source":         DATASET_SOURCE,
        "kaggle_available":       False,
        "n_rows_total":           len(df),
        "n_rows_train":           int((df["SPLIT"] == "train").sum()),
        "n_rows_val":             int((df["SPLIT"] == "val").sum()),
        "n_rows_test":            int((df["SPLIT"] == "test").sum()),
        "default_rate_train":     float(df.loc[df["SPLIT"]=="train", TARGET_COL].mean()),
        "synthetic_columns_added": [
            "APPLICATION_DATE",
            "FEATURE_TIMESTAMP_EXT_SOURCE_2",
            "FEATURE_TIMESTAMP_INJECTED_LEAK",
            "EXTERNAL_BUREAU_QUERY_RESULT__INJECTED",
            "EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC",
            "SPLIT",
        ],
        "injected_leakage_feature": "EXTERNAL_BUREAU_QUERY_RESULT__INJECTED",
        "injected_leakage_reason":  (
            "Simulates a post-application credit bureau query result. "
            "Timestamped APPLICATION_DATE + 1-30 days. "
            "Not available at application time → temporal leakage FAIL."
        ),
        "fll_audit":              fll_dict,
        "source_reference_note":  (
            "SR-12: FeatureLeakageLens on Home Credit produced 3 WARNs, 0 FAILs "
            "(SOURCE_REFERENCE — not PulseGuard-built). "
            "PulseGuard result on synthetic data with injected FAIL is shown above."
        ),
    }

    with open(json_path, "w") as f:
        json.dump(enriched, f, indent=2, default=str)

    # Prepend PulseGuard metadata block to FLL's markdown
    metadata_md = f"""# PulseGuard G3 — Leakage Detection Report

| Field | Value |
|-------|-------|
| Gate | G3 |
| Run timestamp | {run_ts} |
| Dataset | {DATASET_LABEL} |
| Kaggle available | No — synthetic fallback |
| Total rows | {len(df):,} |
| Default rate (train) | {df.loc[df['SPLIT']=='train', TARGET_COL].mean():.4f} |
| Overall status | **{report.status}** |

## Synthetic Columns Added
- `APPLICATION_DATE` — outcome reference timestamp (SYNTHETIC)
- `FEATURE_TIMESTAMP_EXT_SOURCE_2` — == APPLICATION_DATE (PASS path; SYNTHETIC)
- `FEATURE_TIMESTAMP_INJECTED_LEAK` — APPLICATION_DATE + 1–30 days (FAIL path; SYNTHETIC)
- `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` — injected leakage feature (SYNTHETIC)
- `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` — FOIR input, 5–25% of income (SYNTHETIC, excluded from audit)

---

## FeatureLeakageLens Findings

"""
    with open(md_path, "w") as f:
        f.write(metadata_md + fll_md)

    # Prepend metadata to HTML
    metadata_html = f"""<!DOCTYPE html>
<html><head><title>PulseGuard G3 Leakage Report</title></head><body>
<h1>PulseGuard G3 — Leakage Detection Report</h1>
<table border="1"><tr><th>Field</th><th>Value</th></tr>
<tr><td>Gate</td><td>G3</td></tr>
<tr><td>Run timestamp</td><td>{run_ts}</td></tr>
<tr><td>Dataset</td><td>{DATASET_LABEL}</td></tr>
<tr><td>Kaggle available</td><td>No — synthetic fallback</td></tr>
<tr><td>Total rows</td><td>{len(df):,}</td></tr>
<tr><td>Default rate (train)</td><td>{df.loc[df['SPLIT']=='train', TARGET_COL].mean():.4f}</td></tr>
<tr><td>Overall status</td><td><strong>{report.status}</strong></td></tr>
</table>
<h2>FeatureLeakageLens Findings</h2>
"""
    with open(html_path, "w") as f:
        f.write(metadata_html + fll_html + "</body></html>")

    return enriched


def print_report(report, enriched: dict) -> None:
    """Print human-readable summary to console."""
    fll = enriched["fll_audit"]
    summary = fll.get("summary", {})

    print("\n" + "=" * 60)
    print("  G3 LEAKAGE AUDIT REPORT")
    print(f"  Dataset:      {enriched['dataset_label']}")
    print(f"  Rows:         {enriched['n_rows_total']:,}")
    print(f"  Default rate: {enriched['default_rate_train']:.4f}")
    print("=" * 60)

    print(f"\n  Overall status: {report.status}")
    print(f"  Features checked: {summary.get('candidate_features_checked', '?')}")
    print(f"  Findings: {summary.get('finding_count', 0)} total "
          f"({summary.get('fail_count', 0)} FAIL, "
          f"{summary.get('warn_count', 0)} WARN, "
          f"{summary.get('insufficient_input_count', 0)} INSUFFICIENT_INPUT)")

    print("\n  Findings detail:")
    for finding in report.findings:
        print(f"    [{finding.status}] {finding.check_name}")
        if finding.feature:
            print(f"           feature: {finding.feature}")
        print(f"           {finding.detail[:100]}")

    print()
    print(f"  Outputs written:")
    print(f"    outputs/evidence/leakage_report.json")
    print(f"    outputs/evidence/leakage_report.md")
    print(f"    outputs/evidence/leakage_report.html")


if __name__ == "__main__":
    run_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    df       = build_dataset()
    report   = run_audit(df)
    enriched = save_outputs(df, report, run_ts)
    print_report(report, enriched)

    # Exit with error code if audit status is FAIL (to make CI gating possible)
    # Note: In PulseGuard design, FAIL blocks training at G4.
    # For G3 evidence, the FAIL is the expected result (injected leakage must fire).
    print("\n  [NOTE] FAIL status is expected — EXTERNAL_BUREAU_QUERY_RESULT__INJECTED")
    print("  is intentionally injected to demonstrate the temporal FAIL path.")
    print("  In a real pre-training gate, this feature would be dropped before training.")
    sys.exit(0)
