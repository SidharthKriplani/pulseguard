# G8 — Model Card
## PulseGuard · Taiwan Default Credit Decision Champion

**Model ID:** `pulseguard-taiwan-xgb-platt-v1`
**Gate:** G8 — Model Risk Governance + Decision Accountability Pack
**Status:** COMPLETE
**Date:** June 2026
**Patch version:** (initial — G8.0)

---

> **Scope statement:** This model card documents a portfolio-grade, research-simulated credit risk model. It does not describe a production system, a regulated lending model, or a model approved for use in any real credit decision affecting real applicants. Every section is written with the discipline a production model card requires — so the methodology is production-pattern — but the deployment status is explicitly `NOT_PRODUCTION_READY`.

---

## 1. Model Purpose

`pulseguard-taiwan-xgb-platt-v1` estimates the 6-month probability of credit card default for individual account holders. Its output is a calibrated probability score (PD — probability of default) in the range [0, 1].

The score is consumed by the G7 threshold policy (`taiwan_real_data_v1.0`) to route each applicant into one of three decision zones:
- **APPROVE** (PD < 0.20): credit extended automatically
- **REVIEW** (0.20 ≤ PD < 0.40): referred to manual underwriting
- **REJECT** (PD ≥ 0.40): credit declined automatically

The model's role in this architecture is **score generation only**. The policy is a separate component that consumes the score. Model changes and policy changes are versioned independently and require separate approval events.

---

## 2. Intended Use

| Use Case | Status |
|----------|--------|
| Portfolio-simulation credit risk scoring on Taiwan credit card data | ✓ INTENDED |
| Champion/challenger performance evaluation | ✓ INTENDED |
| Calibration and ECE analysis demonstration | ✓ INTENDED |
| PSI drift monitoring protocol testing | ✓ INTENDED |
| Interview / portfolio evidence of model lifecycle methodology | ✓ INTENDED |
| G8 governance artifact generation and model-risk documentation | ✓ INTENDED |

---

## 3. Out-of-Scope Use

| Use Case | Status | Reason |
|----------|--------|--------|
| Real credit decisions affecting real applicants | ✗ OUT OF SCOPE | No real applicant data; no regulatory approval; no adverse-action notice framework |
| Consumer loan underwriting (FOIR-based) | ✗ OUT OF SCOPE | Taiwan Default is credit card data; no income or EMI fields available |
| Regulatory capital / stress testing | ✗ OUT OF SCOPE | Not validated against regulatory stress scenarios; uses illustrative cost assumptions |
| Fair-lending compliance under ECOA / FCRA / RBI | ✗ OUT OF SCOPE | No compliance certification; fairness audit is methodology demonstration only |
| Real-time production serving (< 100 ms latency) | ✗ OUT OF SCOPE | FastAPI serving not built in current gate scope (deferred to G9) |
| Home Credit or other dataset populations | ✗ OUT OF SCOPE | Model trained exclusively on Taiwan Default (UCI 2005 credit card); different product and population |
| Adverse action notice generation | ✗ OUT OF SCOPE | ECOA / Regulation B adverse action code assignment not implemented |

---

## 4. Dataset

| Property | Value |
|----------|-------|
| **Name** | UCI ML Repository — Default of Credit Card Clients |
| **Alias** | Taiwan Default (`PUBLIC_REAL_TAIWAN_DEFAULT`) |
| **Source** | https://archive.ics.uci.edu/dataset/350 |
| **Access** | Public; no authentication required |
| **Rows** | 30,000 credit card accounts |
| **Vintage** | Taiwan, April–September 2005 |
| **Product type** | Revolving credit card (not consumer instalment loan) |
| **Target event** | Default payment in the following month (binary: 0 / 1) |
| **Default rate** | 22.12% (6,636 / 30,000) |
| **Missing values** | Zero — no imputation required |
| **Demographic fields** | SEX (1=M, 2=F), AGE (continuous), EDUCATION (1–6 ordinal), MARRIAGE (0–3 ordinal) |
| **Payment features** | PAY_0, PAY_2–PAY_6 (payment status, −2 to 8 scale) |
| **Balance features** | BILL_AMT1–BILL_AMT6 (NT dollar statement balance, monthly) |
| **Payment amount features** | PAY_AMT1–PAY_AMT6 (actual NT dollar payment, monthly) |
| **Credit limit** | LIMIT_BAL (NT dollar revolving credit limit) |
| **Split** | Train: 18,000 / Val: 6,000 / Test: 6,000 (60/20/20, stratified by target, seed=42) |
| **Artifact** | `data/public/taiwan_credit_default.xls` |

**Known dataset limitations (see Section 13):**
- 2005 vintage: consumer credit behaviour has changed in 19 years
- Taiwan revolving credit card product: not directly analogous to any other jurisdiction or product type
- PAY_0 encoding has known undocumented categories (values −2, 0 observed in data not described in original paper)
- No income, employment, or FOIR-relevant fields

---

## 5. Target Definition

**Target variable:** `default payment next month`

- **0:** No default in the following month
- **1:** Default (missed payment, defined by credit bureau standard for Taiwan 2005)

**Label timing:** The label is observed at month T+1. All features (PAY_0, BILL_AMT1, PAY_AMT1, etc.) reflect the state at month T. This temporal ordering is preserved in the dataset as-provided; no synthetic timestamp injection was required on this dataset (unlike the synthetic Home Credit lane at G3).

**Training signal:** Features at month T predict the binary event at T+1. The 6-month payment history panel (PAY_0 through PAY_6, BILL_AMT1–6, PAY_AMT1–6) provides a strong temporal signal for this prediction horizon.

---

## 6. Model Family

| Property | Value |
|----------|-------|
| **Algorithm** | XGBoost (gradient boosted decision trees) |
| **Library** | `xgboost` (Python) |
| **Key hyperparameters** | `n_estimators=500, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, scale_pos_weight=(n_neg/n_pos)=3.52, eval_metric='aucpr', early_stopping_rounds=50, random_state=42` |
| **Actual iterations used** | 57 (early stopping on val AUCPR) |
| **Calibration** | Platt sigmoid (`CalibratedClassifierCV(cv='prefit', method='sigmoid')`, fit on val set only) |
| **Preprocessing** | `StandardScaler` on numeric features; `OneHotEncoder(handle_unknown='ignore')` on SEX/EDUCATION/MARRIAGE |
| **Preprocessor fit** | Training set only (val and test transformed, not fit) |
| **Output** | Calibrated probability in [0, 1] — `predict_proba()[:, 1]` from `CalibratedClassifierCV` |
| **Model artifacts** | Stored as serialised sklearn pipeline (Platt wrapper + XGBoost base) |
| **Training script** | `scripts/g6_champion_challenger.py` |

**Why XGBoost over LR / LightGBM:**
- LR Baseline rejected: ROC-AUC 0.7283 vs XGBoost 0.7852; PR-AUC 0.5138 vs 0.5709 — both gates fail
- LightGBM held (not rejected): competitive AUC (0.7742) but ECE gate fails uncalibrated (ECE=0.132 vs calibrated champion ECE=0.011); held pending calibrated LightGBM comparison at G9
- XGBoost (Platt): all 4 promotion gates pass; ECE 94.6% reduction from raw; selected as champion

---

## 7. Feature Set

23 features used for training. `ID` and `default payment next month` are excluded.

| Feature Group | Features | Count | Preprocessing |
|--------------|----------|-------|---------------|
| Credit limit | `LIMIT_BAL` | 1 | StandardScaler |
| Demographics | `AGE` | 1 | StandardScaler |
| Payment status (6-month panel) | `PAY_0`, `PAY_2`, `PAY_3`, `PAY_4`, `PAY_5`, `PAY_6` | 6 | StandardScaler |
| Statement balance (6-month) | `BILL_AMT1`–`BILL_AMT6` | 6 | StandardScaler |
| Payment amount (6-month) | `PAY_AMT1`–`PAY_AMT6` | 6 | StandardScaler |
| Categorical demographics | `SEX`, `EDUCATION`, `MARRIAGE` | 3 | OneHotEncoder |

**Features NOT used:** `ID` (identifier — excluded by design).

**Note on FOIR:** No income or proposed-EMI field is available in Taiwan Default. FOIR (fixed obligation to income ratio) is not computable on this dataset. Credit card analogues — credit utilisation (`BILL_AMT1 / LIMIT_BAL`) and payment-to-balance ratio (`PAY_AMT1 / BILL_AMT1`) — are implicitly captured by the feature panel but not explicitly engineered as ratio features in this version.

**Feature leakage status:** No temporal leakage detected. All features in this panel are contemporaneous with the decision point (month T). No FeatureLeakageLens FAIL-level findings on Taiwan Default. (Note: G3 FAIL was on the synthetic Home Credit lane — an injected column.)

---

## 8. Performance Summary

All metrics computed on held-out test set (6,000 rows, 22.12% default rate). No test-set data was used in training or calibration.

| Metric | Raw XGBoost | **XGBoost (Platt)** ⭐ | LightGBM (held) | LR Baseline |
|--------|-------------|----------------------|-----------------|-------------|
| ROC-AUC | 0.7852 | **0.7852** | 0.7742 | 0.7283 |
| PR-AUC | 0.5709 | **0.5709** | 0.5525 | 0.5138 |
| Brier Score | 0.1778 | **0.1329** | 0.1553 | 0.2047 |
| ECE (10-bin) | 0.2082 | **0.0112** | 0.1321 | 0.2347 |

**Calibration uplift:** Platt calibration reduces ECE 94.6% (0.2082 → 0.0112) with no loss in discrimination (ROC-AUC and PR-AUC unchanged). This is the largest calibration improvement across all PulseGuard gates.

**Source reference comparison:** Source reference SR-1 (RiskFrame on real Home Credit data) ROC-AUC=0.7663. Taiwan Default achieves 0.7852. This is a dataset characteristic difference — Taiwan has a higher base rate (22% vs 8%) and stronger 6-month sequential payment signal. **This is not a claim that PulseGuard's model outperforms RiskFrame's model.**

**Artifact:** `outputs/evidence/g6_champion_challenger_report.json` · `outputs/evidence/g6_calibration_report.json`

---

## 9. Calibration Summary

**Why calibration is required for this model:**

Raw XGBoost probability outputs (ECE=0.208) are systematically miscalibrated on Taiwan Default's complex real feature space. A raw score of 0.35 does not mean a 35% probability of default — the actual observed default rate for that cohort is significantly different. Setting thresholds on raw scores is therefore not interpretable.

**Platt calibration result:**

| Calibration Check | Value | Interpretation |
|-------------------|-------|----------------|
| ECE (10-bin, calibrated) | 0.0112 | Near-perfect calibration: score decile DR matches predicted PD |
| ECE (10-bin, raw) | 0.2082 | Severe miscalibration: raw score ≠ true probability |
| ECE reduction | 94.6% | Largest calibration improvement in PulseGuard |
| Calibration method | Platt sigmoid (CalibratedClassifierCV cv='prefit') | Fit on val set (6,000 rows); never touched test set |

**Empirical validation:** The G7 policy-bands plot (`outputs/plots/g7_taiwan_policy_bands.png`) shows the score decile observed default rate vs. predicted PD. Deciles track closely — confirming that "PD=0.20" reliably identifies cohorts with ~20% observed default rate.

**Bayes-optimal threshold confirmation:** The G7 sweep finds empirical minimum expected loss at θ=0.10, matching the Bayes-optimal formula θ* = C_reject / (C_bad + C_reject) = 1/11 ≈ 0.091. This match is only possible if the calibrated probabilities are accurate. It constitutes an independent validation of calibration quality.

**Artifact:** `outputs/evidence/g6_calibration_report.json` · `outputs/plots/g6_calibration_curve.png` · `outputs/plots/g7_taiwan_policy_bands.png`

---

## 10. Threshold Policy

The threshold policy is a separate versioned component from the model. Policy changes do not require model retraining; model changes require policy review.

| Property | Value |
|----------|-------|
| **Policy ID** | `taiwan_real_data_v1.0` |
| **Policy gate** | G7 |
| **Policy artifact** | `outputs/evidence/g7_taiwan_threshold_policy_report.json` |
| **Approve threshold** | PD < 0.20 |
| **Reject threshold** | PD ≥ 0.40 |
| **Review band** | 0.20 ≤ PD < 0.40 |
| **Cost formula** | θ* = C_reject / (C_bad + C_reject) |
| **C_bad** | 10.0 (false approval cost; illustrative) |
| **C_reject** | 1.0 (false rejection opportunity cost; illustrative) |
| **Bayes-optimal θ*** | ≈ 0.091 (confirmed empirically at θ=0.10) |
| **Approve zone population** | 65.1% of test applicants |
| **Review zone population** | 19.0% of test applicants |
| **Reject zone population** | 15.9% of test applicants |
| **Observed DR — approve zone** | 10.7% |
| **Observed DR — review zone** | 27.2% |
| **Observed DR — reject zone** | 62.7% |
| **Expected loss / applicant** | 1.140 (normalised, base cost matrix) |

**Policy selection rationale:** θ_approve=0.20 (not the Bayes-optimal 0.09) because a single threshold of 9% collapses the review band, giving no human-judgment zone for borderline applicants. The 3-zone design trades ~0.45/app EL overhead for operational soundness. This is explicitly documented as a deliberate business trade-off, not a modelling limitation.

---

## 11. Fairness Summary

Fairness was evaluated at G5 on the synthetic Home Credit lane (not directly on Taiwan Default in the current build). The following table summarises findings and documents the gap.

| Check | Dataset | Result | Status |
|-------|---------|--------|--------|
| Disparate Impact (F/M approval ratio) | Synthetic Home Credit | 1.0127 (within 0.80–1.25 band) | G5 PASS |
| Equal Opportunity gap (TPR F vs M) | Synthetic | 2.2 pp | G5 documented |
| Predictive Parity gap (PPV F vs M) | Synthetic | 0.2 pp | G5 documented |
| CODE_GENDER feature rank | Synthetic | #24 / 28 by XGBoost gain | G5 documented |
| Disparate Impact on Taiwan Default | Taiwan Default | **NOT YET COMPUTED** | Deferred to G9 |
| Equal Opportunity gap on Taiwan Default | Taiwan Default | **NOT YET COMPUTED** | Deferred to G9 |

**Critical disclosure:** Taiwan Default contains real demographic fields (SEX, AGE, EDUCATION, MARRIAGE). These fields are present in the model as features — they contribute to the score. No formal fairness audit has been run on the Taiwan Default lane for the G7 threshold policy. The G5 synthetic-lane results are methodology demonstrations; they cannot be cited as fairness evidence for the Taiwan Default model.

**G9 requirement:** A full fairness audit on Taiwan Default — approval rate, TPR, FPR, PPV, ECE, and score distribution by SEX/EDUCATION/MARRIAGE group — at the chosen thresholds (0.20 / 0.40) is required before the G8 governance packet is upgraded to include a fairness determination.

---

## 12. Monitoring Plan

Full monitoring policy is in `docs/G8_MONITORING_AND_INCIDENT_POLICY.md`. Key triggers:

| Trigger | Threshold | Severity | Action |
|---------|-----------|---------|--------|
| PSI on PAY_0 | > 0.10 | WARN | Alert on-call; monitor closely |
| PSI on PAY_0 | > 0.20 | ALERT | Model review; consider freeze |
| PSI on PAY_2 | > 0.10 | WARN | Alert on-call |
| PSI on PAY_2 | > 0.20 | ALERT | Model review; consider freeze |
| ECE drift | > 0.025 (from baseline 0.011) | WARN | Recalibration review |
| ECE drift | > 0.05 | ALERT | Mandatory recalibration before threshold decisions |
| Approve zone observed DR | > 25% (3 consecutive months) | ALERT | Freeze approve zone; mandatory review |
| Approval rate change | > 5 pp month-over-month | WARN | Policy drift investigation |

**Monitoring reference:** G4 synthetic drift lifecycle established PSI > 0.10 = WARN, PSI > 0.20 = ALERT as the operational thresholds. These are applied to PAY_0 and PAY_2 on the Taiwan Default lane.

---

## 13. Known Limitations

1. **2005 vintage data:** Taiwan credit card payment behaviour from 2005 may not reflect current consumer behaviour. Payment infrastructure, credit bureau standards, and macroeconomic conditions have changed materially.

2. **Single-country, single-product scope:** Results are specific to Taiwan revolving credit card accounts. Direct application to other jurisdictions, product types, or credit bureaus is not validated.

3. **No income or EMI features:** FOIR-based hard rules — a standard lending underwriting gate — cannot be implemented on this dataset. Credit utilization and payment status are used as proxies.

4. **PAY_0 encoding ambiguity:** PAY_0 values −2 and 0 appear in data but are not clearly defined in the original paper. Preprocessing treats them numerically. This may introduce noise in the strongest predictive feature.

5. **Reject inference not applied:** The model is trained on all 30,000 accounts (both future defaulters and non-defaulters). In a real deployment, a lender would only observe outcomes for approved accounts, introducing selection bias. Taiwan Default does not simulate this; reject inference is not implemented.

6. **Synthetic cost matrix:** The G7 threshold policy uses C_bad=10, C_reject=1 as illustrative values. Real lender economics — observed charge-off loss rates, net interest margins, manual review costs — would shift the optimal threshold. The policy is a methodology demonstration, not an economics recommendation.

7. **No temporal train/test split:** The 60/20/20 split is random (stratified by default rate) rather than temporal. In a real deployment, the model would be trained on historical months and tested on future months. Random split may overstate performance if temporal autocorrelation is present.

8. **Fairness gap on Taiwan Default:** No fairness audit on Taiwan Default threshold policy. SEX, EDUCATION, MARRIAGE are model features. Approval rates by group at θ=0.20/0.40 are unknown. This is a material gap for any governance determination.

---

## 14. Known Failure Modes

| Failure Mode | Description | Mitigation |
|-------------|-------------|-----------|
| **PAY_0 distribution shift** | PAY_0 (most recent payment status) is the strongest model signal. A macroeconomic shock causing widespread payment delays would shift PAY_0 distribution, causing the model to systematically underpredict default risk. PSI on PAY_0 is the primary drift trigger. | PSI > 0.20 → ALERT → model freeze |
| **Calibration drift** | If the relationship between predicted PD and observed default rate changes — due to population shift or economic regime change — threshold labels (e.g. "PD=0.20 = 20% default risk") become inaccurate. | ECE recalculation monthly; ECE > 0.05 triggers mandatory recalibration |
| **Credit limit inflation** | LIMIT_BAL distribution shift (e.g., due to a credit limit campaign) would alter utilization-related signals without changing actual default risk. | PSI on LIMIT_BAL as secondary monitor |
| **SEX/AGE/EDUCATION-correlated drift** | If approval rate in one demographic group changes significantly due to distributional shift (not model discrimination), this could be misread as a fairness violation — or a real fairness violation could be masked by model drift. | Fairness audit at G9 + periodic approval rate decomposition |
| **Review zone fatigue** | If underwriters systematically approve all review-zone applicants, the review zone becomes a de facto approve zone and the model loses its middle-tier function. | Override reason code analysis; override rate monitoring |
| **LightGBM challenger calibration** | LightGBM challenger was held because its uncalibrated ECE fails the promotion gate. If deployed uncalibrated, LightGBM scores would not support the interpretable threshold policy. | Do not deploy LightGBM without Platt calibration; gate remains open for G9 calibrated comparison |

---

## 15. Human Review Role

Full policy in `docs/G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md`.

The model produces a score. The **policy** routes applicants. Humans intervene in the **REVIEW zone** only (PD 0.20–0.40; 19% of applicants). No human intervention is designed for APPROVE or REJECT zones in the current architecture.

**What the reviewer sees:** Calibrated PD score, LIMIT_BAL, PAY_0 through PAY_6, BILL_AMT1–6, PAY_AMT1–6, AGE, EDUCATION, MARRIAGE. The reviewer does not see the raw XGBoost score (only the calibrated score).

**What the reviewer must not do:** Use SEX as a decision factor. Override without logging a reason code. Approve based solely on demographic information. Use intuition to override a PD > 0.40 to APPROVE without escalation.

---

## 16. Claim Boundaries

| Claim | Status |
|-------|--------|
| "This model estimates 6-month credit card default probability on Taiwan Default test data with ROC-AUC=0.7852, PR-AUC=0.5709, ECE=0.0112" | ✓ SAFE — artifact-backed |
| "Platt calibration reduces ECE 94.6% — enabling interpretable threshold decisioning" | ✓ SAFE — artifact-backed |
| "The G7 3-zone policy routes 65.1% approve / 19.0% review / 15.9% reject on Taiwan test data" | ✓ SAFE — artifact-backed |
| "This is a production-ready credit scoring model" | ✗ FORBIDDEN — `launch_status: NOT_PRODUCTION_READY` |
| "This model complies with ECOA / FCRA / RBI fair-lending requirements" | ✗ FORBIDDEN — no compliance claim |
| "This model is fair across demographic groups" | ✗ FORBIDDEN — Taiwan fairness audit not completed |
| "This model outperforms RiskFrame's Home Credit model" | ✗ FORBIDDEN — different datasets, not comparable |
| "Adverse action codes are assigned" | ✗ FORBIDDEN — not implemented |

**Artifact:** `outputs/evidence/g8_governance_packet_summary.json` (machine-readable claim boundary)
