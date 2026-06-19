# 03 — BUILD GATES
## PulseGuard · BeastMax Ordered Build Plan

---

### Gate Progression Philosophy

Each gate must be fully closed before the next opens. Every gate has a hard stop condition — if it fires, work stops, the issue is logged in the evidence ledger, and the gate is reopened. No gate is skipped. No claim is made for work not yet done.

---

## G1 — Repo Audit and Artifact Inventory

**Objective:** Map every existing asset from RiskFrame, FeatureLeakageLens, and LendFlow into PulseGuard's module structure. Identify what is reusable, what needs adaptation, and what needs to be built from scratch.

**Files / Artifacts to Create:**
- `docs/G1_repo_audit.md` — full inventory table (file, module, reuse status: COPY / ADAPT / BUILD)
- `docs/G1_dataset_plan.md` — confirm Home Credit dataset usage, synthetic data plan, no real data
- `scripts/verify_imports.py` — test that key dependencies (xgboost, lightgbm, shap, optuna, scipy) import correctly in the PulseGuard environment

**Success Criteria:**
- Every key file from source repos is classified (COPY / ADAPT / BUILD)
- Dataset confirmed: Home Credit Default Risk (public, Kaggle) — no real customer data
- Dependency environment validated
- `04_EVIDENCE_LEDGER.md` entry #1 written: "Repo audit complete; N assets identified"

**No-Overclaim Boundary:**
- Do not claim any model is trained until G2 is complete
- Do not claim any metric until it is computed against real data

**Stop Condition:** If any source repo has breaking changes or missing files that block absorption, document the gap and adjust the mix map before proceeding.

---

## G2 — Risk-Decision PRD and Component Map

**Objective:** Finalize the PulseGuard decision workflow diagram, confirm component mapping, and write the data flow specification that all subsequent gates will build against.

**Files / Artifacts to Create:**
- `docs/G2_decision_workflow.md` — step-by-step decision flow with module names and data contracts
- `docs/G2_data_contracts.md` — input/output schema for each module (feature set, model output, policy output, audit record)
- `docs/G2_risk_signal_design.md` — risk signal layer design (credit score, FOIR, calibrated probability, PSI flag, fairness flag)
- Updated `01_BEASTMAX_PRD.md` if any gaps found

**Success Criteria:**
- Decision workflow diagram covers all 7 stages (leakage → policy gate → champion score → challenger shadow → drift → fairness → governance)
- Data contracts specify column names and types at each module boundary
- All deferred components explicitly labeled DEFERRED in the design doc

**No-Overclaim Boundary:**
- Workflow diagram is a design document, not a running system
- Do not claim any component is "integrated" until code is written and tested

**Stop Condition:** If the decision workflow has unresolvable design conflicts (e.g., FOIR module requires data not available in Home Credit dataset), document the gap, create a synthetic workaround specification, and note it as simulated.

---

## G3 — Leakage Detection Kernel

**Objective:** Build and run the FeatureLeakageLens pre-training audit on the Home Credit feature set. Produce a structured leakage report that becomes the first evidence artifact.

**Files / Artifacts to Create:**
- `scripts/leakage_audit.py` — runs `LeakageAuditConfig` on Home Credit features; outputs JSON/Markdown/HTML
- `scripts/add_synthetic_timestamps.py` — adds synthetic timestamp columns to Home Credit features to demonstrate temporal FAIL path (Home Credit does not have native feature timestamps; without this, TemporalAvailabilityCheck and TrainingFutureDateScan cannot fire)
- `notebooks/01_leakage_audit.ipynb` — walkthrough of audit results with business interpretation
- `outputs/evidence/leakage_report.json`
- `outputs/evidence/leakage_report.md`
- `outputs/evidence/leakage_report.html`

**Success Criteria:**
- All 7 checks run without error on Home Credit feature set
- At least 1 WARN finding documented with business interpretation (e.g., `EXT_SOURCE_2` high correlation with target)
- Temporal checks demonstrate the FAIL path via synthetic timestamps (document clearly as synthetic)
- Evidence ledger entry #2: "Feature leakage audit: N features, M WARNs, K FAILs"
- Safe interview line written for this artifact
- Group leakage check noted as a roadmap gap (entity contamination check not yet in FLL)

**No-Overclaim Boundary:**
- This audit is run on a training simulation dataset, not a production feature store
- Temporal checks require timestamps — if not present in Home Credit, document the limitation and create a synthetic temporal extension
- "PASS" on this audit does not prove the model is production-safe

**Stop Condition:** If `featureleakagelens` library errors or produces unexpected results on Home Credit columns, debug and fix before claiming the gate is closed.

---

## G4 — Drift and Data Quality Monitor

**Objective:** Implement PSI drift computation and per-feature KS statistics across a 30-day simulated operational lifecycle. Confirm drift alert fires correctly on synthetic population shift.

**Files / Artifacts to Create:**
- `scripts/drift_monitor.py` — computes PSI and KS for each batch; outputs `drift_report.json`
- `scripts/seed_lifecycle.py` — generates 30 synthetic batch populations with controlled drift injection (Day 7 WARN, Day 14 ALERT)
- `notebooks/02_drift_analysis.ipynb` — PSI over time plots; feature-level KS heatmap
- `outputs/evidence/drift_report.json`
- `outputs/plots/psi_over_time.png`
- `outputs/plots/ks_heatmap.png`

**Success Criteria:**
- PSI computed across 30 batches; Day 7 > 0.10 (WARN), Day 14 > 0.20 (ALERT)
- `drift_alert_test.py` asserts PSI > 0.20 on Day 14 population — passes
- Top 5 drifted features identified and named
- Evidence ledger entry #3: "PSI Day14 = X.XXXX (ALERT); KS top feature = <name>"

**No-Overclaim Boundary:**
- Day 14 drift is synthetic injection — document explicitly as "simulated drift event, not observed production drift"
- PSI values are not real-time monitoring; they are computed post-hoc on scripted populations

**Stop Condition:** If drift monitor does not fire on the injected population, do not adjust the injection until the bug in the monitor is fixed. Do not reverse-engineer the threshold to make the test pass.

---

## G5 — Fairness / Proxy-Risk Layer

**Objective:** Run fairness audit on the champion model's decisions. Document Disparate Impact and Equal Opportunity gap for at least one protected attribute. Check SHAP rank of protected attribute proxies.

**Files / Artifacts to Create:**
- `scripts/fairness_audit.py` — computes Disparate Impact ratio and Equal Opportunity gap by group
- `scripts/shap_proxy_rank.py` — computes SHAP values; ranks protected attribute and known proxies
- `notebooks/03_fairness_audit.ipynb` — group-level approval rate analysis; SHAP beeswarm; calibration by group
- `outputs/evidence/fairness_report.json`
- `outputs/plots/shap_beeswarm.png`
- `outputs/plots/calibration_by_group.png`

**Success Criteria:**
- Disparate Impact (F/M approval rate ratio) computed and documented (target: 0.80–1.25 = no violation)
- Equal Opportunity gap (TPR parity) computed (target: < 5pp)
- SHAP rank of `CODE_GENDER` or proxy confirmed (must not be top-5 feature by mean |SHAP|)
- Evidence ledger entry #4: "Disparate Impact = X.XXX (PASS/FAIL); EOpp gap = Xpp"
- Safe interview line written

**No-Overclaim Boundary:**
- Fairness audit uses `CODE_GENDER` from Home Credit as a proxy for gender — this is a public variable, not a real protected class in a deployed system
- "No violation" result on synthetic data does not constitute regulatory compliance
- Do not claim this is equivalent to a formal SR 11-7 or RBI Fair Practice Code audit

**Stop Condition:** If Disparate Impact is outside bounds (< 0.80 or > 1.25), do not adjust thresholds to make it pass — instead document the finding as a genuine fairness concern and propose a remediation plan.

---

## G6 — Champion / Challenger Decision Engine

**Objective:** Train LightGBM challenger, run shadow scoring, apply 5-gate promotion framework, and produce a documented promotion decision (PROMOTE / HOLD / REJECT).

**Files / Artifacts to Create:**
- `scripts/train_challenger.py` — LightGBM training with same split; Platt calibration
- `scripts/champion_challenger_compare.py` — 8-metric head-to-head; 5-gate promotion logic
- `scripts/optuna_hpo.py` — 50-trial Bayesian HPO; ECE regression case documented
- `notebooks/04_champion_challenger.ipynb` — head-to-head analysis; promotion decision rationale
- `outputs/evidence/challenger_comparison_report.json`
- `outputs/evidence/challenger_promotion_decision.json`
- `outputs/evidence/optuna_hpo_results.json`

**Success Criteria:**
- Both champion and challenger evaluated on held-out test set (same split as training)
- 5 promotion gates defined and applied: PR AUC delta, ROC AUC delta, ECE gate, calibration gate, DeLong test
- Promotion decision documented with rationale (should match RiskFrame outcome: champion retained, challenger HOLD)
- Optuna HPO documents ECE regression: xgb_v2 better AUC, worse ECE → HOLD
- Evidence ledger entries #5, #6, #7

**No-Overclaim Boundary:**
- "Champion retained" does not mean the model is production-ready
- DeLong test p-value reported accurately — do not claim statistical significance unless p < 0.05
- ECE regression case is genuine; do not fabricate convergence or divergence

**Stop Condition:** If LightGBM training fails or produces degenerate results, debug before claiming the gate is closed. Do not adjust gate thresholds retroactively to engineer a specific outcome.

---

## G7 — Credit / Fraud Decision Simulation

**Objective:** Implement the credit underwriting decision workflow: FOIR engine, hard-rule gate, calibrated model score, and policy-based routing. Simulate 20–50 synthetic applications end-to-end.

**Files / Artifacts to Create:**
- `src/foir_engine.py` — recomputes FOIR from raw income and EMI obligations (no LLM, deterministic)
- `src/policy_gate.py` — hard rule enforcement (income floor, LTV cap, FOIR threshold, blacklist check)
- `src/decision_router.py` — applies policy to model score; outputs APPROVE / REVIEW / REJECT
- `src/policy_change_log.py` — logs policy version changes with timestamp, threshold delta, authorized_by
- `src/adverse_action_codes.py` — maps REJECT decisions to top-3 SHAP factors as illustrative adverse action reason codes (ECOA Regulation B awareness; not a legal implementation)
- `scripts/approval_rate_decomposition.py` — separates approval rate change into model signal vs. policy change signal using policy version log + drift monitor output
- `notebooks/05_decision_simulation.ipynb` — 50 synthetic applications (not 30 — 50 provides more statistical meaning); decision distribution; edge cases
- `outputs/evidence/policy_change_log.json`
- `outputs/evidence/batch_scoring_runs.csv`
- `outputs/evidence/decision_simulation_report.json`
- `outputs/evidence/adverse_action_report.json`

**Success Criteria:**
- FOIR correctly recomputed from raw inputs; not trusted from application input
- Hard rules fire correctly on edge cases (FOIR > 0.65 → REJECT; income below floor → HARD_REJECT)
- Policy v1.0 → v1.1 change logged with rationale
- 50 synthetic applications scored end-to-end with decision distribution and approval rate reported
- Approval rate decomposition: shows that Day 12 approval rate drop is attributable to policy change, not model drift
- Adverse action codes: top-3 SHAP factors for at least 5 REJECT decisions documented as illustrative reason codes
- Evidence ledger entries #8, #9, #10

**No-Overclaim Boundary:**
- FOIR computed on synthetic income figures — not real bank statements
- Do not claim "95% routing accuracy" without labeled ground truth — report decision distribution only
- Adverse action codes are illustrative (ECOA Regulation B awareness, not a legal compliance implementation)
- LangGraph is NOT used — sequential Python modules only

**Stop Condition:** If FOIR engine produces incorrect results on any edge case, fix the bug before claiming the gate is closed. Do not paper over incorrect routing with a disclaimer.

---

## G8 — Governance Evidence Ledger

**Objective:** Populate the full evidence ledger with 15+ entries. Write the model card. Produce a governance sign-off document that links all artifacts.

**Files / Artifacts to Create:**
- `04_EVIDENCE_LEDGER.md` — fully populated (15+ rows)
- `docs/MODEL_CARD.md` — model identity, training data, performance metrics, drift history, fairness results, limitations, governance sign-off status; includes:
  - Reject inference section: "Known boundary — model trained on approved applicants only; selection bias unmitigated; ECE is conditional on approval"
  - SR 26-2 alignment note: each lifecycle stage mapped to SR 26-2 requirement
  - Retraining trigger and decommissioning trigger defined
- `docs/governance_signoff.md` — decision: APPROVE / MONITOR / CHALLENGE / ESCALATE with rationale, artifact links, and SR 26-2 aligned evidence chain
- `outputs/evidence/governance_report.json` — machine-readable governance summary
- `scripts/delayed_label_validate.py` — generates synthetic 12-month outcomes (NOT derived from model scores); computes bad rate per score decile; validates rank-order preservation

**Success Criteria:**
- Every claim in the evidence ledger has an artifact, metric, and confidence level
- Model card covers: identity, data, performance, calibration, drift, fairness, limitations (including reject inference), governance status
- Governance decision is documented with specific artifact references (not just "model looks good")
- No evidence row has confidence "HIGH" without a computed artifact behind it
- Reject inference is documented as a known boundary condition with specific impact quantification
- Retraining and decommissioning triggers are defined in model card

**No-Overclaim Boundary:**
- Governance sign-off is internal/portfolio-level, not regulatory
- "Model approved" in this context means "approved for portfolio demonstration" — not production deployment

**Stop Condition:** If any evidence row cannot be supported by an artifact, mark it DEFERRED and do not fill it with placeholder metrics.

---

## G9 — Deep Defense Kernel

**Objective:** Add the interview defense layer. Write the technical defense document. Stress-test every claim against the hardest interview questions.

**Files / Artifacts to Create:**
- `docs/defense/PulseGuard_Interview_Defense.md` — 30+ Q&A covering all 10 technical areas
- `docs/defense/claim_stress_test.md` — every claim in `06_CLAIM_BOUNDARY.md` stress-tested against a skeptical interviewer
- `scripts/run_all_tests.sh` — runs all test suites end-to-end; outputs pass/fail summary

**Success Criteria:**
- Defense document covers: leakage detection methodology, calibration rationale, PSI threshold selection, fairness metric choice, champion/challenger framework, FOIR design, governance decision chain
- Every "resume-safe claim" in `06_CLAIM_BOUNDARY.md` has a corresponding Q&A defense
- All test suites pass (target: 45+ tests across all modules)

**No-Overclaim Boundary:**
- Defense document answers the hard questions honestly — including "what is not real", "what is simulated", "what would you do differently in production"
- Do not rehearse only the favorable answers

**Stop Condition:** If any test fails at this gate, fix the underlying code before writing the defense for that component.

---

## G10 — Final RiskFrame-Gold Audit

**Objective:** Final end-to-end audit. Verify that PulseGuard answers the flagship question in full. Produce the final portfolio presentation artifact.

**Files / Artifacts to Create:**
- `docs/final_audit.md` — gate-by-gate checklist; every artifact verified as present and non-empty
- `docs/portfolio_one_pager.md` — single-page summary for recruiter/hiring manager consumption
- Updated `00_CONTROL_TOWER.md` — status changed to "Gold-complete" with date
- Updated `06_CLAIM_BOUNDARY.md` — all built claims marked BUILT with artifact references

**Success Criteria:**
- All 10 gates closed
- 15+ evidence artifacts present in `outputs/evidence/`
- Flagship question answered end-to-end: "Can a bank, fintech, risk, or ML governance team decide whether a model is safe to use, whether its features are valid, whether its performance is drifting, whether decisions are fair, and whether the model should be approved, challenged, escalated, or retired?" → YES, with evidence.
- One-pager is clean, accurate, and defensible

**No-Overclaim Boundary:**
- "Gold-complete" means all gates closed and all claims supported by artifacts — not production deployment
- Final audit is a self-assessment; treat it as a pre-interview readiness check, not a certification

**Stop Condition:** If any gate has unclosed items at the final audit, re-open that gate rather than declaring gold-complete.
