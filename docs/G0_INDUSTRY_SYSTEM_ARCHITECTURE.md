# G0 — INDUSTRY SYSTEM ARCHITECTURE
## PulseGuard · What a Serious Version of This System Looks Like

---

## 1. THE FULL INDUSTRY SYSTEM MAP

### Core Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                          │
│  Raw applicant data → Feature engineering → Feature store           │
│  (point-in-time correctness enforced)                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PRE-TRAINING GATE                                                   │
│  Feature leakage audit → Temporal integrity check → Split validation│
│  PASS → proceed | FAIL → block training | WARN → document + proceed │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  TRAINING LAYER                                                      │
│  Champion training (XGBoost + HPO + Platt calibration)              │
│  Challenger training (LightGBM + same pipeline)                     │
│  Validation: PR AUC, ROC AUC, ECE, Brier, calibration curve        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  VALIDATION GATE (Champion/Challenger)                               │
│  5-gate promotion framework                                          │
│  DeLong test for AUC comparison                                      │
│  ECE gate: calibration must not regress                              │
│  Fairness gate: DI within 0.80–1.25                                  │
│  Decision: PROMOTE / HOLD / REJECT challenger                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DEPLOYMENT LAYER                                                    │
│  Model registry (version, artifact hash, calibration params)        │
│  Decision policy registry (thresholds, capacity, authorized_by)     │
│  Parity test: batch scorer == API scorer within 1e-6                │
│  FastAPI serving (/score /explain /drift /policy)                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DECISION LAYER                                                      │
│  Hard rule gate: FOIR, LTV cap, income floor, blacklist              │
│  Model score: calibrated probability                                 │
│  Policy routing: APPROVE / REVIEW / REJECT                           │
│  SHAP explanation: top-3 driving factors for adverse action          │
│  Audit record: JSONL with model version, policy version, score       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  MONITORING LAYER                                                    │
│  PSI per feature (per batch) → WARN > 0.10 / ALERT > 0.20          │
│  KS per feature                                                      │
│  Approval rate monitoring (model signal vs. policy signal)           │
│  Review rate monitoring (REVIEW queue volume)                        │
│  Delayed label validation (score decile vs. observed bad rate)       │
│  Alert escalation path: DS → Risk Manager → MRM committee            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GOVERNANCE LAYER                                                    │
│  Evidence ledger: 15+ artifacts with metrics and confidence          │
│  Model card: identity, data, performance, drift, fairness, limits    │
│  Governance decision: APPROVE / MONITOR / CHALLENGE / RETIRE         │
│  SR 26-2 alignment: lifecycle lineage, versioning, escalation docs   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. DATA INPUTS

| Input Type | What It Contains | Who Produces It | Point-in-Time Risk |
|-----------|-----------------|-----------------|-------------------|
| Applicant application | Demographics, income declaration, loan ask | Applicant | Low (contemporaneous) |
| Bureau data | Credit history, payment history, existing obligations | Credit bureau (CIBIL, Experian) | **HIGH** — bureau pull date must precede decision date |
| Bank statement | Transaction history, salary credits, EMI debits | Bank API / upload | **HIGH** — must use pre-decision window only |
| Engineered features | Income ratios, utilization rates, delinquency counts | Feature pipeline | **HIGH** — must be computed before outcome is known |
| Outcome label | Defaulted / Not defaulted at 12 months | Loan servicing system | **Temporal** — only available 6-12 months post-decision |

The feature store's job is to guarantee that every feature value attached to a training row reflects what was known **at the time of the credit decision** — not after the default event. This is the technical implementation of temporal leakage prevention.

---

## 3. DECISION OUTPUTS

| Output | Consumer | Format | Contains |
|--------|---------|--------|---------|
| APPROVE | Applicant, loan ops | JSON | Score, product recommendation, EMI, rate |
| REFER | Loan officer (human review) | JSON + SHAP | Score, top-3 factors, policy flag reason |
| REJECT | Applicant | JSON + adverse action codes | Decision reason codes (ECOA Regulation B compliant) |
| AUDIT_RECORD | MRM team, audit | JSONL | Model version, policy version, score, decision, timestamp |
| DRIFT_ALERT | Risk DS, operations | Alert | PSI value, feature name, threshold breached, severity |
| GOVERNANCE_SIGN_OFF | MRM committee | PDF/doc | Full evidence chain, decision, authorized by |

---

## 4. USER ROLES AND TOUCHPOINTS

```
Credit Applicant
  → Submits application
  → Receives APPROVE/REFER/REJECT + reason codes
  → Never sees model internals

Loan Underwriter (Human in the Loop — REFER queue)
  → Receives REFER cases with SHAP top-3 factors
  → Reviews bureau data manually
  → Overrides model (logged with reason)
  → Override data feeds back into label validation

Risk Data Scientist
  → Owns model training, calibration, HPO, evaluation
  → Reviews drift alerts
  → Initiates challenger training
  → Produces evidence artifacts

ML Governance / MRM Analyst
  → Independent validation of champion model
  → Reviews challenger promotion decision
  → Signs off on governance document
  → Escalates to committee if REJECT or ESCALATE outcome

Risk Policy Lead / Decision Scientist
  → Owns decision threshold and capacity management
  → Versions the decision policy
  → Analyzes approval rate decomposition (model vs. policy changes)
  → Responds to business KPI movements

Regulator / Auditor (External)
  → Receives model card, evidence ledger, governance sign-off
  → Validates SR 26-2 compliance
  → Reviews adverse action code compliance (ECOA/Reg B)
```

---

## 5. SYSTEM COMPONENTS

| Component | Industry Pattern | Portfolio Implementation |
|-----------|----------------|------------------------|
| Feature store | Feast / Tecton / Hopsworks (point-in-time) | Feature pipeline with temporal audit (FeatureLeakageLens) |
| Model registry | MLflow / SageMaker / Vertex | `artifacts/` directory with version tags; JSON metadata |
| Training pipeline | Databricks / Airflow / Kubeflow | `scripts/train_champion.py` — standalone, reproducible |
| Decision engine | Custom rule engine + model serving | `src/decision_router.py` — FOIR gate + model score + policy |
| Serving | SageMaker / BentoML / Triton | FastAPI with `/score /explain /drift /policy` |
| Monitoring | Evidently AI / WhyLabs / Fiddler | `scripts/drift_monitor.py` — PSI + KS per feature |
| Governance | Internal MRM platform / manual | Evidence ledger + model card + governance sign-off doc |
| Audit trail | Immutable JSONL / data lake | `outputs/evidence/audit_log.jsonl` |

---

## 6. EVALUATION LAYER

The evaluation layer is not "run the model and compute AUC." It is a sequence of gates.

| Gate | Metric | Pass Threshold | Fail Action |
|------|--------|---------------|-------------|
| Feature leakage | FAIL count from 7-check audit | 0 FAILs | Block training |
| Discrimination | PR AUC (primary), ROC AUC | Challenger delta ≥ 0.001 to promote | Hold challenger |
| Calibration | ECE | < 0.01 for champion; must not regress by > 0.005 for promotion | Hold challenger or block deployment |
| Statistical significance | DeLong AUC test p-value | p < 0.05 to claim challenger is superior | Log result; do not promote if not significant |
| Fairness | Disparate Impact ratio | 0.80 ≤ DI ≤ 1.25 | Escalate; remediation required |
| Drift (ongoing) | PSI per batch | WARN > 0.10; ALERT > 0.20 | Alert DS; ALERT triggers model review |
| Label validation (ongoing) | Score decile vs. observed bad rate | Rank-order preserved; Brier score stable | Re-evaluate model; potential retraining |

---

## 7. GOVERNANCE LAYER (SR 26-2 ALIGNED)

The governance layer is not a post-hoc formality. Under SR 26-2 (April 2026), the expectation is:

> "Development, validation, deployment, monitoring, and retirement are one governed chain, with supervisors expecting lineage across every link, not snapshots at handoff points."
> — Databricks SR 26-2 Guide

**What a governed chain requires:**
1. **Model inventory entry**: Every model gets registered before training begins. Training without registration is a governance violation.
2. **Validation report**: Conceptual soundness + outcome analysis + ongoing monitoring plan — produced before deployment
3. **Champion/challenger documentation**: Versioned and reproducible. Not "we ran a comparison" — "here are the exact gate results with artifact hashes"
4. **Policy version log**: Every threshold change logged with timestamp, rationale, and authorization
5. **Ongoing monitoring cadence**: Defined alert thresholds, escalation paths, review frequency
6. **Retirement plan**: Every deployed model must have a defined retirement trigger (PSI ALERT sustained for N batches; AUC below floor; fairness violation)

---

## 8. HUMAN-IN-THE-LOOP POINTS

These are where the automated system must stop and involve a human:

1. **REFER queue**: Applicants with scores in the borderline zone (REVIEW tier) go to human underwriters with SHAP explanations
2. **Drift ALERT escalation**: PSI > 0.20 triggers human review by the risk DS before next batch scoring run
3. **Fairness violation**: Disparate Impact outside 0.80–1.25 triggers mandatory escalation — no automatic retry
4. **Challenger promotion decision**: A human (risk DS + MRM analyst) must sign the promotion decision — no automatic promotion
5. **Policy change authorization**: Threshold changes require a named authorized_by field — cannot be changed programmatically without sign-off

---

## 9. FAILURE HANDLING

| Failure | Detection | Response | Escalation |
|---------|----------|----------|-----------|
| Feature FAIL in leakage audit | Pre-training alert | Block training | DS + data team |
| PSI ALERT (> 0.20) | Batch monitoring | Pause batch scoring | DS → Risk Manager |
| Calibration regression in challenger | ECE gate | Hold challenger | Document; retrain |
| Fairness violation | Fairness audit | Block deployment | DS → MRM → Compliance |
| Batch scoring error (null rows, schema drift) | Data quality check | Reject bad rows; log rejected_rows.csv | Ops team |
| API latency > threshold | SLA monitoring | Alert | MLOps / on-call |

---

## 10. OFFLINE VS. ONLINE BOUNDARY

```
OFFLINE                         │ ONLINE
─────────────────────────────────┼────────────────────────────────────
Feature engineering              │ Request-time feature computation
Model training                   │ Model inference (FastAPI /score)
Champion/challenger evaluation   │ Shadow scoring (challenger)
PSI computation (batch)          │ Real-time score logging
Fairness audit (batch)           │ SHAP explanation (/explain endpoint)
Policy simulation                │ Decision routing
Evidence ledger assembly         │ Audit record write (JSONL)
Governance sign-off              │ Drift alert trigger
```

Portfolio note: PulseGuard operates primarily offline. The FastAPI server simulates the online boundary but is not production-deployed. This is clearly stated in all claim documents.

---

## 11. COST / LATENCY TRADEOFFS

| Component | Compute Cost | Latency | Portfolio Simplification |
|-----------|-------------|---------|------------------------|
| XGBoost inference | Very low | < 5ms | No simplification needed |
| SHAP computation (online) | Medium | 50-200ms | Portfolio: compute SHAP in batch, cache for explanation endpoint |
| PSI computation (per batch) | Low-Medium | Batch job | No simplification needed |
| Fairness audit | Low | Batch job | No simplification needed |
| Hybrid RAG (credit policy lookup) | Medium-High | 500-1500ms | Deferred to G7 |
| Graph contagion risk | High | Batch | Deferred to G9 |

---

## 12. BUILD VS. BUY TRADEOFFS

| Component | What to Buy / Use | What to Build | Portfolio Choice |
|-----------|------------------|---------------|-----------------|
| Feature store | Feast (open source) | Custom feature pipeline | Build custom pipeline (simpler, more demonstrable) |
| Model monitoring | Evidently AI | Custom PSI + KS | Build custom (shows technical understanding; Evidently AI is the industry tool to reference) |
| Experiment tracking | MLflow | Custom artifacts dir | MLflow for HPO; custom for evidence ledger |
| Serving | FastAPI | Custom | FastAPI (demonstrates production pattern) |
| Governance | Archer, MetricStream | Custom model card + ledger | Build custom (demonstrates domain knowledge) |

The build-vs-buy framing is itself an interview topic. A senior candidate should be able to say: "In production, I would use Evidently AI or WhyLabs for monitoring. In this portfolio, I built PSI computation from scratch to demonstrate I understand the underlying mechanics — not because I would always build it."

---

## 13. PRODUCTION VS. PORTFOLIO-SAFE BOUNDARY

| Capability | Production Requirement | Portfolio-Safe Version | Label in Artifacts |
|-----------|----------------------|----------------------|-------------------|
| Real-time scoring | < 5ms P99 at scale | FastAPI with synthetic requests | "Production-pattern" |
| Drift monitoring | Continuous, with paging | Batch scripts on simulated lifecycle | "Simulated 30-day lifecycle" |
| Feature store | Point-in-time, distributed | Temporal audit pre-training | "Pre-training temporal check" |
| Label collection | Real outcome labels | Synthetic label simulation | "Synthetic labels, labeled as such" |
| Reject inference | Full propensity model | Acknowledged as limitation | "Known boundary — not implemented" |
| Regulatory compliance | Formal SR 26-2 submission | Evidence-aligned documentation | "SR 26-2 aligned, not certified" |

Every artifact in PulseGuard must carry one of these labels. No artifact claims production capability it does not have.
