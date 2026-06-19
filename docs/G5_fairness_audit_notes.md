# G5 — FAIRNESS AUDIT NOTES
## PulseGuard · Group-Level Model Performance and Calibration Analysis

**Gate:** G5 — Fairness Audit
**Status:** COMPLETE
**Date:** June 2026

---

## 1. SCOPE BOUNDARY

**Allowed (G5):**
- Group-level model performance comparison
- Group-level calibration comparison
- Approval-rate / score-distribution analysis under synthetic policy
- Fairness caveats and claim boundaries

**Forbidden (G5 — deferred):**
- SHAP explanation system → G5 (limited scope) / G7
- Adverse-action notices → G7
- FOIR routing → G7
- Decision engine → G7
- Governance signoff → G8
- Compliance certification → never claim
- Real protected-class claim → never claim
- Production fairness claim → never claim

---

## 2. GROUP VARIABLE

**Column:** `CODE_GENDER`
**Groups:** F (female proxy) / M (male proxy)
**Generation:** `rng.choice(['F', 'M'], n, p=[0.65, 0.35])` — matches real Home Credit dataset gender ratio.
**Critical caveat:** CODE_GENDER is a **synthetic proxy attribute**. It is NOT a real protected class, not a real individual's gender, and does not represent a real credit applicant population. Fairness analysis demonstrates methodology only.

**CODE_GENDER in DGP logit:** NOT PRESENT. The default probability formula does not include CODE_GENDER as a term. Default rate differences between groups reflect sampling variance only, not structural discrimination in the DGP.

| Group | N (test) | N (defaults) | Default Rate |
|-------|----------|-------------|-------------|
| F | 6,444 | 517 | 0.0802 |
| M | 3,556 | 300 | 0.0844 |
| Overall | 10,000 | 817 | 0.0817 |

---

## 3. SYNTHETIC POLICY v1.0

**Thresholds (not a real credit policy — synthetic only):**

| Decision | Condition | Rationale |
|----------|-----------|-----------|
| APPROVE | PD < 0.06 | Well below default rate — confident non-default |
| REVIEW | 0.06 ≤ PD < 0.28 | Uncertain band — manual review in a real system |
| REJECT | PD ≥ 0.28 | High risk — above 3× the population default rate |

These thresholds are chosen for demonstration purposes and are not calibrated to a real business loss function.

---

## 4. SCORE DISTRIBUTION BY GROUP

| Statistic | F | M | Gap |
|-----------|---|---|-----|
| mean PD | 0.08148 | 0.08087 | 0.0006 |
| median PD | 0.06947 | 0.06907 | 0.0004 |
| std PD | 0.03645 | 0.03601 | 0.0004 |

Score distributions are near-identical between groups. This is expected: CODE_GENDER is not in the DGP logit, and its correlations with signal features (EXT_SOURCE_2, income, employment) are minimal in this synthetic DGP.

---

## 5. APPROVAL RATES (SYNTHETIC POLICY v1.0)

| Routing | F | M |
|---------|---|---|
| APPROVE (PD < 0.06) | 22.98% | 22.69% |
| REVIEW | 76.69% | 77.02% |
| REJECT (PD ≥ 0.28) | 0.33% | 0.28% |

---

## 6. FAIRNESS METRICS — ACTUAL (PulseGuard-BUILT)

All computed on the held-out test set (10,000 rows, same split as G4 champion evaluation).

### 6.1 Disparate Impact (DI)

```
DI = approval_rate_F / approval_rate_M = 0.22983 / 0.22694 = 1.0127
```

| Metric | Value | Band | Status |
|--------|-------|------|--------|
| DI (F/M) | **1.0127** | 0.80–1.25 | **PASS** |

The 4/5ths rule heuristic requires DI ≥ 0.80 (no adverse impact). DI = 1.0127 is within the acceptable band. Female applicants are approved at a marginally higher rate than male applicants.

**Note:** DI = 1.0127 is close to the source reference SR-8 (DI ~1.059 from RiskFrame on real Home Credit). The synthetic DGP produces a similar no-violation finding, validating the methodology.

### 6.2 Equal Opportunity Gap

```
TPR = P(score ≥ 0.06 | TARGET=1)  [true defaults correctly flagged for REVIEW/REJECT]
EOpp gap = |TPR_F − TPR_M| = |0.8820 − 0.8600| = 0.0220  (2.2 pp)
```

| Group | TPR | EOpp Gap |
|-------|-----|----------|
| F | 0.8820 | — |
| M | 0.8600 | **0.022** |

2.2 pp gap. No hard threshold is mandated by G5 scope; the gap is small relative to the base rate. Both groups have high flag rates (>86%) for true defaults.

### 6.3 Predictive Parity Gap

```
PPV = P(TARGET=1 | score ≥ 0.06)  [precision of REVIEW/REJECT decisions]
Parity gap = |PPV_F − PPV_M| = |0.0919 − 0.0939| = 0.0020  (0.2 pp)
```

Predictive parity gap is negligible (0.2 pp). When the model flags an applicant for REVIEW/REJECT, it is equally predictive of true default across both groups.

### 6.4 ROC-AUC by Group

| Group | ROC-AUC | Gap |
|-------|---------|-----|
| F | 0.6374 | — |
| M | 0.6002 | **0.037** |

AUC gap: 3.7 pp. The male group has a lower AUC despite a slightly higher default rate. Contributing factors: (1) smaller test sample (M=3,556 vs F=6,444) increases AUC variance; (2) CODE_GENDER is not in the DGP, so group-level AUC difference reflects sampling noise, not structural discrimination. The gap is within expected sampling variance for groups of these sizes.

### 6.5 Calibration by Group (ECE)

| Group | ECE | Gap |
|-------|-----|-----|
| F | 0.0036 | — |
| M | 0.0092 | **0.0056** |

Both groups have low ECE (well-calibrated). The female group is slightly better calibrated, likely due to larger sample size providing more signal to the Platt sigmoid fit.

---

## 7. CODE_GENDER FEATURE IMPORTANCE RANK

Feature importance extracted from XGBoost booster (gain importance, not SHAP). CODE_GENDER is ordinal-encoded by the preprocessor; feature name maps to index 20 (first categorical column).

| Rank | Feature | Gain |
|------|---------|------|
| 1 | DAYS_EMPLOYED | 27.208 |
| 2 | EXT_SOURCE_2 | 9.562 |
| 3 | AMT_INCOME_TOTAL | 8.473 |
| 4 | EXT_SOURCE_3 | 8.365 |
| 5 | REGION_RATING_CLIENT | 7.996 |
| 6 | DEF_30_CNT_SOCIAL_CIRCLE | 7.242 |
| 7 | AMT_CREDIT | 7.034 |
| 8 | REGION_POPULATION_RELATIVE | 6.973 |
| 9 | AMT_ANNUITY | 6.885 |
| 10 | AMT_GOODS_PRICE | 6.881 |
| **24** | **CODE_GENDER** | **5.622** |

**CODE_GENDER is ranked #24 out of 28 features.** It is among the lowest-contributing features in the model. DAYS_EMPLOYED has 4.8× the gain of CODE_GENDER. This confirms CODE_GENDER is not a primary driver of model predictions.

**Interview phrasing:** "I checked feature importance by gain. CODE_GENDER ranks #24 out of 28 features — it's not a primary driver. DAYS_EMPLOYED, EXT_SOURCE_2, and income are the dominant signals, which matches the DGP design."

**Scope note:** This is XGBoost gain importance, not SHAP. SHAP TreeExplainer (global explanation system) is G5-forbidden per gate boundary. The gain rank is a lightweight proxy confirming CODE_GENDER is not a top driver. Full SHAP analysis belongs to a later gate.

---

## 8. FAIRNESS RESULTS SUMMARY TABLE

| Metric | Value | Threshold/Band | Status |
|--------|-------|----------------|--------|
| Disparate Impact (F/M) | **1.0127** | 0.80–1.25 | ✓ PASS |
| Equal Opportunity gap | **0.022** (2.2 pp) | < 5 pp (heuristic) | ✓ PASS |
| Predictive Parity gap | **0.002** (0.2 pp) | negligible | ✓ PASS |
| ROC-AUC gap (F vs M) | **0.037** | no hard threshold | INFO |
| ECE gap (F vs M) | **0.006** | no hard threshold | INFO |
| CODE_GENDER feature rank | **#24 / 28** | not top-5 | ✓ PASS |

All primary fairness checks pass under the synthetic policy v1.0 thresholds.

---

## 9. EVIDENCE BOUNDARY

These metrics are **PulseGuard-BUILT** on `synthetic_home_credit_like` test data:
- DI = 1.0127 (PASS)
- EOpp gap = 0.022 (2.2 pp)
- Predictive Parity gap = 0.002 (0.2 pp)
- CODE_GENDER gain rank = #24

These are **SOURCE_REFERENCE** from prior projects (not PulseGuard-built):
- SR-8: DI ~1.059 (RiskFrame, real Home Credit)
- SR-9: Equal Opportunity gap < 5 pp (RiskFrame, real Home Credit)

The PulseGuard DI (1.0127) is directionally consistent with SR-8 (1.059) — both show no adverse impact against female applicants.

---

## 10. CAVEATS (MANDATORY — MUST APPEAR IN MODEL CARD AND INTERVIEW)

1. **Synthetic proxy only.** CODE_GENDER is assigned randomly with p=[0.65, 0.35]. It does not represent real individuals. Fairness results are illustrative, not actual fairness evidence for a deployed system.

2. **No real protected class.** Home Credit CODE_GENDER is a public dataset field, not a protected characteristic in a deployed credit system. Making regulatory fairness claims based on this analysis is forbidden.

3. **DI is a heuristic.** The 4/5ths rule (DI ≥ 0.80) is an EEOC employment testing heuristic. It is not a legal standard for credit fairness under ECOA, FCRA, or any banking regulation.

4. **ROC-AUC gap may reflect sampling variance.** Male group (n=3,556) is smaller than female group (n=6,444). AUC differences of 3–5% are within expected sampling noise at these sample sizes.

5. **Single protected attribute.** Only CODE_GENDER is audited. A complete fairness audit would examine intersectional groups, income brackets, geographic regions, and other proxy variables.

6. **Static threshold.** Policy v1.0 threshold (0.06) is fixed. A real system would require threshold calibration by group to maintain equal opportunity under dynamic business conditions.

---

## 11. NOTES FOR G6

**G6 = Champion/Challenger** (XGBoost vs. LightGBM, 5-gate promotion framework)

Pre-G6 checklist:
1. Load `outputs/models/champion_calibrated.pkl` and `outputs/models/preprocessor.pkl`
2. Train LightGBM challenger on same training set (same split, same features, same preprocessor)
3. Platt calibrate challenger on validation set
4. Evaluate both on test set: ROC-AUC, PR-AUC, ECE, Brier
5. 5-gate promotion check: PR-AUC delta ≥ 0.001, ROC-AUC delta ≥ 0.001, ECE non-regression, calibration curve non-divergence, DeLong test at p < 0.05
6. Expected outcome (per G0 design): LightGBM challenger within ~0.0002 PR-AUC of champion (Gate 1 FAIL → champion retained)
7. Output: `outputs/evidence/g6_challenger_evaluation.json` + `outputs/evidence/g6_promotion_decision.json`
8. Hard rule: Do NOT run Optuna in G6 training; default hyperparameters for challenger only
