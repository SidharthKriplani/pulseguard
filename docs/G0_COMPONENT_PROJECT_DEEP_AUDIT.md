# G0 — COMPONENT PROJECT DEEP AUDIT
## PulseGuard · Honest Assessment of Every Source Asset

**Audit stance:** Every component project is evaluated as if submitted by a candidate for a staff-level risk DS role. What would a skeptical senior interviewer say about each one? What survives the pressure test? What doesn't?

---

## PROJECT 1: riskframe_platform

### Identity
End-to-end credit decisioning platform. XGBoost + LightGBM champion/challenger, Optuna HPO, Platt calibration, PSI drift alerting, fairness audit, FastAPI serving.

### Strong Assets (KEEP — port directly or by reference)

**1. The ECE regression finding (highest-value artifact in the entire portfolio)**
xgb_v2 achieves PR AUC 0.2654 (better than champion 0.2611) but ECE regresses from 0.0046 to 0.0243. Model held. This is a governance decision, not a model comparison. No naive portfolio project has this. Every senior interviewer will recognize it. It demonstrates that the candidate understands calibration is the deployment gate, not AUC.

**2. 5-Gate Promotion Framework**
Pre-defined gates (PR AUC delta, ROC AUC delta, ECE gate, DeLong test, promotion decision). The DeLong test p-value (~0.07) shows the AUC difference is not statistically significant — correct decision to hold the challenger. This is exactly the right governance judgment.

**3. Platt Calibration with ECE 0.0046**
ECE 0.0046 is genuinely good. For reference, a perfectly calibrated model has ECE = 0. ECE < 0.01 is a strong result. This is a real, computed, defensible metric.

**4. PSI Drift with Synthetic Injection**
Day 7 WARN (PSI 0.158), Day 14 ALERT (PSI 0.2358). The injection is synthetic but labeled as such. `drift_fire_test.py` asserts PSI > 0.20 on the injected population. This is correctly implemented.

**5. Policy Version Log (policy_change_log.json)**
Day 12: policy v1.0 → v1.1, capacity 30% → 15%, threshold tightened. This is the policy-model decoupling concept implemented. Almost no portfolio projects have this.

**6. Training-Serving Parity Check**
`parity_check.py` asserts batch scorer == API scorer within 1e-6. This demonstrates production engineering discipline.

**7. 30-Day Operational Lifecycle Simulation**
Scripted lifecycle with malformed batch (Day 4), drift injection (Day 14), policy change (Day 12), challenger shadow (Day 10), delayed label validation (Day 30). The simulation structure is production-shaped.

**8. Fairness Audit**
DI = 1.059 (PASS), EOpp gap ~2.8pp (PASS). SHAP rank of CODE_GENDER_F = #10. Correctly measures fairness at the decision output level.

**9. 22/22 Tests Passing**
Including `drift_fire_test.py` which asserts the specific PSI threshold. This is testable, reproducible evidence.

### Weak / Fake-Looking Parts

**1. Home Credit PR AUC 0.2611 without context**
PR AUC 0.2611 sounds weak in isolation. Without context — "this is a heavily imbalanced dataset (8% default rate), and PR AUC is the primary metric in imbalanced classification" — it sounds like a bad model. The README provides this context, but it needs to be front-and-center in the interview story.

**2. "Production-simulated" framing needs sharpening**
The README says "production-simulated" but does not always make clear what this means mechanically. In an interview, a skeptic could ask: "Is this actually running in production?" The answer must be immediately clear: "No — this is a simulated lifecycle on public data. The infrastructure pattern is production-shaped."

**3. Fairness: CODE_GENDER is a public dataset field, not a real protected class**
The fairness analysis correctly measures DI, but CODE_GENDER in the Home Credit dataset is a self-declared binary field in a public Kaggle dataset. It is not a real protected class in a deployed system. The model card must document this boundary.

**4. Disparate Impact on the approval rate — not the full applicant pool**
The fairness check is on approved applicants' outcomes, not on the full applicant pool's approval rate. This is a subtle but important limitation: if the model never approves female applicants, the DI of 1.059 would be misleading. Need to confirm the DI computation uses the approval decision on all scored applicants, not just approved ones.

**5. Reject inference: completely missing**
The model is trained on approved applicants only. This is not documented as a limitation anywhere in the current README/control docs. It must be acknowledged.

**6. Delayed label validation is synthetic**
Day 30 "bad-rate-by-bucket" validation uses synthetic labels. This is fine but must be labeled explicitly. The current README says "200 synthetic review outcomes logged with override reasons" — correct framing.

### What Should Be Ported (Reuse)
- Platt calibration implementation
- PSI + KS computation
- 5-gate promotion framework
- Policy change log schema
- `parity_check.py` pattern
- FastAPI endpoint structure
- 30-day lifecycle seed script
- Test suite structure (22/22 pattern)
- Fairness computation (DI + EOpp + SHAP rank)
- Evidence artifact schemas (JSON)

### What Should Be Dependency-Only (Reference but Rebuilt)
- Feature pipeline (ABTBuilder for Home Credit) — rebuild cleaner with leakage audit gate built in
- XGBoost training script — rebuild with cleaner separation of concerns

### What Should Be Reference-Only (Don't Port)
- Docker compose (build later at G9)
- FastAPI dashboard.html (build later at G9)

### What Should Be Killed
- Nothing. RiskFrame is the strongest source project and the core of PulseGuard.

### Overall Verdict
RiskFrame is production-quality portfolio work. The ECE regression finding alone justifies the project. Port everything. The gaps (reject inference, calibration at decision boundary documentation, DI on full applicant pool) must be fixed in PulseGuard.

---

## PROJECT 2: featureleakagelens

### Identity
PyPI library (pip install featureleakagelens). 7 leakage checks, 2 FAIL-level (temporal). JSON/Markdown/HTML output.

### Strong Assets (KEEP)

**1. The 7-check system with WARN/FAIL tiering**
Two checks that can FAIL (temporal availability, training future date scan) vs. five that WARN. The distinction is correct and defensible: temporal violations are structural (not just suspicious); statistical WARNs require human confirmation.

**2. The "truth boundary" concept**
"This tool flags suspicious patterns. Human judgment confirms whether a feature was available at prediction time." This is honest, correct, and impressive. Most tools overclaim.

**3. 23 tests**

**4. PyPI-published**
`pip install featureleakagelens` is a real deliverable. A working PyPI package is more credible than a notebook.

**5. Structured output (JSON/Markdown/HTML)**
Machine-readable (for evidence ledger) + human-readable (for model card).

**6. Connection to RiskFrame pre-training gate**
The README explicitly connects FLL to RiskFrame: "FeatureLeakageLens audits the feature set for target leakage (features that encode default status directly) and temporal leakage (features computed after the loan decision date)." This framing is correct and portfolio-coherent.

### Weak / Fake-Looking Parts

**1. The temporal checks require timestamps**
Home Credit does not have feature-level timestamps. This means `TemporalAvailabilityCheck` and `TrainingFutureDateScan` will not fire on the Home Credit dataset without synthetic timestamp engineering. This must be addressed in PulseGuard — either add synthetic timestamps to demonstrate the checks, or clearly document why they don't fire and what they would catch.

**2. Roadmap items (mutual information, group leakage) are listed but not built**
This is correctly labeled as "Roadmap" in the README. But the absence of group leakage check is a gap — entity contamination (same SK_ID_CURR in train and test) is a real leakage type. PulseGuard should add a group leakage check.

**3. The split distribution scan fires INSUFFICIENT_INPUT without split_col**
On Home Credit data where the split is done in code (not a column), this check may produce INSUFFICIENT_INPUT rather than PASS or WARN. This must be handled — either add a split column or document the INSUFFICIENT_INPUT result.

### What Should Be Ported
- All 7 checks as the pre-training gate
- LeakageAuditConfig API
- JSON/Markdown/HTML output
- 23 tests

### What Should Be Reference-Only
- PyPI package: import directly; don't rebuild

### What Needs to Be Added in PulseGuard
- Synthetic timestamp extension for Home Credit to demonstrate temporal checks
- Group leakage check (entity-level contamination)
- Clear documentation of INSUFFICIENT_INPUT handling for split distribution check

### Overall Verdict
Strong PyPI library. The temporal check limitation on Home Credit is a gap that must be addressed. Otherwise, integrate directly via `pip install` and run as the pre-training gate.

---

## PROJECT 3: lendflow

### Identity
LangGraph 7-node AI pipeline for vehicle loan underwriting (Indian NBFC context). FOIR engine, hybrid RAG, RAGAS evaluation, APPROVE/REFER/REJECT routing.

### Strong Assets (KEEP)

**1. Deterministic-first design principle**
"LLMs are synthesis engines, not decision engines." Hard rules compute before any LLM call. FOIR is always recomputed from raw inputs. This is the correct production principle and will impress any senior interviewer in risk.

**2. FOIR engine**
Recomputes FOIR from raw income and EMI obligations. Never trusts the application-provided value. This is both technically correct and governance-aligned. One-liner in an interview that demonstrates domain understanding.

**3. APPROVE / REFER / REJECT routing with hard rule gate**
Six hard rules (LTV cap, age limits, income floor, pincode blacklist, vehicle age, loan tenor) produce HARD_REJECT before any model call. This is the correct layering: deterministic gates before probabilistic scoring.

**4. Hybrid RAG (BM25 + ChromaDB + cross-encoder)**
RAGAS faithfulness 0.91 is a strong result. The hybrid retrieval design (BM25 for exact-match regulatory phrases + dense for semantic) is the correct production pattern.

**5. Tamper-evident JSONL audit trail**
Every decision produces a JSONL record. This is the right governance pattern.

**6. PII redaction (Presidio)**
Aadhaar, PAN, phone numbers scrubbed before any LLM call. This demonstrates privacy engineering awareness.

**7. RAGAS evaluation on 20 synthetic applications**
Routing accuracy 95% (19/20). The 1 failure is documented: Application #14, FOIR = 43.1% on the CONDITIONAL/APPROVE boundary. Risk band wrong. This is the correct way to report an evaluation — include the failure case and explain it.

### Weak / Fake-Looking Parts

**1. LangGraph architecture is overkill for this decision**
The 7-node LangGraph pipeline for what is essentially a rule engine + FOIR computation + RAG lookup is significantly more complex than needed. LangGraph is appropriate for multi-agent workflows with complex state transitions and conditional branching. A sequential 7-node credit decision that always executes in the same order is better implemented as a Python pipeline with explicit state.

**2. The NBFC/vehicle loan domain is very narrow**
"Indian NBFC vehicle loan underwriting" is a narrow vertical. PulseGuard needs to generalize this to "credit underwriting decision workflow" — keeping the FOIR engine and hard rule gate as core modules while dropping the LangGraph wrapper.

**3. 20 synthetic applications is a small evaluation set**
19/20 routing accuracy on 20 applications is not statistically meaningful. With 95% confidence interval on a proportion, the true accuracy is anywhere from 75% to 99%. The evaluation needs more applications or should be presented as a demonstration, not a benchmark.

**4. RAG over "RBI Master Directions, NBFC Circulars, NHB Circulars" is unverifiable**
The policy corpus is described but the actual documents, their licensing, and their availability are not documented. In PulseGuard, the credit policy corpus must be clearly described: what documents, what format, what license, how obtained.

**5. HARD_REJECT on "blacklisted pincode" with no source for the blacklist**
The pincode blacklist is described but not sourced. In a portfolio project, this should either be a clearly synthetic list or a publicly available regulatory document.

### What Should Be Ported
- FOIR engine (pure Python, standalone) → `src/foir_engine.py`
- Hard rule gate logic → `src/policy_gate.py`
- APPROVE/REFER/REJECT routing framework → `src/decision_router.py`
- Tamper-evident JSONL audit trail pattern → `src/audit_logger.py`
- Policy citation format (linking decisions to policy clauses)

### What Should Be Dependency-Only (Reference but Rebuilt Simpler)
- Evaluation framework: rebuild with more synthetic applications (50+) and clearer statistical framing
- RAG policy lookup: rebuild as a simpler version (hardcoded rules for MVP; hybrid RAG for Gold)

### What Should Be Killed
- LangGraph wiring: not needed; adds complexity without adding governance value
- Presidio PII redaction: not needed for synthetic data pipeline; note it as a production requirement
- NBFC/vehicle loan domain framing: generalize to "credit underwriting workflow"
- 7-node pipeline as an "agent" story: this is not an agentic system; it is a decision pipeline

### What Needs to Be Added in PulseGuard
- FOIR computation with synthetic Home Credit income/EMI equivalents
- Decision simulation on 50+ synthetic applications
- Clear documentation that the "credit policy" is synthetic/illustrative

### Overall Verdict
Lendflow's strongest contribution to PulseGuard is the deterministic-first principle and the FOIR engine. The LangGraph wrapper and NBFC framing are distractions. Extract the core decision logic; drop the agent architecture.

---

## PROJECT 4: nexussupply

### Identity
Supplier risk intelligence platform. 4 signals (Altman Z, FinBERT sentiment, ESG, graph contagion). Composite scoring. LangGraph 7-node pipeline.

### Strong Assets (SELECTIVE ABSORB)

**1. Composite multi-signal risk fusion formula**
`composite = 0.40 × financial_risk + 0.25 × sentiment_risk + 0.20 × esg_risk + 0.15 × contagion_risk`
The formula structure — explicit weights, documented rationale, deterministic composite computed before LLM synthesis — is the right pattern for any multi-signal risk system. This is reusable as a template for PulseGuard's multi-signal scoring module (IF we add multiple signals beyond model score).

**2. Altman Z-score 3-variant selection logic**
Auto-selecting the correct Altman Z variant (public manufacturer, private firm, non-manufacturing) based on industry vertical is a sophisticated touch that most implementations skip. This is genuinely impressive in a supplier risk / corporate credit context.

**3. XGBoost distillation from rule-based scores**
Training XGBoost on financial ratio features to distill the Altman Z signal into a continuous ML health score demonstrates the correct pattern: start with an interpretable rule-based signal, then distill into a more flexible ML model.

**4. Graph contagion propagation math**
2-hop BFS with decay factor 0.4. Betweenness centrality. This is a real graph algorithm correctly applied to supply chain contagion.

**5. MLflow tracking for the XGBoost financial model**
MLflow experiment tracking is the production-standard tool. Using it in a portfolio project correctly signals MLOps awareness.

### Weak / Fake-Looking Parts

**1. CV ROC-AUC 1.00 on synthetic data is a red flag**
"CV ROC-AUC: 1.00 · CV F1: 0.997 · CV PR-AUC: 1.00 — Near-perfect CV on synthetic data is expected: labels are derived from the same financial ratios used as features." The README correctly caveats this. But a near-perfect AUC on a model trained on synthetic data where labels are derived from features is not an AUC — it is a tautology. An interviewer will probe this immediately. The answer ("the synthetic label generation intentionally made this tautological to demonstrate the pipeline; in production you'd calibrate on real distress events") is defensible but risky.

**2. FinBERT on 20 synthetic headlines with calibrated sentiment**
"Sentiment distribution calibrated per risk tier — CRITICAL suppliers get 75% negative headlines." This is circular: the sentiment model confirms the label that determined the data it was tested on. This is data leakage at the evaluation level.

**3. ESG parsing via LLM on synthetic ESG summaries**
Templated ESG summaries with risk-tier-aware metric ranges. Same problem: the LLM is being evaluated on data it can trivially get right because the data was generated with systematic signals.

**4. The supplier/procurement domain is not aligned with PulseGuard's buyer**
A risk DS at a bank or fintech is not interested in supplier risk intelligence as a domain. They are interested in borrower risk, counterparty risk, and fraud — not procurement.

### What Should Be Ported (Formula patterns only)
- Composite risk scoring formula structure (weighted multi-signal fusion)
- Altman Z-score 3-variant selection (IF counterparty/corporate credit module is added)
- Graph contagion math (IF fraud network analysis is added at G9)

### What Should Be Reference-Only
- MLflow tracking pattern (reference; recommend using MLflow in PulseGuard for HPO)

### What Should Be Killed
- Full NexusSupply pipeline: not ported to PulseGuard
- FinBERT sentiment: not relevant to credit/fraud risk DS role
- ESG parsing: not relevant
- Synthetic supplier dataset (500 suppliers, 6000 records): not used
- LangGraph wiring: not needed
- Supply chain contagion framing: not aligned with buyer/role

### Overall Verdict
NexusSupply's contribution to PulseGuard is exactly one design pattern: the composite multi-signal fusion formula. The supplier domain, the circular evaluation, and the LangGraph architecture are all dropped. If PulseGuard adds a corporate credit or counterparty risk module, Altman Z is pulled in then.

---

## CROSS-PROJECT REDUNDANCY ANALYSIS

| Concern | RiskFrame | LendFlow | NexusSupply | Resolution |
|---------|-----------|---------|-------------|-----------|
| APPROVE/REJECT decision output | ✓ (model-based) | ✓ (rule-based + model) | ✓ (composite score) | Use RiskFrame for model-based; LendFlow for rule-based; these are separate layers |
| LangGraph pipeline | — | ✓ | ✓ | Drop from PulseGuard entirely |
| XGBoost model | ✓ | — | ✓ (financial scorer) | Use RiskFrame XGBoost as champion; NexusSupply XGBoost is different domain |
| Audit trail | ✓ (CSV + JSON) | ✓ (JSONL) | ✓ (JSONL) | Use LendFlow's JSONL pattern as standard |
| FastAPI serving | ✓ | ✓ | ✓ | Use RiskFrame's serving pattern |
| Evidence artifacts | ✓ | ✓ | ✓ | Consolidate into PulseGuard evidence ledger |

---

## WHAT DOES NOT SURVIVE THE PRESSURE TEST

1. **NexusSupply's evaluation metrics**: CV AUC 1.00 on synthetic data is not a real evaluation result. Do not port this claim.
2. **LendFlow's 95% routing accuracy on 20 applications**: Not statistically meaningful. Re-benchmark on 50+ in PulseGuard.
3. **RiskFrame's fairness claim without full applicant pool DI**: Must add DI on the approval decision for all scored applicants, not just a subset.
4. **The absence of reject inference documentation**: Must be added to the model card.
5. **PSI computation without documenting the multivariate shift blindspot**: Must be documented in the monitoring design.
