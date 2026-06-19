# G9A — Interview Q&A Reference

**Gate:** G9A | Use for: interview preparation, recruiter screens, take-home presentations  
**Key constraint:** Every answer is grounded in work actually done. No inflation.

---

## Dataset & Feature Engineering

**Q: Walk me through your data pipeline.**

A: "I used the full Home Credit Default Risk dataset — 307,511 applicants with 7 side-tables totalling 57 million rows. The pipeline has two phases. First, I aggregate each side-table to SK_ID_CURR level: bureau_balance (27 million rows) gets aggregated to bureau account level for DPD ratios, then joined to bureau.csv for overdue ratios. Installments, credit card, and POS cash tables each become behavioural signal tables. Second, I join all 5 aggregated tables to application_train and engineer ratio features — FOIR proxy as annuity/income, DTI as credit/income, LTV as credit/goods price, plus a composite behavioural risk score weighting instalment lateness at 0.4, CC DPD at 0.3, POS DPD at 0.2, and bureau overdue at 0.1. The final matrix is 140 numeric features. Processing takes about 20 seconds on CPU."

**Q: Why fill NaN with 0 for behavioural features instead of the mean?**

A: "Because the NaN is informative — an applicant with no credit card history has no DPD record, so their CC_DPD_RATIO isn't unknown, it's effectively 0. Imputing the mean would introduce a false signal that they're average credit card users. For application-level fields where NaN is truly unknown, I let the tree models handle it natively."

**Q: What's FLAG_EMPLOYED_ANOMALY?**

A: "In Home Credit, DAYS_EMPLOYED has a sentinel value of 365243 — which is 1,000 years — indicating the applicant is unemployed or self-employed without a formal employer. Rather than letting that bleed into the EMPLOYED_YEARS ratio as garbage, I flagged it as a binary indicator and replaced the underlying value with NaN. That way the model sees both the fact of non-standard employment and the absence of employment duration as separate signals."

---

## Model Tournament

**Q: How did you pick the champion model?**

A: "I ran a full 12-model tournament — from logistic regression and LDA through random forest, extra trees, XGBoost, LightGBM, CatBoost, and MLP. Two models hard-failed: TabNet because CPU training on 184k rows would take 400–800 hours with no GPU available, and sklearn's GradientBoostingClassifier because it's single-threaded and exceeded our time limit even on a 50k subsample.

CatBoost won with AUC 0.7716. But I don't pick champion on AUC alone. I evaluated calibration via 10-bin expected calibration error — CatBoost's raw ECE was 0.32, terrible, because it outputs log-odds not probabilities. After Platt sigmoid calibration on the val set, ECE dropped to 0.0054, which is production-quality. KS stat is 0.41. So the champion is CatBoost plus Platt calibration."

**Q: Why not LightGBM if it's faster?**

A: "LightGBM came in at AUC 0.72 vs CatBoost's 0.77 on this dataset — a 5-point gap, which is meaningful in credit risk where every AUC point translates to economic value. However, I documented LightGBM with monotone constraints as the governance alternative. If model risk review requires directional interpretability under SR 26-2, you drop in LightGBM-Monotonic with its 15 constrained features — you trade 5 AUC points for full directional compliance. That's a documented, explicit tradeoff, not a guess."

**Q: What's a monotone constraint and why does it matter?**

A: "A monotone constraint tells the model that as a feature increases, the prediction must only increase (or only decrease). For example, INST_LATE_RATIO — the fraction of instalments paid late — must be constrained to be monotonically risk-increasing. Without constraints, a GBM could theoretically learn a non-monotonic relationship that fits the training data but violates the credit risk directional expectation. Regulators under SR 26-2 care about this because it makes the model more auditable: you can tell a model risk reviewer 'as this applicant's late payment rate goes up, their default probability always goes up' with mathematical certainty."

---

## Calibration

**Q: What is ECE and why does it matter for credit scoring?**

A: "ECE is Expected Calibration Error — you bin the predicted probabilities into 10 buckets and compare the average predicted probability in each bucket to the actual default rate. A perfectly calibrated model has ECE of zero. In credit scoring it matters because we use the probability output for pricing — the expected loss on a 10% PD applicant drives the risk premium. If the model says 10% but the actual rate for that score range is 25%, you're significantly under-provisioning."

**Q: How did you calibrate?**

A: "Platt sigmoid calibration. I fit a logistic regression on one input — the raw model probability — and the validation labels. Then I apply that sigmoid transformation to the test set scores. CatBoost went from ECE=0.32 to ECE=0.0054 post-calibration. The AUC is preserved because calibration is a monotone transformation — it doesn't change the ranking, just the scale."

---

## Governance & LLM Layer

**Q: Tell me about the LM Studio layer.**

A: "We added a local LM Studio governance assistant that runs a small LLM — Mistral-7B or Llama-3-8B — fully offline. It has two functions. First, policy Q&A: analysts query the credit policy corpus using BM25 retrieval, and the LLM generates a grounded, cited answer. If the retrieval score is below threshold, the system abstains rather than hallucinating. Second, adverse action drafting: given SHAP-derived adverse factors, the LLM drafts an adverse action notice in plain language, which a human then reviews before sending.

The design is ASSISTIVE_ONLY — it cannot approve, decline, or score applications. We chose BM25 over vector search because credit policy is keyword-rich and precise: 'What is the FOIR threshold?' benefits from exact term matching, not semantic similarity. And we chose local LM Studio because credit applications contain PII — you can't send that to OpenAI."

---

## Known Limitations (Say These Proactively)

**Q: What are the limitations of your model?**

A: "Three main ones I want to be upfront about. First, reject inference: the dataset only contains approved applicants, so the model has no signal on declined applications. This is a classic MNAR selection bias — we don't know if the people we rejected would have defaulted or not. A proper reject inference implementation would require semi-supervised or counterfactual methods.

Second, no temporal validation: Home Credit doesn't provide absolute timestamps, so we couldn't do an out-of-time holdout. We used stratified random splitting. In production, I'd implement PSI-based monitoring to catch vintage drift.

Third, single geography: the model was trained on Home Credit's Eastern European and Asian portfolio. Income levels, credit bureau structure, and default patterns may differ significantly from US or UK lending. I wouldn't claim this generalises directly."

---

*G9A Example — Interview Q&A | Part of PulseGuard.*
