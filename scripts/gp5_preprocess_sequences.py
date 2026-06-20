"""
Gold Pass 5 — Installment Sequence Preprocessor
=================================================
Reads installments_payments.csv (13.6M rows) and builds compact numpy
arrays for LSTM training on Colab GPU.

Outputs (saved to outputs/data/):
  inst_sequences.npy   — float32, shape (N_applicants, 50, 3)
                         channels: [days_late, payment_ratio, log_amt_instalment]
  inst_sk_ids.npy      — int32,   shape (N_applicants,)   SK_ID_CURR order
  gp5_splits.npz       — keys: train_ids, val_ids, test_ids,
                                y_train,   y_val,   y_test

Usage:
    python scripts/gp5_preprocess_sequences.py

Runtime: ~3-4 minutes on a laptop (690MB CSV, pandas chunked read).
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR  = ROOT / "data" / "home-credit-default-risk"
OUT_DIR   = ROOT / "outputs" / "data"
SPLITS_PKL = OUT_DIR / "g9a_splits.pkl"
INST_CSV  = DATA_DIR / "installments_payments.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

SEQ_LEN = 50   # last N installments per applicant

# ── 1. Load installments ───────────────────────────────────────────────────────
print("Loading installments_payments.csv …")
inst = pd.read_csv(
    INST_CSV,
    usecols=["SK_ID_CURR", "DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT",
             "AMT_INSTALMENT", "AMT_PAYMENT"],
    dtype={"SK_ID_CURR": np.int32,
           "DAYS_INSTALMENT": np.float32,
           "DAYS_ENTRY_PAYMENT": np.float32,
           "AMT_INSTALMENT": np.float32,
           "AMT_PAYMENT": np.float32},
)
print(f"  Loaded {len(inst):,} rows, {inst['SK_ID_CURR'].nunique():,} unique applicants")

# ── 2. Feature engineering per row ────────────────────────────────────────────
print("Computing per-row features …")
inst["days_late"]      = inst["DAYS_ENTRY_PAYMENT"] - inst["DAYS_INSTALMENT"]
inst["payment_ratio"]  = inst["AMT_PAYMENT"] / (inst["AMT_INSTALMENT"] + 1.0)
inst["log_amt"]        = np.log1p(inst["AMT_INSTALMENT"].clip(lower=0))

# Clip days_late to [-30, 120] — extreme outliers from missing entries
inst["days_late"] = inst["days_late"].clip(-30, 120).fillna(0).astype(np.float32)
inst["payment_ratio"] = inst["payment_ratio"].clip(0, 3).fillna(1).astype(np.float32)
inst["log_amt"]   = inst["log_amt"].fillna(0).astype(np.float32)

# ── 3. Sort by SK_ID_CURR, then DAYS_INSTALMENT (ascending) ──────────────────
print("Sorting …")
inst.sort_values(["SK_ID_CURR", "DAYS_INSTALMENT"], inplace=True)

# ── 4. Build padded sequences (vectorised groupby) ────────────────────────────
print("Building padded sequences …")

feature_cols = ["days_late", "payment_ratio", "log_amt"]
groups = inst.groupby("SK_ID_CURR", sort=False)

sk_ids_list   = []
sequences_list = []

for sk_id, grp in groups:
    arr = grp[feature_cols].values.astype(np.float32)  # (T, 3)
    # take LAST SEQ_LEN rows
    if len(arr) >= SEQ_LEN:
        seq = arr[-SEQ_LEN:]
    else:
        # left-pad with zeros
        pad = np.zeros((SEQ_LEN - len(arr), 3), dtype=np.float32)
        seq = np.concatenate([pad, arr], axis=0)        # (SEQ_LEN, 3)
    sk_ids_list.append(sk_id)
    sequences_list.append(seq)

sk_ids    = np.array(sk_ids_list, dtype=np.int32)
sequences = np.stack(sequences_list, axis=0).astype(np.float32)  # (N, 50, 3)
print(f"  sequences shape: {sequences.shape}  |  dtype: {sequences.dtype}")

# ── 5. Save sequence arrays ────────────────────────────────────────────────────
print("Saving inst_sequences.npy and inst_sk_ids.npy …")
np.save(OUT_DIR / "inst_sequences.npy", sequences)
np.save(OUT_DIR / "inst_sk_ids.npy",    sk_ids)
print(f"  inst_sequences.npy: {sequences.nbytes / 1e6:.1f} MB")

# ── 6. Extract train/val/test splits ──────────────────────────────────────────
print("Loading g9a_splits.pkl …")
with open(SPLITS_PKL, "rb") as f:
    splits = pickle.load(f)

train_ids = np.array(splits["X_train"].index, dtype=np.int32)
val_ids   = np.array(splits["X_val"].index,   dtype=np.int32)
test_ids  = np.array(splits["X_test"].index,  dtype=np.int32)
y_train   = np.array(splits["y_train"],        dtype=np.int8)
y_val     = np.array(splits["y_val"],          dtype=np.int8)
y_test    = np.array(splits["y_test"],         dtype=np.int8)

print(f"  train: {len(train_ids):,}  val: {len(val_ids):,}  test: {len(test_ids):,}")
print(f"  default rate — train: {y_train.mean():.3f}  val: {y_val.mean():.3f}  test: {y_test.mean():.3f}")

np.savez_compressed(
    OUT_DIR / "gp5_splits.npz",
    train_ids=train_ids, val_ids=val_ids, test_ids=test_ids,
    y_train=y_train,     y_val=y_val,     y_test=y_test,
)
print("Saved gp5_splits.npz")

# ── 7. Sanity check ────────────────────────────────────────────────────────────
print("\n── Sanity check ──")
# verify SK_ID coverage
seq_id_set = set(sk_ids.tolist())
missing_train = np.sum([i not in seq_id_set for i in train_ids])
print(f"  train IDs missing from sequences: {missing_train:,}  (will be zero-padded by Colab notebook)")

# quick stats on sequences
print(f"  days_late  — mean: {sequences[:,:,0].mean():.2f}  std: {sequences[:,:,0].std():.2f}")
print(f"  pay_ratio  — mean: {sequences[:,:,1].mean():.2f}  std: {sequences[:,:,1].std():.2f}")
print(f"  log_amt    — mean: {sequences[:,:,2].mean():.2f}  std: {sequences[:,:,2].std():.2f}")

print("\nDone. Files written to outputs/data/")
print("  inst_sequences.npy  (N×50×3 float32)")
print("  inst_sk_ids.npy     (N int32)")
print("  gp5_splits.npz      (train/val/test IDs + labels)")
