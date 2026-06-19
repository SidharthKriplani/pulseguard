# G4 — VERIFICATION REPORT
## PulseGuard · Champion Model + Drift Monitoring Kernel
## Pre-Acceptance Evidence Package

**Status:** VERIFICATION COMPLETE — PASS
**Date:** June 2026
**Verifier:** Artifact existence checks + protocol code-path trace + Bayes-ceiling re-derivation

---

## SECTION 1 — ARTIFACT EXISTENCE CHECKS

All files verified to exist on disk with non-zero byte count.

### 1.1 Implementation Files

| File | Status | Bytes | Lines |
|------|--------|-------|-------|
| `src/feature_pipeline.py` | ✓ EXISTS | 5,871 | 158 |
| `scripts/train_champion.py` | ✓ EXISTS | 17,746 | 394 |
| `scripts/seed_lifecycle.py` | ✓ EXISTS | 4,792 | 130 |
| `scripts/drift_monitor.py` | ✓ EXISTS | 13,229 | 310 |

### 1.2 Evidence JSONs

| File | Status | Bytes |
|------|--------|-------|
| `outputs/evidence/g4_champion_training_report.json` | ✓ EXISTS | 4,663 |
| `outputs/evidence/g4_calibration_report.json` | ✓ EXISTS | 1,453 |
| `outputs/evidence/g4_drift_report.json` | ✓ EXISTS | 110,360 |

### 1.3 Plots

| File | Status | Bytes |
|------|--------|-------|
| `outputs/plots/g4_calibration_curve.png` | ✓ EXISTS | 78,241 |
| `outputs/plots/g4_drift_psi_ext_source_2.png` | ✓ EXISTS | 73,615 |

### 1.4 Model Artifacts

| File | Status | Bytes |
|------|--------|-------|
| `outputs/models/champion_xgb.json` | ✓ EXISTS | 209,536 |
| `outputs/models/champion_calibrated.pkl` | ✓ EXISTS | 153,651 |
| `outputs/models/preprocessor.pkl` | ✓ EXISTS | 6,366 |

**All 13 artifacts present. No missing files.**

---

## SECTION 2 — CHAMPION MODEL EVIDENCE LEDGER (FULL METADATA)

### Ledger Row #3: Champion Model Metrics

| Field | Value |
|-------|-------|
| **Metric** | ROC-AUC, PR-AUC, Brier Score, ECE (raw and calibrated) |
| **Data tag** | `synthetic_home_credit_like` |
| **N (total)** | 50,000 rows |
| **N (train)** | 30,000 rows (60%) |
| **N (val)** | 10,000 rows (20%) |
| **N (test)** | 10,000 rows (20%) |
| **Split method** | Stratified 60/20/20, `random_state=42` |
| **Default rate train** | 0.0817 |
| **Default rate val** | 0.0817 |
| **Default rate test** | 0.0817 |
| **ROC-AUC (calibrated)** | **0.623694** |
| **PR-AUC (calibrated)** | **0.133746** |
| **Brier Score (calibrated)** | **0.073806** |
| **ECE (raw XGBoost)** | **0.011050** |
| **ECE (Platt calibrated)** | **0.001594** |
| **Bayes-optimal AUC ceiling** | **0.626057** (verified; see Section 4) |
| **Champion efficiency** | **99.62%** of Bayes ceiling |
| **Best iteration** | 9 (early_stopping_rounds=50, eval_metric=aucpr) |
| **Source file** | `scripts/train_champion.py` |
| **Artifact** | `outputs/evidence/g4_champion_training_report.json` (4,663 B) |
| **Reproducibility** | Deterministic at seed=42; re-running `python3 scripts/train_champion.py` reproduces identical split, preprocessor, and XGBoost model |
| **Uncertainty / limitation** | Synthetic DGP with 6 signal features; Bayes ceiling 0.626 is characteristic of this DGP, not a model deficiency. Real Home Credit source reference (SR-1: ROC-AUC ~0.7663) used hundreds of real-world features — the gap is a dataset characteristic, not a model shortfall. |

### Ledger Row #3: Calibration Sub-Table

| Metric | Raw XGBoost | Platt Calibrated | Note |
|--------|-------------|-----------------|------|
| ECE | 0.011050 | **0.001594** | 86% reduction |
| Brier | 0.074274 | **0.073806** | Marginal improvement |
| ROC-AUC | 0.623694 | 0.623694 | Identical — calibration is monotonic |
| PR-AUC | 0.133746 | 0.133746 | Identical — calibration is monotonic |

Calibration fit on: **validation set (10,000 rows)**.  
Calibration evaluated on: **held-out test set (10,000 rows)** — never seen during training or calibration.

---

## SECTION 3 — DRIFT MONITORING EVIDENCE LEDGER (FULL METADATA)

### Ledger Row #4: PSI Drift Results

| Field | Value |
|-------|-------|
| **Metric** | PSI (Population Stability Index) + KS statistic per feature per day |
| **Data tag** | `synthetic_home_credit_like` (daily serving batches) |
| **Reference** | Training split (30,000 rows, seed=42) |
| **N per batch** | 2,000 rows/day |
| **N total (lifecycle)** | 60,000 rows (30 days × 2,000) |
| **N monitored features** | 20 numeric features |
| **PSI bins** | 10 equal-frequency quantile bins from reference |
| **PSI WARN threshold** | > 0.10 |
| **PSI ALERT threshold** | > 0.20 |
| **Source file** | `scripts/drift_monitor.py` + `scripts/seed_lifecycle.py` |
| **Artifact** | `outputs/evidence/g4_drift_report.json` (110,360 B) |

### Ledger Row #4: Full 30-Day EXT_SOURCE_2 PSI Results

| Day | Regime | PSI | KS | Status |
|-----|--------|-----|----|--------|
| 1 | BASELINE | 0.002584 | — | OK |
| 2 | BASELINE | 0.003046 | — | OK |
| 3 | BASELINE | 0.009776 | — | OK |
| 4 | BASELINE | 0.002711 | — | OK |
| 5 | BASELINE | 0.003378 | — | OK |
| 6 | BASELINE | 0.005463 | — | OK |
| **7** | WARN_INJECTED | **0.153195** | **0.193500** | **WARN** ✓ |
| 8 | WARN_INJECTED | 0.122037 | 0.175367 | WARN ✓ |
| 9 | WARN_INJECTED | 0.133542 | 0.160167 | WARN ✓ |
| 10 | WARN_INJECTED | 0.106411 | 0.166700 | WARN ✓ |
| 11 | WARN_INJECTED | 0.113633 | 0.163667 | WARN ✓ |
| 12 | WARN_INJECTED | 0.127511 | 0.174533 | WARN ✓ |
| 13 | WARN_INJECTED | 0.148023 | 0.189967 | WARN ✓ |
| **14** | ALERT_INJECTED | **0.297411** | **0.292700** | **ALERT** ✓ |
| 15 | ALERT_INJECTED | 0.293357 | 0.300800 | ALERT ✓ |
| 16 | ALERT_INJECTED | 0.242432 | 0.276467 | ALERT ✓ |
| 17 | ALERT_INJECTED | 0.325432 | 0.306767 | ALERT ✓ |
| 18 | ALERT_INJECTED | 0.276067 | 0.274433 | ALERT ✓ |
| 19 | ALERT_INJECTED | 0.283723 | 0.291500 | ALERT ✓ |
| 20 | ALERT_INJECTED | 0.276857 | 0.285233 | ALERT ✓ |
| 21 | ALERT_INJECTED | 0.243339 | 0.284333 | ALERT ✓ |
| 22 | ALERT_INJECTED | 0.246674 | 0.287733 | ALERT ✓ |
| 23 | ALERT_INJECTED | 0.295372 | 0.284900 | ALERT ✓ |
| 24 | ALERT_INJECTED | 0.264116 | 0.292167 | ALERT ✓ |
| 25 | ALERT_INJECTED | 0.295571 | 0.298367 | ALERT ✓ |
| 26 | ALERT_INJECTED | 0.217451 | 0.252700 | ALERT ✓ |
| 27 | ALERT_INJECTED | 0.260587 | 0.284900 | ALERT ✓ |
| 28 | ALERT_INJECTED | 0.259753 | 0.290067 | ALERT ✓ |
| 29 | ALERT_INJECTED | 0.289434 | 0.278633 | ALERT ✓ |
| 30 | ALERT_INJECTED | 0.272487 | 0.280200 | ALERT ✓ |

**Classification accuracy:** 30/30 days correct (6 OK, 7 WARN, 17 ALERT — zero misclassifications)

**Reproducibility:** Deterministic at SEED_BASE=1000 (day d uses seed 1000+d). Re-running `python3 scripts/drift_monitor.py` reproduces identical PSI values.

**Uncertainty / limitation:** Univariate PSI/KS only. Multivariate joint-distribution drift can produce false OK at the day level if individual feature marginals are stable while correlations shift. Documented as G0 boundary condition (PSI multivariate blindspot). Multivariate monitoring deferred to G9.

---

## SECTION 4 — BAYES-OPTIMAL CEILING VERIFICATION

**Method:** Re-derived true DGP probability scores from the calibrated logistic formula (6 signal terms), evaluated against observed TARGET labels using ROC-AUC.

**DGP formula (confirmed from `scripts/generate_synthetic_data.py` lines 110–119):**
```
logit = -4.20703
        + 1.2 × (1 − EXT_SOURCE_2)
        + 0.9 × (1 − EXT_SOURCE_3_imputed)
        + 0.4 × (AMT_CREDIT / 1e6)
        − 0.3 × (AMT_INCOME_TOTAL / 1e5)
        + 0.7 × I(DAYS_EMPLOYED == 365243)
        + 0.3 × I(REGION_RATING_CLIENT == 3)
prob = sigmoid(logit)
```

**Verified result (n=50,000, seed=42):**

| Measure | Value |
|---------|-------|
| Default rate | 0.0817 (8.17%) ✓ |
| Bayes-optimal AUC (true DGP prob → TARGET) | **0.626057** |
| Champion XGBoost AUC (calibrated) | **0.623694** |
| Champion efficiency | **99.62%** |

The champion is within 0.002363 AUC of what is theoretically achievable with perfect knowledge of the DGP. This confirms the model is near-optimal — no further gains are possible without additional features or a fundamentally different DGP.

The source reference gap (0.7663 − 0.6237 = 0.1426) is a **dataset characteristic**, not a model deficiency. SR-1 was computed on real Home Credit data with hundreds of real-world features encoding genuine applicant behavior.

---

## SECTION 5 — PROTOCOL CHECKS

| Check | Result | Evidence |
|-------|--------|----------|
| Calibrated 8.17% default-rate synthetic dataset used | ✓ PASS | `data_splits.default_rate_train = 0.0817` in `g4_champion_training_report.json`; DGP intercept −4.20703 confirmed in `generate_synthetic_data.py` line 111 |
| Injected leakage columns excluded from training | ✓ PASS | `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` in `EXCLUDED_COLS` at `feature_pipeline.py:44`; `leakage_excluded: ["EXTERNAL_BUREAU_QUERY_RESULT__INJECTED"]` in training report |
| `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` excluded | ✓ PASS | `feature_pipeline.py:45`; `synthetic_excluded: ["EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC"]` in training report |
| Preprocessing fit only on train | ✓ PASS | `train_champion.py:134`: `build_features(df_train, fit=True)`; lines 135–136: `fit=False, preprocessor=preprocessor` for val and test |
| Validation used for calibration only — not for final metrics | ✓ PASS | `train_champion.py:169–170`: `calibrated.fit(X_val, y_val)`; `train_champion.py:175`: `evaluate(model_raw, model_cal, X_test, y_test, ...)` — test set passed for final eval |
| Test set held out for final metrics | ✓ PASS | `train_champion.py:176`: `evaluate` called with `X_test, y_test` only; val set not used in evaluate() |
| Drift Day 7 WARN and Day 14 ALERT script-generated (not hand-written) | ✓ PASS | `drift_monitor.py:295`: `report = run_drift_monitor(reference, batches)` — all 30-day results computed by `run_drift_monitor()` loop (lines 130–207); JSON keys `EXT_SOURCE_2_psi`, `EXT_SOURCE_2_status` set by code, not hardcoded |
| RiskFrame source-reference metrics not upgraded to PulseGuard-built | ✓ PASS | `g4_champion_training_report.json.source_reference_note` explicitly states: "No SOURCE_REFERENCE metric is upgraded to PulseGuard-built"; drift report `drift_note`: "All drift is SYNTHETIC/INJECTED. Not observed production telemetry." |
| No challenger trained | ✓ PASS | `no_challenger_trained: true` in `g4_champion_training_report.json`; no `challenger` script or output exists |
| No Optuna HPO | ✓ PASS | `no_optuna_hpo_run: true` in `g4_champion_training_report.json`; no optuna import in any G4 script |
| No fairness audit | ✓ PASS | `no_fairness_audit: true` in `g4_champion_training_report.json` |
| No SHAP computed | ✓ PASS | `no_shap_computed: true` in `g4_champion_training_report.json` |
| No production / real applicant / compliance claim | ✓ PASS | All JSONs tagged `data_type: "synthetic_home_credit_like"`; drift note explicitly states "Not observed production telemetry" |
| Bayes-optimal ceiling documented and verified | ✓ PASS | Ceiling 0.626057 re-derived from DGP formula (Section 4); champion efficiency = 99.62% |

**All 14 protocol checks: PASS**

---

## SECTION 6 — SOURCE-REFERENCE BOUNDARY CONFIRMATION

The following numbers remain SOURCE_REFERENCE. They have NOT been upgraded to PulseGuard-built evidence.

| # | Metric | SR Value | Source | PulseGuard Status |
|---|--------|----------|--------|------------------|
| SR-1 | Champion XGBoost ROC-AUC | ~0.7663 | RiskFrame (real Home Credit) | SOURCE_REFERENCE — not built |
| SR-2 | Champion XGBoost PR-AUC | ~0.2611 | RiskFrame (real Home Credit) | SOURCE_REFERENCE — not built |
| SR-3 | ECE (Platt calibrated) | ~0.0046 | RiskFrame | SOURCE_REFERENCE — not built |
| SR-6 | PSI Day 14 (ALERT) | ~0.2358 | RiskFrame synthetic drift | SOURCE_REFERENCE — not built |
| SR-7 | EXT_SOURCE_2 drift shift | −0.18 | RiskFrame | SOURCE_REFERENCE — not built |

The PulseGuard G4 values (ROC-AUC 0.6237, PR-AUC 0.1337, ECE 0.00159, Day 14 PSI 0.2974) are computed on `synthetic_home_credit_like` data and are distinct PulseGuard-built results. They do not replace SR-1 through SR-7; they coexist as the PulseGuard-built evidence column.

---

## SECTION 7 — KNOWN LIMITATIONS (CARRIED INTO MODEL CARD)

1. **Synthetic dataset only.** All metrics are on `synthetic_home_credit_like`. Kaggle CLI was unavailable; real Home Credit data was not downloaded. The synthetic DGP is designed to mimic the real dataset's structure and default rate but does not encode real behavioral patterns.

2. **Bayes AUC ceiling of 0.626.** The DGP has only 6 contributing signal features. The 0.62 champion AUC is near-optimal for this DGP. The gap from the RiskFrame source reference (0.77) is a dataset characteristic.

3. **Univariate drift monitoring only.** PSI and KS are computed per feature in isolation. Multivariate joint-distribution shifts can be missed. Documented as G0 boundary; deferred to G9.

4. **Calibration FutureWarning.** `CalibratedClassifierCV(cv='prefit')` is deprecated in sklearn 1.6 (will be removed in 1.8). Fix in G9: replace with `CalibratedClassifierCV(FrozenEstimator(estimator))`. Non-critical for G4 — calibration output is correct.

5. **9 XGBoost trees.** Early stopping optimizes on validation PR-AUC. The logistic DGP with 6 features has limited complexity; additional trees overfit. This is the correct regularization point for this DGP.

---

## SECTION 8 — VERDICT

**G4 verification: PASS**

All artifacts exist. All protocol checks pass. Metrics are consistent with the DGP design. Source-reference boundary is intact. Bayes-optimal ceiling is independently verified.

**G4 is ready for ACCEPT. G5 (Fairness Audit) may be opened.**
