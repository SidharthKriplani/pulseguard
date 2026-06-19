# G2 — DATA CONTRACTS
## PulseGuard · Module Input/Output Schemas

**Gate:** G2 — Risk-Decision PRD and Component Map
**Status:** COMPLETE (design only)
**Date:** June 2026

> **Design-only document.** No code is written, no models are trained, no metrics are generated.
> All schemas are design specifications — not descriptions of existing files.
> Files marked DEFERRED do not exist yet. Files will be created at the indicated gate.
> "SYNTHETIC" means the field is generated programmatically, not from real data.
> "SOURCE" indicates where the field value originates.

---

## MODULE 1 — FEATURE SET INPUT

**File:** `data/application_train.csv` (Home Credit) or `data/synthetic_applicants.csv`
**Gate:** G3 (dataset confirmed or synthetic generated)
**Format:** CSV, one row per applicant

### Core Feature Schema (30-column working set)

| Column | Type | Required | Source | Notes |
|--------|------|----------|--------|-------|
| SK_ID_CURR | int64 | Required | Home Credit / Synthetic | Primary key; unique per applicant |
| TARGET | int8 | Required | Home Credit / Synthetic | 0 = repaid, 1 = defaulted; 8% base rate |
| EXT_SOURCE_2 | float64 | Required | Home Credit (public) | External credit bureau score 1; range [0,1]; higher = lower risk |
| EXT_SOURCE_3 | float64 | Optional | Home Credit (public) | External credit bureau score 2; ~50% missing; imputed with median |
| AMT_CREDIT | float64 | Required | Home Credit (public) | Total loan amount; range [45k, 4M] |
| AMT_INCOME_TOTAL | float64 | Required | Home Credit (public) | Monthly income; range [25k, 1.2M] |
| AMT_ANNUITY | float64 | Required | Home Credit (public) | Proposed monthly EMI; range [2k, 200k] |
| AMT_GOODS_PRICE | float64 | Optional | Home Credit (public) | Goods price underlying loan; ~1% missing |
| DAYS_BIRTH | int32 | Required | Home Credit (public) | Age in days (negative integer); divide by −365 for years |
| DAYS_EMPLOYED | int32 | Required | Home Credit (public) | Employment duration in days (negative) or 365243 (unemployed) |
| CODE_GENDER | str | Required | Home Credit (public) | M / F; used in fairness audit (CODE_GENDER_F indicator) |
| NAME_INCOME_TYPE | str | Required | Home Credit (public) | Working / Commercial associate / Pensioner / State servant / Unemployed |
| NAME_CONTRACT_TYPE | str | Required | Home Credit (public) | Cash loans / Revolving loans |
| NAME_EDUCATION_TYPE | str | Required | Home Credit (public) | Secondary / Higher education / Incomplete higher / Primary |
| NAME_FAMILY_STATUS | str | Required | Home Credit (public) | Married / Single / Civil marriage / Widow |
| REGION_RATING_CLIENT | int8 | Required | Home Credit (public) | {1, 2, 3}; 3 = highest risk |
| FLAG_OWN_CAR | str | Optional | Home Credit (public) | Y / N |
| FLAG_OWN_REALTY | str | Optional | Home Credit (public) | Y / N |
| REGION_POPULATION_RELATIVE | float64 | Optional | Home Credit (public) | Regional population density proxy |
| DAYS_REGISTRATION | float64 | Optional | Home Credit (public) | Days since last registration change (negative) |
| DAYS_ID_PUBLISH | int32 | Optional | Home Credit (public) | Days since ID document issued (negative) |
| CNT_CHILDREN | int32 | Required | Home Credit (public) | Number of children |
| CNT_FAM_MEMBERS | float64 | Optional | Home Credit (public) | Family size |
| DEF_30_CNT_SOCIAL_CIRCLE | float64 | Optional | Home Credit (public) | Defaults in social circle (30-day); ~3% missing |
| DEF_60_CNT_SOCIAL_CIRCLE | float64 | Optional | Home Credit (public) | Defaults in social circle (60-day); ~3% missing |
| OBS_30_CNT_SOCIAL_CIRCLE | float64 | Optional | Home Credit (public) | Observations in social circle (30-day) |
| FLAG_DOCUMENT_3 | int8 | Optional | Home Credit (public) | Document 3 provided (0/1) |
| HOUR_APPR_PROCESS_START | int8 | Optional | Home Credit (public) | Hour of day application was submitted |
| LIVE_REGION_NOT_WORK_REGION | int8 | Optional | Home Credit (public) | Lives in different region than work (0/1) |
| ORGANIZATION_TYPE | str | Optional | Home Credit (public) | Employer organization type (58 categories) |

### Synthetic Augmentation Columns (added at G3)

| Column | Type | Required | Source | Notes |
|--------|------|----------|--------|-------|
| EXISTING_OBLIGATIONS_MONTHLY | float64 | Required for FOIR | **SYNTHETIC** — generated as Uniform(0.05, 0.25) × AMT_INCOME_TOTAL | Not in Home Credit; represents existing monthly debt obligations |
| APPLICATION_DATE | datetime64 | Required for FLL temporal checks | **SYNTHETIC** — assigned as 2024-01-01 + randint(0, 365) days | No native timestamps in Home Credit |
| FEATURE_TIMESTAMP_EXT_SOURCE_2 | datetime64 | Optional | **SYNTHETIC** — = APPLICATION_DATE | Needed for FLL Check 6 |
| FEATURE_TIMESTAMP_INJECTED_LEAK | datetime64 | Optional | **SYNTHETIC** — = APPLICATION_DATE + randint(1, 30) days | Deliberately future-dated to trigger FLL Check 6 FAIL |

> ⚠️ EXISTING_OBLIGATIONS_MONTHLY is a SYNTHETIC field. It does not represent real borrower data.
> Every artifact referencing FOIR must include: "FOIR computed using synthetic existing obligations
> (5–25% of income). Not from real debt obligation data."

---

## MODULE 2 — LEAKAGE AUDIT OUTPUT

**File:** `outputs/evidence/leakage_report.json`
**Gate:** G3 (DEFERRED)
**Produced by:** `scripts/leakage_audit.py`

### Top-Level Schema

```json
{
  "audit_id": "string — UUID",
  "run_timestamp": "string — ISO 8601 datetime",
  "dataset": "string — 'home_credit' | 'synthetic'",
  "n_rows": "integer — number of training rows audited",
  "n_features": "integer — number of features audited",
  "target_column": "string — 'TARGET'",
  "overall_status": "string — 'PASS' | 'WARN' | 'FAIL'",
  "checks": "[array of CheckResult objects]",
  "summary": {
    "n_pass": "integer",
    "n_warn": "integer",
    "n_fail": "integer",
    "n_insufficient_input": "integer"
  },
  "timestamp_columns_synthetic": "boolean — true if synthetic timestamps were added",
  "pulseguard_version": "string — 'G3'"
}
```

### CheckResult Object Schema

```json
{
  "check_id": "integer — 1 through 7",
  "check_name": "string — e.g., 'TemporalAvailabilityCheck'",
  "status": "string — 'PASS' | 'WARN' | 'FAIL' | 'INSUFFICIENT_INPUT'",
  "flagged_features": "[array of strings — column names that triggered this check]",
  "details": "string — human-readable explanation",
  "is_temporal": "boolean — true for Checks 6 and 7",
  "synthetic_trigger": "boolean — true if FAIL was triggered by INJECTED_LEAK column"
}
```

### Expected Check Results (Design Target)

| Check | Expected Status | Flagged Features | Notes |
|-------|----------------|-----------------|-------|
| 1: Name heuristic | PASS or WARN | Possibly INJECTED_LEAK | INJECTED_LEAK name may trigger |
| 2: ID proxy | PASS | None | SK_ID_CURR excluded from features |
| 3: Target correlation | WARN | EXT_SOURCE_2, EXT_SOURCE_3 | High correlation expected; legitimate predictors |
| 4: Categorical proxy | PASS or WARN | CODE_GENDER, NAME_INCOME_TYPE | May warn; legitimate categorical features |
| 5: Split distribution | PASS or INSUFFICIENT_INPUT | — | INSUFFICIENT_INPUT without split_col |
| 6: Temporal availability | FAIL | FEATURE_TIMESTAMP_INJECTED_LEAK | INJECTED_LEAK timestamped after APPLICATION_DATE |
| 7: Training future date | WARN | FEATURE_TIMESTAMP_INJECTED_LEAK | Future-dated rows present |

---

## MODULE 3 — CHAMPION MODEL OUTPUT

**File:** `outputs/evidence/calibration_report.json`
**Gate:** G4 (DEFERRED)
**Produced by:** `scripts/train_champion.py`

### Schema

```json
{
  "model_id": "string — 'champion_xgb_v1'",
  "run_timestamp": "string — ISO 8601",
  "dataset": "string — 'home_credit' | 'synthetic'",
  "split": {
    "train_n": "integer",
    "val_n": "integer",
    "test_n": "integer",
    "train_default_rate": "float",
    "test_default_rate": "float",
    "stratified": true
  },
  "hyperparameters": {
    "model_type": "string — 'XGBClassifier'",
    "n_estimators": "integer",
    "max_depth": "integer",
    "learning_rate": "float",
    "subsample": "float",
    "colsample_bytree": "float",
    "optuna_trial_id": "integer",
    "n_optuna_trials": 50
  },
  "calibration": {
    "method": "string — 'platt_sigmoid'",
    "cv": "string — 'prefit'",
    "fit_on": "string — 'val_set'"
  },
  "evaluation": {
    "roc_auc": "float",
    "pr_auc": "float",
    "ece": "float",
    "brier_score": "float",
    "confusion_matrix_threshold_006": {
      "tp": "integer", "fp": "integer", "tn": "integer", "fn": "integer"
    },
    "confusion_matrix_threshold_028": {
      "tp": "integer", "fp": "integer", "tn": "integer", "fn": "integer"
    }
  },
  "held_model": {
    "model_id": "string — 'optuna_xgb_v2' (if ECE regression found)",
    "hold_reason": "string — 'ECE regressed; AUC improvement insufficient to justify'",
    "xgb_v2_roc_auc": "float",
    "xgb_v2_pr_auc": "float",
    "xgb_v2_ece": "float",
    "ece_regression_ratio": "float — xgb_v2_ece / xgb_v1_ece"
  },
  "shap": {
    "top_features": "[array of {feature: string, mean_abs_shap: float, rank: integer}]",
    "code_gender_f_rank": "integer",
    "explainer_type": "string — 'shap.Explainer (predict_proba)'"
  },
  "source_reference": {
    "roc_auc_target": 0.7663,
    "pr_auc_target": 0.2611,
    "ece_target": 0.0046,
    "note": "SOURCE_REFERENCE from RiskFrame (SR-1, SR-2, SR-3) — not PulseGuard-built"
  },
  "pulseguard_version": "string — 'G4'"
}
```

### Per-Application Scoring Output

For each application scored by the champion model:

| Field | Type | Source |
|-------|------|--------|
| SK_ID_CURR | int64 | Feature input |
| pd_score_champion | float64 | Champion model output; range [0,1] |
| pd_score_champion_uncalibrated | float64 | Raw XGBoost prediction (for comparison) |
| pd_decile | int8 | Score decile (1 = lowest risk, 10 = highest) |

---

## MODULE 4 — CHALLENGER OUTPUT

**File:** `outputs/evidence/challenger_promotion_decision.json`
**Gate:** G6 (DEFERRED)
**Produced by:** `scripts/champion_challenger_compare.py`

### Schema

```json
{
  "comparison_id": "string — UUID",
  "run_timestamp": "string — ISO 8601",
  "champion": {
    "model_id": "string — 'champion_xgb_v1'",
    "roc_auc": "float",
    "pr_auc": "float",
    "ece": "float"
  },
  "challenger": {
    "model_id": "string — 'challenger_lgbm_v1'",
    "roc_auc": "float",
    "pr_auc": "float",
    "ece": "float"
  },
  "gates": {
    "gate_1_pr_auc_delta": {
      "delta": "float",
      "threshold": 0.001,
      "result": "string — 'PASS' | 'FAIL'"
    },
    "gate_2_roc_auc_delta": {
      "delta": "float",
      "threshold": 0.001,
      "result": "string — 'PASS' | 'FAIL'"
    },
    "gate_3_ece_regression": {
      "challenger_ece": "float",
      "champion_ece": "float",
      "regression_ratio": "float",
      "threshold": 1.10,
      "result": "string — 'PASS' | 'FAIL'"
    },
    "gate_4_calibration_curve": {
      "threshold_006_divergence": "float",
      "threshold_028_divergence": "float",
      "result": "string — 'PASS' | 'FAIL'"
    },
    "gate_5_delong_test": {
      "test_statistic": "float",
      "p_value": "float",
      "threshold_p": 0.05,
      "result": "string — 'PASS' | 'FAIL'"
    }
  },
  "promotion_decision": "string — 'PROMOTED' | 'HELD'",
  "decision_reason": "string — narrative explanation of gate failures",
  "source_reference": {
    "gate_1_expected_delta": 0.0002,
    "gate_1_expected_result": "FAIL",
    "delong_p_expected": 0.07,
    "note": "SOURCE_REFERENCE from RiskFrame (SR-10, SR-11) — not PulseGuard-built"
  },
  "pulseguard_version": "string — 'G6'"
}
```

### Per-Application Shadow Score Fields

| Field | Type | Source | Used for Decision? |
|-------|------|--------|--------------------|
| pd_score_challenger | float64 | Challenger model | NO — shadow only |
| challenger_decision | str | Decision router applied to challenger score | NO — shadow only |
| challenger_agrees | bool | champion decision == challenger decision | NO — logged only |

---

## MODULE 5 — DRIFT REPORT

**File:** `outputs/evidence/drift_report.json`
**Gate:** G4 (DEFERRED)
**Produced by:** `scripts/drift_monitor.py`, `scripts/seed_lifecycle.py`

### Top-Level Schema

```json
{
  "report_id": "string — UUID",
  "run_timestamp": "string — ISO 8601",
  "n_batches": 30,
  "reference_batch": "string — 'B00 (training distribution)'",
  "lifecycle_type": "SIMULATED",
  "batches": "[array of BatchDriftRecord objects]",
  "alert_log": "[array of AlertRecord objects]",
  "retraining_triggered": "boolean",
  "retraining_trigger_batch": "integer | null",
  "pulseguard_version": "string — 'G4'"
}
```

### BatchDriftRecord Object

```json
{
  "batch_id": "string — 'B00' through 'B29'",
  "day": "integer — 0 through 29",
  "n_rows": "integer",
  "simulated_event": "string | null — e.g., 'drift_injection_day14', 'policy_change_v1.1_day12'",
  "features": {
    "<feature_name>": {
      "psi": "float",
      "ks_statistic": "float",
      "ks_p_value": "float",
      "psi_status": "string — 'STABLE' | 'WARN' | 'ALERT'",
      "mean_shift": "float — (batch mean − reference mean)"
    }
  },
  "approval_rate": "float",
  "review_rate": "float",
  "reject_rate": "float",
  "policy_version": "string — 'v1.0' | 'v1.1'"
}
```

### AlertRecord Object

```json
{
  "batch_id": "string",
  "day": "integer",
  "feature": "string",
  "psi": "float",
  "alert_type": "string — 'WARN' | 'ALERT'",
  "consecutive_alert_count": "integer",
  "retraining_recommended": "boolean"
}
```

### Expected Key Batch Values (Design Target, SIMULATED)

| Batch | Day | EXT_SOURCE_2 PSI | EXT_SOURCE_2 Status | Event |
|-------|-----|-----------------|----------------------|-------|
| B00 | 0 | 0.000 | STABLE | Reference |
| B01–B06 | 1–6 | < 0.05 | STABLE | No shift |
| B07 | 7 | ~0.11 | WARN | Early shift |
| B08–B13 | 8–13 | 0.11–0.20 | WARN | Progressive |
| B14 | 14 | ~0.23 | ALERT | Injected −0.18 shift |
| B15–B29 | 15–29 | varies | varies | Monitor |

---

## MODULE 6 — FAIRNESS REPORT

**File:** `outputs/evidence/fairness_report.json`
**Gate:** G5 (DEFERRED)
**Produced by:** `scripts/fairness_audit.py`, `scripts/shap_proxy_rank.py`

### Schema

```json
{
  "report_id": "string — UUID",
  "run_timestamp": "string — ISO 8601",
  "dataset": "string — 'home_credit' | 'synthetic'",
  "n_applicants": "integer",
  "protected_attribute": "string — 'CODE_GENDER'",
  "group_definitions": {
    "majority": "string — 'M'",
    "minority": "string — 'F'"
  },
  "approval_rates": {
    "overall": "float",
    "group_M": "float",
    "group_F": "float"
  },
  "disparate_impact": {
    "value": "float — group_F_approval / group_M_approval",
    "threshold_lower": 0.80,
    "threshold_upper": 1.25,
    "status": "string — 'PASS' | 'FAIL'"
  },
  "equal_opportunity": {
    "tpr_group_M": "float",
    "tpr_group_F": "float",
    "gap_pp": "float — |tpr_F − tpr_M| × 100",
    "threshold_warn": 5.0,
    "threshold_fail": 10.0,
    "status": "string — 'PASS' | 'WARN' | 'FAIL'"
  },
  "shap_proxy_check": {
    "code_gender_f_rank": "integer",
    "top_5_features": "[array of {feature: string, mean_abs_shap: float, rank: integer}]",
    "protected_attribute_in_top_5": "boolean",
    "status": "string — 'PASS' | 'WARN'"
  },
  "scope_caveat": "string — 'CODE_GENDER is a public dataset variable, not a regulated protected class. Methodology is production-pattern; results are dataset-specific.'",
  "source_reference": {
    "di_target": 1.059,
    "eopp_target_pp": "<5",
    "gender_shap_rank_target": 10,
    "note": "SOURCE_REFERENCE from RiskFrame (SR-8, SR-9) — not PulseGuard-built"
  },
  "pulseguard_version": "string — 'G5'"
}
```

---

## MODULE 7 — POLICY OUTPUT

**File:** `outputs/evidence/decision_simulation_report.json`
**Gate:** G7 (DEFERRED)
**Produced by:** `src/foir_engine.py`, `src/policy_gate.py`, `src/decision_router.py`

### Per-Application Policy Output Schema

| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| SK_ID_CURR | int64 | Required | Feature input | Applicant key |
| foir_recomputed | float64 | Required | Computed — (EXISTING_OBLIGATIONS_MONTHLY + AMT_ANNUITY) / AMT_INCOME_TOTAL | Always recomputed; never trusted from input |
| foir_existing_obligations_source | str | Required | Always "SYNTHETIC" | Documents that existing_obligations was generated |
| hard_rule_foir_flag | bool | Required | Rule 1 | True if FOIR > 0.65 → HARD_REJECT |
| hard_rule_ltv_flag | bool | Required | Rule 2 | True if AMT_CREDIT/AMT_GOODS_PRICE > 0.90 |
| hard_rule_income_flag | bool | Required | Rule 3 | True if AMT_INCOME_TOTAL < 15000 |
| hard_rule_age_min_flag | bool | Required | Rule 4 | True if age < 18 years |
| hard_rule_age_max_flag | bool | Required | Rule 5 | True if age > 70 years |
| hard_rule_region_flag | bool | Required | Rule 6 | True if REGION_RATING_CLIENT == 3 |
| hard_reject | bool | Required | Any of Rules 1–5 | True if any hard-reject rule fires |
| hard_reject_reason | str | Conditional | First triggered rule | "FOIR_EXCEEDED" / "LTV_EXCEEDED" / etc.; null if no hard reject |
| pd_score_champion | float64 | Conditional | Champion model; null if hard_reject = True | Calibrated PD |
| pd_score_challenger | float64 | Conditional | Challenger shadow; null if hard_reject = True | Shadow only |
| decision | str | Required | Decision router | "APPROVE" / "REVIEW" / "REJECT" / "HARD_REJECT" |
| policy_version | str | Required | Policy version log | "v1.0" / "v1.1" |
| adverse_action_code_1 | str | Conditional | SHAP; populated for REVIEW/REJECT | Top-1 reason code |
| adverse_action_code_2 | str | Conditional | SHAP; null if less than 2 | Top-2 reason code |
| adverse_action_code_3 | str | Conditional | SHAP; null if less than 3 | Top-3 reason code |
| adverse_action_shap_1 | float64 | Conditional | SHAP value for code 1 | |
| adverse_action_shap_2 | float64 | Conditional | SHAP value for code 2 | |
| adverse_action_shap_3 | float64 | Conditional | SHAP value for code 3 | |
| decision_timestamp | str | Required | System timestamp | ISO 8601 |
| batch_id | str | Required | Lifecycle batch | "B00" through "B29" |

### Approval Rate Decomposition Sub-Schema

```json
{
  "approval_rate_decomposition": {
    "batch_id": "string",
    "day": "integer",
    "actual_approval_rate": "float",
    "counterfactual_approval_rate_v1.0_thresholds": "float",
    "model_effect": "float — approval rate change attributable to PD score distribution",
    "policy_effect": "float — approval rate change attributable to threshold change",
    "dominant_driver": "string — 'model_drift' | 'policy_change' | 'mixed'"
  }
}
```

---

## MODULE 8 — AUDIT / GOVERNANCE RECORD

**File:** `outputs/evidence/audit_trail.jsonl` (one JSON object per line)
**Gate:** G7 (DEFERRED)
**Produced by:** `src/audit_logger.py`

### Per-Record Schema

```json
{
  "record_id": "string — UUID (unique per application-batch combination)",
  "SK_ID_CURR": "integer",
  "batch_id": "string",
  "day": "integer",
  "decision_timestamp": "string — ISO 8601",
  "policy_version": "string — 'v1.0' | 'v1.1'",
  "champion_model_id": "string — 'champion_xgb_v1'",
  "challenger_model_id": "string — 'challenger_lgbm_v1'",
  "foir_recomputed": "float",
  "foir_existing_obligations_source": "string — always 'SYNTHETIC'",
  "hard_reject": "boolean",
  "hard_reject_reason": "string | null",
  "pd_score_champion": "float | null",
  "pd_score_challenger": "float | null",
  "decision": "string",
  "adverse_action_codes": "[string | null, string | null, string | null]",
  "input_hash": "string — SHA-256 of (SK_ID_CURR + batch_id + feature_vector)",
  "output_hash": "string — SHA-256 of (decision + pd_score_champion + timestamp)",
  "tamper_check": "string — SHA-256 of (input_hash + output_hash)"
}
```

### Delayed Label Validation Output

**File:** `outputs/evidence/delayed_label_report.json`
**Gate:** G8 (DEFERRED)

```json
{
  "report_id": "string — UUID",
  "label_arrival_day": 30,
  "label_source": "SIMULATED — generated by same DGP as TARGET; independent of model scores",
  "deciles": [
    {
      "decile": "integer — 1 through 10",
      "n_applicants": "integer",
      "predicted_default_rate": "float — mean PD score in decile",
      "observed_default_rate": "float — actual delayed label default rate",
      "rank_order_preserved": "boolean"
    }
  ],
  "overall_rank_order_preserved": "boolean",
  "gini_coefficient": "float",
  "pulseguard_version": "string — 'G8'"
}
```

---

## MODULE 9 — EVIDENCE LEDGER RECORD

**File:** `04_EVIDENCE_LEDGER.md`
**Gate:** Running (updated at each gate close)

Each row in the evidence ledger corresponds to one or more output files from the modules above. The ledger is the governance index — it maps every claim to an artifact.

| Ledger Row | Module Output | Current Status |
|-----------|--------------|---------------|
| #1 Repo audit | `docs/G1_repo_audit.md` | HIGH (G1 complete) |
| #2 Leakage audit | Module 2 output | DEFERRED (G3) |
| #3 Champion evaluation | Module 3 output | DEFERRED (G4) |
| #4 PSI drift | Module 5 output | DEFERRED (G4) |
| #5 Fairness | Module 6 output | DEFERRED (G5) |
| #6 Optuna HPO | Module 3 held model | DEFERRED (G6) |
| #7 Challenger decision | Module 4 output | DEFERRED (G6) |
| #8 FOIR recompute | Module 7 output | DEFERRED (G7) |
| #9 Hard rule gate | Module 7 output | DEFERRED (G7) |
| #10 Policy version log | Module 7 output | DEFERRED (G7) |
| #11 SHAP rank | Module 3 SHAP section | DEFERRED (G5) |
| #12 Delayed label | Module 8 delayed label | DEFERRED (G8) |
| #13 Evidence ledger 15+ artifacts | All modules | DEFERRED (G8) |
| #14 Model card | `docs/MODEL_CARD.md` | DEFERRED (G8) |
| #15 Governance sign-off | `docs/governance_signoff.md` | DEFERRED (G8) |
