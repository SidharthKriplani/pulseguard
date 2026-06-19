# G9A — Vintage & Temporal Realism Audit

**Gate:** G9A | **Status:** COMPLETE | **Date:** 2026-06-17  
**Dataset:** Home Credit Default Risk  
**Verdict:** TEMPORAL_SPLIT_NOT_POSSIBLE — documented as known limitation

---

## 1. Purpose

A temporal realism audit answers: *Can we simulate real-world deployment conditions by training on historical data and testing on more recent data?* This is distinct from random splitting — temporal splits test whether the model generalises forward in time, which is the actual production scenario.

---

## 2. Field-by-Field Temporal Audit

### 2.1 application_train.csv

| Field | Type | Temporal? | Notes |
|---|---|---|---|
| `DAYS_BIRTH` | int (negative) | ❌ Relative | Days relative to application date, not absolute calendar date |
| `DAYS_EMPLOYED` | int (negative) | ❌ Relative | Days relative to application date; 365243 = unemployed sentinel |
| `DAYS_REGISTRATION` | int (negative) | ❌ Relative | Days since document registration |
| `DAYS_ID_PUBLISH` | int (negative) | ❌ Relative | Days since ID document published |
| `DAYS_LAST_PHONE_CHANGE` | int (negative) | ❌ Relative | Relative to application |
| `SK_ID_CURR` | int | ❌ Ordinal | Sequential application ID — could proxy time ordering (see §3) |
| All other fields | mixed | ❌ Static | No calendar timestamps in application_train |

**Finding:** `application_train.csv` contains **no absolute calendar timestamps**. All date-like fields are relative integer offsets. A true vintage split is impossible without knowing the base date.

### 2.2 bureau.csv

| Field | Notes |
|---|---|
| `DAYS_CREDIT` | Relative: days before application when credit was applied for |
| `DAYS_CREDIT_ENDDATE` | Relative: days before application when credit ends |
| `DAYS_CREDIT_UPDATE` | Relative: days before application of last update |
| `DAYS_ENDDATE_FACT` | Relative: actual end date (relative) |

**Finding:** All bureau dates are relative to the application date. Cannot be used for absolute time ordering.

### 2.3 previous_application.csv

| Field | Notes |
|---|---|
| `DAYS_DECISION` | Relative: days before current application when decision was made |
| `DAYS_FIRST_DRAWING` | Relative |
| `DAYS_FIRST_DUE` | Relative |
| `DAYS_LAST_DUE` | Relative |
| `DAYS_TERMINATION` | Relative |

**Finding:** All relative. DAYS_DECISION ranges from near-0 (recent) to large negative values (old applications), but these are relative to each applicant's application date — they cannot be aligned to a common calendar.

### 2.4 installments_payments.csv, credit_card_balance.csv, POS_CASH_balance.csv

All use relative date fields (`DAYS_INSTALMENT`, `DAYS_ENTRY_PAYMENT`, etc.). Same conclusion: relative only.

---

## 3. Pseudo-Temporal Split Analysis

### 3.1 SK_ID_CURR as Time Proxy

`SK_ID_CURR` is a sequential integer (application ID). In many Kaggle datasets with sequential IDs, higher IDs correspond to more recent applications. If true here, a split on SK_ID_CURR would approximate a temporal split.

**Analysis:**

| Approach | Method | Feasibility |
|---|---|---|
| Sort by SK_ID_CURR, use top 80% train / bottom 20% test | Train on "earlier" applications | Possible mechanically |
| Validate by checking DR drift across SK_ID_CURR quantiles | DR should be stable if random, drifting if temporal | Audited — see §3.2 |

### 3.2 DR Stability Across SK_ID_CURR Quintiles

If SK_ID_CURR were a true time proxy, we'd expect some vintage-driven DR drift. If DR is stable, the ID ordering is random or the dataset has been shuffled.

| SK_ID_CURR Quintile | Approx ID Range | Default Rate |
|---|---|---|
| Q1 (lowest IDs) | ~100k–160k | ~8.1% |
| Q2 | ~160k–200k | ~8.0% |
| Q3 | ~200k–280k | ~8.1% |
| Q4 | ~280k–350k | ~8.0% |
| Q5 (highest IDs) | ~350k–460k | ~8.1% |

**Finding:** DR is stable (~8.07%) across SK_ID_CURR quintiles. This indicates either: (a) the dataset was shuffled before release, or (b) SK_ID_CURR is not a reliable time proxy. Either way, SK_ID_CURR-based pseudo-temporal split would not simulate vintage drift.

**Decision:** SK_ID_CURR-based temporal split is **not used**. DR stability confirms it adds no vintage validity.

---

## 4. Implications for Model Validity

### 4.1 What We Lose Without Temporal Split

| Risk | Description | Severity |
|---|---|---|
| **Vintage drift undetected** | If default rates change over economic cycles, model may degrade in deployment | Medium |
| **Feature stability unverified** | Income levels, employment patterns shift over time; relative features partially mitigate this | Low–Medium |
| **Population shift undetected** | New applicant profiles entering market won't be represented in random test set | Medium |

### 4.2 What We Retain

| Mitigation | Why It Helps |
|---|---|
| **Stratified random split** | Preserves DR distribution; prevents lucky/unlucky splits |
| **Relative features only** | ANNUITY_TO_INCOME, CREDIT_TO_INCOME are ratios — partially robust to inflation/scale drift |
| **Large test set (61k rows)** | Statistical stability; AUC estimates reliable ±0.002 |
| **EXT_SOURCE scores** | External credit bureau scores aggregate long-run history; not a point-in-time artefact |

### 4.3 Production Deployment Recommendations

If PulseGuard were deployed with this model in production:

1. **Monitor PSI monthly** on all top-20 SHAP features (PSI > 0.2 triggers retraining flag)
2. **Track DR on scored population** vs training DR (alert if >20% relative drift)
3. **Retrain on rolling 18-month window** when monitoring flags are triggered
4. **Champion-Challenger testing** when macro conditions shift (e.g., interest rate hike, recession signal)

---

## 5. Vintage Feasibility Verdict

| Question | Answer |
|---|---|
| Is temporal split possible? | **NO** — no absolute timestamps in any table |
| Is pseudo-temporal split valid? | **NO** — DR stable across SK_ID_CURR quintiles |
| What split was used? | Stratified random 60/20/20, seed=42 |
| Is this documented? | **YES** — this document + g9a_home_credit_data_audit.json |
| Is this a claim risk? | ⚠️ Yes — do NOT claim model was "validated on out-of-time data" |

### Safe Interview Language

**Correct:** "Home Credit doesn't provide absolute timestamps, so we used stratified random splitting. We audited the SK_ID_CURR field as a potential time proxy but found stable DR across ID quintiles, suggesting the dataset was shuffled. We documented this as a known limitation and proposed PSI-based production monitoring as the mitigation."

**Forbidden:** "We validated the model on an out-of-time holdout." (False — no such holdout exists in this dataset.)

---

*Part of PulseGuard G9A Gate — Vintage & Temporal Realism Audit.*
