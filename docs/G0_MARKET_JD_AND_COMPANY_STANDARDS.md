# G0 — MARKET JD AND COMPANY STANDARDS
## PulseGuard · Job Description Analysis + Industry Benchmarks

---

## 1. JD PATTERN ANALYSIS

### The Intuit Staff AI Scientist Template (Best Available JD Signal)

Intuit (Intuit Credit Karma, Consumer Risk) is the best public JD signal for the risk DS archetype in a FAANG-adjacent fintech. Their Staff and Senior positions represent the 95th percentile of expectation.

**Staff Fraud AI Scientist — Intuit (2025)**
Sources: [Staff Fraud AI Scientist](https://jobs.intuit.com/job/mountain-view/staff-fraud-ai-scientist-fintech-consumer-risk/27595/87369449712) | [Senior Credit Risk AI Scientist](https://jobs.intuit.com/job/mountain-view/senior-credit-risk-ai-scientist-fintech-consumer-risk/27595/89706909120)

Core requirement: "Designing, building, evaluating, monitoring, maintaining, and defending machine learning models to predict and prevent various types of fraud and/or financial risk — with full model lifecycle ownership."

Key skill phrases extracted:
- "fraud score calibration" → not AUC, specifically calibration
- "label bias correction" → understanding of selection/survivorship bias
- "case disposition logic" → decision routing, not just scoring
- "network or graph-based link analysis" → graph risk signal sophistication
- "deep learning, tree-based models, reinforcement learning, clustering, time series, causal analysis" → multi-technique fluency
- "deploy, monitor and maintain" — not just train and evaluate
- 5+ years in credit risk, decision science, or quantitative analytics within a bank, credit union, fintech, or consumer lender

**Gap between this JD and a naive portfolio project:**

| JD Requirement | Naive Portfolio | PulseGuard Candidate |
|---------------|-----------------|---------------------|
| Fraud score calibration | Missing | ECE 0.0046, Platt calibration, calibration curve at threshold |
| Label bias correction | Missing | Reject inference documented as known limitation in model card |
| Case disposition logic | Missing | APPROVE/REVIEW/REJECT routing with FOIR gate and policy log |
| Monitor and maintain | Missing | 30-day lifecycle simulation, PSI alerting, delayed label validation |
| Lifecycle ownership | Missing | Leakage → training → calibration → drift → fairness → governance chain |
| Defend | Missing | Interview defense document, 30+ Q&A, technique rationale |

---

## 2. COMPANY STANDARDS BY TIER

### Tier 1 — Regulated Banks / NBFC (compliance-mandatory)

What they require by regulation (SR 26-2, OCC Bulletin 2026-13):
- Model inventory with tiering
- Independent validation (conceptual soundness + outcome analysis)
- Champion/challenger with documented, versioned comparison
- Ongoing monitoring with defined thresholds and escalation
- Retirement/decommissioning documentation

What they value in a DS candidate joining the MRM or risk team:
- Evidence of having operated within a governance framework
- Understanding of why champion/challenger gates exist (not just how to run them)
- Calibration discipline (especially at the decision threshold)
- Ability to produce audit-ready documentation, not just model notebooks

### Tier 2 — FAANG-adjacent Fintechs (Intuit, Affirm, Klarna, Stripe, Plaid, Chime)

What they require technically:
- Full lifecycle tooling: feature store awareness, serving parity, drift monitoring
- Calibration as a first-class citizen (Platt vs. isotonic, ECE as gate)
- Training/serving parity (the same object that trained must serve)
- Reject inference acknowledgment (at minimum) or implementation
- Business consequence chain: model → decision → approval rate → credit loss → revenue impact

What they look for in candidates:
- Senior candidates who understand the difference between AUC (discrimination) and ECE (calibration) and when each matters more
- Evidence of having been "wrong" and documented why — the held model is more impressive than the deployed one
- Graph signal awareness (fraud interconnection, transaction graph)
- Policy-model versioning (rare in portfolios, highly valued)

### Tier 3 — ML Governance / Model Risk Teams (at large banks or dedicated MRM consultancies)

What they require:
- SR 26-2 / interagency guidance familiarity (as of April 2026, SR 11-7 is rescinded)
- Model card / evidence ledger discipline
- Independent validation methodology
- Fairness at the decision output level (Regulation B / ECOA compliance awareness)
- Ability to challenge a model submitted by the development team

What they look for in candidates:
- Candidates who understand the difference between a model that is technically correct and one that is governance-ready
- Evidence of having produced artifacts that could survive an independent review
- Awareness of the adverse action code system (ECOA Regulation B requires specific reason codes for credit denials)

---

## 3. ROLE-TO-PROJECT ALIGNMENT TABLE

| Role Archetype | Primary Interview Axis | What PulseGuard Should Demonstrate for This Role |
|---------------|----------------------|--------------------------------------------------|
| Risk Data Scientist | Model quality + governance | Champion/challenger gates; calibration; PSI alerting; fairness; model card |
| Credit Data Scientist | Underwriting workflow + label handling | FOIR engine; APPROVE/REFER/REJECT routing; delayed label validation; reject inference awareness |
| Fraud Data Scientist | Model explainability + real-time pipeline | SHAP + business consequence; training-serving parity; graph signal awareness |
| ML Governance / MRM | Evidence chain + regulatory alignment | SR 26-2 alignment; evidence ledger; governance sign-off; model card with all artifacts |
| Decision Scientist | Policy-model coupling + business consequence | Policy version log; approval rate decomposition (model change vs. policy change); negative cost chain |
| Applied AI / MLOps | Pipeline reliability + monitoring | Training-serving parity; drift alerting; feature leakage gate; reproducibility |

---

## 4. WHAT AN INTERVIEWER AT STAFF LEVEL WILL PROBE

The following questions will be asked. If the candidate cannot answer at depth, they will not clear the bar.

**Q1: Walk me through the full lifecycle of your risk model — from data to governance decision.**
Expected depth: 7+ stages, each with artifacts. A candidate who stops at "I trained the model and deployed it" has failed.

**Q2: You have ROC AUC 0.77. How do you know your model makes good decisions?**
Expected answer: AUC measures discrimination — the model's ability to rank borrowers correctly. But decisions are made at a threshold. At that threshold, I need calibration: are probabilities > 0.28 associated with true default rates that justify rejection? I measure ECE and calibrate with Platt scaling. ECE 0.0046 confirms calibration quality at the decision boundary.

**Q3: Your model's approval rate dropped 5% in month 6. What happened?**
Expected answer: I need to separate three possible causes: (1) the model drifted — PSI alert should have caught this; (2) the decision threshold changed — policy version log should document this; (3) the population changed without the model drifting. I decompose these using the policy change log and the drift monitor. Without versioning both separately, this question is unanswerable.

**Q4: How did you handle the fact that you only trained on approved applicants?**
Expected answer: Selection bias / reject inference. I document it as a known limitation. In the full solution, I would use augmentation (assigning pseudo-outcomes to rejected applicants using a propensity-weighted model) or semi-supervised methods. In this portfolio version, I acknowledge it and quantify its impact on the expected calibration error at the marginal borrower boundary.

**Q5: Is your model fair?**
Expected answer: I measured Disparate Impact (F/M approval rate ratio = 1.059, within the 0.80–1.25 no-violation band) and Equal Opportunity gap (< 5pp). I checked SHAP ranks for proxy attributes — gender ranks #10 in SHAP importance. I did not declare the model "fair" — I declared it "no violation detected at these thresholds on this dataset." Fairness requires ongoing monitoring and context, not a one-time check.

**Q6: Your Optuna HPO produced a model with better AUC. Why didn't you deploy it?**
Expected answer: ECE regressed from 0.0046 to 0.0243 — a 5x calibration degradation. The decision policy engine converts probability scores to APPROVE/REVIEW/REJECT. An uncalibrated model means the threshold boundaries don't correspond to the actual risk levels they're supposed to represent. Better discrimination is not enough to justify deployment when calibration regresses. This is the governance judgment.

**Q7: What does a champion/challenger framework require beyond just comparing two models?**
Expected answer: Five things: (1) defined, pre-agreed promotion gates evaluated on a held-out test set before the comparison; (2) a statistical test for the AUC comparison (DeLong test, not just point estimate); (3) calibration gating; (4) fairness gating; (5) business case documentation. Without these, you have a model comparison, not a governance framework.

---

## 5. SENIOR VS. JUNIOR PORTFOLIO MARKERS

| Marker | Junior Portfolio | Senior / BeastMax Portfolio |
|--------|-----------------|----------------------------|
| Primary metric | AUC | AUC + ECE (calibration); PR AUC for imbalanced data |
| Feature validation | None or basic correlation check | 7-check leakage audit including temporal integrity (FAIL-level) |
| Drift | PSI computed, not acted on | PSI alert fires; escalation path documented; stop condition defined |
| Fairness | "Checked gender not in features" | Decision-output DI + EOpp + SHAP rank of proxies |
| Challenger | "LightGBM was worse, I kept XGBoost" | 5-gate promotion framework; DeLong test; ECE gate; documented rationale |
| Negative case | Missing | The model that was HELD is documented — most impressive artifact |
| Policy | "I used threshold 0.5" | Versioned decision policy with business rationale; policy-model decoupling |
| Governance | Missing | 15-artifact evidence ledger; model card; governance sign-off document |
| Reject inference | Missing | Acknowledged, quantified as limitation, roadmap item documented |
| Training-serving parity | "I deployed the model" | Parity test: batch scorer == API scorer within 1e-6 |
| Defense | "I can explain the code" | 30+ Q&A interview defense; knows when methods fail |

---

## 6. WHAT SETS THIS PROJECT APART FROM EVERY OTHER HOME CREDIT NOTEBOOK

The Home Credit Default Risk dataset (Kaggle) has thousands of public notebooks. The differentiation is not the dataset or the model. It is:

1. **The governance layer**: an evidence ledger, model card, and governance sign-off that make the project look like a document submitted to a model risk committee
2. **The negative case**: the Optuna HPO result that was held due to ECE regression — a governance judgment that demonstrates senior thinking
3. **The leakage gate**: a pre-training audit that runs before the first model is fit — treating data quality as a first-class engineering concern
4. **The policy-model decoupling**: showing that the approval rate is a function of both model and policy, and versioning them separately
5. **The reject inference acknowledgment**: demonstrating awareness of a production problem that Kaggle competitions suppress entirely (because Kaggle gives you full outcome labels for all rows)
6. **The regulatory alignment**: connecting every artifact to SR 26-2 governance requirements (not claiming compliance — claiming awareness and alignment)

These six things create a portfolio project that cannot be dismissed as a Kaggle re-run. They require domain understanding that only comes from research, first-principles reasoning, or production experience.
