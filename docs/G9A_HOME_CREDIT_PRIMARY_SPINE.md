# G9A — Home Credit Default Risk: Primary Data Spine

**Gate:** G9A | **Status:** COMPLETE | **Date:** 2026-06-17  
**Dataset status:** PRIMARY — replaces Taiwan Default as main modelling substrate  
**Taiwan Default:** LEGACY_APPENDIX_ONLY — retained in BRIDGE_ONLY mode, not interview story  
**LendingClub:** DROPPED_FROM_CURRENT_SCOPE

---

## 1. Dataset Identity

| Field | Value |
|---|---|
| Source | Home Credit Default Risk (Kaggle competition) |
| Organiser | Home Credit Group |
| Primary table | `application_train.csv` |
| Population | Credit applicants (approved-only — MNAR selection bias documented) |
| Rows | 307,511 |
| Columns (raw) | 122 |
| Target variable | `TARGET` (1 = defaulted within contract term, 0 = repaid) |
| Default rate | 8.07% |
| Side-tables | 7 (see §2) |
| Total rows across all tables | ~57.6M |
| Disk size (all tables) | ~2.5 GB |

---

## 2. All Tables Confirmed Downloaded

All 8 files (application_train + 7 side-tables) confirmed present in  
`data/home-credit-default-risk/` before any synthetic generation was attempted.

| Table | Rows | Key Join | Primary Signal |
|---|---|---|---|
| `application_train.csv` | 307,511 | `SK_ID_CURR` | Application-level demographics, financials, EXT_SOURCE scores |
| `bureau.csv` | 1,716,428 | `SK_ID_CURR → SK_ID_BUREAU` | External credit history from Credit Bureau |
| `bureau_balance.csv` | 27,299,925 | `SK_ID_BUREAU` | Monthly delinquency status per bureau credit (27M rows) |
| `previous_application.csv` | 1,670,214 | `SK_ID_CURR` | Past HC applications and outcomes |
| `installments_payments.csv` | 13,605,401 | `SK_ID_CURR, SK_ID_PREV` | Actual vs scheduled instalment payments |
| `credit_card_balance.csv` | 3,840,312 | `SK_ID_CURR, SK_ID_PREV` | Monthly CC balance and DPD |
| `POS_CASH_balance.csv` | 10,001,358 | `SK_ID_CURR, SK_ID_PREV` | Point-of-sale and cash loan monthly snapshots |
| `application_test.csv` | 48,744 | `SK_ID_CURR` | Holdout (no TARGET — competition format) |

---

## 3. Why Home Credit is the Right Substrate

### 3.1 Realism Advantages

Home Credit is one of the largest public real-world retail credit datasets:

- **Scale:** 307k applicants with 7 side-tables totalling 57M rows — sufficient for GBM early stopping, proper stratified splits, and SHAP stability
- **Target quality:** Binary default indicator tied to actual repayment behaviour (not survey self-report)
- **Feature diversity:** Demographics, financials, bureau history, prior applications, payment behavioural sequences — covers all five feature categories in modern credit scorecards
- **Class imbalance realism:** 8.07% DR matches consumer lending norms (retail cards 5–10%; personal loans 7–12%)
- **Multi-bureau coverage:** bureau + bureau_balance provides external credit history at the bureau-account level, enabling delinquency trajectory features

### 3.2 Known Limitations (Documented, Not Ignored)

| Limitation | Impact | Mitigation |
|---|---|---|
| **Reject inference** | Approved-applicant-only sample → MNAR selection bias. True default rate in full population is unknown. | Documented as G9A known limitation. Not implemented (would require semi-supervised or counterfactual approaches). |
| **Temporal split not possible** | No absolute timestamp in application_train. DAYS_BIRTH/DAYS_EMPLOYED are relative integers. DAYS_DECISION in previous_application is not linked at application level. | Stratified random 60/20/20 split (seed=42). Vintage audit documented in G9A_VINTAGE_TEMPORAL_REALISM_AUDIT.md. |
| **Single geography** | Home Credit operates in Eastern Europe and Asia. Features like income levels, bureau structure may not generalise to US/UK lending. | Scope constraint documented. Not claimed as US-deployable model. |
| **No income verification flag** | AMT_INCOME_TOTAL is self-reported, no verification status available. | ANNUITY_TO_INCOME used as ratio (relative, partially controls for inflation). |

---

## 4. Feature Engineering Pipeline

### 4.1 Application-Level Features

Engineered directly from `application_train`:

| Feature | Formula | Direction | Rationale |
|---|---|---|---|
| `FLAG_EMPLOYED_ANOMALY` | `DAYS_EMPLOYED == 365243` → 1, else 0 | +1 risk | 365243 is a sentinel for "unemployed". Replaced DAYS_EMPLOYED with NaN after flag. |
| `CREDIT_TO_INCOME` | `AMT_CREDIT / (AMT_INCOME_TOTAL + 1)` | +1 risk | Debt-to-income proxy (DTI). Higher = more leveraged. |
| `ANNUITY_TO_INCOME` | `AMT_ANNUITY / (AMT_INCOME_TOTAL + 1)` | +1 risk | Fixed Obligation Income Ratio (FOIR). Higher = more cash constrained. |
| `CREDIT_TO_GOODS` | `AMT_CREDIT / (AMT_GOODS_PRICE + 1)` | +1 risk | Loan-to-Value proxy (LTV). Over-borrowing relative to asset value. |
| `CREDIT_TO_ANNUITY` | `AMT_CREDIT / (AMT_ANNUITY + 1)` | derived | Loan tenor proxy. |
| `AGE_YEARS` | `-DAYS_BIRTH / 365.25` | -1 risk | Older applicants historically lower default risk. |
| `EMPLOYED_YEARS` | `-DAYS_EMPLOYED / 365.25` | -1 risk | Longer employment = more job stability. |
| `EXT_SOURCE_MEAN` | mean(EXT_SOURCE_1, 2, 3) | -1 risk | External credit score composite (higher = better credit). |
| `EXT_SOURCE_STD` | std(EXT_SOURCE_1, 2, 3) | derived | Score volatility across bureaus. |
| `INCOME_PER_PERSON` | `AMT_INCOME_TOTAL / (CNT_FAM_MEMBERS + 1)` | -1 risk | Per-capita household income. |

### 4.2 Bureau-Level Features (via bureau + bureau_balance)

Processing chain: `bureau_balance.csv` (27.3M rows) → aggregate to `SK_ID_BUREAU` → merge into `bureau.csv` → aggregate to `SK_ID_CURR`

| Feature | Source | Meaning |
|---|---|---|
| `BUREAU_COUNT` | bureau | Total external credit accounts |
| `BUREAU_ACTIVE_COUNT` | bureau | Active credit accounts |
| `BUREAU_OVERDUE_COUNT` | bureau | Accounts with overdue balance > 0 |
| `BUREAU_OVERDUE_RATIO` | bureau | Fraction of accounts overdue |
| `BUREAU_AMT_OVERDUE` | bureau | Total overdue balance |
| `BUREAU_AMT_CREDIT_SUM` | bureau | Total external credit outstanding |
| `BB_DPD_RATIO_MEAN` | bureau_balance | Mean fraction of months in DPD across all bureau accounts |

### 4.3 Previous Application Features

| Feature | Meaning |
|---|---|
| `PREV_COUNT` | Number of previous HC applications |
| `PREV_REFUSAL_COUNT` | Times previously refused |
| `PREV_REFUSAL_RATE` | Fraction refused (+1 risk direction) |
| `PREV_CREDIT_SUM` | Total credit in previous applications |
| `PREV_DAYS_DECISION_MEAN` | Mean days since previous decision |

### 4.4 Instalment Payment Features

| Feature | Meaning |
|---|---|
| `INST_COUNT` | Number of scheduled instalments |
| `INST_LATE_COUNT` | Instalments paid late (DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT) |
| `INST_LATE_RATIO` | Fraction of late payments (+1 risk) |
| `INST_DAYS_LATE_MEAN` | Average days late |
| `INST_UNDERPAY_RATIO` | Fraction of instalments underpaid |

### 4.5 Credit Card Balance Features

| Feature | Meaning |
|---|---|
| `CC_MONTHS` | Months of CC history |
| `CC_BALANCE_MEAN` | Average monthly balance |
| `CC_UTILIZATION_MEAN` | Average balance / limit (+1 risk) |
| `CC_DPD_COUNT` | Months with DPD > 0 |
| `CC_DPD_RATIO` | Fraction of months in DPD (+1 risk) |

### 4.6 POS / Cash Loan Features

| Feature | Meaning |
|---|---|
| `POS_MONTHS` | Months of POS/cash loan history |
| `POS_DPD_COUNT` | Months in DPD |
| `POS_IS_DPD_RATIO` | Fraction in DPD (+1 risk) |

### 4.7 Composite Behavioural Feature

```
BEHAVIORAL_RISK_SCORE = 
    0.4 × INST_LATE_RATIO
  + 0.3 × CC_DPD_RATIO
  + 0.2 × POS_IS_DPD_RATIO
  + 0.1 × BUREAU_OVERDUE_RATIO
```

Weights reflect data volume and signal strength (installments > CC > POS > bureau_balance). Range [0, 1]. Higher = greater payment stress history.

---

## 5. Final Feature Matrix

| Stat | Value |
|---|---|
| Total columns after merge | 158 |
| Numeric features used | 140 |
| Dropped (non-numeric / ID cols) | 18 |
| Feature source breakdown | application_raw: 90, application_engineered: 18, bureau: 13, installments: 5, credit_card: 5, previous: 5, pos_cash: 3, behavioral_composite: 1 |

---

## 6. Train/Val/Test Split

| Split | Rows | Default Rate |
|---|---|---|
| Train (60%) | 184,506 | 0.0807 |
| Val (20%) | 61,502 | 0.0807 |
| Test (20%) | 61,503 | 0.0807 |

- Method: Stratified 60/20/20 (sklearn `train_test_split`, `random_state=42`, `stratify=y`)
- DR perfectly balanced across splits (stratification confirmed)
- `scale_pos_weight` for GBMs: (y==0).sum() / (y==1).sum() ≈ **11.39**

---

## 7. Evidence Files

| File | Location |
|---|---|
| Data audit JSON | `outputs/evidence/g9a_home_credit_data_audit.json` |
| Feature factory report | `outputs/evidence/g9a_feature_factory_report.json` |
| Processed splits | `outputs/data/g9a_splits.pkl` |
| Intermediate parquets | `outputs/data/bb_agg.parquet`, `bureau_agg.parquet`, `prev_agg.parquet`, `inst_agg.parquet`, `cc_agg.parquet`, `pos_agg.parquet` |

---

*Part of PulseGuard G9A Gate — Home Credit as primary spine.*
