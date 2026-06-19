# G9A — Modern Credit-Intelligence Architecture

**Gate:** G9A | **Status:** COMPLETE | **Date:** 2026-06-17  
**Scope:** End-to-end architecture for a governed, explainable, production-ready credit risk scoring system

---

## 1. System Overview

PulseGuard is a credit risk scoring platform designed to:

1. **Score applicants** with calibrated default probabilities from a model tournament champion
2. **Explain decisions** via SHAP-grounded, policy-anchored rationales
3. **Assist analysts** via a local LM Studio governance assistant (offline, no data egress)
4. **Enforce governance** via monotone constraints, calibration gates, and claim boundaries
5. **Monitor in production** via PSI-based drift detection and DR tracking

```
┌─────────────────────────────────────────────────────────────────┐
│                    PulseGuard Architecture                       │
│                                                                  │
│  DATA LAYER          MODEL LAYER         GOVERNANCE LAYER        │
│  ┌──────────┐       ┌───────────┐       ┌──────────────────┐    │
│  │application│      │ CatBoost  │       │ Monotone          │    │
│  │  _train  │──────▶│  +Platt  │──────▶│ Constraints LGB  │    │
│  └──────────┘       │(Champion) │       │ (Gov Alternative)│    │
│  ┌──────────┐       └───────────┘       └──────────────────┘    │
│  │bureau +  │              │                     │               │
│  │bureau_bal│       ┌──────▼──────┐      ┌───────▼───────┐      │
│  └──────────┘       │   SHAP      │      │  Calibration  │      │
│  ┌──────────┐       │ Explainer   │      │  Gate (ECE)   │      │
│  │prev_app  │       └──────┬──────┘      └───────┬───────┘      │
│  └──────────┘              │                     │               │
│  ┌──────────┐       ┌──────▼─────────────────────▼──────┐       │
│  │instalments      │        Decision Output               │      │
│  └──────────┘       │  prob + band + SHAP reasons         │      │
│  ┌──────────┐       └──────────────┬─────────────────────┘       │
│  │CC balance│                      │                              │
│  └──────────┘       ┌──────────────▼──────────────────────┐      │
│  ┌──────────┐       │   LM Studio Governance Assistant     │      │
│  │POS_CASH  │       │   (Local, Offline, Policy-RAG)       │      │
│  └──────────┘       │   ASSISTIVE_ONLY — not decisioning   │      │
│                     └─────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Layer

### 2.1 Ingestion Pipeline

```
Raw CSVs → Parquet intermediate → SK_ID_CURR merge → Feature matrix → PKL splits
```

Processing order (dependency-respecting):
1. `bureau_balance.csv` (27.3M rows) → `bb_agg.parquet` (SK_ID_BUREAU level)
2. `bureau.csv` (1.7M) + `bb_agg` → `bureau_agg.parquet` (SK_ID_CURR level)
3. `previous_application.csv` (1.7M) → `prev_agg.parquet`
4. `installments_payments.csv` (13.6M) → `inst_agg.parquet`
5. `credit_card_balance.csv` (3.8M) → `cc_agg.parquet`
6. `POS_CASH_balance.csv` (10M) → `pos_agg.parquet`
7. `application_train.csv` (307k) + all 5 aggregates → feature matrix → `g9a_splits.pkl`

**Performance:** All steps complete in <20 seconds total using columnar reads (select_dtypes, usecols), pre-encoding before groupby (no lambda functions), and parquet intermediate storage.

### 2.2 Feature Categories

| Category | Count | Source |
|---|---|---|
| Application raw | 90 | application_train numeric columns |
| Application engineered | 18 | Ratios, flags, composite scores |
| Bureau | 13 | bureau + bureau_balance aggregated |
| Installments | 5 | installments_payments aggregated |
| Credit card | 5 | credit_card_balance aggregated |
| Previous applications | 5 | previous_application aggregated |
| POS/Cash | 3 | POS_CASH_balance aggregated |
| Behavioral composite | 1 | BEHAVIORAL_RISK_SCORE |
| **Total** | **140** | |

---

## 3. Model Layer

### 3.1 Champion Model

**CatBoost + Platt Calibration** (`pulseguard-hc-catboost-platt-v1`)

```python
# Production scoring pipeline
def score_applicant(feature_vector: dict) -> dict:
    X = pd.DataFrame([feature_vector])[feature_names]
    X_filled = X.fillna(-999)
    
    # Raw score
    raw_prob = catboost_model.predict_proba(X_filled)[0, 1]
    
    # Platt calibration
    cal_prob = platt_model.predict_proba([[raw_prob]])[0, 1]
    
    # Score band assignment
    band = assign_band(cal_prob)
    
    # SHAP explanation
    shap_vals = shap_explainer.shap_values(X)[1][0]
    top_factors = get_top_shap_factors(shap_vals, feature_names)
    
    return {
        'application_id': feature_vector['SK_ID_CURR'],
        'default_probability': round(float(cal_prob), 4),
        'score_band': band,
        'risk_factors': top_factors,
        'model_version': 'pulseguard-hc-catboost-platt-v1',
        'calibrated': True,
    }
```

### 3.2 Score Bands

| Band | Probability Range | Decision | Action |
|---|---|---|---|
| GREEN | < 5% | AUTO_APPROVE | Straight-through processing |
| AMBER_LOW | 5–10% | CONDITIONAL | May approve with terms |
| AMBER_HIGH | 10–20% | REVIEW | Manual underwriter review |
| RED | > 20% | DECLINE | Decline with adverse action notice |

Band thresholds are calibrated probabilities. At DR=8.07%, approximately:
- GREEN: ~55% of applicants
- AMBER_LOW: ~25% of applicants  
- AMBER_HIGH: ~12% of applicants
- RED: ~8% of applicants

### 3.3 Governance Alternative Path

When model risk review requires SR 26-2 directional interpretability:

```
Champion (CatBoost) → REPLACE WITH → LightGBM_Monotonic + Platt
AUC loss: -0.051 (0.7716 → 0.7203)
ECE gain: -0.0038 (0.0054 → 0.0016)
Governance gain: 15 monotone constraints enforced
```

---

## 4. Explainability Layer

### 4.1 SHAP Integration

```python
# TreeExplainer (fast, exact for tree models)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_batch)

# For LightGBM: shap_values is a list [class_0, class_1]
# For CatBoost: shap_values is a 2D array directly
```

Top SHAP factors per applicant become the **risk factor explanation** shown to:
- Underwriters (AMBER/RED decisions)
- Compliance (adverse action notices)
- Model risk (governance review)

### 4.2 Global vs Local Explanations

| Explanation Type | Method | Audience | Frequency |
|---|---|---|---|
| Global feature importance | Mean |SHAP| across test set | Model validation | Per model version |
| Local applicant explanation | Per-sample SHAP values | Underwriter, applicant | Per decision |
| Population segment SHAP | Mean |SHAP| by score band | Product/risk | Monthly |

### 4.3 Safe SHAP Claims

**Can claim:** "SHAP values explain which features contributed most to each applicant's score, with EXT_SOURCE scores, INST_LATE_RATIO, and AGE_YEARS being the strongest global drivers."

**Cannot claim:** "SHAP values explain why the model makes its decisions" (SHAP explains contributions to the model's prediction, not causal reasons for default).

---

## 5. Calibration Gate

ECE threshold for production deployment:

```
ECE_gate = champion_uncalibrated_ECE × 0.10   # Must reduce by 90%
         = 0.3157 × 0.10 = 0.032

Post-Platt ECE = 0.0054  ✅  (< 0.032 gate)
```

Additionally: ECE_post_calibration ≤ 0.01 (absolute threshold for production-grade calibration).

Gate passes. Model probabilities can be interpreted as probabilities.

---

## 6. Monitoring Architecture

### 6.1 Production Metrics

| Metric | Calculation | Alert Threshold | Action |
|---|---|---|---|
| PSI (top-20 features) | Population Stability Index monthly | PSI > 0.20 | Flag for retraining review |
| DR on scored population | Rolling 90-day actual default rate | ±30% relative from train DR (8.07%) | Retrain or recalibrate |
| AUC on labelled subset | Rolling AUC on accounts with resolved labels | AUC drops > 0.03 | Champion-Challenger activation |
| ECE on labelled subset | 10-bin ECE on accounts with resolved labels | ECE > 0.02 | Recalibrate Platt weights |

### 6.2 Reject Inference Monitoring

Since Home Credit data is approved-applicant-only, the model has no signal on declined applications. In production:

- Track acceptance rate vs DR on accepted population
- If acceptance rate drops significantly (stricter cutoffs → population shift), consider reject inference via augmentation
- Flag if AMBER_HIGH approval rate changes materially (indicates threshold drift)

---

## 7. Claim Boundary Summary

| Claim | Status |
|---|---|
| "We built a credit risk model on 307k real applications with 8.07% DR" | ✅ SAFE |
| "Our champion CatBoost achieves AUC=0.7716 on a 61k holdout test set" | ✅ SAFE |
| "Post-calibration ECE=0.0054 (Platt sigmoid)" | ✅ SAFE |
| "We documented reject inference as a known limitation (not implemented)" | ✅ SAFE |
| "We hard-failed TabNet due to CPU constraint (400–800h estimated)" | ✅ SAFE |
| "This model is validated for production deployment in regulated credit" | ❌ FORBIDDEN |
| "The model is fair across protected classes" | ❌ FORBIDDEN — fairness audit not in G9A scope |
| "We validated on out-of-time data" | ❌ FORBIDDEN — no temporal split possible |
| "This replicates a production scorecard" | ❌ FORBIDDEN — reject inference not implemented |

---

*Part of PulseGuard G9A Gate — Modern Credit-Intelligence Architecture.*
