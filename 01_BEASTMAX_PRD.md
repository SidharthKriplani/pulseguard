# 01 — BEASTMAX PRD
## PulseGuard · Product Requirements Document

---

### Target User / Buyer

**Primary:** Risk Data Scientist, Credit DS, Fraud DS at a bank, fintech, or NBFC who owns a credit default or fraud model and must defend it in a model risk committee or regulatory review.

**Secondary:** ML Governance lead or Head of Model Risk who needs an audit-ready dossier — evidence of feature validity, drift history, fairness checks, and champion/challenger decisions — before approving a model for production.

**Buyer signal:** Any team that has been asked "how do you know this model is fair?", "when did you last check for drift?", "what happens when this model starts failing?", or "can you show us the feature validation before training?"

---

### Regulatory Context (Updated after G0)

In April 2026, SR 26-2 replaced SR 11-7 as the governing interagency guidance on model risk management. The new guidance explicitly treats development → validation → deployment → monitoring → retirement as "one governed chain, with supervisors expecting lineage across every link." Champion/challenger comparisons must be "versioned and reproducible — not a one-time memo." Ongoing monitoring must be tied to "changing conditions: products, exposures, clients, data relevance, and market dynamics."

PulseGuard is designed to generate the artifacts that this governed chain requires. It does not claim regulatory certification. It claims SR 26-2 aligned governance methodology.

---

### Business Pain

Risk systems fail silently. A credit default model with ROC AUC 0.77 can:

1. Be miscalibrated at the approval threshold — producing systematically wrong approval rates even as AUC looks fine
2. Use features that encode the outcome after the fact (post-outcome flags, future timestamps) — inflating validation AUC that collapses in production
3. Drift without alerting — a 14-day population shift pushes PSI above the alert threshold while the model keeps scoring
4. Encode proxy bias — a feature not labeled "gender" can still discriminate if it correlates with gender at the decision threshold
5. Make decisions that cannot be explained — the model approves or rejects without a defensible policy citation
6. Never be formally challenged — the incumbent champion runs indefinitely because there is no structured challenger promotion framework

Teams catch these failures late: after deployment, after regulatory inquiry, after business losses. The audit trail is informal, the review is manual, and the decision chain is undocumented.

---

### Decision Workflow

```
Application / Score Request
        │
        ▼
[1] Feature Leakage Gate
    (FeatureLeakageLens — 7 checks)
    PASS → continue
    WARN → document and proceed with caveat
    FAIL → block training; escalate to data team
        │
        ▼
[2] Policy Hard Gate
    (Deterministic rule enforcement — FOIR, LTV, income floor, blacklist)
    HARD_REJECT → audit trail, no model call
    PASS → continue
        │
        ▼
[3] Champion Model Scoring
    (Calibrated XGBoost — probability output)
    → Decision policy lookup:
      score < 0.06 → APPROVE
      0.06–0.28   → REVIEW (human queue)
      ≥ 0.28      → REJECT
        │
        ▼
[4] Challenger Shadow Scoring
    (LightGBM — runs parallel, not live)
    → Stored for head-to-head comparison at gate G25
        │
        ▼
[5] Drift Monitor
    (PSI + KS per feature)
    NOMINAL → continue
    WARN    → flag; alert in ops log
    ALERT   → escalate; model review triggered
        │
        ▼
[6] Fairness Check
    (Disparate Impact + Equal Opportunity gap)
    → Check at decision output level (not just feature list)
    → SHAP rank of protected attribute proxies
    PASS    → document in model card
    FAIL    → escalate; policy review required
        │
        ▼
[7] Approval Rate Decomposition
    (Is approval rate change caused by model drift or policy change?)
    → Compare PSI trend vs. policy version log delta
    → Isolate model signal from policy signal
        │
        ▼
[8] Governance Decision
    APPROVE / MONITOR / CHALLENGE / REJECT / ESCALATE
    → Recorded in governance evidence ledger
    → SR 26-2 aligned evidence chain
    → Retraining trigger defined
    → Decommissioning trigger defined
```

---

### Model Risk Lifecycle

```
Pre-training
  └── Feature leakage audit (FeatureLeakageLens)
  └── Dataset split integrity check

Training
  └── Champion training (XGBoost + Optuna HPO)
  └── Calibration (Platt sigmoid, ECE < 0.01)
  └── Gate evaluation (PR AUC, ROC AUC, ECE, calibration curve)

Challenger Registration
  └── LightGBM trained on same split
  └── Shadow scoring begins
  └── 5-gate promotion framework

Deployment Decision
  └── Promote / Hold / Reject challenger
  └── Policy version logged (threshold, capacity, authorized_by)

Monitoring (30-day simulation)
  └── PSI per batch
  └── Per-feature KS
  └── Review rate tracking
  └── Delayed label validation (bad-rate-by-bucket vs. predicted at Day 30)
  └── Retraining trigger: PSI ALERT ≥ 2 consecutive batches, or Gini drop > 3pp
  └── Decommissioning trigger: PSI > 0.30 sustained; DI violation unresolved > 30 days
  └── Known limitation: reject inference not implemented — model trained on approved applicants only

Fairness Audit
  └── Disparate Impact (target: 0.80–1.25)
  └── Equal Opportunity gap (target: < 5pp)
  └── SHAP rank of protected attribute proxies

Governance Sign-off
  └── Evidence ledger entry
  └── Model card update
  └── Governance decision: APPROVE / MONITOR / CHALLENGE / RETIRE
```

---

### Key Governance Decisions

| Decision | Trigger | Output |
|----------|---------|--------|
| **APPROVE** | All gates pass; ECE < 0.01; PSI < 0.10; Disparate Impact 0.80–1.25 | Promote to champion; log in registry |
| **MONITOR** | PSI WARN (0.10–0.20); minor ECE regression; fairness borderline | Continue with enhanced monitoring cadence |
| **CHALLENGE** | Challenger within delta on AUC but not all gates; performance equivalent | Keep champion; record challenger report |
| **REJECT** | ECE regression > 2x; PSI ALERT > 0.20; Disparate Impact outside bounds | Block; do not deploy; remediation required |
| **ESCALATE** | Fairness violation; leakage FAIL on champion feature set; policy conflict | Human review required; governance committee notification |

---

### Success Criteria

**MVP (BeastMax base):**
- Feature leakage audit runs on training dataset and produces structured report
- Champion model trained, calibrated, and evaluated (AUC, ECE, calibration curve)
- PSI drift computed across 30-day simulated lifecycle
- Fairness report generated for at least one protected attribute
- Decision policy engine applies APPROVE/REVIEW/REJECT thresholds with version log
- Evidence ledger populated with at least 5 artifacts
- All claims tagged: built / simulated / proposed / deferred

**Gold (T3):**
- Full champion/challenger 5-gate promotion framework with documented decision
- Optuna HPO with ECE regression case documented
- Temporal leakage check integrated into pre-training pipeline
- Hybrid RAG over credit policy corpus with RAGAS evaluation
- FOIR recomputation module for underwriting scenario
- Full 30-day operational lifecycle with batch scoring, policy change event, drift injection, delayed label validation
- Governance evidence ledger with 15+ artifacts
- FastAPI serving with training-serving parity test
- Docker-composed end-to-end run
- Model card with all audit artifacts linked
- Interview defense document covering all decision points

---

### Negative-Cost Chain

If the system fails at each stage, the business consequence is:

| Failure Point | Consequence |
|--------------|-------------|
| Feature leakage not caught | Model AUC inflates pre-launch; collapses in production; months of decisions made on a broken model |
| Calibration not checked | Approval rates miscalibrated; too many approvals at wrong risk level or too many rejections of good borrowers |
| Drift not monitored | Silent degradation; model continues scoring on an out-of-distribution population |
| Fairness not audited | Regulatory exposure; discriminatory approval rates by protected group |
| No challenger framework | Champion runs indefinitely; no mechanism to improve or replace |
| No policy version log | Threshold change made silently; cannot attribute decision outcomes to policy version |
| No governance evidence | Model risk committee cannot approve; audit fails |

---

### Failure Modes

1. **Leakage invisibility:** Post-outcome feature passes name scan but fails temporal check — caught only by `TemporalAvailabilityCheck`
2. **Calibration collapse:** Optuna HPO improves AUC but ECE regresses 5x — model held despite better discrimination
3. **Drift without alert:** PSI computed but not compared against threshold; alert never fires
4. **Proxy bias entry:** Protected attribute excluded from features but correlated proxy included — fairness check must audit SHAP ranks, not just feature list
5. **Champion lock-in:** No structured challenger framework means better models never get promoted
6. **Policy-model conflation:** Approval rate drops 5% — was it model drift or policy tightening? Without separate versioning, this question takes weeks to answer
7. **Selection bias (reject inference):** Model trained only on approved applicants; never learned the risk profile of marginal borrowers; calibration is conditional on approval, not on the full applicant pool
8. **PSI multivariate blindspot:** PSI detects per-feature distribution shift but misses joint distribution shift — two stable features can jointly shift significantly while PSI appears nominal
9. **Governance evidence absence:** SR 26-2 audit arrives; no evidence ledger, no model card, no champion/challenger artifacts → model cannot be approved; remediation takes months

---

### MVP BeastMax Version

Scope: G1–G8 (Repo audit → PRD/Design → Leakage → Champion Training + Drift → Fairness → Champion/Challenger → Decision Pipeline → Governance)

> PRD gap fixed at G2: Prior version listed "G1–G5" but G5 (fairness) does not include
> the decision policy engine (FOIR + hard rules + routing), which is G7. The MVP must
> include G7 to demonstrate a complete risk-decision platform.
> G8 (governance sign-off + model card) is the MVP completion gate.

Deliverables:
- `docs/G1_repo_audit.md` — source asset classification ✓ BUILT
- `docs/G1_dataset_plan.md` — dataset and lifecycle design ✓ BUILT
- `scripts/verify_imports.py` — environment verification ✓ BUILT (16/16 PASS)
- `docs/G2_decision_workflow.md` — full pipeline design ✓ BUILT
- `docs/G2_data_contracts.md` — module data contracts ✓ BUILT
- `docs/G2_risk_signal_design.md` — risk signal specifications ✓ BUILT
- `scripts/leakage_audit.py` — runs FeatureLeakageLens on Home Credit (DEFERRED — G3)
- `scripts/train_champion.py` — XGBoost training with calibration (DEFERRED — G4)
- `scripts/drift_monitor.py` — PSI + KS across 30-day simulated batches (DEFERRED — G4)
- `scripts/fairness_audit.py` — Disparate Impact + Equal Opportunity (DEFERRED — G5)
- `scripts/train_challenger.py` — LightGBM challenger + 5-gate evaluation (DEFERRED — G6)
- `src/foir_engine.py`, `src/policy_gate.py`, `src/decision_router.py` — underwriting decision pipeline (DEFERRED — G7)
- `scripts/approval_rate_decomposition.py` — model vs. policy attribution (DEFERRED — G7)
- `docs/MODEL_CARD.md`, `docs/governance_signoff.md` — governance sign-off artifacts (DEFERRED — G8)
- `04_EVIDENCE_LEDGER.md` with 15 entries populated (DEFERRED — G8)

---

### Ideal T3 / Gold Version

Full G1–G10 completion:
- Feature leakage gate → calibrated champion training → Optuna HPO with ECE regression case → challenger registration and 5-gate promotion → 30-day drift lifecycle → fairness audit → FOIR/underwriting decision simulation → hybrid RAG credit policy lookup → governance evidence ledger → FastAPI serving → Docker end-to-end → model card → interview defense document

Claim at gold: "End-to-end risk decision and model governance system covering the complete ML lifecycle from feature validation through governance sign-off, production-simulated on public credit data with 15+ evidence artifacts."
