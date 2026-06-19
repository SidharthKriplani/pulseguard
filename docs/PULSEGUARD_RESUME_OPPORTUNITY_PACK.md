# PulseGuard — Resume & Opportunity Pack

**Version:** Gold Pass 4/4 | **Date:** 2026-06-17  
**Use:** Copy-paste ready content for resume, LinkedIn, cover letters, and spoken pitches.

> All metrics are sourced from `outputs/evidence/gold_pass2_final_untouched_test_report.json` and the Gold Audit.  
> Safe claims only — forbidden claims documented in `06_CLAIM_BOUNDARY.md`.

---

## 1. Resume Bullets (5 — Pick by Role)

### Bullet A — General ML / Data Science

> **PulseGuard Credit-Risk Governance Portfolio** | Python, LightGBM, Optuna, SHAP, BM25  
> Built end-to-end credit-risk ML pipeline on Home Credit Default Risk dataset (307k applicants, 57.4M rows, 7 relational tables). Engineered 140 features; ran 12-model baseline tournament + Optuna-tuned 5-model search; champion LightGBM with monotone constraints achieves **AUC=0.7769, KS=0.41, ECE=0.0034** on 61k held-out test. Champion selected by 9-component composite score (AUC, PR-AUC, KS, Brier, ECE, latency, explainability, adverse-reason readiness) — not AUC alone. Delivered full governance artifact stack: model card, evidence ledger, score-band policy, SHAP reason codes, fairness proxy audit, drift baseline, and BM25+LLM governance assistant. Project scored **89.3% (GOLD) on 15-dimension governance audit**.

---

### Bullet B — Credit Risk / Financial Services Focused

> **PulseGuard Credit-Risk Governance Portfolio** | LightGBM, Platt Calibration, SHAP, BM25  
> Designed governed ML credit-risk pipeline: 140 features across 7 tables (bureau aggregates, instalment ratios, DPD composites, FOIR/LTV/DTI proxies); champion LightGBM with 15 monotone directional constraints (SR 26-2 aligned) achieves AUC=0.7769, ECE=0.0034 post-Platt. Built 3-band score policy (GREEN<0.20: DR=5.8%; AMBER 0.20–0.40: DR=27%; RED≥0.40: DR=54%). SHAP reason codes stable across 30 bootstrap resamples (EXT_SOURCE_MEAN rank-1 30/30). Fairness proxy audit — no approval-rate amplification beyond base-rate differentials. Local BM25 policy RAG: adverse-action memo drafting, ASSISTIVE_ONLY hard constraint, OOD abstain verified.

---

### Bullet C — MLOps / Governance Focused

> **PulseGuard Credit-Risk ML Governance Stack** | LightGBM, Optuna, SHAP, reportlab  
> Delivered production-pattern ML lifecycle for regulated lending context: leakage audit (10/10 PASS, safe_to_tune=true) → validation-only Optuna HPO (TPE, 4–8 trials, val-only objective) → Platt calibration (ECE 0.296→0.0034) → 9-component composite champion selection → score-band policy → SHAP bootstrap stability (30/30 top-5, 30/30 rank-1) → fairness proxy audit → PSI drift baseline (val-vs-test PSI=0.0002) → model card + evidence ledger + claim boundary. All 15-dimension governance audit dimensions documented; project scored GOLD at 89.3%.

---

### Bullet D — GenAI / LLM Engineering Focused

> **PulseGuard RAG/LLM Governance Assistant** | BM25, Python, local LLM  
> Built local policy retrieval-augmented generation layer for credit decisioning governance: BM25 over 5-document policy corpus; abstain threshold (BM25<0.25) prevents hallucinated citations; 6-case demo — GREEN approve, AMBER review, RED decline, conflict override, OOD abstain, drift escalation. All LLM outputs ASSISTIVE_ONLY + HUMAN_REVIEW_REQUIRED + NOT_FINAL_DECISION; LLM never generates approve/reject in any case. Design enforces SR 26-2 human-accountability model risk management principle.

---

### Bullet E — Short Version (LinkedIn, tight resume space)

> **PulseGuard** — credit-risk governance portfolio · LightGBM + Platt · AUC=0.7769, ECE=0.0034 · 140 features across 7 relational tables (57M rows) · SHAP reason codes, score-band policy, fairness proxy audit, BM25+LLM governance demo · GOLD at 89.3% on 15-dimension governance audit

---

## 2. LinkedIn Bullets (3)

### LinkedIn Bullet 1 — Project Feature Post

> 🏛️ **PulseGuard** — just shipped Gold Pass 4/4 (project freeze)
>
> End-to-end credit-risk governance ML on Home Credit Default Risk: 307k applicants, 57M rows, 7 tables.
>
> What I built:
> ▸ 140 engineered features (bureau aggregates, instalment ratios, DPD composites)
> ▸ 12-model baseline tournament + Optuna-tuned final 5 models
> ▸ Champion: LightGBM + Platt — AUC 0.7769, KS 0.41, ECE 0.003
> ▸ Selected by 9-component composite (calibration + explainability weighted in)
> ▸ Score-band policy: GREEN/AMBER/RED with PD-semantic thresholds
> ▸ SHAP reason codes, stable 30/30 bootstrap resamples
> ▸ Local BM25 policy RAG — ASSISTIVE_ONLY, abstain on OOD
> ▸ Full model card, evidence ledger, claim boundary
>
> GOLD checkpointed at 89.3% on 15-dimension governance audit.
>
> Not a production system — a demonstration of governed ML lifecycle. Every claim has an artifact.

---

### LinkedIn Bullet 2 — Methodology Insight Post

> Most credit risk projects show you a confusion matrix and call it done.
>
> PulseGuard asked: what if you governed it properly?
>
> ▸ Pre-tuning leakage audit (10/10 PASS) before any model training
> ▸ Monotone constraints on 15 features — directional interpretability without SHAP
> ▸ Platt calibration: ECE 0.296 → 0.003 (raw GBM score ≠ probability)
> ▸ SHAP bootstrapped 30 times — EXT_SOURCE_MEAN stable as rank-1 in all 30 runs
> ▸ Score-band policy derived from PD semantics, not arbitrary percentiles
> ▸ LLM governance assistant with hard ASSISTIVE_ONLY constraint
>
> A model is only as defensible as its documentation.

---

### LinkedIn Bullet 3 — Short Credential Post

> Built PulseGuard: end-to-end credit-risk governance stack (Home Credit, 307k applicants).
>
> Champion: LightGBM + Platt · AUC=0.7769 · ECE=0.0034 · KS=0.41
>
> Governance: SHAP reason codes (30-bootstrap stable) · fairness proxy audit · PSI drift baseline · BM25+LLM policy assistant (ASSISTIVE_ONLY)
>
> Gold audit: 89.3% · 15 dimensions · GOLD
>
> Full model card + evidence ledger + claim boundary docs included.

---

## 3. Interview One-Liners (3)

### One-Liner A — High-level (used after "tell me about yourself")

> "PulseGuard is my credit-risk governance portfolio — tuned LightGBM on 307,000 Home Credit applicants, AUC 0.7769, ECE 0.003, selected by a 9-component composite including calibration and explainability, with a full governance stack: SHAP reason codes, score bands, fairness proxy audit, and a local LLM governance assistant that drafts adverse-action memos for credit officer review."

---

### One-Liner B — Role-contextualised (model risk / regulatory)

> "I built a governed credit-risk ML pipeline with an explicit leakage audit, validation-only Optuna HPO, Platt calibration to ECE=0.003, monotone constraints for SR 26-2 directional interpretability, SHAP reason codes bootstrapped for stability, a fairness proxy audit skeleton, and PSI drift monitoring — all documented in a model card with a claim boundary that distinguishes what I implemented from what I haven't."

---

### One-Liner C — GenAI angle (LLM / RAG roles)

> "On the governance side of PulseGuard, I built a local BM25 retrieval-augmented policy assistant: it retrieves the relevant credit policy section, drafts an adverse-action memo using an LLM, and hard-enforces an ASSISTIVE_ONLY rule — the LLM never makes a credit decision, it only drafts language for the credit officer to review and sign off."

---

## 4. Spoken Answers

### 60-Second Pitch

> "PulseGuard is my credit-risk governance portfolio project built on the Home Credit Default Risk dataset — 307,000 applicants, 57 million rows across 7 relational tables. I engineered 140 features, ran a 12-model baseline tournament, then tuned 5 models with Optuna hyperparameter search on the validation set only.
>
> The champion is LightGBM with monotone constraints — meaning the model is guaranteed to be directionally interpretable without needing SHAP. Post-Platt calibration, I get ECE=0.003 on the test set, which means the predicted probabilities are very close to actual default rates.
>
> The governance layer is the main contribution: score-band policy, SHAP reason codes that are stable across 30 bootstrap resamples, a fairness proxy audit, a PSI drift baseline, and a local policy RAG assistant that drafts adverse-action memos — ASSISTIVE_ONLY, the LLM never decides.
>
> Every metric in the resume has an artifact in the evidence ledger. Every limitation is documented in the model card. The project scored GOLD at 89.3% on a 15-dimension governance audit."

---

### 2-Minute Deep Dive

> "I'll walk you through the four layers: data, model, governance, and boundaries.
>
> **Data.** Home Credit Default Risk — 307,000 applicants at 8% default rate, 7 relational tables including bureau history, instalment payments, credit cards, and POS cash records. I engineered 140 features: ratio features like credit-to-annuity and loan-to-goods-value, behavioural aggregates like late-payment ratio and bureau overdue ratio, a composite behavioral risk score, and employment anomaly flags. I ran a 10-check leakage audit before any training.
>
> **Model.** 12 baseline models, 2 hard-failed with documented cause. Optuna hyperparameter search on 5 finalists — validation-only, test set never touched. Champion is LightGBM with monotone constraints on 15 features. Post-Platt calibration: AUC=0.7769, KS=0.41, ECE=0.0034 on 61,000-row holdout. Selected by a 9-component composite — not AUC alone.
>
> **Governance.** Score-band policy with PD-semantic thresholds — GREEN below 0.20, AMBER 0.20 to 0.40, RED above 0.40. SHAP reason codes derived from LightGBM's native pred_contrib, bootstrapped 30 times — EXT_SOURCE_MEAN is rank-1 in all 30 runs. Fairness proxy audit on 4 proxy groups — approval-rate gaps align with default-rate differentials. PSI val-vs-test is 0.0002. Local policy RAG: BM25 retriever, 6-case demo, abstain on out-of-domain, LLM output always ASSISTIVE_ONLY.
>
> **Boundaries.** This is a portfolio project on public data. Documented limitations: reject inference not implemented, no temporal holdout possible (no timestamps), CPU trial count was 4 to 8 not 100, fairness is proxy-only. Everything I claim is traceable to an artifact. Everything I don't claim is documented in the model card and claim boundary."

---

## 5. What Not to Say

| Forbidden Statement | Why | Safe Alternative |
|---|---|---|
| "I built a production credit scoring model" | It's a portfolio project | "Credit-risk governance portfolio project on public data" |
| "AUC=0.7769 exceeds industry benchmarks" | No benchmark cited; claim undefended | "AUC=0.7769 on 61k held-out test" |
| "The model is fair" | No protected-class labels; proxy audit only | "Proxy audit shows no amplification beyond base-rate differentials" |
| "I validated on out-of-time data" | No timestamps in Home Credit; random split only | "No temporal holdout possible; documented as limitation" |
| "I ran 100 Optuna trials" | Actual: 4–8 per model (CPU constraint) | "4–8 Optuna trials per model; CPU sandbox constraint" |
| "CatBoost champion at AUC=0.7716" | CatBoost is the G9A BASELINE, not the final champion | "LightGBM_monotonic champion, tuned AUC=0.7769" |
| "Isotonic calibration" | Platt is the selected calibrator; isotonic overfits val | "Platt sigmoid, ECE=0.0034 on test" |
| "The LLM generates credit decisions" | ASSISTIVE_ONLY by design | "LLM drafts memos; officer decides" |
| "SR 26-2 compliant" | Compliance requires external validation team | "SR 26-2 aligned design; not certified" |
| "Reject inference implemented" | Not implemented; documented as limitation | "Reject inference deferred; approved-applicant selection bias documented" |

---

## 6. SQL / Python Relevance Notes

### SQL Pattern Awareness

PulseGuard does not use SQL directly (raw CSV ingestion via pandas), but the multi-table join logic maps 1:1 to SQL:

```sql
-- What feature engineering does in SQL terms
SELECT
    a.SK_ID_CURR,
    a.AMT_CREDIT / NULLIF(a.AMT_INCOME_TOTAL, 0) AS CREDIT_TO_INCOME,
    a.AMT_ANNUITY / NULLIF(a.AMT_INCOME_TOTAL, 0) AS ANNUITY_TO_INCOME,
    COUNT(b.SK_ID_BUREAU) AS BUREAU_ACTIVE_COUNT,
    AVG(CASE WHEN b.CREDIT_ACTIVE = 'Active' AND b.AMT_CREDIT_SUM_OVERDUE > 0 THEN 1 ELSE 0 END) AS BUREAU_OVERDUE_RATIO
FROM application_train a
LEFT JOIN bureau b ON a.SK_ID_CURR = b.SK_ID_CURR
GROUP BY a.SK_ID_CURR, a.AMT_CREDIT, a.AMT_INCOME_TOTAL, a.AMT_ANNUITY
```

**Safe claim:** "Feature engineering maps directly to multi-table SQL joins and group-by aggregations — I implemented this in pandas for scale, but the logic is SQL-equivalent."

### Python Pattern Depth

| Pattern | Used In | Transferable To |
|---|---|---|
| pandas merge + groupby on 57M rows | Feature factory | Any analytical ETL pipeline |
| Stratified train_test_split with seed | Data prep | Standard ML pipeline |
| scale_pos_weight / class_weight | Imbalanced data | Any binary classification with class imbalance |
| Optuna TPE with validation objective | HPO | Any model tuning workstream |
| sigmoid calibration (LogisticRegression) | Platt | Post-hoc calibration for any GBM |
| pred_contrib=True | SHAP reason codes | Any LightGBM SHAP workstream |
| np.percentile bins + PSI | Drift monitoring | Any score distribution monitoring |
| BM25 keyword retrieval | RAG | Document retrieval, search, Q&A |
| bootstrap resampling | Stability audit | Any robustness / CI estimation |
| JSON evidence artifacts | Governance docs | Any claim-tracing documentation system |

---

## 7. Opportunity Fit Matrix

| Role Type | Relevant PulseGuard Component | Key Claim |
|---|---|---|
| Data scientist (credit/banking) | Champion selection, calibration, SHAP, fairness | "AUC=0.7769, ECE=0.003, monotone constraints, 30-bootstrap SHAP stability" |
| ML engineer | Feature pipeline, HPO, serving architecture (FUTURE) | "140 features, Optuna, pred_contrib, PSI monitoring design" |
| Model risk / MRM | Governance stack, claim boundary, evidence ledger | "SR 26-2 aligned; leakage audit; 15-dim governance audit GOLD" |
| GenAI / LLM engineer | RAG/LLM governance assistant | "BM25 retriever, abstain threshold, ASSISTIVE_ONLY hard constraint" |
| Quant/risk analyst | Score-band policy, cost matrix, threshold economics | "Score bands, PSI, fairness proxy, cost-sensitive decisioning" |
| Full-stack ML | End-to-end pipeline | "Full governed lifecycle: ingest → feature → tune → calibrate → govern → document" |

---

---

## 8. Role-Expansion Bullets (Fraud & MLOps Framing)

> PulseGuard is frozen. These bullets reframe existing work for adjacent role contexts without changing any underlying methodology or claims. Use these **instead of** Bullets A–E when the JD is primarily fraud detection or MLOps — not in addition to them. One bullet per application.

---

### Bullet F — Fraud Detection Roles

> **PulseGuard Credit-Risk Governance Portfolio** | LightGBM, Platt Calibration, SHAP, BM25  
> Solved imbalanced binary classification (8.07% positive rate) — the same problem class as fraud detection — on Home Credit Default Risk (307k applicants, 57.4M rows across 7 tables). Applied scale_pos_weight=11.39 class weighting + LightGBM monotone constraints; post-Platt calibration achieves ECE=0.0034, recovering well-calibrated probabilities from an extreme-weight GBM. SHAP reason codes stable across 30 bootstrap resamples (EXT_SOURCE_MEAN rank-1 30/30); PSI drift monitoring with WARN/ALERT/CRITICAL cascade. Governance: model card, evidence ledger, score-band policy, ASSISTIVE_ONLY reason-code memo drafting. Methodology directly transferable to application fraud or transaction fraud scoring — same algorithmic stack, different feature domain.

**When to use:** Role is titled "Fraud Detection", "Risk Scoring", or "Financial Crimes ML" and the JD emphasizes class imbalance, recall/precision trade-offs, GBM-based scoring, or SHAP reason codes.

**What NOT to say:** "I built a fraud detection model" / "I have transaction fraud experience" / "I've worked with velocity features or device fingerprinting."

---

### Bullet G — MLOps / ML Platform Roles

> **PulseGuard Credit-Risk ML Governance Stack** | LightGBM, Optuna, SHAP, reportlab  
> Implemented the full governed ML lifecycle by hand — the layer that MLOps tooling automates: leakage audit → validation-only Optuna HPO (TPE) → Platt calibration (ECE 0.296→0.0034) → 9-component composite champion promotion criteria → score-band deployment policy → SHAP bootstrap stability audit (30 resamples) → PSI/KS drift monitoring with SLA thresholds (WARN/ALERT/CRITICAL) → model card + evidence ledger (equivalent to MLflow experiment tracking) + claim boundary documentation. Champion selection criteria fully specified before any experiment ran — no post-hoc metric selection. Governance artifacts structured to plug directly into a model registry and monitoring dashboard.

**When to use:** Role is titled "MLOps Engineer", "ML Platform", "ML Infrastructure", or "Model Risk Management" and the JD emphasizes monitoring, model lifecycle, experiment tracking, or governance.

**What NOT to say:** "I built an MLOps platform" / "I have CI/CD for ML experience" / "I've deployed models to production" / "I've used MLflow."

---

### Bullet H — Risk Scoring / Decision Science Roles

> **PulseGuard Credit-Risk Governance Portfolio** | LightGBM, Platt Calibration, SHAP  
> Designed end-to-end score-to-decision pipeline: calibrated LightGBM champion (ECE=0.0034) → PD-semantic score bands (GREEN<20% PD: 89.7% of applicants, 5.8% DR; AMBER 20–40%: 9.8%, 27% DR; RED≥40%: 0.5%, 54% DR) → cost-sensitive threshold analysis across 4 cost-ratio scenarios → SHAP-driven reason-code policy for adverse action. Champion selected by 9-component composite (AUC, PR-AUC, KS, Brier, ECE, latency, explainability, adverse-reason readiness) — the same selection discipline used in production champion/challenger frameworks. Score-band policy documented with approval-rate and default-rate impact; governance stack includes fairness proxy audit and PSI drift baseline.

**When to use:** Role is titled "Risk Analyst", "Decision Scientist", "Strategy Analytics", or "Risk Modelling" and the JD emphasizes policy design, threshold economics, or score interpretation.

---

*PulseGuard Resume & Opportunity Pack | Gold Pass 4/4 + Role Expansion | 2026-06-18*  
*All claims traceable to `outputs/evidence/` artifacts. Forbidden claims documented in `06_CLAIM_BOUNDARY.md`.*
