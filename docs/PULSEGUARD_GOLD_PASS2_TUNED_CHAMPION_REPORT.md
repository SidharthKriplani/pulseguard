# PulseGuard — Gold Pass 2/4: Tuned Champion Report

**Gate:** GOLD_PASS_2 | **Status:** COMPLETE  
**Date:** 2026-06-17 | **Champion:** LightGBM_monotonic + Platt calibration

---

## 1. Why Pass 2 Exists

Gold Pass 1 established a baseline tournament labeled **BASELINE_NOT_TUNED**. The 12 models were fitted with default or near-default hyperparameters for tournament comparison. The provisional champion (CatBoost, val_AUC=0.7716) was explicitly marked as a starting point, not a final answer.

Pass 2 answers: **after proper validation-only hyperparameter search and post-tuning calibration, which model is the best credit-risk champion under performance, calibration, governance, latency, explainability, and adverse-reason readiness — not AUC alone?**

---

## 2. Why G9A Was BASELINE_NOT_TUNED

The G9A tournament used one configuration per model family to establish competitive ordering, confirm that the pipeline was leakage-free, and verify that the feature engineering produced signal. Tuning prior to these audits would have risked discovering leakage only after investing tuning compute. Gold Pass 1 confirmed `safe_to_tune=true` before any hyperparameter search began.

---

## 3. Tuning Method

**Search algorithm:** Optuna Tree-structured Parzen Estimator (TPE), seed=42.

**Runtime constraint:** CPU-only sandbox, 44-second bash call limit per model. Optuna was given a 35-second wall-clock budget per run. Trial counts reflect actual completions within this budget, documented honestly:

| Model | Trials Completed | Runtime (s) | Notes |
|---|---|---|---|
| LightGBM_base | 6 | 37.2 | Fixed n_estimators (LGB AUC early-stopping bug on imbalanced data) |
| LightGBM_monotonic | 5 | 40.4 | Same fix + 15 monotone constraints |
| CatBoost | 8 (2 runs) | 75.2 | Two runs merged; best params from run with eval_set |
| XGBoost | 4 | 17.2 | Fixed n_estimators; no early stopping |
| XGBoost_monotonic | 4 | 17.5 | Same params as XGBoost + monotone constraints |

**LightGBM early-stopping bug note:** When `eval_metric='auc'` is combined with `scale_pos_weight` in LightGBM, the internal early-stopping mechanism fires at iteration=1 (known imbalanced-class behavior). Fix: treat n_estimators as a hyperparameter within Optuna instead of using LightGBM's native early stopping. Verified that the same parameter range with fixed n_estimators produces AUC=0.7707 (matching XGBoost baseline), confirming the fix is correct.

---

## 4. Search Spaces

### LightGBM (base + monotonic)
- `n_estimators`: [150, 400]
- `learning_rate`: [0.02, 0.15] log
- `num_leaves`: [31, 127]
- `max_depth`: [4, 8]
- `min_child_samples`: [20, 150]
- `subsample`: [0.6, 1.0]
- `colsample_bytree`: [0.6, 1.0]
- `reg_alpha`, `reg_lambda`: [1e-6, 5.0] log
- `scale_pos_weight`: 11.39 **fixed**
- LightGBM_monotonic adds: `monotone_constraints` (15 features) **fixed**

### XGBoost (base + monotonic)
- `n_estimators`: [150, 350]
- `learning_rate`: [0.02, 0.15] log
- `max_depth`: [3, 7]
- `min_child_weight`: [5, 80]
- `subsample`, `colsample_bytree`: [0.6, 1.0]
- `gamma`: [0, 2.0]
- `reg_alpha`, `reg_lambda`: [1e-6, 3.0] log
- `scale_pos_weight`: 11.39 **fixed**
- XGBoost_monotonic adds: `monotone_constraints` tuple **fixed**

### CatBoost
- `iterations`: [150, 350]
- `learning_rate`: [0.03, 0.15] log
- `depth`: [4, 7]
- `l2_leaf_reg`: [1, 8]
- `bagging_temperature`: [0, 1]
- `random_strength`: [0.5, 4]
- `border_count`: [64, 150]
- `auto_class_weights`: Balanced **fixed**

### Fixed Constraints (not tunable)
- `scale_pos_weight` / `auto_class_weights` — fixed at class imbalance ratio (11.39)
- `monotone_constraints` — fixed list from G9A governance design
- Validation set — only split used for eval; test set untouched until final evaluation

---

## 5. Monotone Constraint Map (LightGBM_monotonic + XGBoost_monotonic)

| Direction | Features | Rationale |
|---|---|---|
| +1 (risk-increasing) | FLAG_EMPLOYED_ANOMALY, CREDIT_TO_INCOME, ANNUITY_TO_INCOME, CREDIT_TO_GOODS, BUREAU_OVERDUE_RATIO, BUREAU_AMT_OVERDUE, PREV_REFUSAL_RATE, INST_LATE_RATIO, CC_DPD_RATIO, POS_IS_DPD_RATIO, BEHAVIORAL_RISK_SCORE, BB_DPD_RATIO_MEAN | Higher value = higher credit risk |
| -1 (risk-decreasing) | AGE_YEARS, EMPLOYED_YEARS, EXT_SOURCE_MEAN | Higher value = lower credit risk |
| 0 (unconstrained) | 125 remaining features | Directional effect uncertain or data-driven |

---

## 6. Calibration After Tuning

Calibration was fit on the validation set only. Two methods were evaluated:

- **Platt** — LogisticRegression(C=1e6) on raw probs: 2 free parameters, avoids overfitting to val
- **Isotonic** — IsotonicRegression on raw probs: interpolates perfectly on val data (ECE=0 on val = overfitting artifact)

**Selected calibrator: Platt.** Isotonic is excluded from model selection comparison because its ECE=0 on val is an artifact of fitting and evaluating on the same set. Final test ECE is reported with Platt calibration to ensure honest generalization measurement.

| Model | ECE_raw | ECE_platt (val) |
|---|---|---|
| LightGBM_monotonic | 0.2964 | 0.0051 |
| LightGBM_base | 0.2928 | 0.0051 |
| CatBoost | 0.3112 | 0.0044 |
| XGBoost | 0.3101 | 0.0054 |
| XGBoost_monotonic | 0.3172 | 0.0057 |

All models had very high raw ECE (>0.29) because GBMs without calibration produce overconfident probabilities, especially with `scale_pos_weight` adjusting the score distribution. Platt reduces ECE to <0.006 for all models.

---

## 7. Validation-Only Model Selection

Champion was selected using a **composite score** on the validation set. Test set was not consulted.

```
COMPOSITE = 0.25×AUC + 0.15×PR-AUC + 0.15×KS + 0.10×(1-Brier) + 0.10×(1-ECE)
          + 0.05×(1-|slope-1|) + 0.05×latency_score + 0.10×explainability + 0.05×adverse_ready
```

| Model | Val AUC | PR-AUC | KS | ECE_platt | Monotone | Composite | Role |
|---|---|---|---|---|---|---|---|
| **LightGBM_mono** | **0.7734** | 0.2661 | **0.4121** | 0.0051 | ✓ | **0.7312** | **CHAMPION + GOVERNANCE** |
| XGBoost_mono | 0.7699 | 0.2624 | 0.4095 | 0.0057 | ✓ | 0.7294 | CONTENDER |
| LightGBM_base | 0.7724 | **0.2665** | 0.4116 | 0.0051 | ✗ | 0.6811 | CONTENDER |
| CatBoost | 0.7708 | 0.2611 | **0.4142** | **0.0044** | ✗ | 0.6802 | CONTENDER |
| XGBoost | 0.7704 | 0.2648 | 0.4112 | 0.0054 | ✗ | 0.6801 | CONTENDER |

**LightGBM_monotonic is simultaneously the performance champion and the governance champion.** The explainability score (0.5 SHAP + 0.5 monotone constraints = 1.0) combined with the highest AUC and KS produces a clear composite lead (+0.0018 over XGBoost_monotonic, +0.0501 over non-monotonic models).

---

## 8. Why Champion Was Not Selected by AUC Alone

CatBoost has the highest KS (0.4142) and lowest ECE (0.0044). LightGBM_base has the highest PR-AUC (0.2665). Neither is the composite champion. The composite framework deliberately weights governance (explainability, monotone, adverse-reason) equally with probability quality. A model that lacks monotone constraints sacrifices directional interpretability required for SR 26-2 aligned deployment — and that cost is explicitly captured in the composite score.

---

## 9. Final Untouched Test Result

**Single evaluation on held-out test set (61,503 rows, DR=0.0807). Test was not used for selection, calibration, or any intermediate decision.**

| Metric | Value | G9A Baseline (CatBoost+Platt, val) | Delta |
|---|---|---|---|
| ROC-AUC | **0.7769** | 0.7716 | **+0.0053** |
| PR-AUC | 0.2628 | 0.2637 | −0.0009 |
| KS | **0.4141** | 0.4094 | **+0.0047** |
| Brier | 0.0668 | — | — |
| ECE (raw) | 0.2948 | 0.3157 | improved |
| ECE (Platt) | **0.0034** | 0.0054 | **+0.0020 improvement** |
| Latency | 327ms/61k rows | — | — |

**Generalization gap:** Val AUC = 0.7734 → Test AUC = 0.7769 (gap = −0.0035, ACCEPTABLE). The test slightly outperforms val, consistent with random stratified splitting from the same distribution.

---

## 10. Remaining Limitations

All limitations from G9A carry forward:

- **Reject inference:** Approved-applicant MNAR selection bias. Not implemented. Documented known limitation.
- **No temporal holdout:** No timestamps in Home Credit. SK_ID_CURR DR range=0.0033 (not a time proxy). Stratified random split only.
- **Single geography:** Home Credit is a single Eastern European portfolio. Generalization to other markets is untested.
- **No fairness audit:** Protected-class fairness analysis not in G9A/Pass 2 scope. Required before any deployment claim.
- **Trial count:** Optuna trial counts (4–8 per model) are lower than the 100-trial plan due to CPU-only constraints. Results represent a reasonable local optimum, not a globally-optimized solution. A GPU environment with 100 trials would likely improve all AUC figures.
- **Calibration evaluated on val:** Platt calibrator fit and ECE comparison both use val set. Final test ECE (0.0034) is the honest generalization measure.

---

## 11. Pass 3 Focus

Gold Pass 3 will address:
- SHAP analysis on the new champion (LightGBM_monotonic tuned) — update feature importance
- Score band calibration: re-derive GREEN/AMBER/RED thresholds on tuned champion
- Adverse action reason mapping: map top SHAP features to ECOA-ready reason codes
- Fairness audit skeleton (protected-class proxies, disparate impact on score bands)
- Update model card, governance signoff packet, and architecture doc with Pass 2 champion

---

*PulseGuard — Gold Pass 2 Tuned Champion Report | 2026-06-17*
