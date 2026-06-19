# G1 — REPO AUDIT AND ARTIFACT INVENTORY
## PulseGuard · Source Asset Classification

**Gate:** G1 — Repo Audit and Artifact Inventory
**Status:** COMPLETE
**Date:** June 2026

**Auditor stance:** Every asset from every source project is classified. "COPY" means bring in almost as-is. "ADAPT" means port with modifications. "BUILD" means write from scratch. "EXCLUDE" means do not use. "DEFER" means correct decision but not G1–G8 scope.

> **Important:** Source repos (`riskframe_platform`, `featureleakagelens`, `lendflow`, `nexussupply`) are separate GitHub repositories and are NOT present in the PulseGuard workspace filesystem. This audit is based on the G0_COMPONENT_PROJECT_DEEP_AUDIT.md analysis. When building each gate, the relevant source files should be referenced from their GitHub repos for implementation guidance — they are not imported or called directly.
>
> Exception: `featureleakagelens` is a PyPI library (`pip install featureleakagelens`) and is used via import, not via source-file copy.

---

## PART 1: RISKFRAME_PLATFORM

**Source:** `SidharthKriplani/riskframe_platform` (GitHub)
**Role in PulseGuard:** Primary backbone — champion training, calibration, PSI drift, fairness, champion/challenger engine
**Overall verdict:** Strongest source project. Port everything listed below. Fix the documented gaps.

### Scripts / Core Computation

| Asset | Description | Classification | PulseGuard Target | Gate |
|-------|-------------|---------------|-------------------|------|
| `train_champion.py` | XGBoost training, 60/20/20 split, Platt calibration, ECE computation | ADAPT | `scripts/train_champion.py` | G4 |
| `train_challenger.py` | LightGBM training, same split, Platt calibration | ADAPT | `scripts/train_challenger.py` | G6 |
| `optuna_hpo.py` | 50-trial TPE Bayesian search; ECE regression case documentation | ADAPT | `scripts/optuna_hpo.py` | G6 |
| `champion_challenger_compare.py` | 8-metric head-to-head; 5-gate promotion logic; DeLong test | ADAPT | `scripts/champion_challenger_compare.py` | G6 |
| `drift_monitor.py` | PSI + KS per feature across 30 batches; Day 7 WARN / Day 14 ALERT | ADAPT | `scripts/drift_monitor.py` | G4 |
| `seed_lifecycle.py` | 30-day synthetic batch generator with controlled drift injection | ADAPT | `scripts/seed_lifecycle.py` | G4 |
| `fairness_audit.py` | Disparate Impact ratio, EOpp gap by group | ADAPT | `scripts/fairness_audit.py` | G5 |
| `shap_proxy_rank.py` | SHAP TreeExplainer; mean |SHAP| rank per feature | ADAPT | `scripts/shap_proxy_rank.py` | G5 |
| `parity_check.py` | Asserts batch scorer == API scorer within 1e-6 | DEFER | `scripts/parity_check.py` | G9 (FastAPI) |
| `delayed_label_validate.py` | Synthetic 12-month outcome labels; bad rate per decile vs. predicted | ADAPT | `scripts/delayed_label_validate.py` | G8 |
| `drift_fire_test.py` | Asserts PSI > 0.20 on Day 14 injected population | ADAPT | `tests/test_drift_fires.py` | G4 |

**Key gap to fix in PulseGuard vs. RiskFrame:**
- Reject inference: not documented in RiskFrame; must be added as Known Boundary Condition in model card (G8)
- DI computation: must verify DI is computed on all scored applicants, not only approved ones (G5)
- Calibration at decision boundary: ECE is global; need calibration curve plotted specifically at the 0.06 / 0.28 threshold points

### Modules / Source Libraries

| Asset | Description | Classification | PulseGuard Target | Gate |
|-------|-------------|---------------|-------------------|------|
| `ABTBuilder` class | Home Credit feature pipeline (assembles application base table) | ADAPT | `src/feature_pipeline.py` | G3/G4 |
| Policy engine logic | Threshold-based routing (score < 0.06 → APPROVE, 0.06–0.28 → REVIEW, ≥ 0.28 → REJECT) | ADAPT | `src/decision_router.py` | G7 |
| Policy change log schema | JSON log: version, timestamp, threshold_delta, rationale, authorized_by | COPY | `src/policy_change_log.py` | G7 |
| Evidence artifact JSON schemas | calibration_report.json, drift_report.json, fairness_report.json schemas | COPY | `outputs/evidence/*.json` | G4–G8 |
| FastAPI serving app | `/predict` endpoint; batch vs. single inference; health check | DEFER | `src/api.py` | G9 |
| Docker compose | Full containerized environment | DEFER | `docker-compose.yml` | G9 |
| Test suite structure (22/22) | pytest framework; fixture pattern; assert style | ADAPT | `tests/` | G4+ |

### Evidence Artifacts (Source-Reference — NOT PulseGuard-built)

These numbers are recorded in `04_EVIDENCE_LEDGER.md` (SOURCE_REFERENCE section). They set expected output ranges for PulseGuard gate results — not claims.

- Champion ROC AUC: ~0.7663 | PR AUC: ~0.2611 | ECE: ~0.0046
- Optuna xgb_v2 PR AUC: ~0.2654 | ECE: ~0.0243 (HELD — 5x regression)
- PSI Day 14: ~0.2358 (ALERT) | EXT_SOURCE_2 shift: −0.18
- DI: ~1.059 (PASS) | EOpp gap: ~2.8pp (PASS) | CODE_GENDER_F SHAP rank: #10
- DeLong test p-value: ~0.07 (not significant) | Gate 1 delta: ~0.0002 (below threshold)

---

## PART 2: FEATURELEAKAGELENS

**Source:** PyPI — `pip install featureleakagelens` (published package)
**Role in PulseGuard:** Pre-training gate — runs 7 leakage checks before any model is trained
**Overall verdict:** Strong PyPI library. Import directly; don't rebuild. Fix the temporal check gap.

### Library Modules

| Asset | Description | Classification | PulseGuard Usage | Gate |
|-------|-------------|---------------|-----------------|------|
| `LeakageAuditConfig` | Main API: pass features, targets, config → run all 7 checks | COPY (import) | `scripts/leakage_audit.py` calls this | G3 |
| Check 1: Name heuristic | Flags features with suspicious names (target, label, default, bad_flag) | COPY (import) | Part of LeakageAuditConfig | G3 |
| Check 2: ID / proxy | Flags near-unique columns that may proxy an ID | COPY (import) | Part of LeakageAuditConfig | G3 |
| Check 3: Target correlation | Flags features with Pearson correlation > threshold against target | COPY (import) | Part of LeakageAuditConfig | G3 |
| Check 4: Categorical proxy | Chi-squared test for target-correlated categoricals | COPY (import) | Part of LeakageAuditConfig | G3 |
| Check 5: Split distribution | Flags if train/val splits differ significantly in feature distribution | COPY (import) | Part of LeakageAuditConfig; may produce INSUFFICIENT_INPUT without split_col | G3 |
| Check 6: Temporal availability (FAIL-level) | Flags features whose timestamp > outcome timestamp | COPY (import) | Requires synthetic timestamps — see G3 gap below | G3 |
| Check 7: Training future date scan (FAIL-level) | Flags training examples with future-dated features | COPY (import) | Requires synthetic timestamps — see G3 gap below | G3 |
| JSON/Markdown/HTML output | Structured leakage report in 3 formats | COPY (import) | `outputs/evidence/leakage_report.{json,md,html}` | G3 |
| 23 tests | pytest suite for all 7 checks | REFERENCE (don't copy; use FLL's test suite as validation spec) | — | G3 |

### Known Gaps to Address in PulseGuard (G3)

| Gap | Problem | Fix |
|-----|---------|-----|
| Temporal checks require timestamps | Home Credit has no feature-level timestamps; Checks 6 and 7 cannot fire natively | `scripts/add_synthetic_timestamps.py` — adds synthetic timestamp columns to demonstrate the FAIL path; clearly labeled as synthetic |
| Split distribution check fires INSUFFICIENT_INPUT | Without a `split_col` parameter, the check cannot run | Either add a synthetic split column or document INSUFFICIENT_INPUT result as expected behavior |
| Group leakage check (entity contamination) missing | SK_ID_CURR contamination across folds not checked in FLL | BUILD at G3 as `scripts/group_leakage_check.py`; document as FLL roadmap gap filled by PulseGuard |

---

## PART 3: LENDFLOW

**Source:** `SidharthKriplani/lendflow` (GitHub)
**Role in PulseGuard:** Credit decision simulation layer — FOIR engine, hard rule gate, decision router, audit trail
**Overall verdict:** Extract the decision logic (FOIR + hard rules + routing). Drop the LangGraph wrapper entirely.

### Extract and Port (ADAPT)

| Asset | Description | Classification | PulseGuard Target | Gate |
|-------|-------------|---------------|-------------------|------|
| FOIR engine | `(all_EMIs + proposed_EMI) / net_income`; never trusts application-provided value | ADAPT | `src/foir_engine.py` | G7 |
| Hard rule gate | 6 rules: LTV cap, income floor, FOIR threshold (> 0.65 → REJECT), age limits, blacklisted zone, loan amount cap | ADAPT | `src/policy_gate.py` | G7 |
| APPROVE / REVIEW / REJECT routing | Routes to APPROVE (below threshold), REVIEW (human queue), REJECT, HARD_REJECT | ADAPT | `src/decision_router.py` | G7 |
| Tamper-evident JSONL audit trail | Every decision produces a JSONL record with decision, reason codes, timestamp, version | ADAPT | `src/audit_logger.py` | G7 |
| Adverse action reason code pattern | Maps REJECT decisions to top-3 SHAP factors as illustrative reason codes | ADAPT | `src/adverse_action_codes.py` | G7 |
| Policy version log schema | JSON: version, timestamp, threshold_delta, rationale, authorized_by | ADAPT | `src/policy_change_log.py` (shared with RiskFrame pattern) | G7 |

### Reference Only (Don't Port)

| Asset | Why |
|-------|-----|
| LangGraph 7-node wiring | Unnecessary complexity for a deterministic sequential pipeline; REJECTED |
| Presidio PII redaction | Not needed for synthetic data; document as production requirement |
| NBFC/vehicle loan domain framing | Too narrow; generalize to credit underwriting workflow |
| Hybrid RAG (BM25 + ChromaDB + cross-encoder) | Deferred to G7+ / Gold; MVP uses hardcoded thresholds |
| RAGAS evaluation framework | Deferred with RAG; re-evaluate in G7 Gold build |
| 20-application evaluation (95% routing accuracy) | Statistically meaningless; PulseGuard will run on 50+ applications |

### What PulseGuard Adds That LendFlow Doesn't Have

| New Capability | Why Needed |
|---------------|-----------|
| Approval rate decomposition script | Separates model drift signal from policy version signal in approval rate |
| Model-score integration in routing | LendFlow uses rule-based routing only; PulseGuard routes uses calibrated XGBoost score |
| Champion/challenger shadow scoring in decision pipeline | LendFlow has no shadow model capability |

---

## PART 4: NEXUSSUPPLY

**Source:** `SidharthKriplani/nexussupply` (GitHub)
**Role in PulseGuard:** Evidence donor only — composite formula pattern and Altman Z variant selection
**Overall verdict:** Selective absorb: formula pattern only. Full pipeline excluded. AUC 1.00 is permanently forbidden.

### Selective Absorb (REFERENCE — document as pattern, don't port code)

| Asset | Description | Classification | PulseGuard Usage |
|-------|-------------|---------------|-----------------|
| Composite multi-signal risk scoring formula | `composite = 0.40×financial_risk + 0.25×sentiment_risk + 0.20×esg_risk + 0.15×contagion_risk` | REFERENCE | Document as multi-signal fusion design pattern in G9 architecture docs; not built G1–G8 |
| Altman Z-score 3-variant selection logic | Auto-selects public/private/non-manufacturing Altman Z variant by industry | REFERENCE | Cite as reference in G9 financial health signal module; not built G1–G8 |
| XGBoost distillation from rule-based scores | Pattern for distilling interpretable rule-based signals into ML model | REFERENCE | General ML pattern; not NexusSupply-specific |

### Exclude Entirely

| Asset | Why Excluded |
|-------|-------------|
| LangGraph 7-node wiring | REJECTED — same reason as LendFlow |
| FinBERT news sentiment on 20 synthetic headlines | Circular evaluation; sentiment calibrated to match the label it was designed to predict |
| ESG parsing via LLM on synthetic summaries | Same circularity; LLM evaluated on LLM-generated data |
| Graph contagion (BFS + decay) | Domain mismatch; supplier/procurement framing not relevant to credit/fraud buyer |
| Full supply chain risk pipeline | Wrong domain entirely |
| CV AUC 1.00 evaluation result | PERMANENTLY FORBIDDEN — circular evaluation; labels derived from features on synthetic data |

---

## PART 5: NEW MODULES — BUILD FROM SCRATCH

These do not exist in any source project. PulseGuard must build them.

| New Module | Why Needed | Source File | Gate |
|-----------|-----------|-------------|------|
| `scripts/leakage_audit.py` | Orchestrates FLL LeakageAuditConfig on Home Credit; writes structured report | BUILD | G3 |
| `scripts/add_synthetic_timestamps.py` | Adds synthetic timestamp columns to Home Credit to enable temporal checks | BUILD | G3 |
| `scripts/group_leakage_check.py` | Entity contamination check (SK_ID_CURR fold contamination) — fills FLL gap | BUILD | G3 |
| `scripts/approval_rate_decomposition.py` | Attributes approval rate change to model drift vs. policy version | BUILD | G7 |
| `src/adverse_action_codes.py` | Maps REJECT decisions to top-3 SHAP factors as illustrative ECOA reason codes | BUILD | G7 |
| `docs/MODEL_CARD.md` | Full model card with SR 26-2 alignment, reject inference boundary, retraining trigger | BUILD | G8 |
| `docs/governance_signoff.md` | Governance decision document linking all 15+ evidence artifacts | BUILD | G8 |
| `scripts/delayed_label_validate.py` | Synthetic delayed label validation; bad rate by decile vs. predicted | BUILD | G8 |

---

## PART 6: ASSET SUMMARY

### Count by Classification

| Classification | Count | Notes |
|---------------|-------|-------|
| COPY (import or use as-is) | 9 | All from FeatureLeakageLens via pip |
| ADAPT (port with modifications) | 18 | Primarily from RiskFrame and LendFlow |
| BUILD (from scratch) | 8 | New PulseGuard-original modules |
| DEFER (correct direction, not G1–G8) | 5 | FastAPI, Docker, advanced fairness, RAG, graph |
| EXCLUDE (don't use) | 7 | LangGraph, LendFlow domain, NexusSupply pipeline, NexusSupply AUC |
| REFERENCE (pattern only, no code port) | 3 | NexusSupply formula, Altman Z selection, distillation pattern |

### Build Order (Dependency-Ordered)

```
G3: leakage_audit.py → add_synthetic_timestamps.py → group_leakage_check.py
G4: feature_pipeline.py → train_champion.py → seed_lifecycle.py → drift_monitor.py
G5: fairness_audit.py → shap_proxy_rank.py
G6: train_challenger.py → optuna_hpo.py → champion_challenger_compare.py
G7: foir_engine.py → policy_gate.py → decision_router.py → audit_logger.py → adverse_action_codes.py → policy_change_log.py → approval_rate_decomposition.py
G8: delayed_label_validate.py → MODEL_CARD.md → governance_signoff.md
```

---

## PART 7: ENVIRONMENT STATUS

| Dependency | Required At | Install Status (as of G1) |
|-----------|------------|--------------------------|
| pandas | G3+ | ✓ INSTALLED (2.3.3) |
| numpy | G3+ | ✓ INSTALLED (2.2.6) |
| xgboost | G4+ | ✗ NEEDS INSTALL |
| lightgbm | G6+ | ✗ NEEDS INSTALL |
| scikit-learn | G4+ | ✗ NEEDS INSTALL |
| scipy | G4+ | ✗ NEEDS INSTALL |
| shap | G5+ | ✗ NEEDS INSTALL |
| optuna | G6+ | ✗ NEEDS INSTALL |
| featureleakagelens | G3+ | ✗ NEEDS INSTALL |

**Action required before G3:** Run `pip install xgboost lightgbm scikit-learn scipy shap optuna featureleakagelens --break-system-packages` and verify via `scripts/verify_imports.py`.

---

## PART 8: G1 COMPLETION CHECKLIST

- [x] All source project assets classified (COPY / ADAPT / BUILD / EXCLUDE / DEFER / REFERENCE)
- [x] Source repos confirmed as not present in PulseGuard workspace (GitHub repos; not cloned)
- [x] FeatureLeakageLens confirmed as PyPI-installable
- [x] All 8 new BUILD modules identified with source file names and gates
- [x] All 5 DEFER items named with gate
- [x] All 7 EXCLUDE items named with rationale
- [x] NexusSupply AUC 1.00 confirmed EXCLUDED / FORBIDDEN
- [x] LangGraph confirmed EXCLUDED from both LendFlow and NexusSupply
- [x] Environment dependency status recorded
- [x] Build order documented (dependency-ordered)

**Evidence Ledger Entry #1 status:** READY TO WRITE — G1 audit artifact exists at `docs/G1_repo_audit.md`.
