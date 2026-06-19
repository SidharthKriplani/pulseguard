# PulseGuard — Future Builds Backlog

**Status:** GOLD CHECKPOINTED — project frozen. This backlog documents intentionally deferred work.  
**Rule:** Nothing below is a blocker for the current resume/interview defense cycle.  
**Date:** 2026-06-17

---

## 1. High-Value Future Upgrades

These would materially raise the Gold audit score and unlock new interview claims.

---

### 1.1 Optuna 100-Trial Search on GPU

**Purpose:** Replace 4–8-trial CPU-bound HPO with a proper 100-trial search per model on GPU.  
**Evidence unlocked:** "Globally optimised champion" vs current "reasonable local optimum". Wider search space (n_estimators up to 1000, deeper max_depth).  
**Why not needed now:** 4–8 trials on CPU is honestly documented. The champion at AUC=0.7769 is already +0.0053 over the baseline. Diminishing returns beyond 100 trials for this dataset size.  
**Risk if built badly:** Over-tuning to val set if trial budget is too large without additional hold-out; data leakage from repeated val evaluation.  
**Priority:** HIGH

---

### 1.2 Out-of-Time Validation (if timestamped credit data available)

**Purpose:** True temporal split — train on earlier applications, validate/test on later ones. Demonstrates model robustness to concept drift.  
**Evidence unlocked:** Vintage analysis; performance stability across cohorts; PSI between real temporal splits.  
**Why not needed now:** Home Credit has no application timestamps. SK_ID_CURR is not monotonically time-ordered. Structurally impossible on current data.  
**Risk if built badly:** Faking temporal order using applicant ID (not validated) would be a material methodological error and claim boundary violation.  
**Priority:** HIGH — requires new dataset (e.g., HMDA with application dates, or a private credit dataset)

---

### 1.3 Real Cost Matrix from Lender Economics

**Purpose:** Replace scenario economics (C_bad=10, C_reject=1) with published lender benchmarks: LGD % of credit line, NIM on good loans, administrative review cost per application.  
**Evidence unlocked:** "Cost-optimal threshold calibrated to real NIM" rather than "scenario assumption". Enables defensible claim on threshold selection.  
**Why not needed now:** Scenario assumptions are honestly documented and correctly labelled SCENARIO_ASSUMPTIONS_NOT_REAL_BANK_ECONOMICS. Any threshold claim requires credit policy sign-off in production.  
**Risk if built badly:** Using a mismatched lender benchmark (e.g., mortgage LGD for consumer loan) invalidates the entire decisioning analysis.  
**Priority:** MEDIUM — requires research into published lender economics papers or partner institution context.

---

### 1.4 Full Fairness Audit with Protected-Class Labels

**Purpose:** Compute Disparate Impact ratio, Equal Opportunity gap, PPV parity, and calibration gap across protected classes (sex, race/ethnicity, national origin) on demographically enriched data.  
**Evidence unlocked:** Defensible claim on disparate impact compliance analysis; model can proceed to fair-lending pre-review.  
**Why not needed now:** Home Credit has no protected-class labels. Proxy analysis (age/income/region) is the maximum achievable. Full fairness audit requires HMDA, CFPB data, or a private demographically labelled dataset.  
**Risk if built badly:** Using age/income/region as direct protected-class proxies without disclosure would be a methodological overclaim.  
**Priority:** HIGH — requires new dataset with demographic fields

---

### 1.5 Champion/Challenger Monitoring Loop

**Purpose:** Deploy challenger (XGBoost_monotonic, composite=0.7294) alongside champion. Monitor AUC, KS, PSI monthly. Promote challenger if champion degrades.  
**Evidence unlocked:** "Running live champion/challenger comparison" — the RiskFrame Gold Audit's highest-value governance feature.  
**Why not needed now:** No production data stream. Champion/challenger framework design is documented in control tower and governance report; build requires serving infrastructure.  
**Risk if built badly:** Promoting challenger based on single-month noise rather than statistically significant degradation.  
**Priority:** HIGH for production; MEDIUM for portfolio upgrade

---

### 1.6 Drift Monitoring Dashboard

**Purpose:** Monthly PSI and KS monitoring on score distribution + top-10 features. Automated WARN/ALERT/CRITICAL thresholds with notification.  
**Evidence unlocked:** "Live drift monitoring operational" — closes the G4-synthetic drift harness gap with real-model monitoring.  
**Why not needed now:** No production data stream. Monitoring policy is documented; build requires data pipeline and alerting infrastructure.  
**Risk if built badly:** False alerts from calibration artefact (train-vs-deploy PSI) being misinterpreted as drift.  
**Priority:** HIGH for production; MEDIUM for portfolio

---

### 1.7 Production-Shaped FastAPI Scoring API

**Purpose:** Serve champion model as REST endpoint with feature validation, prediction latency tracking, and training-serving parity check.  
**Evidence unlocked:** "FastAPI scoring in <50ms" — closes the G9 serving gap. Demonstrates ML engineering beyond modeling.  
**Why not needed now:** Portfolio project; offline evaluation is complete and documented.  
**Risk if built badly:** Serving pipeline that doesn't match training pipeline (different scaling, feature order) — a classic training-serving skew bug.  
**Priority:** MEDIUM — valuable for ML engineering roles, not required for data science interviews

---

### 1.8 MLflow / Model Registry

**Purpose:** Track all model versions, hyperparameters, and metrics in a model registry. Champion promotion logged with full artifact lineage.  
**Evidence unlocked:** "MLflow model versioning" — adds production MLOps credibility.  
**Why not needed now:** Evidence ledger (`04_EVIDENCE_LEDGER.md`) serves as manual model registry for portfolio purposes.  
**Risk if built badly:** Registry without governance rules (approval workflow) is just a file store — doesn't add interview value over the evidence ledger.  
**Priority:** MEDIUM

---

### 1.9 Stronger Policy Corpus for RAG/LLM Layer

**Purpose:** Expand BM25 policy corpus from 5 to 50+ documents covering ECOA, Regulation B, SR 26-2 sections, CFPB guidelines, adverse action code registry, model risk committee procedures.  
**Evidence unlocked:** "RAG retrieval over 50-document credit policy corpus" — elevates the governance assistant from demo to prototype.  
**Why not needed now:** 5-document corpus demonstrates the architecture correctly. Retrieval quality and abstain behaviour work. Scale requires policy document curation.  
**Risk if built badly:** Large corpus with weak documents degrades retrieval quality and increases hallucination risk.  
**Priority:** MEDIUM

---

## 2. Nice-to-Have Upgrades

Low-effort but not high-impact for interview defense.

---

### 2.1 Streamlit Decision Demo UI

**Purpose:** Interactive front-end where a user inputs applicant features, gets a PD score, band assignment, and top-3 SHAP reason codes in real time.  
**Evidence unlocked:** "Interactive demo" for portfolio presentations.  
**Why not needed now:** Offline evidence is complete and more rigorous than a UI demo.  
**Risk if built badly:** Demo that looks polished but produces wrong scores if feature pipeline is mismatched.  
**Priority:** LOW for interviews; MEDIUM for portfolio showcase events

---

### 2.2 Richer Underwriter UI

**Purpose:** Credit officer review interface showing applicant summary, model score, band, SHAP waterfall, policy-retrieved memo, and override logging.  
**Evidence unlocked:** "Human-in-the-loop workflow demo" for governance presentations.  
**Why not needed now:** The 6-case RAG/LLM demo and local case SHAP report cover the same evidence space.  
**Risk if built badly:** UI that appears to approve/reject applicants autonomously — violates the ASSISTIVE_ONLY design principle.  
**Priority:** LOW

---

### 2.3 More Applicant Case Studies

**Purpose:** Expand from 4 local SHAP cases to 20+ — including edge cases (borderline GREEN/AMBER, very high PD, conflict case with business override).  
**Evidence unlocked:** Richer qualitative narrative for interviews.  
**Why not needed now:** 4 cases cover the full decision spectrum (approve/review/decline/conflict).  
**Priority:** LOW

---

### 2.4 Scorecard-Style Secondary Model (WOE/IV)

**Purpose:** Build a logistic regression scorecard as an interpretability benchmark against LightGBM. Demonstrates classic credit scoring methodology.  
**Evidence unlocked:** "Scorecard vs GBM comparison" — relevant for traditional credit risk roles.  
**Why not needed now:** LightGBM + monotone constraints + SHAP covers the interpretability requirement. Scorecard is additive, not required.  
**Priority:** LOW for ML governance roles; MEDIUM for traditional credit scoring roles

---

### 2.5 Bootstrap Confidence Intervals on Test Metrics

**Purpose:** Report AUC=0.7769 ± 0.003 (95% CI) rather than a point estimate. Demonstrates statistical rigour.  
**Evidence unlocked:** "AUC confidence interval on 61k test set".  
**Why not needed now:** Standard for publications; acceptable for portfolio without CI. Test set is 61k rows — CI on AUC will be narrow (±0.002–0.003).  
**Priority:** LOW

---

## 3. Do-Not-Build / Distraction List

These are explicitly prohibited for this portfolio cycle. Do not add them.

---

### 3.1 Taiwan Default as Primary Dataset

**Why not:** Home Credit (307k, 7 tables, 57.4M rows) is materially stronger evidence. Taiwan (30k, single table, 2005 vintage) regresses the portfolio. Reintroducing Taiwan as primary invalidates the G9A/Pass 2–4 champion and requires retraining.  
**Risk:** Weaker data realism; portfolio regression; interview narrative confusion.

---

### 3.2 LendingClub Reintroduction

**Why not:** LendingClub is dropped from current scope. Reject inference is a separate future workstream. Reintroducing it before reject inference is implemented would require honest labelling of the approved-applicant bias — the same problem as Home Credit.  
**Risk:** Scope creep; no evidence value over Home Credit.

---

### 3.3 Fake Production Deployment

**Why not:** Claiming production deployment when none exists is the #1 resume red flag in technical interviews. Interviewers ask "what's your p99 latency?" and "what monitoring alerts have fired?" — questions that expose a fake deployment immediately.  
**Risk:** Interview failure; reputational damage.

---

### 3.4 Legal Adverse Action Notice Generator

**Why not:** Legally compliant adverse action notices require licensed credit officer review and sign-off under ECOA and Regulation B. Building an automated generator and claiming legal compliance is a regulatory overclaim.  
**Risk:** Serious legal and ethical claim violation. LLM output is ASSISTIVE_ONLY by design.

---

### 3.5 LLM Autonomous Credit Decisioning

**Why not:** The governance design explicitly prohibits this. An LLM that autonomously approves or rejects applicants creates material legal and ethical liability. This is also a senior interviewer red flag for governance awareness.  
**Risk:** Violates ASSISTIVE_ONLY principle; governance design collapses.

---

### 3.6 Fairness Certification Claim

**Why not:** Full fairness certification requires protected-class labels, a formal disparate impact analysis, legal review, and independent validator sign-off. No combination of proxy analysis achieves this.  
**Risk:** Claim boundary violation; interview exposure.

---

### 3.7 Full Vintage Curves Without Time Data

**Why not:** Vintage analysis requires a time dimension. Creating fake vintage curves by binning on applicant ID or application number is methodologically invalid and dishonest.  
**Risk:** If an interviewer asks "how did you create the vintage split?", the answer exposes the fabrication.

---

## Summary Table

| Build Item | Category | Priority | Blocker for Defense? |
|---|---|---|---|
| Optuna 100-trial GPU | High-value | HIGH | No |
| Out-of-time validation | High-value | HIGH | No |
| Real cost matrix | High-value | MEDIUM | No |
| Full fairness audit | High-value | HIGH | No |
| Champion/challenger monitoring | High-value | MEDIUM | No |
| Drift monitoring dashboard | High-value | MEDIUM | No |
| FastAPI serving | High-value | MEDIUM | No |
| MLflow/model registry | High-value | MEDIUM | No |
| Stronger policy corpus | High-value | MEDIUM | No |
| Streamlit UI | Nice-to-have | LOW | No |
| Underwriter UI | Nice-to-have | LOW | No |
| More case studies | Nice-to-have | LOW | No |
| WOE/IV scorecard | Nice-to-have | LOW | No |
| Bootstrap CIs | Nice-to-have | LOW | No |
| Taiwan as primary | DO NOT BUILD | — | — |
| LendingClub reintroduction | DO NOT BUILD | — | — |
| Fake production deployment | DO NOT BUILD | — | — |
| Legal adverse action generator | DO NOT BUILD | — | — |
| LLM autonomous decisioning | DO NOT BUILD | — | — |
| Fairness certification claim | DO NOT BUILD | — | — |
| Fake vintage curves | DO NOT BUILD | — | — |

---

*PulseGuard Future Builds Backlog | Gold Pass 4/4 | 2026-06-17*
