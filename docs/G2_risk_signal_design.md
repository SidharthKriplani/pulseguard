# G2 — RISK SIGNAL DESIGN
## PulseGuard · Risk Signal Layer Specification

**Gate:** G2 — Risk-Decision PRD and Component Map
**Status:** COMPLETE (design only)
**Date:** June 2026

> **Design-only document.** No signals have been computed. All values labeled SOURCE_REFERENCE
> are from prior source projects (RiskFrame) and are not PulseGuard-built.
> All values labeled DESIGN TARGET are expected output ranges to guide implementation.
> All signals labeled SYNTHETIC or SIMULATED use generated data, not real borrower data.
> A signal moves from DESIGN TARGET → BUILT only when a PulseGuard artifact exists in `outputs/evidence/`.

---

## 1. SIGNAL TAXONOMY

PulseGuard produces seven categories of risk signal. Each has a defined computation method,
source (real/public vs. synthetic), output range, threshold rules, and gate.

| Signal Category | Signals | Phase | Gate | Data Type |
|----------------|---------|-------|------|-----------|
| Credit quality | Calibrated PD score | Training + Decision | G4, G7 | Real/Public (Home Credit) |
| Affordability | FOIR | Decision | G7 | Partially SYNTHETIC |
| Policy compliance | Hard-rule flags | Decision | G7 | Partially SYNTHETIC |
| Policy versioning | Policy threshold + version | Decision | G7 | SIMULATED |
| Distribution health | PSI / KS drift flags | Monitoring | G4 | SIMULATED lifecycle |
| Equity | Fairness flags | Monitoring | G5 | Real/Public (Home Credit) |
| Explainability | SHAP / adverse-action factors | Decision + Monitoring | G5, G7 | Real/Public (Home Credit) |
| Governance | Governance decision signal | Governance | G8 | Aggregated |

---

## 2. SIGNAL 1 — CALIBRATED PD SCORE

### Identity
| Property | Value |
|----------|-------|
| Signal name | `pd_score_champion` |
| Abbreviation | PD (Probability of Default) |
| Type | Continuous float |
| Range | [0.0, 1.0] |
| Semantics | Probability that the applicant defaults on the loan |
| Computation | XGBoost base model + Platt sigmoid calibration |
| Data source | Home Credit Default Risk (public, Kaggle) OR synthetic fallback |
| Data classification | **REAL/PUBLIC** (if Home Credit) or **SYNTHETIC** (if fallback) |
| Gate | G4 (DEFERRED) |

### Computation Method
```
1. Train XGBoost classifier on X_train (60% of dataset, stratified by TARGET)
2. Optimize hyperparameters via Optuna (50 trials, TPE, objective = PR AUC on X_val)
3. Select best trial as base champion
4. Apply Platt calibration: CalibratedClassifierCV(base_model, method='sigmoid', cv='prefit')
   Fit calibrator on X_val (20% of dataset)
5. Evaluate calibrated model on X_test (20% of dataset):
   - Primary metric: PR AUC (class-imbalance appropriate)
   - Secondary metric: ECE (calibration quality; must be < 0.01)
   - Tertiary: ROC AUC
6. ECE regression check: if Optuna best trial has better AUC but ECE > 1.10 × baseline ECE,
   the model is HELD. Champion is the best trial that does NOT regress ECE.
```

### Thresholds (Policy v1.0)
| Score Range | Decision | Rationale |
|-------------|----------|-----------|
| PD < 0.06 | APPROVE | Low credit risk; within acceptable default probability |
| 0.06 ≤ PD < 0.28 | REVIEW | Marginal; human underwriter review required |
| PD ≥ 0.28 | REJECT | High credit risk; expected loss exceeds policy tolerance |

### Policy v1.1 Threshold Change (SIMULATED, Day 12)
| Score Range | Decision | Change from v1.0 |
|-------------|----------|-----------------|
| PD < 0.05 | APPROVE | Lower threshold → fewer approvals (tightening) |
| 0.05 ≤ PD < 0.28 | REVIEW | Wider REVIEW band |
| PD ≥ 0.28 | REJECT | Unchanged |

### Source-Reference Benchmarks (NOT PulseGuard-built)
| Metric | Source-Reference Value | Source | Status |
|--------|----------------------|--------|--------|
| ROC AUC | ~0.7663 | RiskFrame (SR-1) | SOURCE_REFERENCE |
| PR AUC | ~0.2611 | RiskFrame (SR-2) | SOURCE_REFERENCE |
| ECE (champion) | ~0.0046 | RiskFrame (SR-3) | SOURCE_REFERENCE |
| PR AUC (held xgb_v2) | ~0.2654 | RiskFrame (SR-4) | SOURCE_REFERENCE |
| ECE (held xgb_v2) | ~0.0243 (5× worse) | RiskFrame (SR-5) | SOURCE_REFERENCE |

### Challenger Shadow Signal
| Property | Value |
|----------|-------|
| Signal name | `pd_score_challenger` |
| Model | LightGBM + Platt calibration |
| Use | Shadow only — NEVER drives decisions |
| Logged | Yes — in audit_trail.jsonl |
| Used for decision | NO |
| Gate | G6 (DEFERRED) |

---

## 3. SIGNAL 2 — FOIR (FIXED OBLIGATION TO INCOME RATIO)

### Identity
| Property | Value |
|----------|-------|
| Signal name | `foir_recomputed` |
| Type | Continuous float |
| Range | [0.0, ∞) — values > 1.0 mean obligations exceed income |
| Semantics | What fraction of monthly income is committed to fixed debt obligations |
| Data classification | **PARTIALLY SYNTHETIC** — see field mapping below |
| Gate | G7 (DEFERRED) |

### Computation Formula
```
FOIR = (EXISTING_OBLIGATIONS_MONTHLY + AMT_ANNUITY) / AMT_INCOME_TOTAL
```

### Field Mapping and Data Classification

| Field | Home Credit Column | Data Classification | Notes |
|-------|-------------------|---------------------|-------|
| Proposed EMI | `AMT_ANNUITY` | **REAL/PUBLIC** | Home Credit: proposed monthly annuity payment |
| Monthly income | `AMT_INCOME_TOTAL` | **REAL/PUBLIC** | Home Credit: declared total monthly income |
| Existing obligations | `EXISTING_OBLIGATIONS_MONTHLY` | **SYNTHETIC** | ⚠️ NOT in Home Credit; generated as Uniform(0.05, 0.25) × AMT_INCOME_TOTAL |

> ⚠️ **FOIR SYNTHETIC GAP DOCUMENTATION**
>
> Home Credit Default Risk does NOT contain existing monthly debt obligation data
> (existing EMI payments on other loans, credit cards, etc.). This is a real limitation
> of using a public competition dataset for credit underwriting simulation.
>
> Resolution: `EXISTING_OBLIGATIONS_MONTHLY` is generated synthetically as:
>   5% to 25% of AMT_INCOME_TOTAL (uniform distribution)
>
> This means:
> - The FOIR formula is correct and production-pattern
> - The FOIR inputs are partially synthetic
> - FOIR values in PulseGuard do NOT represent real borrower obligations
>
> Mandatory label in all artifacts: "FOIR computed using SYNTHETIC existing obligations.
> Not from real debt obligation data."
>
> Safe interview phrasing:
> "I implement FOIR as (existing obligations + proposed EMI) / net income — always
> recomputing from raw inputs. Home Credit doesn't provide existing obligation data,
> so I use a synthetic proxy. The recomputation logic and policy enforcement are
> production-pattern; the specific FOIR values are synthetic."

### FOIR Threshold
| FOIR Value | Hard Rule | Action |
|-----------|-----------|--------|
| > 0.65 | FOIR_EXCEEDED | HARD_REJECT — skip model scoring |
| 0.50–0.65 | — | Elevated risk; note in audit trail |
| < 0.50 | — | Acceptable; continue |

### FOIR Recomputation Principle
The FOIR is ALWAYS recomputed from raw `AMT_INCOME_TOTAL`, `AMT_ANNUITY`,
and the synthetic `EXISTING_OBLIGATIONS_MONTHLY`. It is NEVER trusted from application
input, even if an application provides a pre-computed ratio. This eliminates one of the
most common manipulation vectors in credit underwriting.

---

## 4. SIGNAL 3 — HARD-RULE FLAGS

### Identity
| Property | Value |
|----------|-------|
| Signal type | 6 binary boolean flags |
| Semantics | Deterministic policy violations that precede model scoring |
| Data classification | Mixed — see per-rule breakdown below |
| Gate | G7 (DEFERRED) |

### Rule Specifications

| Flag | Rule | Threshold | Data Source | Classification |
|------|------|-----------|-------------|---------------|
| `hard_rule_foir_flag` | FOIR > 0.65 | 0.65 | AMT_INCOME_TOTAL (real), AMT_ANNUITY (real), EXISTING_OBLIGATIONS_MONTHLY (SYNTHETIC) | PARTIALLY SYNTHETIC |
| `hard_rule_ltv_flag` | AMT_CREDIT / AMT_GOODS_PRICE > 0.90 | 0.90 | AMT_CREDIT (real), AMT_GOODS_PRICE (real, 1% missing) | REAL/PUBLIC |
| `hard_rule_income_flag` | AMT_INCOME_TOTAL < 15,000 | 15,000/month | AMT_INCOME_TOTAL (real) | REAL/PUBLIC |
| `hard_rule_age_min_flag` | DAYS_BIRTH > −6,570 (age < 18) | 18 years | DAYS_BIRTH (real) | REAL/PUBLIC |
| `hard_rule_age_max_flag` | DAYS_BIRTH < −25,550 (age > 70) | 70 years | DAYS_BIRTH (real) | REAL/PUBLIC |
| `hard_rule_region_flag` | REGION_RATING_CLIENT == 3 | Category 3 | REGION_RATING_CLIENT (real) | REAL/PUBLIC |

### Evaluation Order
Rules evaluate in the order listed. First triggered hard-reject rule sets `hard_reject_reason`.
Region flag (Rule 6) produces REVIEW routing, not HARD_REJECT — the application still gets model scored.

### Hard-Reject Reason Code Mapping

| Reason Code | Triggered By |
|-------------|-------------|
| `FOIR_EXCEEDED` | hard_rule_foir_flag == True |
| `LTV_EXCEEDED` | hard_rule_ltv_flag == True |
| `INCOME_BELOW_FLOOR` | hard_rule_income_flag == True |
| `AGE_BELOW_MINIMUM` | hard_rule_age_min_flag == True |
| `AGE_ABOVE_MAXIMUM` | hard_rule_age_max_flag == True |
| (none — REVIEW forced) | hard_rule_region_flag == True |

---

## 5. SIGNAL 4 — POLICY THRESHOLDS AND VERSION LOG

### Identity
| Property | Value |
|----------|-------|
| Signal type | Versioned configuration |
| Semantics | Defines PD score bands for APPROVE/REVIEW/REJECT; updated when policy changes |
| Data classification | **SIMULATED** — no real policy committee; portfolio-internal |
| Gate | G7 (DEFERRED) |

### Policy Version Log Schema

```json
{
  "policy_version": "string — 'v1.0' | 'v1.1'",
  "effective_day": "integer",
  "approve_threshold": "float — PD below this → APPROVE",
  "reject_threshold": "float — PD above this → REJECT",
  "change_rationale": "string",
  "authorized_by": "string — 'portfolio_governance_simulation'",
  "change_magnitude_approve_threshold": "float — delta from prior version"
}
```

| Version | Approve < | Review: [L, H) | Reject ≥ | Effective Day | Change Reason |
|---------|-----------|----------------|----------|--------------|---------------|
| v1.0 | 0.06 | [0.06, 0.28) | 0.28 | Day 0 | Initial deployment |
| v1.1 | 0.05 | [0.05, 0.28) | 0.28 | Day 12 | Policy tightening (SIMULATED) |

> Note: v1.1 is a SIMULATED policy event designed to test the approval rate decomposition
> signal. In a real system this would require governance committee approval.

---

## 6. SIGNAL 5 — PSI / KS DRIFT FLAGS

### Identity
| Property | Value |
|----------|-------|
| Signal names | `psi_<feature>`, `ks_<feature>`, `psi_status_<feature>` |
| Type | Continuous float (PSI/KS) + categorical enum (status) |
| Range | PSI: [0, ∞); KS: [0, 1] |
| Semantics | Quantifies how much the current serving distribution differs from training distribution |
| Data classification | **SIMULATED** lifecycle — all batches are synthetic; drift is injected |
| Gate | G4 (DEFERRED) |

### PSI Computation
```
PSI = Σ (actual_pct_i − expected_pct_i) × ln(actual_pct_i / expected_pct_i)
where:
  expected = training reference distribution (B00)
  actual   = current serving batch distribution
  bins     = 10 equal-width bins over [0, 1] for bounded features
```

### PSI Threshold Rules
| PSI Value | Status | Action |
|-----------|--------|--------|
| < 0.10 | STABLE | No action required |
| 0.10 ≤ PSI < 0.20 | WARN | Log alert; increase monitoring frequency |
| PSI ≥ 0.20 | ALERT | Trigger model review; document retraining consideration |

### KS Statistic
```
KS = max|F_expected(x) − F_actual(x)| over all x
where F = empirical CDF
```
KS supplements PSI — PSI detects overall distribution divergence; KS detects the maximum
point of divergence. Together they provide a more complete drift picture.

### Retraining Trigger Definition
```
Condition: PSI ALERT (≥ 0.20) on EXT_SOURCE_2 OR EXT_SOURCE_3 for ≥ 2 consecutive batches
Action: Document "retraining_triggered = True" in drift_report.json
        Add retraining event to policy_change_log.json
        Do NOT automatically retrain in the portfolio version
```

### Decommissioning Trigger Definition
```
Condition: PSI > 0.30 sustained for ≥ 5 consecutive batches
           OR Disparate Impact violation unresolved for > 30 days
Action: Document "decommissioning_triggered = True" in governance_signoff.md
        Model status → "RETIRE"
```

### Key Feature Drift Design Targets (SIMULATED)

| Feature | Day 7 PSI | Day 14 PSI | Day 14 Status |
|---------|-----------|-----------|--------------|
| EXT_SOURCE_2 | ~0.11 (WARN) | ~0.23 (ALERT) | ⚠️ ALERT — retraining trigger fires |
| EXT_SOURCE_3 | < 0.05 (STABLE) | < 0.10 (STABLE) | STABLE |
| AMT_CREDIT | < 0.05 (STABLE) | < 0.05 (STABLE) | STABLE |
| AMT_INCOME_TOTAL | < 0.05 (STABLE) | < 0.05 (STABLE) | STABLE |

Source-reference: SR-6 (PSI Day 14 ~0.2358), SR-7 (EXT_SOURCE_2 shift −0.18) — not PulseGuard-built.

### PSI Multivariate Blindspot (Documented Limitation)
PSI is a univariate signal. It computes distribution shift per feature independently.
It cannot detect joint distribution shift — two features can shift together in a correlated
manner while both individual PSIs remain below ALERT. This is documented as a Known Boundary
Condition. Multivariate drift (Wasserstein distance, MMD) is DEFERRED to G9.

---

## 7. SIGNAL 6 — FAIRNESS FLAGS

### Identity
| Property | Value |
|----------|-------|
| Signal names | `di_value`, `di_status`, `eopp_gap_pp`, `eopp_status`, `protected_attr_shap_rank` |
| Type | Continuous float (DI, gap) + categorical enum (status) + integer (rank) |
| Semantics | Quantifies whether the model produces disparate outcomes by demographic group |
| Data classification | **REAL/PUBLIC** — CODE_GENDER is from Home Credit dataset |
| Gate | G5 (DEFERRED) |

### Disparate Impact (DI)
```
DI = approval_rate(group=F) / approval_rate(group=M)

Threshold bands (80% rule — industry standard):
  DI ≥ 0.80 → PASS (no adverse impact finding)
  DI < 0.80 → FAIL (potential adverse impact; escalate)
  DI > 1.25 → WARN (opposite direction imbalance; monitor)
```

### Equal Opportunity (EOpp) Gap
```
EOpp_gap = |TPR(group=F) − TPR(group=M)|  [in percentage points]

where TPR = true positive rate at the decision boundary
      (correctly approved genuinely-creditworthy applicants)

Threshold:
  < 5pp  → PASS
  5–10pp → WARN
  ≥ 10pp → FAIL
```

### SHAP Proxy Check
```
Compute mean |SHAP| for all features including CODE_GENDER_F.
Rank features by mean |SHAP| descending.
Check: is CODE_GENDER_F in top-5 features?
  YES → WARN (protected attribute proxy may be influencing decisions)
  NO  → PASS
```

### Source-Reference Benchmarks (NOT PulseGuard-built)
| Metric | Source-Reference Value | Source | Status |
|--------|----------------------|--------|--------|
| Disparate Impact | ~1.059 | RiskFrame (SR-8) | SOURCE_REFERENCE |
| EOpp gap | < 5pp | RiskFrame (SR-9) | SOURCE_REFERENCE |
| CODE_GENDER_F SHAP rank | ~#10 | RiskFrame (implied) | SOURCE_REFERENCE |

### Scope Caveat
CODE_GENDER in Home Credit is a data field in a public competition dataset — it is not a
regulated protected class in a real deployed system. The fairness audit methodology follows
production patterns, but the specific results are dataset-specific and do not constitute
a regulatory compliance assessment.

---

## 8. SIGNAL 7 — SHAP / ADVERSE ACTION FACTORS

### Identity
| Property | Value |
|----------|-------|
| Signal names | `adverse_action_code_1/2/3`, `adverse_action_shap_1/2/3` |
| Type | String (code) + float (SHAP value) |
| Semantics | Top-3 model features driving the REJECT/REVIEW decision for a specific applicant |
| Data classification | **REAL/PUBLIC** (feature values from Home Credit) |
| Gate | G5 (SHAP ranking), G7 (adverse action codes in decision pipeline) (DEFERRED) |

### Computation
```
For each application with decision = REJECT or REVIEW:
1. Compute SHAP values using shap.Explainer(model.predict_proba, background_sample)
2. Sort features by |SHAP value| descending for that specific applicant
3. Return top-3 features and their SHAP values as adverse_action_code_{1,2,3}
```

> Note: The `shap.TreeExplainer` API has a compatibility issue with XGBoost 3.2 (base_score
> format change). PulseGuard uses `shap.Explainer(model.predict_proba, background)` which
> is model-agnostic and confirmed working in the G1 environment check (16/16 PASS).

### Adverse Action Code Mapping

| Home Credit Feature | Adverse Action Code | Reason Text |
|--------------------|--------------------|----|
| EXT_SOURCE_2 | `LOW_BUREAU_SCORE_1` | Insufficient external credit bureau score (source 2) |
| EXT_SOURCE_3 | `LOW_BUREAU_SCORE_2` | Insufficient external credit bureau score (source 3) |
| AMT_INCOME_TOTAL | `INSUFFICIENT_INCOME` | Declared monthly income below threshold for requested credit |
| AMT_CREDIT | `CREDIT_AMOUNT_EXCESSIVE` | Requested credit amount too high relative to income/obligations |
| DAYS_EMPLOYED | `INSUFFICIENT_EMPLOYMENT` | Employment history insufficient |
| AMT_ANNUITY | `HIGH_EMI_BURDEN` | Proposed EMI creates unacceptable debt burden |
| FOIR (synthetic) | `DTI_RATIO_EXCEEDED` | Debt-to-income ratio exceeds policy threshold |
| REGION_RATING_CLIENT | `HIGH_RISK_REGION` | Applicant region has elevated credit risk rating |

### Interview Note
These are ILLUSTRATIVE codes following ECOA adverse action notice patterns. In a real
production system, adverse action notices would be drafted by compliance and legal teams,
not auto-generated from SHAP values. The methodology demonstrates the explainability
capability — it does not constitute filed adverse action notices.

---

## 9. SIGNAL 8 — GOVERNANCE DECISION SIGNAL

### Identity
| Property | Value |
|----------|-------|
| Signal name | `governance_decision` |
| Type | Categorical enum |
| Range | {APPROVE, MONITOR, CHALLENGE, RETIRE} |
| Semantics | Formal end-of-lifecycle governance verdict on the champion model |
| Data classification | **SIMULATED** — portfolio governance; not regulatory sign-off |
| Gate | G8 (DEFERRED) |

### Decision Rules

| Governance Decision | Trigger Conditions |
|--------------------|--------------------|
| APPROVE | All of: ECE < 0.01; PSI_ALERT_count ≤ 1; DI ∈ [0.80, 1.25]; EOpp_gap < 5pp; no leakage FAIL; no challenger promoted without gate review |
| MONITOR | Any of: 1 PSI WARN sustained; ECE borderline (0.01–0.015); DI approaching boundary (0.80–0.85 or 1.20–1.25); leakage WARNs documented |
| CHALLENGE | Any of: Challenger within 0.001 PR AUC but failed gate; external evidence of model degradation; > 2 consecutive PSI WARNs |
| RETIRE | Any of: PSI ALERT ≥ 2 consecutive batches on key feature; DI FAIL unresolved; ECE > 0.03 (> 3× initial); leakage FAIL on champion features |

### SR 26-2 Alignment Note
The governance decision document is designed to demonstrate SR 26-2 aligned methodology:
"complete lifecycle governance as one governed chain." It maps each gate artifact to the
corresponding SR 26-2 lifecycle requirement (development → validation → deployment →
monitoring → retirement). It does NOT claim SR 26-2 compliance or certification — that
requires external regulatory validation not available in a portfolio project.

---

## 10. SIGNAL COMPUTATION STATUS REGISTRY

| Signal | Status | Data Classification | Gate | Artifact When Built |
|--------|--------|--------------------|----|---------------------|
| Calibrated PD score | DEFERRED | Real/Public (Home Credit) | G4 | `calibration_report.json` |
| Challenger shadow PD | DEFERRED | Real/Public (Home Credit) | G6 | `challenger_promotion_decision.json` |
| FOIR | DEFERRED | Partially SYNTHETIC | G7 | `decision_simulation_report.json` |
| Hard-rule flags (1–5) | DEFERRED | Mostly Real/Public | G7 | `decision_simulation_report.json` |
| Hard-rule flag (Region, Rule 6) | DEFERRED | Real/Public | G7 | `decision_simulation_report.json` |
| Policy threshold v1.0 | DEFERRED | SIMULATED | G7 | `policy_change_log.json` |
| Policy threshold v1.1 | DEFERRED | SIMULATED | G7 | `policy_change_log.json` |
| PSI per feature (30 batches) | DEFERRED | SIMULATED lifecycle | G4 | `drift_report.json` |
| KS per feature (30 batches) | DEFERRED | SIMULATED lifecycle | G4 | `drift_report.json` |
| Day 7 WARN event | DEFERRED | SIMULATED | G4 | `drift_report.json` |
| Day 14 ALERT event | DEFERRED | SIMULATED | G4 | `drift_report.json` |
| DI (Disparate Impact) | DEFERRED | Real/Public | G5 | `fairness_report.json` |
| EOpp gap | DEFERRED | Real/Public | G5 | `fairness_report.json` |
| SHAP ranking (global) | DEFERRED | Real/Public | G5 | `shap_beeswarm.png` |
| SHAP adverse-action factors (per app) | DEFERRED | Real/Public | G7 | `audit_trail.jsonl` |
| Approval rate decomposition | DEFERRED | SIMULATED | G7 | `decision_simulation_report.json` |
| Delayed label validation | DEFERRED | SIMULATED | G8 | `delayed_label_report.json` |
| Governance decision | DEFERRED | SIMULATED | G8 | `governance_signoff.md` |

**All 18 signals are DEFERRED as of G2. None have been computed inside PulseGuard.**
All SOURCE_REFERENCE values from RiskFrame (SR-1 through SR-12) remain SOURCE_REFERENCE.
