# PulseGuard — Gold Pass 2/4: Hyperparameter Tuning Battlefield

**Gate:** GOLD_PASS_2 | **Status:** READY_TO_START  
**Pre-condition:** Gold Pass 1 verdict = PASS, safe_to_tune = true  
**Author:** G9A pipeline | **Date:** 2026-06-17

---

## 0. Context

Pass 1 established a **BASELINE_NOT_TUNED** tournament:

| Model | val_AUC | PR-AUC | KS | ECE_post |
|---|---|---|---|---|
| CatBoost | 0.7716 | 0.2637 | 0.4094 | 0.0054 |
| XGBoost | 0.7703 | 0.2620 | 0.4097 | 0.0040 |
| LightGBM_monotonic | 0.7203 | 0.1879 | 0.3322 | 0.0016 |
| LightGBM_base | 0.7197 | 0.1826 | 0.3265 | 0.0005 |

**Goal of Pass 2:** Find the best hyperparameters for each GBM family on the existing 60/20/20 split. No test set is touched. Final champion is re-selected on validation metrics only.

---

## 1. Models in Scope

| Model | Priority | Governance role |
|---|---|---|
| CatBoost | P1 — current champion | Production candidate |
| XGBoost | P1 — close second on AUC | Challenger |
| LightGBM_monotonic | P1 — governance alternative | SR 26-2 aligned |
| LightGBM_base | P2 — benchmark | Comparison baseline |
| Monotonic XGBoost | P2 — new variant | Governance challenger |

---

## 2. Search Method

**Primary:** Optuna (Tree-structured Parzen Estimator, TPE)  
**Fallback:** Halving grid search via `sklearn.model_selection.HalvingGridSearchCV` (if Optuna unavailable)  
**Budget:** 100 trials per model × 5 models = 500 trials total  
**Early stopping:** Val AUC plateau for 20 consecutive trials triggers Optuna pruning (MedianPruner)  
**Seed:** 42 for all samplers  
**Parallelism:** `n_jobs=1` per trial (avoid OOM); outer Optuna loop single-threaded

```python
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(
    direction='maximize',
    sampler=optuna.samplers.TPESampler(seed=42),
    pruner=optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=0),
)
study.optimize(objective, n_trials=100, timeout=3600)  # 1h wall-time cap per model
```

---

## 3. Composite Champion Score

No model is crowned on AUC alone. The composite score weights governance factors explicitly:

```
COMPOSITE = (
    0.25 × AUC_val
  + 0.15 × PR_AUC_val           # Precision-recall matters at 8% DR
  + 0.15 × KS_val               # Separation quality
  + 0.10 × (1 – Brier_val)      # Probabilistic accuracy
  + 0.10 × (1 – ECE_post_cal)   # Calibration quality (post-calibration)
  + 0.05 × (1 – abs(calib_slope – 1))  # Calibration slope near 1.0
  + 0.05 × latency_score        # Inference time (<100ms=1.0, >500ms=0.0)
  + 0.10 × explainability_score # SHAP available=0.5; + monotone constraints=+0.5
  + 0.05 × adverse_reason_ready # Feature names map to adverse action reasons
)
```

**Governance tiebreaker:** If top two models are within 0.005 COMPOSITE, prefer the model with monotone constraints (SR 26-2 alignment).

---

## 4. Hyperparameter Search Spaces

### 4.1 LightGBM (base + monotonic variants)

```python
def lgb_search_space(trial):
    return {
        'n_estimators':        trial.suggest_int('n_estimators', 300, 2000),
        'learning_rate':       trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
        'num_leaves':          trial.suggest_int('num_leaves', 31, 512),
        'max_depth':           trial.suggest_int('max_depth', 4, 12),
        'min_child_samples':   trial.suggest_int('min_child_samples', 20, 200),
        'subsample':           trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree':    trial.suggest_float('colsample_bytree', 0.4, 1.0),
        'reg_alpha':           trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda':          trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        'min_split_gain':      trial.suggest_float('min_split_gain', 0.0, 1.0),
        'scale_pos_weight':    11.39,  # FIXED — class imbalance ratio
        'random_state': 42, 'n_jobs': -1, 'verbose': -1,
    }
# For monotonic variant: add monotone_constraints=mc after constructing params
```

### 4.2 XGBoost (base + monotonic variants)

```python
def xgb_search_space(trial):
    return {
        'n_estimators':        trial.suggest_int('n_estimators', 300, 2000),
        'learning_rate':       trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
        'max_depth':           trial.suggest_int('max_depth', 3, 10),
        'min_child_weight':    trial.suggest_int('min_child_weight', 1, 100),
        'subsample':           trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree':    trial.suggest_float('colsample_bytree', 0.4, 1.0),
        'colsample_bylevel':   trial.suggest_float('colsample_bylevel', 0.4, 1.0),
        'gamma':               trial.suggest_float('gamma', 0.0, 5.0),
        'reg_alpha':           trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda':          trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        'scale_pos_weight':    11.39,  # FIXED
        'tree_method': 'hist', 'eval_metric': 'auc',
        'random_state': 42, 'n_jobs': -1,
    }
# For monotonic variant: add monotone_constraints=dict(zip(feature_names, mc))
```

### 4.3 CatBoost

```python
def cat_search_space(trial):
    return {
        'iterations':          trial.suggest_int('iterations', 300, 2000),
        'learning_rate':       trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
        'depth':               trial.suggest_int('depth', 4, 10),
        'l2_leaf_reg':         trial.suggest_float('l2_leaf_reg', 1.0, 10.0),
        'bagging_temperature': trial.suggest_float('bagging_temperature', 0.0, 1.0),
        'random_strength':     trial.suggest_float('random_strength', 0.0, 10.0),
        'border_count':        trial.suggest_int('border_count', 32, 255),
        'auto_class_weights': 'Balanced',  # equiv to scale_pos_weight
        'eval_metric': 'AUC', 'random_seed': 42,
        'verbose': 0, 'use_best_model': True,
    }
```

---

## 5. Fixed Constraints (Not Tunable)

| Parameter | Value | Reason |
|---|---|---|
| `scale_pos_weight` | 11.39 | Hard-coded from class imbalance; must not vary |
| `monotone_constraints` | 15 constraints | Hard-coded for monotonic variants |
| `eval_set` | `(X_val, y_val)` only | Leakage guard — test never seen during tuning |
| `early_stopping_rounds` | 50 | Applied to val set only |
| Split seed | 42 | Reproducibility |
| Calibration | Platt (val), Isotonic (val), Beta (val) | Always fit on val only |

---

## 6. Calibration After Tuning

For every tuned model, fit three calibrators on `(val_probs, y_val)`:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
# Beta calibration: via betacal package or manual (a,b) fit

calibrators = {
    'platt':     LogisticRegression(C=1e6).fit(val_probs.reshape(-1,1), y_val),
    'isotonic':  IsotonicRegression(out_of_bounds='clip').fit(val_probs, y_val),
}
# Beta calibration if betacal available; else skip
```

Select calibrator by lowest ECE on validation set. Apply selected calibrator to test set for final ECE reporting.

---

## 7. Optuna Objective Function Template

```python
def make_objective(ModelClass, params_fn, X_tr, y_tr, X_val, y_val, mono_constraints=None):
    def objective(trial):
        params = params_fn(trial)
        if mono_constraints and hasattr(ModelClass(), 'monotone_constraints'):
            params['monotone_constraints'] = mono_constraints
        
        model = ModelClass(**params)
        model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=50,
            verbose=False,
        )
        val_probs = model.predict_proba(X_val)[:,1]
        return roc_auc_score(y_val, val_probs)
    return objective
```

---

## 8. Output Expectations for Pass 2

All outputs saved under `outputs/`:

| File | Contents |
|---|---|
| `data/pass2_best_params.json` | Best params per model from Optuna |
| `data/pass2_tuned_models.pkl` | All 5 fitted models + calibrators |
| `data/pass2_val_probs.pkl` | Val probabilities (tuned) |
| `data/pass2_te_probs.pkl` | Test probabilities (tuned, final eval only) |
| `evidence/pass2_tuning_report.json` | Per-model: trial count, best AUC, composite score, calibration ECE |
| `evidence/pass2_champion_selection.json` | Composite score table, champion, governance alt, rationale |
| `plots/pass2_calibration_curves.png` | Reliability diagrams for top-3 models |
| `plots/pass2_optuna_history.png` | Trial history per model (AUC vs trial#) |

---

## 9. Champion Re-Selection Criteria

After Pass 2 completes:

1. Compute COMPOSITE score for all 5 tuned models
2. If COMPOSITE_best – COMPOSITE_2nd ≥ 0.005: new champion = best
3. If within 0.005: prefer monotonic variant (governance tiebreaker)
4. Document in `pass2_champion_selection.json` with verbatim rationale
5. Update `00_CONTROL_TOWER.md` champion row
6. Apply Platt calibration to new champion (refit on val)

---

## 10. Leakage Guards (Carry Forward from Pass 1)

- `safe_to_tune = True` confirmed in `gold_pass1_leakage_audit.json`
- Early stopping **only** on `(X_val, y_val)`; test not touched until Pass 3
- Calibrators fit on val only; test ECE is final evaluation output, not selection input
- No re-encoding or target encoding anywhere
- SHAP analysis run after champion is frozen (not used for selection)

---

## 11. Pass 2 Acceptance Criteria

Pass 2 is COMPLETE when ALL of:

- [ ] Optuna study complete for all 5 models (or wall-time reached)
- [ ] `pass2_best_params.json` saved
- [ ] `pass2_tuning_report.json` with composite scores for all models
- [ ] `pass2_champion_selection.json` with chosen champion and rationale
- [ ] Best post-cal val ECE ≤ 0.01 (otherwise calibration investigation required)
- [ ] `00_CONTROL_TOWER.md` updated with Pass 2 verdict
- [ ] `04_EVIDENCE_LEDGER.md` updated with 2 new entries (GP2-TUNE, GP2-CHAMP)
- [ ] `06_CLAIM_BOUNDARY.md` updated with new champion metrics

---

*PulseGuard — Gold Pass 2 Tuning Plan | Part of the G9A primary lane.*
