# G5.5 — PUBLIC CREDIT DATASET RESEARCH
## PulseGuard · Dataset Realism Gate

**Gate:** G5.5 — Public/Realistic Data Lane Evaluation
**Status:** COMPLETE
**Date:** June 2026

---

## CONTEXT

G1 through G5 established a fully governed synthetic harness: calibrated 8% DGP, injected leakage, drift simulation, proxy fairness audit. The synthetic lane is retained as a controlled failure-mode testing environment. G5.5 adds a separate research layer to evaluate which public credit datasets should supply the realistic data lane for G6 and beyond.

**Two-lane architecture (post G5.5):**

| Lane | Role | Data |
|------|------|------|
| Synthetic harness | Injected failure testing; controlled protocol checks | `synthetic_home_credit_like` (DGP) |
| Real/public data | Business-realistic modeling, credible evaluation, interview defensibility | Public dataset (selected here) |

---

## 1. HOME CREDIT DEFAULT RISK

**Source:** Kaggle competition `home-credit-default-risk`
**URL:** https://www.kaggle.com/c/home-credit-default-risk
**Access:** Kaggle authentication required (CLI or manual download)
**Download status in this environment:** NOT AVAILABLE (Kaggle CLI not installed; manual download requires user action)

### Schema
- **Primary table:** `application_train.csv` — 307,511 rows × 122 columns
- **Supplementary tables:** bureau.csv, bureau_balance.csv, previous_application.csv, credit_card_balance.csv, POS_CASH_balance.csv, installments_payments.csv
- **Target:** `TARGET` (1=defaulted, 0=did not default)
- **Default rate:** ~8.07% (consistent with PulseGuard synthetic DGP target)

### Feature Richness
- 120+ features in application table alone; hundreds more via joins
- Strong signals: EXT_SOURCE_1/2/3 (external bureau scores), DAYS_EMPLOYED, AMT_INCOME_TOTAL, AMT_CREDIT
- Credit bureau history: 6 months bureau balance snapshots per loan
- Previous application history
- Point-of-sale and installment payment history

### Temporal Fields
- APPLICATION_DATE (implicit), DAYS_BIRTH, DAYS_EMPLOYED, DAYS_REGISTRATION, DAYS_ID_PUBLISH
- Credit bureau: DAYS_CREDIT, DAYS_CREDIT_ENDDATE, DAYS_OVERDUE_DAYS
- Rich temporal structure across multiple tables

### Protected / Proxy Attributes
- CODE_GENDER (F/M) — explicit sex proxy
- NAME_INCOME_TYPE, NAME_EDUCATION_TYPE, NAME_FAMILY_STATUS — socioeconomic proxies
- REGION_RATING_CLIENT — geographic proxy
- DAYS_BIRTH (age proxy)

### Missingness Realism
- EXT_SOURCE_3: ~50% missing (most realistic missingness in dataset)
- EXT_SOURCE_1: ~56% missing
- AMT_GOODS_PRICE: ~0.1% missing
- OCCUPATION_TYPE: ~31% missing
- Bureau table: many applicants have no bureau history → complex join missingness

### Why This Dataset Is the Gold Standard
1. It is the source for PulseGuard's synthetic DGP — the synthetic data was designed to mimic this dataset's feature structure and default rate
2. Matching the RiskFrame source-reference AUC (0.7663) requires this exact dataset
3. Default rate 8% matches the calibrated synthetic DGP
4. Most feature-rich public credit default dataset
5. Has bureau-level credit history → enables realistic temporal feature engineering

### Limitations
- Requires Kaggle authentication → blocked in current automated environment
- Multi-table join required to reproduce RiskFrame feature engineering
- Large: 307k training + 48k test rows, 6 supplementary tables
- The source-reference metrics (SR-1 through SR-7) were computed on this dataset

### Decision: **USE_LATER** (blocked by Kaggle auth; first choice when accessible)
**Manual access path:** User downloads from https://www.kaggle.com/c/home-credit-default-risk/data → saves to `data/real/home_credit/`

---

## 2. LENDINGCLUB ACCEPTED/REJECTED LOANS

**Source:** Kaggle dataset `wordsforthewise/lending-club` (accepted) + `jenniferli/lending-club` (rejected)
**URL:** https://www.kaggle.com/datasets/wordsforthewise/lending-club
**Access:** Kaggle authentication required
**Download status:** NOT AVAILABLE (Kaggle auth required)

### Schema
- **Accepted loans:** ~2.26M rows × 150 columns (2007–2018)
- **Rejected loans:** ~27.6M rows × 9 columns (2007–2018) — crucial for reject inference
- **Target (accepted):** `loan_status` → "Charged Off" (default) vs "Fully Paid"
- **Default rate:** ~15–20% on accepted portfolio (varies by cohort year and grade)

### Feature Richness
- `grade`, `sub_grade` (A1–G5): lender's own risk tier — high predictive power
- `int_rate`: interest rate reflects lender risk perception
- `annual_inc`, `dti` (debt-to-income): income and leverage
- `emp_length`: employment stability
- `purpose`: loan purpose (debt consolidation, home improvement, etc.)
- `fico_range_low/high`: FICO score at origination — gold-standard credit signal
- `revol_util`, `revol_bal`: revolving credit utilization
- Installment history, payment history for mature loans

### Temporal Fields
- `issue_d` (loan issue date), `earliest_cr_line` (credit history length)
- Payment dates, last payment date
- Enables realistic time-window training / temporal split validation

### Protected / Proxy Attributes
- No explicit sex/race columns (consumer credit law compliance)
- `addr_state` (geographic proxy → redlining risk)
- `zip_code` (geographic proxy)
- `annual_inc` (income proxy for socioeconomic status)
- `home_ownership` (socioeconomic proxy)

### Missingness Realism
- Moderate: emp_length, mths_since_last_delinq, mths_since_last_record have significant missingness
- FICO scores present for nearly all records (required at origination)
- Rejected loan table: very sparse (only 9 columns; no loan performance data available)

### Unique Strength: Reject Inference
LendingClub is the only major public dataset that provides both:
1. Accepted loans with performance outcomes (Charged Off / Fully Paid)
2. Rejected applications (application features, rejection reason)

This enables reject inference experimentation: estimating default probability for the rejected population using semi-supervised or propensity-weighting methods. This is a documented G0 limitation of PulseGuard.

### Limitations
- Kaggle auth required
- LendingClub ceased consumer lending in 2021; no new data expected
- Accepted loans are a selection-biased sample (only loans LendingClub chose to fund)
- `grade` and `sub_grade` are lender-assigned → leakage risk if used naively
- Very large dataset (2.26M rows) → sampling required
- No explicit demographic columns → limited for demographic fairness audit

### Decision: **USE_LATER** (second priority; most valuable for reject inference lane; blocked by Kaggle auth)

---

## 3. HMDA — HOME MORTGAGE DISCLOSURE ACT

**Source:** CFPB public data
**URL:** https://ffiec.cfpb.gov/data-publication/
**Access:** Publicly available (no auth); CSV download via CFPB API
**Download status:** ACCESSIBLE (CFPB makes data public) — but requires large-file handling

### Schema
- **2022 National LAR (Loan Application Register):** ~12M mortgage applications
- **Key outcome column:** `action_taken` (1=originated, 2=approved but not accepted, 3=denied, 4=withdrawn, 5=incomplete, 6=purchased, 7=pre-approval denied, 8=pre-approval approved)
- **Target for fairness:** `action_taken == 3` (denied) vs `action_taken == 1` (originated)
- **This is an APPROVAL dataset, NOT a default dataset**

### Feature Richness
- Loan amount, loan type (conventional/FHA/VA/USDA), loan purpose
- Property type, lien status
- Income, debt-to-income ratio (DTI)
- CLTV (combined loan-to-value ratio)
- Census tract (geographic detail)
- Co-applicant information
- Total units

### Protected Attributes (EXPLICITLY PRESENT)
- `derived_race`, `derived_sex`, `derived_ethnicity` — mandatory HMDA disclosure fields
- `applicant_age` (age bands), `co_applicant_age`
- These are actual regulatory reporting fields under ECOA and FHA

### Missingness
- Mandatory fields (loan amount, action taken, income): near-complete
- Voluntary fields (race/ethnicity when applicant declines): some suppression
- DTI: often missing for non-originated loans

### Critical Limitation: No Default Outcome
HMDA records loan application outcomes (approved/denied), not loan performance (default/no default). This means:
- HMDA CANNOT be used for default risk modeling
- HMDA IS appropriate for denial rate analysis and fairness audit on lending decisions
- The fairness methodology differs: disparate impact on denial rates, not model scores

### Business Realism
HMDA is the most legally and regulatorily significant fairness dataset in US credit:
- Banks file HMDA under the Home Mortgage Disclosure Act of 1975
- CFPB actively analyzes HMDA for disparate impact evidence
- Using HMDA methodology in PulseGuard signals genuine regulatory awareness

### Decision: **USE_LATER** (fairness/approval-rate lane only; complex schema; not default modeling)

---

## 4. FICO HELOC (HOME EQUITY LINE OF CREDIT)

**Source:** FICO Explainability Challenge (2018)
**URL:** https://community.fico.com/s/explainability-challenge (HTTP 404 — PAGE OFFLINE)
**Access:** UNAVAILABLE — FICO community page no longer exists at this URL
**Download status:** NOT DIRECTLY ACCESSIBLE

### Schema (from published papers)
- ~10,459 rows × 24 features
- **Target:** `RiskPerformance` (Good / Bad) — missed payment in 24 months
- Default rate (Bad): ~23%

### Feature Richness
- 23 anonymized features: ExternalRiskEstimate, MSinceMostRecentInqexcl7days, PercentInstallTrades, NumTrades90Ever, etc.
- All features are credit bureau metrics (credit utilization, delinquency counts, account age)
- Features are numeric only; some have structured missingness encoded as -7, -8, -9 (special codes for "not applicable", "condition not met", "no bureau record")

### Protected / Proxy Attributes
- **NONE** — all features are anonymized bureau metrics
- Cannot support demographic fairness analysis
- This was by design for the explainability challenge (focus on model explanation, not fairness)

### Missingness Realism
- Structured missingness (special codes) is realistic for credit bureau data
- Requires specific imputation strategies for -7/-8/-9

### Limitations for PulseGuard
- FICO page is offline; access requires finding a secondary source (GitHub mirrors, research papers)
- No demographic attributes → cannot demonstrate fairness methodology
- Only 10k rows → limited for champion/challenger evaluation
- Anonymized features → hard to tell realistic credit stories in interview
- Single-table, no temporal structure beyond 6-month window implied by feature names

### Decision: **FALLBACK** (accessible via secondary sources if needed; too small; no demographics; primary page offline)

---

## 5. GIVE ME SOME CREDIT (KAGGLE)

**Source:** Kaggle competition `GiveMeSomeCredit` (2011)
**URL:** https://www.kaggle.com/c/GiveMeSomeCredit
**Access:** Kaggle authentication required
**Download status:** NOT AVAILABLE (HTTP 403 on direct data download)

### Schema
- **Training set:** 150,000 rows × 11 columns
- **Test set:** 101,503 rows (no labels; competition held-out)
- **Target:** `SeriousDlqin2yrs` (1 = 90+ days past due in next 2 years)
- **Default rate:** ~6.68% (training set)

### Feature Richness
- 10 features only:
  - `RevolvingUtilizationOfUnsecuredLines`: revolving credit utilization (0–1)
  - `age`: age in years (explicit demographic variable)
  - `NumberOfTime30-59DaysPastDueNotWorse`, `NumberOfTime60-89DaysPastDueNotWorse`, `NumberOfTimes90DaysLate`: delinquency history
  - `NumberOfOpenCreditLinesAndLoans`, `NumberOfRealEstateLoansOrLines`: credit accounts
  - `DebtRatio`: total monthly debt / gross monthly income
  - `MonthlyIncome`: monthly income (20% missing)
  - `NumberOfDependents`: household size (2.6% missing)
- Simple compared to Home Credit or LendingClub

### Protected / Proxy Attributes
- `age` — explicit demographic variable; useful for age fairness analysis
- `NumberOfDependents` — household size proxy
- No sex, race, or geography

### Missingness Realism
- `MonthlyIncome`: ~20% missing (realistically motivated — some borrowers don't disclose)
- `NumberOfDependents`: ~2.6% missing
- Well-suited for demonstrating realistic imputation strategies

### Business Realism
- US consumer credit behavior (bureau-like data)
- Simple enough to explain fully in an interview
- 6.68% default rate is close to Home Credit's 8% target

### Decision: **FALLBACK** (blocked by Kaggle auth; feature-poor vs Home Credit; good backup if Home Credit remains inaccessible)

---

## 6. TAIWAN DEFAULT OF CREDIT CARD CLIENTS

**Source:** UCI Machine Learning Repository
**URL:** https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients
**Data URL:** https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls
**Access:** NO AUTHENTICATION REQUIRED — direct HTTP download (HTTP 200 confirmed)
**Download status:** DOWNLOADED AND VERIFIED (5.5MB XLS → `data/public/taiwan_credit_default.xls`)

### Verified Schema (from actual data inspection)
- **Rows:** 30,000 credit card clients
- **Features:** 23 (excluding ID and target)
- **Target:** `default payment next month` (binary: 1=default, 0=no default)
- **Default rate:** **22.12%** (6,636 defaults / 30,000)
- **Missing values:** 0 (no missingness in primary features)
- **File size:** 5,539,328 bytes (5.5 MB)

### Feature Structure
| Feature Group | Columns | Description |
|---------------|---------|-------------|
| Credit profile | LIMIT_BAL | Credit limit in NT dollars |
| Demographics | SEX, EDUCATION, MARRIAGE, AGE | Explicit demographic variables |
| Payment status | PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6 | Monthly repayment status (6 months) |
| Bill statements | BILL_AMT1–6 | Statement amounts (Sep–Apr) |
| Payments made | PAY_AMT1–6 | Previous payments (Sep–Apr) |

**PAY_X encoding:** -2=no consumption, -1=paid duly, 0=minimum paid/revolving, 1=1-month delay, 2=2-month delay, ..., 9=9+ month delay

### Temporal Structure
6 consecutive months of payment behavior (April–September):
- PAY_0 = September (most recent); PAY_6 = April (oldest)
- BILL_AMT1–6 and PAY_AMT1–6 mirror this monthly structure

This is a **realistic temporal panel** — each client row contains a 6-month behavior history leading up to the default observation window.

### Protected / Proxy Attributes (VERIFIED)
| Attribute | Encoding | Default Rate by Group |
|-----------|----------|-----------------------|
| SEX | 1=male (11,888), 2=female (18,112) | Male: 24.2%, Female: 20.8% |
| EDUCATION | 1=graduate (35%), 2=university (47%), 3=high school (16%), 4-6/0=other | Varies by education level |
| MARRIAGE | 0=unknown (0.2%), 1=married (46%), 2=single (53%), 3=other (1%) | Varies |
| AGE | Range 21–79; median ~35 | Varies by decade |

**Notable:** Male default rate (24.2%) is significantly higher than female (20.8%) — a genuine demographic signal worth investigating in G5.5+ fairness work.

### Data Quality Notes
- EDUCATION has 465 rows with values 0, 5, or 6 (undocumented in paper → treat as "other" or impute)
- MARRIAGE has 54 rows with value 0 (undocumented → treat as "unknown")
- No explicit credit bureau features (simpler feature set than Home Credit)
- Single-table, no join required

### Missingness Realism
- **0 null values** — unlike Home Credit, all fields are complete
- Data quality issues instead come from coding anomalies (undocumented EDUCATION/MARRIAGE values)
- Less missingness realism than Home Credit, but more realistic than PulseGuard's synthetic DGP

### Business Context
- Credit card default prediction
- Taiwan credit card market (2005 data, Yeh & Lien 2009 paper)
- Product type differs from Home Credit (consumer loans) → default rate higher (22% vs 8%)
- Same financial services discipline: credit risk scoring, payment behavior modeling

### What This Enables Immediately
1. **Real default labels** → no synthetic DGP ceiling limitation
2. **Real demographic variables** (SEX, AGE, EDUCATION, MARRIAGE) → genuine fairness analysis
3. **Real temporal feature structure** → realistic drift simulation
4. **Real feature distributions** → defensible interview claims
5. **No Kaggle auth required** → available right now

### Decision: **USE_NOW** (immediate real-data integration; primary realistic lane until Home Credit becomes accessible)

---

## 7. GERMAN CREDIT (UCI STATLOG)

**Source:** UCI Machine Learning Repository (Statlog)
**URL:** https://archive.ics.uci.edu/ml/datasets/statlog+(german+credit+data)
**Access:** No authentication required (HTTP 200 verified)
**Download status:** AVAILABLE (102KB)

### Schema
- **Rows:** 1,000 credit applications
- **Features:** 20 (mix of numeric and categorical)
- **Target:** 1=good credit, 2=bad credit (1,000 records: 700 good, 300 bad)
- **Default rate:** 30%

### Why This Dataset Is Inadequate for Gold-Level Evidence
1. **1,000 rows is toy scale** — confidence intervals on AUC at 1k rows are ±3–5%, making champion/challenger comparisons statistically meaningless
2. Produced in 1994 using German savings bank data — extremely outdated
3. Features are cryptic (A11, A12...) or poorly documented
4. Default rate of 30% is unrealistically high for modern credit
5. Used as a demo dataset in academic papers since the 1990s — interviewers will recognize it immediately as a toy example
6. No meaningful temporal structure
7. No proper credit bureau features

### Decision: **EXCLUDE** — 1,000 rows is not interview-defensible for a gold-standard credit risk platform

---

## 8. CROSS-DATASET COMPARISON SUMMARY

| Dataset | Rows | Default Rate | Demographics | Temporal | Missing | Auth | Download Status |
|---------|------|-------------|-------------|---------|---------|------|-----------------|
| Home Credit | 307,511 | 8.1% | CODE_GENDER + proxies | Rich (bureau history) | High (EXT_SOURCE_3: 50%) | Kaggle | BLOCKED |
| LendingClub | 2.26M accepted + 27M rejected | 15–20% | Geographic proxies only | Yes (issue_d, credit history) | Moderate | Kaggle | BLOCKED |
| HMDA 2022 | ~12M | N/A (approval, not default) | Race, sex, ethnicity (mandatory) | Application date | Low | None (CFPB) | ACCESSIBLE (large) |
| FICO HELOC | 10,459 | ~23% | None (anonymized) | Implied 6-month | Structured codes | FICO site | OFFLINE |
| Give Me Some Credit | 150,000 | 6.7% | Age only | None | MonthlyIncome 20% | Kaggle | BLOCKED |
| **Taiwan Default** | **30,000** | **22.1%** | **SEX, AGE, EDUCATION, MARRIAGE** | **6-month payment history** | **None** | **None (UCI)** | **✓ DOWNLOADED** |
| German Credit | 1,000 | 30% | Age, sex | None | Low | None (UCI) | ACCESSIBLE |

---

## 9. IMMEDIATE ACTION ITEMS (POST G5.5)

1. **Taiwan Default integration** — already downloaded to `data/public/taiwan_credit_default.xls`. Build a parallel real-data feature pipeline for G6.

2. **Home Credit manual download** — user should download from https://www.kaggle.com/c/home-credit-default-risk/data and save to `data/real/home_credit/`. Once available, this becomes the primary real-data lane matching the source-reference metrics.

3. **LendingClub for reject inference** — when Home Credit is available, LendingClub's rejected loan dataset becomes the reject inference extension for G9.

4. **HMDA fairness extension** — post-G6, integrate HMDA's denial rate data as a fairness benchmark for the approval decision lane (not default modeling).
