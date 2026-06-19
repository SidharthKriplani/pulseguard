# G0 — TECHNIQUE TOURNAMENT
## PulseGuard · Every Method Earns Its Place or Gets Cut

**Rule:** Every technique listed here must connect to a product decision. This is not a museum of methods. Each entry answers: what decision does this technique enable, what is the business consequence of getting it wrong, and should it be built now, later, or rejected?

---

## TECHNIQUE 1: PSI (Population Stability Index) — Drift Detection

**Problem it solves:** Detects when the feature distribution of incoming applicants has shifted away from the training distribution, indicating the model is scoring an out-of-distribution population.

**Why it belongs:**
PSI is the industry standard in credit scoring for distribution monitoring. It maps directly to SR 26-2 monitoring requirements. It is what a risk DS at any bank will ask about. Threshold bands (< 0.10 stable, 0.10–0.20 WARN, > 0.20 ALERT) are used across NBFC, credit card, and mortgage lending.

**Assumptions:**
- PSI treats each feature independently — it is a univariate measure
- PSI computes distribution shift against a reference window (training distribution or a recent stable window)
- PSI is sensitive to bin choice — coarser binning = less sensitive; finer binning = noisier

**Why it may not belong:**
PSI misses multivariate shift. Two features can each individually remain stable (PSI < 0.10) while their joint distribution shifts significantly. A model that depends on the interaction of those two features can degrade silently while PSI looks fine. This is a known failure mode that must be documented.

**Alternatives:**
- KS test (Kolmogorov-Smirnov): non-parametric, compares CDFs rather than bin counts. Better for detecting distributional shifts at the tails. Use alongside PSI.
- Wasserstein distance (Earth Mover's Distance): captures the geometry of the shift, not just the magnitude. More robust for heavy-tailed distributions. Deferred to G9.
- MMD (Maximum Mean Discrepancy): handles multivariate shift. Deferred.
- Model-based drift detection (predict "is this new data from training distribution?"): most powerful, most expensive. Deferred.

**Failure modes:**
- PSI fires but model performance is unchanged → false alarm; alert fatigue
- PSI stable but model performance degrades → multivariate shift; PSI blindspot
- PSI computed against wrong reference (recent window instead of training) → misleading WARN/ALERT

**Business tradeoff:**
PSI alert has a cost: every ALERT requires a DS review (time), and may pause batch scoring (revenue impact). False alerts are expensive. Setting threshold too low → alert fatigue → alerts ignored. Setting threshold too high → silent degradation → credit losses.

**Evidence to prove it worked:** PSI > 0.20 fires on Day 14 synthetic drift injection. `drift_fire_test.py` passes.

**Evidence that kills it:** PSI fires on Day 14 but feature performance analysis shows model's Gini coefficient is unchanged → PSI was wrong signal; need multivariate check.

**Industry validation (added after GitHub/blog research):**
- **Stripe (Jan 2025):** "One approach to monitoring payment performance would be tracking aggregate performance across all payments on our platform. While this would give us a comprehensive overview, it would likely obscure degradations affecting specific segments of traffic." Stripe monitors 16,000+ payment dimensions and confirmed that aggregate drift metrics miss segment-level degradations at production scale.
- **Nubank (2024):** "There may be a problem that affects your data in severe ways but the average values for the features may not move at all." Nubank prescribes percentile monitoring (1st, 5th, 10th, 90th, 95th, 99th) as a supplement to mean-based PSI.

**G4 enhancement (added after research — low-cost):**
1. **Percentile-level feature monitoring:** Compute per-feature percentile snapshots (1st, 10th, 90th, 99th) alongside PSI. Log in `outputs/evidence/drift_percentile_report.json`. Validates tail shift that aggregate PSI bins can miss.
2. **Subpopulation PSI (one slice):** Compute PSI separately for AMT_CREDIT quartile split (high/low credit amount). Report: "Aggregate PSI stable; high-risk segment PSI WARN." Demonstrates subpopulation awareness consistent with Nubank and Stripe production patterns.

**Decision: BUILD NOW (G4).**

---

## TECHNIQUE 2: KS Test — Per-Feature Distribution Check

**Problem it solves:** Per-feature distribution comparison between reference and current populations. Non-parametric, sensitive to tail differences.

**Why it belongs:** KS identifies which specific features are drifting, enabling targeted remediation (re-engineer a specific feature vs. full retraining).

**Assumptions:** Continuous features. For categorical, use Chi-squared or TVD (Total Variation Distance).

**Why it may not belong:** KS is also univariate. Does not capture feature-feature correlations.

**Alternatives:** PSI (already built); Jensen-Shannon divergence; Chi-squared for categorical features.

**Decision: BUILD NOW (G4) — alongside PSI.**

---

## TECHNIQUE 3: Platt Calibration — Model Calibration

**Problem it solves:** XGBoost raw probability outputs are not calibrated. They can be systematically too high or too low relative to actual default rates. Platt scaling fits a logistic regression on top of raw scores (on the validation set) to produce calibrated probabilities.

**Why it belongs:**
The decision policy engine converts probabilities to decisions at thresholds (score < 0.06 = APPROVE). If probabilities are miscalibrated, the threshold boundaries do not correspond to actual risk levels. A model with perfect AUC and miscalibrated probabilities produces systematically wrong approval rates. Calibration is not optional in a threshold-based decision system.

**Why Platt specifically (not isotonic):**
Platt scaling assumes the uncalibrated scores are linearly related to log-odds. This is a reasonable assumption for well-trained tree ensembles. Isotonic regression is more flexible (piecewise monotone function, no shape assumption) but overfits on small calibration sets. For Home Credit's large validation set, either works — Platt is simpler and produces smoother calibration curves.

**When Platt fails:**
Platt assumes the score-to-probability relationship is sigmoid-shaped. If the underlying model's output distribution is bimodal or has heavy tails, Platt calibration will not capture the shape correctly. Isotonic regression or temperature scaling would be needed.

**Evidence of success:** ECE < 0.01 on the test set (achieved: 0.0046 for champion XGBoost). Calibration curve plots show actual vs. predicted default rate per decile.

**Evidence it fails:** ECE > 0.01 after Platt calibration → switch to isotonic regression; re-evaluate.

**The ECE regression case (most important negative finding in the portfolio):**
Optuna HPO produced xgb_v2 with better AUC (0.2654 vs 0.2611). Platt calibration on xgb_v2 produced ECE 0.0243 — 5x worse than champion. **This is the most important finding in the entire portfolio.** It demonstrates that better discrimination does not imply deployment fitness. xgb_v2 was held.

**Decision: BUILD NOW (G3/G4) — ECE regression case is a MUST-HAVE evidence artifact.**

---

## TECHNIQUE 4: SHAP (SHapley Additive exPlanations) — Feature Attribution

**Problem it solves:** Explains individual model predictions by attributing the prediction to input features proportionally. Enables adverse action code generation (ECOA Regulation B), proxy bias detection, and model debugging.

**Why it belongs:**
SHAP is the standard explainability method in production credit risk. It satisfies the "right to explanation" for adverse action notice requirements under Regulation B. A SHAP beeswarm plot is the primary tool for detecting whether a protected attribute or its proxy is a dominant driver.

**Assumptions:**
SHAP for tree models (TreeExplainer) uses the conditional expectation of the model's output, not marginal expectation. This means SHAP values are model-consistent but may not reflect data-generating process causal structure.

**When SHAP is insufficient:**
- SHAP does not detect causal relationships. A feature with high SHAP importance may be a mediator, confounder, or proxy — not a causal driver.
- SHAP values computed on test data do not reflect what would happen if the feature were changed in production (interventional fairness).
- SHAP interactions between features require TreeExplainer SHAP interaction values — more expensive but more informative.

**Alternatives:**
- LIME: local, model-agnostic. Less consistent than SHAP, more suitable for non-tree models.
- Permutation importance: global, model-agnostic. Biased toward high-cardinality features. Simpler than SHAP.
- Integrated Gradients: for neural networks. Not applicable here.
- Causal importance (intervention-based): gold standard but computationally expensive. Deferred.

**Business tradeoff:**
Online SHAP (at inference time, per request) adds 50-200ms latency. For a credit decision that takes 4-8 hours in the manual process, this is negligible. For real-time fraud detection (< 100ms requirement), SHAP must be pre-computed or approximated.

**Evidence of success:** SHAP beeswarm plot produced. Top feature is EXT_SOURCE_2 (mean |SHAP| = 0.35). CODE_GENDER_F rank ≥ #10 (mean |SHAP| = 0.08). SHAP rank confirms gender is not a primary driver.

**Decision: BUILD NOW (G5) — required for fairness audit and adverse action rationale.**

---

## TECHNIQUE 5: Disparate Impact + Equal Opportunity — Fairness Metrics

**Problem it solves:** Detects whether the model's decisions disproportionately favor or disadvantage protected groups at the output level (not the feature level).

**Why it belongs:**
The CFPB stated explicitly (August 2024): "there are no exceptions to the federal consumer financial protection laws for new technologies." Courts have held that disparate impact theory of liability applies to algorithmic credit decisions. Measuring fairness at the decision output — not just the feature list — is the standard that regulators apply.

**Disparate Impact:**
DI = (approval rate for group A) / (approval rate for group B). The "4/5 rule" from EEOC: DI < 0.80 or > 1.25 signals potential disparate impact. This is the threshold used in US consumer credit regulation.

**Equal Opportunity (True Positive Rate parity):**
Measures whether creditworthy applicants in different groups are approved at equal rates. A model that passes DI can still fail EOpp — it can have the same overall approval rate but systematically misclassify creditworthy applicants in one group. These are complementary metrics.

**The proxy problem (critical):**
Excluding gender from the feature set does not guarantee fairness. Zip code, employment type, or income source can correlate with gender at > 0.70. Fairness must be measured at the decision output, not the feature list. The SHAP rank check of proxy features is the mechanism that catches this.

**When these metrics conflict:**
Demographic parity (equal approval rates regardless of creditworthiness) conflicts with Equal Opportunity (approve equally creditworthy applicants regardless of group). You cannot simultaneously maximize both if the underlying credit risk differs by group. This is known as the impossibility theorem of fairness. A senior candidate knows this and can articulate the tradeoff.

**Alternatives:**
- Demographic parity: same approval rate across groups. Stronger but may deny approval to qualified borrowers in one group.
- Calibration by group: does the model's predicted probability match observed default rate within each group? Stronger than DI for regulatory use.
- Counterfactual fairness: would the decision have been different if the applicant belonged to a different group, holding all else equal? Most rigorous but computationally expensive. Deferred.

**Evidence of success:** DI within 0.80–1.25 = no violation. EOpp gap < 5pp = no violation. SHAP rank of gender proxy ≥ #10.

**Evidence it fails:** DI < 0.80 = potential disparate impact → escalate; document as finding; propose remediation.

**Decision: BUILD NOW (G5). Calibration by group deferred to G9.**

---

## TECHNIQUE 6: Champion / Challenger Framework — Model Promotion Governance

**Problem it solves:** Provides a formal, pre-defined, reproducible process for deciding whether a new model (challenger) is superior enough to replace the current model (champion) in production.

**Why it belongs:**
SR 26-2 explicitly requires champion/challenger and benchmarking to be "versioned and reproducible." Without a formal framework, model replacement is a political negotiation. With a framework, it is a governance decision with evidence.

**The 5-Gate Promotion Framework:**
1. **PR AUC delta ≥ 0.001**: Challenger must be meaningfully better at discrimination (not just noise)
2. **ROC AUC delta ≥ 0.001**: Consistent improvement on the secondary metric
3. **ECE gate**: Challenger ECE must not exceed champion ECE by > 0.005
4. **DeLong test p < 0.05**: Statistical significance — performance difference must not be attributable to sampling variation
5. **Fairness gate**: DI must remain within 0.80–1.25 for the challenger

**Why pre-defined gates matter:**
If gates are defined after the comparison ("let's see what the challenger looks like and decide"), the comparison is biased by knowing the result. Gates must be defined before training begins. This is the governance discipline.

**Alternatives:**
- Shadow deployment (online A/B test): routes a percentage of live traffic to the challenger and compares real outcomes. Gold standard in production. Cannot be replicated in portfolio — requires real users.
- Bandit testing: Thompson sampling / UCB to dynamically allocate traffic to the better model. Deferred.
- Simulated A/B test on historical data: possible in portfolio; requires careful hold-out design.

**Decision: BUILD NOW (G6).**

---

## TECHNIQUE 7: Optuna HPO — Bayesian Hyperparameter Optimization

**Why it belongs:**
The most important finding from HPO is not the best model — it is the held model. xgb_v2 achieves better AUC but worse ECE. This is a governance finding that demonstrates senior judgment. The HPO process is not about finding the globally optimal model; it is about exploring the Pareto frontier of discrimination vs. calibration and making a principled deployment decision.

**Why 50 trials, not 500:**
Diminishing returns. After 30-50 trials with TPE (Tree-structured Parzen Estimator), the search has explored the high-value region of the hyperparameter space. 500 trials at similar computation cost would find marginal improvements. The correct question is not "more trials" but "do the additional trials change the deployment decision?" In this case: no. Champion is retained regardless.

**What should be logged for each trial:** PR AUC (val), ROC AUC (val), ECE (val), decision (PASS/HOLD), rationale.

**Decision: BUILD NOW (G6) — 50-trial TPE, ECE regression case is the key artifact.**

---

## TECHNIQUE 8: Platt Calibration vs. Isotonic Regression vs. Temperature Scaling

**The tradeoff in depth:**
- **Platt scaling**: Parametric sigmoid. Works well for well-trained tree ensembles on large val sets. Produces smooth calibration curves. Our choice for champion.
- **Isotonic regression**: Non-parametric, piecewise constant. More flexible, overfits on small val sets. Better for recalibration over time (shown in research for credit scoring time series).
- **Temperature scaling**: Scales the logit by a single parameter T. Works for neural networks with softmax outputs. Not applicable to XGBoost directly.

**Research finding:** For credit scoring treated as time series, isotonic regression with periodic recalibration outperforms Platt scaling over the long run. Source: arxiv 2509.23665. **Implication for PulseGuard:** At G9, consider isotonic recalibration as the ongoing recalibration method; use Platt for initial deployment calibration.

**Decision: BUILD PLATT NOW (G4); isotonic recalibration at G9.**

---

## TECHNIQUE 9: Feature Leakage Detection (7-Check Audit)

**The 7 checks and their business justification:**

| Check | Tier | Business Consequence if Missed |
|-------|------|-------------------------------|
| Post-outcome name heuristic | Name/Structure | Fast catch of obvious leaks (payment_received_flag) |
| ID/proxy scan | Name/Structure | Catches columns that are essentially applicant IDs disguised as features |
| Target correlation scan | Statistical | Catches features that are near-perfect predictors (AUC inflater) |
| Categorical proxy scan | Statistical | Catches categorical features with near-perfect target rate stratification |
| Split distribution scan | Statistical | Catches distribution differences between train and test sets |
| Temporal availability | Temporal | **FAIL-level**: feature timestamp > outcome timestamp → post-outcome feature |
| Training future date scan | Temporal | **FAIL-level**: feature contains dates beyond training cutoff → future data in training |

Only temporal checks produce FAIL (block training). All others produce WARN (document and proceed).

**Why WARN ≠ FAIL for statistical checks:**
A high target correlation could be a legitimate strong predictor. A domain expert must confirm whether the feature was available at prediction time. The tool flags; the human confirms. This boundary is documented explicitly ("truth boundary") in the FeatureLeakageLens output.

**What is missing from the 7 checks (known gaps):**
- Group leakage: same entity (e.g., SK_ID_CURR) appearing in both train and test sets. This is entity-level data contamination.
- Mutual information scan: catches non-linear proxy features that pass the linear target correlation check.
- Walk-forward split validator: confirms that time-series splits respect temporal ordering.
These are roadmap items documented in FeatureLeakageLens README. Deferred to G9.

**Decision: BUILD NOW (G3) — all 7 checks on Home Credit features.**

---

## TECHNIQUE 10: FOIR Engine — Deterministic Credit Policy Enforcement

**Why deterministic first:**
FOIR (Fixed Obligation to Income Ratio) must not be computed by an LLM or inferred by a model. It is a regulatory ratio with legal implications. An error in FOIR computation can produce a HARD_REJECT on a qualified applicant or an APPROVE on an ineligible one. The correct pattern is: compute deterministically from raw income and EMI figures; never trust the figure provided in the application.

**Why FOIR matters for PulseGuard:**
It demonstrates the principle that not everything in a risk decision system should be an ML problem. Hard rules exist for good reasons: they are predictable, auditable, and regulatorily defensible. The governance value of a hard rule is that it cannot hallucinate.

**Business consequence of getting it wrong:**
FOIR miscalculation → APPROVE on an applicant with debt-to-income > 0.65 → higher default probability → credit loss → regulatory exposure.

**Decision: BUILD NOW (G7) — FOIR engine as pure Python deterministic module.**

---

## TECHNIQUE 11: Hybrid RAG for Credit Policy Lookup

**Problem it solves:** LendFlow demonstrated that relevant credit policy clauses (RBI FOIR guidance, LTV caps, income floor definitions) can be retrieved from a corpus using hybrid BM25 + dense retrieval + cross-encoder reranking, achieving RAGAS faithfulness 0.91.

**Why it belongs in PulseGuard:**
A governance decision requires policy citations. "APPROVED under FOIR policy" is insufficient. "APPROVED — FOIR 0.43, within RBI-aligned threshold of 0.50 (Source: NBFC Policy Circular §4.2)" is audit-ready. The RAG layer converts vague policy references to specific, retrievable citations.

**Why it might not belong in MVP:**
RAG requires: (1) a policy corpus, (2) embedding infrastructure, (3) a cross-encoder, (4) evaluation (RAGAS). This is a 1-2 week build. The value-add for G7 MVP is marginal if the policy rules are hardcoded correctly. The value-add for T3/Gold is high — it demonstrates a production-pattern for policy compliance.

**Alternatives:**
- Hardcoded policy rules: simpler, faster, less flexible. Appropriate for MVP.
- LLM with hardcoded policy text in context: no retrieval, no faithfulness guarantee. Appropriate for prototype only.
- Hybrid RAG: production-pattern. Appropriate for Gold.

**Decision: DEFERRED to G7+ — hardcoded rules for MVP; RAG for Gold.**

---

## TECHNIQUE 12: Reject Inference

**Why it belongs:**
Every credit model trained on approved applicants has selection bias. The training population is a non-random sample of all applicants — it excludes those who were rejected (precisely the highest-risk applicants). Without reject inference, the model has not learned the risk profile of the marginal borrower.

**Why it may not belong in the build:**
Reject inference requires either: (1) a separate model trained on the full population using proxy labels, or (2) semi-supervised learning using augmented pseudo-outcomes, or (3) weight adjustment using propensity scores. All three require careful implementation and validation. The portfolio implementation risk is high (easy to implement incorrectly and claim the problem is solved when it isn't).

**What PulseGuard should do:**
1. Document reject inference as a known boundary condition in the model card
2. Quantify the expected calibration impact: "Because we only observe outcomes for approved applicants, our ECE estimate is conditional on approval. The true ECE on the full applicant pool is unknown and likely worse."
3. Propose the augmentation approach as a roadmap item
4. Do NOT claim reject inference is implemented unless it is

**Decision: DEFERRED to G9 — documented as known limitation NOW; implement later if feasible.**

---

## TECHNIQUE 13: Policy Version Log

**What it is:** A machine-readable log of every change to the decision policy (approval thresholds, capacity limits, FOIR cutoffs), with timestamp, delta, rationale, and authorized_by.

**Why it is non-obvious:** Most portfolio projects version the model. Almost none version the decision policy separately. But in production, the approval rate is a function of BOTH the model AND the policy threshold. Without separate versioning, you cannot decompose an approval rate change into "model degraded" vs. "policy tightened."

**Business consequence:** Month-end approval rate drops 5%. Finance team blames the risk model. Risk team says policy changed. Without the policy version log, this takes weeks to investigate. With the log, it takes seconds.

**Decision: BUILD NOW (G7) — small implementation, very high interview value.**

---

## TECHNIQUE 14: Delayed Label Validation

**What it is:** Credit outcomes (default / no default) are only observable 6-12 months after the credit decision. This means the model's performance cannot be directly validated on recent predictions. Delayed label validation simulates this by: comparing predicted default rates (by score decile) against observed bad rates at the end of the observation window.

**Why it belongs:**
Most portfolio projects use a static test set and claim high performance. In production, you must monitor performance as labels arrive — and they arrive late. Delayed label validation is the bridge between the training-time AUC claim and the production-time performance reality.

**What it requires:**
- A score log: predicted scores for each applicant (synthetic in portfolio)
- An outcome log: observed default/no-default at 12 months (synthetic in portfolio)
- Rank-order preservation check: do higher-score applicants default more often? (Gini coefficient / KS statistic on the outcome data)
- Bad rate by bucket vs. predicted probability: does score decile 10 have 10x the bad rate of score decile 1?

**Decision: BUILD NOW (G7/G8) — synthetic labels with controlled bad rate distribution.**

---

## TECHNIQUE 15: Decision-Layer Monitoring (Nubank Production Pattern)

**What it is:** A named monitoring concept — distinct from model-technical monitoring (PSI, AUC, ECE) — that tracks the *decisions* produced by the model+policy system. Specifically: approval rate by day, decision count by routing bucket (APPROVE/REVIEW/REJECT), and approval rate change attribution (model drift vs. policy change).

**Industry source:** Nubank Engineering Blog — "9 Tips for Machine Learning Model Monitoring" explicitly separates "Policy/Decision Layer monitoring" from model-technical monitoring.
> "It isn't enough to monitor models from a technical perspective because this doesn't make it clear to other stakeholders how the business is being impacted. Monitor how many people got loans approved by the risk model on each day."

**Why it belongs:**
PSI detects input distribution shift. AUC detects discrimination degradation. Neither tells a business stakeholder how many loans got approved today vs. last week, or whether an approval rate drop was caused by the model or by a policy change. These are different questions that require different metrics.

**What PulseGuard implements:**
The `scripts/approval_rate_decomposition.py` module (G7) implements decision-layer monitoring. It attributes approval rate changes to:
1. Model signal (PSI trend → score distribution shift)
2. Policy version (policy_change_log.json → threshold delta)

**Why it matters in interviews:**
> "Most teams monitor their models technically (PSI, AUC) but not their decisions. Nubank explicitly identifies 'Policy/Decision Layer monitoring' as a separate concern. PulseGuard's approval rate decomposition module is the direct implementation of this: it separates model degradation from policy decisions in the approval rate signal."

**Decision: NAMED CONCEPT (already built as approval_rate_decomposition at G7) — rename and document explicitly as "decision-layer monitoring."**

---

## TECHNIQUE TOURNAMENT SUMMARY

| Technique | Decision | Gate | Rationale |
|-----------|---------|------|-----------|
| PSI drift | BUILD NOW | G4 | Industry standard; SR 26-2; Stripe + Nubank production validation |
| PSI percentile monitoring | BUILD NOW | G4 | Nubank pattern; tail shifts invisible to mean-based PSI |
| PSI subpopulation slice | BUILD NOW | G4 | Nubank + Stripe pattern; aggregate PSI hides segment drift |
| Decision-layer monitoring | BUILD NOW | G7 | Nubank "Policy/Decision Layer" concept; implemented as approval_rate_decomposition |
| KS test | BUILD NOW | G4 | Per-feature complement to PSI |
| Platt calibration | BUILD NOW | G3/G4 | Required for threshold-based decision policy |
| ECE + calibration curve | BUILD NOW | G3/G4 | ECE regression case is the key evidence artifact |
| SHAP | BUILD NOW | G5 | Adverse action rationale; proxy bias detection |
| Disparate Impact + EOpp | BUILD NOW | G5 | Decision-output fairness; regulatory alignment |
| Champion/challenger 5-gate | BUILD NOW | G6 | SR 26-2 requirement; governance evidence |
| Optuna HPO | BUILD NOW | G6 | ECE regression case is the key negative finding |
| FeatureLeakageLens 7 checks | BUILD NOW | G3 | Pre-training gate; temporal integrity FAIL detection |
| FOIR engine | BUILD NOW | G7 | Deterministic policy; audit-ready |
| Policy version log | BUILD NOW | G7 | Approval rate decomposition; governance |
| Delayed label validation | BUILD NOW | G7/G8 | Production realism; label delay awareness |
| Hybrid RAG (policy lookup) | DEFERRED G7+ | G7 | MVP uses hardcoded rules; RAG for Gold |
| Reject inference | DEFERRED G9 | G9 | SAIL paper (2025) + GitHub repo provides concrete implementation path |
| Calibration by group | DEFERRED G9 | G9 | Fairness depth; after G5 baseline |
| Isotonic recalibration | DEFERRED G9 | G9 | Ongoing recalibration; after initial deployment |
| Counterfactual fairness | DEFERRED G9 | G9 | Research-grade; after baseline fairness |
| Wasserstein drift | DEFERRED G9 | G9 | Multivariate drift; after PSI baseline |
| Graph contagion risk | DEFERRED G9 | G9 | NexusSupply integration; not core to credit |
| Bandit / online A/B | REJECTED | — | Requires live traffic; not portfolio-replicable |
| LLM for numeric decisions | REJECTED | — | Violates deterministic-first principle |
