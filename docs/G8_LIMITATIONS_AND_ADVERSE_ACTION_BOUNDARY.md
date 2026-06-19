# G8 — Limitations and Adverse Action Boundary
## PulseGuard · Taiwan Default Credit Decision Model

**Model ID:** `pulseguard-taiwan-xgb-platt-v1`
**Policy ID:** `taiwan_real_data_v1.0`
**Gate:** G8 — Model Risk Governance
**Date:** June 2026

---

> **Purpose of this document:** Explicit, signed-off documentation of what PulseGuard cannot do, cannot claim, and what would be required for it to do those things. This is not a list of failures — it is a governance discipline artifact. Knowing the boundary of a model's validity is as important as knowing its performance metrics.

---

## 1. No Production Lending Claim

**Explicit statement:** PulseGuard is not a production lending system. No real credit decisions affecting real applicants have been made using this model.

| Claim | Status |
|-------|--------|
| "PulseGuard is deployed in production at any bank, NBFC, or fintech" | ✗ FALSE — never stated; never implied |
| "PulseGuard has been used to approve or reject any real loan or credit card application" | ✗ FALSE |
| "PulseGuard is production-ready" | ✗ FALSE — `launch_status: NOT_PRODUCTION_READY` |
| "PulseGuard could be deployed immediately in a real lending environment" | ✗ FALSE — minimum 7 additional pre-launch requirements (see Governance Sign-off Packet, Section 3) |

**Why this distinction matters:** A resume or portfolio claim of "production credit risk model" implies the system has undergone regulatory review, real applicant validation, and IMV sign-off. PulseGuard has none of these. The correct framing is "production-simulated, research-grade" — meaning the methodology follows production patterns, not that the system is in production.

**Safe portfolio claim:** "PulseGuard demonstrates the full model lifecycle from feature leakage audit to threshold policy to governance sign-off — the same sequence a production credit risk model would require."

---

## 2. No Regulatory Compliance Claim

**Explicit statement:** PulseGuard does not comply with any financial regulation and has not been reviewed by any regulatory body.

| Regulation | Claim Status | Reason |
|-----------|-------------|--------|
| ECOA (Equal Credit Opportunity Act) | ✗ NOT APPLICABLE | US federal law; requires adverse action notices, prohibited basis documentation; neither implemented |
| Regulation B (CFPB) | ✗ NOT APPLICABLE | US federal regulation; requires specific adverse action language; not implemented |
| FCRA (Fair Credit Reporting Act) | ✗ NOT APPLICABLE | US federal law; requires permissible purpose and consumer rights disclosures; not implemented |
| RBI (Reserve Bank of India) Fair Practices Code | ✗ NOT APPLICABLE | India-specific; requires disclosures in local language and form |
| EU AI Act (High-Risk AI Systems) | ✗ NOT APPLICABLE | EU regulation; credit scoring is a listed high-risk use case requiring conformity assessment |
| Basel III / IV capital requirements | ✗ NOT APPLICABLE | Not a regulatory capital model; no stress testing |
| SR 26-2 (Federal Reserve / FDIC / OCC, April 2026) | ✗ NOT CERTIFIED — ALIGNED IN METHODOLOGY | PulseGuard is designed to demonstrate SR 26-2 aligned governance artifacts; it has not been reviewed or certified by any regulator |

**What "SR 26-2 aligned" means and does not mean:**
- ✓ MEANS: Governance artifacts follow the SR 26-2 lifecycle chain (development → validation → deployment → monitoring → sign-off); each artifact is traceable
- ✗ DOES NOT MEAN: External regulatory review completed; SR 26-2 compliance certified; any regulatory approval

**Safe interview phrasing:** "The governance packet is designed to demonstrate SR 26-2 aligned model risk management — meaning I can map each evidence artifact to a corresponding SR 26-2 lifecycle requirement. This is not a compliance certification claim."

---

## 3. No Adverse Action Automation Claim

**Explicit statement:** PulseGuard does not generate adverse action notices. Auto-REJECT decisions do not produce any legally required communication to the declined applicant.

**What adverse action automation requires (and is not in PulseGuard):**

1. **Principal reason codes:** Under ECOA/Regulation B, a declined applicant must receive the principal reasons for denial (e.g., "excessive obligations in relation to income", "derogatory credit history"). PulseGuard's REJECT zone produces a PD score and a zone label — not codified adverse action reasons. SHAP-based reason code assignment is deferred to G9.

2. **Regulatory reason code taxonomy:** CFPB and credit bureau standards define specific reason code lists (e.g., FICO reason codes). These have not been mapped to PulseGuard model features.

3. **Communication channel:** Regulatory adverse action notices must be delivered within a specified timeframe and in a specified format. No communication infrastructure exists.

4. **Right to explanation:** Under some frameworks (EU AI Act, GDPR Article 22), a declined applicant has the right to a meaningful explanation of the automated decision. PulseGuard does not implement this.

**What PulseGuard does produce:**
- A REJECT zone classification with calibrated PD ≥ 0.40
- An audit trail record with the decision, model version, and policy version
- A logged reason that a human could use as the basis for an adverse action notice — but not the notice itself

**Safe portfolio claim:** "The system logs every decision with model version and policy version. In a production system, this audit trail would feed an adverse action notice generation module — that module is deferred to G9."

---

## 4. No Protected-Class Fairness Certification

**Explicit statement:** PulseGuard cannot certify that the Taiwan Default model is fair across protected demographic groups.

**What has been done:**

| Fairness Check | Status | Artifact |
|---------------|--------|---------|
| G5 fairness audit — Disparate Impact (F/M) on synthetic lane | ✓ COMPLETE (DI=1.0127, PASS) | `outputs/evidence/g5_fairness_report.json` |
| G5 fairness audit — Equal Opportunity gap, synthetic | ✓ DOCUMENTED (2.2 pp) | `outputs/evidence/g5_fairness_report.json` |
| CODE_GENDER feature rank on synthetic data | ✓ DOCUMENTED (#24/28) | `outputs/evidence/g5_fairness_report.json` |
| Fairness audit on Taiwan Default at G7 thresholds | ✗ NOT DONE — DEFERRED TO G9 | — |
| SEX approval rate at θ_approve=0.20 on Taiwan Default | ✗ NOT COMPUTED | — |
| EDUCATION/MARRIAGE approval rate at thresholds | ✗ NOT COMPUTED | — |
| Disparate Impact on Taiwan Default lane | ✗ NOT COMPUTED | — |

**Why this gap is material:** Taiwan Default contains real demographic fields (SEX, AGE, EDUCATION, MARRIAGE) as model features. The model's calibrated PD is a function of these fields. The 3-zone policy applies identical thresholds (0.20/0.40) to all applicants — but if the score distribution differs significantly across groups (which it may, given that male/female default rates differ: male DR=24.17%, female DR=20.78%), identical thresholds will produce different approval/rejection rates by group. Whether this constitutes disparate impact under any applicable standard has not been evaluated.

**What "fair" requires (and is not present):**
- Disparate Impact ≥ 0.80 for each protected group at each decision threshold
- Equal Opportunity gap documentation with business justification if gap > 5 pp
- Predictive Parity analysis
- Score distribution overlap analysis by group
- All of the above evaluated on the Taiwan Default test set at thresholds 0.20 and 0.40

**Safe portfolio claim:** "I documented the fairness methodology at G5 using the synthetic lane (DI=1.01, PASS). A complete fairness audit on the Taiwan Default lane at G7 thresholds is the first G9 deliverable. I know where the gap is and what to do to close it."

---

## 5. No Real Bank Economics Claim

**Explicit statement:** The cost matrix (C_bad=10, C_reject=1) is illustrative. It does not represent any real lender's observed charge-off rates, net interest margins, or review costs.

| Assumption | Status | What Real Economics Would Require |
|-----------|--------|----------------------------------|
| C_bad=10 (bad-debt charge-off cost) | ILLUSTRATIVE | Observed historical charge-off rate × average outstanding balance at default |
| C_reject=1 (lost net interest revenue) | ILLUSTRATIVE | Observed net interest margin × expected lifetime of a good customer's relationship |
| C_review=0.3 (manual review cost) | ILLUSTRATIVE | Actual underwriter labour cost + delay cost + compliance overhead |
| C_bad / C_reject = 10:1 ratio | ILLUSTRATIVE | Market-specific; varies by product, portfolio vintage, macroeconomic environment |

**Consequence of illustrative costs:** The Bayes-optimal threshold θ* = C_reject / (C_bad + C_reject) = 9% and the chosen thresholds (0.20 / 0.40) are derived from these illustrative assumptions. A real lender with different observed economics would derive different thresholds. The G7 cost sensitivity analysis (ratios 2:1 to 20:1) shows the direction and magnitude of this sensitivity.

**Safe interview framing:** "The cost matrix is a methodology demonstration. I can show a stakeholder how threshold changes as their economics change — that's the purpose of the sensitivity analysis. The specific values are placeholders; the framework is production-ready."

---

## 6. Taiwan Default Dataset Limitations

These limitations apply specifically to the Taiwan Default dataset and the evidence built on it.

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| **2005 vintage** | Consumer payment behaviour, credit bureau standards, and macroeconomic conditions have changed materially since 2005. Model performance on current Taiwan (or any other) market is unknown. | Use for methodology demonstration only; not for actual current-market prediction |
| **Single product — revolving credit card** | Not directly applicable to consumer instalment loans, home loans, SME loans, or any other product type | Clearly label all claims as "Taiwan credit card context only" |
| **Single geography — Taiwan** | Payment culture, credit infrastructure, and default definitions differ across jurisdictions | Do not extrapolate to other markets without re-training and re-validation |
| **No income / EMI fields** | FOIR-based underwriting rules (a standard credit gate) cannot be applied to this data | Document as a gap; show FOIR methodology on synthetic income field as a design demonstration |
| **PAY_0 encoding ambiguity** | Values −2 and 0 are not clearly defined in the original paper; model treats them numerically | Add to known failure modes; monitor PAY_0 distribution closely |
| **Random (not temporal) split** | The 60/20/20 split is stratified-random, not time-based. In production, temporal split is required. | Document as a methodology gap; temporal split would be mandatory before production |
| **No reject inference** | All 30,000 accounts have observed outcomes; no selection bias from prior lending decisions. In a real deployment, only approved accounts have outcomes — reject inference required. | Document as a known limitation; semi-supervised label propagation deferred to G9 |
| **Sample size** | 30,000 accounts is adequate for methodology demonstration but small by production standards (Home Credit: 307,511; typical bank portfolio: millions) | Performance metrics may have wider confidence intervals than production-scale results |

---

## 7. Synthetic Harness Limitations

The synthetic Home Credit-like dataset (used at G3–G5) has the following additional limitations:

| Limitation | Impact |
|-----------|--------|
| DGP has only 6 signal features | AUC ceiling = 0.6261; deliberately lower than real data (which has many more signals) |
| Synthetic default rate of 8% was calibrated from −4.21 logit intercept | The DGP parameters have no real-world grounding; 8% was chosen to match Home Credit's reported default rate |
| CODE_GENDER is a synthetic proxy (p=[0.65, 0.35]) | Fairness audit results are methodology demonstrations; not real protected-class findings |
| Injected temporal leakage is known and deliberate | G3 FAIL is a designed test, not a real discovery; the feature would never exist in real data with this property |
| PSI drift is scripted (Day 7: shift −0.07; Day 14: shift −0.12) | Drift magnitudes and timing are illustrative; real production drift is gradual and multi-dimensional |

**What synthetic harness results can be claimed:**
- "The monitoring kernel correctly detects the injected drift — PSI fires at the specified thresholds"
- "The leakage audit correctly identifies the injected leakage feature before training"
- "The fairness methodology is correct — the result is illustrative given the synthetic data"

**What synthetic harness results cannot be claimed:**
- "PulseGuard's AUC is 0.6237" (without specifying this is on the synthetic DGP, not a real dataset)
- "PulseGuard has a fair model" (the fairness result is on a synthetic proxy group, not a real protected class)

---

## 8. What Would Be Required for Actual Lending Deployment

A complete list of what is missing from PulseGuard for real-world credit lending deployment. This is a documented gap list, not a failure list.

| Gap | Category | What's Needed |
|-----|----------|--------------|
| Out-of-time model validation | Methodology | Test on data at least 12 months newer than training vintage |
| Independent Model Validation | Governance | IMV unit reviews and challenges model development; issues formal sign-off |
| Adverse action notice system | Regulatory | Reason code assignment (SHAP + regulatory taxonomy); notice delivery infrastructure |
| Fair-lending assessment at thresholds | Regulatory | Disparate Impact, Equal Opportunity, Predictive Parity for SEX/EDUCATION/MARRIAGE at 0.20 and 0.40 |
| Real cost matrix | Economics | Observed charge-off rates, net interest margins, and review costs from lender's portfolio data |
| FOIR engine with income data | Underwriting | Real income and obligation data to compute FOIR; hard-rule pre-screen before model scoring |
| Reject inference study | Statistical | Assessment of approved-only training sample selection bias; propensity weighting or semi-supervised correction |
| Stress testing | Risk | Macroeconomic scenario analysis (e.g., recession, payment infrastructure failure) |
| Model serving infrastructure | Engineering | FastAPI or equivalent with < 100 ms p99 latency; training-serving parity check |
| Applicant consent and data rights | Legal | Data use disclosures; GDPR Article 22 right to explanation (EU) |
| Compliance officer sign-off | Governance | Chief Compliance Officer or equivalent reviews and signs off on all items above |
| Ongoing monitoring infrastructure | Engineering | Production PSI monitoring, ECE monitoring, approval rate tracking, delayed label pipeline |
