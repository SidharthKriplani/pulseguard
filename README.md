# PulseGuard — Credit Risk Governance Platform

<p align="left">
  <!-- Champion row -->
  <img src="https://img.shields.io/badge/Champion-LightGBM__monotonic-22c55e?style=flat-square" alt="Champion"/>
  <img src="https://img.shields.io/badge/AUC-0.7769-22c55e?style=flat-square" alt="AUC"/>
  <img src="https://img.shields.io/badge/ECE-0.0034-22c55e?style=flat-square" alt="ECE"/>
  <img src="https://img.shields.io/badge/KS-0.4141-22c55e?style=flat-square" alt="KS"/>
  <img src="https://img.shields.io/badge/PR--AUC-0.2628-22c55e?style=flat-square" alt="PR-AUC"/>
  <img src="https://img.shields.io/badge/Dataset-307k_applicants-22c55e?style=flat-square" alt="Dataset"/>
</p>

<p align="left">
  <!-- Live endpoint row -->
  <a href="https://pulseguard-api-98058433335.us-central1.run.app/health">
    <img src="https://img.shields.io/badge/Live_Endpoint-Cloud_Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white" alt="Live"/>
  </a>
  <img src="https://img.shields.io/badge/Served_Model-G4_XGBoost-f59e0b?style=flat-square" alt="Served Model"/>
  <img src="https://img.shields.io/badge/Served_AUC-0.6261-f59e0b?style=flat-square" alt="Served AUC"/>
  <img src="https://img.shields.io/badge/Bayes_Efficiency-99.6%25-8b5cf6?style=flat-square" alt="Bayes Efficiency"/>
  <img src="https://img.shields.io/badge/Serving_Gap-Documented-ef4444?style=flat-square" alt="Serving Gap"/>
</p>

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/LightGBM-4.3-00B050?style=flat-square" alt="LightGBM"/>
  <img src="https://img.shields.io/badge/XGBoost-2.0-red?style=flat-square" alt="XGBoost"/>
  <img src="https://img.shields.io/badge/SHAP-reason_codes-FF6B6B?style=flat-square" alt="SHAP"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Gold_Pass-4%2F4-22c55e?style=flat-square" alt="Gold Pass"/>
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License"/>
</p>

> A credit risk governance platform — built to answer: **when does a model score become a defensible governance output, and what happens when the champion can't be deployed?**  
> Built on Home Credit Default Risk (307,511 real applicants). Champion efficiency 99.6% of the Bayes ceiling on the synthetic lane. Serving gap between champion and live endpoint fully documented. Every result is artifact-backed.

---

## Failure Mode Addressed

**Credit risk models fail not when the AUC is wrong, but when no one documents the gap between the champion and what's actually served.** A model can win a tournament on val AUC, pass a calibration gate, and still be permanently undeployable due to a serialization version lock. A model can show SHAP reason codes and still fire them against the wrong pandas index. An early-stopping hyperparameter can silently interact with class imbalance to halt training at tree #9.

PulseGuard is built around making those failure points explicit, reproducible, and documented — not hidden in a notebook or discovered in an interview.

The domain — binary credit default prediction on real applicant data — is the test environment. Champion/challenger governance, calibration auditing, SHAP-grounded reason codes, and a fully documented deployment gap are the thesis.

---

## Architecture

![PulseGuard Two-Lane Architecture](docs/assets/pipeline_architecture.svg)

---

## Sample Scoring Output

![PulseGuard Sample Output](docs/assets/sample_output.svg)

---

## The Problem

Manual credit underwriting is slow, inconsistent, and poorly documented. A loan officer reviewing bank statements and income declarations takes 4–8 hours per application, produces inconsistent outcomes across reviewers, and generates regulatory exposure when scoring rationale is missing or unreproducible. The Reserve Bank of India mandates FOIR and LTV compliance; global SR 26-2 / FDIC guidance requires documented model risk governance, explainability, and drift monitoring.

PulseGuard demonstrates what that governance stack looks like end-to-end: a champion model selected through a 3-model tournament with Optuna HPO, Platt-calibrated probabilities, SHAP-grounded adverse action codes, and a deployment layer that is honest about what it actually serves.

**Dataset:** [Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk) — 307,511 loan applicants, 7 tables, 140 engineered features, 8.1% observed default rate. The most widely benchmarked public credit dataset with a real-world applicant population.

---

## Champion Model

LightGBM_monotonic with Platt calibration — selected at Gold Pass 2 through Optuna TPE search over 5 trials, with 15 directional monotone constraints enforced on credit-relevant features. The tournament result reversed the G9A provisional champion (CatBoost) after the LightGBM early-stopping bug was diagnosed and corrected.

| Metric | Value | Notes |
|--------|-------|-------|
| Val AUC | 0.7734 | Held-out validation set |
| Test AUC | **0.7769** | Final held-out test set |
| ECE | **0.0034** | After Platt calibration; near-perfect |
| KS Statistic | 0.4141 | Separation at optimal threshold |
| PR-AUC | 0.2628 | Precision-recall area under curve |
| Scale pos weight | 11.39 | Reflects 8.1% observed default rate |
| Monotone constraints | 15 features | Governance: directional risk expectations enforced |
| Calibration method | Platt sigmoid | Fit on val set only; no data leakage |

### Why monotone constraints matter

A credit model that assigns lower default probability to higher debt-to-income ratios is legally and operationally indefensible, regardless of AUC. Monotone constraints guarantee the model cannot learn perverse relationships between credit-relevant features and default risk — a governance requirement, not a performance optimization. The 15 constrained features include credit amount, income, external credit scores, days employed, and family dependants.

---

## Model Tournament — Gold Pass 2

Three model families were tuned head-to-head with Optuna TPE (seed=42). The provisional G9A champion (CatBoost, val_AUC=0.7716) was overturned after diagnosing and correcting the LightGBM early-stopping interaction with class imbalance.

| Rank | Model | G9A Val AUC | GP2 Val AUC | ECE (Platt) | Gate decision | Notes |
|------|-------|------------|-------------|-------------|---------------|-------|
| **1** | **LightGBM_monotonic** | 0.7203 ⚠ | **0.7734** | **0.0034** | **CHAMPION** | Early stopping bug fixed — 15 monotone constraints |
| 2 | CatBoost | 0.7716 | 0.7716 | 0.0054 | Governance alt | G9A provisional champion; no directional constraints |
| 3 | XGBoost | 0.7703 | ~0.7703 | 0.0040 | Not promoted | Competitive; serves G4 synthetic demo at live endpoint |
| — | TabNet | HARD_FAIL | — | — | Excluded | ~6 min/epoch on CPU; est. 400–800h full training; no GPU |

**⚠ LightGBM early stopping bug:** With `eval_metric='auc'` and `scale_pos_weight=11.39`, LightGBM's early-stopping fires at iteration 1–9. The first tree captures most of the imbalanced gradient signal; subsequent marginal gains fall below stopping tolerance; training halts at 9 trees. G9A LightGBM AUC=0.7203 was entirely due to this bug, not model quality. Fix: treat `n_estimators` as an Optuna hyperparameter (range 150–400), remove early stopping from the objective. After fix: AUC jumps to 0.7734.

---

## Gold Pass Governance

PulseGuard is structured around a 9-gate development pipeline (G0–G9A) plus 4 Gold Pass review checkpoints. Every gate either passes with evidence or documents the exact failure and fix.

| Gate | What it validates | Result |
|------|-------------------|--------|
| G0 | Problem framing, dataset selection, DGP design | ✅ PASS |
| G1 | Data contracts, schema validation, leakage pre-audit | ✅ PASS |
| G2 | Feature engineering, ABT build, signal design | ✅ PASS |
| G3 / G3.1 | Synthetic DGP calibration — DR=8% target | ✅ PASS (binary search: intercept=−4.20703 in 8 iterations) |
| G4 | Champion on synthetic data — XGBoost, AUC=0.6261 | ✅ PASS |
| G5 | Dataset selection — Home Credit confirmed; Taiwan/LendingClub rejected | ✅ PASS |
| G6 | Real-data champion/challenger: LightGBM vs CatBoost vs XGBoost | ✅ PASS |
| G7 | Threshold policy, decision bands, adverse action codes | ✅ PASS |
| G8 | Governance signoff — fairness audit, model card, monitoring policy | ✅ PASS |
| G9A | Full model tournament (baseline) — CatBoost provisional champion | ✅ PASS |
| **Gold Pass 1** | Baseline tournament audit — BASELINE_NOT_TUNED flagged | ✅ COMPLETE |
| **Gold Pass 2** | Optuna HPO, LightGBM bug fix, LightGBM_monotonic crowned champion | ✅ COMPLETE |
| **Gold Pass 3** | SHAP reason codes, RAG policy layer, LLM governance memo | ✅ COMPLETE |
| **Gold Pass 4** | Cloud Run deployment, serving gap documented, stress test (12/12 PASS) | ✅ COMPLETE |

---

## Live Endpoint

PulseGuard is the only project in this portfolio with a live, public-facing model API.

**Base URL:** `https://pulseguard-api-98058433335.us-central1.run.app`

```bash
# Health check
curl https://pulseguard-api-98058433335.us-central1.run.app/health
# → {"status":"ok","model":"xgboost_g4_champion","n_features":28,"auc":0.6261}

# Score an applicant
curl -X POST https://pulseguard-api-98058433335.us-central1.run.app/score \
  -H "Content-Type: application/json" \
  -d '{
    "SK_ID_CURR": 100002,
    "AMT_CREDIT": 406597,
    "AMT_INCOME_TOTAL": 202500,
    "AMT_ANNUITY": 24700,
    "AMT_GOODS_PRICE": 351000,
    "DAYS_BIRTH": -9461,
    "DAYS_EMPLOYED": -637,
    "CODE_GENDER": "M",
    "NAME_INCOME_TYPE": "Working",
    "NAME_EDUCATION_TYPE": "Secondary / secondary special",
    "NAME_FAMILY_STATUS": "Married",
    "NAME_HOUSING_TYPE": "House / apartment",
    "CNT_CHILDREN": 0,
    "CNT_FAM_MEMBERS": 2
  }'
```

```json
{
  "pd": 0.2847,
  "band": "AMBER",
  "label": "REFER — human review required",
  "shap_top5": [
    {"feature": "EXT_SOURCE_2",        "shap":  0.0842},
    {"feature": "credit_income_ratio",  "shap":  0.0614},
    {"feature": "DAYS_EMPLOYED",        "shap": -0.0341},
    {"feature": "AMT_ANNUITY",          "shap":  0.0217},
    {"feature": "DAYS_BIRTH",           "shap": -0.0156}
  ],
  "flags": ["ASSISTIVE_ONLY", "HUMAN_REVIEW_REQUIRED", "NOT_FINAL_DECISION"],
  "model": "xgboost_g4_synthetic"
}
```

### ⚠ Serving gap — read before citing the endpoint

| | Live Endpoint | Champion |
|---|---|---|
| Model | G4 XGBoost (28 features) | LightGBM_monotonic (140 features) |
| Dataset | Synthetic (50k rows, 6-signal DGP) | Home Credit (307,511 real applicants) |
| AUC | 0.6261 | **0.7769** |
| Deployed? | ✅ Yes | ❌ No |

**Root cause:** GP2 LightGBM pkl artifacts were saved with sklearn 1.7.2 (requires Python 3.10+). The Cloud Run environment runs Python 3.9 (max sklearn 1.6.1). Loading a 1.7.2-serialized pkl under 1.6.1 raises `_pickle.UnpicklingError: invalid load key`. The artifacts are permanently unloadable in this environment. Fix at training time: pin sklearn in `requirements.txt` and match it exactly in the Dockerfile, or serialize to ONNX to decouple from sklearn versioning. Full audit: [06_CLAIM_BOUNDARY.md](06_CLAIM_BOUNDARY.md).

---

## Failures I'm Proud Of

Eight real failures, root-caused and documented. Not cleaned up. Not hidden.

| # | Failure | What it revealed |
|---|---------|-----------------|
| FA-01 | G3.1 DGP default rate 26% → target 8% | Binary search on logistic intercept over N=200k samples; converged at −4.20703 in 8 iterations |
| FA-02 | LightGBM early stopping at tree #9 (AUC=0.7203) | `scale_pos_weight × eval_metric` gradient landscape interaction; treat `n_estimators` as Optuna param |
| FA-03 | SHAP `KeyError` on `y_val[green_idx]` — 3 sessions to diagnose | Pandas Series indexed by Home Credit SK_ID_CURR IDs, not 0-based; fix: `.values` |
| FA-04 | RAG abstain not firing on OOD queries | BM25 threshold calibrated on multi-doc corpus; single-doc ceiling is lower; recalibrated at 0.25 |
| FA-05 | LightGBM labelled "rejected" — overclaim | It was held pending calibrated rematch; it then became champion |
| FA-06 | `X \| Y` union type annotation crash on Python 3.9 | `from __future__ import annotations` (PEP 563) makes annotations lazily-evaluated strings |
| FA-07 | sklearn 1.7.2 pkl unloadable on Python 3.9 | Environment parity: training and serving must share exact sklearn version |
| FA-08 | `pickle.load()` on a `joblib.dump()` artifact | `STACK_GLOBAL requires str` — joblib extends pickle; always load with `joblib.load()` |

Full post-mortems: [docs/PULSEGUARD_FAILURE_ARCHAEOLOGY.md](docs/PULSEGUARD_FAILURE_ARCHAEOLOGY.md)

---

## Decision Policy

```
PD < 0.20            →  GREEN  — low risk, proceed
0.20 ≤ PD < 0.40     →  AMBER  — refer for human review
PD ≥ 0.40            →  RED    — high risk, human escalation required
```

All outputs tagged: `ASSISTIVE_ONLY` · `HUMAN_REVIEW_REQUIRED` · `NOT_FINAL_DECISION`

**Hard rule:** The LLM/RAG governance layer drafts memos and checklists only. It never approves or rejects an applicant. Every numeric decision is made deterministically before any LLM is consulted.

---

## Quick Start

```bash
# Clone
git clone https://github.com/SidharthKriplani/pulseguard.git
cd pulseguard

# Install
pip install -r requirements.txt

# Run locally
uvicorn app:app --reload
# → http://localhost:8000/health
# → http://localhost:8000/docs

# Docker
docker build -t pulseguard .
docker run -p 8000:8000 pulseguard
```

---

## Key Evidence Artifacts

| Artifact | Proves |
|----------|--------|
| `docs/PULSEGUARD_GOLD_PASS2_TUNED_CHAMPION_REPORT.md` | LightGBM_monotonic champion selection + early stopping bug diagnosis |
| `docs/PULSEGUARD_GOLD_PASS3_GOVERNANCE_REPORT.md` | SHAP reason codes, RAG policy layer, LLM memo governance |
| `docs/PULSEGUARD_GOLD_CHECKPOINT.md` | Consolidated Gold Pass 1–4 pass/fail record |
| `docs/PULSEGUARD_MODEL_CARD.md` | AUC=0.7769 / ECE=0.0034 / KS=0.4141, intended use, limitations |
| `docs/G9A_FULL_MODERN_MODEL_TOURNAMENT.md` | 3-model tournament full results (baseline) |
| `docs/G8_GOVERNANCE_SIGNOFF_PACKET.md` | Model risk governance signoff — fairness, adverse action, monitoring |
| `docs/PULSEGUARD_FAILURE_ARCHAEOLOGY.md` | 8 real failures with root cause + fix |
| `06_CLAIM_BOUNDARY.md` | Truth boundary — champion vs. serving, safe vs. forbidden claims |
| `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.pdf` | 30+ Q&A pairs across all gates + serving gap (Sections 27D, 28) |

---

## Interview Defense

Full design rationale, architecture decisions, and 30+ expected interview Q&A pairs — covering every gate, the model tournament, the early stopping bug, the Bayes ceiling, the serving gap, temporal split strategy, and the "Failures I'm Proud Of" section:

**[docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.pdf](docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.pdf)**

Sections 27D and 28 cover the serving gap Q&A (for interviewers who test the live endpoint) and 8 failure post-mortems with interview framing.

---

## Truth Boundary

| Claim | Status |
|-------|--------|
| Champion model AUC=0.7769 (LightGBM_monotonic, Home Credit test set) | ✅ True |
| Live endpoint AUC=0.6261 (G4 XGBoost, synthetic 50k rows) | ✅ True — serving gap documented |
| Bayes ceiling efficiency 99.6% on G4 synthetic DGP | ✅ True — applies to synthetic lane only |
| SHAP reason codes at live endpoint | ✅ True |
| Platt calibration ECE=0.0034 on champion | ✅ True |
| 307,511 real Home Credit applicants in training pipeline | ✅ True |
| Gold Pass governance gates completed | ✅ True |
| Live endpoint AUC=0.7769 | ❌ False — endpoint serves G4 XGBoost (AUC=0.6261) |
| Champion model is deployed | ❌ False — sklearn 1.7.2 / Python 3.9 pkl lock-out |
| Production lending decisions | ❌ Not claimed — ASSISTIVE_ONLY |
| Regulatory compliance certification | ❌ Not claimed |
| Real bank validation | ❌ Not claimed |
| Temporal split by application date | ❌ Not implemented — SK_ID_CURR DR range=0.003 confirms no detectable time proxy |

**What this is:** Solo-built, non-production, interview-portfolio credit governance platform. Every numeric claim is backed by an executable script or evidence artifact. The serving gap between the champion and the live endpoint is documented in full.

---

## Resume-Safe Claim

Built PulseGuard, a production-simulated credit risk governance platform on Home Credit Default Risk (307,511 real applicants, 140 engineered features, 7 tables). Ran a 3-model Optuna tournament (LightGBM, CatBoost, XGBoost); diagnosed and fixed a LightGBM early-stopping interaction with `scale_pos_weight` that undertrained the baseline at 9 trees; crowned LightGBM_monotonic + Platt calibration as champion (AUC=0.7769, ECE=0.0034, KS=0.4141, PR-AUC=0.2628) with 15 directional monotone constraints. Demonstrated 99.6% Bayes ceiling efficiency on a synthetic 6-signal DGP. Implemented SHAP-grounded adverse action reason codes, GREEN/AMBER/RED decision banding, and a RAG + LLM governance memo layer (ASSISTIVE_ONLY). Deployed to GCP Cloud Run with a fully documented serving gap due to sklearn serialization version incompatibility. Documented 8 real failures with root cause and fix across a 9-gate Gold Pass governance structure.

---

## Part of Applied LLM Systems Portfolio

This project is part of a 13-repo portfolio targeting Applied LLM Systems Engineer, MLOps, and Technical AI PM roles.

**Applied Systems (LangGraph pipelines):**

| Project | Domain | Primary Failure Mode |
|---------|--------|----------------------|
| [LendFlow](https://github.com/SidharthKriplani/lendflow) | Financial underwriting | When to stop or escalate |
| [AgentReliabilityLab](https://github.com/SidharthKriplani/agentreliabilitylab) | Cyber threat triage | When to stop or escalate |
| [NexusSupply](https://github.com/SidharthKriplani/nexussupply) | Supplier risk intelligence | Conflicting signal fusion |

**Platforms & Auditors (domain-agnostic tooling):**

| Project | What It Audits / Builds |
|---------|------------------------|
| [InferenceLens](https://github.com/SidharthKriplani/inferencelens) | Inference cost/quality tradeoffs — Pareto frontier, routing rules |
| **PulseGuard** | Credit risk governance — champion/challenger, serving gap, 8 failure post-mortems |
| [RiskFrame](https://github.com/SidharthKriplani/riskframe_platform) | ML model lifecycle — champion/challenger, drift, fairness |
| [MetaSignal](https://github.com/SidharthKriplani/metasignal_platform) | A/B experiment validity — CUPED, guardrail-first, SRM |
| [DevPulse](https://github.com/SidharthKriplani/devpulse_platform) | Version-safe RAG — conflict detection, LLM-Last architecture |
| [PulseRank](https://github.com/SidharthKriplani/pulserank_platform) | Marketplace ranking — IPS debiasing, MMR diversity |
| [TrialCheck](https://github.com/SidharthKriplani/trialcheck_v0) | A/B readout audit — SRM, peeking, underpowered tests |
| [FeatureLeakageLens](https://github.com/SidharthKriplani/featureleakagelens_v0) | Pre-training leakage — target, temporal, overlap |
| [GoldenSetAuditor](https://github.com/SidharthKriplani/goldensetauditor_v0) | LLM/RAG eval dataset quality |
| [DocIngestQA](https://github.com/SidharthKriplani/docingestqa) | RAG document ingestion quality — 11 deterministic checks |
| [MetricLens](https://github.com/SidharthKriplani/metriclens) | Metric movement decomposition — mix shift vs rate shift |

---

## Author

**Sidharth Kriplani** · [linkedin.com/in/sidharth-kriplani](https://linkedin.com/in/sidharth-kriplani) · [github.com/SidharthKriplani](https://github.com/SidharthKriplani)
