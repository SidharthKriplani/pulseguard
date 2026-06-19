# G0 — GOLD RESEARCH DOSSIER
## PulseGuard · First-Principles Industry Research
### Written from scratch — component projects intentionally set aside for this phase

---

## 1. THE REAL INDUSTRY PROBLEM

### What is actually breaking in production?

Risk ML systems in financial services fail in a specific and non-random pattern. The failure is almost never "the model is inaccurate." It is almost always one of the following:

**Failure 1 — Silent drift with no detection infrastructure.**
A credit default model trained in Q1 deploys in Q4. By Q2 of the following year, the population has shifted — income distribution changed, bureau score composition changed, macroeconomic stress has redistributed risk — but the model is still scoring. PSI eventually hits 0.3. Nobody noticed at 0.2. There was no alert threshold defined, or the alert fired and nobody escalated it.

**Failure 2 — Calibration at the wrong layer.**
The model has ROC AUC 0.78. The business celebrates. But the probability outputs are not calibrated against the actual decision threshold. A model can discriminate perfectly (perfect ROC AUC) and still systematically approve too many bad borrowers or reject too many good ones because the probability-to-decision mapping assumes the probabilities mean something they do not. This is why ECE (Expected Calibration Error) at the decision threshold matters more than ROC AUC in credit.

**Failure 3 — Feature leakage inflates validation AUC.**
A post-outcome flag — "payment_received_flag," "bureau_update_after_decision" — is included in training. Validation AUC is 0.91. Production AUC is 0.64. The model never learned credit risk; it learned that payment confirmation predicts itself. This is one of the most common causes of model re-deployment at 6-month mark.

**Failure 4 — Selection bias and reject inference.**
Credit models are trained only on *approved* applicants whose outcomes are observed. Rejected applicants have no outcome labels because they were never given loans. The training population is systematically different from the full applicant pool. Without reject inference, the model has never learned the risk profile of the marginal borrower — the population it most needs to score correctly. Almost every naive portfolio project ignores this completely.

**Failure 5 — No policy-model version decoupling.**
A threshold tightening at month 12 reduces the approval rate from 30% to 15%. Is this because the model degraded? Or because the policy changed? Without separate versioning of the model and the decision policy, this question is unanswerable. Post-hoc, finance teams blame the model; risk teams blame the market. Nobody knows who is right. This causes months of misdirected remediation work.

**Failure 6 — Proxy bias in features.**
Gender is excluded. Race is excluded. Zip code is included. Zip code correlates with race at 0.73. The model discriminates on a proxy. The fairness audit checked the feature list, not the decision output. The CFPB (August 2024) has stated explicitly that algorithmic tools using proxies can violate disparate impact standards just as direct discrimination would.

**Failure 7 — No champion/challenger governance.**
The incumbent model runs for 3 years. A better candidate exists but nobody built a framework to compare them. When the challenger is finally evaluated, the teams disagree on what "better" means — one team uses ROC AUC, another uses business metrics, a third uses calibration. The absence of pre-defined promotion gates means the promotion decision becomes political.

**Failure 8 — No audit trail.**
Regulatory inquiry arrives. The risk committee asks: "On what date did you change the decision threshold? What was the model version at that time? What was the approval rate the week before and after? Was a fairness check run?" The answer is: buried in spreadsheets, if at all. Without a governance evidence ledger, these questions take weeks to answer — if they can be answered at all.

### Why does this matter more now than before?

In April 2026, the Federal Reserve, FDIC, and OCC issued SR 26-2 — the Revised Interagency Guidance on Model Risk Management — replacing the 15-year-old SR 11-7 framework. The new guidance explicitly:

- Requires the complete model lifecycle (development → validation → deployment → monitoring → retirement) to be a **governed chain, not snapshots at handoff**
- Ties ongoing monitoring to changing conditions: products, exposures, clients, data relevance, market dynamics — not just to scheduled annual reviews
- Requires champion/challenger and benchmarking to be "versioned and reproducible — not a one-time memo"
- Explicitly keeps traditional ML in scope (generative AI is excluded from SR 26-2 scope as "novel and rapidly evolving" — traditional ML remains fully in scope)
- References: [Databricks SR 26-2 Guide](https://www.databricks.com/blog/model-risk-management-2026-bankers-guide-revised-interagency-guidance), [FDIC SR 26-2 Announcement](https://www.fdic.gov/news/financial-institution-letters/2026/agencies-revise-interagency-model-risk-management-guidance), [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html)

This means: **the problem PulseGuard is solving has just gotten a regulatory upgrade**. Any bank with over $30B in assets is now expected to demonstrate governed model lifecycles with traceable lineage.

---

## 2. WHO OWNS THIS PROBLEM IN COMPANIES

The problem sits at the intersection of four teams. The power structure matters for product positioning.

| Role | What They Own | What Breaks for Them | What They Need from PulseGuard |
|------|-------------|---------------------|-------------------------------|
| **Credit/Risk Data Scientist** | Model training, feature engineering, calibration, HPO, validation | Model miscalibration, leaky features, drift without alert | Leakage audit, calibration report, drift monitor, champion/challenger |
| **ML/Decision Scientist** | Decision policy, threshold setting, approval rate management, downstream metric ownership | Policy-model version confusion, approval rate unexplained changes | Policy version log, policy-consequence chain, audit trail |
| **Fraud Data Scientist** | Real-time and batch fraud detection, rule engines, ensemble fraud scores | Rule-model coupling, training-serving skew, latency vs. accuracy tradeoff | Training-serving parity, model registry, feature consistency check |
| **ML Governance / Model Risk** | Model inventory, independent validation, SR 26-2 compliance, model cards | No evidence artifacts, no audit trail, no champion/challenger docs | Evidence ledger, governance sign-off, model card, promotion decision docs |
| **Applied AI / MLOps Engineer** | Feature pipelines, serving, retraining triggers, monitoring infrastructure | Silent failures in batch scoring, feature drift, pipeline failures | Drift alerting, parity check, batch monitoring, observability |

The governance/MRM role is the **buyer** — the one who approves or blocks deployment. The risk DS is the **builder** who must produce the evidence the MRM team requires. PulseGuard speaks to both: it is a build tool for the DS and an evidence generator for the governance layer.

---

## 3. WHAT STRONG COMPANIES EXPECT FROM A CANDIDATE/PROJECT

### The Intuit Staff AI Scientist Signal (direct JD evidence)

Intuit's Staff Fraud AI Scientist JD (Consumer Risk, 2025) requires candidates to demonstrate:
- "Full model lifecycle ownership" — not just training, but calibration, monitoring, maintenance, and defense
- "Fraud score calibration, label bias correction, case disposition logic" — three things a naive portfolio project will not have
- "Network or graph-based link analysis" — graph risk signals
- "Deep understanding of fraud risk modeling concepts" — not just gradient boosting
- 5+ years in credit risk modeling, decision science, or quantitative analytics within a bank, fintech, or consumer lender
- Source: [Intuit Staff Fraud AI Scientist JD](https://jobs.intuit.com/job/mountain-view/staff-fraud-ai-scientist-fintech-consumer-risk/27595/87369449712)

### What "full model lifecycle" means in a FAANG-tier interview

A senior interviewer asking "walk me through your model" expects the answer to cover:
1. Feature validity (leakage audit, temporal integrity)
2. Training methodology (train/val/test split discipline, no data leakage across folds)
3. Calibration (not just AUC — ECE, Brier, calibration curve at the decision threshold)
4. Selection bias handling (reject inference or acknowledgment of its absence)
5. Drift detection (what fires when, at what threshold, who gets alerted)
6. Fairness (at the decision output level, not just the feature list)
7. Policy-model version decoupling (model v1.0 vs. policy v1.1)
8. Governance evidence (what artifacts exist to prove the model was validated)
9. Failure mode reasoning (what happens when the model fails silently)

A candidate who can only answer items 1, 3, and 7 will be flagged as mid-level.

### What Uber/Airbnb/Netflix build at scale

- **Uber Michelangelo**: Handles 10,000 features, 1,000 models, 200 petabytes of feature data, 10 million feature requests per second. Batch jobs run hourly to monitor prediction drift. Source: [Uber Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- **Airbnb**: Published "Architecting a Machine Learning System for Risk" — covers exactly the model monitoring and governance architecture PulseGuard is simulating. Source: [Airbnb Engineering](https://medium.com/airbnb-engineering/architecting-a-machine-learning-system-for-risk-941abbba5a60)
- **LinkedIn (Feathr)**: A feature store for productive ML that enforces point-in-time correctness — the exact temporal leakage prevention that FeatureLeakageLens checks for.

---

## 4. WHAT JDs REPEATEDLY ASK FOR

Pattern analysis across risk DS, fraud DS, credit DS, and ML governance JDs at FAANG/fintech (2024-2025):

| Skill Cluster | Frequency | What This Means for PulseGuard |
|--------------|-----------|-------------------------------|
| Full model lifecycle ownership | Very High | Must show training → validation → monitoring → retirement chain |
| Champion/challenger framework | High | Must have formal promotion gates, not just "we compared two models" |
| Calibration (Platt, ECE, Brier) | High | Must show calibration at the decision threshold, not just AUC |
| PSI / distribution drift | High | Must show alerting, not just computation |
| SHAP / feature explainability | High | Must connect SHAP to business consequence and regulatory use |
| Fairness audit (DI, TPR parity) | Medium-High | Must show decision-output fairness, not just feature fairness |
| Feature store / point-in-time | Medium | Must acknowledge temporal leakage risk, show prevention |
| Policy versioning | Medium | Rarely built in portfolios; highly valued at senior level |
| Delayed label handling | Medium | Shows understanding of credit-specific production realities |
| Reject inference | Medium | Almost never in portfolios; highly valued at fintech credit roles |
| Training-serving parity | Medium | Must show the same pipeline is used for training and serving |
| Graph-based risk signals | Lower | Valued at fraud-heavy roles; good differentiator |
| Model card / governance docs | Lower (but growing) | SR 26-2 is making this standard |

---

## 5. WHAT MATURE COMPANIES ACTUALLY SOLVE IN THIS DOMAIN

### Tier 1 capabilities (every bank with $30B+ assets now required by SR 26-2):
- Model inventory with tiering (Tier 1/2/3 by materiality)
- Pre-deployment validation (conceptual soundness + outcome analysis)
- Champion/challenger with reproducible, versioned comparison
- Ongoing monitoring with defined alert thresholds
- Annual review cycle with documented governance sign-off

### Tier 2 capabilities (what leading fintechs actually build):
- Feature stores with point-in-time correctness (Feast, Tecton, Hopsworks, Feathr)
- Automated drift alerting with escalation paths (Evidently AI, WhyLabs, Fiddler, Arize)
- Online A/B testing of model variants in shadow mode
- Calibration regression CI gates — ECE computed on every training run; deployment blocked if regressed beyond threshold
- Reject inference via augmentation or semi-supervised methods
- Real-time explainability at the decision endpoint (/explain endpoint with SHAP)
- Automated adverse action code generation (ECOA/Regulation B compliance)

### Tier 3 capabilities (advanced / research-grade):
- Counterfactual fairness testing
- Causal feature importance (not just correlational SHAP)
- Graph contagion risk signals for network fraud
- Dynamic policy optimization (RL-based threshold adaptation)
- Federated model validation across institutions

---

## 6. FAILURE MODES THAT CAUSE REAL BUSINESS DAMAGE

| Failure Mode | Business Consequence | Detection Method |
|-------------|---------------------|-----------------|
| Feature leakage | Model with AUC 0.91 collapses to 0.64 in production; months of wrong decisions; reputational damage | FeatureLeakageLens / temporal audit |
| Silent drift | Approval rates miscalibrated for months; credit loss exceeds model prediction | PSI > 0.20 alert |
| Calibration collapse | Too many approvals at wrong threshold; credit loss spike; too many rejections; revenue loss | ECE monitoring; calibration curve at decision boundary |
| Selection bias | Model systematically underestimates risk of marginal borrowers; default rate higher than predicted | Reject inference audit; outcome tracking by approval tier |
| Proxy bias | Regulatory action; CFPB enforcement; litigation under disparate impact theory | Decision-output fairness audit (not feature-level) |
| No policy version log | Cannot attribute approval rate changes to model vs. policy; remediation misdirected | Policy change log with timestamped version history |
| Missing governance evidence | SR 26-2 audit fails; model cannot be deployed; remediation takes months | Evidence ledger; model card; governance sign-off |

Reference: [Hidden Technical Debt in ML Systems](https://papers.neurips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf) — Sculley et al. (Google, NeurIPS 2015) identifies boundary erosion, entanglement, hidden feedback loops, and undeclared consumers as systemic production ML risks.

---

## 7. COMMON NAIVE PORTFOLIO-PROJECT VERSIONS OF THIS PROBLEM

These are the patterns that signal "junior" to a senior interviewer:

1. **"I trained XGBoost on the Home Credit dataset and got AUC 0.78."** No calibration, no drift, no fairness, no governance. This is a Kaggle notebook, not a risk platform.

2. **"I built a credit scoring model with SHAP explainability."** SHAP without calibration is decoration. SHAP without fairness analysis is incomplete. SHAP without connecting to business consequence is impressive-sounding but shallow.

3. **"I deployed the model to FastAPI."** Serving is not governance. A served model with no drift monitoring, no calibration check, and no policy version log is a black box with a REST endpoint.

4. **"I compared XGBoost and LightGBM — XGBoost was better."** Without formal promotion gates, this is not champion/challenger. It is a model comparison notebook.

5. **"I added PSI monitoring."** Computing PSI is not the same as building a monitoring system. Does the alert fire? Who receives it? What is the escalation path? Is the threshold justified?

6. **"I added fairness metrics."** Computing Disparate Impact on the training set is not a fairness audit. Did you check the decision output? Did you check SHAP ranks of proxies? Did you check calibration by group?

7. **"I used Optuna for hyperparameter optimization and got better AUC."** This misses the ECE regression case — the most interesting governance finding in the entire RiskFrame portfolio. A senior candidate knows when better discrimination does not justify deployment.

---

## 8. WHAT MAKES A PROJECT SENIOR/STAFF-LEVEL

A senior/staff-level project demonstrates four things that a junior project does not:

**A — First-principles problem framing:** The candidate understands why the problem exists in production, not just how to solve it in a notebook. They can explain the selection bias problem, the policy-model decoupling problem, and the regulatory evidence problem without being asked.

**B — Negative cases documented:** The most impressive artifact in RiskFrame is not the model that got deployed — it is the model that got HELD. The Optuna HPO result that improved AUC but regressed ECE, and was therefore held, demonstrates governance judgment. A senior candidate has evidence of what they decided NOT to do and why.

**C — Business consequence chain:** Every technique is connected to a dollar consequence. PSI alert fires → what happens to the approval rate? → what happens to credit loss? → what is the remediation path? Calibration failure → how many approvals were wrong? → what is the estimated dollar loss?

**D — Interview defensibility at depth:** A senior candidate can answer follow-up questions at three levels of depth:
- Level 1: What it does ("PSI measures distribution shift")
- Level 2: Why this method ("PSI is industry standard in credit; KS is feature-level; I use both")
- Level 3: When it fails ("PSI misses multivariate shift — two features can each individually stay stable while their joint distribution shifts significantly")

---

## 9. THE MISSING LAYER: REJECT INFERENCE

This is the problem that almost no portfolio project addresses and that separates a sophisticated credit ML practitioner from a general ML practitioner.

**The problem:** A credit model is trained only on approved applicants (those who were given loans) because only they have observed outcomes. Rejected applicants were never given loans, so we never observed whether they would have defaulted. But the model needs to score the marginal borrower — someone who might have been rejected or approved depending on the policy. The training distribution systematically under-represents high-risk borrowers.

**Why it matters for interview:** A senior interviewer at Intuit, Affirm, or any lending-focused company will ask this. The correct answer demonstrates understanding of survivorship bias in credit. The naive answer ("I used cross-validation") misses the point entirely.

**What PulseGuard should do:** Acknowledge reject inference as a known limitation, document it in the model card as a boundary condition, and propose the augmentation approach (assigning pseudo-outcomes to rejected applicants using a propensity-weighted model). Implementing full reject inference is deferred — but understanding it and documenting it is evidence of senior thinking.

---

## 10. KEY CITATIONS

- [SR 26-2 — FDIC (April 2026)](https://www.fdic.gov/news/financial-institution-letters/2026/agencies-revise-interagency-model-risk-management-guidance)
- [Databricks Guide to SR 26-2](https://www.databricks.com/blog/model-risk-management-2026-bankers-guide-revised-interagency-guidance)
- [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html)
- [Hidden Technical Debt in ML Systems — Sculley et al., NeurIPS 2015](https://papers.neurips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf)
- [Airbnb: Architecting a ML System for Risk](https://medium.com/airbnb-engineering/architecting-a-machine-learning-system-for-risk-941abbba5a60)
- [Uber Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- [Intuit Staff Fraud AI Scientist JD](https://jobs.intuit.com/job/mountain-view/staff-fraud-ai-scientist-fintech-consumer-risk/27595/87369449712)
- [Intuit Senior Credit Risk AI Scientist JD](https://jobs.intuit.com/job/mountain-view/senior-credit-risk-ai-scientist-fintech-consumer-risk/27595/89706909120)
- [The Fairness of Credit Scoring Models — arxiv](https://arxiv.org/pdf/2205.10200)
- [Evaluating AI Fairness with BRIO — arxiv 2024](https://arxiv.org/pdf/2406.03292)
- [Evidently AI vs. Arize vs. Fiddler comparison](https://medium.com/@tanish.kandivlikar1412/comprehensive-comparison-of-ml-model-monitoring-tools-evidently-ai-alibi-detect-nannyml-a016d7dd8219)
- [SoK: Machine Learning Governance — arxiv](https://arxiv.org/pdf/2109.10870)

**New citations added after GitHub/blog research (June 2026):**
- [Nubank Engineering Blog — 9 Tips for ML Model Monitoring](https://building.nubank.com/ml-model-monitoring-9-tips-from-the-trenches/) — Policy/Decision Layer monitoring; percentile monitoring over averages; subpopulation monitoring; meta-monitoring for batch jobs
- [Nubank Engineering Blog — Real-time ML adversarial robustness (March 2025)](https://building.nubank.com/making-real-time-ml-models-more-robust-in-adversarial-scenarios-practical-tips-monitoring/) — Decision approval rate monitoring for adversarial detection; segmentation-first monitoring strategy
- [Nubank Engineering Blog — Feature stores for real-time ML (June 2026)](https://building.nubank.com/feature-stores-for-real-time-ml-why-and-when-to-centralize-feature-logic/) — Point-in-time correctness; centralized feature logic for real-time models
- [Stripe Engineering Blog — ML for payment slice monitoring (Jan 2025)](https://stripe.com/blog/using-ml-to-detect-and-respond-to-performance-degradations-in-slices-of-stripe-payments) — Production confirmation that aggregate metrics mask segment-level degradation; ML-estimated expected baseline; >90% precision
- [DataRobot — MLOps Champion/Challenger for Banks (webinar)](https://www.datarobot.com/webinars/mlops-and-challenger-models-for-banks/) — Shadow mode champion/challenger as first-class MRM requirement for financial institutions
- [SAIL: Graph-based Semi-supervised Reject Inference (Annals of Operations Research, 2025)](https://link.springer.com/article/10.1007/s10479-025-06621-9) — Divide and conquer reject inference; distribution mismatch as core challenge; XGB/LightGBM/SVM/MLP evaluation
- [SAIL GitHub Implementation](https://github.com/yzkang/graph-based-semi-supervised-reject-inference-framework) — Code for G9 reject inference roadmap
- [JakobLS/mlops-credit-risk (GitHub)](https://github.com/JakobLS/mlops-credit-risk) — Portfolio benchmark: PSI monitoring on credit risk; no champion/challenger or governance layer
