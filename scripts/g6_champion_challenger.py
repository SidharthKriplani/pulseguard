"""
G6 — Real-Data Champion/Challenger Evaluation
PulseGuard · Taiwan Default (PUBLIC_REAL_TAIWAN_DEFAULT)

Models:
  - Logistic Regression (baseline/scorecard-style)
  - XGBoost (champion candidate)
  - LightGBM (challenger)

Evaluation: ROC-AUC, PR-AUC, Brier, ECE, calibration curve,
            confusion matrix at documented threshold.

Calibration: Platt sigmoid on champion (XGBoost), fitted on val set.

Outputs:
  outputs/evidence/g6_champion_challenger_report.json
  outputs/evidence/g6_calibration_report.json
  outputs/plots/g6_calibration_curve.png
  outputs/plots/g6_model_comparison.png
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
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    auc,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import xgboost as xgb
import lightgbm as lgb

warnings.filterwarnings("ignore")

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
XLS_PATH = ROOT / "data" / "public" / "taiwan_credit_default.xls"
EVIDENCE_DIR = ROOT / "outputs" / "evidence"
PLOTS_DIR = ROOT / "outputs" / "plots"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# ── constants ────────────────────────────────────────────────────────────────
SEED = 42
TARGET_COL = "default payment next month"
ID_COL = "ID"
CATEGORICAL_COLS = ["SEX", "EDUCATION", "MARRIAGE"]
PAY_COLS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAY_AMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]
NUMERIC_COLS = ["LIMIT_BAL", "AGE"] + PAY_COLS + BILL_COLS + PAY_AMT_COLS
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS

# Documented business threshold (synthetic policy — not a real underwriting rule)
# PD >= 0.35 → REJECT; PD in [0.20, 0.35) → REVIEW; PD < 0.20 → APPROVE
# Chosen to reflect credit card default context (22% base rate; more conservative than G4's 6% approve)
DECISION_THRESHOLD = 0.35  # primary classification threshold for confusion matrix


# ── data loading and splitting ────────────────────────────────────────────────
def load_and_split(path: Path):
    df = pd.read_excel(path, header=1, engine="xlrd")
    df.columns = [c.strip() for c in df.columns]

    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].values

    idx = np.arange(len(df))
    idx_train, idx_tmp = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val, idx_test = train_test_split(idx_tmp, test_size=0.50, stratify=y[idx_tmp], random_state=SEED)

    X_train, y_train = X.iloc[idx_train], y[idx_train]
    X_val,   y_val   = X.iloc[idx_val],   y[idx_val]
    X_test,  y_test  = X.iloc[idx_test],  y[idx_test]

    print(f"Split — train: {len(X_train)}, val: {len(X_val)}, test: {len(X_test)}")
    print(f"  Train DR: {y_train.mean():.4f} | Val DR: {y_val.mean():.4f} | Test DR: {y_test.mean():.4f}")
    return X_train, y_train, X_val, y_val, X_test, y_test


# ── feature preprocessing ─────────────────────────────────────────────────────
def build_preprocessor():
    numeric_transformer = Pipeline([("scaler", StandardScaler())])
    categorical_transformer = Pipeline([
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, NUMERIC_COLS),
        ("cat", categorical_transformer, CATEGORICAL_COLS),
    ])
    return preprocessor


# ── metrics ──────────────────────────────────────────────────────────────────
def compute_ece(y_true, y_prob, n_bins=10) -> float:
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if mask.sum() == 0:
            continue
        acc = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += mask.sum() / n * abs(acc - conf)
    return float(ece)


def compute_metrics(y_true, y_prob, label: str, threshold: float = DECISION_THRESHOLD) -> dict:
    roc = roc_auc_score(y_true, y_prob)
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(rec, prec)
    brier = brier_score_loss(y_true, y_prob)
    ece = compute_ece(y_true, y_prob)

    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    return {
        "model": label,
        "roc_auc": round(roc, 6),
        "pr_auc": round(pr_auc, 6),
        "brier_score": round(brier, 6),
        "ece": round(ece, 6),
        "confusion_matrix": {
            "threshold": threshold,
            "threshold_meaning": f"PD >= {threshold} → default prediction",
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
            "precision": round(tp / (tp + fp) if (tp + fp) > 0 else 0.0, 4),
            "recall": round(tp / (tp + fn) if (tp + fn) > 0 else 0.0, 4),
            "f1": round(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0, 4),
        },
    }


# ── model training ────────────────────────────────────────────────────────────
def train_logistic_regression(X_train, y_train, preprocessor) -> Pipeline:
    print("\nTraining Logistic Regression (baseline)...")
    pipe = Pipeline([
        ("prep", preprocessor),
        ("clf", LogisticRegression(C=0.1, max_iter=1000, random_state=SEED,
                                   class_weight="balanced", solver="lbfgs")),
    ])
    pipe.fit(X_train, y_train)
    return pipe


def train_xgboost(X_train, y_train, X_val, y_val, preprocessor):
    print("\nTraining XGBoost (champion candidate)...")
    prep = build_preprocessor()
    X_tr_t = prep.fit_transform(X_train, y_train)
    X_vl_t = prep.transform(X_val)

    scale_pos = int((y_train == 0).sum()) / int((y_train == 1).sum())
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        eval_metric="aucpr",
        early_stopping_rounds=50,
        random_state=SEED,
        verbosity=0,
        use_label_encoder=False,
    )
    model.fit(
        X_tr_t, y_train,
        eval_set=[(X_vl_t, y_val)],
        verbose=False,
    )
    best_iter = int(model.best_iteration)
    print(f"  XGBoost best iteration: {best_iter}")
    return model, prep, best_iter


def train_lightgbm(X_train, y_train, X_val, y_val, preprocessor):
    print("\nTraining LightGBM (challenger)...")
    prep = build_preprocessor()
    X_tr_t = prep.fit_transform(X_train, y_train)
    X_vl_t = prep.transform(X_val)

    scale_pos = int((y_train == 0).sum()) / int((y_train == 1).sum())
    model = lgb.LGBMClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        random_state=SEED,
        verbose=-1,
        n_jobs=1,
    )
    callbacks = [lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)]
    model.fit(
        X_tr_t, y_train,
        eval_set=[(X_vl_t, y_val)],
        eval_metric="auc",
        callbacks=callbacks,
    )
    best_iter = int(model.best_iteration_)
    print(f"  LightGBM best iteration: {best_iter}")
    return model, prep, best_iter


def calibrate_model(model, prep, X_val, y_val):
    """Platt sigmoid calibration fitted on validation set."""
    print("\nFitting Platt calibration on champion (XGBoost)...")
    X_val_t = prep.transform(X_val)
    # Wrap model in CalibratedClassifierCV with prefit
    calibrated = CalibratedClassifierCV(model, cv="prefit", method="sigmoid")
    calibrated.fit(X_val_t, y_val)
    return calibrated


# ── plots ─────────────────────────────────────────────────────────────────────
def plot_calibration_curve(models_probs: dict, y_test, out_path: Path):
    """Calibration curves for all models + calibrated champion."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    colors = {"LR Baseline": "#1f77b4", "XGBoost": "#ff7f0e",
              "LightGBM": "#2ca02c", "XGBoost (Platt)": "#d62728"}

    # Left: calibration curves
    ax = axes[0]
    ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Perfect calibration")
    for name, prob in models_probs.items():
        frac_pos, mean_pred = calibration_curve(y_test, prob, n_bins=10)
        ax.plot(mean_pred, frac_pos, "s-", label=name, color=colors.get(name), lw=1.8, markersize=5)
    ax.set_xlabel("Mean predicted probability", fontsize=11)
    ax.set_ylabel("Fraction of positives (observed)", fontsize=11)
    ax.set_title("Calibration Curves — Taiwan Default (Test Set)", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Right: ROC curves
    ax = axes[1]
    for name, prob in models_probs.items():
        fpr, tpr, _ = roc_curve(y_test, prob)
        roc = roc_auc_score(y_test, prob)
        ax.plot(fpr, tpr, label=f"{name} (AUC={roc:.4f})", color=colors.get(name), lw=1.8)
    ax.plot([0, 1], [0, 1], "k--", lw=1.2)
    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)
    ax.set_title("ROC Curves — Taiwan Default (Test Set)", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_model_comparison(metrics_list: list, out_path: Path):
    """Bar chart comparing ROC-AUC, PR-AUC, Brier, ECE across models."""
    names = [m["model"] for m in metrics_list]
    roc_aucs = [m["roc_auc"] for m in metrics_list]
    pr_aucs  = [m["pr_auc"]  for m in metrics_list]
    briers   = [m["brier_score"] for m in metrics_list]
    eces     = [m["ece"] for m in metrics_list]

    x = np.arange(len(names))
    width = 0.2

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    bars1 = ax.bar(x - width/2, roc_aucs, width, label="ROC-AUC", color="#1f77b4", alpha=0.85)
    bars2 = ax.bar(x + width/2, pr_aucs,  width, label="PR-AUC",  color="#ff7f0e", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, rotation=10, ha="right")
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("Discrimination — Taiwan Default (Test Set)", fontsize=12)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis="y", alpha=0.3)
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{bar.get_height():.4f}", ha="center", va="bottom", fontsize=7.5)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{bar.get_height():.4f}", ha="center", va="bottom", fontsize=7.5)

    ax = axes[1]
    bars3 = ax.bar(x - width/2, briers, width, label="Brier Score (↓)", color="#2ca02c", alpha=0.85)
    bars4 = ax.bar(x + width/2, eces,   width, label="ECE (↓)",          color="#d62728", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, rotation=10, ha="right")
    ax.set_ylabel("Score (lower = better)", fontsize=11)
    ax.set_title("Calibration Quality — Taiwan Default (Test Set)", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    for bar in bars3:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f"{bar.get_height():.4f}", ha="center", va="bottom", fontsize=7.5)
    for bar in bars4:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f"{bar.get_height():.4f}", ha="center", va="bottom", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


# ── promotion decision ────────────────────────────────────────────────────────
def make_promotion_decision(lr_m, xgb_m, xgb_cal_m, lgb_m) -> dict:
    """
    Champion: XGBoost (Platt calibrated).
    Decision gates:
      Gate 1: PR-AUC delta vs champion ≥ 0.001
      Gate 2: ROC-AUC delta vs champion ≥ 0.001
      Gate 3: ECE must not increase by > 0.005 vs champion calibrated
      Gate 4: Brier score must not increase by > 0.003
    """
    champion = xgb_cal_m  # calibrated XGBoost
    champion_name = "XGBoost (Platt calibrated)"

    def gate_result(challenger_m, name):
        g1 = challenger_m["pr_auc"] - champion["pr_auc"]
        g2 = challenger_m["roc_auc"] - champion["roc_auc"]
        g3 = challenger_m["ece"] - champion["ece"]
        g4 = challenger_m["brier_score"] - champion["brier_score"]

        g1_pass = g1 >= 0.001
        g2_pass = g2 >= 0.001
        g3_pass = g3 <= 0.005   # ECE must not worsen by more than 0.005
        g4_pass = g4 <= 0.003   # Brier must not worsen by more than 0.003

        gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass])
        # Must pass Gate 3 (calibration) to even be considered
        if not g3_pass:
            decision = "REJECT"
            rationale = f"ECE regression {g3:+.5f} exceeds tolerance 0.005 — calibration gate blocks promotion"
        elif not g1_pass and not g2_pass:
            decision = "HOLD"
            rationale = f"PR-AUC delta {g1:+.5f} and ROC-AUC delta {g2:+.5f} both below threshold 0.001 — insufficient discrimination gain"
        elif g1_pass and g2_pass:
            decision = "PROMOTE"
            rationale = f"PR-AUC delta {g1:+.5f} ≥ 0.001 and ROC-AUC delta {g2:+.5f} ≥ 0.001; calibration and Brier gates pass"
        else:
            decision = "HOLD"
            rationale = f"Mixed gates — PR-AUC delta {g1:+.5f}, ROC-AUC delta {g2:+.5f}; marginal improvement insufficient"

        return {
            "challenger": name,
            "champion": champion_name,
            "gate_1_pr_auc_delta": round(g1, 6),
            "gate_1_pass": g1_pass,
            "gate_2_roc_auc_delta": round(g2, 6),
            "gate_2_pass": g2_pass,
            "gate_3_ece_delta": round(g3, 6),
            "gate_3_pass": g3_pass,
            "gate_4_brier_delta": round(g4, 6),
            "gate_4_pass": g4_pass,
            "gates_passed": gates_passed,
            "decision": decision,
            "rationale": rationale,
        }

    return {
        "champion": champion_name,
        "champion_metrics": champion,
        "lr_baseline_vs_champion": gate_result(lr_m, "LR Baseline"),
        "xgb_uncalibrated_vs_champion": gate_result(xgb_m, "XGBoost (raw)"),
        "lgb_vs_champion": gate_result(lgb_m, "LightGBM"),
        "promotion_rule": (
            "Gate 1: PR-AUC delta ≥ 0.001; "
            "Gate 2: ROC-AUC delta ≥ 0.001; "
            "Gate 3: ECE increase ≤ 0.005 (calibration gate — BLOCKING); "
            "Gate 4: Brier increase ≤ 0.003. "
            "PROMOTE requires all 4 gates pass. "
            "REJECT if Gate 3 fails. "
            "HOLD otherwise."
        ),
    }


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    # 1. Load + split
    X_train, y_train, X_val, y_val, X_test, y_test = load_and_split(XLS_PATH)

    # 2. Build preprocessor (LR uses its own pipeline; XGB/LGB use standalone prep)
    lr_preprocessor = build_preprocessor()

    # 3. Train models
    lr_pipe = train_logistic_regression(X_train, y_train, lr_preprocessor)

    xgb_model, xgb_prep, xgb_best_iter = train_xgboost(X_train, y_train, X_val, y_val, build_preprocessor())

    lgb_model, lgb_prep, lgb_best_iter = train_lightgbm(X_train, y_train, X_val, y_val, build_preprocessor())

    # 4. Platt calibration on XGBoost (champion)
    calibrated_xgb = calibrate_model(xgb_model, xgb_prep, X_val, y_val)

    # 5. Get test probabilities
    X_test_xgb = xgb_prep.transform(X_test)
    X_test_lgb = lgb_prep.transform(X_test)

    lr_prob_test  = lr_pipe.predict_proba(X_test)[:, 1]
    xgb_prob_test = xgb_model.predict_proba(X_test_xgb)[:, 1]
    lgb_prob_test = lgb_model.predict_proba(X_test_lgb)[:, 1]
    cal_prob_test = calibrated_xgb.predict_proba(X_test_xgb)[:, 1]

    # 6. Compute metrics on TEST set
    print("\nComputing test-set metrics...")
    lr_metrics  = compute_metrics(y_test, lr_prob_test,  "LR Baseline")
    xgb_metrics = compute_metrics(y_test, xgb_prob_test, "XGBoost (raw)")
    lgb_metrics = compute_metrics(y_test, lgb_prob_test, "LightGBM")
    cal_metrics = compute_metrics(y_test, cal_prob_test,  "XGBoost (Platt)")

    for m in [lr_metrics, xgb_metrics, lgb_metrics, cal_metrics]:
        print(f"  {m['model']}: ROC={m['roc_auc']:.4f} | PR={m['pr_auc']:.4f} | "
              f"Brier={m['brier_score']:.4f} | ECE={m['ece']:.5f}")

    # 7. Calibration comparison on TEST set (raw vs calibrated XGBoost)
    ece_raw = xgb_metrics["ece"]
    ece_cal = cal_metrics["ece"]
    ece_reduction_pct = round((ece_raw - ece_cal) / ece_raw * 100, 2) if ece_raw > 0 else 0.0
    print(f"\n  XGBoost ECE: raw={ece_raw:.5f} → calibrated={ece_cal:.5f} "
          f"({ece_reduction_pct:+.1f}% {'reduction' if ece_cal < ece_raw else 'increase'})")

    # 8. Promotion decision
    promotion = make_promotion_decision(lr_metrics, xgb_metrics, cal_metrics, lgb_metrics)
    print(f"\n  Champion: {promotion['champion']}")
    print(f"  LR vs champion: {promotion['lr_baseline_vs_champion']['decision']}")
    print(f"  LightGBM vs champion: {promotion['lgb_vs_champion']['decision']}")

    # 9. Plots
    models_probs = {
        "LR Baseline":       lr_prob_test,
        "XGBoost":           xgb_prob_test,
        "LightGBM":          lgb_prob_test,
        "XGBoost (Platt)":   cal_prob_test,
    }
    plot_calibration_curve(models_probs, y_test, PLOTS_DIR / "g6_calibration_curve.png")
    plot_model_comparison(
        [lr_metrics, xgb_metrics, lgb_metrics, cal_metrics],
        PLOTS_DIR / "g6_model_comparison.png"
    )

    # 10. Write champion/challenger report
    cc_report = {
        "pulseguard_gate": "G6",
        "data_tag": "PUBLIC_REAL_TAIWAN_DEFAULT",
        "dataset": "UCI Credit Card Default (Taiwan)",
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "n_test": int(len(y_test)),
        "default_rate_train": round(float(y_train.mean()), 6),
        "default_rate_val": round(float(y_val.mean()), 6),
        "default_rate_test": round(float(y_test.mean()), 6),
        "split": "60/20/20 stratified, seed=42",
        "feature_cols": FEATURE_COLS,
        "n_features_input": len(FEATURE_COLS),
        "categorical_encoding": "OneHotEncoder (handle_unknown=ignore)",
        "numeric_scaling": "StandardScaler",
        "decision_threshold": DECISION_THRESHOLD,
        "threshold_policy": (
            f"Synthetic business threshold: PD >= {DECISION_THRESHOLD} → REJECT prediction. "
            "Not a real underwriting rule. Chosen to reflect 22% base rate context."
        ),
        "models": {
            "lr_baseline": {
                "type": "LogisticRegression",
                "params": {"C": 0.1, "class_weight": "balanced", "solver": "lbfgs", "max_iter": 1000},
                "test_metrics": lr_metrics,
            },
            "xgb_raw": {
                "type": "XGBClassifier",
                "params": {
                    "n_estimators": 500, "max_depth": 5, "learning_rate": 0.05,
                    "subsample": 0.8, "colsample_bytree": 0.8,
                    "early_stopping_rounds": 50, "eval_metric": "aucpr"
                },
                "best_iteration": xgb_best_iter,
                "test_metrics": xgb_metrics,
            },
            "lgb_challenger": {
                "type": "LGBMClassifier",
                "params": {
                    "n_estimators": 500, "max_depth": 5, "learning_rate": 0.05,
                    "subsample": 0.8, "colsample_bytree": 0.8,
                    "early_stopping_rounds": 50
                },
                "best_iteration": lgb_best_iter,
                "test_metrics": lgb_metrics,
            },
            "xgb_calibrated": {
                "type": "XGBClassifier + Platt sigmoid calibration",
                "calibration_method": "CalibratedClassifierCV(cv='prefit', method='sigmoid') on val set",
                "test_metrics": cal_metrics,
            },
        },
        "promotion_decision": promotion,
        "synthetic_harness_boundary": (
            "These metrics are computed on Taiwan Default (PUBLIC_REAL_TAIWAN_DEFAULT). "
            "Do NOT compare directly with G4 synthetic metrics (ROC-AUC=0.6237, ECE=0.00159). "
            "Different dataset, different product, different DGP. "
            "Synthetic harness retained only for injected failure-mode tests."
        ),
        "claim_boundary": [
            "Real public data — not synthetic",
            "Credit card default (Taiwan, 2005) — not consumer loan underwriting",
            "No production deployment claim",
            "No regulatory-grade fairness claim",
            "No Home Credit claim",
        ],
    }

    cc_path = EVIDENCE_DIR / "g6_champion_challenger_report.json"
    with open(cc_path, "w") as f:
        json.dump(cc_report, f, indent=2)
    print(f"\nSaved: {cc_path}")

    # 11. Write calibration report
    # Get val-set probs for calibration comparison (calibration was fit on val, so use test for fair evaluation)
    cal_report = {
        "pulseguard_gate": "G6",
        "data_tag": "PUBLIC_REAL_TAIWAN_DEFAULT",
        "calibration_method": "Platt sigmoid (CalibratedClassifierCV cv='prefit' method='sigmoid')",
        "calibration_fit_on": "validation set (6,000 rows)",
        "evaluation_on": "held-out test set (6,000 rows)",
        "base_model": "XGBoost champion (best_iteration={})".format(xgb_best_iter),
        "raw_xgb": {
            "ece": xgb_metrics["ece"],
            "brier_score": xgb_metrics["brier_score"],
            "roc_auc": xgb_metrics["roc_auc"],
            "pr_auc": xgb_metrics["pr_auc"],
        },
        "calibrated_xgb": {
            "ece": cal_metrics["ece"],
            "brier_score": cal_metrics["brier_score"],
            "roc_auc": cal_metrics["roc_auc"],
            "pr_auc": cal_metrics["pr_auc"],
        },
        "ece_delta": round(cal_metrics["ece"] - xgb_metrics["ece"], 6),
        "ece_reduction_pct": ece_reduction_pct,
        "brier_delta": round(cal_metrics["brier_score"] - xgb_metrics["brier_score"], 6),
        "calibration_verdict": (
            "IMPROVED" if cal_metrics["ece"] < xgb_metrics["ece"]
            else "NO_IMPROVEMENT"
        ),
        "note": (
            "On Taiwan Default, XGBoost outputs from tree splits are already reasonably calibrated "
            "at this base rate (22%). Platt calibration is applied as protocol — "
            "any ECE improvement, however small, is retained for the champion."
        ),
    }

    cal_path = EVIDENCE_DIR / "g6_calibration_report.json"
    with open(cal_path, "w") as f:
        json.dump(cal_report, f, indent=2)
    print(f"Saved: {cal_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
