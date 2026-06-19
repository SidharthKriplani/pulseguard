# 06 — CLAIM BOUNDARY
## PulseGuard · What Can Be Claimed, Where, and When

---

### Claim Status Legend

- **BUILT** — artifact exists, computation ran, metric is real
- **SIMULATED** — computation ran on synthetic or scripted data; accurately labeled as such
- **PROPOSED** — design documented but not yet implemented
- **DEFERRED** — explicitly out of scope for current build
- **SOURCE_REFERENCE** — metric inherited from a prior source project (RiskFrame, LendFlow, FLL); not a PulseGuard-built result

All claims below are currently **DEFERRED** until the corresponding build gate is closed. Update this file as gates close.

---

### Source-Reference Boundary Rule (added G0 patch)

> **RiskFrame, LendFlow, and FeatureLeakageLens produced real metrics. PulseGuard has not re-run them yet.**
>
> The numbers below appear in `04_EVIDENCE_LEDGER.md` (SOURCE_REFERENCE section) as context-setting targets. They describe what prior source projects computed — not what PulseGuard has computed:
>
> | Metric | Value | Source | PulseGuard Gate |
> |--------|-------|--------|----------------|
> | ROC AUC | ~0.7663 | RiskFrame champion XGBoost | G4 |
> | PR AUC | ~0.2611 | RiskFrame champion XGBoost | G4 |
> | ECE (champion) | ~0.0046 | RiskFrame Platt calibration | G4 |
> | ECE (Optuna xgb_v2, held) | ~0.0243 | RiskFrame HPO | G6 |
> | PSI Day 14 | ~0.2358 (ALERT) | RiskFrame synthetic drift | G4 |
> | Disparate Impact | ~1.059 (PASS) | RiskFrame fairness audit | G5 |
> | Leakage audit (SR-12) | 3 WARNs, 0 FAILs | FeatureLeakageLens on Home Credit | **G3 BUILT** — PulseGuard result on synthetic data: 1 FAIL · 2 WARN (SR-12 remains SOURCE_REFERENCE; PulseGuard result differs: dataset is synthetic + injected FAIL feature) |
>
> **Interview answer before the gate closes:**
> *"The source project RiskFrame produced [metric]. PulseGuard will reproduce and extend that when G4 closes — I haven't run it inside PulseGuard yet, so I won't claim that number as PulseGuard evidence."*
>
> **What is forbidden until the gate closes:**
> - "PulseGuard achieves ROC AUC 0.77" — PulseGuard hasn't computed it yet
> - Presenting any SOURCE_REFERENCE number as a PulseGuard metric in any context

---

## Resume-Safe Claims

Claims appropriate for a resume, CV, or portfolio description. Must be defensible in 30 seconds. No metric without an artifact.

| Claim | Status | Gate | Artifact | Caveat |
|-------|--------|------|----------|--------|
| "Built PulseGuard, a risk-decision and model-governance platform merging credit risk scoring, feature leakage detection, PSI drift monitoring, fairness auditing, and underwriting decision simulation" | DEFERRED | G8 | `docs/MODEL_CARD.md` | Do not claim until G8 is closed |
| "Implemented champion/challenger framework (XGBoost vs. LightGBM) with 5-gate promotion framework; champion retained based on ECE superiority despite equivalent AUC" | DEFERRED | G6 | `outputs/evidence/challenger_promotion_decision.json` | "Champion retained" is the documented outcome, not a claim of model superiority |
| "Ran Optuna HPO (50 trials); documented ECE regression case where better AUC did not justify deployment" | DEFERRED | G6 | `outputs/evidence/optuna_hpo_results.json` | Explicitly state: xgb_v2 had better AUC but worse ECE — held, not deployed |
| "Built pre-training feature leakage audit using FeatureLeakageLens (7 checks: target, temporal, overlap, ID proxy, split distribution); injected temporal FAIL confirmed; PulseGuard group leakage check PASS on clean split" | **BUILT** | G3 | `outputs/evidence/leakage_report.json` · `outputs/evidence/group_leakage_report.json` | Dataset is `synthetic_home_credit_like` (Kaggle unavailable); injected FAIL is by design; 2 WARNs on legitimate predictors (DAYS_EMPLOYED, DAYS_ID_PUBLISH) are documented in G3 notes; "mandatory gate" is a design choice, not enforced by production CI |
| "Trained XGBoost champion on calibrated synthetic dataset (8% default rate, 28 features); Platt calibration reduced ECE 86% (0.0111→0.0016); model at 99.6% of Bayes-optimal AUC ceiling" | **BUILT** | G4 | `outputs/evidence/g4_champion_training_report.json` · `outputs/evidence/g4_calibration_report.json` · `outputs/models/champion_calibrated.pkl` | Dataset is `synthetic_home_credit_like`; ROC-AUC 0.6237 is dataset-characteristic (6 signal features, synthetic DGP); source reference 0.77 uses real Home Credit data; must disclose this distinction; Bayes-optimal ceiling claim requires explaining the ceiling calculation |
| "Implemented PSI + KS drift monitoring across 20 numeric features; Day 7 synthetic drift fires WARN (PSI=0.1532); Day 14 fires ALERT (PSI=0.2974 > 0.20)" | **BUILT** | G4 | `outputs/evidence/g4_drift_report.json` · `outputs/plots/g4_drift_psi_ext_source_2.png` | All drift is injected synthetic data, not observed production telemetry; 20 features monitored (univariate PSI/KS only); multivariate drift is a documented blindspot per G0 boundary |
| "Conducted fairness audit: Disparate Impact (1.01, PASS), Equal Opportunity gap (2.2 pp), Predictive Parity gap (0.2 pp) across CODE_GENDER groups; XGBoost gain rank confirms CODE_GENDER is #24/28 features — not a primary driver" | **BUILT** | G5 | `outputs/evidence/g5_fairness_report.json` · `outputs/plots/g5_score_distribution.png` | CODE_GENDER is a synthetic proxy (p=[0.65, 0.35]), NOT a real protected class; 4/5ths DI rule is a heuristic, not a legal standard; feature rank is XGBoost gain (not SHAP — SHAP is G5-forbidden); results apply to synthetic_home_credit_like data only |
| "Designed deterministic-first credit underwriting simulation: FOIR recomputed from raw inputs; hard rules enforce before model call; APPROVE/REVIEW/REJECT routing with versioned policy log" | DEFERRED | G7 | `outputs/evidence/decision_simulation_report.json` | FOIR computed on synthetic income figures, not real bank statements |
| "Produced governance evidence ledger with 15+ artifacts covering the full model lifecycle from feature validation to governance decision" | DEFERRED | G8 | `04_EVIDENCE_LEDGER.md` | "Governance decision" is portfolio-internal, not regulatory sign-off |

---

## LinkedIn-Safe Claims

Shorter, more accessible. Appropriate for LinkedIn project summary or About section bullets.

| Claim | Status | Notes |
|-------|--------|-------|
| "Built an end-to-end model governance platform for credit risk: feature leakage detection → champion/challenger evaluation → drift monitoring → fairness audit → governance sign-off" | DEFERRED | Use "production-simulated" qualifier |
| "Documented the ECE regression case in HPO: a model with better AUC was held because calibration regressed — proving discrimination ≠ deployment fitness" | DEFERRED | This is a genuine and defensible observation |
| "Champion/challenger framework: LightGBM challenger within 0.0002 PR AUC of XGBoost champion; DeLong test not significant; champion retained" | DEFERRED | Accurate framing; no overstatement |
| "Pre-training leakage audit caught high-target-correlation features before a single model was fit" | DEFERRED | Specify: on Home Credit data |

---

## Interview-Safe Claims

What you say when asked directly in a technical interview. Must be accurate, specific, and ready for follow-up.

| Question | Safe Answer | Status |
|----------|------------|--------|
| "What's your ROC AUC?" | "PulseGuard has two lanes. **Synthetic lane (G4):** XGBoost achieves ROC-AUC 0.6237 on synthetic_home_credit_like — at 99.6% of the Bayes-optimal ceiling for that DGP. This lane tests protocol correctness, not business performance. **Real-data lane (G6):** XGBoost with Platt calibration achieves ROC-AUC 0.7852 on the UCI Taiwan credit card default dataset (30,000 rows, 22% default rate). The source reference of 0.7663 used real Home Credit consumer loan data — Taiwan credit card data is a different product." | **BUILT** |
| "How did you handle calibration?" | "Platt sigmoid calibration fit on the validation set in both lanes. **Synthetic lane (G4):** ECE dropped 86% — 0.01105 → 0.00159. **Real-data lane (G6):** ECE dropped 94.6% — 0.2082 → 0.0112. The larger raw ECE on real data is expected: XGBoost's probability outputs on complex real feature spaces are more miscalibrated than on a known synthetic DGP. Platt's correction is essential on real data, not cosmetic." | **BUILT** |
| "How do you know your features aren't leaking?" | "I ran FeatureLeakageLens before training — 7 checks including temporal availability (feature timestamp > outcome timestamp) and training future date scan. I documented every WARN and FAIL finding before fitting a model. The temporally-injected feature (EXTERNAL_BUREAU_QUERY_RESULT__INJECTED) was hard-excluded from the feature pipeline as a result." | DEFERRED (leakage audit BUILT at G3; FLL claim BUILT; interview answer updated with G4 specifics) |
| "How did you detect drift?" | "PSI computed across 30 simulated daily batches per feature, using the training distribution as reference. I injected synthetic drift on Day 7 (EXT_SOURCE_2 shift −0.07) and Day 14 (shift −0.12). Day 7 fires WARN at PSI 0.1532; Day 14 fires ALERT at PSI 0.2974. All 6 WARN days (7–13) correctly classify as WARN; all 17 ALERT days (14–30) correctly classify as ALERT. This is synthetic data, not observed production drift." | **BUILT** |
| "Is this a fair model?" | "Disparate Impact (female/male approval rate ratio) is 1.01 — within the 0.80–1.25 acceptable band. Equal Opportunity gap is 2.2 pp; predictive parity gap is 0.2 pp. CODE_GENDER ranks #24 out of 28 features by XGBoost gain — it's not a primary driver. This is on synthetic_home_credit_like data; CODE_GENDER is a synthetic proxy, not a real protected class. The methodology is production-pattern; the results are illustrative." | **BUILT** |
| "How does challenger promotion work?" | "Four gates: PR-AUC delta ≥ 0.001, ROC-AUC delta ≥ 0.001, ECE increase ≤ 0.005 (blocking calibration gate), Brier increase ≤ 0.003. On Taiwan Default, LightGBM challenger has competitive AUC (0.7742 vs champion 0.7852) but fails the ECE gate uncalibrated (ECE=0.132 vs calibrated champion ECE=0.011). LightGBM is held — not rejected; a follow-on gate with calibrated LightGBM is the natural next step." | **BUILT (G6)** |
| "What is your FOIR calculation?" | "FOIR applies to consumer loan underwriting (EMI/income ratio). Taiwan Default is credit card data — no proposed EMI or income fields. FOIR is documented as a G7/G2 design element for the consumer loan workflow but is not applicable to the Taiwan Default lane. The correct credit card analog is credit utilization (BILL_AMT1/LIMIT_BAL) and payment status pattern (PAY_0 series)." | **BUILT (G7 scope note)** |
| "What governance artifacts do you produce?" | "15+ artifacts: leakage report, calibration report, drift report, fairness report, challenger comparison, HPO results, policy change log, batch scoring runs, delayed label validation, model card, governance sign-off. Each is linked in an evidence ledger with metric, artifact, dataset, method, and confidence level." | DEFERRED |

---

## Forbidden Claims

**Never say these in any context — resume, interview, LinkedIn, or portfolio.**

| Forbidden Claim | Why Forbidden |
|-----------------|---------------|
| "Deployed at a bank / NBFC / fintech" | This is a production-simulated portfolio project on public data |
| "Real loan decisions were made using this system" | All applications are synthetic; no real credit decisions |
| "RBI / Basel / SR 11-7 compliant" | Regulatory compliance requires external certification; this is not certified |
| "Trained on real customer data" | Dataset is Home Credit Default Risk (public Kaggle) or synthetic |
| "Production drift metrics" | All drift is scripted simulation, not observed production telemetry |
| "95% routing accuracy" (from LendFlow) unless benchmarked against labeled ground truth in PulseGuard | LendFlow's 95% was on 20 synthetic applications — do not carry this claim forward without re-running on PulseGuard's test set |
| "Fairness-certified" or "bias-free model" | Fairness audit shows no violation within threshold — does not mean bias-free |
| "Model risk governance framework (regulatory)" | Evidence ledger is a portfolio artifact, not an SR 11-7 or RBI model risk governance framework |
| "The model is production-ready" | No claim of production readiness; only production-pattern methodology |

---

## G8.1 — Data Provenance Audit Claim Boundary

### G8.1 BUILT claims

| Claim | Status | Artifact | Caveat |
|-------|--------|----------|--------|
| "Taiwan Default (UCI) is a verified real public dataset — SHA256 `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` confirmed byte-for-byte identical to live UCI ML Repository download" | **BUILT** | `outputs/evidence/g8_1_data_provenance_audit.json` | SHA256 matches UCI as of June 2026; UCIs dataset page and file may change in future; hash was live-verified at G8.1 |
| "20/20 provenance checks passed: file integrity, size, SHA256, row count, column schema, data quality (0 missing, 0 duplicates), default rate (22.12%), target distribution, ID sequential integrity, content fingerprints vs. Yeh & Lien 2009, synthetic contamination checks, split provenance" | **BUILT** | `outputs/evidence/g8_1_data_provenance_audit.json` | All checks automated and reproducible via `scripts/run_g8_1_data_provenance_audit.py` |
| "Acquisition method documented: file was downloaded by a prior Claude agent session during G5.5 gate from UCI ML Repository; no download script retained in scripts/; source URL documented in g6_taiwan_adapter.py; G8.1 live re-download confirms authenticity" | **BUILT** | `docs/G8_1_DATA_PROVENANCE_AND_REALISM_AUDIT.md` (§1–3) | This is a full transparency disclosure; acquisition method is unusual but provenance is clean |
| "Taiwan Default dataset realism assessment: 7 dataset limitations documented; comparison vs. Home Credit and LendingClub documented; recommendation for stronger realism lane at G9+" | **BUILT** | `docs/G8_1_DATA_PROVENANCE_AND_REALISM_AUDIT.md` (§6–8) | Limitations are documented deficiencies, not hidden; they inform G9 scope |

### G8.1 interview answers

| Question | Safe Answer |
|----------|-------------|
| "How do you know your dataset is authentic?" | "G8.1 computes SHA256 of the raw XLS file and re-downloads from the UCI ML Repository URL. The hashes are identical — `30c6be3a...` — confirming byte-for-byte authenticity. The content fingerprints also match Yeh & Lien 2009's reported statistics: LIMIT_BAL mean of NT$167,484, age range 21–79, exactly 23,364 non-default and 6,636 default records." |
| "Where exactly did the dataset come from?" | "It was downloaded from the UCI ML Repository by an earlier session of the same Claude agent during the G5.5 gate. The user didn't hand it to me manually — the agent fetched it programmatically. I document this explicitly in the provenance audit: the acquisition method is non-standard, but the SHA256 verification proves the file is the authentic UCI dataset. A download script should have been retained in scripts/ — that's a documentation gap I flag." |
| "Is Taiwan Default a strong enough real-data source?" | "It's a bridge, not the destination. It satisfies four criteria: real observed outcomes (not simulated), real payment behaviour signals (ledger-level), real demographic attributes (for a genuine fairness audit), and is peer-reviewed and widely benchmarked. But it has 7 documented limitations: 2005 vintage, single geography, credit card only, no income data, random not temporal split, no reject inference, and 30k rows. Home Credit is the next natural upgrade — 10× larger, multi-year, income proxies — and is planned for G9+." |

### G8.1 forbidden claims

- "The dataset was user-provided" — it was not; the agent downloaded it during G5.5
- "PulseGuard uses a current-vintage credit dataset" — Taiwan Default is 2005; a 19+ year vintage gap is documented
- "The dataset is representative of any current credit market" — 2005 Taiwan, single product; not transferable without re-training

---

## G8 — Governance + Decision Accountability Pack Claim Boundary

### G8 BUILT claims

| Claim | Status | Artifact | Caveat |
|-------|--------|----------|--------|
| "PulseGuard has a complete model card covering purpose, OOS use, dataset, performance, calibration, limitations (8), failure modes (6), monitoring plan, and claim boundaries" | **BUILT** | `docs/G8_MODEL_CARD.md` | Portfolio research project; same structure a production model card requires |
| "Governance sign-off packet documents: 6 ownership roles, 4-section approval checklist (24/25 COMPLETE), 10 pre-launch gaps, 8 launch blockers, threshold-change approval process, rollback criteria" | **BUILT** | `docs/G8_GOVERNANCE_SIGNOFF_PACKET.md` | Governance status = PENDING_SIGNOFF; launch status = NOT_PRODUCTION_READY; no real regulatory body reviewed this |
| "Monitoring policy defines 5 independent monitors (PSI, ECE, score distribution, approval rate, delayed-label DR) with WARN/ALERT/CRITICAL thresholds and response SLAs" | **BUILT** | `docs/G8_MONITORING_AND_INCIDENT_POLICY.md` | Thresholds validated against G4 synthetic drift kernel; production telemetry is simulated |
| "Human review policy specifies: reviewer information access, 6 prohibited behaviours, override logging JSON schema, 10 reason codes, 8 audit trail fields, escalation path, override rate monitoring" | **BUILT** | `docs/G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md` | REVIEW zone is 19% of test applicants; in portfolio, no real underwriters review decisions |
| "Limitations boundary explicitly declares: no production lending, no regulatory compliance, no adverse-action automation, no fairness certification, no real bank economics — with 11-item what-would-be-needed list" | **BUILT** | `docs/G8_LIMITATIONS_AND_ADVERSE_ACTION_BOUNDARY.md` | These are documented gaps, not model failures |
| "Machine-readable governance summary: launch_status=NOT_PRODUCTION_READY, 13 evidence artifacts logged, 10 forbidden claims, 7 G9 deliverables" | **BUILT** | `outputs/evidence/g8_governance_packet_summary.json` | JSON is the canonical machine-readable governance record for this model version |
| "Taiwan Default fairness gap documented as G9 first deliverable — male DR=24.17%, female DR=20.78%; approval rates at 0.20/0.40 thresholds by SEX/EDUCATION/MARRIAGE not yet computed" | **BUILT** | `docs/G8_MODEL_CARD.md` (Section 11) · `outputs/evidence/g8_governance_packet_summary.json` | Gap is documented and prioritised; not hidden |

### G8 interview answers

| Question | Safe Answer |
|----------|-------------|
| "Is your model production-ready?" | "No — and the governance packet documents exactly why. There are 10 pre-launch requirements that are unmet: no IMV sign-off, no Taiwan Default fairness audit at the decision thresholds, no adverse action notice infrastructure, no out-of-time validation, 2005 vintage data, and no compliance officer review. The launch_status is explicitly NOT_PRODUCTION_READY. I can tell you what each gap requires to close — that's the point of the governance artifact." |
| "What does your model card cover?" | "16 sections: model purpose, intended vs out-of-scope use, dataset (Taiwan Default, 30k rows, 2005 vintage, 22.12% DR), target definition and timing, model family (XGBoost + Platt, 57 trees, 23 features), performance (ROC=0.7852, ECE=0.0112), calibration summary, threshold policy (taiwan_real_data_v1.0), fairness status (synthetic lane: DI=1.01 PASS; Taiwan Default: not yet audited), monitoring plan, 8 limitations, 6 failure modes, and full claim boundaries." |
| "How would you handle a model failure in production?" | "The monitoring policy defines 5 independent monitors. If ECE exceeds 0.10 — meaning the model's probability labels no longer correspond to observed default rates — all decisions route to REVIEW and the model is frozen pending investigation. The response SLA for a CRITICAL alert is 30 minutes. Rollback reinstates the previous model version if its PSI on current population is below 0.20. Every freeze event generates a root-cause report within 24 hours." |
| "What happens if a reviewer makes a biased decision?" | "Override reason codes are logged for every REVIEW decision. SEX is not presented to reviewers — it's withheld from the decision interface. If RC-99 (Other) reason codes spike or if approval rates differ systematically by demographic group across reviewers, that's flagged in the override rate monitoring. Override decisions are immutable tamper-evident JSONL. If a real compliance concern is found, the escalation path goes to the compliance officer." |
| "What's your governance sign-off status?" | "PENDING_SIGNOFF — meaning the documentation chain is complete and ready for review, but the model has not received a formal production approval because 10 pre-launch requirements are unmet. In a production environment, the Risk Owner and IMV unit would issue the sign-off after reviewing the evidence chain. In the portfolio, I'm playing the role of the governance framework builder — the sign-off itself is deliberately not self-issued." |

### G8 forbidden claims

- "PulseGuard is SR 26-2 compliant or certified" — methodology is aligned; no external certification
- "The governance sign-off means PulseGuard is approved for production" — sign-off is PENDING; launch status is NOT_PRODUCTION_READY
- "The monitoring policy is in operation" — monitoring is defined and architecturally implemented; production telemetry is simulated
- "Adverse action notices are generated" — not implemented; explicitly documented as a gap
- "The fairness audit is complete" — G5 synthetic lane is complete; Taiwan Default fairness at G7 thresholds is G9's first deliverable

---

## G7 — Threshold / Decision Policy Claim Boundary (taiwan_primary_patch_v1)

### G7 BUILT claims

| Claim | Status | Artifact | Caveat |
|-------|--------|----------|--------|
| "3-zone policy `taiwan_real_data_v1.0` (PRIMARY lane): APPROVE PD<0.20 (65.1%, observed DR=10.7%) / REVIEW 20–40% (19.0%, DR=27.2%) / REJECT PD≥40% (15.9%, DR=62.7%); EL=1.140/app under C_bad=10, C_reject=1, C_review=0.3" | **BUILT** | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | Synthetic cost assumptions; not real lender economics; Taiwan credit card context only; policy name is `taiwan_real_data_v1.0` not `synthetic_v1.0` |
| "Bayes-optimal formula: threshold = C_reject / (C_bad + C_reject) = 1/11 ≈ 9%; empirical sweep on Taiwan test set confirms minimum EL at θ=0.10" | **BUILT** | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | Valid only for this cost matrix and calibrated model; formula uses C_bad/C_reject notation (not C_FN/C_FP) |
| "Calibrated probabilities produce lower expected loss than raw at all thresholds; calibration is essential for interpretable decisioning at any threshold" | **BUILT** | `outputs/plots/g7_taiwan_cost_curve.png` | Specific to XGBoost Platt on Taiwan Default test set (6,000 rows) |
| "Cost sensitivity: optimal θ moves 0.32→0.07 as C_bad/C_reject ratio moves 2→20; approval rate stable ~78% across all tested ratios" | **BUILT** | `outputs/evidence/g7_cost_sensitivity_report.json` | 4 ratios tested (2:1, 5:1, 10:1, 20:1); synthetic; real ratios require observed charge-off and revenue data |
| "Score distribution by class and policy band visualised; decile reliability plot confirms calibrated PD matches observed default rates in each band" | **BUILT** | `outputs/plots/g7_taiwan_policy_bands.png` | Taiwan Default test set (6,000 rows); PD=0.20 ≈ 20% observed DR confirmed in decile plot |
| "Synthetic data is retained ONLY as a secondary stress-test harness — not as the primary threshold policy lane; policy is grounded in Taiwan real data" | **BUILT** | `docs/G7_threshold_decision_policy_notes.md` (Section 3) | Architecture claim; validates G5.5 lane decision is honoured in G7 |

### G7 interview answers

| Question | Safe Answer |
|----------|-------------|
| "How did you choose your threshold?" | "Threshold is a business decision, not a model parameter. I define a cost matrix with two terms: C_bad (cost of approving a defaulter — bad debt, normalised to 10) and C_reject (cost of rejecting a good applicant — lost revenue, normalised to 1). The Bayes-optimal formula is: threshold = C_reject / (C_bad + C_reject) = 1/11 ≈ 9%. My empirical minimum-expected-loss sweep on the Taiwan test set confirms θ=0.10. I then chose a 3-zone policy at 20%/40% rather than the mathematical optimum — a 9% threshold collapses the review band." |
| "What data did you use for the threshold policy?" | "Taiwan Default — the real UCI credit card dataset, 30,000 rows, 22.12% default rate, actual 6-month payment history. Not synthetic data. G5.5 established Taiwan as the primary real-data lane; G7 honours that. Synthetic data is retained only for stress-testing failure modes — it's not the headline policy." |
| "What's in the review zone?" | "Applications with PD between 20% and 40% — 19% of the test set. Observed default rate in this zone is 27.2%. These go to manual underwriting. The reviewer examines payment history (PAY_0 through PAY_6), credit utilization (BILL_AMT1/LIMIT_BAL), and recent payment amounts. The review cost (C_review=0.3, normalised to 30% of C_reject) is explicit in the expected-loss calculation." |
| "Why C_bad and C_reject instead of C_FN and C_FP?" | "C_FN and C_FP are generic statistical labels — a business stakeholder wouldn't know what C_FN means. C_bad = 'cost of approving a defaulter (bad debt)' and C_reject = 'cost of rejecting a good applicant (lost revenue)' are immediately interpretable. The formula threshold = C_reject/(C_bad+C_reject) is something a non-technical lending manager can audit: if bad debt is 10× the opportunity cost, approve below 9%." |
| "What triggers retraining?" | "Two conditions: PSI > 0.20 on PAY_0 or PAY_2 (primary payment-status features), or observed default rate in the approved cohort exceeding 25%. First catches feature distribution drift; second catches calibration drift." |

### G7 forbidden claims

- "PulseGuard makes production credit decisions" — portfolio simulation; no real applicants
- "This policy satisfies ECOA, FCRA, RBI, or any regulatory standard" — no compliance claim
- "20% threshold is a regulatory capital boundary" — it is a synthetic cost-matrix-derived threshold
- "Adverse action notices are generated" — not implemented
- "FOIR hard rules are enforced" — FOIR not applicable to Taiwan credit card data (no income/EMI fields)
- "The primary policy is synthetic_v1.0" — the policy name was patched to `taiwan_real_data_v1.0`; synthetic = secondary stress-test only
- "C_FN / C_FP cost notation" — correct notation is C_bad (false approval cost) and C_reject (false rejection opportunity cost)

---

## G6 — Real-Data Champion/Challenger Claim Boundary

### G6 BUILT claims

| Claim | Status | Artifact | Caveat |
|-------|--------|----------|--------|
| "XGBoost champion on Taiwan Default: ROC-AUC=0.7852, PR-AUC=0.5709, ECE=0.0112 after Platt calibration (94.6% reduction from 0.2082)" | **BUILT** | `outputs/evidence/g6_champion_challenger_report.json` | Taiwan credit card default data only; not Home Credit; not consumer loan; 6,000-row held-out test set |
| "LightGBM challenger held — did not improve PR-AUC over calibrated champion (Δ=−0.018); ECE gate blocks uncalibrated challenger" | **BUILT** | `outputs/evidence/g6_champion_challenger_report.json` | LightGBM was not calibrated in this gate; fair comparison would require calibrating both; documented limitation |
| "Platt calibration reduces ECE 94.6% on real credit data — validates calibration gate as essential on complex feature spaces" | **BUILT** | `outputs/evidence/g6_calibration_report.json` | Specific to XGBoost on this dataset/vintage |
| "Two-lane architecture operational: synthetic harness retained for failure tests; Taiwan Default is primary G6 evidence" | **BUILT** | `docs/G6_real_data_champion_challenger_notes.md` · G5.5 artifacts | Architecture claim; no single metric captures the two-lane design |

### G6 interview answers

| Question | Safe Answer |
|----------|-------------|
| "What's your AUC on real data?" | "On the Taiwan UCI credit card default dataset — 30,000 rows, 22% default rate, real demographic variables — XGBoost with Platt calibration achieves ROC-AUC 0.7852 and PR-AUC 0.5709. ECE drops from 0.208 to 0.011 after Platt calibration — 95% reduction. This is substantially better calibration than the raw model." |
| "What did the challenger comparison find?" | "LightGBM challenger has competitive discrimination (ROC-AUC 0.7742) but fails the 4-gate promotion test: it does not improve PR-AUC over the calibrated champion and has higher ECE uncalibrated. The champion is retained. A follow-on gate where LightGBM is also calibrated before comparison is the natural next step." |
| "Your real-data AUC is higher than your source reference — does that mean your model is better?" | "No — it means different datasets. Taiwan credit card default has stronger payment history features and 22% base rate vs. Home Credit's 8%. A higher base rate and 6 months of sequential payment data make classification slightly easier. The fair comparison is within the same dataset, not across datasets." |

### G6 forbidden claims

- "XGBoost Platt calibrated achieves ROC-AUC 0.7852 on Home Credit" — this is Taiwan Default
- "LightGBM is inferior to XGBoost in general" — only tested uncalibrated vs. calibrated champion; unfair comparison
- "94.6% ECE reduction proves PulseGuard is production-calibrated" — this is a research portfolio result
- "The two-lane architecture means PulseGuard is a complete real-world system" — it demonstrates the architecture; not a production claim

---

## G5.5 — Two-Lane Architecture Claim Boundary

> **All performance claims after G5.5 must specify the data lane.**

### Safe phrasing after G5.5 (before G6):
> "PulseGuard operates two lanes. The synthetic harness lane uses a calibrated logistic DGP to prove protocol correctness — injected temporal leakage caught pre-training, controlled drift triggers at Day 7/14, proxy fairness audit complete. The real-data lane uses the UCI Taiwan credit card default dataset (30,000 clients, 6-month payment history, real demographics: sex, age, education, marriage) for business-credible champion/challenger evaluation and genuine fairness analysis."

### Required disclosures when citing Taiwan Default:
- Product: credit card default, not consumer loan
- Geography: Taiwan, 2005 vintage
- Size: 30,000 rows (smaller than Home Credit 307,511)
- Demographics: real fields (SEX/AGE/EDUCATION/MARRIAGE) present in data, no synthetic proxy
- Download: UCI ML Repository, no authentication, reproducible

### Transition path to Home Credit:
> "The pipeline is designed so only the data source changes when Home Credit becomes available. All scripts, feature pipeline, and evaluation framework run identically. Home Credit produces directly comparable results to the source-reference metrics (SR-1: AUC 0.7663) — Taiwan results will not."

### Forbidden after G5.5:
- "Taiwan results confirm what RiskFrame found" — different dataset, different product, different market
- "PulseGuard now has real-world results" — real data, not real deployment; results are portfolio evidence
- "Removing synthetic harness" — synthetic lane remains the controlled failure-mode test environment

---

## SR 26-2 Alignment Claims (Interview-Safe After G8)

| Claim | When Safe | Gate |
|-------|----------|------|
| "Governance artifacts are designed to be SR 26-2 aligned — I can map each evidence artifact to the corresponding SR 26-2 lifecycle requirement" | After G8 model card is written | G8 |
| "PulseGuard simulates the governed model lifecycle chain that SR 26-2 requires: development → validation → deployment → monitoring → governance sign-off" | After G8 governance_signoff.md exists | G8 |
| "The retraining and decommissioning triggers are explicitly defined in the model card — a SR 26-2 requirement that most portfolio projects ignore" | After G8 model card section is complete | G8 |

**Never claim:** "SR 26-2 compliant" or "SR 26-2 certified" — these require external regulatory validation.

---

## Reject Inference Boundary Claim (Always)

| Context | Safe Phrasing |
|---------|--------------|
| Resume | Do not mention reject inference unless the JD calls for it |
| Interview | "I trained the model on approved applicants — Home Credit only provides outcomes for loans that were funded. This is selection bias (reject inference problem). I documented it as a known limitation in the model card and quantified its expected calibration impact. I did not implement reject inference in the portfolio version; the correct approach is propensity-weighted augmentation or semi-supervised label propagation to rejected applicants." |
| LinkedIn | Not needed |
| Forbidden | "I solved the reject inference problem" or "I corrected selection bias" unless G9 implements it |

---

## Deferred Claims

Claims that could be made if later gates are built — do not claim until the corresponding gate is closed.

| Deferred Claim | Requires | Gate |
|---------------|---------|------|
| "Hybrid RAG over credit policy corpus with RAGAS faithfulness" | LendFlow RAG rebuilt and re-evaluated in PulseGuard on 50+ applications | G7+ |
| "Multi-signal risk fusion: financial health + contagion + sentiment" | NexusSupply integration | G9 |
| "FastAPI serving with training-serving parity test" | FastAPI app built in PulseGuard | G9 |
| "Streamlit dashboard" | Dashboard built | G9+ |
| "Graph contagion risk scoring" | NexusSupply graph layer integrated | G9 |
| "Altman Z-score financial health signal" | NexusSupply financial scorer integrated | G9 |
| "Group leakage check (cross-validation fold contamination) — FLL roadmap item, native FLL implementation" | FeatureLeakageLens roadmap item implemented natively in FLL | G9 | Note: PulseGuard-specific entity contamination check (`scripts/group_leakage_check.py`) is **BUILT at G3** as a PulseGuard extension (not the FLL-native implementation). The G9 item refers to using FLL's own future group-leakage API if/when it ships. |
| "Walk-forward temporal split validator" | FeatureLeakageLens roadmap item implemented | G9 |
| "Reject inference implemented via propensity-weighted augmentation" | G9 reject inference module | G9 |
| "Calibration by group (calibration curves per demographic group)" | G9 fairness depth module | G9 |

## Permanently Forbidden (Never Claim Even if NexusSupply Results Are Tempting)

- "CV AUC 1.00 on financial health model" — NexusSupply's AUC 1.00 is circular (labels derived from features used for training on synthetic data). Never claim this.
- "95% routing accuracy on 20 applications" — 20 applications is not a statistically meaningful evaluation. Re-run on 50+ applications in PulseGuard and report with appropriate confidence intervals.

---

## RISKFRAME-GOLD AUDIT — Claim Boundary

**Audit verdict:** STRONG_NEEDS_MEAT_PASS · Score: 104/150 (69%) · Audit doc: `docs/PULSEGUARD_RISKFRAME_GOLD_AUDIT.md` · Evidence: `outputs/evidence/pulseguard_riskframe_gold_audit.json`

### RISKFRAME_GOLD_AUDIT BUILT claims

| Claim | Status | Artifact | Caveat |
|-------|--------|----------|--------|
| "Ruthless 15-dimension RiskFrame audit completed: score 104/150 (69%), verdict STRONG_NEEDS_MEAT_PASS — foundations strong, data realism and decision economics thin" | **BUILT** | `outputs/evidence/pulseguard_riskframe_gold_audit.json` | Score is an internal governance assessment, not a third-party certification |
| "Taiwan Default assessed as BRIDGE_ONLY: verified real public data with 8 documented limitations (2005 vintage, single product, no income, random split, 30k rows, no reject inference complexity)" | **BUILT** | `docs/PULSEGUARD_RISKFRAME_GOLD_AUDIT.md` §D | Limitations are documented deficiencies openly; Home Credit is recommended next |
| "15 ambition gaps documented with severity, build timing, and unlocked claims per gap" | **BUILT** | `outputs/evidence/pulseguard_riskframe_gold_audit.json` → top_15_ambition_gaps | Gaps are known-acknowledged; not hidden |
| "7 delete-or-downgrade claims identified: cost matrix overclaiming, LightGBM rejected claim, synthetic AUC credit risk claim, SR 26-2 compliance claim, Taiwan representativeness claim, fairness certification claim, production readiness claim" | **BUILT** | `outputs/evidence/pulseguard_riskframe_gold_audit.json` → delete_or_downgrade_claims | These claims must not appear in any portfolio communication |
| "Next gate confirmed as G9: Taiwan fairness audit (DI/EOpp/PPV at θ=0.20/0.40 for SEX/EDUCATION/MARRIAGE) + calibrated LightGBM champion/challenger + SHAP adverse reason codes + KS statistic" | **BUILT** | `outputs/evidence/pulseguard_riskframe_gold_audit.json` → next_gate_recommendation | G9 does not require new data; unblocked now |
| "Home Credit realism lane scheduled as G10 BeastMax primary lane: 307k rows, multi-vintage, reject inference required, temporal split possible, income fields available" | **BUILT** | `docs/PULSEGUARD_RISKFRAME_GOLD_AUDIT.md` §D | G10 requires Kaggle registration and significant preprocessing; do not start until G9 complete |

### RISKFRAME_GOLD_AUDIT safe interview claims

| Question | Safe Answer |
|----------|-------------|
| "Is PulseGuard a serious credit risk governance dossier or just a demo?" | "Serious, with documented gaps. The RiskFrame audit scores it 104/150 on 15 dimensions — strong on governance discipline, calibration methodology, and claim boundary precision; thin on data realism and decision economics. I can tell you exactly where it's thin and what it would take to close each gap: Home Credit for realism, real lender economics for the cost matrix, temporal validation for stability." |
| "Why is Taiwan Default a bridge and not your final dataset?" | "Eight documented limitations: 2005 vintage (19-year gap), single geography (Taiwan), single product (revolving credit cards), no income/FOIR data, random not temporal split, no reject inference complexity, PAY_0 encoding ambiguity, and 30k rows. It's real and SHA256-verified — it demonstrates real calibration, real payment signals, and real demographics for a genuine fairness audit. It's not the strongest evidence available. Home Credit is." |
| "What's the gap between where PulseGuard is now and RiskFrame-Gold?" | "26 points from GOLD_CANDIDATE, 46 points from RISKFRAME_GOLD. The biggest gaps: data realism (4/10) needs Home Credit at G10 (+3pts); evaluation validity (6/10) needs calibrated LightGBM comparison and bootstrap CI at G9 (+2pts); decision economics (4/10) needs real charge-off data or published benchmark NIM (+2pts). Gold requires all of those plus reject inference implementation, WOE/IV scorecard, and temporal validation." |
| "What would you delete from your current dossier?" | "Seven specific claims: (1) any framing that implies Taiwan cost matrix is based on real lender economics, (2) LightGBM 'rejected' — it's HELD pending fair comparison, (3) synthetic AUC=0.62 cited as credit risk performance, (4) SR 26-2 compliant — aligned only, (5) Taiwan as representative of any current market, (6) fairness certified, (7) production-ready. All of these are documented in the delete_or_downgrade list in the audit JSON." |

### RISKFRAME_GOLD_AUDIT forbidden claims

- "PulseGuard has passed the RiskFrame-Gold audit" — score is 104/150; verdict is STRONG_NEEDS_MEAT_PASS, not RISKFRAME_GOLD
- "Taiwan Default is the best available credit risk dataset" — it is the verified bridge; Home Credit is materially stronger
- "The audit confirms production readiness" — it confirms governance discipline; launch_status remains NOT_PRODUCTION_READY
- "104/150 is a high score" — it is 69%; GOLD requires 87%+; present the score honestly
- "Audit validates LightGBM rejection" — audit confirms LightGBM is HELD pending calibrated rematch, not definitively inferior

---

## G9A HOME CREDIT — Claim Boundary (2026-06-17)

### G9A built claims (✅ SAFE)

| Claim | Artifact |
|---|---|
| "Home Credit Default Risk: 307,511 applicants, 8.07% DR, 7 side-tables, 57.4M total rows" | `g9a_home_credit_data_audit.json` |
| "140 features from multi-table engineering: ratios, behavioural aggregates, composite score" | `g9a_feature_factory_report.json` + `g9a_splits.pkl` |
| "CatBoost champion: AUC=0.7716, ECE=0.0054 post-Platt, KS=0.41 on 61k held-out test" | `g9a_model_tournament_report.json` |
| "LightGBM_Monotonic governance alternative: AUC=0.7203, ECE=0.0016, 15 monotone constraints" | `g9a_calibration_governance_report.json` |
| "12-model tournament run; 2 hard-failed with documented reason (TabNet CPU, sklearn GBM)" | `g9a_model_tournament_report.json` |
| "TabNet hard-fail: ~6min/epoch CPU vs ~15s GPU; estimated 400-800h on 184k rows; no GPU" | Code comment + tournament report |
| "SHAP top feature: EXT_SOURCE_3; first behavioural feature: INST_LATE_RATIO (rank #5)" | `g9a_shap_summary.json` + plot |
| "scale_pos_weight = 11.39; stratified 60/20/20 split seed=42; DR 0.0807 preserved" | `g9a_home_credit_data_audit.json` |
| "Local LM Studio governance assistant: BM25 policy RAG, ASSISTIVE_ONLY, offline" | `src/pulseguard/policy_rag.py` + `llm_governance_assistant.py` |
| "Reject inference: documented as MNAR known limitation, not implemented" | `g9a_home_credit_data_audit.json` |
| "Temporal split not possible: no timestamps; SK_ID_CURR DR stable across quintiles" | `G9A_VINTAGE_TEMPORAL_REALISM_AUDIT.md` |

### G9A safe interview answers

| Question | Safe Answer |
|---|---|
| "What is your champion model?" | "CatBoost with Platt sigmoid calibration. AUC 0.7716 on a 61k held-out test set. Pre-calibration ECE was 0.32 — terrible — Platt brings it to 0.0054, which is production-quality. KS is 0.41. Champion was selected on AUC plus calibration ECE, not AUC alone." |
| "Why not LightGBM?" | "LightGBM came in at 0.72 AUC on this dataset vs CatBoost's 0.77 — a 5-point gap. However, LightGBM with monotone constraints on 15 features is documented as the governance-preferred alternative under SR 26-2 directional interpretability requirements. The tradeoff is 5 AUC points for full directional compliance. That's an explicit documented choice, not a dismissal." |
| "Did you do reject inference?" | "No. Home Credit contains approved applicants only — it's an MNAR selection bias. I documented it as a known limitation. Implementing reject inference correctly would require semi-supervised or counterfactual methods, which is a separate workstream. I was explicit about that limitation rather than hiding it." |
| "What is BEHAVIORAL_RISK_SCORE?" | "A composite payment stress feature: 0.4 × instalment late ratio + 0.3 × credit card DPD ratio + 0.2 × POS DPD ratio + 0.1 × bureau overdue ratio. Weights reflect data volume and signal strength — instalments have the most observations and the strongest individual signal. NaN inputs are filled with 0 before computing the composite." |

### G9A forbidden claims

- "AUC > 0.78 on Home Credit" — champion is 0.7716; do not round up
- "Validated on out-of-time data" — no timestamps; stratified random split only
- "Reject inference implemented" — documented as known limitation, not implemented
- "Model is production-ready for regulated credit scoring" — no independent validation
- "The model is fair across protected classes" — no fairness audit in G9A scope
- "LightGBM is the champion" — CatBoost is champion; LightGBM is governance alternative
- "TabNet would have scored lower" — we cannot claim results we did not compute
- "This replicates a production Home Credit scorecard" — approved-applicants only; single geography

---

## GOLD PASS 1 — Claim Boundary Patch (2026-06-17)

**Gold Pass 1 verdict:** PASS · safe_to_tune=true · 7 audit JSONs produced

### Strongest defensible current claim (verbatim)

> "I ran a structured pre-tuning audit over the Home Credit pipeline before any hyperparameter search. The audit covers 23 artifacts (all pass), the data spine across 57.4M rows (21/21 checks), a 10-check leakage audit (safe_to_tune=true — no target leak, no post-outcome proxies, no test contamination), a temporal feasibility analysis (SK_ID_CURR confirmed not a time proxy, DR range 0.003 across quintiles), a full tournament quality extraction (PR-AUC, KS, Brier, ECE for all 12 models), and a RAG governance audit (BM25 abstain verified functional, ASSISTIVE_ONLY tagging confirmed). The baseline CatBoost achieves AUC=0.7716, PR-AUC=0.2637, KS=0.41, ECE=0.0054 without any hyperparameter tuning. These are documented baselines, not final numbers — Pass 2 Optuna tuning is the next step."

### Gold Pass 1 safe claims

| Claim | Artifact |
|---|---|
| "23/23 G9A artifacts verified — all exist, non-stale, cross-referenced metrics consistent" | `gold_pass1_artifact_audit.json` |
| "21/21 data spine checks PASS — DR=0.0807 consistent across train/val/test, 0 ID overlap" | `gold_pass1_data_spine_validation.json` |
| "10/10 leakage checks PASS — TARGET not in features, Platt fit on val only, test never seen during training" | `gold_pass1_leakage_audit.json` |
| "Temporal feasibility FEASIBILITY_LIMITED — no timestamps, SK_ID_CURR DR range=0.0033 confirms shuffled dataset" | `gold_pass1_temporal_vintage_feasibility.json` |
| "CatBoost baseline: AUC=0.7716 PR-AUC=0.2637 KS=0.4094 ECE=0.0054 — BASELINE_NOT_TUNED" | `gold_pass1_tournament_quality_audit.json` |
| "BM25 policy RAG verified functional: abstain fires on off-topic queries (top_score<0.25 threshold), citations present, ASSISTIVE_ONLY enforced" | `gold_pass1_rag_llm_governance_audit.json` |
| "Pass 2 tuning plan ready: Optuna TPE, 100 trials × 5 models, composite champion score" | `docs/PULSEGUARD_GOLD_PASS2_TUNING_PLAN.md` |

### Gold Pass 1 clarifications and caveats

| Claim to clarify | Correct framing |
|---|---|
| "CatBoost AUC=0.7716 is the final champion score" | "That is the **baseline** score with no hyperparameter tuning. Final champion is determined after Pass 2 Optuna search. Provisional champion only." |
| "BM25 abstain threshold is 0.5" | "Threshold is **0.25** for the current single-document corpus. Documented for scale-up to 0.5 at 5+ policy documents. Both values and the calibration method are in `policy_rag.py`." |
| "Temporal split was performed" | "No temporal split is possible — dataset has no timestamps and SK_ID_CURR is not a time proxy (DR range=0.003 across quintiles). Stratified random split at seed=42 is the methodology. Documented limitation." |
| "The model was tuned with Optuna" | "Optuna tuning is **Pass 2** — not yet run. The tournament used default/sensible parameters as a documented baseline." |

### Gold Pass 1 forbidden claims

- "The champion is finalized" — champion is PROVISIONAL until Pass 2 Optuna search completes
- "AUC=0.7716 after hyperparameter tuning" — this is the **untuned** baseline; never claim it as a tuning result
- "Abstain threshold is 0.5 (validated)" — threshold is 0.25 for current single-doc corpus; 0.5 is the scale-up target
- "RAG has been tested against a live LLM" — LM Studio governance layer requires local LM Studio running; audit verified retrieval only
- "The pipeline is leakage-free by construction" — audit verified no leakage was found; future feature additions require re-audit

---

---

## GOLD PASS 2 — Claim Boundary Patch (2026-06-17)

**Gold Pass 2 verdict:** COMPLETE · Champion: LightGBM_monotonic + Platt · Test AUC=0.7769 · safe_to_pass3=true

### Strongest defensible current claim (verbatim)

> "I ran a validation-only hyperparameter tuning tournament across CatBoost, XGBoost, LightGBM, and monotonic GBM variants on the Home Credit feature spine, then calibrated top candidates and selected the champion using performance, calibration, latency, explainability, and governance tradeoffs — not AUC alone. The final selected model was evaluated once on the held-out test set, giving a tuned and calibrated credit-risk champion under offline public-data evidence."

### Gold Pass 2 safe claims

| Claim | Artifact |
|---|---|
| "5 models tuned via Optuna TPE: CatBoost, XGBoost, XGBoost_monotonic, LightGBM_base, LightGBM_monotonic — trial counts honest (4–8/model, CPU budget documented)" | `gold_pass2_tuning_trace.json` |
| "Champion: LightGBM_monotonic + Platt (val_AUC=0.7734, composite=0.7312) — selected by 9-component composite score, not AUC alone" | `gold_pass2_champion_selection_report.json` |
| "Governance champion: LightGBM_monotonic (same model) — 15 monotone constraints qualify for SR 26-2 directional interpretability" | `gold_pass2_champion_selection_report.json` |
| "Post-tuning Platt calibration reduces ECE to 0.0051 (val); Isotonic excluded from comparison (ECE=0.0 on val = overfitting artifact)" | `gold_pass2_calibration_report.json` |
| "Final untouched test: AUC=0.7769, PR-AUC=0.2628, KS=0.4141, Brier=0.0668, ECE_platt=0.0034 — single evaluation, val-test gap=−0.0035 ACCEPTABLE" | `gold_pass2_final_untouched_test_report.json` |
| "Δ vs G9A baseline CatBoost: AUC+0.0053, KS+0.0047, ECE_platt improved from 0.0054 to 0.0034" | `gold_pass2_final_untouched_test_report.json` |
| "G9A baseline CatBoost val_AUC=0.7716 was BASELINE_NOT_TUNED — correct champion after tuning is LightGBM_monotonic, not CatBoost" | `gold_pass2_champion_selection_report.json` + Pass 1 boundary |

### Gold Pass 2 clarifications and caveats

| Claim to clarify | Correct framing |
|---|---|
| "CatBoost lost the championship after tuning" | "CatBoost val_AUC=0.7708 after tuning. LightGBM_monotonic val_AUC=0.7734 — only +0.0026 on AUC. But LightGBM_mono's composite score (0.7312) is higher because it has monotone constraints (+0.5 explainability, adverse-reason ready), which CatBoost lacks. The champion decision is explicitly not AUC alone." |
| "LightGBM was terrible in G9A (AUC=0.7203)" | "That was the BASELINE_NOT_TUNED result with default parameters and early stopping on imbalanced data (a known LightGBM bug with scale_pos_weight). After fixing the early stopping and tuning properly, LightGBM_mono reaches AUC=0.7734. The baseline tournament underrepresented LightGBM." |
| "Optuna ran 100 trials per model as planned" | "Actual trial counts: 4–8 per model, not 100. CPU-only sandbox with 44s bash limit. The planning doc specified 100 trials; honest actual counts are in the tuning trace. Results are a reasonable local optimum, not a globally exhaustive search." |
| "Test AUC=0.7769 is better than val AUC=0.7734" | "Val-test gap = −0.0035 (test slightly higher than val). This is within acceptable range for a stratified random split from the same distribution — not evidence of leakage. Gap direction is random; the important check is it is small." |

### Gold Pass 2 forbidden claims

- "Champion is CatBoost" — champion is LightGBM_monotonic after Pass 2 tuning
- "AUC=0.7716 is the tuned result" — that is the G9A BASELINE untuned CatBoost score; tuned champion AUC = 0.7769 on test
- "100 Optuna trials completed" — actual trial counts are 4–8; do not overstate the search budget
- "Isotonic calibration produces ECE=0.0034" — ECE=0.0000 on val is an overfitting artifact; Platt is the final calibrator
- "The model is production-ready after Pass 2" — no claim of production readiness; limitations (reject inference, fairness audit, temporal validation) remain
- "LightGBM_monotonic is SR 26-2 certified" — methodology is aligned; no regulatory certification

---

## GOLD PASS 3 — Claim Boundary Patch (2026-06-17)

**Gold Pass 3 verdict:** COMPLETE · safe_to_pass4=true · 7 evidence JSONs + model card + governance report

### Strongest defensible current claim (verbatim)

> "I built a credit-risk ML governance stack on Home Credit Default Risk: a tuned LightGBM champion with monotone constraints, calibrated PD scores, score-band policy (GREEN/AMBER/RED with PD-semantic rationale), SHAP reason codes bootstrapped for stability across 30 resamples, a fairness proxy audit skeleton, a PSI drift baseline, and a BM25 RAG + LLM governance assistant that drafts adverse action memos for credit officer review — all under ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED governance constraints, with a model card and evidence ledger traceable to every claim."

### Gold Pass 3 safe claims

| Claim | Artifact |
|---|---|
| "Score-band policy: GREEN<0.20 (89.72% of test, DR=5.77%), AMBER 0.20–0.40 (9.80%, DR=26.96%), RED≥0.40 (0.47%, DR=53.77%)" | `gold_pass3_threshold_scoreband_report.json` |
| "Cost-optimal threshold t=0.47 under scenario economics (C_bad=10, C_reject=1, C_review=0.3) — NOT real bank economics" | `gold_pass3_cost_sensitive_decisioning.json` |
| "EXT_SOURCE_MEAN is the dominant SHAP driver: mean |contribution|=0.510, 3.6× next feature; rank-1 in 30/30 bootstraps" | `gold_pass3_shap_reason_code_report.json` + `gold_pass3_reason_code_stability.json` |
| "Top-5 SHAP features (EXT_SOURCE_MEAN, CREDIT_TO_ANNUITY, CREDIT_TO_GOODS, INST_LATE_RATIO, EXT_SOURCE_1) each appear in top-5 across all 30 bootstrap resamples — HIGH stability" | `gold_pass3_reason_code_stability.json` |
| "val-vs-test score PSI=0.0002 (STABLE); all top-10 feature PSIs <0.001 between train and test" | `gold_pass3_drift_vintage_stress.json` |
| "Fairness proxy audit on age, income, employment, region: all approval rate differentials align with observed DR differentials — no amplification beyond base rates" | `gold_pass3_fairness_proxy_audit.json` |
| "RAG/LLM demo: 6 cases; abstain fires on OOD query (BM25 top-score=0.0 < threshold 0.25); LLM never approves or rejects applicant in any case" | `gold_pass3_rag_llm_demo_report.json` |
| "SHAP computed via LightGBM built-in pred_contrib — avoids SHAP library pandas index dependency" | `gold_pass3_shap_reason_code_report.json` |

### Gold Pass 3 clarifications and caveats

| Claim to clarify | Correct framing |
|---|---|
| "The model is fair" | "Fairness audit is a SKELETON. No protected-class labels exist in Home Credit. Proxy analysis on age/income/region shows approval-rate gaps aligned with default-rate gaps — not evidence of model bias amplification, but also not evidence of fairness compliance. Full fairness certification requires protected-class enrichment and independent review." |
| "Train PSI is 8.10 — the model drifts significantly" | "Train PSI is a Platt calibration artefact: the calibrator was fit on val-set scores. The calibrated val/test score distribution is consistent (val-vs-test PSI=0.0002). Train scores are more extreme because the model memorises training data — this is expected and documented, not a deployment drift signal." |
| "The LLM makes credit decisions" | "The LLM (governance assistant) never approves or rejects. It drafts memos and reason codes for credit officer review only. All outputs are tagged ASSISTIVE_ONLY + HUMAN_REVIEW_REQUIRED + NOT_FINAL_DECISION." |
| "SHAP adverse action language is ready to send" | "SHAP-derived adverse action language requires credit officer review and sign-off before any applicant communication. It is a draft aid, not a legally compliant adverse action notice." |
| "Cost-optimal threshold is t=0.47" | "Cost-optimal under SCENARIO_ASSUMPTIONS_NOT_REAL_BANK_ECONOMICS (C_bad=10, C_reject=1). Real-world threshold must be calibrated to actual loss-given-default, cost-of-funds, and regulatory capital." |

### Gold Pass 3 forbidden claims

- "Do not claim: production lending system" — portfolio project, offline evidence only
- "Do not claim: regulatory compliance certification" — SR 26-2 aligned, not certified
- "Do not claim: legally compliant adverse action notice" — adverse action drafts require officer sign-off
- "Do not claim: fairness certified or disparate impact compliant" — skeleton audit only; no protected-class labels
- "Do not claim: real bank data validation" — Home Credit is public Kaggle data
- "Do not claim: full vintage validation" — no timestamps; stratified random split only
- "Do not claim: live deployment" — no deployment; all results are offline evaluation
- "Do not claim: LLM makes credit decisions" — ASSISTIVE_ONLY; human officer decides
- "Do not claim: applicant data safe in production" — not a production system
- "Do not claim: model approved for underwriting" — NOT_PRODUCTION_READY

---

## Gold Pass 4 — Final Freeze (Project Frozen)

### Gold Pass 4 safe claims

| Claim | Evidence artifact |
|---|---|
| "PulseGuard scores GOLD at 89.3% (134/150) on 15-dimension governance audit" | `pulseguard_final_gold_audit.json` |
| "Perfect 10/10 scores on leakage_discipline, calibration_quality, reason_code_stability, evidence_honesty" | `pulseguard_final_gold_audit.json` |
| "Project frozen at Gold Pass 4/4; all claims documented, all limitations documented" | `docs/PULSEGUARD_GOLD_CHECKPOINT.md` |
| "Interview Defense Document: 20 sections, 30+ Q&As, 15 failure modes table, implemented vs future table" | `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md` + `.pdf` |
| "Resume + Opportunity Pack: 5 resume bullets, 3 LinkedIn bullets, 60s + 2min spoken answers, what-not-to-say, role fit matrix" | `docs/PULSEGUARD_RESUME_OPPORTUNITY_PACK.md` |
| "Future Builds Backlog: 9 high-value / 5 nice-to-have / 7 do-not-build — explicitly documented" | `docs/PULSEGUARD_FUTURE_BUILDS_BACKLOG.md` |

### Gold Pass 4 caveats

| Claim to clarify | Correct framing |
|---|---|
| "GOLD status means the model is production-ready" | "GOLD means the governance documentation stack is comprehensive. The model is NOT_PRODUCTION_READY: no independent validation team review, no out-of-time validation, no regulatory review." |
| "89.3% means the model is excellent" | "89.3% is the governance audit score across 15 dimensions — model quality is one dimension (8/10). The score reflects documentation completeness, not deployment readiness." |
| "The interview defense document is a script" | "It is a preparation guide. Answers should be personalised and conversational in actual interviews." |

### Gold Pass 4 forbidden claims (carry-forward — all prior gates)

1. Production lending system or live deployment
2. SR 26-2 certified or regulatory compliance certified
3. Legally compliant adverse action notice
4. Fairness certified or disparate impact compliant
5. Real bank data or real lender economics
6. Full vintage / out-of-time validation
7. LLM makes or influences credit decisions
8. 100 Optuna trials completed (actual: 4–8 per model)
9. CatBoost is the final champion (champion is LightGBM_monotonic + Platt)
10. AUC=0.7716 is the tuned result (that is the BASELINE untuned CatBoost score)
11. "Model is fair" — proxy audit only; no protected-class labels
12. "Reject inference implemented" — documented limitation; not built
13. "Production-grade" — say "portfolio project"
14. "State-of-the-art" — say "AUC=0.7769 on Home Credit test set"

### Status — FINAL

**This file is FROZEN at Gold Pass 4/4. No further updates unless a severe bug is discovered.**

---

---

## Role-Translation Table — Narrative Expansion (no new code)

> PulseGuard's methodology maps 1:1 to fraud detection and MLOps roles. The code doesn't change; the vocabulary does. Safe framing: "same problem class, same methods, different domain vocabulary." Do NOT claim you built a fraud model or deployed an MLOps platform.

| PulseGuard Component | Credit Risk | Fraud Detection | MLOps / Model Risk |
|---|---|---|---|
| Imbalanced binary classification (8.07% DR, scale_pos_weight=11.39) | Probability of default | Fraud flag (0.1–5% positive rate — same problem class) | Minority-class detection with class-weight handling |
| Platt calibration, ECE=0.0034 | Calibrated PD score | Fraud probability score for risk-based decisioning | Model calibration audit metric |
| Score bands GREEN/AMBER/RED | Auto-approve / Manual review / Decline | Auto-approve / Step-up authentication / Hard block | Low / Medium / High risk tier routing |
| SHAP reason codes (ASSISTIVE_ONLY) | Adverse action reasons (ECOA-draft) | Fraud indicator explanation for case analyst | Feature attribution for model decision audit |
| Reason-code stability (30/30 bootstraps) | Consistent adverse action reasons | Stable fraud alert rules across resamples | Explainability robustness under sampling variance |
| PSI drift monitoring, val-vs-test PSI=0.0002 | Score distribution stability | Fraud pattern drift (fraud evolves — PSI is the standard monitor) | Model health monitoring, population stability |
| KS=0.4141 | Credit discrimination measure | Fraud model lift curve | Model discrimination at operational threshold |
| 15 monotone constraints | SR 26-2 directional interpretability | Business-rule consistency guaranteed by construction | Governance constraint on model behaviour |
| 9-component composite champion selection | Credit model promotion criteria | Fraud model promotion with governance gate | Model versioning and promotion criteria |
| Leakage audit 10/10 PASS | Pre-training data integrity | Post-outcome fraud flags excluded from features | Data pipeline validation before HPO |
| Model card + evidence ledger | SR 26-2 documentation | Fraud model docs for AML/compliance review | MLOps model registry equivalent (manual) |
| BM25 + LLM assistant (ASSISTIVE_ONLY) | Adverse action memo drafting | Fraud case narrative for analyst review | Governance assistant for model decisions |
| Fairness proxy audit | ECOA compliance skeleton | Protected-class impact analysis (proxy-only) | Fairness monitoring layer |
| FastAPI, MLflow, champion/challenger loop | [FUTURE] production credit deployment | [FUTURE] production fraud scoring API | [FUTURE] MLOps platform components |

### Safe claim — fraud detection context

> "PulseGuard applies the same algorithmic stack used in fraud detection — gradient boosting, Platt calibration, SHAP explainability, PSI/KS drift monitoring, score-band decisioning — to credit default prediction. The problem class is identical: imbalanced binary classification with a rare positive label. The methodology transfers directly; the feature domain and regulatory vocabulary differ."

### Safe claim — MLOps / model risk context

> "PulseGuard implements the governance layer of an ML platform by hand: champion selection by composite score, a 4-gate promotion framework, an evidence-traced artifact ledger, PSI/KS drift policy with WARN/ALERT thresholds, model card, and claim boundary documentation. These are the artefacts MLflow/Model Registry automates — building them manually demonstrates understanding of what the automation is actually doing."

### Safe claim — risk scoring / decision science context

> "PulseGuard covers the full scoring-to-decisioning chain: calibrated probability output, threshold economics under scenario cost assumptions, 3-band score policy with PD-semantic justification, SHAP reason codes for decision explainability, and a governance assistant for adverse action drafting."

### Forbidden in these contexts

| Claim | Why Forbidden |
|---|---|
| "I built a fraud detection model" | Data is credit default, not transaction fraud |
| "Tested on fraud datasets" | No fraud data used |
| "Real-time fraud scoring" | Offline evaluation only |
| "I built an MLOps platform" | Governance docs stack, not a deployed platform |
| "CI/CD for ML models" | Not implemented |
| "Production model registry" | Evidence ledger is manual; no MLflow/Model Registry |

---

---

## Cloud Run Deployment — Serving Gap (Added Post-Gold)

### What the live endpoint serves

| Field | Live endpoint | PulseGuard champion |
|---|---|---|
| Model | G4 XGBoost + Platt | GP2 LightGBM_monotonic + Platt |
| Dataset | synthetic_home_credit_like | Home Credit Default Risk |
| Training rows | 50,000 (synthetic DGP) | 307,511 (public Kaggle) |
| Features | 28 (20 numeric + 8 categorical) | 140 (multi-table engineered) |
| Test AUC | 0.6261 (Bayes-optimal ceiling on 6-signal DGP) | 0.7769 |
| ECE | 0.00386 | 0.0034 |
| Endpoint | `https://pulseguard-api-98058433335.us-central1.run.app` | Not deployed |

### Root cause — why the champion is not live

GP2 LightGBM pkl artifacts were serialized with **scikit-learn 1.7.2** (Python 3.10+ required).
The deployment machine runs **Python 3.9**, which can only install scikit-learn ≤ 1.6.1.
Attempting to load a 1.7.2 pkl under 1.6.1 raises `_pickle.UnpicklingError: invalid load key`.
The pkl files are permanently unloadable on Python 3.9 without retraining.

A secondary issue: `app.py` initially used `pickle.load()` but `train_champion.py` saves artifacts via
`joblib.dump()`. Loading a joblib artifact with pickle raises `_pickle.UnpicklingError: STACK_GLOBAL requires str`.
Fix: use `joblib.load()` throughout.

A tertiary issue: `src/feature_pipeline.py` used `ColumnTransformer | None` union syntax (Python 3.10+ only).
Fix: `from __future__ import annotations` (PEP 563) at top of file — makes Python 3.9 treat all
annotations as strings, resolving `TypeError: unsupported operand type(s) for |: 'ABCMeta' and 'NoneType'`.

### Interview framing — what to say

> "The live endpoint at Cloud Run demonstrates the serving pattern: preprocessing, Platt-calibrated probability, SHAP top-3 reason codes, score banding (GREEN/AMBER/RED), and ASSISTIVE_ONLY response structure. The model inside is the G4 demo model trained on synthetic data — AUC=0.6261, 28 features, 50k rows. The GP2 LightGBM champion (AUC=0.7769, 140 features, 307k rows) could not be deployed: the pkl artifacts were serialized with sklearn 1.7.2 on Python 3.10+, but my deployment environment runs Python 3.9 (max sklearn 1.6.1). The deployment gap is documented. If you want to evaluate the champion's quality, I'll walk you through the offline evidence artifacts — the serving infrastructure is correct; the model-in-container is the demo version due to a version-pinning constraint I hit during deployment."

### Safe claim — deployment context

| Claim | Status | Caveat |
|---|---|---|
| "FastAPI scoring endpoint deployed to Google Cloud Run" | **BUILT** | Endpoint URL: `https://pulseguard-api-98058433335.us-central1.run.app`; model is G4 XGBoost synthetic demo, not GP2 LightGBM champion |
| "Endpoint serves calibrated PD score, score band, SHAP top-3 reasons, ASSISTIVE_ONLY disclaimer" | **BUILT** | Serving pattern is correct; model quality is demo-tier (AUC=0.6261 on synthetic DGP) |
| "sklearn 1.7.2/Python 3.9 pkl incompatibility documented as deployment limitation" | **BUILT** | Root cause: sklearn pkl files are version-pinned; no cross-version deserialization path |

### Forbidden claims — deployment context

- "The champion model is deployed" — the GP2 LightGBM champion is NOT in the live endpoint
- "Live endpoint AUC=0.7769" — live endpoint uses G4 XGBoost; AUC=0.6261 on synthetic data
- "Production-ready serving infrastructure" — Cloud Run demo only; no autoscaling, auth, or SLA

---

*PulseGuard — 06 Claim Boundary | Gold Pass 4 FINAL FREEZE + Role Expansion | 2026-06-18*
*Deployment caveat appended post-Gold: 2026-06-20*
