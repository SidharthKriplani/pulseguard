# G9A — Safe vs Forbidden Claim Examples

**Gate:** G9A | Purpose: Claim boundary reference for resume, interviews, portfolio  
**Rule:** Every claim must be traceable to a file, metric, or code artifact in this repo.

---

## Resume Line Examples

### ✅ SAFE Resume Lines

```
• Built end-to-end credit risk ML pipeline on Home Credit Default Risk dataset
  (307k applicants, 8.07% DR, 7 side-tables, 57M rows total)

• Engineered 50+ features across 7 relational tables including payment behaviour
  ratios (FOIR proxy, DTI proxy, LTV proxy) and BEHAVIORAL_RISK_SCORE composite

• Ran 12-model tournament (LR → RF → XGBoost → CatBoost → LightGBM) on 140
  features; champion CatBoost achieves AUC=0.7716, ECE=0.0054 post-Platt calibration,
  KS=0.41 on 61k held-out test set

• Implemented Platt sigmoid calibration; reduced CatBoost ECE from 0.32 to 0.005

• Applied monotone constraints to 15 features on LightGBM governance alternative
  (SR 26-2 compliant directional interpretability); documented as drop-in replacement

• Built local LM Studio governance assistant (Mistral-7B, offline, BM25 policy RAG)
  for policy Q&A and adverse action drafting — ASSISTIVE_ONLY, no data egress

• Hard-failed TabNet with documented evidence: CPU training ~400-800h at 6min/epoch
  vs ~15s/epoch on GPU; torch.cuda.is_available()=False

• Documented known limitations: reject inference (approved-applicant MNAR bias),
  no temporal holdout (no timestamps), single-geography portfolio
```

### ❌ FORBIDDEN Resume Lines

```
✗ "AUC of 0.85 on credit risk model"
  → Our champion achieves 0.7716. Do not inflate.

✗ "Production-deployed credit scoring model"
  → This is a portfolio project, not a production system.

✗ "Validated on out-of-time test set"
  → No temporal holdout exists. We used stratified random splitting.

✗ "Reject inference implemented"
  → Documented as known limitation. Not implemented.

✗ "Fair across protected classes"
  → Fairness audit not in G9A scope.

✗ "Model complies with SR 26-2"
  → SR 26-2 compliance requires independent model validation team, not self-assessment.

✗ "LightGBM outperforms CatBoost on AUC"
  → False. CatBoost 0.7716 > LightGBM 0.7203.
```

---

## Interview Claim Examples

### ✅ SAFE Interview Claims

| Claim | Evidence |
|---|---|
| "The dataset has 307,511 applicants with 8.07% default rate" | `g9a_home_credit_data_audit.json` |
| "bureau_balance has 27.3M rows — that's 359MB CSV" | Shell `wc -l` confirmed |
| "CatBoost AUC=0.7716 on 61k test set" | `g9a_model_tournament_report.json` |
| "ECE dropped from 0.32 to 0.0054 with Platt calibration" | `g9a_calibration_governance_report.json` |
| "Top SHAP feature is EXT_SOURCE_3" | `g9a_shap_summary.json` + plot |
| "LightGBM with 15 monotone constraints as governance alternative" | Code in `scripts/g9a_model_tournament.py` |
| "TabNet hard-failed: 6min/epoch on CPU vs 15s on GPU" | Code comment + tournament report |
| "stratified 60/20/20 split, seed=42, DR preserved at 0.0807" | `g9a_splits.pkl` verified |
| "BM25 retrieval with abstain threshold 0.5" | `src/pulseguard/policy_rag.py` |

### ❌ FORBIDDEN Interview Claims

| Claim | Why Forbidden |
|---|---|
| "AUC > 0.80" | Champion is 0.7716 |
| "Out-of-time holdout" | No timestamps; stratified random split only |
| "Reject inference implemented" | Documented as limitation, not implemented |
| "Model is production-ready" | No independent validation, no fairness audit |
| "LLM makes credit decisions" | ASSISTIVE_ONLY by design |
| "This is better than Taiwan Default model" | Different datasets; not apples-to-apples |
| "TabNet would have scored lower than CatBoost" | We don't have TabNet results — we can't claim it |

---

## Portfolio Writeup Examples

### ✅ SAFE Portfolio Description

> "PulseGuard is a credit risk intelligence portfolio project built on the Home Credit Default Risk dataset (307k applicants, 57M total rows across 7 tables). The pipeline engineers 140 features from multi-table relational data, runs a 12-model tournament with calibration, and wraps the champion model in a local LM Studio governance assistant for policy-grounded decision support.
> 
> Champion model: CatBoost + Platt calibration (AUC=0.7716, ECE=0.0054, KS=0.41). Governance alternative: LightGBM with monotone constraints (15 features) for SR 26-2 aligned deployment. Known limitations documented: approved-applicant selection bias, no temporal holdout, single-geography dataset."

### ❌ FORBIDDEN Portfolio Description

> "Built a production-grade credit scoring model achieving 85% AUC, validated on real-world applicant data across multiple geographies, with full compliance with SR 26-2 model risk management standards."

---

---

## Gold Pass 2 — Safe vs Forbidden Claim Examples

### ✅ SAFE Resume Lines (after Pass 2)

```
• Ran validation-only Optuna hyperparameter tuning across 5 GBM variants (CatBoost,
  XGBoost, LightGBM, monotonic variants); selected champion by 9-component composite
  score including ECE, KS, explainability, and adverse-reason readiness — not AUC alone

• Tuned LightGBM_monotonic champion: AUC=0.7769 on held-out test, ECE=0.0034
  after Platt calibration — +0.0053 AUC and +0.0047 KS vs untuned G9A baseline

• Identified LightGBM early-stopping bug on imbalanced data (scale_pos_weight +
  eval_metric='auc' causes early stop at iteration 1); fixed via fixed n_estimators as
  Optuna hyperparameter — improved AUC from 0.7203 baseline to 0.7734 tuned

• Champion is simultaneously performance champion and governance champion:
  LightGBM_monotonic with 15 directional constraints aligns with SR 26-2 model
  interpretability requirements and supports ECOA adverse action reason generation
```

### ❌ FORBIDDEN Resume Lines (after Pass 2)

```
• "Improved model AUC to 0.7716 through Optuna tuning"   ← that was the UNTUNED baseline
• "CatBoost champion tuned to AUC=0.77"                   ← champion is now LightGBM, not CatBoost
• "100 Optuna trials per model"                           ← actual: 4–8 trials (CPU budget)
• "Isotonic calibration achieves ECE=0.0034"              ← Platt is the calibrator; isotonic overfits val
```

### ✅ SAFE Interview Answers (Pass 2)

| Question | Safe Answer |
|---|---|
| "What model did you end up with after tuning?" | "LightGBM with monotone constraints on 15 features. It was actually weaker than CatBoost in the G9A untuned baseline because LightGBM has a known early-stopping bug on imbalanced data — early stopping fires at iteration 1 when you combine scale_pos_weight with eval_metric='auc'. Once I fixed that and ran Optuna properly, LightGBM_monotonic leads at AUC=0.7734 val and 0.7769 test. The baseline tournament underrepresented LightGBM." |
| "How did you select the champion?" | "9-component composite score: AUC (25%), PR-AUC (15%), KS (15%), Brier (10%), ECE (10%), calibration slope (5%), latency (5%), explainability — SHAP plus monotone constraints (10%), and adverse-reason readiness (5%). LightGBM_monotonic scores 0.7312 composite vs. XGBoost_monotonic at 0.7294. The explainability component is the tiebreaker — monotone constraints add 0.5 points that non-monotonic models don't get." |
| "Did you use the test set during tuning?" | "No. The test set was physically isolated throughout. Optuna optimized on validation AUC. The champion was selected by composite score on validation metrics. The calibrator was fit on validation probabilities. The test set was evaluated exactly once, after all decisions were locked — single evaluation, result: AUC=0.7769." |
| "Why is LightGBM_monotonic also the governance champion?" | "In SR 26-2 aligned model risk management, directional interpretability matters. A monotone constraint says 'higher BUREAU_OVERDUE_RATIO always increases predicted default probability' — you can defend that to an auditor or regulator without needing to explain SHAP. When performance champion and governance champion are the same model, there's no trade-off to defend." |

### ❌ FORBIDDEN Interview Claims (Pass 2)

- "The model is now production-ready" — Pass 2 addresses performance and calibration; fairness audit, SHAP update, and adverse action reason mapping remain for Pass 3
- "AUC=0.7769 beats the industry benchmark" — no industry benchmark specified; claim is undefended
- "Isotonic is the calibrator" — Isotonic is fit for completeness only; Platt is the selected calibrator
- "CatBoost was rejected" — CatBoost is a contender (val_AUC=0.7708); LightGBM_mono won the composite comparison, not a rejection
- "I ran 100 Optuna trials" — actual budget was 4–8 trials per model; be honest about the constraint

---

---

## Gold Pass 3 — Safe vs Forbidden Claim Examples

### ✅ SAFE Resume Lines (after Pass 3)

```
• Designed score-band decisioning policy (GREEN/AMBER/RED) from calibrated PD scores:
  GREEN<0.20 (89.7% of 61k test applicants, 5.8% DR), AMBER 0.20–0.40 (9.8%, 27% DR),
  RED≥0.40 (0.5%, 54% DR) — semantically justified PD thresholds, not arbitrary cutoffs

• Computed SHAP reason codes via LightGBM pred_contrib; EXT_SOURCE_MEAN dominant driver
  (mean |SHAP|=0.51, rank-1 in all 30 bootstrap resamples); top-5 features stable 30/30

• Built BM25 RAG + LLM governance assistant for adverse action drafting (ASSISTIVE_ONLY):
  6-case demo covering approve/review/decline/conflict/abstain/drift-alert; abstain fires
  on out-of-domain queries; LLM never autonomously approves or rejects applicants

• Conducted fairness proxy audit on age, income, employment, region; approval-rate
  differentials aligned with observed default-rate differentials (no amplification
  beyond base rates); documented as governance skeleton — not a fairness certification

• Delivered complete governance artifact: model card + governance report + evidence
  ledger traceable to every metric claim (7 evidence JSONs, model card, governance report)
```

### ❌ FORBIDDEN Resume Lines (after Pass 3)

```
• "Model is fair / disparate impact compliant"  ← skeleton proxy audit only; no protected-class labels
• "Legally compliant adverse action notices generated"  ← drafts require credit officer sign-off
• "PSI=8.1 drift detected on training data"  ← Platt calibration artefact, not drift
• "Cost-optimal threshold t=0.47 from real bank economics"  ← scenario assumptions, not bank data
• "LLM handles credit decisions"  ← LLM is ASSISTIVE_ONLY; human officer decides
• "SR 26-2 certified"  ← aligned, not certified; certification requires external validator
```

### ✅ SAFE Interview Answers (Pass 3)

| Question | Safe Answer |
|---|---|
| "How did you set your score-band thresholds?" | "PD=0.20 as the GREEN/AMBER boundary has a semantic interpretation: the calibrated model estimates a 20% default probability at that boundary. The GREEN band (PD<0.20) has an observed default rate of 5.77% — materially below 20%, confirming the model is conservative in GREEN assignment. I chose this over the KS-optimal single threshold (0.096) because the KS threshold would classify 50% of applicants as approve, which is operationally aggressive and doesn't leave a useful review zone." |
| "What did SHAP tell you?" | "EXT_SOURCE_MEAN dominates by a large margin — mean absolute SHAP contribution of 0.51, about 3.6× the next feature (CREDIT_TO_ANNUITY at 0.14). It's rank-1 in all 30 bootstrap resamples across 500-sample draws. This tells me that whatever external credit bureau data underlies EXT_SOURCE_MEAN is the primary risk signal in this dataset. For an adverse action draft, EXT_SOURCE_MEAN translates to 'External credit bureau composite score below threshold' — which a credit officer can verify against the bureau report." |
| "How does your LLM governance assistant work?" | "It's a BM25 policy retriever over a 5-document corpus. The user query is scored against policy docs. If the top BM25 score is below 0.25, the assistant abstains — it won't hallucinate a policy citation for out-of-domain queries. Above that threshold, it retrieves the most relevant policy section and drafts a memo. All outputs are tagged ASSISTIVE_ONLY and HUMAN_REVIEW_REQUIRED. The LLM never makes a final credit decision — it drafts language for the credit officer to review and sign." |
| "What are your model's limitations?" | "Five main ones. First, reject inference: model trained on approved applicants only — declined applicant outcomes are unobserved. Second, no temporal holdout: no timestamps in Home Credit so I can't do out-of-time validation. Third, single geography: Eastern European portfolio, untested elsewhere. Fourth, trial count: only 4–8 Optuna trials due to CPU constraints. Fifth, fairness: no protected-class labels so I can only do proxy analysis, not compute a disparate impact ratio. All documented in the model card." |

### ❌ FORBIDDEN Interview Claims (Pass 3)

- "The model is production-ready after Pass 3" — Pass 3 delivers governance artifacts; no independent validation, no regulatory review
- "Adverse action reasons are compliant with Regulation B" — drafts are ASSISTIVE_ONLY; compliance requires legal review and credit officer sign-off
- "PSI confirms no drift" — val-vs-test PSI=0.0002 confirms stability within a static snapshot split; not a production drift guarantee
- "Fairness analysis clears the model for fair lending" — proxy-only audit; protected-class labels not available; full fair-lending review requires demographic data and legal counsel
- "Cost threshold t=0.47 is the recommended operational threshold" — computed under scenario economics (C_bad=10, C_reject=1) not real bank parameters; operational threshold requires actual charge-off and funding cost data

---

*G9A + Gold Pass 2 + Gold Pass 3 Safe Claim Reference | PulseGuard | 2026-06-17*
