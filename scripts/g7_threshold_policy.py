"""
G7 — Threshold / Cost-Sensitive Decision Policy
PulseGuard · Taiwan Default (PUBLIC_REAL_TAIWAN_DEFAULT)

Converts calibrated XGBoost probabilities into a 3-zone business decision policy:
  APPROVE  (PD < θ_approve)
  REVIEW   (θ_approve ≤ PD < θ_reject)
  REJECT   (PD ≥ θ_reject)

Outputs:
  outputs/evidence/g7_threshold_policy_report.json
  outputs/evidence/g7_cost_sensitivity_report.json
  outputs/plots/g7_cost_curve.png
"""

import json
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import xgboost as xgb

warnings.filterwarnings("ignore")

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
XLS_PATH = ROOT / "data" / "public" / "taiwan_credit_default.xls"
EVIDENCE_DIR = ROOT / "outputs" / "evidence"
PLOTS_DIR = ROOT / "outputs" / "plots"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# ── schema constants (same as G6) ────────────────────────────────────────────
SEED = 42
TARGET_COL = "default payment next month"
ID_COL = "ID"
CATEGORICAL_COLS = ["SEX", "EDUCATION", "MARRIAGE"]
PAY_COLS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAY_AMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]
NUMERIC_COLS = ["LIMIT_BAL", "AGE"] + PAY_COLS + BILL_COLS + PAY_AMT_COLS
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS

# ── synthetic cost matrix (illustrative; NOT real lender costs) ───────────────
# Credit card context:
#   FN (False Negative = missed default = False Approval):
#     Lender approves a defaulter; loses outstanding balance.
#     Normalized to 1.0 unit.
#   FP (False Positive = missed good customer = False Rejection):
#     Lender rejects a good customer; loses net interest income over relationship.
#     Typically 8–15% annual rate on ~12 months → ~10–15% of credit limit.
#     Normalized to 0.10 (10% of false approval cost).
#   REVIEW: Manual review labor + decision delay.
#     Normalized to 0.03 (3% of false approval cost).
BASE_COST_FN = 1.00      # False Approval cost (normalized)
BASE_COST_FP = 0.10      # False Rejection opportunity cost
BASE_COST_REVIEW = 0.03  # Manual review cost per application

# Sensitivity sweep: C_FN / C_FP ratios to explore
COST_RATIOS = [5, 10, 15, 20, 30]  # how many times more costly is FN than FP


# ── data loading and splitting (identical to G6) ──────────────────────────────
def load_and_split(path: Path):
    df = pd.read_excel(path, header=1, engine="xlrd")
    df.columns = [c.strip() for c in df.columns]
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].values
    idx = np.arange(len(df))
    idx_train, idx_tmp = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val, idx_test = train_test_split(idx_tmp, test_size=0.50, stratify=y[idx_tmp], random_state=SEED)
    return (X.iloc[idx_train], y[idx_train],
            X.iloc[idx_val],   y[idx_val],
            X.iloc[idx_test],  y[idx_test])


def build_preprocessor():
    return ColumnTransformer([
        ("num", Pipeline([("scaler", StandardScaler())]), NUMERIC_COLS),
        ("cat", Pipeline([("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CATEGORICAL_COLS),
    ])


def train_champion(X_train, y_train, X_val, y_val):
    """Train XGBoost + Platt (same config as G6)."""
    prep = build_preprocessor()
    X_tr_t = prep.fit_transform(X_train, y_train)
    X_vl_t = prep.transform(X_val)
    scale_pos = int((y_train == 0).sum()) / int((y_train == 1).sum())
    model = xgb.XGBClassifier(
        n_estimators=500, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, scale_pos_weight=scale_pos,
        eval_metric="aucpr", early_stopping_rounds=50,
        random_state=SEED, verbosity=0,
    )
    model.fit(X_tr_t, y_train, eval_set=[(X_vl_t, y_val)], verbose=False)
    calibrated = CalibratedClassifierCV(model, cv="prefit", method="sigmoid")
    calibrated.fit(X_vl_t, y_val)
    return model, calibrated, prep


# ── threshold analysis ────────────────────────────────────────────────────────
def metrics_at_threshold(y_true, y_prob, threshold: float) -> dict:
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    n = len(y_true)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr       = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {
        "threshold": round(threshold, 4),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "n": n,
        "approval_rate": round((tn + fp) / n, 4),   # predicted negatives = approved
        "rejection_rate": round((tp + fn) / n, 4),  # predicted positives = rejected
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tpr": round(recall, 4),
        "fpr": round(fpr, 4),
        "youden_j": round(recall - fpr, 4),
    }


def expected_loss_single_threshold(y_true, y_prob, threshold, c_fn, c_fp) -> float:
    """Expected loss per application under single-threshold policy (no review zone)."""
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    n = len(y_true)
    return (c_fn * fn + c_fp * fp) / n


def expected_loss_three_zone(y_true, y_prob, theta_low, theta_high,
                              c_fn, c_fp, c_review) -> dict:
    """
    3-zone policy:
      PD < theta_low  → APPROVE
      theta_low ≤ PD < theta_high → REVIEW
      PD ≥ theta_high → REJECT

    Review zone: we assume manual review correctly identifies defaults
    among reviewed applicants with probability = local_default_rate.
    For a conservative bound, assume no review savings: review zone
    contributes c_review per reviewed application (labor), plus residual
    expected FN and FP from review decisions.

    Simplified model: reviewed applications → 50% approved, 50% rejected
    after manual underwriting. This is a conservative / neutral assumption.
    The c_review cost is paid for all reviewed applications regardless.
    """
    n = len(y_true)
    mask_approve = y_prob < theta_low
    mask_review  = (y_prob >= theta_low) & (y_prob < theta_high)
    mask_reject  = y_prob >= theta_high

    # Approve zone: all approved; true defaults among them = FN
    fn_approve = int(y_true[mask_approve].sum())
    fp_approve = 0  # no rejections in approve zone

    # Reject zone: all rejected; true non-defaults among them = FP
    fp_reject = int((y_true[mask_reject] == 0).sum())
    fn_reject = 0  # no approvals in reject zone

    # Review zone: assume 50/50 decision; half approved, half rejected
    n_review = int(mask_review.sum())
    y_review = y_true[mask_review]
    defaults_in_review = int(y_review.sum())
    # Approvals in review: ~50% → FN = defaults among approved half
    fn_review = int(defaults_in_review * 0.5)
    # Rejections in review: ~50% → FP = non-defaults among rejected half
    fp_review = int((n_review - defaults_in_review) * 0.5)

    total_fn = fn_approve + fn_review
    total_fp = fp_approve + fp_reject + fp_review
    total_review_cost = c_review * n_review

    el = (c_fn * total_fn + c_fp * total_fp + total_review_cost) / n

    return {
        "theta_low": round(theta_low, 3),
        "theta_high": round(theta_high, 3),
        "n_approve": int(mask_approve.sum()),
        "n_review": n_review,
        "n_reject": int(mask_reject.sum()),
        "approve_rate": round(mask_approve.sum() / n, 4),
        "review_rate": round(n_review / n, 4),
        "reject_rate": round(mask_reject.sum() / n, 4),
        "defaults_in_approve_zone": int(y_true[mask_approve].sum()),
        "defaults_in_review_zone": defaults_in_review,
        "defaults_in_reject_zone": int(y_true[mask_reject].sum()),
        "fn_total": total_fn,
        "fp_total": total_fp,
        "review_cost_total_normalized": round(total_review_cost, 6),
        "expected_loss_per_application": round(el, 6),
    }


def sweep_single_threshold(y_true, y_prob, c_fn, c_fp, thresholds):
    results = []
    for t in thresholds:
        m = metrics_at_threshold(y_true, y_prob, t)
        el = expected_loss_single_threshold(y_true, y_prob, t, c_fn, c_fp)
        m["expected_loss_per_app"] = round(el, 6)
        results.append(m)
    return results


def find_optimal_threshold(sweep_results) -> dict:
    """Find threshold with minimum expected loss."""
    best = min(sweep_results, key=lambda x: x["expected_loss_per_app"])
    return best


def find_youden_threshold(sweep_results) -> dict:
    """Find threshold maximizing Youden J = TPR - FPR."""
    best = max(sweep_results, key=lambda x: x["youden_j"])
    return best


def find_f1_threshold(sweep_results) -> dict:
    best = max(sweep_results, key=lambda x: x["f1"])
    return best


# ── plotting ──────────────────────────────────────────────────────────────────
def plot_cost_curve(sweep_results_cal, sweep_results_raw,
                    youden_t, el_opt_t, f1_t,
                    c_fn, c_fp, out_path: Path):
    thresholds = [r["threshold"] for r in sweep_results_cal]
    el_cal = [r["expected_loss_per_app"] for r in sweep_results_cal]
    el_raw = [r["expected_loss_per_app"] for r in sweep_results_raw]
    prec_cal  = [r["precision"] for r in sweep_results_cal]
    recall_cal = [r["recall"] for r in sweep_results_cal]
    f1_cal = [r["f1"] for r in sweep_results_cal]
    approval_cal = [r["approval_rate"] for r in sweep_results_cal]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(
        f"G7 — Cost-Sensitive Threshold Analysis\nTaiwan Default · XGBoost (Platt) Champion · "
        f"C_FN={c_fn}, C_FP={c_fp}",
        fontsize=12, fontweight="bold"
    )

    # Top-left: Expected loss vs threshold (calibrated vs raw)
    ax = axes[0, 0]
    ax.plot(thresholds, el_cal, "b-", lw=2, label="Calibrated XGBoost (champion)")
    ax.plot(thresholds, el_raw, "r--", lw=1.5, alpha=0.7, label="Raw XGBoost (uncalibrated)")
    ax.axvline(el_opt_t["threshold"], color="blue", lw=1.2, ls=":", label=f"Min EL θ={el_opt_t['threshold']}")
    ax.axvline(youden_t["threshold"], color="green", lw=1.2, ls=":", label=f"Youden J θ={youden_t['threshold']}")
    ax.set_xlabel("Threshold (θ)")
    ax.set_ylabel("Expected Loss per Application (normalized)")
    ax.set_title("Expected Loss vs Threshold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Top-right: Precision, Recall, F1 vs threshold
    ax = axes[0, 1]
    ax.plot(thresholds, prec_cal, "b-", lw=1.8, label="Precision")
    ax.plot(thresholds, recall_cal, "r-", lw=1.8, label="Recall (TPR)")
    ax.plot(thresholds, f1_cal, "g-", lw=1.8, label="F1")
    ax.axvline(f1_t["threshold"], color="green", lw=1.2, ls=":", label=f"Max F1 θ={f1_t['threshold']}")
    ax.axvline(el_opt_t["threshold"], color="purple", lw=1.2, ls=":", label=f"Min EL θ={el_opt_t['threshold']}")
    ax.set_xlabel("Threshold (θ)")
    ax.set_ylabel("Score")
    ax.set_title("Precision / Recall / F1 vs Threshold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Bottom-left: Approval rate vs threshold
    ax = axes[1, 0]
    ax.plot(thresholds, approval_cal, "darkorange", lw=2)
    ax.axvline(el_opt_t["threshold"], color="blue", lw=1.2, ls=":", label=f"Min EL θ={el_opt_t['threshold']}")
    ax.axhline(1 - 0.2212, color="gray", lw=1, ls="--", label="True approval rate (77.9%)")
    ax.set_xlabel("Threshold (θ)")
    ax.set_ylabel("Approval Rate")
    ax.set_title("Approval Rate vs Threshold (Calibrated XGBoost)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)

    # Bottom-right: Calibrated vs raw EL difference
    ax = axes[1, 1]
    el_diff = [raw - cal for raw, cal in zip(el_raw, el_cal)]
    ax.fill_between(thresholds, 0, el_diff, alpha=0.4, color="blue",
                    label="EL reduction from calibration (raw − calibrated)")
    ax.plot(thresholds, el_diff, "b-", lw=1.5)
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(el_opt_t["threshold"], color="blue", lw=1.2, ls=":", label=f"Min EL θ={el_opt_t['threshold']}")
    ax.set_xlabel("Threshold (θ)")
    ax.set_ylabel("Expected Loss Difference (per application)")
    ax.set_title("Benefit of Calibration for Threshold Decisions\n(positive = calibrated saves cost)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print("Loading and splitting Taiwan Default...")
    X_train, y_train, X_val, y_val, X_test, y_test = load_and_split(XLS_PATH)

    print("Training champion (XGBoost + Platt, same as G6)...")
    xgb_raw, xgb_cal, prep = train_champion(X_train, y_train, X_val, y_val)
    X_test_t = prep.transform(X_test)
    prob_cal = xgb_cal.predict_proba(X_test_t)[:, 1]
    prob_raw = xgb_raw.predict_proba(X_test_t)[:, 1]
    print(f"Test set: {len(y_test)} rows | Default rate: {y_test.mean():.4f}")

    # Threshold sweep
    thresholds = np.round(np.arange(0.05, 0.80, 0.01), 3).tolist()

    print("Sweeping thresholds (calibrated)...")
    sweep_cal = sweep_single_threshold(y_test, prob_cal, BASE_COST_FN, BASE_COST_FP, thresholds)
    print("Sweeping thresholds (raw)...")
    sweep_raw = sweep_single_threshold(y_test, prob_raw, BASE_COST_FN, BASE_COST_FP, thresholds)

    # Optimal thresholds
    el_opt   = find_optimal_threshold(sweep_cal)
    youden_t = find_youden_threshold(sweep_cal)
    f1_t     = find_f1_threshold(sweep_cal)

    print(f"\nOptimal thresholds (calibrated XGBoost):")
    print(f"  Min expected loss: θ={el_opt['threshold']}  EL={el_opt['expected_loss_per_app']:.5f}  "
          f"Approval rate={el_opt['approval_rate']:.3f}")
    print(f"  Max Youden J:      θ={youden_t['threshold']}  J={youden_t['youden_j']:.4f}  "
          f"TPR={youden_t['tpr']:.3f}  FPR={youden_t['fpr']:.3f}")
    print(f"  Max F1:            θ={f1_t['threshold']}  F1={f1_t['f1']:.4f}  "
          f"Precision={f1_t['precision']:.3f}  Recall={f1_t['recall']:.3f}")

    # Key business thresholds for policy comparison
    policy_thresholds = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    policy_comparison = []
    for t in policy_thresholds:
        m = metrics_at_threshold(y_test, prob_cal, t)
        m["expected_loss_per_app"] = round(
            expected_loss_single_threshold(y_test, prob_cal, t, BASE_COST_FN, BASE_COST_FP), 6
        )
        policy_comparison.append(m)

    # 3-zone policy analysis (θ_approve=0.20, θ_reject=0.35 as primary policy)
    # Also compare θ_approve=el_opt/θ_reject=el_opt+0.15
    three_zone_primary = expected_loss_three_zone(
        y_test, prob_cal,
        theta_low=0.20, theta_high=0.40,
        c_fn=BASE_COST_FN, c_fp=BASE_COST_FP, c_review=BASE_COST_REVIEW
    )
    three_zone_conservative = expected_loss_three_zone(
        y_test, prob_cal,
        theta_low=0.15, theta_high=0.35,
        c_fn=BASE_COST_FN, c_fp=BASE_COST_FP, c_review=BASE_COST_REVIEW
    )
    three_zone_aggressive = expected_loss_three_zone(
        y_test, prob_cal,
        theta_low=0.25, theta_high=0.50,
        c_fn=BASE_COST_FN, c_fp=BASE_COST_FP, c_review=BASE_COST_REVIEW
    )
    print(f"\n3-zone policies:")
    print(f"  Primary    (0.20/0.40): approve={three_zone_primary['approve_rate']:.2f} "
          f"review={three_zone_primary['review_rate']:.2f} reject={three_zone_primary['reject_rate']:.2f} "
          f"EL={three_zone_primary['expected_loss_per_application']:.5f}")
    print(f"  Conservative (0.15/0.35): approve={three_zone_conservative['approve_rate']:.2f} "
          f"review={three_zone_conservative['review_rate']:.2f} reject={three_zone_conservative['reject_rate']:.2f} "
          f"EL={three_zone_conservative['expected_loss_per_application']:.5f}")
    print(f"  Aggressive  (0.25/0.50): approve={three_zone_aggressive['approve_rate']:.2f} "
          f"review={three_zone_aggressive['review_rate']:.2f} reject={three_zone_aggressive['reject_rate']:.2f} "
          f"EL={three_zone_aggressive['expected_loss_per_application']:.5f}")

    # Cost sensitivity analysis: vary C_FN/C_FP ratio
    print("\nCost sensitivity sweep...")
    sensitivity_results = []
    for ratio in COST_RATIOS:
        c_fn = float(ratio)
        c_fp = 1.0
        sweep_r = sweep_single_threshold(y_test, prob_cal, c_fn, c_fp, thresholds)
        opt_r = find_optimal_threshold(sweep_r)
        opt_r["cost_ratio_fn_fp"] = ratio
        opt_r["c_fn"] = c_fn
        opt_r["c_fp"] = c_fp
        sensitivity_results.append(opt_r)
        print(f"  Ratio C_FN/C_FP={ratio:2d}: opt θ={opt_r['threshold']}  "
              f"approval={opt_r['approval_rate']:.3f}  EL={opt_r['expected_loss_per_app']:.5f}")

    # Calibrated vs raw expected loss at base cost (θ=0.35, G6 threshold)
    el_cal_35 = expected_loss_single_threshold(y_test, prob_cal, 0.35, BASE_COST_FN, BASE_COST_FP)
    el_raw_35 = expected_loss_single_threshold(y_test, prob_raw, 0.35, BASE_COST_FN, BASE_COST_FP)
    el_cal_opt_th = expected_loss_single_threshold(y_test, prob_cal, el_opt["threshold"], BASE_COST_FN, BASE_COST_FP)
    el_raw_opt_th = expected_loss_single_threshold(y_test, prob_raw, el_opt["threshold"], BASE_COST_FN, BASE_COST_FP)

    # Decision card
    chosen_policy = "three_zone_primary"  # θ_approve=0.20, θ_reject=0.40
    chosen_theta_low = 0.20
    chosen_theta_high = 0.40

    # Plot
    plot_cost_curve(sweep_cal, sweep_raw, youden_t, el_opt, f1_t,
                    BASE_COST_FN, BASE_COST_FP,
                    PLOTS_DIR / "g7_cost_curve.png")

    # Threshold policy report
    policy_report = {
        "pulseguard_gate": "G7",
        "data_tag": "PUBLIC_REAL_TAIWAN_DEFAULT",
        "model": "XGBoost (Platt calibrated) — G6 champion",
        "test_set_n": int(len(y_test)),
        "test_default_rate": round(float(y_test.mean()), 6),

        "cost_matrix": {
            "description": "Synthetic/illustrative cost assumptions — NOT real lender economics",
            "c_fn_false_approval": BASE_COST_FN,
            "c_fp_false_rejection": BASE_COST_FP,
            "c_review_per_application": BASE_COST_REVIEW,
            "ratio_fn_fp": BASE_COST_FN / BASE_COST_FP,
            "cost_fn_interpretation": "Lender approves a defaulter → loses outstanding balance (normalized to 1.0)",
            "cost_fp_interpretation": "Lender rejects a good customer → loses ~10% of credit limit in net interest income (normalized to 0.10)",
            "cost_review_interpretation": "Manual review labor + decision delay per application (normalized to 0.03)",
        },

        "threshold_candidates": {
            "min_expected_loss": el_opt,
            "max_youden_j": youden_t,
            "max_f1": f1_t,
        },

        "policy_comparison_table": policy_comparison,

        "three_zone_policies": {
            "primary_020_040": three_zone_primary,
            "conservative_015_035": three_zone_conservative,
            "aggressive_025_050": three_zone_aggressive,
        },

        "chosen_policy": {
            "name": "three_zone_primary",
            "theta_approve": chosen_theta_low,
            "theta_reject": chosen_theta_high,
            "zones": {
                "APPROVE":  f"PD < {chosen_theta_low} — predicted probability of default below 20%",
                "REVIEW":   f"{chosen_theta_low} ≤ PD < {chosen_theta_high} — borderline; manual underwriting recommended",
                "REJECT":   f"PD ≥ {chosen_theta_high} — predicted probability of default above 40%",
            },
            "zone_rates": {
                "approve_rate": three_zone_primary["approve_rate"],
                "review_rate": three_zone_primary["review_rate"],
                "reject_rate": three_zone_primary["reject_rate"],
            },
            "expected_loss_per_app": three_zone_primary["expected_loss_per_application"],
            "rationale": (
                "θ_approve=0.20 and θ_reject=0.40 creates a balanced 3-zone policy. "
                "The approve band captures the majority of good applicants with PD below 20%. "
                "The review band (20–40%) captures borderline applicants for human judgment. "
                "The reject band (PD≥40%) hard-rejects the highest-risk applicants. "
                "This policy balances expected loss minimization against operational review burden."
            ),
        },

        "calibration_aware_decisioning": {
            "raw_xgb_el_at_threshold_035": round(el_raw_35, 6),
            "calibrated_xgb_el_at_threshold_035": round(el_cal_35, 6),
            "el_difference_at_035": round(el_raw_35 - el_cal_35, 6),
            "raw_xgb_el_at_optimal_threshold": round(el_raw_opt_th, 6),
            "calibrated_xgb_el_at_optimal_threshold": round(el_cal_opt_th, 6),
            "el_difference_at_optimal": round(el_raw_opt_th - el_cal_opt_th, 6),
            "interpretation": (
                "Raw XGBoost probabilities are systematically compressed/biased (ECE=0.208). "
                "Setting a threshold on raw probabilities gives inconsistent expected-loss behavior: "
                "the model 'says' PD=0.35 but the true expected default rate for those applicants may differ. "
                "Calibrated probabilities (ECE=0.011) have a direct expected-loss interpretation: "
                "approving a cohort with PD=0.20 means we expect 20% of them to default. "
                "Threshold policy on calibrated probabilities is therefore more defensible and predictable."
            ),
        },

        "decision_card": {
            "model": "XGBoost (Platt calibrated) — trained on PUBLIC_REAL_TAIWAN_DEFAULT",
            "champion_selected_at_gate": "G6",
            "threshold_selected_at_gate": "G7",
            "policy_version": "synthetic_v1.0",
            "theta_approve": chosen_theta_low,
            "theta_reject": chosen_theta_high,
            "approve_zone": f"PD < {chosen_theta_low}",
            "review_zone": f"{chosen_theta_low} ≤ PD < {chosen_theta_high}",
            "reject_zone": f"PD ≥ {chosen_theta_high}",
            "business_owner": "SYNTHETIC_PORTFOLIO_OWNER",
            "decision_cadence": "Per-application (batch or real-time)",
            "cost_assumption": f"C_FN={BASE_COST_FN}, C_FP={BASE_COST_FP}, C_review={BASE_COST_REVIEW}",
            "risk_if_wrong": {
                "threshold_too_low": "Too many defaulters approved; bad-debt losses increase",
                "threshold_too_high": "Too many good customers rejected; revenue opportunity lost; potential fair-lending review if rejection rates are demographically skewed",
                "miscalibration": "If model loses calibration over time, threshold no longer corresponds to stated default probability — PSI drift monitor (G4 protocol) should trigger recalibration",
            },
            "manual_review_policy": (
                "Applications in REVIEW zone (20–40% PD) are escalated to manual underwriting. "
                "Manual reviewer examines payment history pattern (PAY_0 through PAY_6), "
                "credit utilization (BILL_AMT vs LIMIT_BAL), and recent payment amounts. "
                "Reviewer makes binary APPROVE/REJECT decision overriding model. "
                "All review decisions are logged for future label validation."
            ),
            "fallback_policy": "If model score is unavailable, apply hard credit limit rule: APPROVE if LIMIT_BAL ≥ NT$50,000 AND PAY_0 ≤ 0 (no current delinquency); else REVIEW.",
            "retraining_trigger": "If PSI > 0.20 on any payment status feature (PAY_0, PAY_2) OR if observed default rate in approved cohort exceeds 25% (calibration drift), retrain champion.",
            "hard_rules": [
                "No compliance claim",
                "No regulatory-grade decisioning claim",
                "No real applicant claim",
                "No adverse-action notice — this is a portfolio simulation",
                "No FOIR routing — credit card context; FOIR not applicable to Taiwan Default",
                "No governance sign-off yet — that is G8",
            ],
        },

        "claim_boundary": {
            "safe": "PulseGuard G7 converts calibrated default probabilities into a transparent synthetic business threshold policy with explicit false-approval, false-rejection, and manual-review tradeoffs.",
            "unsafe": "PulseGuard can now make production lending decisions.",
        },
    }

    pol_path = EVIDENCE_DIR / "g7_threshold_policy_report.json"
    with open(pol_path, "w") as f:
        json.dump(policy_report, f, indent=2)
    print(f"\nSaved: {pol_path}")

    # Cost sensitivity report
    sens_report = {
        "pulseguard_gate": "G7",
        "data_tag": "PUBLIC_REAL_TAIWAN_DEFAULT",
        "model": "XGBoost (Platt calibrated)",
        "analysis_type": "cost_sensitivity_sweep",
        "description": (
            "Sensitivity of optimal threshold to C_FN/C_FP ratio. "
            "As false-approval cost rises relative to false-rejection, "
            "the optimal threshold falls (model becomes more conservative — rejects more applicants). "
            "This documents the business risk of cost assumption errors."
        ),
        "cost_ratios_tested": COST_RATIOS,
        "c_fp_fixed_at": 1.0,
        "results": sensitivity_results,
        "interpretation": {
            "threshold_sensitivity": "As C_FN/C_FP ratio increases from 5 to 30, optimal threshold decreases — model becomes more rejection-conservative to avoid costly defaults.",
            "approval_rate_sensitivity": "Higher cost ratio → lower approval rate. Decision-maker must choose cost ratio explicitly; 'neutral' ratio does not exist.",
            "implication": "Threshold is not a model parameter — it is a business policy decision that encodes the lender's risk appetite. PulseGuard documents this dependency transparently.",
        },
        "full_sweep_calibrated": [{"threshold": r["threshold"], "expected_loss": r["expected_loss_per_app"],
                                    "approval_rate": r["approval_rate"], "f1": r["f1"],
                                    "tpr": r["tpr"], "fpr": r["fpr"]}
                                   for r in sweep_cal],
    }

    sens_path = EVIDENCE_DIR / "g7_cost_sensitivity_report.json"
    with open(sens_path, "w") as f:
        json.dump(sens_report, f, indent=2)
    print(f"Saved: {sens_path}")

    # Print decision card summary
    dc = policy_report["decision_card"]
    print(f"\n{'='*60}")
    print("DECISION CARD — G7 THRESHOLD POLICY")
    print(f"{'='*60}")
    print(f"  Model:         {dc['model']}")
    print(f"  Policy:        {dc['policy_version']}")
    print(f"  APPROVE zone:  {dc['approve_zone']}  ({three_zone_primary['approve_rate']*100:.1f}% of applicants)")
    print(f"  REVIEW zone:   {dc['review_zone']}   ({three_zone_primary['review_rate']*100:.1f}% of applicants)")
    print(f"  REJECT zone:   {dc['reject_zone']}   ({three_zone_primary['reject_rate']*100:.1f}% of applicants)")
    print(f"  Expected loss: {three_zone_primary['expected_loss_per_application']:.5f} per application")
    print(f"  Cost matrix:   C_FN={BASE_COST_FN}, C_FP={BASE_COST_FP}, C_review={BASE_COST_REVIEW}")
    print(f"  Retraining:    PSI>0.20 on PAY_0/PAY_2 OR observed DR>25% in approve cohort")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
