"""
G4 — Drift Monitoring Kernel
PulseGuard · PSI + KS Drift Detection Across 30-Day Lifecycle

Computes Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) statistic
for each numeric feature across 30 daily serving batches. Uses the training set
distribution as the reference.

Drift thresholds (standard industry convention):
  PSI < 0.10 → OK (stable)
  PSI 0.10–0.20 → WARN (monitor; investigation recommended)
  PSI > 0.20 → ALERT (significant shift; model reliability may be degraded)

  KS p-value < 0.01 → significant distribution shift (reported but not primary metric)

Run: python3 scripts/drift_monitor.py
"""

import json
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.generate_synthetic_data import generate, DATASET_LABEL
from scripts.seed_lifecycle import generate_batches, DRIFT_FEATURE, WARN_SHIFT, ALERT_SHIFT
from src.feature_pipeline import NUMERIC_COLS

# ── Configuration ──────────────────────────────────────────────────────────────
SEED        = 42
N_ROWS      = 50_000
OUTPUT_DIR  = "outputs/evidence"
PLOT_DIR    = "outputs/plots"
N_PSI_BINS  = 10
PSI_WARN    = 0.10
PSI_ALERT   = 0.20
DATA_TYPE   = "synthetic_home_credit_like"


# ── PSI computation ────────────────────────────────────────────────────────────
def compute_psi(
    reference: np.ndarray,
    actual:    np.ndarray,
    n_bins:    int = N_PSI_BINS,
) -> tuple[float, list[dict]]:
    """
    Compute PSI using reference-distribution quantile bins.

    Returns (psi_value, bin_details).
    """
    # Bin edges from reference distribution (equal-frequency bins)
    quantiles = np.linspace(0, 100, n_bins + 1)
    bin_edges = np.percentile(reference, quantiles)
    bin_edges[0]  -= 1e-8
    bin_edges[-1] += 1e-8

    eps = 1e-8
    ref_counts = np.histogram(reference, bins=bin_edges)[0].astype(float)
    act_counts = np.histogram(actual,    bins=bin_edges)[0].astype(float)

    ref_pct = (ref_counts + eps) / (ref_counts.sum() + eps * n_bins)
    act_pct = (act_counts + eps) / (act_counts.sum() + eps * n_bins)

    bin_psi  = (act_pct - ref_pct) * np.log(act_pct / ref_pct)
    psi_val  = float(bin_psi.sum())

    bin_details = [
        {
            "bin":           i + 1,
            "lower":         round(float(bin_edges[i]), 6),
            "upper":         round(float(bin_edges[i + 1]), 6),
            "ref_pct":       round(float(ref_pct[i]), 6),
            "act_pct":       round(float(act_pct[i]), 6),
            "bin_psi":       round(float(bin_psi[i]), 6),
        }
        for i in range(n_bins)
    ]
    return round(psi_val, 6), bin_details


def psi_status(psi: float) -> str:
    if psi > PSI_ALERT: return "ALERT"
    if psi > PSI_WARN:  return "WARN"
    return "OK"


# ── KS computation ─────────────────────────────────────────────────────────────
def compute_ks(reference: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    """Return (KS statistic, p-value)."""
    result = stats.ks_2samp(reference, actual)
    return round(float(result.statistic), 6), round(float(result.pvalue), 8)


# ── Reference distribution ─────────────────────────────────────────────────────
def build_reference() -> dict[str, np.ndarray]:
    """Build reference distributions from the training split."""
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        df = generate(n=N_ROWS, seed=SEED)

    y   = df["TARGET"].to_numpy()
    idx = df.index.to_numpy()
    idx_train, _ = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    df_train = df.loc[idx_train]

    reference = {}
    for col in NUMERIC_COLS:
        vals = df_train[col].dropna().to_numpy(dtype=np.float64)
        reference[col] = vals
    return reference


# ── Main monitoring loop ────────────────────────────────────────────────────────
def run_drift_monitor(reference: dict, batches: dict) -> dict:
    """
    For each day and each numeric feature, compute PSI and KS.
    Returns a full report dict.
    """
    n_days = max(batches.keys())
    daily_results = []

    for day in sorted(batches.keys()):
        df_batch = batches[day]
        regime        = df_batch["DRIFT_REGIME"].iloc[0]
        drift_injected = df_batch["DRIFT_INJECTED"].iloc[0]
        drift_shift    = float(df_batch["DRIFT_SHIFT_MAGNITUDE"].iloc[0])

        feature_stats = {}
        day_max_psi   = 0.0
        day_alerts    = []
        day_warns     = []

        for col in NUMERIC_COLS:
            ref_vals = reference[col]
            act_vals = df_batch[col].dropna().to_numpy(dtype=np.float64)
            if len(act_vals) < 10:
                continue

            psi_val, _    = compute_psi(ref_vals, act_vals)
            ks_stat, ks_p = compute_ks(ref_vals, act_vals)
            status        = psi_status(psi_val)

            feature_stats[col] = {
                "psi":       psi_val,
                "ks_stat":   ks_stat,
                "ks_pvalue": ks_p,
                "status":    status,
            }

            if psi_val > day_max_psi:
                day_max_psi = psi_val
            if status == "ALERT": day_alerts.append(col)
            if status == "WARN":  day_warns.append(col)

        day_overall_status = "ALERT" if day_alerts else ("WARN" if day_warns else "OK")

        daily_results.append({
            "day":              day,
            "drift_regime":     regime,
            "drift_injected":   bool(drift_injected),
            "drift_shift":      drift_shift,
            "overall_status":   day_overall_status,
            "max_psi_any_feature": round(day_max_psi, 6),
            "n_alert_features": len(day_alerts),
            "n_warn_features":  len(day_warns),
            "alert_features":   day_alerts,
            "warn_features":    day_warns,
            f"{DRIFT_FEATURE}_psi":    feature_stats.get(DRIFT_FEATURE, {}).get("psi"),
            f"{DRIFT_FEATURE}_ks":     feature_stats.get(DRIFT_FEATURE, {}).get("ks_stat"),
            f"{DRIFT_FEATURE}_status": feature_stats.get(DRIFT_FEATURE, {}).get("status"),
            "feature_stats":    feature_stats,
        })

        ext_psi = feature_stats.get(DRIFT_FEATURE, {}).get("psi", 0)
        ext_status = feature_stats.get(DRIFT_FEATURE, {}).get("status", "OK")
        print(f"  Day {day:2d}  {regime:<20s}  "
              f"{DRIFT_FEATURE}_PSI={ext_psi:.4f}  {DRIFT_FEATURE}={ext_status}  "
              f"overall={day_overall_status}")

    return {
        "pulseguard_gate":     "G4",
        "artifact":            "g4_drift_report.json",
        "data_type":           DATA_TYPE,
        "dataset_label":       DATASET_LABEL,
        "reference":           "training split (30,000 rows, seed=42)",
        "n_days":              n_days,
        "batch_size":          2000,
        "n_psi_bins":          N_PSI_BINS,
        "psi_warn_threshold":  PSI_WARN,
        "psi_alert_threshold": PSI_ALERT,
        "drift_schedule": {
            "days_1_6":   {"regime": "BASELINE",        "shift": 0.0,       "expected_status": "OK"},
            "days_7_13":  {"regime": "WARN_INJECTED",   "shift": WARN_SHIFT, "expected_status": "WARN"},
            "days_14_30": {"regime": "ALERT_INJECTED",  "shift": ALERT_SHIFT,"expected_status": "ALERT"},
            "drift_note": "All drift is SYNTHETIC/INJECTED. Not observed production telemetry.",
        },
        "monitored_features": NUMERIC_COLS,
        "n_monitored_features": len(NUMERIC_COLS),
        "daily_results":      daily_results,
    }


# ── Plots ──────────────────────────────────────────────────────────────────────
def plot_psi_time_series(daily_results: list, out_path: str) -> None:
    days = [r["day"] for r in daily_results]
    psi_vals = [r[f"{DRIFT_FEATURE}_psi"] or 0.0 for r in daily_results]
    statuses = [r[f"{DRIFT_FEATURE}_status"] or "OK" for r in daily_results]

    colors = []
    for s in statuses:
        if s == "ALERT":  colors.append("#e05c5c")
        elif s == "WARN": colors.append("#f4a34a")
        else:             colors.append("#4caf79")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(days, psi_vals, color=colors, alpha=0.85, edgecolor="white", linewidth=0.5)

    ax.axhline(PSI_WARN,  color="#f4a34a", lw=2.0, ls="--", label=f"WARN threshold ({PSI_WARN})")
    ax.axhline(PSI_ALERT, color="#e05c5c", lw=2.0, ls="--", label=f"ALERT threshold ({PSI_ALERT})")

    ax.axvline(6.5,  color="gray", lw=1, ls=":", alpha=0.7)
    ax.axvline(13.5, color="gray", lw=1, ls=":", alpha=0.7)
    ax.text(3.5,  max(psi_vals) * 0.92, "Baseline",     ha="center", fontsize=9, color="gray")
    ax.text(10.0, max(psi_vals) * 0.92, "WARN\n(injected)", ha="center", fontsize=9, color="#c47c00")
    ax.text(22.0, max(psi_vals) * 0.92, "ALERT\n(injected)", ha="center", fontsize=9, color="#cc0000")

    ax.set_xlabel("Day",           fontsize=12)
    ax.set_ylabel("PSI",           fontsize=12)
    ax.set_title(f"PulseGuard G4 — EXT_SOURCE_2 PSI Over 30-Day Lifecycle\n"
                 f"(synthetic_home_credit_like · SYNTHETIC drift injection)",
                 fontsize=11)
    ax.legend(fontsize=10)
    ax.set_xlim(0.5, 30.5)
    ax.set_ylim(0, max(psi_vals) * 1.15)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[drift_monitor] PSI plot saved → {out_path}")


# ── Summary report ─────────────────────────────────────────────────────────────
def print_summary(report: dict) -> None:
    daily = report["daily_results"]

    day7  = next(r for r in daily if r["day"] == 7)
    day14 = next(r for r in daily if r["day"] == 14)

    ext_7  = day7.get(f"{DRIFT_FEATURE}_psi",    0)
    ext_14 = day14.get(f"{DRIFT_FEATURE}_psi",   0)
    st_7   = day7.get(f"{DRIFT_FEATURE}_status",  "?")
    st_14  = day14.get(f"{DRIFT_FEATURE}_status", "?")
    ks_7   = day7.get(f"{DRIFT_FEATURE}_ks",      0)
    ks_14  = day14.get(f"{DRIFT_FEATURE}_ks",     0)

    print("\n" + "=" * 60)
    print("  G4 DRIFT MONITORING REPORT")
    print("=" * 60)
    print(f"  Reference: training split (30,000 rows)")
    print(f"  Batch size: 2,000 per day | {report['n_days']} days")
    print(f"\n  Day 7  ({DRIFT_FEATURE}):  PSI={ext_7:.4f}  KS={ks_7:.4f}  → {st_7}")
    print(f"  Day 14 ({DRIFT_FEATURE}):  PSI={ext_14:.4f}  KS={ks_14:.4f}  → {st_14}")
    print(f"\n  WARN threshold:  PSI > {PSI_WARN:.2f}")
    print(f"  ALERT threshold: PSI > {PSI_ALERT:.2f}")
    day7_pass  = st_7 == "WARN"
    day14_pass = st_14 == "ALERT"
    print(f"\n  Day 7 WARN fires:  {'✓ YES' if day7_pass  else '✗ NO  (UNEXPECTED)'}")
    print(f"  Day 14 ALERT fires: {'✓ YES' if day14_pass else '✗ NO  (UNEXPECTED)'}")
    print(f"\n  Outputs:")
    print(f"    outputs/evidence/g4_drift_report.json")
    print(f"    outputs/plots/g4_drift_psi_ext_source_2.png")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    run_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR,   exist_ok=True)

    print("[drift_monitor] Building reference distributions from training split…")
    reference = build_reference()

    print(f"[drift_monitor] Generating {30} daily serving batches…")
    batches = generate_batches(n_days=30)

    print(f"[drift_monitor] Computing PSI and KS for {len(NUMERIC_COLS)} features × 30 days…")
    report = run_drift_monitor(reference, batches)
    report["run_timestamp"] = run_ts

    json_path = os.path.join(OUTPUT_DIR, "g4_drift_report.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n[drift_monitor] Report saved → {json_path} ({os.path.getsize(json_path):,} bytes)")

    plot_path = os.path.join(PLOT_DIR, "g4_drift_psi_ext_source_2.png")
    plot_psi_time_series(report["daily_results"], plot_path)

    print_summary(report)


if __name__ == "__main__":
    main()
