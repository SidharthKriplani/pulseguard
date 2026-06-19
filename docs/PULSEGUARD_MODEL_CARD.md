# PulseGuard — Model Card

**Model:** LightGBM_monotonic + Platt calibration  
**Version:** Gold Pass 3 | **Date:** 2026-06-17  
**Status:** PORTFOLIO PROJECT — NOT PRODUCTION DEPLOYMENT  

---

## Model Details

| Field | Value |
|---|---|
| Model family | LightGBM Gradient Boosted Trees |
| Governance variant | Monotonic constraints on 15 features (SR 26-2 aligned directional interpretability) |
| Calibration | Platt sigmoid (LogisticRegression C=1e6, fit on validation set only) |
| Champion selection | 9-component composite score (AUC 25%, PR-AUC 15%, KS 15%, Brier 10%, ECE 10%, slope 5%, latency 5%, explainability 10%, adverse-ready 5%) |
| Training objective | Binary cross-entropy with scale_pos_weight=11.39 |
| Hyperparameter search | Optuna TPE, 5 trials, validation-only budget (CPU constraint) |
| Explainability | LightGBM built-in SHAP (pred_contrib); monotone constraints for directional audit |
| Policy interface | BM25 policy RAG + LLM governance assistant (ASSISTIVE_ONLY) |

---

## Intended Use

**In-scope (portfolio demonstration):**
- Credit default probability estimation on Home Credit Default Risk dataset
- Governance artifact for SR 26-2 aligned model risk management demonstration
- SHAP-driven adverse action reason code generation (draft, requires human review)
- Policy Q&A via RAG governance assistant

**Out-of-scope (explicitly prohibited):**
- Production lending decisions
- Regulatory compliance certification
- Legally compliant adverse action notices without licensed credit officer review
- Deployment to any real applicant population
- Generalization claims to non-Home-Credit portfolios

---

## Training Data

| Field | Value |
|---|---|
| Dataset | Home Credit Default Risk (Kaggle, public) |
| Total rows | 307,511 applicants (application_train.csv) |
| Side tables | 7 tables, 57M total rows |
| Default rate | 8.07% |
| Geography | Single Eastern European portfolio |
| Timestamps | None — no temporal ordering available |
| Split | Stratified random 60/20/20 (train/val/test), seed=42, DR preserved |
| Features engineered | 140 features from 7 relational tables |

---

## Evaluation Results

### Test Set (61,503 rows, held-out, evaluated once)

| Metric | Value |
|---|---|
| ROC-AUC | **0.7769** |
| PR-AUC | 0.2628 |
| KS statistic | **0.4141** |
| Brier score | 0.0668 |
| ECE (Platt calibrated) | **0.0034** |
| Latency | 327 ms / 61k rows |

### Score Band Policy (Balanced, PD-semantic)

| Band | Threshold | Test % | Test Default Rate |
|---|---|---|---|
| GREEN (approve) | PD < 0.20 | 89.72% | 5.77% |
| AMBER (review) | 0.20 ≤ PD < 0.40 | 9.80% | 26.96% |
| RED (high-risk) | PD ≥ 0.40 | 0.47% | 53.77% |

### By Split (Calibrated Probabilities)

| Split | AUC | KS | ECE |
|---|---|---|---|
| Train | 0.8526 | 0.5425 | 0.399 (Platt artefact — not re-fit on train) |
| Validation | 0.7734 | 0.4121 | 0.0051 |
| Test | 0.7769 | 0.4141 | 0.0034 |

---

## Monotone Constraints

15 features carry directional constraints enforced at every tree split:

| Direction | Features |
|---|---|
| +1 (risk-increasing) | FLAG_EMPLOYED_ANOMALY, CREDIT_TO_INCOME, ANNUITY_TO_INCOME, CREDIT_TO_GOODS, BUREAU_OVERDUE_RATIO, BUREAU_AMT_OVERDUE, PREV_REFUSAL_RATE, INST_LATE_RATIO, CC_DPD_RATIO, POS_IS_DPD_RATIO, BEHAVIORAL_RISK_SCORE, BB_DPD_RATIO_MEAN |
| −1 (risk-decreasing) | AGE_YEARS, EMPLOYED_YEARS, EXT_SOURCE_MEAN |

Constraints support directional interpretability audits without requiring per-prediction SHAP explanation.

---

## Global Feature Importance (SHAP, mean |contribution|, 1000-sample draw)

| Rank | Feature | Mean |SHAP| |
|---|---|---|
| 1 | EXT_SOURCE_MEAN | 0.5098 |
| 2 | CREDIT_TO_ANNUITY | 0.1414 |
| 3 | CREDIT_TO_GOODS | 0.1393 |
| 4 | INST_LATE_RATIO | 0.1292 |
| 5 | EXT_SOURCE_1 | 0.1196 |
| 6 | OWN_CAR_AGE | 0.0924 |
| 7 | EMPLOYED_YEARS | 0.0911 |
| 8 | BUREAU_ACTIVE_COUNT | 0.0874 |
| 9 | AMT_GOODS_PRICE | 0.0817 |
| 10 | EXT_SOURCE_3 | 0.0782 |

Top-5 features appear in top-5 of all 30 bootstrap resamples (HIGH stability). EXT_SOURCE_MEAN is rank-1 in 30/30 bootstraps.

---

## Fairness and Bias

**Scope:** Proxy-variable audit only. Home Credit dataset contains no protected-class labels.

| Proxy Group | Approval Rate | Observed Default Rate |
|---|---|---|
| Age < 30 | 80.5% | 11.5% |
| Age 30–50 | 88.6% | 8.8% |
| Age 50+ | 95.5% | 5.6% |
| Income low tercile | 89.0% | 8.1% |
| Income mid tercile | 88.5% | 8.8% |
| Income high tercile | 91.3% | 7.5% |
| Region rating 1 (low-risk) | 96.5% | 4.9% |
| Region rating 3 (high-risk) | 81.7% | 11.2% |

Observed approval rate differences are directionally aligned with actual default rate differences. No evidence of model amplifying disparities beyond base rates. Full fairness certification requires protected-class labels and independent validator — not performed.

---

## Limitations

| Limitation | Detail |
|---|---|
| Reject inference | Approved-applicant MNAR selection bias. Model trained only on applicants who received prior loans. Declined population is unobserved. |
| No temporal holdout | No timestamps in Home Credit. Out-of-time validation not possible. |
| Single geography | Eastern European portfolio. Generalization to other markets is untested. |
| Trial count | 5 Optuna trials (CPU budget). A 100-trial GPU search would likely improve AUC. |
| Calibrator scope | Platt fit on val only. Train-set ECE is high (0.40) — expected artefact, not a deployment concern. |
| Fairness | No protected-class labels. Disparate impact ratio cannot be computed. |

---

## Ethical Considerations

- Model output must never autonomously approve or reject a real applicant.
- SHAP reason codes are governance artifacts — they require credit officer review before use in any applicant communication.
- Adverse action drafts generated by the LLM governance assistant are NOT legally compliant adverse action notices.
- Model is not SR 26-2 certified. SR 26-2 compliance requires independent model validation team review.

---

## Citation and Repository

```
PulseGuard — Credit Risk ML Portfolio Project
Dataset: Home Credit Default Risk (Kaggle)
Model: LightGBM_monotonic + Platt calibration
Champion selection: Gold Pass 2/4 composite score
Evidence: outputs/evidence/
```

---

*PulseGuard Model Card | Gold Pass 3 | 2026-06-17 | PORTFOLIO PROJECT — NOT FOR PRODUCTION*
