# 05 — CLAUDE KICKOFF PROMPT
## PulseGuard · Continuation Prompt for Fresh Claude Session

---

### How to Use This File

Copy the prompt below into a new Claude conversation when resuming this project. This gives the new Claude instance full context without re-reading all control documents. Append the current gate status and any decisions made since last session.

---

### Kickoff Prompt

```
You are continuing the BeastMax build for PulseGuard — a risk-decision and model-governance platform.

## Project Location
Workspace folder: pulseguard/
All control documents are in the root. Code goes in src/, scripts/, notebooks/. Artifacts go in outputs/evidence/ and outputs/plots/.

## What This Is
PulseGuard merges three GitHub projects (RiskFrame, FeatureLeakageLens, LendFlow) into a single auditable risk-decision system. It should answer:
"Can a bank, fintech, risk, or ML governance team decide whether a model is safe to use, whether its features are valid, whether its performance is drifting, whether decisions are fair, and whether the model should be approved, challenged, escalated, or retired?"

## Source Projects (already audited)
- riskframe_platform: champion/challenger (XGBoost vs LightGBM), Optuna HPO, Platt calibration, PSI drift, fairness audit, APPROVE/REVIEW/REJECT policy engine, 30-day lifecycle, FastAPI serving. Home Credit Default Risk dataset. ECE 0.0046, ROC AUC 0.7663, PSI Day14 0.2358 ALERT, DI 1.059 PASS.
- featureleakagelens: PyPI library, 7 leakage checks (2 FAIL-level: temporal availability + training future date scan), JSON/Markdown/HTML output.
- lendflow: LangGraph-based vehicle loan underwriting. FOIR recomputed deterministically; hard rules (FOIR, LTV, income floor, blacklist) enforce before model call; hybrid RAG (BM25 + ChromaDB + cross-encoder) over credit policy corpus; RAGAS faithfulness 0.91; APPROVE/REFER/REJECT routing.
- nexussupply: SELECTIVE ABSORB ONLY. Composite multi-signal fusion formula and Altman Z 3-variant logic are reusable. Full supplier pipeline, FinBERT, ESG, LangGraph are deferred.

## Control Documents (already written — read before coding)
- 00_CONTROL_TOWER.md — identity, what survives, forbidden claims
- 01_BEASTMAX_PRD.md — PRD, decision workflow, success criteria
- 02_PROJECT_MIX_MAP.md — full component mapping table
- 03_BUILD_GATES.md — G1–G10 with objectives, artifacts, stop conditions
- 04_EVIDENCE_LEDGER.md — 15-row ledger (all DEFERRED until gates close)
- 06_CLAIM_BOUNDARY.md — what can be claimed where

## Current Gate Status
[UPDATE THIS BEFORE PASTING THE PROMPT]
- G1 (Repo Audit): [OPEN / CLOSED]
- G2 (PRD and Component Map): [OPEN / CLOSED]
- G3 (Leakage Kernel): [OPEN / CLOSED]
- G4 (Drift Monitor): [OPEN / CLOSED]
- G5 (Fairness Layer): [OPEN / CLOSED]
- G6 (Champion/Challenger): [OPEN / CLOSED]
- G7 (Credit Decision Sim): [OPEN / CLOSED]
- G8 (Governance Ledger): [OPEN / CLOSED]
- G9 (Deep Defense): [OPEN / CLOSED]
- G10 (Final Audit): [OPEN / CLOSED]

## Task for This Session
[FILL IN: e.g., "Close G3 — run FeatureLeakageLens on Home Credit features and produce leakage_report.json"]

## Hard Rules for This Session
1. Read 03_BUILD_GATES.md before starting the target gate. Follow the artifact list exactly.
2. Do not claim a gate is closed until all artifacts exist and all success criteria are met.
3. Do not fabricate metrics. If a computation fails, document the failure, not a placeholder number.
4. After producing each artifact, write its evidence ledger entry in 04_EVIDENCE_LEDGER.md immediately.
5. Do not skip to a later gate — close gates in order.
6. Forbidden claims: production deployment, real customer data, regulatory certification, real loan decisions.
7. Every claim must be tagged: built / simulated / proposed / deferred.

## Dataset
Home Credit Default Risk (public, Kaggle). Files: application_train.csv, bureau.csv, bureau_balance.csv, previous_application.csv, installments_payments.csv, credit_card_balance.csv, POS_CASH_balance.csv.

If dataset files are not present in the workspace, create a synthetic equivalent using numpy/pandas that replicates the column schema and statistical properties needed for the gate. Document it as "synthetic dataset, Home Credit schema."

## Style Guide
- Python 3.10+
- One script per module (not monolithic)
- Every script is runnable standalone: `python scripts/module_name.py`
- Evidence artifacts are JSON (machine-readable) + Markdown (human-readable) at minimum
- All outputs go to outputs/evidence/ or outputs/plots/
- No hardcoded absolute paths — use relative paths from project root
- Comments explain business consequence, not just code action

## What NOT to Build (deferred)
- Full LangGraph wiring (from LendFlow)
- FinBERT news sentiment (from NexusSupply)
- ESG parsing (from NexusSupply)
- Presidio PII redaction (not needed for synthetic data)
- Streamlit dashboard (deferred to G9+)
- Graph contagion layer (deferred to G9+)

Start by reading the target gate in 03_BUILD_GATES.md, confirming the artifact list, then proceed.
```

---

### Session Log (append after each session)

| Date | Gate Worked | Artifacts Created | Issues Encountered | Next Action |
|------|-------------|------------------|-------------------|-------------|
| [setup] | Base control docs | 00–06 .md files, folder scaffold | None | Start G1 |

