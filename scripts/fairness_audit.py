"""
G5 — Fairness Audit
PulseGuard · Group-Level Model Performance and Calibration Analysis

Evaluates the champion model for fairness across CODE_GENDER groups (F/M).
CODE_GENDER is a proxy demographic attribute in the synthetic dataset — it is
NOT a real protected class. This audit demonstrates the methodology; results
apply only to synthetic_home_credit_like data.

Metrics computed:
  1. Score distribution by group (mean, median, std PD)
  2. Approval rates under synthetic policy v1.0
       APPROVE: PD < 0.06
       REVIEW:  0.06 ≤ PD < 0.28
       REJECT:  PD ≥ 0.28
  3. Disparate Impact (DI) = approval_rate_F / approval_rate_M
     Acceptable range: 0.80–1.25 (4/5ths rule heuristic)
  4. Equal Opportunity gap = |TPR_F − TPR_M|
     TPR = P(score ≥ 0.06 | TARGET=1) — flag rate among true defaults
  5. Predictive Parity gap = |PPV_F − PPV_M|
     PPV = P(TARGET=1 | score ≥ 0.06) — precision at REVIEW/REJECT threshold
  6. ROC-AUC by group
  7. ECE by group (calibration quality per group)
  8. XGBoost feature importance rank of CODE_GENDER (gain)

Scope boundary (G5):
  - ALLOWED: group performance comparison, calibration, score distribution
  - FORBIDDEN: SHAP explanation system, adverse-action notices,
               FOIR routing, compliance certification, real protected-class claim

Run: python3 scripts/fairness_audit.py
"""

import json
import os
import sys
from datetime import datetime

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.generate_synthetic_data import generate, DATASET_LABEL
from src.feature_pipeline import build_features, FEATURE_COLS

# ── Configuration ──────────────────────────────────────────────────────────────
SEED             = 42
N_ROWS           = 50_000
GROUP_COL        = "CODE_GENDER"
GROUP_VALS       = ["F", "M"]
OUTPUT_DIR       = "outputs/evidence"
PLOT_DIR         = "outputs/plots"
DATA_TYPE        = "synthetic_home_credit_like"

# Synthetic policy v1.0 thresholds (not a real credit policy)
APPROVE_THRESH   = 0.06   # PD < 0.06 → APPROVE
REJECT_THRESH    = 0.28   # PD ≥ 0.28 → REJECT

# Disparate Impact acceptability band (4/5ths rule heuristic)
DI_LOWER         = 0.80
DI_UPPER         = 1.25

# ECE bins
N_ECE_BINS       = 10


# ── Helper: ECE ────────────────────────────────────────────────────────────────
def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = N_ECE_BINS) -> float:
    """Expected Calibration Error, equal-width bins."""
    bins   = np.linspace(0, 1, n_bins + 1)
    ece    = 0.0
    n      = len(y_true)
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() == 0:
            continue
        acc = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += (mask.sum() / n) * abs(acc - conf)
    return round(float(ece), 6)


# ── Helper: group metrics ──────────────────────────────────────────────────────
def group_metrics(y: np.ndarray, prob: np.ndarray, group_name: str) -> dict:
    """Compute all fairness-relevant metrics for one group."""
    n   = len(y)
    dr  = float(y.mean())

    # Score distribution
    score_mean   = float(prob.mean())
    score_median = float(np.median(prob))
    score_std    = float(prob.std())

    # Routing under synthetic policy v1.0
    approve_mask = prob < APPROVE_THRESH
    review_mask  = (prob >= APPROVE_THRESH) & (prob < REJECT_THRESH)
    reject_mask  = prob >= REJECT_THRESH

    approval_rate = float(approve_mask.mean())
    review_rate   = float(review_mask.mean())
    reject_rate   = float(reject_mask.mean())

    # Equal Opportunity: TPR = P(score ≥ APPROVE_THRESH | Y=1)
    # i.e., among true defaults, fraction correctly flagged as REVIEW or REJECT
    true_defaults = y == 1
    if true_defaults.sum() > 0:
        tpr = float((prob[true_defaults] >= APPROVE_THRESH).mean())
    else:
        tpr = float("nan")

    # Predictive Parity: PPV = P(Y=1 | score ≥ APPROVE_THRESH)
    flagged = prob >= APPROVE_THRESH
    if flagged.sum() > 0:
        ppv = float(y[flagged].mean())
    else:
        ppv = float("nan")

    # ROC-AUC (suppress if only one class)
    try:
        auc = round(float(roc_auc_score(y, prob)), 6)
    except ValueError:
        auc = float("nan")

    # ECE
    ece = compute_ece(y, prob)

    return {
        "group":         group_name,
        "n":             int(n),
        "n_defaults":    int(y.sum()),
        "default_rate":  round(dr, 6),
        "score_mean_pd": round(score_mean, 6),
        "score_median_pd": round(score_median, 6),
        "score_std_pd":  round(score_std, 6),
        "approval_rate": round(approval_rate, 6),
        "review_rate":   round(review_rate, 6),
        "reject_rate":   round(reject_rate, 6),
        "tpr":           round(tpr, 6),   # Equal Opportunity numerator
        "ppv":           round(ppv, 6),   # Predictive Parity numerator
        "roc_auc":       auc,
        "ece":           ece,
    }


# ── Data loading ───────────────────────────────────────────────────────────────
def load_test_set():
    """Reproduce the exact test split used in train_champion.py."""
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        df = generate(n=N_ROWS, seed=SEED)

    y   = df["TARGET"].to_numpy()
    idx = df.index.to_numpy()

    idx_train, idx_tmp = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val,   idx_test = train_test_split(
        idx_tmp, test_size=0.50,
        stratify=y[idx_tmp], random_state=SEED,
    )
    df_test = df.loc[idx_test].reset_index(drop=True)
    return df_test


def load_models():
    preprocessor = joblib.load("outputs/models/preprocessor.pkl")
    calibrated   = joblib.load("outputs/models/champion_calibrated.pkl")
    return preprocessor, calibrated


# ── Feature importance rank of CODE_GENDER ────────────────────────────────────
def get_gender_feature_rank(calibrated_model) -> dict:
    """
    Extract CODE_GENDER ordinal-encoded importance rank from XGBoost.
    Uses gain importance. The underlying XGB is at calibrated_model.calibrated_classifiers_[0].estimator.
    Feature order: NUMERIC_COLS (20) then CATEGORICAL_COLS (8).
    CODE_GENDER is the first categorical feature → index 20.
    """
    from src.feature_pipeline import NUMERIC_COLS, CATEGORICAL_COLS
    all_features = NUMERIC_COLS + CATEGORICAL_COLS

    # CalibratedClassifierCV wraps one or more calibrated classifiers
    xgb_model = calibrated_model.calibrated_classifiers_[0].estimator

    scores = xgb_model.get_booster().get_score(importance_type="gain")
    # XGB uses "f0", "f1", ... for column-index feature names when trained on arrays
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Map f<idx> → feature name
    def fname(fidx_str):
        idx = int(fidx_str[1:])
        return all_features[idx] if idx < len(all_features) else fidx_str

    ranked_named = [(fname(k), round(v, 6)) for k, v in ranked]

    # Find CODE_GENDER rank
    gender_rank = None
    gender_gain = None
    for rank, (feat, gain) in enumerate(ranked_named, start=1):
        if feat == "CODE_GENDER":
            gender_rank = rank
            gender_gain = gain
            break

    return {
        "top10_features": [{"rank": i+1, "feature": f, "gain": g}
                           for i, (f, g) in enumerate(ranked_named[:10])],
        "code_gender_rank": gender_rank,
        "code_gender_gain": gender_gain,
        "n_features_with_nonzero_gain": len(ranked_named),
        "note": "Gain importance from XGBoost booster. CODE_GENDER rank and gain determine whether gender is a primary driver.",
    }


# ── Plot: score distribution by group ─────────────────────────────────────────
def plot_score_distribution(df_test: pd.DataFrame, probs: np.ndarray, out_path: str):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    colors = {"F": "#4b8bbe", "M": "#e87b35"}

    # Left: score density by group
    ax = axes[0]
    for grp in GROUP_VALS:
        mask = df_test[GROUP_COL] == grp
        ax.hist(
            probs[mask], bins=40, alpha=0.60, density=True,
            color=colors[grp], label=f"CODE_GENDER={grp} (n={mask.sum():,})",
            edgecolor="white", linewidth=0.3,
        )
    ax.axvline(APPROVE_THRESH, color="green",  ls="--", lw=1.5, label=f"APPROVE|REVIEW ({APPROVE_THRESH})")
    ax.axvline(REJECT_THRESH,  color="red",    ls="--", lw=1.5, label=f"REVIEW|REJECT ({REJECT_THRESH})")
    ax.set_xlabel("Predicted Default Probability (PD)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title("PulseGuard G5 — Score Distribution by CODE_GENDER\n(synthetic_home_credit_like)", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Right: calibration curve by group
    ax = axes[1]
    for grp in GROUP_VALS:
        mask = df_test[GROUP_COL] == grp
        y_g    = df_test["TARGET"].to_numpy()[mask]
        prob_g = probs[mask]
        frac_pos, mean_pred = calibration_curve(y_g, prob_g, n_bins=8)
        ax.plot(mean_pred, frac_pos, "o-", color=colors[grp], label=f"CODE_GENDER={grp}", lw=1.5, ms=5)

    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")
    ax.set_xlabel("Mean Predicted Probability", fontsize=11)
    ax.set_ylabel("Fraction of Positives", fontsize=11)
    ax.set_title("PulseGuard G5 — Calibration Curve by CODE_GENDER\n(synthetic_home_credit_like)", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 0.55)
    ax.set_ylim(0, 0.55)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[fairness_audit] Plot saved → {out_path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    run_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR,   exist_ok=True)

    print("[fairness_audit] Loading models…")
    preprocessor, calibrated = load_models()

    print("[fairness_audit] Loading test set (same split as train_champion.py, seed=42)…")
    df_test = load_test_set()
    n_test  = len(df_test)
    print(f"  Test set: {n_test:,} rows | default_rate={df_test['TARGET'].mean():.4f}")

    print("[fairness_audit] Generating predictions…")
    X_test, y_test, _ = build_features(df_test, fit=False, preprocessor=preprocessor)
    probs = calibrated.predict_proba(X_test)[:, 1]

    # Group breakdown
    print(f"\n[fairness_audit] Group breakdown ({GROUP_COL}):")
    for grp in GROUP_VALS:
        mask = df_test[GROUP_COL] == grp
        print(f"  {grp}: n={mask.sum():,}  default_rate={df_test['TARGET'][mask].mean():.4f}")

    # Per-group metrics
    print("\n[fairness_audit] Computing per-group metrics…")
    group_results = {}
    for grp in GROUP_VALS:
        mask   = (df_test[GROUP_COL] == grp).to_numpy()
        y_g    = y_test[mask]
        prob_g = probs[mask]
        group_results[grp] = group_metrics(y_g, prob_g, grp)

    gF = group_results["F"]
    gM = group_results["M"]

    # Fairness metrics
    di          = round(gF["approval_rate"] / gM["approval_rate"], 6) if gM["approval_rate"] > 0 else float("nan")
    eopp_gap    = round(abs(gF["tpr"] - gM["tpr"]), 6)
    pparity_gap = round(abs(gF["ppv"] - gM["ppv"]), 6)
    auc_gap     = round(abs(gF["roc_auc"] - gM["roc_auc"]), 6)
    ece_gap     = round(abs(gF["ece"] - gM["ece"]), 6)

    di_pass = DI_LOWER <= di <= DI_UPPER
    di_status = "PASS" if di_pass else "FAIL"

    # Feature importance rank of CODE_GENDER
    print("[fairness_audit] Extracting CODE_GENDER feature importance rank…")
    gender_rank_info = get_gender_feature_rank(calibrated)

    # Print summary
    print("\n" + "=" * 60)
    print("  G5 FAIRNESS AUDIT SUMMARY")
    print("=" * 60)
    print(f"  Group column:           {GROUP_COL}")
    print(f"  Policy threshold:       APPROVE < {APPROVE_THRESH}  |  REJECT >= {REJECT_THRESH}")
    print()
    print(f"  {'Metric':<30}  {'F':>10}  {'M':>10}  {'Gap':>10}")
    print(f"  {'-'*30}  {'-'*10}  {'-'*10}  {'-'*10}")
    print(f"  {'n':.<30}  {gF['n']:>10,}  {gM['n']:>10,}")
    print(f"  {'default_rate':.<30}  {gF['default_rate']:>10.4f}  {gM['default_rate']:>10.4f}  {abs(gF['default_rate']-gM['default_rate']):>10.4f}")
    print(f"  {'mean_pd':.<30}  {gF['score_mean_pd']:>10.4f}  {gM['score_mean_pd']:>10.4f}  {abs(gF['score_mean_pd']-gM['score_mean_pd']):>10.4f}")
    print(f"  {'approval_rate':.<30}  {gF['approval_rate']:>10.4f}  {gM['approval_rate']:>10.4f}")
    print(f"  {'Disparate Impact (F/M)':.<30}  {di:>10.4f}  {'':>10}  → {di_status} (band {DI_LOWER}–{DI_UPPER})")
    print(f"  {'TPR (Equal Opportunity)':.<30}  {gF['tpr']:>10.4f}  {gM['tpr']:>10.4f}  {eopp_gap:>10.4f}")
    print(f"  {'PPV (Predictive Parity)':.<30}  {gF['ppv']:>10.4f}  {gM['ppv']:>10.4f}  {pparity_gap:>10.4f}")
    print(f"  {'ROC-AUC':.<30}  {gF['roc_auc']:>10.4f}  {gM['roc_auc']:>10.4f}  {auc_gap:>10.4f}")
    print(f"  {'ECE':.<30}  {gF['ece']:>10.4f}  {gM['ece']:>10.4f}  {ece_gap:>10.4f}")
    print()
    print(f"  CODE_GENDER importance rank:  #{gender_rank_info['code_gender_rank']}  (gain={gender_rank_info['code_gender_gain']})")
    print(f"  Top feature:                  {gender_rank_info['top10_features'][0]['feature']} (gain={gender_rank_info['top10_features'][0]['gain']})")

    # Build report
    report = {
        "pulseguard_gate":  "G5",
        "artifact":         "g5_fairness_report.json",
        "run_timestamp":    run_ts,
        "data_type":        DATA_TYPE,
        "dataset_label":    DATASET_LABEL,
        "group_col":        GROUP_COL,
        "group_vals":       GROUP_VALS,
        "n_test":           n_test,
        "split_context":    "test set only (10,000 rows); same 60/20/20 split as train_champion.py, seed=42",
        "policy_thresholds": {
            "approve_below": APPROVE_THRESH,
            "reject_above_or_equal": REJECT_THRESH,
            "policy_version": "v1.0 (synthetic — not a real credit policy)",
        },
        "group_metrics": {grp: group_results[grp] for grp in GROUP_VALS},
        "fairness_metrics": {
            "disparate_impact_F_over_M": di,
            "di_acceptable_band":        f"{DI_LOWER}–{DI_UPPER}",
            "di_status":                 di_status,
            "equal_opportunity_gap_abs": eopp_gap,
            "predictive_parity_gap_abs": pparity_gap,
            "roc_auc_gap_abs":           auc_gap,
            "ece_gap_abs":               ece_gap,
        },
        "code_gender_importance": gender_rank_info,
        "scope_boundary": {
            "allowed": [
                "group performance comparison",
                "group calibration comparison",
                "approval-rate / score-distribution analysis",
                "fairness caveats and claim boundaries",
            ],
            "forbidden": [
                "SHAP explanation system",
                "adverse-action notices",
                "FOIR routing",
                "decision engine",
                "compliance certification",
                "real protected-class claim",
                "production fairness claim",
            ],
        },
        "caveats": [
            "CODE_GENDER is a synthetic proxy attribute generated with p=[0.65, 0.35] (F/M). It is NOT a real protected class.",
            "CODE_GENDER is NOT in the DGP logit formula; default rates are near-identical (F=0.0823, M=0.0806).",
            "Fairness methodology is production-pattern. Results apply only to synthetic_home_credit_like data.",
            "DI 4/5ths rule is a heuristic — not a legal or regulatory standard.",
            "Threshold (0.06) is a synthetic policy parameter, not a real credit-decision threshold.",
        ],
        "source_reference": {
            "SR-8": {"metric": "Disparate Impact", "value": 1.059, "source": "RiskFrame on real Home Credit", "status": "SOURCE_REFERENCE — not PulseGuard-built"},
            "SR-9": {"metric": "Equal Opportunity gap", "value": "<5pp", "source": "RiskFrame on real Home Credit", "status": "SOURCE_REFERENCE — not PulseGuard-built"},
        },
    }

    json_path = os.path.join(OUTPUT_DIR, "g5_fairness_report.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[fairness_audit] Report saved → {json_path} ({os.path.getsize(json_path):,} bytes)")

    plot_path = os.path.join(PLOT_DIR, "g5_score_distribution.png")
    plot_score_distribution(df_test, probs, plot_path)

    return report


if __name__ == "__main__":
    main()
