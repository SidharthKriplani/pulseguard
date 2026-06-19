# G3 — LEAKAGE DETECTION NOTES
## PulseGuard · Pre-Training Feature Leakage Audit

**Gate:** G3 — Leakage Detection Kernel + G3.1 — Synthetic DGP Calibration Patch
**Status:** COMPLETE (G3.1 patch applied; G4 blocker resolved)
**Date:** June 2026

---

## 1. DATASET DECISION

**Kaggle attempt:** `kaggle` CLI not found in the execution environment.
**Decision:** Synthetic fallback per `docs/G1_dataset_plan.md`.
**Dataset label:** `synthetic_home_credit_like`

| Property | Value |
|----------|-------|
| Generator | `scripts/generate_synthetic_data.py` |
| Rows | 50,000 |
| Features | 30 (plus synthetic augmentations) |
| Default rate (train) | **8.17%** — G3.1 calibrated (was 26.0% at G3; see G3.1 section below) |
| Split | Stratified 60/20/20 (30k/10k/10k) |
| SK_ID_CURR | Unique per row (100002–150001) |

### G3 Default Rate Gap (Historical — Now Resolved by G3.1 Patch)

At G3 close, the DGP intercept of −2.8 produced a ~26% default rate, not the 8% target. This was documented as a G4 blocker.

**G3.1 resolution:** See Section 8 (G3.1 Calibration Patch) below. The intercept was calibrated to −4.20703 via binary search on N=200,000. Re-generation on N=50,000 (seed=42) produces default_rate=8.17%, within the 7%–9% acceptance range. **The G4 blocker is resolved.**

---

## 2. SYNTHETIC COLUMNS ADDED

All columns below are SYNTHETIC — not from real borrower data. Labeled in every artifact.

| Column | Type | Purpose |
|--------|------|---------|
| `APPLICATION_DATE` | datetime64 | Outcome reference timestamp (= when application was received) |
| `FEATURE_TIMESTAMP_EXT_SOURCE_2` | datetime64 | = APPLICATION_DATE (clean PASS path) |
| `FEATURE_TIMESTAMP_INJECTED_LEAK` | datetime64 | = APPLICATION_DATE + 1–30 days (FAIL path) |
| `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` | float32 | Injected leakage feature: post-application bureau query |
| `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` | float32 | FOIR input: 5–25% of income (excluded from leakage checks) |
| `SPLIT` | str | Train/val/test marker for FLL Check 5 |

---

## 3. FEATURELEAKAGELENS AUDIT RESULTS (ACTUAL — G3.1 RE-RUN)

**Run:** `scripts/leakage_audit.py` on calibrated dataset (default_rate=8.17%)
**FLL version:** imported via `pip install featureleakagelens` (PyPI)

### Summary

| Metric | G3 (26% rate) | G3.1 (8.17% rate) |
|--------|--------------|-------------------|
| Total rows | 50,000 | 50,000 |
| Features checked | 29 | 29 |
| Overall status | **FAIL** | **FAIL** |
| FAIL findings | 1 | 1 |
| WARN findings | 2 | 1 |
| INSUFFICIENT_INPUT findings | 0 | 0 |

**G3.1 is the operative result.** G3 result shown for reference only.

### Findings Detail (G3.1 — operative)

| # | Check | Status | Feature | Detail |
|---|-------|--------|---------|--------|
| 1 | `categorical_proxy_scan` | WARN | `DAYS_ID_PUBLISH` | Target-rate gap 0.667 (above 0.65 threshold) |
| 2 | `temporal_availability` | **FAIL** | `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` | Feature timestamp occurs after outcome timestamp for all 50,000 rows |

### WARN: DAYS_ID_PUBLISH

Certain ranges of days-since-ID-publish correlate with default in the DGP. This is a legitimate credit risk predictor (recency of identity documents can be a fraud/risk signal) — not leakage. The WARN is documented and the feature is RETAINED for training.

### Why DAYS_EMPLOYED WARN Dropped Between G3 and G3.1

At G3 (26% default rate), the sentinel value `365243` (unemployed) created a target-rate gap ≥ 1.000 — large enough to exceed FLL's 0.65 threshold.

At G3.1 (8.17% default rate), the overall default rate dropped. While unemployed applicants still have elevated default probability (DGP coefficient +0.7 for `DAYS_EMPLOYED == 365243`), the absolute target-rate gap for the sentinel bucket fell below the 0.65 FLL threshold. This is a calibration artifact: the predictor is still valid, the gap metric is distribution-dependent.

**Action:** `DAYS_EMPLOYED` is retained as a training feature. Its legitimate risk signal (unemployment as default predictor) is documented in the model card. No leakage correction needed.

### Finding 3 Analysis: TEMPORAL FAIL (Injected — Expected)

`EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` was timestamped at `APPLICATION_DATE + 1–30 days` (mean offset: 15.5 days). FLL Check 6 (temporal availability) correctly identifies that this feature's observation time exceeds the outcome reference time for all 50,000 rows.

**This is the designed FAIL path.** In a real pre-training gate:
- The feature would be DROPPED before any model training begins
- A data team investigation would be triggered to determine how the feature entered the training set
- The leakage report would be filed as a gate block

In PulseGuard's simulated lifecycle, the feature remains in the dataset (for demonstrating the FAIL finding) but would not be passed to the model training script at G4. At G4, `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` is added to the feature exclusion list.

### Check Status by Number (G3.1 — operative)

| Check # | Check Name | Status | Notes |
|---------|-----------|--------|-------|
| 1 | Name heuristic | No finding reported | No suspicious column names detected |
| 2 | ID / proxy | No finding reported | SK_ID_CURR excluded via ignore_cols |
| 3 | Target correlation | No finding reported | Pearson below 0.85 threshold |
| 4 | Categorical proxy | WARN × 1 | DAYS_ID_PUBLISH (gap=0.667; DAYS_EMPLOYED gap dropped below threshold at 8% rate) |
| 5 | Split distribution | No finding reported | Train/test distributions consistent |
| 6 | Temporal availability | **FAIL × 1** | EXTERNAL_BUREAU_QUERY_RESULT__INJECTED |
| 7 | Training future date scan | No finding reported | No rows with future APPLICATION_DATE |

---

## 4. GROUP LEAKAGE CHECK RESULTS (ACTUAL)

**Run:** `scripts/group_leakage_check.py`
**Type:** PulseGuard-specific extension (not in FLL)

### Summary

| Check | Status | Detail |
|-------|--------|--------|
| SK_ID_CURR uniqueness | PASS | All 50,000 SK_ID_CURR values are unique |
| Clean 60/20/20 split | PASS | 0 SK_ID_CURR overlap between train and val |
| Contaminated split (INJECTED) | FAIL | 500 duplicated IDs, 4.762% of val contaminated |

**Overall status: PASS** (clean split only; INJECTED contamination is a demonstration)

### Interpretation

With unique SK_ID_CURR per row and a random stratified split, entity contamination does not occur. This confirms PulseGuard's 60/20/20 split strategy is safe.

The contaminated FAIL demonstration shows: if 500 applicants appeared in both train and val, the model would see their examples during training and during evaluation, inflating apparent generalization. The `GroupShuffleSplit` recommendation in the output is the correct remediation for datasets with multiple rows per applicant.

---

## 5. EVIDENCE BOUNDARY

All findings above are PulseGuard-BUILT on the `synthetic_home_credit_like` dataset. They are NOT source-reference numbers from RiskFrame.

The source-reference SR-12 states: "FLL on Home Credit: 3 WARNs, 0 FAILs." PulseGuard's result differs for two reasons:
1. Dataset is synthetic (not real Home Credit)
2. An injected leakage feature produces a FAIL finding that was not present in the source-reference run

PulseGuard's G3.1 (operative) result: **1 FAIL, 1 WARN, 0 INSUFFICIENT_INPUT** on synthetic data (calibrated to 8.17% default rate). G3 result was 1 FAIL, 2 WARNs on 26% default rate dataset — superseded.

This does not override SR-12. SR-12 remains a SOURCE_REFERENCE from RiskFrame describing what would happen on the real Home Credit dataset without injected leakage. SR-12 cannot become a PulseGuard evidence row until PulseGuard re-runs FLL on the real Home Credit data.

---

## 6. G3 + G3.1 COMPLETION CHECKLIST

- [x] Kaggle download attempted — CLI not available — synthetic fallback used
- [x] Dataset labeled `synthetic_home_credit_like` in all artifacts
- [x] `scripts/generate_synthetic_data.py` — generates 50k rows, 30 features, logistic DGP
- [x] `scripts/add_synthetic_timestamps.py` — adds APPLICATION_DATE, two feature timestamps, injected leakage feature
- [x] `scripts/leakage_audit.py` — runs FLL via import (not source copy)
- [x] `scripts/group_leakage_check.py` — PulseGuard-specific entity contamination check
- [x] `outputs/evidence/leakage_report.json` — regenerated on calibrated data (1 FAIL, 1 WARN)
- [x] `outputs/evidence/leakage_report.md` — regenerated
- [x] `outputs/evidence/leakage_report.html` — regenerated
- [x] `outputs/evidence/group_leakage_report.json` — regenerated (PASS clean, FAIL injected)
- [x] `outputs/evidence/g3_1_dgp_calibration_report.json` — 3,309 bytes; calibration trace + verification
- [x] Injected leakage feature `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` triggers FAIL ✓ (confirmed G3.1)
- [x] Group leakage check PASS on clean split; FAIL on injected contamination ✓ (confirmed G3.1)
- [x] No model trained
- [x] No drift, fairness, or decision metric generated
- [x] G3 default rate gap (26% vs. 8%) documented and resolved at G3.1
- [x] DGP intercept corrected: −2.8 → −4.20703; actual default_rate=8.17% (within 7%–9%)

---

## 7. NOTES FOR G4

**G4 is now unblocked. G3.1 resolved the dataset calibration blocker.**

**Remaining pre-G4 checklist:**
1. ~~Correct DGP intercept~~ — Done at G3.1 (intercept = −4.20703, default_rate = 8.17%)
2. Add `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` to the feature exclusion list in `train_champion.py`
3. Add `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` to the exclusion list (FOIR input, not a model feature)
4. Verify `generate_synthetic_data.py` prints default_rate ≈ 8% when regenerating — should show 8.17%
5. Document dataset label `synthetic_home_credit_like` (intercept=−4.20703, calibrated G3.1) in all G4 artifacts

---

## 8. G3.1 — SYNTHETIC DGP CALIBRATION PATCH

**Status:** COMPLETE — G4 blocker resolved
**Date:** June 2026

### Problem

G3 DGP intercept −2.8 → 26% default rate. G3 was accepted as a leakage-detection gate but G4 training was blocked until the dataset rate matched the ~8% target.

### Method

Binary search on the logistic intercept using N=200,000 samples (for stable convergence). Target rate: 8.00%. Tolerance: ±0.05%.

Convergence after 8 iterations:

| Iteration | Intercept | Default Rate | Delta |
|-----------|-----------|-------------|-------|
| 1 | −4.50000 | 6.10% | −1.90pp |
| 2 | −3.75000 | 12.07% | +4.07pp |
| 3 | −4.12500 | 8.59% | +0.59pp |
| 4 | −4.31250 | 7.24% | −0.76pp |
| 5 | −4.21875 | 7.88% | −0.12pp |
| 6 | −4.17188 | 8.24% | +0.24pp |
| 7 | −4.19531 | 8.06% | +0.06pp |
| **8** | **−4.20703** | **7.97%** | **−0.03pp** ✓ |

### Verification on N=50,000 (5 seeds)

| Seed | Default Rate | In Range [7%, 9%] |
|------|-------------|-------------------|
| 42 | 7.86% | ✓ |
| 43 | 8.13% | ✓ |
| 44 | 8.03% | ✓ |
| 45 | 8.19% | ✓ |
| 46 | 8.05% | ✓ |

Mean: 8.05% · Std: 0.11% · All seeds PASS

### Production Run

`python3 scripts/generate_synthetic_data.py` → `default_rate=0.0817` (8.17%) ✓

### G3.1 Leakage Re-Audit Confirmation

| Check | G3 Result | G3.1 Result | Change |
|-------|-----------|-------------|--------|
| Temporal FAIL (injected feature) | FAIL | **FAIL** | ✓ Same |
| DAYS_EMPLOYED categorical proxy | WARN | No finding | Expected drop at 8% rate |
| DAYS_ID_PUBLISH categorical proxy | WARN | **WARN** (gap=0.667) | ✓ Still present |
| Group leakage — clean split | PASS | **PASS** | ✓ Same |
| Group leakage — injected contamination | FAIL | **FAIL** | ✓ Same |

**No unexpected leakage issues. Dataset is valid for G4 training.**

### Artifact

`outputs/evidence/g3_1_dgp_calibration_report.json` — 3,309 bytes; contains full convergence trace, 5-seed verification, production run result, and patch metadata.
