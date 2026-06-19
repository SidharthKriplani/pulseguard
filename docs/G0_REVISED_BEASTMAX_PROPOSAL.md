# G0 — REVISED BEASTMAX PROPOSAL
## PulseGuard · Consolidated Flagship After First-Principles Research

---

## 1. FINAL PRODUCT IDENTITY

**PulseGuard is the model lifecycle governance platform for credit risk and fraud decisions.**

It answers the exact questions asked in SR 26-2, FAANG-tier risk DS interviews, and model risk committee reviews:
- Is the model's feature set valid before training? (leakage audit)
- Is the model calibrated at the decision threshold? (ECE + Platt calibration)
- Is the champion the best candidate available? (5-gate promotion framework)
- Is the model's performance degrading? (PSI drift + KS alerting)
- Are decisions fair to protected groups? (DI + EOpp + SHAP proxy rank)
- Are credit decisions made by enforceable policy? (FOIR engine + hard rule gate + policy version log)
- Can the full lifecycle be audited? (evidence ledger + model card + governance sign-off)
- What should happen to the model now? (APPROVE / MONITOR / CHALLENGE / RETIRE)

**One-sentence pitch:** PulseGuard is a production-simulated, evidence-bound platform that makes every step of a credit risk model's lifecycle — from feature validation through governance sign-off — traceable, defensible, and aligned with SR 26-2 model risk management standards.

---

## 2. NORTH-STAR DECISION

**The governance decision:** After running the full PulseGuard lifecycle, the output is a governance sign-off with a concrete recommendation:

```
GOVERNANCE DECISION: APPROVE WITH ENHANCED MONITORING
────────────────────────────────────────────────────────
Model:    XGBoost Champion v1.0 (deployed)
Date:     [date]
Basis:
  ✓ Leakage audit: 3 WARNs, 0 FAILs — no training blocked
  ✓ Calibration: ECE 0.0046 — well-calibrated at decision threshold
  ✓ Challenger gate: LightGBM held (Gate 1 FAIL; DeLong p=0.07)
  ✓ Optuna HPO: xgb_v2 held (ECE regression 5x)
  ✓ Drift: Day 7 WARN, Day 14 ALERT — alert fires correctly
  ⚠ Drift: Day 14 PSI 0.2358 ALERT — enhanced monitoring required
  ✓ Fairness: DI 1.059 (PASS), EOpp 2.8pp (PASS)
  ⚠ Reject inference: not implemented — known boundary
Authorized by: [governance sign-off]
Next review trigger: PSI > 0.20 for 2 consecutive batches
────────────────────────────────────────────────────────
```

This governance document is the final product. Everything else — training, calibration, drift, fairness, challenger — is infrastructure that produces the evidence for this decision.

---

## 3. MODULE HIERARCHY

```
PulseGuard
├── G0 — Gold Template Alignment (this gate — planning only)
├── G1 — Repo Audit and Artifact Inventory
├── G2 — Decision Workflow and Data Contracts
│
├── [MODULE: PRE-TRAINING GATE]
│   ├── G3 — FeatureLeakageLens integration (7 checks)
│   └── G3+ — Synthetic timestamp extension for Home Credit
│
├── [MODULE: TRAINING AND CALIBRATION]
│   ├── G4 — Champion training (XGBoost + Platt + ECE)
│   └── G4 — Drift monitor (PSI + KS, 30-day lifecycle)
│
├── [MODULE: FAIRNESS LAYER]
│   └── G5 — Disparate Impact + EOpp + SHAP proxy rank
│
├── [MODULE: CHAMPION/CHALLENGER ENGINE]
│   └── G6 — 5-gate promotion + Optuna HPO + ECE regression case
│
├── [MODULE: CREDIT DECISION SIMULATION]
│   ├── G7 — FOIR engine (deterministic)
│   ├── G7 — Hard rule gate (policy_gate.py)
│   ├── G7 — Decision router (APPROVE/REVIEW/REJECT)
│   └── G7 — Policy version log
│
├── [MODULE: GOVERNANCE EVIDENCE]
│   ├── G8 — Evidence ledger (15+ artifacts)
│   ├── G8 — Model card
│   └── G8 — Governance sign-off document
│
└── [MODULE: DEEP DEFENSE / GOLD]
    ├── G9 — Interview defense document (30+ Q&A)
    ├── G9 — Delayed label validation
    ├── G9 — Reject inference: SAIL (graph-based semi-supervised label spreading, 2025 paper) + boundary quantification
    ├── G9 — Calibration by group
    ├── G9 — Group leakage check (entity contamination)
    ├── G9 — FastAPI serving with parity test
    └── G10 — Final audit + one-pager
```

---

## 4. WHICH COMPONENTS BECOME CORE MODULES

| Module | Source | Status |
|--------|--------|--------|
| Pre-training leakage gate | FeatureLeakageLens (pip install) | CORE — G3 |
| Champion training + calibration | RiskFrame (port + refactor) | CORE — G4 |
| Drift monitor (PSI + KS) | RiskFrame (port + refactor) | CORE — G4 |
| Drift percentile monitor | New (G4 enhancement) | CORE — G4 |
| Subpopulation PSI slice | New (G4 enhancement) | CORE — G4 |
| Decision-layer monitoring | G7 approval_rate_decomposition | CORE — G7 |
| Fairness audit (DI + EOpp + SHAP) | RiskFrame (port + refactor) | CORE — G5 |
| Champion/challenger 5-gate | RiskFrame (port + refactor) | CORE — G6 |
| Optuna HPO + ECE regression case | RiskFrame (port + refactor) | CORE — G6 |
| FOIR engine | LendFlow (extract, simplify) | CORE — G7 |
| Hard rule gate | LendFlow (extract, simplify) | CORE — G7 |
| Decision router | LendFlow (extract, generalize) | CORE — G7 |
| Policy version log | RiskFrame (from `policy_change_log.json`) | CORE — G7 |
| Audit trail (JSONL) | LendFlow pattern | CORE — G7 |
| Evidence ledger | New (PulseGuard original) | CORE — G8 |
| Model card | RiskFrame pattern + G0 enrichment | CORE — G8 |
| Governance sign-off | New (PulseGuard original) | CORE — G8 |

---

## 5. WHICH COMPONENTS BECOME EVIDENCE DONORS ONLY

| Component | What It Contributes | What Is Not Ported |
|-----------|--------------------|--------------------|
| NexusSupply | Composite risk fusion formula (as a design pattern in G0 docs) | Full pipeline, FinBERT, ESG, graph |
| LendFlow RAG | Hybrid RAG pattern documented in G0_TECHNIQUE_TOURNAMENT; not built until G7+ | Full LangGraph, Presidio |
| LendFlow evaluation | 95% routing accuracy framing (corrected: needs 50+ applications to claim statistical meaning) | Not ported as-is |

---

## 6. WHAT IS REMOVED

| Component | Source | Reason for Removal |
|-----------|--------|-------------------|
| LangGraph wiring | LendFlow + NexusSupply | Adds complexity; not needed for decision pipeline |
| FinBERT news sentiment | NexusSupply | Not aligned with credit/fraud risk DS role |
| ESG parsing | NexusSupply | Not relevant to PulseGuard buyer |
| Supplier/procurement domain | NexusSupply | Wrong domain for target role |
| NBFC/vehicle loan vertical framing | LendFlow | Replace with generalized credit workflow |
| Presidio PII | LendFlow | Not needed for synthetic data; document as production requirement |
| NexusSupply evaluation metrics (CV AUC 1.00) | NexusSupply | Circular evaluation; not a valid claim |
| Streamlit dashboard | NexusSupply | Deferred to G9+ |

---

## 7. NEW MODULES THAT MUST BE BUILT TO REACH BEASTMAX

These do not exist in any source project and must be built from scratch:

| New Module | Why Needed | Gate |
|-----------|-----------|------|
| Reject inference documentation + boundary quantification | Almost no portfolio project has it; required for senior credit DS roles; SAIL (graph-based, 2025) is the G9 implementation path | G8/G9 |
| Group leakage check (entity contamination) | Not in FLL; important for cross-fold contamination | G3+/G9 |
| Synthetic timestamp extension for Home Credit | Makes temporal FLL checks fire; required to demonstrate the FAIL path | G3 |
| Calibration by group (DI on calibration curves) | Fairness depth beyond DI; shows calibration doesn't just hold globally | G9 |
| Delayed label validation script | Simulates the 6-12 month label delay reality; strong evidence artifact | G8 |
| Governance sign-off document | The final product of the governance lifecycle; connects all artifacts | G8 |
| SR 26-2 alignment note in model card | Connect every artifact to the revised regulatory standard | G8 |
| Approval rate decomposition (model vs. policy) | Separates the effect of model drift from policy change on approval rate | G7/G8 |

---

## 8. T3/GOLD TECHNICAL DEPTH STILL MISSING

After G1-G8, PulseGuard is strong but not gold. The following add depth that distinguishes a gold project from a good one:

| Gap | Why It Matters | Difficulty |
|-----|---------------|-----------|
| Reject inference (even partial) | Staff-level credit DS must know this | Medium |
| Isotonic recalibration (periodic) | Research-backed improvement for credit time series | Medium |
| Calibration by group | Shows fairness depth | Low |
| Group leakage check | Closes FLL gap | Low |
| Hybrid RAG for policy lookup | LendFlow's strongest unique contribution; RAGAS faithfulness | High |
| Approval rate decomposition module | Policy-model decoupling in code, not just docs | Medium |
| FastAPI serving with parity test | Production pattern; parity_check.py | Low |
| Interview defense document (30+ Q&A) | Required for any senior interview | Medium |
| The "what I would do differently in production" section | Shows self-awareness; rare in portfolios | Low |

---

## 9. MINIMUM BUILD PATH (G3–G8, ~3 weeks)

```
Week 1: G3 + G4
  - pip install featureleakagelens; run on Home Credit; produce leakage_report.json
  - Add synthetic timestamps for temporal checks to fire
  - Train XGBoost champion; Platt calibration; ECE 0.0046
  - 30-day lifecycle simulation; PSI computation

Week 2: G5 + G6
  - Fairness audit: DI + EOpp + SHAP beeswarm
  - LightGBM challenger training; 5-gate evaluation; DeLong test
  - Optuna HPO 50 trials; ECE regression case documented

Week 3: G7 + G8
  - FOIR engine (pure Python)
  - Hard rule gate (6 rules)
  - Decision router + policy version log
  - 50 synthetic applications scored end-to-end
  - Evidence ledger: 15+ entries
  - Model card + governance sign-off
```

At the end of the minimum build path, PulseGuard has 15+ artifacts and can answer the flagship question.

---

## 10. HIGH-CEILING BUILD PATH (G9–G10, +2 weeks)

```
Week 4: G9
  - Reject inference documentation + boundary quantification
  - Calibration by group
  - Group leakage check
  - FastAPI serving + parity test
  - Delayed label validation
  - Interview defense document (30+ Q&A)

Week 5: G10
  - Isotonic recalibration module
  - Hybrid RAG policy lookup (BM25 + ChromaDB + cross-encoder)
  - RAGAS evaluation on 50 synthetic applications
  - Full audit: all gates closed; all artifacts verified
  - Portfolio one-pager
  - Final governance sign-off document
```

---

## 11. FINAL INTERVIEW STORY

The interview story has three acts:

**Act 1 — The Problem (30 seconds):**
"Risk models fail not because they have bad AUC — they fail because of silent drift, miscalibrated probabilities, features that leak future information, and decisions that cannot be traced to a policy version. PulseGuard is built to prevent every one of those failure modes."

**Act 2 — The Build (2-3 minutes):**
"I start with a feature leakage audit before any model is trained. I train a calibrated XGBoost champion — the critical result is that Optuna HPO found a model with better AUC that I held because ECE regressed 5x — that governance judgment is the most important artifact in the platform. I run a 30-day simulated lifecycle with synthetic drift injection at Day 14, PSI 0.2358 alert fires correctly. I measure fairness at the decision output level — not the feature list — with DI 1.059 and SHAP rank confirming gender is not a primary driver. The FOIR engine enforces hard rules before any model call. Every decision produces a versioned policy log and an audit record. The final output is a governance sign-off document that connects all 15+ evidence artifacts."

**Act 3 — The Limits (30 seconds):**
"What I did not implement, and why: reject inference — because credit models only see approved applicants, there's selection bias I documented but didn't solve in the portfolio version. Full hybrid RAG policy lookup is deferred. What I would do differently in production: use Evidently AI for monitoring, MLflow for experiment tracking, a feature store with point-in-time correctness. The portfolio uses custom implementations to demonstrate I understand the underlying mechanics."

This three-act story is coherent, honest, and impossible to attack with a simple follow-up question.

---

## 12. INDUSTRY VALIDATION (added after GitHub/blog research)

PulseGuard's architecture is independently validated by production engineering decisions at Nubank and Stripe:

| PulseGuard Design Choice | Industry Validation |
|--------------------------|---------------------|
| PSI drift monitoring with WARN/ALERT thresholds | Standard in all credit risk MLOps portfolios (JakobLS, DataRobot) |
| Decision-layer monitoring (approval rate decomposition) | Nubank Engineering Blog explicitly identifies this as separate from model-technical monitoring — "Policy/Decision Layer monitoring" |
| Aggregate PSI documented as having a multivariate blindspot | Stripe (Jan 2025): aggregate metrics "obscure degradations affecting specific segments of traffic" — confirmed at production scale across 16,000+ payment dimensions |
| Percentile feature monitoring alongside PSI | Nubank: "Monitor the 99th, 95th, 90th and 10th, 5th, 1st percentiles" — explicitly recommended over average-based monitoring |
| Champion/challenger with automated gates | DataRobot explicitly sells this to banks; shadow mode → promotion is the documented production pattern |
| Train/serve skew monitoring (G9 deferred) | Nubank explicitly documents this as a mandatory concern for real-time models |
| Reject inference as documented boundary condition | SAIL framework (Annals of Operations Research, 2025) confirms this is an active research problem — not a solved one |
| Governance sign-off document | SR 26-2 explicitly requires the governed lifecycle chain to produce evidence at every handoff; governance sign-off is the evidence of evidence |

**Interview-safe framing:**
> "PulseGuard's monitoring design separates technical drift monitoring (PSI/KS) from decision-layer monitoring (approval rate attribution). This mirrors how Nubank structures their production monitoring — they explicitly call out that technical metrics don't tell business stakeholders how decisions are being impacted. Stripe's 2025 blog on slice monitoring confirmed at production scale that aggregate drift metrics miss segment-level degradation — which is exactly what PulseGuard's PSI multivariate blindspot warning documents."
