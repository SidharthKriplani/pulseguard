# PulseGuard G3 — Leakage Detection Report

| Field | Value |
|-------|-------|
| Gate | G3 |
| Run timestamp | 2026-06-16T20:32:52 |
| Dataset | synthetic_home_credit_like |
| Kaggle available | No — synthetic fallback |
| Total rows | 50,000 |
| Default rate (train) | 0.0817 |
| Overall status | **FAIL** |

## Synthetic Columns Added
- `APPLICATION_DATE` — outcome reference timestamp (SYNTHETIC)
- `FEATURE_TIMESTAMP_EXT_SOURCE_2` — == APPLICATION_DATE (PASS path; SYNTHETIC)
- `FEATURE_TIMESTAMP_INJECTED_LEAK` — APPLICATION_DATE + 1–30 days (FAIL path; SYNTHETIC)
- `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` — injected leakage feature (SYNTHETIC)
- `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` — FOIR input, 5–25% of income (SYNTHETIC, excluded from audit)

---

## FeatureLeakageLens Findings

# FeatureLeakageLens Audit Report

**Overall status:** `FAIL`

## Summary

- **rows:** 50000
- **columns:** 36
- **candidate_features_checked:** 29
- **finding_count:** 2
- **warn_count:** 1
- **fail_count:** 1
- **insufficient_input_count:** 0

## Findings

### 1. categorical_proxy_scan — `WARN` / medium
- **Feature:** `DAYS_ID_PUBLISH`
- **Detail:** Feature values have a large target-rate gap (0.667).
- **Recommendation:** Check if this categorical feature encodes post-outcome state or business-process leakage.
- **Evidence:** target_rate_gap=0.6667, threshold=0.65

### 2. temporal_availability — `FAIL` / high
- **Feature:** `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED`
- **Detail:** Feature timestamp occurs after outcome timestamp for 50000 rows.
- **Recommendation:** Do not use this feature unless the prediction-time workflow can prove availability before outcome.
- **Evidence:** future_rows=50000, checked_rows=50000

## Interpretation note

FeatureLeakageLens is an auditor. WARN and FAIL findings should be reviewed against feature availability rules before removing any column.