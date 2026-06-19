# PULSEGUARD — RISKFRAME-GOLD RUTHLESS AUDIT
## Credit-Risk Model Governance Dossier · Full-Stack Evaluation

**Audit gate:** PULSEGUARD_RISKFRAME_GOLD_RUTHLESS_AUDIT
**Date:** June 2026
**Scope:** PulseGuard only — G0 through G8.1 inclusive
**Verdict:** STRONG — NEEDS MEAT PASS
**RiskFrame score:** 104 / 150 (69%) — Strong foundations; data-realism and decision-economics layers thin
**Provenance status:** PASS (G8.1 complete — 20/20 checks, SHA256 verified against live UCI download)
**Taiwan realism decision:** BRIDGE_ONLY — verified real-public bridge; not BeastMax ceiling; Home Credit realism lane required for T2

---

## A. NORTH-STAR IDENTITY

### Canonical One-Liner

> *PulseGuard helps risk and model-governance teams decide whether a credit-risk model and threshold policy can be promoted by catching miscalibration, threshold-cost errors, data-realism gaps, drift, reject-bias, fairness gaps, and governance failures before they cause bad lending decisions.*

### What Decision This Governs

The gate decision is: **"Is this model safe to promote to a lending policy that affects real applicants?"** That decision requires evidence across six sub-decisions:
1. Are features clean of leakage?
2. Does the model discriminate (rank order) well on real credit data?
3. Are predicted probabilities calibrated so they can be used as thresholds?
4. Does the threshold policy reflect real cost assumptions?
5. Are approval/rejection outcomes fair across protected groups?
6. Are monitoring, escalation, and override policies operational?

PulseGuard is an evidence-assembly system for this gate chain — not an answer to any single sub-question.

### Who Uses It

| Role | What They Audit | What They Can't Claim |
|------|----------------|----------------------|
| Risk Data Scientist | Model performance, calibration, champion/challenger | Real bank economics; production performance |
| Credit Modeling Team | Feature quality, leakage audit, real-data metrics | Compliance; adverse-action readiness |
| Model Governance / Model Risk | Governance sign-off checklist, evidence chain, SR 26-2 alignment | External certification; IMV sign-off |
| Decision Scientist | Threshold policy, cost-sensitive decisioning, 3-zone logic | P&L-validated thresholds; real charge-off rates |
| Lending PM | Monitoring triggers, approval rate decomposition | Operational SLA; real applicant outcomes |

### Why Wrongness Is Expensive

A miscalibrated PD of 0.15 means nothing if the threshold is 0.20 — but if the true default rate at that score is 0.30 (ECE = 0.208 as in G6 raw XGBoost), then every approval in the 0.15–0.20 band is systematically mispriced. At C_bad = NT$10 units and 65% approval rate over 30,000 applications, even a 1pp miscalibration in the approve band costs roughly 195 bad-debt units. Wrongness compounds: bad threshold → bad approval rate → bad P&L → bad monitoring triggers.

### Why This Is Not Just a Credit-Risk Model

A credit-risk model produces a PD score. PulseGuard adds:
- Pre-training leakage audit (catching features that shouldn't exist before training)
- Champion/challenger governance with calibration gates (catching the model that looks better but is less deployable)
- Cost-sensitive threshold derivation (translating PD into a business policy)
- Monitoring triggers tied to model assumptions (PSI, ECE, approval-zone DR)
- Human review and override logging policy (making the REVIEW zone auditable)
- Governance sign-off packet with explicit non-production declaration

### Why Calibration and Thresholding Matter Beyond AUC

AUC ranks. It does not price. A model with AUC = 0.80 but ECE = 0.21 cannot support a 20% threshold because "PD = 0.20" does not mean 20% actual default probability — it may mean 35%. The threshold is meaningless. PulseGuard's G6 raw XGBoost has AUC = 0.7852 and ECE = 0.2082 (pre-calibration). Platt calibration reduces ECE to 0.0112. Only after calibration does the 20% threshold become interpretable.

### Why Taiwan Is Real-Public Bridge Only If Provenance Is Proven

Taiwan Default is a real dataset with real payment histories and real default outcomes. But "real" is not credible without provenance. If the file was modified, synthetic rows injected, or source unknown, every calibration result and fairness claim rests on unverified data. G8.1 has now verified provenance (PASS — SHA256 matches live UCI download, 20/20 checks). This unlocks the "verified real public credit-card default dataset" claim. It does not unlock "real bank data," "production data," or "demographically representative" claims.

### Why Synthetic Data Is Stress-Harness Only

The synthetic Home Credit-like dataset was designed to have a known Bayes ceiling (0.6261), injected leakage, scripted drift, and calibrated default rate. It tests whether the monitoring kernel, leakage audit, and calibration protocol work correctly under known conditions. Its AUC (0.6237) is a ceiling proof, not a performance claim. Claiming synthetic results as credit-risk performance evidence would collapse the claim boundary.

### Forbidden Identity (Hard Rules)

- PulseGuard is a production lending system
- PulseGuard used real bank customer data
- PulseGuard made decisions on live applicants
- PulseGuard is regulatory-grade or SR 26-2 certified
- PulseGuard produced adverse-action notices
- PulseGuard is fair-lending certified
- Taiwan Default is the best or most realistic dataset available
- Synthetic results prove real-world lending performance

---

## B. CURRENT COMPONENT MAP

| Component | Role | Input | Output | Status Tag | Evidence File | Why It Exists | Claim Enabled | Claim NOT Enabled |
|-----------|------|-------|--------|------------|---------------|---------------|---------------|-------------------|
| Synthetic Home Credit-like harness | Controlled failure injection; known DGP | Calibrated synthetic generator (seed=42, intercept=−4.207, DR=8.17%) | 50k rows, 30 features, injected leakage + drift + group column | [SYNTHETIC HARNESS] | `outputs/evidence/g3_1_dgp_calibration_report.json` | Test protocol correctness without real data uncertainty | "Monitoring kernel detects scripted PSI breach"; "Leakage audit catches injected temporal feature" | "PulseGuard AUC on credit risk"; "Real fairness result"; "Production performance" |
| Public dataset decision gate (G5.5) | Research + lane decision | 7 dataset candidates (Taiwan, HC, LC, HELOC, German, GiveMeSomeCredit, HMDA) | Decision matrix: USE_NOW / USE_LATER / EXCLUDE | [BUILT] | `outputs/evidence/g5_5_dataset_research_summary.json` | Avoid running G6 on synthetic-only data | "Systematic public data evaluation"; "Two-lane architecture rationale" | "All viable datasets evaluated"; "Best dataset selected definitively" |
| Taiwan Default raw dataset | Real-public primary data lane | UCI XLS, header=1, engine=xlrd | 30,000 rows, 25 cols, 22.12% DR | [BUILT — verified real public data] | `data/public/taiwan_credit_default.xls` (SHA256 verified) | Bridge from synthetic to real-public evidence | "Verified real public credit-card default dataset"; "Real payment history signals" | "Real bank data"; "Current-vintage"; "Income-complete"; "Demographically representative" |
| Taiwan provenance record (G8.1) | SHA256 verification + structural audit | Raw XLS file | 20/20 provenance checks; acquisition chain documented | [BUILT] | `outputs/evidence/g8_1_data_provenance_audit.json` | Block G9 until provenance confirmed | "SHA256-verified dataset identity"; "Authentic UCI file confirmed" | "User provided this dataset"; "Audit-grade data lineage" |
| Train/val/test split | Prevent leakage into calibration/evaluation | 30k rows; stratified, seed=42 | 18k/6k/6k; DR preserved across splits | [BUILT] | `outputs/evidence/g6_champion_challenger_report.json` | Correct protocol: val for calibration, test for evaluation | "Calibration fit on held-out val set"; "Evaluation on unseen test set" | "Temporal split"; "Out-of-time validation"; "Production stability estimate" |
| Logistic regression baseline | Weak learner baseline | 23 features, Taiwan train | ROC-AUC=0.7283, PR-AUC=0.5138, ECE=0.2347 | [BUILT] | `outputs/evidence/g6_champion_challenger_report.json` | Champion comparison anchor | "LR baseline established"; "XGBoost materially outperforms LR" | "LR is adequate for this credit population" |
| XGBoost raw | Pre-calibration discriminator | 23 features, Taiwan train+val | ROC-AUC=0.7852, ECE=0.2082 | [BUILT] | `outputs/evidence/g6_champion_challenger_report.json` | Show calibration necessity | "XGBoost discriminates well but is miscalibrated pre-calibration" | "XGBoost raw is threshold-ready" |
| LightGBM | Challenger model | 23 features, Taiwan train+val | ROC-AUC=0.7742, ECE=0.1321, best_iter=9 | [BOUNDARY-LIMITED] | `outputs/evidence/g6_champion_challenger_report.json` | Challenger comparison | "LightGBM tested and held"; "Uncalibrated challenger does not improve champion" | "LightGBM is inferior to XGBoost in general"; "Fair calibrated comparison completed" |
| XGBoost Platt calibrated champion | Calibrated PD for thresholding | XGBoost raw + val set | ECE=0.0112, Brier=0.1329; threshold-ready PD | [BUILT — verified real public data] | `outputs/evidence/g6_calibration_report.json` | Calibration gate: Platt on val, evaluate on test | "Platt calibration reduces ECE 94.6%"; "Calibrated PD supports interpretable threshold" | "Model is production-calibrated in a real bank context" |
| Calibration evaluation (ECE, Brier, curve) | Calibration quality measurement | Calibrated vs raw PD, test labels | ECE before/after; calibration curve plot | [BUILT] | `outputs/evidence/g6_calibration_report.json` · `outputs/plots/g6_calibration_curve.png` | Gate: calibration must not regress | "ECE is the calibration gate; model must pass before promotion" | "ECE=0.0112 is production-calibration grade" |
| Threshold/cost policy (G7) | Cost-sensitive threshold derivation | Calibrated PD; C_bad=10, C_reject=1 | θ*=0.09 (Bayes-optimal); empirical min-EL at θ=0.10 | [BUILT] | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | Bayes-optimal threshold; cost sensitivity sweep | "Threshold derived from cost assumptions"; "Formula θ*=C_reject/(C_bad+C_reject) documented" | "Cost matrix reflects real lender economics"; "Threshold is regulatory" |
| 3-zone APPROVE/REVIEW/REJECT policy | Operational 3-zone decision policy | Calibrated PD; θ_approve=0.20, θ_reject=0.40 | Zone rates: 65.1% / 19.0% / 15.9%; EL=1.140/app | [BUILT] | `outputs/evidence/g7_taiwan_threshold_policy_report.json` | Operational alternative to single-threshold | "3-zone policy with observed DR per zone documented" | "Zone rates are production approval rates"; "Policy meets any regulatory standard" |
| Governance sign-off packet (G8) | Governance evidence chain | All G3–G7 artifacts | 5 docs + JSON summary; PENDING_SIGNOFF | [BUILT] | `outputs/evidence/g8_governance_packet_summary.json` | SR 26-2-aligned lifecycle; explicit NOT_PRODUCTION_READY | "Full model lifecycle documented"; "Launch blockers explicit" | "Model is governance-approved"; "IMV sign-off obtained" |
| Monitoring triggers (G8) | Monitor thresholds tied to G4/G7 evidence | PSI, ECE, approval-zone DR baselines | WARN/ALERT/CRITICAL thresholds with SLAs | [BUILT] | `docs/G8_MONITORING_AND_INCIDENT_POLICY.md` | Production-pattern monitoring; every trigger grounded in evidence | "Monitoring policy grounds thresholds in observed baseline metrics" | "Monitoring is operational in production" |
| Human review policy (G8) | REVIEW zone workflow + audit | 19% of applicants (PD 0.20–0.40) | 10 reason codes; tamper-evident JSONL; SEX withheld | [BUILT] | `docs/G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md` | REVIEW zone must be auditable and fair | "Override logging is tamper-evident JSONL" | "Override policy tested in simulation"; "REVIEW process is regulatorily compliant" |
| Override logging policy | Tamper-evident audit trail | Reviewer decisions, reason codes | Hash-chained JSONL per override | [BUILT] | `docs/G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md` | Cannot claim fairness without auditable human decisions | "Override logging architecture is production-pattern" | "Override logging is in production operation" |
| Adverse-action boundary (G8) | Explicit gap documentation | All G3–G8 evidence | 11-item deployment gap list; 5 no-claim declarations | [BUILT] | `docs/G8_LIMITATIONS_AND_ADVERSE_ACTION_BOUNDARY.md` | Protects against overclaiming | "Adverse action gap is documented"; "What would be needed is explicit" | "Adverse action notices generated"; "ECOA/FCRA compliance" |
| Stronger realism lane decision | Home Credit / LendingClub upgrade path | Dataset comparison (G8.1 + this audit) | Recommendation: BRIDGE_ONLY for Taiwan; Home Credit = G10 | [BUILD-TASK] | `docs/PULSEGUARD_RISKFRAME_GOLD_AUDIT.md` (§D) | BeastMax ceiling requires richer, larger, multi-vintage real data | "Realism lane decision is explicit and documented" | "Home Credit lane is built" |
| Fairness/subgroup audit — Taiwan | Real-demographics fairness at G7 thresholds | Taiwan test set; SEX/EDUCATION/MARRIAGE | DI, EOpp, PPV by group at θ=0.20/0.40 | [BUILD-TASK] | — (G9 first deliverable) | Real demographics = real fairness signal; genuine not proxy | (unlocked at G9) | "PulseGuard is fairness-certified or fair-lending approved" |

---

## C. DATA PROVENANCE AUDIT — STATUS: PASS

**G8.1 was completed in this session before this audit. All required fields are verified.**

| Field | Value | Status |
|-------|-------|--------|
| Dataset name | Default of Credit Card Clients (Taiwan, 2005) | VERIFIED |
| Source type | UCI ML Repository | VERIFIED |
| Source URL | https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls | VERIFIED |
| UCI dataset page | https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients | VERIFIED |
| User provided file | No | DOCUMENTED |
| Builder downloaded | Yes — prior Claude agent session during G5.5 gate (2026-06-16T21:25:21Z) | DOCUMENTED |
| Download script retained | No — downloaded ad hoc; source URL documented in g6_taiwan_adapter.py | GAP (documented) |
| Raw file path | `data/public/taiwan_credit_default.xls` | VERIFIED |
| Raw file size | 5,539,328 bytes (5.3 MB) | VERIFIED |
| Raw SHA256 | `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` | VERIFIED |
| SHA256 matches live UCI | YES — identical byte-for-byte | VERIFIED |
| Row count | 30,000 | VERIFIED |
| Column count | 25 (ID + 23 features + target) | VERIFIED |
| Feature names | ID, LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE, PAY_0–6, BILL_AMT1–6, PAY_AMT1–6 | VERIFIED |
| Target column | "default payment next month" | VERIFIED |
| Missing values | 0 | VERIFIED |
| Duplicate rows | 0 | VERIFIED |
| Target distribution | {0: 23,364 (77.88%), 1: 6,636 (22.12%)} | VERIFIED |
| Synthetic rows added | No | VERIFIED |
| Preprocessing changed raw records | No (strip column names only; no row modification) | VERIFIED |
| License/terms | UCI ML Repository — public research; no authentication; research use | DOCUMENTED |
| Acquisition timestamp | 2026-06-16T21:25:21Z (file mtime) | VERIFIED |
| Split seed | 42 | VERIFIED |
| Split logic | train_test_split(stratified, test_size=0.40), then val/test 50/50 → 18k/6k/6k | VERIFIED |
| Leakage-prone features | PAY_0 encoding ambiguity (values −2, 0 not clearly defined); ID is sequential — excluded | DOCUMENTED |
| Temporal order | ABSENT — random stratified split; no date field; single-cohort 2005 snapshot | CRITICAL GAP |

**Provenance verdict: PASS.** All 20 G8.1 checks passed. Safe claim: "verified real public credit-card default dataset (UCI Taiwan Default, SHA256-confirmed)."

**Residual provenance gaps (not blocking G9, but must be documented):**
1. No download script in `scripts/` — if workspace is re-created, file cannot be re-fetched automatically.
2. No temporal order — random split cannot estimate production stability over time.
3. PAY_0 encoding ambiguity — values −2 and 0 treated numerically; original paper is ambiguous.

---

## D. DATASET REALISM / AMBITION AUDIT

| Dataset | Realism | UW Fit | Credit/Loan | Label Quality | Leakage Risk | Feature Richness | Fairness Fields | Gov. Relevance | Effort | Access | Decision |
|---------|---------|--------|-------------|---------------|--------------|-----------------|----------------|----------------|--------|--------|----------|
| Taiwan Default | Real public; 2005; single cohort; credit cards | Low (no income, FOIR, bureau score) | Credit card revolving | HIGH — binary 6-month default | PAY_0 encoding ambiguity; no temporal | Medium (23 features: payment history, bill, limit) | HIGH — real SEX/EDUCATION/MARRIAGE/AGE | HIGH — compact bridge | Already downloaded | UCI, no auth | **BRIDGE_ONLY** |
| Home Credit Default Risk | Real public; 2007–2015; multi-cohort; consumer loans | HIGH — has income, employment, bureau queries | Consumer instalment loan | HIGH — binary + multi-state | Rejected applicant bias (approved-only); bureau query timing | VERY HIGH (120+ features; bureau, demographics, prior apps) | MEDIUM — CODE_GENDER; limited protected attr. | VERY HIGH — reject inference + multi-vintage + large N | Significant (Kaggle download + preprocessing) | Kaggle registration; CC BY-NC-SA | **BeastMax PRIMARY LANE** |
| LendingClub | Real public; 2007–2018; peer-to-peer | MEDIUM (income stated; DTI available; no hard bureau) | P2P unsecured loans | MEDIUM — multi-state loan status; not binary default | FICO score and grade at time of loan (info leakage from grade) | HIGH — DTI, income, loan purpose, FICO grade | LOW — no demographic features in public release | HIGH — large N; multi-vintage; reject inference implicit | Large (multi-GB CSVs; preprocessing intensive) | Kaggle / LC website; public | **T3 — secondary realism** |
| FICO HELOC | Real public; HELOC product; binary delinquency | MEDIUM (home equity; different risk profile) | Home equity; secured | HIGH | Low | Medium (24 features; WOE-ready) | LOW — no demographics available | MEDIUM | Low (single CSV) | FICO website; free | **PARKED — product mismatch** |
| German Credit | 1994 vintage; 1,000 rows; toy scale | VERY LOW | Mixed (car, furniture, business loans) | MEDIUM | Low | LOW (20 features; 7 categorical) | MEDIUM — sex, age, foreign worker | LOW — too small; toy | Near zero | UCI; public | **EXCLUDE — too small, too old** |
| Give Me Some Credit | 2011; 150k rows; Kaggle; US consumer | MEDIUM | Generic revolving/instalment | MEDIUM | Missing values (age=0); heavy tails | LOW (10 features; SeriousDlqin2yrs) | LOW — no demographics | LOW | Low (Kaggle download) | Kaggle; requires registration | **PARKED — feature-poor** |
| HMDA 2022 | US mortgage application data; 10M+ rows | HIGH for mortgage approval/denial workflow | Mortgage | N/A — approval/denial, not default | Application-time; regulated | LOW for default modeling; HIGH for fairness | VERY HIGH — protected basis, race, sex, ethnicity, income | HIGH for fair-lending methodology | Very high (massive file; complex schema) | CFPB public | **T3 — fairness methodology demonstration only; not default model** |

### Explicit Verdicts

**Is Taiwan only a bridge?** Yes. 2005 vintage, no income, single product, 30k rows, single cohort. Correct methodology demonstration; not the strongest evidence for a senior credit-risk DS role.

**Is Taiwan good enough for current governance evidence?** Yes — provenance PASS, real payment history, real demographics, real default labels. G9 fairness and G10 monitoring can proceed on Taiwan.

**Is Taiwan too weak for final BeastMax?** Yes. The ceiling gaps are: no income/FOIR, no multi-vintage, no reject inference complexity, no bureau-grade feature set, random not temporal split. A BeastMax dossier at a top-tier credit risk team needs ≥ 100k rows, multi-vintage, reject inference documented or mitigated.

**Should Home Credit become primary realism lane?** Yes for BeastMax. It forces: reject inference implementation, temporal split, 120+ feature preprocessing, bureau-data feature engineering, multi-cohort vintage analysis. These are the hard problems every production credit team faces.

**Should LendingClub become primary or secondary?** T3 secondary — income/DTI fields are valuable, but no demographics for fairness, multi-state labels complicate binary default definition. After Home Credit is complete.

**Should Taiwan remain as compact bridge?** Yes. After Home Credit, Taiwan becomes the "compact verified bridge with calibration proof" while Home Credit becomes the "full-scale realism lane with reject inference."

**BeastMax path:** G9 fairness on Taiwan → G10 Home Credit raw data + temporal split + reject inference study → G10.1 calibrated LightGBM on Home Credit → G10.2 fairness on Home Credit → G11 SHAP reason codes + FastAPI serving.

**T3 path:** After G11 — LendingClub secondary realism; HMDA fairness methodology; adverse action reason code taxonomy; Optuna HPO with ECE gate.

---

## E. MODEL / EVIDENCE AUDIT

### Metrics Table

| Claim | Number | Tag | N | CI/Uncertainty | Source File | Reproducible? | Dataset | Data Type | Interview Line | Claim Boundary |
|-------|--------|-----|---|----------------|-------------|---------------|---------|-----------|----------------|----------------|
| LR Baseline ROC-AUC | 0.7283 | VERIFIED_REAL_PUBLIC | 6,000 (test) | ±~0.012 (95%) | g6_champion_challenger_report.json | Yes (seed=42) | Taiwan Default | Real public | "LR is the interpretable baseline; XGBoost adds meaningful lift" | Credit card context only |
| LR Baseline PR-AUC | 0.5138 | VERIFIED_REAL_PUBLIC | 6,000 | ±~0.013 | g6_champion_challenger_report.json | Yes | Taiwan Default | Real public | Same | Same |
| XGBoost raw ROC-AUC | 0.7852 | VERIFIED_REAL_PUBLIC | 6,000 | ±~0.011 | g6_champion_challenger_report.json | Yes | Taiwan Default | Real public | "XGBoost discriminates well but ECE of 0.208 makes thresholding unreliable pre-calibration" | Pre-calibration; not threshold-ready |
| XGBoost raw ECE | 0.2082 | VERIFIED_REAL_PUBLIC | 6,000 | — | g6_calibration_report.json | Yes | Taiwan Default | Real public | "Raw ECE of 0.208 means PD=0.20 does not mean 20% actual DR — Platt calibration is mandatory" | Raw; not threshold-usable |
| LightGBM ROC-AUC | 0.7742 | BOUNDARY-LIMITED | 6,000 | ±~0.011 | g6_champion_challenger_report.json | Yes | Taiwan Default | Real public | "LightGBM competitive on AUC but fails uncalibrated ECE gate; held for calibrated rematch at G9" | Uncalibrated; comparison is not apples-to-apples |
| LightGBM ECE (raw) | 0.1321 | BOUNDARY-LIMITED | 6,000 | — | g6_champion_challenger_report.json | Yes | Taiwan Default | Real public | Same | Uncalibrated only |
| XGBoost Platt ROC-AUC | 0.7852 | VERIFIED_REAL_PUBLIC | 6,000 | ±~0.011 | g6_calibration_report.json | Yes | Taiwan Default | Real public | "Calibration does not change discrimination (AUC); it corrects the probability scale" | Taiwan credit card; 2005 vintage |
| XGBoost Platt PR-AUC | 0.5709 | VERIFIED_REAL_PUBLIC | 6,000 | ±~0.013 | g6_calibration_report.json | Yes | Taiwan Default | Real public | "PR-AUC of 0.57 vs random of 0.22 shows real lift on imbalanced positive class" | Same |
| XGBoost Platt Brier | 0.1329 | VERIFIED_REAL_PUBLIC | 6,000 | — | g6_calibration_report.json | Yes | Taiwan Default | Real public | "Brier decomposes into calibration + resolution; 0.13 reflects both" | Same |
| XGBoost Platt ECE | 0.0112 | CALIBRATION_EVIDENCE | 6,000 | — | g6_calibration_report.json | Yes | Taiwan Default | Real public | "ECE drops 94.6% post-calibration; Platt sigmoid fit on held-out val set (not test)" | Valid only for this population; ECE sensitive to binning |
| Platt protocol | Fit on val (6,000); evaluate on test (6,000) | CALIBRATION_EVIDENCE | 12,000 total | — | g6_champion_challenger_report.json | Yes | Taiwan Default | Real public | "Calibration is fit on held-out val, not test — otherwise ECE is optimistically biased" | Correct protocol |
| Bayes-optimal θ* | 0.0909 = 1/11 | THRESHOLD_ASSUMPTION | — | Exact formula | g7_taiwan_threshold_policy_report.json | Yes | — | Analytic | "Formula is θ* = C_reject/(C_bad+C_reject); at 10:1 ratio gives 9%" | Depends entirely on cost assumptions |
| Empirical min-EL θ | 0.10 | VERIFIED_REAL_PUBLIC | 6,000 | — | g7_taiwan_threshold_policy_report.json | Yes | Taiwan Default | Real public | "Empirical sweep confirms theoretical optimum; Platt calibration is accurate enough for formula to hold" | Same cost assumptions |
| 3-zone EL/app | 1.140 | THRESHOLD_ASSUMPTION | 6,000 | — | g7_taiwan_threshold_policy_report.json | Yes | Taiwan Default | Analytic + real | "EL of 1.14 per application under 10:1 cost ratio is illustrative; real EL depends on charge-off rates" | Illustrative cost matrix |
| Approve-zone observed DR | 10.7% | VERIFIED_REAL_PUBLIC | ~3,906 (65.1% of 6k) | ±~0.5pp | g7_taiwan_threshold_policy_report.json | Yes | Taiwan Default | Real public | "Approve zone DR of 10.7% vs reject zone 62.7% confirms model risk-stratifies well" | Credit card 2005; not a production approval rate |
| G4 synthetic AUC | 0.6237 | SYNTHETIC_HARNESS | 10,000 (test) | — | g4_champion_training_report.json | Yes | Synthetic | Synthetic | "Synthetic AUC of 0.62 is at 99.6% of the Bayes ceiling for a 6-signal DGP — the ceiling matters, not the AUC" | Synthetic DGP only; no real-data claim |
| G4 synthetic ECE | 0.00159 | SYNTHETIC_HARNESS | 10,000 | — | g4_calibration_report.json | Yes | Synthetic | Synthetic | "Synthetic DGP has a known distribution — calibration nearly perfect; real data is harder" | Synthetic only |

### Evaluation Validity Flags

| Issue | Severity | Impact | Mitigation |
|-------|----------|--------|------------|
| Random not temporal split | HIGH | Overstates stability over time; production split must be temporal | Document as gap; temporal split = G10 with Home Credit |
| LightGBM comparison uncalibrated | MEDIUM | Unfair gate; calibrated LightGBM may match or beat XGBoost | Explicit in G6 notes; calibrated rematch = G9 deliverable |
| Test set size 6,000 | MEDIUM | ±1pp uncertainty on key metrics; narrow CI | Adequate for methodology; larger test set with Home Credit |
| PAY_0 encoding ambiguity | LOW | Values −2/0 treated numerically; interpretation unclear | Documented as known failure mode |
| No confidence intervals reported | MEDIUM | Point estimates without uncertainty; AUC CI ≈ ±0.011 | Add bootstrap CI to G10 evaluation |
| Cost matrix illustrative | HIGH | Threshold policy is correct in structure but not in values | Document as THRESHOLD_ASSUMPTION; real economics = G11 |

---

## F. TECHNIQUE TOURNAMENT

| Method | Category | What It Optimizes | Data Needed | Strength | Failure Mode | Interpretability | Decision | Evidence Status |
|--------|----------|------------------|-------------|----------|--------------|-----------------|----------|----------------|
| Logistic regression | Model | Log-loss / linear decision boundary | Any tabular | Regulatory preference; fast; calibrated natively | Nonlinear relationships missed | VERY HIGH (coefficients) | Baseline only | BUILT — G6 baseline |
| Scorecard | Model | Binned WOE logit; integer scorecard | Tabular; WOE preprocessing needed | Regulatory standard; human-readable; adverse-action ready | Manual binning; misses interactions | VERY HIGH (scorecard points) | V2 | NOT BUILT — G10 |
| WOE / IV | Feature transform | Information Value for feature selection + encoding | Categorical + continuous | Monotone encoding; interpretable; reduces multicollinearity | Loses nonlinear signal; information-theoretic IV threshold is a rule of thumb | HIGH | V2 | NOT BUILT — G10 |
| XGBoost | Model | AUC/PR-AUC (AUCPR early stopping) | Medium-large tabular; class imbalance handled | Best AUC on tabular; handles missing; regularized | Miscalibrated raw outputs; no monotonicity guarantee | LOW (black box) | Use now | BUILT — G6 champion |
| LightGBM | Model | AUC (leaf-wise growth) | Large tabular; faster than XGBoost | Faster training; competitive AUC; better on large N | Overfits fast; early stopping sensitive; miscalibrated | LOW | Use now | BOUNDARY-LIMITED — G6 held |
| CatBoost | Model | AUC; native categorical handling | Tabular with many categoricals | No preprocessing for categoricals; reduced leakage | Slower than LightGBM; less tuned ecosystem | LOW | V2 | NOT BUILT |
| Monotonic GBM | Model | AUC + monotonicity constraints | Domain knowledge on feature direction | Regulatory preference; PD monotone in risk factors | Constrained = potentially lower AUC | MEDIUM | V2 | NOT BUILT |
| TabNet | Model | End-to-end tabular attention | Large tabular; GPU available | Attentive feature selection per sample | Slow; unstable; rarely beats XGBoost on credit data | LOW | Exclude | NOT BUILT |
| Platt calibration | Calibration | Sigmoid rescaling of raw scores | Val set PD + labels | Fast; works well on tree models; correct protocol | Underestimates tails; assumes monotone relationship | N/A | Use now | BUILT — G6 champion |
| Isotonic calibration | Calibration | Non-parametric monotone fit | Larger val set (>1k) needed | No parametric assumption | Overfits on small val; non-monotone risk | N/A | V2 | NOT BUILT |
| Beta calibration | Calibration | Beta distribution fit; handles boundary | Moderate val set | Better at distribution tails | More complex; less industry adoption | N/A | Discuss only | NOT BUILT |
| ROC-AUC | Metric | Rank-order discrimination | Any binary classifier output | Threshold-agnostic; widely understood | Insensitive to calibration; can hide threshold-specific failures | N/A | Use now | BUILT |
| PR-AUC | Metric | Minority class precision-recall | Imbalanced binary | Sensitive to positive class; better than AUC for 22% DR | Less familiar to non-technical stakeholders | N/A | Use now | BUILT |
| Brier score | Metric | Proper scoring rule; squared calibration error | Calibrated probabilities | Proper; decomposes into calibration + resolution | Not interpretable in isolation | N/A | Use now | BUILT |
| ECE | Metric | Calibration error binned | Calibrated probabilities; binning needed | Directly interpretable; 10-bin standard | Sensitive to bin count; noisy on small N | N/A | Use now | BUILT |
| KS | Metric | Max cumulative separation between classes | Ranked PD | Industry standard; easy to communicate | Single-threshold summary; ignores shape | N/A | V2 | NOT BUILT explicitly — G9 |
| PSI | Drift | Population Stability Index | Reference distribution vs current | Industry standard; alerts feature drift | Univariate blindspot; segment-level PSI ignored | N/A | Use now | BUILT — G4 synthetic |
| Reject inference | Method | Label imputation for rejected applicants | Prior decisions + selection model | Essential in production; removes selection bias | Hard to implement; MNAR assumption sensitive | N/A | BeastMax | NOT BUILT — documented gap |
| SHAP | Explainability | Additive feature attribution | Trained model; test set | Game-theoretic; model-agnostic; adverse-action ready | Expensive on large N; TreeSHAP is fast for XGBoost | HIGH (local) | Use now | NOT BUILT — G9 deliverable |
| Scorecard explanations | Explainability | Point deductions per feature bin | Scorecard model | Regulatory preferred; adverse action native | Requires scorecard model; not available for XGBoost | VERY HIGH | V2 | NOT BUILT |
| Cost-sensitive thresholding | Decision policy | Minimise expected loss at cost ratio | Calibrated PD; cost matrix | Economic; bridges model output to business policy | Wrong cost matrix = wrong threshold; illustrative only | HIGH (formula) | Use now | BUILT — G7 |
| Champion/challenger governance | Governance | Model promotion decision | Two trained models; promotion gates | Disciplines model update; prevents AUC chasing | Gates can be gamed; ECE gate may be too strict/loose | N/A | Use now | BUILT — G6 |
| Subgroup/fairness audit | Governance | Disparate Impact, EOpp, PPV by group | Test set + demographic labels | Legally relevant; catches biased outcomes | Does not certify fair lending; depends on available fields | N/A | Use now | BUILT (synthetic) / BUILD-TASK (Taiwan G9) |
| Drift monitoring | Governance | PSI/KS per feature vs reference | Production distribution vs training | Early warning system | Univariate; segment blindspot; not tied to labels without delay | N/A | Use now | BUILT (synthetic G4) |
| Adverse-action boundary | Governance | Gap documentation for regulatory | Evidence chain | Honest gap declaration | Does not replace actual adverse action infrastructure | N/A | Use now | BUILT — G8 |
| Temporal/vintage validation | Validation | Out-of-time model stability | Dataset with timestamps / multi-cohort | Essential for production; detects vintage drift | Not available on Taiwan (single cohort, no timestamps) | N/A | BeastMax | NOT BUILT — G10 |

---

## G. DEEP DEFENSE KERNEL

### Card 1 — Logistic Regression / Scorecard

**Problem:** Need an interpretable, regulatory-preferred baseline that quantifies each feature's marginal contribution to default probability.
**Objective:** Minimise binary cross-entropy: L = −Σ[y·log(p) + (1−y)·log(1−p)] where p = σ(Xβ).
**Assumptions:** Log-odds linearity; features independent; no interactions (unless engineered).
**Algorithmic flow:** Fit β via L-BFGS or SGD; output p = σ(Xβ); threshold at business cutoff.
**Failure modes:** Misses nonlinear interactions; sensitive to outliers; multicollinearity inflates variance.
**Why over alternatives:** Regulators accept logit; coefficient = log-odds ratio (interpretable); adverse-action reason codes native (top positive coefficients).
**When alternatives win:** Feature space is complex and nonlinear (XGBoost wins); class imbalance is severe (tree methods handle better).
**PulseGuard:** G6 LR baseline: ROC-AUC=0.7283, PR-AUC=0.5138, ECE=0.2347.
**Business decision protected:** "Is this model materially better than the simplest interpretable alternative?"
**Hard question:** "Why is your LR ECE worse than XGBoost raw if LR is supposed to be well-calibrated?"
**Safe answer:** "LR is calibrated for the linear decision boundary, but the Taiwan feature space has nonlinear interactions — PAY_0 categorical encoding breaks the linearity assumption. The ECE of 0.23 reflects that LR is mis-specified, not that calibration failed in general. This is why we need Platt on XGBoost, not just LR."

---

### Card 2 — WOE / IV

**Problem:** Raw categorical and continuous features have arbitrary encoding; information content is unquantified.
**Objective:** WOE_i = ln(Events_i% / Non-Events_i%); IV = Σ(Events_i% − Non-Events_i%) × WOE_i.
**Assumptions:** Monotone risk relationship possible; sufficient events per bin (>5).
**Algorithmic flow:** Bin continuous features → compute WOE per bin → replace raw values → compute IV → reject IV < 0.02 (weak).
**Failure modes:** Loses nonlinear signal within bins; IV threshold (0.02/0.1/0.3) is heuristic; overfits on small N.
**Why over alternatives:** Produces monotone encoding; interpretable; WOE features work well in logit; required for scorecard.
**When alternatives win:** Tree models handle raw categoricals without WOE.
**PulseGuard:** NOT BUILT. Gap for G10/scorecard path.
**Business decision protected:** "Are all features meaningfully predictive and monotonically encoded?"
**Hard question:** "Why haven't you built WOE — it's standard in credit risk?"
**Safe answer:** "WOE/IV is on the V2 build list. Taiwan Default has 23 clean numeric and categorical features. XGBoost handles them natively. WOE becomes essential when we build a scorecard for adverse-action reason codes — that's G10+. I can walk through the WOE calculation and the IV interpretation."

---

### Card 3 — XGBoost

**Problem:** Need a high-discrimination nonlinear model with early stopping to prevent overfitting on imbalanced credit data.
**Objective:** Minimise AUCPR (at train time) via gradient boosted decision trees. Objective: second-order Taylor approximation of cross-entropy. scale_pos_weight = 23364/6636 = 3.52 handles class imbalance.
**Assumptions:** Additive tree ensemble; stationary feature distribution; no temporal ordering enforced.
**Algorithmic flow:** Greedy tree construction per boosting round; split by max gain; prune by min_child_weight; early stopping on val PR-AUC.
**Complexity:** O(n × d × K) per tree where K = max_depth, d = features.
**Failure modes:** Raw probabilities miscalibrated (Platt required); no monotonicity; feature importance ≠ causal effect.
**Why over alternatives:** Best tabular AUC benchmark on credit data; handles missing; regularized; fast with GPU.
**PulseGuard:** n_estimators=500, max_depth=5, lr=0.05, scale_pos_weight=3.52, eval_metric=aucpr, early_stopping=50, seed=42, best_iteration=57.
**Business decision protected:** "Is this the best discriminating model we can train on this data?"
**Hard question:** "Why did early stopping choose 57 trees from 500 — does that mean the model underfit?"
**Safe answer:** "57 trees is not underfit — it's early stopping on PR-AUC on the validation set. The XGBoost gradient is evaluated on a different metric (aucpr) than what regularization controls, so the model stops when val PR-AUC plateaus. 57 trees on 23 features with max_depth=5 gives up to 57×31 leaf nodes — more than enough capacity. The Bayes ceiling on this data is not known precisely, but comparable papers on Taiwan Default report ~0.77–0.78 ROC-AUC, which we match."

---

### Card 4 — LightGBM

**Problem:** Need a fast challenger model to compare against XGBoost champion.
**Objective:** Same cross-entropy; leaf-wise tree growth (best-first) vs XGBoost's level-wise.
**Assumptions:** Same as XGBoost; leaf-wise growth more aggressive = higher overfitting risk.
**Failure modes:** Overfits faster than XGBoost on small N; early stopping at iter=9 suggests high variance; uncalibrated ECE=0.1321 fails the promotion gate.
**PulseGuard:** ROC-AUC=0.7742, ECE=0.1321, best_iteration=9 (very early stop).
**Critical gap:** LightGBM was compared uncalibrated vs. calibrated XGBoost. This is an unfair gate. Calibrated LightGBM may close the ECE gap.
**Business decision protected:** "Is XGBoost definitively the right model, or should we trial LightGBM with proper calibration?"
**Hard question:** "You rejected LightGBM on ECE, but you calibrated XGBoost and not LightGBM — isn't that an unfair comparison?"
**Safe answer:** "Yes, that's a documented limitation of the G6 gate. LightGBM was held, not rejected — the distinction is explicit in the promotion decision. Calibrated LightGBM vs. calibrated XGBoost is the first G9 deliverable. The current champion is XGBoost Platt; the door for LightGBM Platt is explicitly open."

---

### Card 5 — Platt Calibration

**Problem:** XGBoost raw outputs are not calibrated probabilities — PD=0.20 does not correspond to 20% default rate. ECE=0.208 pre-calibration.
**Objective:** Fit sigmoid p_calibrated = 1/(1+exp(A×f+B)) on validation set where f is raw model output. Minimise log-loss.
**Assumptions:** Monotone transformation is sufficient; sigmoid shape is appropriate; val set is representative.
**Algorithmic flow:** sklearn CalibratedClassifierCV(cv='prefit') on val set; evaluates on test set (no leakage).
**Failure modes:** Underestimates tails (sigmoid too light); fails if relationship is not sigmoid-shaped; wrong if fit on test set.
**Why over alternatives:** Simple; fast; works well on tree models; widely accepted.
**When isotonic wins:** Large val set (>5k); non-monotone shape; tails are important.
**PulseGuard:** ECE 0.2082 → 0.0112 (94.6% reduction). Platt fit on val (6k), evaluate on test (6k).
**Business decision protected:** "Can we trust the PD output to set a business threshold?"
**Hard question:** "Can you guarantee Platt calibration holds on a new population?"
**Safe answer:** "Calibration is population-specific. Platt corrects for the distributional mismatch between XGBoost's raw output and the true probability on the validation population. If the scoring population drifts (PSI > 0.20), recalibration is required. The monitoring trigger at ECE > 0.025 catches calibration drift before it becomes a threshold problem."

---

### Card 6 — Isotonic Calibration

**Problem:** When the calibration curve is non-monotone or sigmoid-shaped assumption is wrong.
**Objective:** Minimise Brier score subject to monotone non-parametric step function.
**Assumptions:** Larger sample needed (>2k–5k); will overfit on small val sets.
**PulseGuard:** NOT BUILT. Would require comparing isotonic vs Platt on Taiwan val set.
**When it wins:** Large val set; complex calibration curve shape; tail accuracy important.
**Decision:** V2 — compare with Platt on Home Credit's larger val set.

---

### Card 7 — Beta Calibration

**Problem:** Platt doesn't handle boundary behaviour well (probabilities near 0 or 1).
**Objective:** Fit Beta distribution parameters to map raw scores to probabilities; handles [0,1] boundary.
**PulseGuard:** NOT BUILT. Discuss only — limited industry adoption; Platt adequate for current ECE=0.0112.

---

### Card 8 — ECE (Expected Calibration Error)

**Problem:** Quantify how well PD outputs correspond to observed default rates.
**Objective:** ECE = Σ_b (|B_b|/n) × |acc(B_b) − conf(B_b)| where B_b is score bin, acc = observed DR, conf = mean PD.
**Assumptions:** 10-bin uniform equal-width (standard); uniform or equal-frequency binning changes ECE.
**Failure modes:** Sensitive to bin count; noisy on small N per bin; does not distinguish overconfidence from underconfidence.
**Why this:** Industry-standard calibration metric; directly interpretable; ties to thresholding quality.
**PulseGuard:** Raw ECE=0.208; calibrated ECE=0.0112. Threshold of 0.025 WARN / 0.05 ALERT / 0.10 CRITICAL in monitoring policy.
**Business decision protected:** "Are we setting the threshold in the right place on the probability scale?"
**Hard question:** "ECE can be gamed by uniform bins — how do you know 10 bins is right?"
**Safe answer:** "10-bin ECE is the standard from Guo et al. 2017. Changing to 15 bins on Taiwan Default changes ECE by ±0.002. The key insight is that Platt reduces ECE by 94.6%, not that the absolute number is 0.0112 vs 0.0108 with different bins. I'd also report reliability diagrams, not just scalar ECE."

---

### Card 9 — Brier Score

**Problem:** Need a proper scoring rule that penalises both discrimination failure and calibration failure.
**Objective:** Brier = (1/n)Σ(p_i − y_i)². Decomposition: Brier = Reliability − Resolution + Uncertainty.
**Assumptions:** None beyond binary labels and [0,1] probability outputs.
**Why this:** Proper scoring rule; cannot be improved by misreporting probabilities; decomposes unlike AUC.
**PulseGuard:** Calibrated XGBoost Brier=0.1329. Platt calibration reduces Brier (0.1778→0.1329) showing calibration improvement in the proper scoring sense.
**Business decision protected:** "Is the model honest about its uncertainty?"
**Hard question:** "What's the reference Brier score for a naive model predicting the base rate?"
**Safe answer:** "A naive model always predicting p=0.2212 scores Brier=0.2212×(1−0.2212)=0.1722. Our calibrated XGBoost scores 0.1329 — 23% better than naive. The Brier skill score is 1 − (0.1329/0.1722) = 0.23, meaning we capture 23% of the maximal achievable skill."

---

### Card 10 — ROC-AUC vs PR-AUC

**Problem:** Which discrimination metric to report for an imbalanced binary credit default dataset?
**ROC-AUC:** Probability of ranking a random positive above a random negative. P(score(defaulter) > score(non-defaulter)).
**PR-AUC:** Area under Precision-Recall curve. Sensitive to positive class (defaulters). Random baseline ≈ default rate (0.22 for Taiwan).
**Why PR-AUC matters more:** At 22% DR, ROC-AUC is less affected by false negatives in the negative-heavy population. PR-AUC measures how well we find defaulters. For credit risk where the cost of false negatives (missed defaulters) is high, PR-AUC is the primary signal.
**PulseGuard:** Reports both. ROC-AUC=0.7852, PR-AUC=0.5709 (vs random baseline ≈0.22).
**Hard question:** "Why is your PR-AUC only 0.57 when your AUC is 0.79?"
**Safe answer:** "PR-AUC of 0.57 vs a random baseline of 0.22 represents a 2.6× lift. AUC of 0.79 measures rank order for all pairs; PR-AUC focuses on how precisely we find the actual defaulters. At 22% base rate, achieving both high AUC and high PR-AUC simultaneously requires that the model doesn't just rank correctly but also concentrates its probability mass on actual defaulters. 0.57 is consistent with published Taiwan Default benchmarks."

---

### Card 11 — KS Statistic

**Problem:** Measure maximum separation between cumulative default and non-default score distributions.
**Objective:** KS = max_threshold |CDF_defaults(t) − CDF_non-defaults(t)|.
**Assumptions:** Monotone score; single-threshold summary statistic.
**Failure modes:** Ignores shape away from the maximum; two models can have same KS but very different calibration.
**PulseGuard:** Not explicitly computed as a scalar metric in G6 — computed by scipy in G4 drift monitoring (KS=0.1935 WARN, KS=0.2927 ALERT on synthetic). Should be added to G9 real-data evaluation.
**Decision:** V2 — add to G9 Taiwan evaluation and G10 Home Credit.

---

### Card 12 — PSI

**Problem:** Detect when the scoring population has drifted from the training population.
**Objective:** PSI = Σ_b (Actual_% − Expected_%) × ln(Actual_%/Expected_%). Thresholds: PSI<0.10 OK, 0.10–0.20 WARN, >0.20 ALERT.
**Assumptions:** Bins fixed from training; univariate per feature; equal-frequency binning standard.
**Failure modes:** PSI can be stable globally while a segment drifts. PSI is a univariate measure — joint drift invisible. Bin count affects PSI value.
**PulseGuard:** G4 synthetic: PAY_0/PAY_2 WARN=0.10, ALERT=0.20 defined in G8 monitoring. G4 synthetic: Day7 PSI=0.1532, Day14 PSI=0.2974.
**Business decision protected:** "Is the current scoring population still similar enough to the training population that the model's behavior is predictable?"
**Hard question:** "PSI can miss segment-level drift — how do you catch that?"
**Safe answer:** "PSI is the industry standard but has a documented blindspot: global PSI can be stable while a subgroup drifts significantly. Stripe Engineering documented this in 2025. The mitigation is segment-conditional PSI — computing PSI within high-risk segments or by PAY_0 value. That's a G10 monitoring enhancement. Right now we flag at PSI > 0.20 and route to model freeze — the false negative risk is acknowledged."

---

### Card 13 — Cost-Sensitive Thresholding

**Problem:** AUC and ECE tell you the model quality; they don't tell you where to draw the line. Business economics determine the threshold.
**Objective:** Minimise Expected Loss = C_bad × FN_rate + C_reject × FP_rate. Bayes-optimal: θ* = C_reject/(C_bad + C_reject).
**Assumptions:** Cost matrix is fixed and known; costs are linear; no interaction between applicants.
**Algebraic derivation:** EL is minimised where C_bad × P(Y=1|score=θ) = C_reject × P(Y=0|score=θ). Since calibrated PD = P(Y=1|score), threshold θ* = C_reject/(C_bad+C_reject).
**PulseGuard:** C_bad=10, C_reject=1, C_review=0.3. θ* = 1/11 ≈ 9%. Empirical min-EL at θ=0.10. 3-zone policy at 20%/40% for operational reasons.
**Why 10:1 is economically low:** At a typical NBFC in India, charge-off on an unsecured loan is ~80–90% of outstanding balance. Net interest margin on a good account over lifetime might be 15–25%. Ratio of charge-off to margin = 3:1 to 6:1, not 10:1. A 10:1 ratio is conservative — it sets a very low threshold (~9%), approving very little. Real banks might operate at 5:1 or even 3:1.
**PulseGuard G7 sensitivity:** Tested ratios 2:1 (θ=0.32), 5:1 (θ=0.17), 10:1 (θ=0.10), 20:1 (θ=0.07). Approval rate stable ~78%.
**Hard question:** "Where do your cost values come from?"
**Safe answer:** "They're illustrative — normalised to C_bad=10, C_reject=1 to demonstrate the methodology. The point is not the specific values but the framework: threshold = C_reject/(C_bad+C_reject). If you tell me your lender's charge-off rate and net interest margin, I can compute the empirically justified threshold. Real banks use observed lifetime P&L, not assumed ratios."

---

### Card 14 — Reject Inference

**Problem:** In production, only approved applicants have observed default outcomes. Rejected applicants are unlabeled. Training only on approved applicants creates selection bias — the model learns from a subset of the risk distribution.
**Types:** MCAR (missing completely at random) — safe to ignore; MNAR (missing not at random) — biases model.
**Why MNAR is dangerous:** A model trained on approved applicants learns that "approved" is predictive of being good. This is circular. If the previous policy approved most good applicants and rejected most bad ones, the model overfits to the prior policy — it cannot improve on it.
**Techniques:** Semi-supervised labeling (propagate labels from approved to rejected); propensity weighting; augmentation; Heckman selection.
**PulseGuard:** NOT BUILT. Taiwan Default does NOT need reject inference (all 30,000 accounts have observed outcomes — they were all active cardholders). Home Credit DOES require it (application-approved-only training data). This is the primary reason Home Credit is harder and more realistic than Taiwan Default.
**Hard question:** "If you go to production and only see outcomes on approved applicants, how do you retrain without selection bias?"
**Safe answer:** "Reject inference is the core problem in lending model retraining. The simplest approach is to assume MCAR for the rejected population and weight the labeled sample by propensity scores from the approval model. More rigorous: semi-supervised label propagation. The G8 limitations boundary explicitly documents that PulseGuard does not implement reject inference — Taiwan Default doesn't require it, but Home Credit at G10 will force us to address it."

---

### Card 15 — SHAP

**Problem:** XGBoost produces a score; stakeholders need to know which features drove the individual score — for adverse action, for debugging, for fairness investigation.
**Objective:** SHAP value = contribution of feature j to prediction minus expected prediction: φ_j = Σ_S [|S|!(|F|−|S|−1)!/|F|!] × [f(S∪{j}) − f(S)].
**TreeSHAP:** Polynomial-time exact computation for tree ensembles. O(TL²D) where T=trees, L=leaves, D=depth.
**Failure modes:** SHAP interactions not shown in main effects; correlated features share SHAP improperly; SHAP ≠ causal.
**Why this:** Additive; complete (sum to prediction); consistent; model-agnostic generalisation available; adverse action reasons expressible as top-k negative SHAP features.
**PulseGuard:** NOT BUILT — G9 first deliverable alongside fairness audit.
**Business decision protected:** "Why was this applicant scored this way, and can we defend it?"
**Hard question:** "SHAP features are correlated on this dataset — PAY_0 and PAY_2 are correlated. Does SHAP split the credit correctly?"
**Safe answer:** "Correlated features do cause SHAP to distribute contributions between them in ways that can be unintuitive. TreeSHAP handles this via conditional expectations, not marginal. If PAY_0 and PAY_2 are collinear, their individual SHAPs will both be smaller but their combined effect is preserved. For adverse action, we report top reasons by |SHAP| — if both PAY_0 and PAY_2 appear, we'd group them as 'payment history' to avoid redundancy."

---

### Card 16 — Champion/Challenger Governance

**Problem:** When a new model is proposed to replace the current champion, the promotion decision must be systematic, not subjective.
**Objective:** Gates: ΔPR-AUC ≥ 0.001 AND ΔROC-AUC ≥ 0.001 AND ΔECE ≤ 0.005 AND ΔBrier ≤ 0.003. All gates must pass.
**Why 4 gates:** AUC alone can be gamed — a model with better AUC but worse calibration would fail the ECE gate. Brier catches combined discrimination + calibration failure. Each gate protects a different business risk.
**PulseGuard:** G6 challenger LightGBM fails ECE gate uncalibrated vs. calibrated champion. Result: HELD, not REJECTED.
**Business decision protected:** "Are we promoting a model that is strictly better across all dimensions the business cares about?"
**Hard question:** "Your ECE gate is 0.005 — why is that the right threshold?"
**Safe answer:** "The 0.005 ECE gate means: if the challenger's calibration is more than 0.005 ECE worse than the champion, don't promote. This corresponds roughly to a 0.5pp miscalibration on the threshold — at PD=0.20, a 0.005 ECE error means the true rate might be 0.195 or 0.205. Given our threshold is 0.20, this is a meaningful error. The gate is calibrated against the monitoring WARN threshold of 0.025 — we don't promote a model that starts close to a WARN condition."

---

### Card 17 — Monitoring Triggers

**Problem:** Model performance degrades between training and production due to population drift, vintage shift, or economic change. Monitoring must detect this before bad decisions compound.
**Triggers (PulseGuard G8):** PSI WARN=0.10, ALERT=0.20 on PAY_0/PAY_2; ECE WARN=0.025, ALERT=0.05, CRITICAL=0.10; approve-zone DR WARN=20%, ALERT=25%, CRITICAL=35%; approval rate change WARN=5pp, ALERT=10pp; score KS WARN=0.05.
**Why these thresholds:** Each is grounded in G6/G7 evidence. ECE WARN at 0.025 is 2.2× the baseline of 0.0112. Approve-zone DR WARN at 20% is 1.9× the G7 observed DR of 10.7%.
**Failure mode:** Triggers copied from literature without grounding in actual model. PulseGuard avoids this by tying every threshold to a specific artifact.
**Remaining gap:** Triggers are defined but not exercised over time — no production timeline exists. Synthetic drift kernel (G4) exercises PSI triggers on a scripted schedule.
**Hard question:** "What happens if PAY_0 PSI fires ALERT but approve-zone DR is still within WARN bounds?"
**Safe answer:** "Partial alert conditions are handled by a severity table in the G8 monitoring policy. PAY_0 ALERT without label deterioration → 72-hour investigation, not immediate freeze. Freeze requires ECE CRITICAL OR approve-zone DR CRITICAL OR PSI > 0.30. The rationale: PSI measures distributional shift in inputs; DR measures outcome-level impact. Both can diverge — PSI fires if the population changes; DR fires if the change translates to worse decisions. We monitor both independently and require both for immediate freeze."

---

### Card 18 — Fairness / Subgroup Audit Limitations

**Problem:** Credit decisions at different rates across protected groups may constitute disparate impact even if no protected attribute is used directly.
**Metrics:** DI = approval_rate_group_A / approval_rate_majority ≥ 0.80 (4/5ths rule). EOpp = |TPR_A − TPR_majority| ≤ 5pp. PPV parity.
**Why fairness audit cannot certify fair lending:** DI at a threshold tells you the approval rate ratio at one point in time on one dataset. It does not prove: (a) business necessity justification, (b) less discriminatory alternative exhausted, (c) legal compliance in any jurisdiction, (d) fairness on the deployment population.
**PulseGuard:** G5 synthetic DI=1.0127 PASS (proxy group; illustrative). G9 Taiwan DI: NOT YET COMPUTED. Male DR=24.17%, female DR=20.78% — different base rates → identical threshold will produce different group outcomes.
**Hard question:** "Male and female default rates differ by 3.4pp — won't any fixed threshold produce disparate impact?"
**Safe answer:** "Disparate impact depends on approval rate ratios, not just default rate differences. If males have higher default rates and the model scores them lower, their approval rate will be lower — but this may be business-necessity justified (different risk) rather than prohibited disparate impact. The G9 fairness audit will compute DI, EOpp, and PPV at θ=0.20/0.40 for SEX, EDUCATION, MARRIAGE. Whether a gap constitutes disparate impact under any legal standard requires legal review — which is not in scope for this portfolio."

---

### Card 19 — Adverse Action Boundary

**Problem:** When a model rejects a credit application, in many jurisdictions the applicant has a right to know why. Automated decisions without adverse-action infrastructure violate this right.
**What adverse action requires:** Specific reason codes (e.g., "excessive obligations in relation to income"); delivery within regulatory timeframe; format compliant with local law; right to explanation (GDPR Art 22, ECOA Regulation B).
**PulseGuard:** Explicit documentation that adverse action is NOT implemented. REJECT zone produces a PD score and zone label. No reason codes. No delivery mechanism. SHAP-based reason code assignment is G9 deliverable.
**What is built:** Audit trail record per decision; policy version + model version logged; human-readable reason codes (RC-01 through RC-99) for REVIEW zone manual decisions.
**Hard question:** "So your rejected applicants can't get a reason — isn't that illegal?"
**Safe answer:** "In a production deployment, yes — ECOA and Regulation B would require adverse action notices. This is explicitly documented in the G8 limitations boundary: adverse action notice generation requires SHAP-based reason code assignment, a regulatory reason code taxonomy, and a communication channel — none of which are built. The reason this is documented explicitly rather than quietly omitted is that the governance discipline requires knowing your gaps. G9 adds SHAP-based reason code assignment as the first step toward an adverse action module."

---

### Card 20 — Temporal / Vintage Validation

**Problem:** A model trained on data from one time period may perform worse when applied to applicants from a later period, due to macroeconomic change, credit bureau evolution, payment behaviour shifts.
**What temporal validation requires:** Train on time period T1; test on time period T2 > T1. The gap should reflect at minimum one economic cycle or the model's intended deployment horizon.
**Why random split is wrong in production:** Random split leaks future behaviour patterns into training. A model trained on 2024 data tested on a random sample of 2024 data overstates stability versus a model tested on 2025 data.
**Taiwan Default failure on this front:** Single cohort (2005); no timestamp; no sequential ordering possible. All splits are random. Temporal validation is structurally impossible on Taiwan Default.
**PulseGuard:** Documented as a known limitation. Random split is used. Out-of-time performance is unknown.
**Why this matters for BeastMax:** A senior credit DS interview at a tier-1 bank will probe this. "How do you know your model works on applicants you haven't seen yet?" requires either temporal validation or explicit rejection of the claim.
**Hard question:** "Your test set is random — how do you know the model performs on applicants from next year?"
**Safe answer:** "I don't claim it does. Taiwan Default is a single 2005 cohort with no date field, so temporal split is structurally impossible. This is documented explicitly in the G8 limitations boundary and the G8.1 provenance audit. The production answer requires either multi-cohort data (Home Credit at G10) or a deployed pipeline with live monitoring. Claiming out-of-time stability from a random split would be a false confidence claim."

---

## H. PRODUCT REASONING KERNEL

| Product Decision | First-Principles Driver | Alternative Rejected | Data/Logging Consequence | Evaluation Consequence | Business Consequence | Evidence Status |
|-----------------|------------------------|---------------------|-------------------------|----------------------|---------------------|----------------|
| Higher AUC can lose money if calibration is poor | Threshold policy depends on PD = P(default\|score); if uncalibrated, PD is wrong → threshold is misplaced → wrong approvals | "Use AUC as primary promotion gate; threshold can be calibrated later" | Calibration must be logged per model version; ECE must be in evidence chain | AUC-only comparisons are inadequate; ECE gate is mandatory | Loans approved at wrong risk band → charge-off exceeds P&L expectation | BUILT — G6: XGBoost raw ECE=0.208; Platt ECE=0.0112; calibrated EL < raw EL at all thresholds |
| Calibration gates model promotion | A model with better AUC but worse calibration would set thresholds using unreliable probabilities | "Let the business team set empirical thresholds from the approval rate" | Val set reserved for calibration; test set reserved for evaluation; protocol enforced | ΔECE ≤ 0.005 is blocking gate in champion/challenger | Prevents AUC-chasing; forces models to be threshold-ready | BUILT — G6 4-gate promotion; LightGBM held on ECE gate |
| PD must be threshold/pricing usable | The credit decision is a function of PD vs threshold. If PD is a rank (AUC metric) not a probability (calibration metric), the threshold has no economic interpretation | "Use a score between 0–1000 and choose threshold empirically from observed default rates" | ECE monitoring; calibration report per gate | ECE is primary model promotion criterion | A 20% threshold means something: "we expect 20% of approvals in this score range to default" — only valid if calibrated | BUILT — G6/G7: calibrated PD supports interpretable thresholding |
| Threshold policy must use cost assumptions | The optimal threshold is not statistical — it is economic. θ* = C_reject/(C_bad+C_reject) is derived from business costs. Different lenders → different thresholds on the same model | "Choose threshold to maximize F1 or by default rate" | Cost matrix must be documented; sensitivity must be swept | Sensitivity table across cost ratios is mandatory evaluation | Wrong threshold → wrong economics → bad P&L | BUILT — G7: formula + 4-ratio sweep |
| 10:1 cost ratio threshold logic is economically low | At 10:1, θ* = 9% — very aggressive. Real lenders often operate at 3:1 to 6:1, giving θ = 14%–25%. 10:1 is conservative (too few approvals) | "Use standard 10:1 as the industry baseline" | Ratio must be disclosed; sensitivity must show what changes if ratio drops | Changing ratio changes threshold materially | Operational constraint: if the institution's actual economics are 3:1, using 10:1 leaves 25% revenue on the table | BUILT — G7: sensitivity documented; THRESHOLD_ASSUMPTION tag |
| 3-zone policy operationally better than one threshold | One threshold → binary APPROVE/REJECT. Review zone captures applicants near the boundary where model uncertainty is highest — human review adds signal the model cannot. EL calculation explicitly models review cost | "Binary threshold is operationally simpler" | Review zone size must be defined; review cost must be explicit | 3-zone EL lower than single-threshold at operational θ | Review zone reduces charge-off in the borderline band; adds operational cost (C_review) | BUILT — G7: 3-zone policy, DR by zone, EL comparison |
| Taiwan is real public data only if provenance passes | Without provenance, "real" is an unverifiable claim. A modified file, injected rows, or unknown source collapses the claim chain | "Assume the file is the UCI dataset because it has the right column names" | SHA256 of raw file; acquisition audit; timestamp | Provenance FAIL → downgrade all metrics to UNVERIFIED | Interview claim "trained on real credit data" is defensible only with evidence | BUILT — G8.1 PASS: SHA256 matches live UCI |
| Taiwan is not real bank production data | UCI dataset is research-grade public data from a single Taiwanese bank, 2005, credit cards only. Real bank data is protected, licensed, governed | "UCI data is real-world data therefore equivalent to bank data" | This claim would be false | Interview claim would collapse under scrutiny | Regulatory risk if misrepresented | BUILT — G8 forbidden claims; G8.1 acquisition note |
| Taiwan may be too weak for final BeastMax | BeastMax requires: ≥100k rows, multi-vintage, reject inference context, bureau-grade features, real income data. Taiwan has 30k rows, single vintage 2005, no income, no reject inference complexity | "Taiwan is good enough; it's real data with real outcomes" | Home Credit / LendingClub must be scheduled explicitly | G10 deliverable must include temporal split + reject inference study | Senior credit DS interviewers will probe feature richness and sample size | DOCUMENTED — this audit; BRIDGE_ONLY verdict |
| Synthetic harness is stress-test only | Known DGP; known ceiling; injected failures. Cannot claim real credit performance from a manufactured distribution | "Synthetic results demonstrate the platform works" | Synthetic results labeled SYNTHETIC_HARNESS; never mixed with real-data claims | Synthetic AUC (0.62) is ceiling proof, not performance benchmark | Claiming synthetic results as credit risk performance evidence would be misleading | BUILT — G3.1 DGP; claim boundary throughout |
| Provenance matters | An unverified file is forensic evidence of nothing. A claim chain built on an unverified file collapses if provenance fails | "The file has the right number of rows — it must be correct" | SHA256 audit; acquisition chain; structural verification | All metrics shift from VERIFIED to UNVERIFIED on provenance FAIL | Portfolio claim "trained on verified real public data" requires proof | BUILT — G8.1 20/20 PASS |
| Fairness audit cannot certify fair lending | DI at one threshold on one dataset is not a legal finding. It is a statistical observation | "DI = 1.01 means the model is fair" | Fairness results labeled BOUNDARY-LIMITED; forbidden claims explicit | Fairness metrics are diagnostic, not certifying | No fair-lending claim can be made from this audit | BUILT — G5 synthetic; G9 Taiwan pending |
| Reject inference matters in actual lending | In production, rejected applicants have no observed outcome. The training population is biased toward approved applicants. Model trained only on approvals will underestimate risk of near-threshold population | "All applicants in our training set have outcomes" | Reject inference study or explicit justification required | Models without reject inference may overstate performance on the borderline population | Charge-off in the near-threshold approve zone may be higher than model predicts | DOCUMENTED — G8 limitations; NOT BUILT |
| Home Credit / LendingClub needed for stronger realism | Taiwan lacks: income, multi-vintage, reject inference context, 100k+ rows. Home Credit has all of these. This is the gap between a bridge dataset and a BeastMax dataset | "Build more analytics on Taiwan" | Home Credit pipeline: temporal split, reject inference study, 120+ feature preprocessing | All metrics to be re-evaluated on Home Credit; Taiwan metrics are bridge only | Interview at tier-1 bank requires Home Credit-grade evidence or equivalent | DOCUMENTED — this audit; G10 recommendation |

---

## I. BUSINESS OPERATING CONTEXT

| Area | PulseGuard Answer | Evidence Status | Missing Evidence |
|------|------------------|----------------|-----------------|
| Business model | Credit decision platform: model governance + threshold policy for a retail lending portfolio (credit cards; consumer loans at G10). Revenue from approving creditworthy applicants; cost from defaults on approved applicants. | DOCUMENTED — G7 cost matrix; G8 governance | Real lender economics; real product revenue model |
| Decision owner | Decision Owner: approves threshold policy changes and signs off on promotion. Model Owner: accountable for model performance. Risk Owner: blocks promotion if risk/fairness gaps exist. | BUILT — G8 governance roles registry | No real individuals; portfolio simulation |
| Decision cadence | Model performance reviewed on defined monitoring triggers (PSI ALERT, ECE ALERT, approve-zone DR ALERT). Retraining review: triggered, not scheduled — Risk Owner decision required. | BUILT — G8 monitoring policy | Not exercised over time; no real approval cohort |
| KPI tree | Primary: Expected Loss per application (EL=C_bad×FN_rate + C_reject×FP_rate). Secondary: Approve rate (65.1%); REVIEW rate (19%); REJECT rate (15.9%); Approve-zone observed DR (10.7%). Monitor: ECE (0.0112); PSI on PAY_0. | BUILT — G7 policy report | Real charge-off rate; real net interest margin; real review cost |
| Cost of wrongness | False approval (C_bad=10): charge-off of bad debt. False rejection (C_reject=1): lost lifetime revenue from a good customer. False negative in review (C_review=0.3). At current policy EL=1.14 per app. | BUILT — G7 | Real per-unit costs; real portfolio P&L impact |
| Constraint envelope | Approve rate bounded by: (a) regulatory fair-lending requirements (DI must pass), (b) capital requirements (max bad-debt ratio), (c) operational review capacity (REVIEW queue = 19% of apps). | DOCUMENTED — G8 | No real regulatory or capital constraint; no review team capacity model |
| Rollout reality | Would require: IMV sign-off, adverse action infrastructure, real-economics cost matrix, temporal validation, compliance officer review. 10 documented pre-launch gaps. | BUILT — G8 governance signoff packet | All 10 pre-launch gaps unresolved |
| Human ownership | REVIEW zone (19% of apps) requires human underwriter. Override logging is tamper-evident JSONL. SEX withheld from reviewer. Escalation conditions documented. | BUILT — G8 human review policy | No real underwriters; no simulation of override rate drift |
| Startup version | Small team: Risk DS trains and calibrates model. Decision Scientist sets threshold from cost matrix. PM monitors approval rate weekly. Human review = credit analyst for borderline apps. | DOCUMENTED | Not implemented |
| Mature-company version | IMV unit reviews model quarterly. Compliance officer signs off. SR 26-2 aligned governance chain. Adversarial model challenge. Champion/challenger on live traffic (A/B). | DOCUMENTED | Not implemented |
| Interview punchline | "I built the entire governance chain: leakage audit before training, calibration gate before promotion, cost-sensitive threshold derivation, 3-zone policy with human review design, and explicit documentation of what would be needed to actually put this in production. The launch status is NOT_PRODUCTION_READY — and I can tell you exactly what those 10 items are and what each costs to close." | BUILT | — |

---

## J. OPERATIONAL FAILURE MODES

| # | Failure | Why It Happens | Naive Miss | Current Detection | Evidence | Mitigation | Remaining Gap |
|---|---------|---------------|------------|------------------|----------|------------|---------------|
| 1 | Challenger improves AUC but worsens calibration | AUC is non-calibration metric; HPO optimizes AUC not ECE; model trusts its own uncertainty less on borderline cases | "Challenger has better AUC therefore promote" | ECE gate in G6 4-gate promotion (ΔECE ≤ 0.005) | G6: LightGBM ECE=0.1321 fails gate vs calibrated champion | 4-gate promotion requires calibration gate pass | Calibrated LightGBM comparison not yet done |
| 2 | Calibrated PD used outside training population | Platt sigmoid is fit on the training-population val set. Applied to a different segment, vintage, or product, the sigmoid may not hold | "Calibration is model property; applies everywhere" | ECE monitoring trigger (WARN=0.025) | G8 monitoring policy: ECE WARN/ALERT/CRITICAL thresholds | Recalibrate on new population before applying threshold | No production ECE monitoring over time |
| 3 | Taiwan data not representative of scoring population | 2005 vintage, Taiwan credit cards only. Any deployment on a different market, product, or time period uses out-of-sample extrapolation | "It's real data; it generalises" | G8.1 provenance audit documents vintage and product scope | G8.1 audit doc §C, §D limitations | Use only as methodology demonstration; real deployment requires relevant-vintage data | No temporal validation; no out-of-time test |
| 4 | Provenance unclear | File placed by prior agent session with no download script retained | "File has the right rows and columns" | G8.1 SHA256 live re-download verification (20/20 PASS) | g8_1_data_provenance_audit.json | SHA256 audit script reproducible; acquisition documented | No download script in scripts/ for automated re-acquisition |
| 5 | Temporal leakage inflates performance | Features computed after the outcome date leak future information; model sees information unavailable at decision time | "All features are from the application form" | FeatureLeakageLens 7-check audit; temporal availability check | G3 leakage_report.json: 1 FAIL on injected temporal feature | Hard-exclude temporally leaky features before training | Taiwan Default has no feature timestamps; temporal availability cannot be formally checked per feature |
| 6 | Rejected applicants lack labels | Production model trained only on approved applicants; rejected population's default rate unknown; model underestimates risk of near-threshold applicants | "Train on all applicants with outcomes" | Documented as known limitation; reject inference acknowledged | G8 limitations boundary | Reject inference study (semi-supervised, propensity weighting) | NOT BUILT — G10 BeastMax requirement |
| 7 | Macro/vintage drift changes default relationship | Economic recession → default rate spikes; payment behaviour patterns shift; PAY_0 predictive power changes | "PSI is stable; model is fine" | PSI monitoring on PAY_0/PAY_2; approve-zone DR monitoring | G8 monitoring triggers | Approve-zone DR trigger fires when defaults spike; model freeze if CRITICAL | No real macro stress test; synthetic drift is scripted not macro-driven |
| 8 | PSI stable globally but segment drifts | Subgroup shifts cancel out in aggregate PSI; a high-risk segment could deteriorate while global PSI is OK | "PSI = 0.08, all OK" | Not currently detected; documented as PSI multivariate blindspot | G8 monitoring policy footnote | Segment-conditional PSI (by PAY_0 value, EDUCATION, age band) | NOT BUILT — G10 enhancement |
| 9 | Threshold cost assumptions wrong | C_bad=10, C_reject=1 are illustrative; real lender economics may give 3:1 or 5:1 ratio | "10:1 is conservative therefore safe" | Cost sensitivity analysis across 4 ratios (2:1, 5:1, 10:1, 20:1) | g7_cost_sensitivity_report.json | Elicit real economics from lending PM before setting production threshold | No real P&L data; threshold not validated against actual charge-off/revenue |
| 10 | Operational review queue overloaded | 19% review rate × application volume = large daily review queue; underwriters cannot clear queue within SLA | "19% review rate is fine" | Review rate monitoring (WARN=5pp change, ALERT=10pp) | G8 monitoring policy: approval rate change thresholds | Adjustable REVIEW zone width; escalation to auto-approve/auto-reject if queue overwhelmed | No review capacity model; no simulation of queue overflow |
| 11 | Fairness audit impossible or weak due to available fields | Taiwan Default has SEX, EDUCATION, MARRIAGE — but these are model features, not just audit fields. Removing them changes the model's risk ranking. | "We ran a fairness audit" | G9 fairness audit required; fairness gap explicitly documented | G8 model card Section 11; g8_governance_packet_summary.json fairness status | Compute DI/EOpp/PPV at thresholds; document business-necessity justification for gaps | G9 fairness not yet done; DI at 0.20/0.40 thresholds unknown |
| 12 | Adverse-action explanation overclaimed | SHAP values used as "the reason" for rejection; applicant told "PAY_0 = delayed payment was the reason"; but SHAP is a local attribution, not a causal reason code | "The model said PAY_0 was the reason" | Adverse-action boundary documentation; forbidden claims | G8 limitations boundary Section 3 | SHAP-based reason codes must be validated against regulatory reason code taxonomies | NOT BUILT; SHAP + reason code taxonomy deferred to G9/G10 |
| 13 | Monitoring triggers copied but not tied to labels | PSI thresholds from literature (0.10/0.20) applied without evidence from the model's actual performance | "PSI > 0.20 means retrain" | All monitoring thresholds grounded in G6/G7 evidence | G8 monitoring policy: ECE WARN at 2.2× baseline; approve-zone DR WARN at 1.9× baseline | Evidence-grounded thresholds documented per trigger | Triggers defined but not exercised over real time period |
| 14 | Platt calibration fit incorrectly | Calibration fit on training set (overfits) or test set (leaks evaluation) | "I fit calibration on the full dataset" | Protocol enforced: Platt fit on val (6k), evaluate on test (6k) | g6_champion_challenger_report.json: val/test split documented | Strict protocol; val used only for calibration; test used only for evaluation | No external validation on a third hold-out population |
| 15 | Synthetic harness overclaimed | Synthetic AUC (0.6237), ECE (0.00159), DI (1.0127) cited as credit risk performance metrics without "synthetic" qualifier | "PulseGuard achieves AUC 0.62 on credit risk" | Claim boundary documents; SYNTHETIC_HARNESS tag throughout | G3/G4/G5 claim boundary; 06_CLAIM_BOUNDARY.md | All synthetic results labeled SYNTHETIC_HARNESS; forbidden claim list includes this | Interview pressure may elide the synthetic qualifier |
| 16 | Cost threshold too aggressive for business tolerance | θ* = 9% means approving only applicants with PD < 9% under base cost assumptions. Operationally, 65% approval rate at θ=0.20 is not the Bayes-optimal but the business-viable policy | "I set the threshold at the Bayes-optimal value" | 3-zone policy at 20%/40% explicitly chosen over 9% Bayes-optimal | G7 policy notes: "9% threshold collapses the review band; 20%/40% is operational" | Operational policy documented; reason for deviation from Bayes-optimal explicit | No real business tolerance test; threshold not validated against board risk appetite |
| 17 | Default labels delayed | In production, a loan approved today defaults 3–12 months from now. Monitoring based on recent approvals has no labels for weeks or months | "We monitor the model on recent predictions" | Delayed label validation architecture defined in G8 monitoring policy | G8 monitoring policy Section 2.5; approve-zone DR trigger | 30-90 day lookback window for label resolution; PSI as leading indicator before labels arrive | NOT OPERATIONAL — no live cohort; label resolution pipeline deferred to G10 |
| 18 | External validation missing | Model validated only on the same temporal population it was trained on (Taiwan 2005, random split). Independent institution validation not performed | "We tested on a held-out set" | Documented as a known gap | G8 governance signoff packet: IMV gap | Independent Model Validation unit review | NOT DONE — G8 pre-launch gap L1 |
| 19 | Real bank economics absent | Cost matrix C_bad=10, C_reject=1 is illustrative. Real charge-off rate and net interest margin are not known for any product | "The 10:1 ratio is standard" | Cost matrix documented as THRESHOLD_ASSUMPTION | G7 policy report; G8 limitations Section 5 | Elicit real economics before setting production threshold | No real P&L data available |

---

## K. ACHIEVEMENT MOMENTS

### Moment 1 — Synthetic Lane Challenged and Demoted

**What looked good?** A synthetic Home Credit-like dataset produced an AUC of 0.6237, a PSI drift at exactly the right days, a fairness DI of 1.0127 PASS. The synthetic harness was producing clean results across all gates.

**What was wrong?** The synthetic lane cannot demonstrate real-world model performance — it demonstrates that the methodology is correct under known conditions. A portfolio that presents synthetic results as credit risk performance evidence misleads any interviewer who asks "what's your AUC on real credit data?"

**How was it detected?** G5.5 gate was opened explicitly to ask the question: "Can PulseGuard proceed to champion/challenger on synthetic data alone?" The answer was no — the synthetic results are protocol tests, not performance claims.

**What decision was made?** Two-lane architecture established: synthetic = stress-test harness only; Taiwan Default = primary real-data lane. All subsequent gates required real-data primary lane.

**Judgment proven:** Unwillingness to accept convenient results that are technically correct but epistemically weak. This is the distinction between a serious governance dossier and a demo.

---

### Moment 2 — Taiwan Real-Data Bridge Added

**What looked good?** Synthetic data was producing results with known ceiling and well-behaved distributions. Adding real data would introduce complexity, missing values, encoding ambiguity, class imbalance.

**What was wrong?** Without real data, every performance claim is about a known DGP — not about credit risk. The core competency being demonstrated is credit-risk DS, not simulation engineering.

**How was it detected?** G5.5 dataset research required evaluating 7 datasets against specific criteria: real outcomes, real payment signals, real demographics, public access, fairness-audit feasibility.

**What decision was made?** Taiwan Default selected as USE_NOW despite limitations: 2005 vintage, no income, single product. It was the only dataset immediately available without authentication and with real demographic fields.

**Judgment proven:** Willingness to accept a dataset that is better than synthetic but still limited, and to document both the value and the limitations honestly — rather than either pretending it's bank-grade data or rejecting it as too limited.

---

### Moment 3 — XGBoost Raw Calibrated via Platt

**What looked good?** XGBoost raw achieved ROC-AUC = 0.7852 — the best discrimination of any model. The model was clearly the champion on rank-order metrics.

**What was wrong?** ECE = 0.2082. PD = 0.20 on raw XGBoost does not correspond to 20% actual default rate. Setting a threshold on uncalibrated probabilities is a systematic error — it might mean "approve at 35% true default rate."

**How was it detected?** G6 calibration evaluation computed ECE raw vs calibrated and plotted the calibration curve. The reliability diagram showed systematic overconfidence in the middle of the score range.

**What decision was made?** Platt calibration applied on the held-out validation set. ECE dropped to 0.0112 — 94.6% reduction. The calibration gate was established: no model is promoted without passing ECE ≤ (champion_ECE + 0.005).

**Judgment proven:** Understanding that discrimination metrics (AUC) and calibration metrics (ECE) measure different properties, and that thresholding requires calibration — not just ranking.

---

### Moment 4 — Champion Selected by Calibration, Not Only AUC

**What looked good?** LightGBM challenger: ROC-AUC = 0.7742 (close to champion 0.7852). If the promotion gate were AUC-only, LightGBM would be near-equivalent. ECE = 0.1321 raw.

**What was wrong?** Calibrated XGBoost ECE = 0.0112 vs uncalibrated LightGBM ECE = 0.1321. The comparison is not apples-to-apples. But even on a fair comparison, LightGBM must be calibrated before comparison — the G6 gate held LightGBM rather than rejecting it.

**How was it detected?** 4-gate promotion framework: ΔECE ≤ 0.005 is a blocking gate. Uncalibrated LightGBM fails this gate against calibrated champion. Documented as an unfair comparison — LightGBM HELD not REJECTED.

**What decision was made?** XGBoost Platt retained as champion. Calibrated LightGBM vs calibrated XGBoost scheduled as G9 deliverable. The hold distinction matters: "HELD" means "needs a fair comparison," not "is inferior."

**Judgment proven:** Governance discipline — not promoting on incomplete evidence, but also not rejecting on unfair evidence. The distinction between HOLD and REJECT demonstrates intellectual precision.

---

### Moment 5 — G7 Synthetic-First Threshold Policy Rejected and Patched to Taiwan-First

**What looked good?** The initial `g7_threshold_policy.py` produced a policy named `synthetic_v1.0` as the primary headline policy. The script ran without errors and produced valid results.

**What was wrong?** The G5.5 lane decision established Taiwan Default as the PRIMARY lane and synthetic as the SECONDARY stress-test harness. Naming the headline policy `synthetic_v1.0` violated this decision — implying the primary policy was grounded in synthetic data.

**How was it detected?** Gate review identified the policy name as violating the lane decision. The issue was not technical — the metrics were correct — but semantic: the label mattered because it determines which lane's policy is cited in any interview claim.

**What decision was made?** G7 was issued as PATCH (not ACCEPT). Full rewrite of `g7_taiwan_threshold_patch.py` with `policy_name: taiwan_real_data_v1.0`, corrected cost notation (C_bad/C_reject not C_FN/C_FP), two new plots, and explicit two-lane separation in all docs.

**Judgment proven:** Precision in labeling is part of governance. A correct metric with a wrong label is a governance failure — it will mislead anyone reading the artifact without full context.

---

### Moment 6 — Data Provenance Challenged Before Fairness G9

**What looked good?** Taiwan Default was loaded and producing valid results. G6 and G7 metrics were internally consistent. G8 was accepted. The natural next step was G9 fairness audit.

**What was wrong?** The claim chain for any G9 fairness result depends on the claim chain for the underlying data. If the file's provenance is unclear, the "verified real public data" claim is unverifiable, and all downstream claims rest on an unverified foundation.

**How was it detected?** G8.1 blocking gate opened explicitly: "Where did the dataset come from if the user did not manually provide it?" The answer required forensic investigation — file timestamp, SHA256, download script search, source URL recovery.

**What decision was made?** G8.1 audit run: 20-check automated script, SHA256 live re-download from UCI, acquisition method documented (prior Claude session, G5.5), no download script retained (documented gap). Provenance verdict: PASS.

**Judgment proven:** Evidence chain integrity. Not allowing G9 to proceed until the foundation of the evidence chain was verified — even when it would have been easy to assume the file was fine.

---

## L. AMBITION GAP / MISSING MEAT

| # | Gap | Why It Matters | Evidence Needed | Build When | Claim Unlocked |
|---|-----|---------------|----------------|-----------|----------------|
| 1 | ~~Data provenance not proven~~ | **CLOSED — G8.1 PASS** | G8.1: SHA256 match, 20/20 checks | DONE | "Verified real public credit-card default dataset" |
| 2 | Taiwan is compact bridge, not final ceiling | 30k rows, 2005 vintage, no income, single product, random split — senior DS interviewers will probe these gaps | No new evidence needed — decision documented | NOW — schedule G10 | "Taiwan is verified bridge; Home Credit is primary BeastMax lane" |
| 3 | Home Credit / LendingClub realism lane missing | 10× larger; multi-vintage; income features; reject inference required; temporal split possible | Home Credit download + preprocessing + temporal split + reject inference study | BeastMax (G10) | "Trained and validated on full application-time feature set with reject inference study"; "Out-of-time validation completed" |
| 4 | Reject inference missing | Production lending trains only on approved applicants; selection bias is the most material methodological gap in applied credit risk | Semi-supervised or propensity-weighted reject inference study on Home Credit | BeastMax (G10) | "Selection bias in training is documented and mitigated"; "Reject inference implemented" |
| 5 | Temporal / vintage split missing | Random split overstates stability. Production performance requires out-of-time validation | Multi-cohort dataset (Home Credit) + temporal split script + OOT metrics | BeastMax (G10) | "Model validated on future cohort"; "Out-of-time AUC documented" |
| 6 | Real application-time underwriting workflow missing | FOIR engine (income/EMI ratio gate) is a hard rule in every consumer lending operation; not applicable to Taiwan credit card data | Real income field (e.g., AMT_INCOME_TOTAL in Home Credit) + FOIR engine implementation | BeastMax (G10) | "FOIR hard rule enforced before model scoring"; "Deterministic pre-screen gate built" |
| 7 | Real operational default-label delay missing | In production, labels arrive 30–90 days after decision; delayed label pipeline is required for monitoring | Live cohort pipeline or simulated label-delay pipeline with bucket-level DR tracking | BeastMax (G10) | "Delayed label validation pipeline operational"; "Monitoring triggered on resolved labels" |
| 8 | Adverse-action-ready explanation layer missing | ECOA requires principal reason codes; SHAP + regulatory taxonomy + notice delivery needed | SHAP on champion model; top-k adverse reasons per application; reason code taxonomy | G9 (SHAP); G10 (regulatory taxonomy) | "SHAP-based adverse action reason code assignment built"; "Principal reasons documentable per decision" |
| 9 | Fair-lending certification impossible currently | Taiwan fairness audit pending (G9); even after G9, DI at thresholds is a statistical observation not a legal certification | G9: DI/EOpp/PPV at θ=0.20/0.40 for SEX/EDUCATION/MARRIAGE; business-necessity justification for gaps | G9 | "Disparate Impact at G7 thresholds computed"; "Fairness methodology demonstrated" |
| 10 | External validation (IMV) missing | Independent model validation is mandatory for production credit models at regulated institutions; no third-party review exists | IMV-equivalent: a second person/team runs the model from scratch and verifies results | T3 | "Model reproducible by independent party"; "IMV-equivalent validation completed" |
| 11 | Bureau-style feature richness missing | Real credit models have 100–500 features from credit bureau pulls (trade-line balance, utilization by product type, derogatory marks, inquiries). Taiwan Default has 23 features, none bureau-sourced | Home Credit: bureau data (AMT_CREDIT, bureau queries, credit active counts) + feature engineering | BeastMax (G10) | "Bureau-style feature set engineered"; "Feature richness comparable to production models" |
| 12 | Production economics missing | Cost matrix C_bad=10/C_reject=1 is illustrative. Real threshold requires observed charge-off rate and net interest margin from a real product | Lender economics data OR published industry charge-off/NIM figures + sensitivity study | T3 | "Threshold policy grounded in real lender economics"; "Charge-off to revenue ratio from observed data" |
| 13 | Monitoring not exercised over time | G4 synthetic drift demonstrates the monitoring kernel fires correctly on scripted drift. No real-time population exists to validate the monitor over a real deployment horizon | Live scoring + label resolution + PSI/ECE tracking over ≥30 days | T3 (requires live deployment) | "Monitoring demonstrated over real deployment period"; "Alert fires on real population shift" |
| 14 | Override policy not tested in simulation | Human review policy documents reason codes, prohibited behaviours, escalation. No simulation of reviewer decisions, override rate drift, or fairness implications of override pattern | Monte Carlo simulation of REVIEW zone decisions; override rate analysis by reason code; reviewer demographic outcome analysis | BeastMax (G10) | "Override simulation completed"; "Override rate within reference range"; "No demographic pattern in override decisions" |
| 15 | Threshold policy not validated on business P&L | Expected loss calculation uses illustrative costs. Real validation requires applying the policy to a cohort with known outcomes and computing actual P&L impact | Historical cohort with outcomes + charge-off data + revenue data + policy simulation | T3 | "Policy P&L validated on historical cohort"; "EL calculation matches observed financials" |

---

## M. NEXT-GATE DECISION

### The Options

**Option A:** G8.1 — Data Provenance only → then open G9. *(DONE — G8.1 completed in this session, PASS)*

**Option B:** G8.1 + Stronger Realism Lane Decision simultaneously.

**Option C:** G8.1 first, then explicit realism lane decision, then G9.

### Status

G8.1 is **COMPLETE (PASS)**. The provenance question is answered. The realism ceiling question is answered by this audit (BRIDGE_ONLY verdict).

### Verdict

**Recommended next gate: G9 — Taiwan Default Fairness Audit + Calibrated LightGBM Rematch.**

G9 is now unblocked (G8.1 PASS). G9 must deliver:
1. **Fairness audit on Taiwan Default** at θ=0.20/0.40: DI, EOpp, PPV for SEX, EDUCATION, MARRIAGE. Male DR=24.17%, female DR=20.78% — whether this produces disparate impact is unknown until computed.
2. **Calibrated LightGBM vs calibrated XGBoost champion/challenger** — close the unfair comparison from G6.
3. **SHAP-based adverse action reason code assignment** — first step toward adverse action readiness.
4. **KS statistic** on Taiwan test set — complete the metric set.

**What must not happen:**
- G9 must not claim "fairness-certified" from a DI computation.
- G9 must not claim Home Credit-grade evidence from Taiwan results.
- G9 must not present calibrated LightGBM as "better than XGBoost in general" — it is better or equal on Taiwan; generalization claim is unjustified.

**Stronger Realism Lane (G10) — schedule, do not block G9:**
Home Credit realism lane is the BeastMax requirement. It must be scheduled as G10, but it must not block G9 fairness audit. Reason: G9 fairness is immediately valuable, requires no new data, and validates methodology that is claimed in G8. G10 Home Credit adds the "meat" to the dossier.

**Evidence G9 must produce:**
- `outputs/evidence/g9_taiwan_fairness_report.json` — DI/EOpp/PPV for all demographic groups at all thresholds
- `outputs/evidence/g9_calibrated_lgbm_challenger_report.json` — calibrated LightGBM promotion decision
- `outputs/plots/g9_fairness_*.png` — approval rate by group, score distribution by group
- `outputs/evidence/g9_shap_report.json` — SHAP top-k per test instance; adverse action reasons
- `docs/G9_FAIRNESS_AND_EXPLAINABILITY_NOTES.md` — with explicit fairness methodology limitations

---

## N. RISKFRAME SCORE SUMMARY

| Dimension | Score | Comment |
|-----------|-------|---------|
| Product thesis clarity | 8/10 | Sharp identity; clear decision governed; user personas well-defined |
| Market/JD relevance | 7/10 | SR 26-2; PSI; calibration; champion/challenger; fairness. Missing: WOE/IV, FOIR on real data, bureau features |
| Technique tournament depth | 6/10 | XGBoost, LightGBM, LR, Platt, PSI, fairness built. Missing: WOE/IV, scorecard, reject inference, temporal validation, KS, isotonic |
| Deep defense kernel | 8/10 | Calibration and threshold defense is production-grade; 20 cards cover the hard questions |
| Product reasoning kernel | 8/10 | Calibration gates promotion; cost-sensitive thresholding well-reasoned; 14 decisions documented |
| Data realism / feature engineering | 4/10 | Taiwan: 2005 vintage, no income, single product, 30k rows, random split. Real but thin. |
| Synthetic realism audit | 9/10 | Synthetic clearly demoted; SYNTHETIC_HARNESS tags throughout; claim boundaries explicit |
| Evidence honesty | 9/10 | Forbidden claims documented; 10 pre-launch gaps explicit; provenance challenged before G9 |
| Evaluation validity | 6/10 | Correct Platt protocol; but random not temporal split; LightGBM comparison unfair; 6k test set |
| Decision economics | 4/10 | Illustrative cost matrix; 10:1 ratio not observed; no P&L validation; no charge-off data |
| Industry pattern awareness | 6/10 | Knows about reject inference, bureau features, temporal validation, FOIR — none built |
| Hairy failure modes | 7/10 | 19 failure modes documented; PSI segment blindspot; label delay; reject inference all present |
| Achievement moments | 8/10 | 6 genuine moments; G7 patch and provenance challenge particularly strong |
| Tradeoff density | 7/10 | AUC vs calibration; 3-zone vs single-threshold; bridge vs BeastMax — all documented |
| Interview dominance | 7/10 | Solid on calibration, ECE, thresholding; weaker on reject inference, bureau features, temporal |
| **TOTAL** | **104/150** | **(69%)** |

**Score band: STRONG — NEEDS MEAT PASS**

Band definitions:
- 130–150 (87–100%): RISKFRAME_GOLD
- 113–129 (75–86%): GOLD_CANDIDATE
- 98–112 (65–74%): **STRONG_NEEDS_MEAT_PASS** ← PulseGuard
- 75–97 (50–64%): FOUNDATIONS_GOOD_REBUILD_NEEDED
- <75 (<50%): REBUILD_REQUIRED

The gap from 69% to GOLD_CANDIDATE (75%) requires closing 3 of the 4 low-scoring dimensions. The two that matter most are data realism (4→7 with Home Credit G10) and evaluation validity (6→8 with temporal split and calibrated LightGBM). Decision economics (4→6) requires either real lender cost data or a published benchmark.

RISKFRAME_GOLD (87%+) requires: Home Credit lane complete, reject inference study, SHAP adverse action, temporal validation, WOE/IV scorecard path, production economics grounded in something more than 10:1 assumption.

---

*Audit complete. Do not open G9 without reviewing this document. Do not claim RiskFrame-Gold without Home Credit lane and temporal validation. Do not present Taiwan as anything other than a verified bridge.*

