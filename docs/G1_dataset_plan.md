# G1 — DATASET PLAN
## PulseGuard · Training Data and Synthetic Lifecycle Design

**Gate:** G1 — Dataset Plan
**Status:** COMPLETE
**Date:** June 2026

---

## 1. DATASET AVAILABILITY CHECK

### Home Credit Default Risk (Primary — Preferred)

| Item | Status |
|------|--------|
| Source | Kaggle — "Home Credit Default Risk" competition dataset |
| URL | `https://www.kaggle.com/c/home-credit-default-risk/data` |
| Files required | `application_train.csv` (307,511 rows × 122 columns), `application_test.csv` |
| Workspace check | **NOT PRESENT** — `application_train.csv` not found under `pulseguard/` |
| Download method | `kaggle competitions download -c home-credit-default-risk` (requires Kaggle API key) |
| License | CC BY-NC-SA 4.0 — permitted for portfolio use; not for commercial use |

**Decision:** Home Credit is the preferred dataset and matches RiskFrame's training provenance (enabling SR-1 through SR-12 source-reference comparisons to be meaningful). If the Kaggle API key is available at G3, download and use it. If not available, fall back to the synthetic dataset below.

**Key properties of Home Credit (for matching in synthetic fallback):**
- 307,511 rows (training set); 8.07% default rate (TARGET = 1)
- 122 features; mix of numeric, categorical, boolean
- Primary key: SK_ID_CURR (unique applicant ID)
- Top features by importance: EXT_SOURCE_2, EXT_SOURCE_3, AMT_CREDIT, AMT_INCOME_TOTAL, DAYS_BIRTH, DAYS_EMPLOYED, CODE_GENDER, NAME_INCOME_TYPE
- No feature-level timestamps (must be added synthetically for temporal leakage checks)
- Missing values present in multiple columns (imputation required)

---

## 2. SYNTHETIC FALLBACK DATASET (if Home Credit not downloadable)

### Design Specification

If Home Credit is unavailable at G3, generate a synthetic dataset that matches its schema and statistical properties closely enough that all scripts produce meaningful (not trivially perfect) results.

| Property | Value |
|----------|-------|
| Row count | 50,000 (minimum); 100,000 preferred |
| Default rate | 8.0% (TARGET = 1) — class imbalance preserved |
| Primary key | SK_ID_CURR (integer, unique) |
| Feature count | ~30 features (subset of 122-column Home Credit schema) |
| Train/val/test split | 60/20/20 stratified on TARGET |

### Synthetic Feature Schema

The following 30 features replicate the Home Credit column types and expected distributions:

| Feature | Type | Distribution / Notes |
|---------|------|---------------------|
| SK_ID_CURR | int | Range 100002–500000; unique per row |
| TARGET | int | Bernoulli(0.08) |
| EXT_SOURCE_2 | float | Beta(2, 5); range 0–1; higher = lower risk |
| EXT_SOURCE_3 | float | Beta(1.5, 4); range 0–1; 50% missing → impute with median |
| AMT_CREDIT | float | LogNormal(13, 0.5); range 45k–4M |
| AMT_INCOME_TOTAL | float | LogNormal(11, 0.7); range 25k–1.2M |
| AMT_ANNUITY | float | AMT_CREDIT × uniform(0.03, 0.06) |
| DAYS_BIRTH | int | Negative integer; uniform(−25000, −6500) (≈ age 18–68) |
| DAYS_EMPLOYED | int | Negative integer (employed) or 365243 (unemployed); 20% unemployed |
| CODE_GENDER | str | 65% F, 35% M |
| NAME_INCOME_TYPE | str | Working(50%), Commercial associate(20%), Pensioner(15%), State servant(10%), Unemployed(5%) |
| NAME_CONTRACT_TYPE | str | Cash loans(90%), Revolving loans(10%) |
| NAME_EDUCATION_TYPE | str | Secondary(60%), Higher education(30%), Incomplete higher(7%), Primary(3%) |
| NAME_FAMILY_STATUS | str | Married(65%), Single/not married(20%), Civil marriage(10%), Widow(5%) |
| REGION_RATING_CLIENT | int | Uniform choice from {1, 2, 3}; 3 = highest risk region |
| FLAG_OWN_CAR | str | Y(35%), N(65%) |
| FLAG_OWN_REALTY | str | Y(70%), N(30%) |
| AMT_GOODS_PRICE | float | ≈ AMT_CREDIT × uniform(0.9, 1.05); 1% missing |
| REGION_POPULATION_RELATIVE | float | LogNormal(−5, 0.5); range 0.0003–0.072 |
| DAYS_REGISTRATION | float | Negative integer; uniform(−25000, −0.5) |
| DAYS_ID_PUBLISH | int | Negative integer; uniform(−7000, 0) |
| CNT_CHILDREN | int | Poisson(0.4); capped at 5 |
| CNT_FAM_MEMBERS | float | CNT_CHILDREN + 1 + Bernoulli(0.65); range 1–7 |
| DEF_30_CNT_SOCIAL_CIRCLE | float | Poisson(0.4); 3% missing |
| DEF_60_CNT_SOCIAL_CIRCLE | float | Poisson(0.2); 3% missing |
| OBS_30_CNT_SOCIAL_CIRCLE | float | Poisson(3); 3% missing |
| FLAG_DOCUMENT_3 | int | Bernoulli(0.71) |
| HOUR_APPR_PROCESS_START | int | Uniform(7, 20) |
| LIVE_REGION_NOT_WORK_REGION | int | Bernoulli(0.15) |
| ORGANIZATION_TYPE | str | 58 categories; Business Entity Type 3(25%), Self-employed(18%), Other(57%) |

### Default Rate Engineering

The default rate must be engineered, not random:

```python
# Logistic model over key features to generate TARGET
logit = (
    -2.8                                       # intercept (targets 8% base rate)
    + 1.2 * (1 - EXT_SOURCE_2)               # higher source = lower risk
    + 0.9 * (1 - EXT_SOURCE_3)
    + 0.4 * (AMT_CREDIT / 1e6)               # larger credit = higher risk
    - 0.3 * (AMT_INCOME_TOTAL / 1e5)          # higher income = lower risk
    + 0.7 * (DAYS_EMPLOYED == 365243).astype(float)  # unemployed = higher risk
    + 0.3 * (REGION_RATING_CLIENT == 3).astype(float)
)
prob = 1 / (1 + np.exp(-logit))
TARGET = np.random.binomial(1, prob)
```

This ensures model training is not trivial (AUC will not be 1.00) and that EXT_SOURCE_2 ranks as a top feature by importance.

---

## 3. SYNTHETIC LIFECYCLE DESIGN (both datasets)

Regardless of which dataset is used (Home Credit or synthetic fallback), the 30-day operational lifecycle must be generated synthetically. This is explicitly labeled "synthetic lifecycle simulation" in all artifacts.

### Batch Structure

| Batch | Day | Event | PSI Expectation |
|-------|-----|-------|----------------|
| B00 | Day 0 | Training reference distribution | Baseline |
| B01–B06 | Days 1–6 | Stable serving; no shift | PSI < 0.10 (all features) |
| B07 | Day 7 | Early drift — WARN threshold | PSI ~0.11 on EXT_SOURCE_2 (WARN > 0.10) |
| B08–B13 | Days 8–13 | Progressive drift accumulation | PSI rising on EXT_SOURCE_2 |
| B14 | Day 14 | Drift injection — ALERT threshold | PSI ~0.23 on EXT_SOURCE_2 (ALERT > 0.20) |
| B15–B29 | Days 15–29 | Continued drift (policy response day) | PSI may continue rising or stabilize depending on design |

### Drift Injection Mechanics

```python
# Day 14 injection: shift EXT_SOURCE_2 distribution down (deteriorating credit quality)
day14_batch = base_batch.copy()
day14_batch["EXT_SOURCE_2"] = day14_batch["EXT_SOURCE_2"] - 0.18  # −0.18 shift
day14_batch["EXT_SOURCE_2"] = day14_batch["EXT_SOURCE_2"].clip(0, 1)
```

This matches the SOURCE_REFERENCE value SR-7 (EXT_SOURCE_2 shift −0.18) from RiskFrame. If PulseGuard reproduces it at G4, the DEFERRED row #4 can be updated to match.

### Synthetic Lifecycle Events (Labeled)

| Event | Day | Type | What It Demonstrates |
|-------|-----|------|---------------------|
| Model v1.0 goes live | Day 0 | Policy | Model deployment; version log entry |
| First drift WARN | Day 7 | Monitoring | PSI > 0.10 WARN on EXT_SOURCE_2 |
| First ALERT | Day 14 | Monitoring | PSI > 0.20 ALERT; retraining trigger documented |
| Policy v1.1 threshold change | Day 12 | Policy | Approval rate decomposition test: rate drops; model drift vs. threshold change |
| Delayed label arrives | Day 30 | Validation | 12-month synthetic outcome labels for G8 validation |

> **Label independence requirement:** Delayed labels at Day 30 must be generated independently of the model's predictions. They must be drawn from the same logistic data-generating process used to create TARGET, NOT from model scores. This prevents circular validation.

---

## 4. SYNTHETIC TIMESTAMP COLUMNS (for FeatureLeakageLens temporal checks)

Home Credit has no feature-level timestamps natively. To demonstrate FLL Checks 6 and 7 (temporal leakage FAIL path), synthetic timestamps must be added.

```python
# Added by scripts/add_synthetic_timestamps.py
df["APPLICATION_DATE"] = pd.Timestamp("2024-01-01") + pd.to_timedelta(
    np.random.randint(0, 365, size=len(df)), unit="D"
)
# Normal features — observation date equals application date (no leakage)
df["FEATURE_TIMESTAMP_EXT_SOURCE_2"] = df["APPLICATION_DATE"]

# Injected leakage case — one feature timestamped AFTER application (future data)
df["FEATURE_TIMESTAMP_INJECTED_LEAK"] = df["APPLICATION_DATE"] + pd.to_timedelta(
    np.random.randint(1, 30, size=len(df)), unit="D"
)  # This will cause FLL Check 6 to FAIL
```

The injected feature is clearly labeled `INJECTED_LEAK` in column name and must appear in the FLL leakage report as a FAIL finding.

---

## 5. DATASET CLAIM RULES

| Scenario | Permitted Claim |
|----------|----------------|
| Home Credit downloaded and used | "Trained on Home Credit Default Risk (public Kaggle competition dataset, 307,511 rows, 8% default rate)" |
| Synthetic fallback used | "Trained on a synthetic dataset matching the Home Credit Default Risk schema: 50,000–100,000 rows, 8% default rate, same feature distribution assumptions. Home Credit was unavailable; this is labeled synthetic in all artifacts." |
| Mixing datasets | NOT PERMITTED — use one or the other; document which one in all artifacts |

**Never claim:** "Trained on real applicant data" regardless of which path is used. Both are public or synthetic.

---

## 6. G1 DATASET COMPLETION CHECKLIST

- [x] Home Credit dataset checked — NOT present in workspace
- [x] Download path documented (kaggle CLI)
- [x] Synthetic fallback schema specified (30 features, distributions, default rate engineering)
- [x] Drift injection mechanics documented (Day 7 WARN, Day 14 ALERT, −0.18 shift on EXT_SOURCE_2)
- [x] Delayed label independence requirement documented
- [x] Synthetic timestamp design documented (for FLL temporal checks)
- [x] Dataset claim rules written (Home Credit vs. synthetic fallback)
- [x] Lifecycle event table complete (Day 0 → Day 30)

**Decision at G3:** Try `kaggle competitions download -c home-credit-default-risk` first. If it succeeds, use Home Credit. If it fails (no API key, quota, etc.), use the synthetic fallback. Either way, update `04_EVIDENCE_LEDGER.md` row #2 with the actual dataset used.
