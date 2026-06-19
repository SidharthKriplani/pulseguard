"""
G6 — Taiwan Default Data Adapter
PulseGuard · Real-Data Lane

Loads data/public/taiwan_credit_default.xls, profiles the dataset,
and writes outputs/evidence/g6_taiwan_data_profile.json.

Data tag: PUBLIC_REAL_TAIWAN_DEFAULT
Source: UCI ML Repository — no authentication required
Citation: Yeh & Lien (2009), Expert Systems with Applications 36(2)
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
XLS_PATH = ROOT / "data" / "public" / "taiwan_credit_default.xls"
OUT_DIR = ROOT / "outputs" / "evidence"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "g6_taiwan_data_profile.json"


# ── schema constants ─────────────────────────────────────────────────────────
TARGET_COL = "default payment next month"
ID_COL = "ID"

# Payment status columns (ordinal; negative = no delinquency, positive = months late)
PAY_COLS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]

# Bill statement amounts (NT$)
BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]

# Previous payment amounts (NT$)
PAY_AMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]

# Demographic / categorical columns
CATEGORICAL_COLS = ["SEX", "EDUCATION", "MARRIAGE"]

# Numeric non-categorical columns
NUMERIC_COLS = ["LIMIT_BAL", "AGE"] + PAY_COLS + BILL_COLS + PAY_AMT_COLS

# All feature columns (excludes ID and target)
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS

# Known EDUCATION codes (0, 5, 6 are undocumented in original paper)
EDUCATION_LABELS = {1: "graduate_school", 2: "university", 3: "high_school",
                    4: "others", 0: "undocumented_0", 5: "undocumented_5",
                    6: "undocumented_6"}
# Known MARRIAGE codes (0 is undocumented)
MARRIAGE_LABELS = {1: "married", 2: "single", 3: "others", 0: "undocumented_0"}
# SEX codes
SEX_LABELS = {1: "male", 2: "female"}


def load_taiwan_data(path: Path) -> pd.DataFrame:
    """Load XLS with correct header row (row index 1, 0-indexed)."""
    df = pd.read_excel(path, header=1, engine="xlrd")
    # Standardise column names: strip whitespace
    df.columns = [c.strip() for c in df.columns]
    return df


def compute_class_balance(df: pd.DataFrame) -> dict:
    vc = df[TARGET_COL].value_counts().sort_index()
    n = len(df)
    return {
        "n_total": int(n),
        "n_default_1": int(vc.get(1, 0)),
        "n_no_default_0": int(vc.get(0, 0)),
        "default_rate": round(float(vc.get(1, 0) / n), 6),
        "no_default_rate": round(float(vc.get(0, 0) / n), 6),
    }


def compute_missingness(df: pd.DataFrame, cols: list) -> dict:
    result = {}
    for c in cols:
        n_null = int(df[c].isna().sum())
        result[c] = {"n_null": n_null, "pct_null": round(n_null / len(df), 6)}
    return result


def compute_demographic_profile(df: pd.DataFrame) -> dict:
    profile = {}

    # SEX
    sex_vc = df["SEX"].value_counts().sort_index()
    profile["sex"] = {
        SEX_LABELS.get(k, str(k)): {
            "n": int(v),
            "pct": round(float(v / len(df)), 4),
            "default_rate": round(float(df.loc[df["SEX"] == k, TARGET_COL].mean()), 4),
        }
        for k, v in sex_vc.items()
    }

    # EDUCATION
    edu_vc = df["EDUCATION"].value_counts().sort_index()
    profile["education"] = {
        EDUCATION_LABELS.get(k, str(k)): {
            "n": int(v),
            "pct": round(float(v / len(df)), 4),
            "default_rate": round(float(df.loc[df["EDUCATION"] == k, TARGET_COL].mean()), 4),
        }
        for k, v in edu_vc.items()
    }

    # MARRIAGE
    mar_vc = df["MARRIAGE"].value_counts().sort_index()
    profile["marriage"] = {
        MARRIAGE_LABELS.get(k, str(k)): {
            "n": int(v),
            "pct": round(float(v / len(df)), 4),
            "default_rate": round(float(df.loc[df["MARRIAGE"] == k, TARGET_COL].mean()), 4),
        }
        for k, v in mar_vc.items()
    }

    # AGE
    profile["age"] = {
        "min": int(df["AGE"].min()),
        "max": int(df["AGE"].max()),
        "mean": round(float(df["AGE"].mean()), 2),
        "median": float(df["AGE"].median()),
        "default_rate_under_30": round(float(df.loc[df["AGE"] < 30, TARGET_COL].mean()), 4),
        "default_rate_30_to_45": round(float(df.loc[(df["AGE"] >= 30) & (df["AGE"] < 45), TARGET_COL].mean()), 4),
        "default_rate_45_plus": round(float(df.loc[df["AGE"] >= 45, TARGET_COL].mean()), 4),
    }

    return profile


def compute_feature_summary(df: pd.DataFrame) -> dict:
    summary = {}
    for c in NUMERIC_COLS:
        summary[c] = {
            "dtype": str(df[c].dtype),
            "min": float(df[c].min()),
            "max": float(df[c].max()),
            "mean": round(float(df[c].mean()), 4),
            "std": round(float(df[c].std()), 4),
            "n_null": int(df[c].isna().sum()),
        }
    for c in CATEGORICAL_COLS:
        summary[c] = {
            "dtype": str(df[c].dtype),
            "unique_values": sorted(df[c].dropna().unique().tolist()),
            "n_null": int(df[c].isna().sum()),
        }
    return summary


def compute_payment_status_distribution(df: pd.DataFrame) -> dict:
    result = {}
    for c in PAY_COLS:
        vc = df[c].value_counts().sort_index()
        result[c] = {str(int(k)): int(v) for k, v in vc.items()}
    return result


def main():
    print(f"Loading: {XLS_PATH}")
    df = load_taiwan_data(XLS_PATH)
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Verify target column exists
    assert TARGET_COL in df.columns, f"Target column '{TARGET_COL}' not found. Columns: {list(df.columns)}"
    assert ID_COL in df.columns, f"ID column not found."

    class_balance = compute_class_balance(df)
    print(f"Default rate: {class_balance['default_rate']:.4f}")

    missingness = compute_missingness(df, FEATURE_COLS + [TARGET_COL])
    total_nulls = sum(v["n_null"] for v in missingness.values())
    print(f"Total null values: {total_nulls}")

    demographic_profile = compute_demographic_profile(df)
    feature_summary = compute_feature_summary(df)
    payment_status_dist = compute_payment_status_distribution(df)

    # Undocumented EDUCATION / MARRIAGE code counts
    edu_undocumented = int(df["EDUCATION"].isin([0, 5, 6]).sum())
    mar_undocumented = int(df["MARRIAGE"].isin([0]).sum())

    report = {
        "pulseguard_gate": "G6",
        "data_tag": "PUBLIC_REAL_TAIWAN_DEFAULT",
        "dataset_name": "UCI Credit Card Default (Taiwan)",
        "local_path": "data/public/taiwan_credit_default.xls",
        "source_url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls",
        "citation": "Yeh & Lien (2009). Expert Systems with Applications 36(2), 2473-2480.",
        "auth_required": False,
        "product_type": "credit_card_default",
        "geography": "Taiwan",
        "vintage": "April 2005 to September 2005",

        "schema": {
            "n_rows": int(df.shape[0]),
            "n_columns": int(df.shape[1]),
            "id_column": ID_COL,
            "target_column": TARGET_COL,
            "target_meaning": "1 = defaulted on next month payment; 0 = no default",
            "feature_columns": FEATURE_COLS,
            "n_features": len(FEATURE_COLS),
            "categorical_features": CATEGORICAL_COLS,
            "numeric_features": NUMERIC_COLS,
            "payment_status_features": PAY_COLS,
            "bill_amount_features": BILL_COLS,
            "payment_amount_features": PAY_AMT_COLS,
        },

        "class_balance": class_balance,

        "missingness": {
            "total_null_values": total_nulls,
            "per_column": missingness,
            "assessment": "zero_missing" if total_nulls == 0 else "has_missing",
        },

        "demographic_profile": demographic_profile,

        "data_quality_notes": [
            f"EDUCATION codes 0/5/6 are undocumented in original paper; {edu_undocumented} rows affected ({100*edu_undocumented/len(df):.2f}%)",
            f"MARRIAGE code 0 is undocumented; {mar_undocumented} rows affected ({100*mar_undocumented/len(df):.2f}%)",
            "PAY_0 represents September 2005 repayment status; PAY_2 = August; PAY_3 = July; ... PAY_6 = April",
            "PAY status codes: -2=no consumption, -1=paid in full, 0=use revolving credit, 1=1 month late, ..., 8=8 months late",
            "BILL_AMT values can be negative (credit balance after overpayment)",
            "PAY_AMT values of 0 may indicate no payment was made",
        ],

        "feature_summary": feature_summary,
        "payment_status_distributions": payment_status_dist,

        "g6_feature_pipeline_notes": {
            "drop_columns": [ID_COL],
            "target": TARGET_COL,
            "categorical_encoding": "ordinal_or_onehot for SEX/EDUCATION/MARRIAGE",
            "numeric_scaling": "StandardScaler on LIMIT_BAL, AGE, BILL_AMT*, PAY_AMT*",
            "payment_status_treatment": "numeric (ordinal; already integer-coded)",
            "undocumented_codes": "retain as-is; document in notes; do not impute",
        },

        "synthetic_harness_boundary": (
            "Taiwan Default data is SEPARATE from synthetic_home_credit_like. "
            "Do NOT mix Taiwan metrics with synthetic G4 champion metrics. "
            "Taiwan Default is the G6 primary modeling evidence. "
            "Synthetic data is retained only for injected failure-mode tests."
        ),

        "claim_boundary": [
            "No real applicant claim — this is public research data",
            "No production deployment claim",
            "No regulatory-grade fairness claim",
            "No Home Credit claim — this is Taiwan credit card data, not Home Credit consumer loan data",
            "Product: credit card default (revolving credit), not consumer loan underwriting",
            "Geography: Taiwan; vintage: 2005; not representative of current global credit populations",
        ],
    }

    with open(OUT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nProfile written: {OUT_PATH}")
    print(f"  Rows: {report['schema']['n_rows']}")
    print(f"  Features: {report['schema']['n_features']}")
    print(f"  Default rate: {report['class_balance']['default_rate']:.4f}")
    print(f"  Total nulls: {total_nulls}")
    print(f"  Male DR: {report['demographic_profile']['sex']['male']['default_rate']:.4f}")
    print(f"  Female DR: {report['demographic_profile']['sex']['female']['default_rate']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
