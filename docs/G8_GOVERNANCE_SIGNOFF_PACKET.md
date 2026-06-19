# G8 — Governance Sign-off Packet
## PulseGuard · Taiwan Default Credit Decision Model

**Model ID:** `pulseguard-taiwan-xgb-platt-v1`
**Policy ID:** `taiwan_real_data_v1.0`
**Gate:** G8 — Model Risk Governance
**Governance Status:** `PENDING_SIGNOFF` — documentation complete; production launch not approved
**Launch Status:** `NOT_PRODUCTION_READY`
**Date:** June 2026

---

> **Non-production declaration:** This governance sign-off packet is a portfolio-simulation artifact. It documents the governance discipline that a production credit risk model would require. No real credit decisions are made by this system. No regulatory body has reviewed or approved this model. The governance status `PENDING_SIGNOFF` means the artifact chain is complete and ready for review — not that production deployment is imminent.

---

## 1. Role Registry

| Role | Responsibility | PulseGuard Portfolio Holder | Production Equivalent |
|------|---------------|----------------------------|-----------------------|
| **Decision Owner** | Authorises the threshold policy (`taiwan_real_data_v1.0`); owns the approve/review/reject routing decision | `SYNTHETIC_PORTFOLIO_OWNER` | Chief Credit Officer / Head of Lending |
| **Model Owner** | Owns model training, validation, and lifecycle; responsible for champion/challenger evidence chain | `SYNTHETIC_MODEL_OWNER` | Model Development Lead / Senior Data Scientist |
| **Risk Owner** | Independent model validation; challenges assumptions; reviews ECE, AUC, cost matrix; signs off gate report | `SYNTHETIC_RISK_OWNER` | Model Risk Management / Independent Validation Unit |
| **Data Owner** | Responsible for data provenance, lineage, access controls, and feature stability | `SYNTHETIC_DATA_OWNER` | Chief Data Officer / Data Governance Lead |
| **Monitoring Owner** | Operates PSI / ECE drift monitoring; owns alert triage and incident response | `SYNTHETIC_MONITORING_OWNER` | MLOps / Model Monitoring Engineering |
| **Compliance Owner** | Determines whether the model satisfies applicable regulations before deployment | `NOT_ASSIGNED — out of scope` | Chief Compliance Officer / Legal |

---

## 2. Approval Checklist

Each item below must be checked before a governance sign-off can be issued. Current status reflects the PulseGuard portfolio state as of G8.

### 2A — Model Development Evidence

| # | Requirement | Evidence Artifact | Status |
|---|-------------|------------------|--------|
| A1 | Feature leakage audit completed pre-training | `outputs/evidence/leakage_report.json` · `outputs/evidence/group_leakage_report.json` | ✓ COMPLETE (G3) |
| A2 | Dataset profiled: class balance, missingness, demographic distribution | `outputs/evidence/g6_taiwan_data_profile.json` | ✓ COMPLETE (G6) |
| A3 | Train/val/test split documented with seed and stratification strategy | `scripts/g6_champion_challenger.py` (60/20/20, seed=42, stratified) | ✓ COMPLETE (G6) |
| A4 | Preprocessor fit on training data only (no val/test leakage) | `scripts/g6_champion_challenger.py` (`ColumnTransformer.fit_transform(X_tr)`) | ✓ COMPLETE (G6) |
| A5 | Champion model selected via documented 4-gate promotion framework | `outputs/evidence/g6_champion_challenger_report.json` | ✓ COMPLETE (G6) |
| A6 | Calibration applied and verified: ECE < 0.02 on test set | `outputs/evidence/g6_calibration_report.json` (ECE=0.0112) | ✓ COMPLETE (G6) |
| A7 | LightGBM challenger documented as HELD (not REJECTED) with reason | `outputs/evidence/g6_champion_challenger_report.json` | ✓ COMPLETE (G6) |
| A8 | DGP calibration for synthetic harness lane documented | `outputs/evidence/g3_1_dgp_calibration_report.json` | ✓ COMPLETE (G3.1) |

### 2B — Threshold Policy Evidence

| # | Requirement | Evidence Artifact | Status |
|---|-------------|------------------|--------|
| B1 | Bayes-optimal threshold derived with explicit cost matrix (C_bad, C_reject) | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | ✓ COMPLETE (G7) |
| B2 | Threshold formula documented: `threshold = C_reject / (C_bad + C_reject)` | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | ✓ COMPLETE (G7) |
| B3 | Cost matrix assumptions stated as illustrative (not real lender economics) | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | ✓ COMPLETE (G7) |
| B4 | 3-zone policy rationale documented (why not single-threshold) | `docs/G7_threshold_decision_policy_notes.md` (Section 2.4) | ✓ COMPLETE (G7) |
| B5 | Cost sensitivity documented across ≥ 3 ratio variants | `outputs/evidence/g7_cost_sensitivity_report.json` (2:1, 5:1, 10:1, 20:1) | ✓ COMPLETE (G7) |
| B6 | Decision card issued with policy version `taiwan_real_data_v1.0` | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | ✓ COMPLETE (G7) |
| B7 | Retraining trigger defined (PSI and observed DR conditions) | `docs/G7_threshold_decision_policy_notes.md` (Section 4 decision card) | ✓ COMPLETE (G7) |
| B8 | Fallback policy documented (model-unavailable scenario) | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | ✓ COMPLETE (G7) |

### 2C — Risk and Fairness Evidence

| # | Requirement | Evidence Artifact | Status |
|---|-------------|------------------|--------|
| C1 | Disparate Impact audit completed | `outputs/evidence/g5_fairness_report.json` (DI=1.0127, synthetic lane) | ✓ COMPLETE on synthetic lane (G5) · ✗ NOT YET on Taiwan Default |
| C2 | Equal Opportunity gap documented | `outputs/evidence/g5_fairness_report.json` (EOpp=2.2pp, synthetic) | ✓ COMPLETE on synthetic lane · ✗ NOT YET on Taiwan Default |
| C3 | Fairness audit on decision policy at chosen thresholds (0.20/0.40) | — | ✗ DEFERRED — G9 required |
| C4 | Feature rank check: protected attributes not top drivers | `outputs/evidence/g5_fairness_report.json` (CODE_GENDER rank #24/28) | ✓ COMPLETE on synthetic lane · ✗ NOT YET on Taiwan SEX/EDUCATION/MARRIAGE |
| C5 | Reject inference limitation documented | `docs/G8_LIMITATIONS_AND_ADVERSE_ACTION_BOUNDARY.md` | ✓ DOCUMENTED |
| C6 | Independent model validation (IMV) completed | — | ✗ NOT APPLICABLE (portfolio project; no IMV function) |

### 2D — Governance and Documentation Evidence

| # | Requirement | Evidence Artifact | Status |
|---|-------------|------------------|--------|
| D1 | Model card complete | `docs/G8_MODEL_CARD.md` | ✓ COMPLETE (G8) |
| D2 | Governance sign-off packet complete | `docs/G8_GOVERNANCE_SIGNOFF_PACKET.md` (this file) | ✓ COMPLETE (G8) |
| D3 | Monitoring and incident policy complete | `docs/G8_MONITORING_AND_INCIDENT_POLICY.md` | ✓ COMPLETE (G8) |
| D4 | Human review and override policy complete | `docs/G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md` | ✓ COMPLETE (G8) |
| D5 | Limitations and adverse-action boundary documented | `docs/G8_LIMITATIONS_AND_ADVERSE_ACTION_BOUNDARY.md` | ✓ COMPLETE (G8) |
| D6 | Evidence ledger updated with all G8 artifacts | `04_EVIDENCE_LEDGER.md` | ✓ COMPLETE (G8) |
| D7 | Claim boundary updated with G8 safe/forbidden claims | `06_CLAIM_BOUNDARY.md` | ✓ COMPLETE (G8) |
| D8 | Control tower gate log updated | `00_CONTROL_TOWER.md` | ✓ COMPLETE (G8) |

---

## 3. Pre-Launch Checklist (Hypothetical — Not Approved for Production)

This checklist documents what would be required before a production launch could be approved. It is included to demonstrate production-pattern governance discipline — not to imply launch approval is in scope.

| # | Pre-Launch Requirement | Why Required | PulseGuard Gap |
|---|----------------------|--------------|----------------|
| L1 | Independent Model Validation (IMV) sign-off | SR 26-2 requirement; challenger to internal model development | No IMV function; portfolio project |
| L2 | Fair-lending assessment at production thresholds | ECOA / Regulation B requirement | Taiwan Default fairness audit not complete; SEX/EDUCATION/MARRIAGE impact at 0.20/0.40 unknown |
| L3 | Adverse action code assignment system | ECOA / Regulation B Section 202.9 | Not implemented |
| L4 | Data lineage and access controls documented to production standard | SR 26-2 data governance requirement | Taiwan Default is a public research dataset; no access-control governance required |
| L5 | Model validated on recent vintage data (within 24 months of launch) | SR 26-2 model validity requirement | Dataset is 2005 vintage — 19+ year gap |
| L6 | Stress testing under adverse scenarios | Basel / capital adequacy stress test requirement | Not implemented; synthetic drift harness is not equivalent to stress testing |
| L7 | FastAPI serving with training-serving parity check | Operational requirement for real-time decision consistency | Deferred to G9 |
| L8 | Retraining pipeline tested end-to-end on production data | Operational requirement | Not implemented |
| L9 | Rollback procedure tested | Business continuity requirement | Defined in this document (Section 7); not tested |
| L10 | Compliance officer sign-off | Regulatory requirement | Not assigned; out of scope |

**Summary:** 0 of 10 pre-launch requirements are fully satisfied for production. This is the correct and expected state for a portfolio research project. The governance artifact chain is complete; the production deployment prerequisites are documented as gaps, not as failures.

---

## 4. Evidence Required Before Launch

If this model were to be deployed in a real lending environment, the following evidence items would be required in addition to items L1–L10 above:

1. **Out-of-time validation:** Test performance on a dataset at least 12 months newer than the training vintage (post-2006 Taiwan data, or equivalent current-market data)
2. **Champion performance on current population:** Current applicant score distribution vs. 2005 distribution; PSI < 0.10 at deployment
3. **Demographic parity test at deployment thresholds:** Approval rate, TPR, FPR for each SEX/EDUCATION/MARRIAGE group at θ_approve=0.20 and θ_reject=0.40
4. **FOIR integration:** Income and obligation data to support hard-rule pre-screen before model scoring
5. **Real charge-off and revenue data:** To replace the illustrative C_bad=10, C_reject=1 cost matrix with actual lender economics
6. **Reject inference study:** Assessment of selection bias in training data; applicants rejected at origination have no observed outcomes; propensity-weighted or semi-supervised correction required
7. **Model risk management framework sign-off:** Full SR 26-2 / equivalent regulatory lifecycle documentation

---

## 5. Reasons to Block Launch

Any of the following conditions independently blocks deployment:

| Blocker | Condition |
|---------|-----------|
| **Calibration failure** | Test-set ECE > 0.05 |
| **Discrimination floor failure** | Test-set ROC-AUC < 0.70 (minimum viable discrimination for 22% base rate) |
| **Fair-lending failure** | Disparate Impact on any protected demographic group < 0.80 at deployment thresholds |
| **Leakage discovered** | Any FAIL-level finding in FeatureLeakageLens audit on production feature pipeline |
| **Data staleness** | Model not validated on data within 24 months of deployment date |
| **Reject inference not assessed** | No reject inference study or documented justification for omission |
| **IMV not complete** | No independent validation sign-off (SR 26-2 requirement) |
| **Cost matrix not validated** | No real lender economics supporting the C_bad / C_reject ratio used in threshold setting |

---

## 6. Reasons to Require Manual Review (Operational)

During simulated operation (portfolio mode), the following conditions escalate any individual decision to mandatory manual review regardless of the model's PD score:

| Condition | Trigger | Reason |
|-----------|---------|--------|
| PD in review band | 0.20 ≤ PD < 0.40 | Standard 3-zone policy routing |
| Extremely high LIMIT_BAL | LIMIT_BAL > NT$800,000 (> 2σ above mean) | High-exposure accounts warrant human judgment |
| All PAY_0 through PAY_2 missing | NULL in key payment features | Model reliability compromised without primary signal |
| PAY_0 = 8 (max delay) first occurrence | No prior payment history of extreme delay | Model may underpredict for first-time extreme delay |
| Model unavailable | Scoring service down | Fallback policy applies; log all fallback decisions |
| Drift alert active | PSI > 0.20 on PAY_0 or PAY_2 | Model in drift state; increased human scrutiny |
| Score boundary proximity | 0.18 ≤ PD < 0.22 or 0.38 ≤ PD < 0.42 | Near threshold; small score change would change outcome |

---

## 7. Threshold Change Approval Process

The policy (`taiwan_real_data_v1.0`) and the model (`pulseguard-taiwan-xgb-platt-v1`) are separate versioned components. Threshold changes require a separate approval event from model changes.

**Threshold change trigger conditions:**
1. Business decision to change C_bad / C_reject ratio (e.g., macro environment changes bad-debt expectations)
2. Approval rate has drifted > 10 pp over 90 days without corresponding default rate change
3. Risk Owner requests policy review based on observed losses

**Required for threshold change approval:**
1. Updated cost sensitivity analysis showing new optimal θ under revised cost matrix
2. Simulated impact on approval rate, review rate, reject rate at new thresholds
3. Projected EL at new thresholds vs. current
4. Fair-lending impact assessment: does the new threshold disproportionately affect any demographic group?
5. Decision Owner sign-off on new policy version (e.g., `taiwan_real_data_v1.1`)
6. Model Owner confirmation that calibrated probabilities are still valid for the new threshold range
7. Evidence ledger entry updated with new policy artifact

**Threshold changes never require model retraining** (unless the change reveals a calibration gap — e.g., the new threshold operates in a PD range where ECE is poor).

---

## 8. Rollback / Disable Criteria

**Immediate disable conditions (model scoring suspended, fallback policy activated):**

| Condition | Threshold | Response Time |
|-----------|-----------|--------------|
| ECE on recent scored cohort > 0.10 | Monitored monthly | Same day |
| PSI on PAY_0 > 0.30 (severe drift) | Monitored weekly | Same day |
| Model scoring infrastructure failure | Any downtime | Immediate — fallback policy |
| Discovery of data leakage in production feature pipeline | Any FAIL-level finding | Immediate — all decisions voided |
| Fair-lending violation confirmed by legal/compliance | Any DI < 0.80 at deployment thresholds on production data | Immediate |

**Rollback procedure:**
1. Suspend model scoring; activate fallback policy (PAY_0 ≤ 0 AND LIMIT_BAL ≥ NT$50,000 → APPROVE; else REVIEW)
2. Tag all decisions made under drift/failure condition for retroactive review
3. Root cause analysis within 5 business days
4. If model retrained: re-run full G6 champion/challenger gate before redeployment
5. If threshold changed: re-run G7 cost analysis gate before redeployment
6. Rollback to prior model version only if prior version has current-population PSI < 0.20

**Permanent decommission conditions:**
- Training data vintage > 36 months old without out-of-time validation on current data
- Regulatory non-compliance finding that cannot be remediated
- IMV finding that model is fundamentally unfit for purpose
