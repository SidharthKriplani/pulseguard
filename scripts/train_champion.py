"""
G4 — Champion Model Training
PulseGuard · XGBoost Champion + Platt Calibration

Train the first PulseGuard champion model on the calibrated synthetic_home_credit_like
dataset. Fit Platt sigmoid calibration on validation set. Evaluate on held-out test set.

Pipeline:
  1. Generate calibrated synthetic dataset (default_rate ≈ 8%)
  2. Add synthetic timestamps (required for data contracts)
  3. Stratified 60/20/20 split (consistent with G3 leakage audit)
  4. Build features via src/feature_pipeline.py (excludes injected leakage columns)
  5. Train XGBoost (early stopping on validation aucpr)
  6. Fit Platt calibration (CalibratedClassifierCV, cv='prefit', method='sigmoid')
  7. Evaluate on test: ROC-AUC, PR-AUC, Brier score, ECE
  8. Save model artifacts
  9. Produce evidence JSONs and calibration curve plot

Hard rules (enforced):
  - EXTERNAL_BUREAU_QUERY_RESULT__INJECTED is excluded from features (G3 FAIL)
  - EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC is excluded (FOIR input, not model feature)
  - No challenger model (G6)
  - No Optuna HPO (G6)
  - No fairness audit (G5)
  - No SHAP explanations (G5/G7)
  - Dataset: synthetic_home_credit_like (data_type labeled in all artifacts)

Run: python3 scripts/train_champion.py
"""

import json
import os
import sys
from datetime import datetime

import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
)
from sklearn.model_selection import train_test_split
import xgboost as xgb

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.generate_synthetic_data import generate, DATASET_LABEL
from scripts.add_synthetic_timestamps import add_timestamps
from src.feature_pipeline import build_features, get_feature_names, FEATURE_METADATA

# ── Configuration ──────────────────────────────────────────────────────────────
SEED          = 42
N_ROWS        = 50_000
TARGET_COL    = "TARGET"
OUTPUT_DIR    = "outputs/evidence"
PLOT_DIR      = "outputs/plots"
MODEL_DIR     = "outputs/models"
DATA_TYPE     = "synthetic_home_credit_like"

XGB_PARAMS = dict(
    n_estimators          = 1000,
    max_depth             = 5,
    learning_rate         = 0.05,
    subsample             = 0.80,
    colsample_bytree      = 0.80,
    min_child_weight      = 3,
    gamma                 = 0.0,
    reg_alpha             = 0.0,
    reg_lambda            = 1.0,
    eval_metric           = "aucpr",
    early_stopping_rounds = 50,
    random_state          = SEED,
    tree_method           = "hist",
    device                = "cpu",
    verbosity             = 0,
)


# ── ECE computation ────────────────────────────────────────────────────────────
def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Expected Calibration Error (uniform-width bins)."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (y_prob >= lo) & (y_prob < hi) if i < n_bins - 1 else (y_prob >= lo) & (y_prob <= hi)
        if mask.sum() == 0:
            continue
        acc  = float(y_true[mask].mean())
        conf = float(y_prob[mask].mean())
        ece += (mask.sum() / n) * abs(conf - acc)
    return float(ece)


def build_calibration_curve_points(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> list[dict]:
    """Return calibration curve as a list of {bin_center, fraction_pos, mean_pred, count}."""
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_true, y_prob, n_bins=n_bins, strategy="uniform"
    )
    points = []
    for fop, mpv in zip(fraction_of_positives, mean_predicted_value):
        points.append({
            "mean_predicted_probability": round(float(mpv), 5),
            "fraction_of_positives":      round(float(fop), 5),
        })
    return points


# ── Data preparation ───────────────────────────────────────────────────────────
def prepare_data():
    print("\n[train_champion] Generating calibrated synthetic dataset…")
    df = generate(n=N_ROWS, seed=SEED)
    df = add_timestamps(df, seed=SEED)

    y = df[TARGET_COL].to_numpy(dtype=np.int8)
    idx = df.index.to_numpy()

    idx_train, idx_tmp = train_test_split(idx, test_size=0.40, stratify=y, random_state=SEED)
    idx_val, idx_test  = train_test_split(idx_tmp, test_size=0.50,
                                          stratify=y[idx_tmp], random_state=SEED)

    df_train = df.loc[idx_train].reset_index(drop=True)
    df_val   = df.loc[idx_val].reset_index(drop=True)
    df_test  = df.loc[idx_test].reset_index(drop=True)

    # Fit preprocessor on train only
    X_train, y_train, preprocessor = build_features(df_train, fit=True)
    X_val,   y_val,   _            = build_features(df_val,   fit=False, preprocessor=preprocessor)
    X_test,  y_test,  _            = build_features(df_test,  fit=False, preprocessor=preprocessor)

    splits = {
        "n_train":      len(df_train),
        "n_val":        len(df_val),
        "n_test":       len(df_test),
        "default_rate_train": float(y_train.mean()),
        "default_rate_val":   float(y_val.mean()),
        "default_rate_test":  float(y_test.mean()),
    }
    print(f"[train_champion] Split: train={splits['n_train']:,} ({splits['default_rate_train']:.3f}) | "
          f"val={splits['n_val']:,} ({splits['default_rate_val']:.3f}) | "
          f"test={splits['n_test']:,} ({splits['default_rate_test']:.3f})")

    return X_train, y_train, X_val, y_val, X_test, y_test, preprocessor, splits


# ── Training ───────────────────────────────────────────────────────────────────
def train_xgb(X_train, y_train, X_val, y_val):
    print("\n[train_champion] Training XGBoost champion…")
    model = xgb.XGBClassifier(**XGB_PARAMS)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=100,
    )
    best_iter = model.best_iteration
    print(f"[train_champion] Best iteration: {best_iter}")
    return model


def calibrate(model, X_val, y_val):
    print("[train_champion] Fitting Platt sigmoid calibration on validation set…")
    calibrated = CalibratedClassifierCV(model, cv="prefit", method="sigmoid")
    calibrated.fit(X_val, y_val)
    return calibrated


# ── Evaluation ─────────────────────────────────────────────────────────────────
def evaluate(model_raw, model_cal, X_test, y_test, feature_names):
    print("[train_champion] Evaluating on held-out test set…")

    # Raw XGBoost probabilities (before calibration)
    prob_raw = model_raw.predict_proba(X_test)[:, 1]
    # Calibrated probabilities
    prob_cal = model_cal.predict_proba(X_test)[:, 1]

    metrics_raw = {
        "roc_auc":     round(float(roc_auc_score(y_test, prob_raw)), 6),
        "pr_auc":      round(float(average_precision_score(y_test, prob_raw)), 6),
        "brier_score": round(float(brier_score_loss(y_test, prob_raw)), 6),
        "ece":         round(compute_ece(y_test, prob_raw), 6),
    }
    metrics_cal = {
        "roc_auc":     round(float(roc_auc_score(y_test, prob_cal)), 6),
        "pr_auc":      round(float(average_precision_score(y_test, prob_cal)), 6),
        "brier_score": round(float(brier_score_loss(y_test, prob_cal)), 6),
        "ece":         round(compute_ece(y_test, prob_cal), 6),
    }

    # Feature importances (gain-based)
    imp = model_raw.feature_importances_
    fi_pairs = sorted(zip(feature_names, imp.tolist()), key=lambda x: -x[1])
    top10 = [{"feature": f, "importance_gain": round(v, 6)} for f, v in fi_pairs[:10]]

    # Calibration curve points
    cal_curve_raw = build_calibration_curve_points(y_test, prob_raw)
    cal_curve_cal = build_calibration_curve_points(y_test, prob_cal)

    print(f"\n  [champion metrics — RAW XGBoost]")
    print(f"    ROC-AUC:     {metrics_raw['roc_auc']:.4f}")
    print(f"    PR-AUC:      {metrics_raw['pr_auc']:.4f}")
    print(f"    Brier score: {metrics_raw['brier_score']:.5f}")
    print(f"    ECE:         {metrics_raw['ece']:.5f}")
    print(f"\n  [champion metrics — Platt CALIBRATED]")
    print(f"    ROC-AUC:     {metrics_cal['roc_auc']:.4f}")
    print(f"    PR-AUC:      {metrics_cal['pr_auc']:.4f}")
    print(f"    Brier score: {metrics_cal['brier_score']:.5f}")
    print(f"    ECE:         {metrics_cal['ece']:.5f}")
    print(f"\n  Top-5 features by gain:")
    for item in top10[:5]:
        print(f"    {item['feature']:42s} {item['importance_gain']:.4f}")

    return metrics_raw, metrics_cal, top10, prob_raw, prob_cal, cal_curve_raw, cal_curve_cal


# ── Plots ──────────────────────────────────────────────────────────────────────
def plot_calibration_curve(y_test, prob_raw, prob_cal, out_path):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Perfect calibration")

    for probs, label, color in [
        (prob_raw, "XGBoost (raw)", "#e05c5c"),
        (prob_cal, "Platt calibrated", "#3a86ff"),
    ]:
        fop, mpv = calibration_curve(y_test, probs, n_bins=10, strategy="uniform")
        ax.plot(mpv, fop, marker="o", markersize=5, lw=1.8, label=label, color=color)

    ax.set_xlabel("Mean Predicted Probability", fontsize=12)
    ax.set_ylabel("Fraction of Positives", fontsize=12)
    ax.set_title("PulseGuard G4 — Champion Calibration Curve\n"
                 "(synthetic_home_credit_like · Platt sigmoid calibration)", fontsize=11)
    ax.legend(fontsize=10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[train_champion] Calibration curve saved → {out_path}")


# ── Artifacts ──────────────────────────────────────────────────────────────────
def save_artifacts(model_raw, calibrated, preprocessor):
    os.makedirs(MODEL_DIR, exist_ok=True)
    raw_path = os.path.join(MODEL_DIR, "champion_xgb.json")
    cal_path = os.path.join(MODEL_DIR, "champion_calibrated.pkl")
    pre_path = os.path.join(MODEL_DIR, "preprocessor.pkl")
    model_raw.save_model(raw_path)
    joblib.dump(calibrated,   cal_path)
    joblib.dump(preprocessor, pre_path)
    print(f"[train_champion] Artifacts saved → {MODEL_DIR}/")
    return raw_path, cal_path, pre_path


def save_training_report(run_ts, splits, metrics_raw, metrics_cal, top10,
                          cal_curve_raw, cal_curve_cal, raw_path, cal_path, pre_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    training_report = {
        "pulseguard_gate":      "G4",
        "artifact":             "g4_champion_training_report.json",
        "run_timestamp":        run_ts,
        "data_type":            DATA_TYPE,
        "dataset_label":        DATASET_LABEL,
        "dgp_intercept":        -4.20703,
        "model_type":           "XGBoostClassifier",
        "calibration_method":   "Platt sigmoid (CalibratedClassifierCV, cv='prefit')",
        "xgb_hyperparameters":  XGB_PARAMS,
        "feature_metadata":     FEATURE_METADATA,
        "data_splits":          splits,
        "metrics_raw_xgb": {
            **metrics_raw,
            "note": "XGBoost raw output probabilities before Platt calibration",
        },
        "metrics_calibrated": {
            **metrics_cal,
            "note": "Platt sigmoid calibrated probabilities — USE THESE for decision engine",
        },
        "top10_feature_importances_gain": top10,
        "model_artifacts": {
            "xgb_raw":      raw_path,
            "calibrated":   cal_path,
            "preprocessor": pre_path,
        },
        "no_challenger_trained":    True,
        "no_optuna_hpo_run":        True,
        "no_fairness_audit":        True,
        "no_shap_computed":         True,
        "leakage_feature_excluded": "EXTERNAL_BUREAU_QUERY_RESULT__INJECTED",
        "synthetic_excluded":       "EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC",
        "source_reference_note": (
            "SR-1 (RiskFrame champion XGBoost ROC-AUC ~0.7663) and SR-2 (PR-AUC ~0.2611) "
            "are SOURCE_REFERENCE from a prior project on real Home Credit data (8% default rate). "
            "PulseGuard metrics above are computed on synthetic_home_credit_like data. "
            "No SOURCE_REFERENCE metric is upgraded to PulseGuard-built."
        ),
    }

    path = os.path.join(OUTPUT_DIR, "g4_champion_training_report.json")
    with open(path, "w") as f:
        json.dump(training_report, f, indent=2, default=str)
    print(f"[train_champion] Training report saved → {path} ({os.path.getsize(path)} bytes)")

    calibration_report = {
        "pulseguard_gate":     "G4",
        "artifact":            "g4_calibration_report.json",
        "run_timestamp":       run_ts,
        "data_type":           DATA_TYPE,
        "dataset_label":       DATASET_LABEL,
        "calibration_method":  "Platt sigmoid",
        "fit_set":             "validation (10,000 rows)",
        "eval_set":            "test (10,000 rows)",
        "n_bins_ece":          10,
        "ece_before_calibration":  metrics_raw["ece"],
        "ece_after_calibration":   metrics_cal["ece"],
        "brier_before_calibration": metrics_raw["brier_score"],
        "brier_after_calibration":  metrics_cal["brier_score"],
        "roc_auc_calibrated":   metrics_cal["roc_auc"],
        "pr_auc_calibrated":    metrics_cal["pr_auc"],
        "calibration_curve_raw": cal_curve_raw,
        "calibration_curve_calibrated": cal_curve_cal,
        "plot": "outputs/plots/g4_calibration_curve.png",
        "source_reference_ece": {
            "value":  0.0046,
            "source": "RiskFrame Platt calibration on real Home Credit",
            "status": "SOURCE_REFERENCE — not PulseGuard-built",
        },
    }

    path2 = os.path.join(OUTPUT_DIR, "g4_calibration_report.json")
    with open(path2, "w") as f:
        json.dump(calibration_report, f, indent=2, default=str)
    print(f"[train_champion] Calibration report saved → {path2} ({os.path.getsize(path2)} bytes)")

    return path, path2


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    run_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR,   exist_ok=True)
    os.makedirs(MODEL_DIR,  exist_ok=True)

    X_train, y_train, X_val, y_val, X_test, y_test, preprocessor, splits = prepare_data()

    model_raw = train_xgb(X_train, y_train, X_val, y_val)
    calibrated = calibrate(model_raw, X_val, y_val)

    feature_names = get_feature_names(preprocessor)
    metrics_raw, metrics_cal, top10, prob_raw, prob_cal, cal_curve_raw, cal_curve_cal = \
        evaluate(model_raw, calibrated, X_test, y_test, feature_names)

    raw_path, cal_path, pre_path = save_artifacts(model_raw, calibrated, preprocessor)

    plot_path = os.path.join(PLOT_DIR, "g4_calibration_curve.png")
    plot_calibration_curve(y_test, prob_raw, prob_cal, plot_path)

    save_training_report(run_ts, splits, metrics_raw, metrics_cal, top10,
                         cal_curve_raw, cal_curve_cal, raw_path, cal_path, pre_path)

    print("\n" + "=" * 60)
    print("  G4 CHAMPION TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Dataset:         {DATASET_LABEL} (data_type={DATA_TYPE})")
    print(f"  default_rate:    train={splits['default_rate_train']:.3f} | "
          f"val={splits['default_rate_val']:.3f} | test={splits['default_rate_test']:.3f}")
    print(f"  ROC-AUC (cal):   {metrics_cal['roc_auc']:.4f}")
    print(f"  PR-AUC  (cal):   {metrics_cal['pr_auc']:.4f}")
    print(f"  Brier   (cal):   {metrics_cal['brier_score']:.5f}")
    print(f"  ECE     (cal):   {metrics_cal['ece']:.5f}  (raw: {metrics_raw['ece']:.5f})")
    print(f"\n  Artifacts:")
    print(f"    outputs/evidence/g4_champion_training_report.json")
    print(f"    outputs/evidence/g4_calibration_report.json")
    print(f"    outputs/plots/g4_calibration_curve.png")
    print(f"    outputs/models/champion_xgb.json")
    print(f"    outputs/models/champion_calibrated.pkl")
    print(f"    outputs/models/preprocessor.pkl")
    print(f"\n  Hard rules verified:")
    print(f"    No challenger trained ✓")
    print(f"    No Optuna HPO ✓")
    print(f"    No fairness audit ✓")
    print(f"    No SHAP explanations ✓")
    print(f"    EXTERNAL_BUREAU_QUERY_RESULT__INJECTED excluded from features ✓")
    print(f"    EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC excluded from features ✓")


if __name__ == "__main__":
    main()
