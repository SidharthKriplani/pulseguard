"""
Gold Pass 5 — Augment Features + Retrain LightGBM
==================================================
Appends 32 LSTM embedding columns (features 141–172) to X_train/val/test,
retrains LightGBM with the same GP2 hyperparameters + isotonic calibration,
and compares AUC vs the 0.7769 baseline.

Prerequisites:
  outputs/models/gp5_embeddings_train.npy   (184506, 32)
  outputs/models/gp5_embeddings_val.npy     (61502,  32)
  outputs/models/gp5_embeddings_test.npy    (61503,  32)
  outputs/models/gp5_median_embedding.npy   (32,)
  outputs/models/lstm_encoder.pt
  outputs/data/g9a_splits.pkl

Usage:
    cd "/Users/ASUS/Documents/Professional/GitHub/beastmax (5)/pulseguard"
    python3 scripts/gp5_augment_and_retrain.py
"""

import json
import os
import pickle
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score

ROOT      = Path(__file__).resolve().parent.parent
DATA_DIR  = ROOT / "outputs" / "data"
MODEL_DIR = ROOT / "outputs" / "models"

BASELINE_AUC = 0.7769

# ── 1. Load base splits ────────────────────────────────────────────────────────
print("Loading g9a_splits.pkl …")
with open(DATA_DIR / "g9a_splits.pkl", "rb") as f:
    splits = pickle.load(f)

X_train = splits["X_train"].copy()   # DataFrame (184506, 140)
X_val   = splits["X_val"].copy()
X_test  = splits["X_test"].copy()
y_train = splits["y_train"].values
y_val   = splits["y_val"].values
y_test  = splits["y_test"].values
base_features = splits["feature_names"]   # list of 140 names

print(f"  Base features: {len(base_features)}")
print(f"  train: {len(X_train):,}  val: {len(X_val):,}  test: {len(X_test):,}")

# ── 2. Load LSTM embeddings ────────────────────────────────────────────────────
print("Loading LSTM embeddings …")
emb_train  = np.load(MODEL_DIR / "gp5_embeddings_train.npy")   # (184506, 32)
emb_val    = np.load(MODEL_DIR / "gp5_embeddings_val.npy")
emb_test   = np.load(MODEL_DIR / "gp5_embeddings_test.npy")
median_emb = np.load(MODEL_DIR / "gp5_median_embedding.npy")   # (32,)

assert emb_train.shape == (len(X_train), 32), f"Shape mismatch: {emb_train.shape}"
assert emb_val.shape   == (len(X_val),   32)
assert emb_test.shape  == (len(X_test),  32)

EMB_COLS = [f"LSTM_EMB_{i}" for i in range(32)]

# ── 3. Augment DataFrames ──────────────────────────────────────────────────────
print("Augmenting feature matrices …")
emb_train_df = pd.DataFrame(emb_train, columns=EMB_COLS, index=X_train.index)
emb_val_df   = pd.DataFrame(emb_val,   columns=EMB_COLS, index=X_val.index)
emb_test_df  = pd.DataFrame(emb_test,  columns=EMB_COLS, index=X_test.index)

X_train_172 = pd.concat([X_train, emb_train_df], axis=1)
X_val_172   = pd.concat([X_val,   emb_val_df],   axis=1)
X_test_172  = pd.concat([X_test,  emb_test_df],  axis=1)

feature_names_172 = base_features + EMB_COLS
assert X_train_172.shape[1] == 172, f"Expected 172 cols, got {X_train_172.shape[1]}"
print(f"  Augmented shape: {X_train_172.shape}")

# ── 4. Monotone constraints: original 140 + 32 zeros for LSTM dims ─────────────
# GP2 champion constraints (140 values, extracted from lgb_mono_champion.txt)
MONO_140 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,
            1, 1, 1, 1, 0,-1,-1,-1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1,
            0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]
assert len(MONO_140) == 140, f"Expected 140, got {len(MONO_140)}"

MONO_172 = MONO_140 + [0] * 32   # LSTM dims unconstrained

# ── 5. GP2 champion hyperparameters (same Optuna result, seed=42) ──────────────
GP2_PARAMS = {
    "n_estimators":      279,
    "learning_rate":     0.06598254106850841,
    "num_leaves":        35,
    "max_depth":         7,
    "min_child_samples": 42,
    "subsample":         0.6260206371941118,
    "colsample_bytree":  0.9795542149013333,
    "reg_alpha":         2.9426595861790874,
    "reg_lambda":        0.26027328087893187,
    "scale_pos_weight":  11.39,
    "random_state":      42,
    "n_jobs":            -1,
    "verbose":           -1,
    "monotone_constraints": MONO_172,
}

# ── 6. Train ───────────────────────────────────────────────────────────────────
print("\nTraining LightGBM GP5 (172 features, same HP as GP2 champion) …")
model_172 = lgb.LGBMClassifier(**GP2_PARAMS)
model_172.fit(
    X_train_172, y_train,
    eval_set=[(X_val_172, y_val)],
    callbacks=[lgb.early_stopping(20, verbose=False),
               lgb.log_evaluation(50)],
)

# ── 7. Evaluate raw AUC ───────────────────────────────────────────────────────
val_probs_raw  = model_172.predict_proba(X_val_172)[:, 1]
test_probs_raw = model_172.predict_proba(X_test_172)[:, 1]

val_auc_raw  = roc_auc_score(y_val,  val_probs_raw)
test_auc_raw = roc_auc_score(y_test, test_probs_raw)
print(f"\nRaw (uncalibrated)  val  AUC: {val_auc_raw:.4f}")
print(f"Raw (uncalibrated)  test AUC: {test_auc_raw:.4f}")
print(f"Baseline GP2 champion AUC:    {BASELINE_AUC:.4f}")

# ── 8. Isotonic calibration ────────────────────────────────────────────────────
print("\nFitting isotonic calibration on val set …")
iso = IsotonicRegression(out_of_bounds="clip")
iso.fit(val_probs_raw, y_val)

val_cal  = iso.predict(val_probs_raw)
test_cal = iso.predict(test_probs_raw)

val_auc_cal  = roc_auc_score(y_val,  val_cal)
test_auc_cal = roc_auc_score(y_test, test_cal)
print(f"Calibrated  val  AUC: {val_auc_cal:.4f}")
print(f"Calibrated  test AUC: {test_auc_cal:.4f}")

# ── 9. Decision ───────────────────────────────────────────────────────────────
delta = test_auc_cal - BASELINE_AUC
print(f"\n{'='*55}")
print(f"GP5 test AUC:   {test_auc_cal:.4f}")
print(f"GP2 baseline:   {BASELINE_AUC:.4f}")
print(f"Delta:          {delta:+.4f}")

if delta > 0:
    print(f"✓ GP5 WINS by {delta:.4f} — saving new champion artifacts")
    new_champion = True
else:
    print(f"✗ GP5 does NOT beat baseline (delta={delta:.4f})")
    print("  Keeping GP2 champion. GP5 result documented honestly.")
    new_champion = False
print("="*55)

# ── 10. Save artifacts ────────────────────────────────────────────────────────
suffix = "gp5_172" if new_champion else "gp5_172_challenger"

# Native booster
booster_path = MODEL_DIR / f"lgb_{suffix}.txt"
model_172.booster_.save_model(str(booster_path))
print(f"\nSaved booster: {booster_path.name}")

# Isotonic lookup arrays (same pattern as GP2 iso_x/y)
iso_x = iso.X_thresholds_
iso_y = iso.y_thresholds_
np.save(MODEL_DIR / f"iso_x_{suffix}.npy", iso_x)
np.save(MODEL_DIR / f"iso_y_{suffix}.npy", iso_y)
print(f"Saved iso_x_{suffix}.npy  iso_y_{suffix}.npy  ({len(iso_x)} thresholds)")

# Feature medians (172 features) — base medians + median embedding for LSTM dims
print("Building feature_medians_172.json …")
with open(MODEL_DIR / "feature_medians.json") as f:
    med140 = json.load(f)

medians_172 = dict(med140["medians"])
for i, col in enumerate(EMB_COLS):
    medians_172[col] = float(median_emb[i])

feature_medians_172 = {
    "features": feature_names_172,
    "medians":  medians_172,
}
fm_path = MODEL_DIR / f"feature_medians_172.json"
with open(fm_path, "w") as f:
    json.dump(feature_medians_172, f, indent=2)
print(f"Saved {fm_path.name}  ({len(feature_names_172)} features)")

# ── 11. Results summary ───────────────────────────────────────────────────────
print("\n── GP5 Results Summary ──────────────────────────────────")
print(f"  Architecture:       LSTM(hidden=64) → Linear(32) → LightGBM(172)")
print(f"  LSTM best val AUC:  (see Colab notebook output)")
print(f"  GP5 raw  val AUC:   {val_auc_raw:.4f}")
print(f"  GP5 cal  val AUC:   {val_auc_cal:.4f}")
print(f"  GP5 cal  test AUC:  {test_auc_cal:.4f}")
print(f"  GP2 baseline:       {BASELINE_AUC:.4f}  (lgb_mono_champion.txt)")
print(f"  Delta:              {delta:+.4f}")
print(f"  Verdict:            {'NEW CHAMPION ✓' if new_champion else 'GP2 RETAINED — GP5 documented'}")
print("────────────────────────────────────────────────────────")
if new_champion:
    print(f"\nNext: update app.py to load lgb_{suffix}.txt + feature_medians_172.json")
    print("      Redeploy to Cloud Run.")
else:
    print("\nGP2 champion intact. GP5 LSTM features provided marginal or no lift.")
    print("This is a valid ML finding — document in README Gold Pass 5 section.")
