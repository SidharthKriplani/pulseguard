# G5.5 — DATASET DECISION MATRIX
## PulseGuard · Public Credit Dataset Selection

**Gate:** G5.5 — Public/Realistic Data Lane Evaluation
**Status:** COMPLETE
**Date:** June 2026

---

## SCORING LEGEND

Scores are 1–5 for each dimension (5 = excellent, 1 = poor/not applicable).

**Business realism score:** composite assessment of how defensible this dataset is in a senior credit risk ML interview at a bank, fintech, or NBFC.

**Implementation cost:** 1=trivial (no-auth, single file), 5=high (auth required, multi-table, large data engineering effort).

---

## DECISION MATRIX

| # | Dataset | Source / Access Method | Row Count | Target / Outcome | Feature Richness (1–5) | Temporal Fields | Protected / Proxy Attributes | Missingness Realism (1–5) | Suitability: Default Modeling (1–5) | Suitability: Fairness Audit (1–5) | Suitability: Drift Monitoring (1–5) | Suitability: Reject Inference (1–5) | Business Realism Score (1–5) | Implementation Cost (1–5) | Download Status | Decision |
|---|---------|----------------------|-----------|-----------------|----------------------|----------------|------------------------------|--------------------------|-------------------------------------|------------------------------------|--------------------------------------|--------------------------------------|------------------------------|--------------------------|----------------|----------|
| 1 | **Home Credit Default Risk** | Kaggle (auth required) | 307,511 train + 48,744 test | Binary default (TARGET=1) | **5** — 120+ features, bureau history, prior loan data | Rich: DAYS_BIRTH, DAYS_EMPLOYED, credit bureau timestamps | CODE_GENDER (F/M), DAYS_BIRTH (age), NAME_EDUCATION_TYPE, REGION | **5** — EXT_SOURCE_3 ~50% missing; bureau joins add structural missingness | **5** | **4** — CODE_GENDER + education/region proxies | **4** — 6-table join enables realistic feature-level drift | **3** — accepted applicants only; no rejected pool | **5** | **4** — Kaggle auth, 6-table join engineering | BLOCKED (Kaggle auth) | **USE_LATER** — Primary real-data lane; first choice when accessible |
| 2 | **LendingClub** | Kaggle (auth required) | ~2.26M accepted + ~27.6M rejected | loan_status: Charged Off vs Fully Paid | **4** — grade, sub_grade, FICO, DTI, int_rate, purpose | issue_d, earliest_cr_line, mths_since_* | addr_state (geographic proxy), annual_inc (income proxy); NO explicit demographics | **3** — moderate; emp_length, delinquency history have missing | **4** | **2** — no explicit demographic columns | **4** — issue date enables temporal splits; grade/rate drift | **5** — rejected loan pool (27M rows) enables reject inference | **4** | **4** — Kaggle auth; very large; requires cohort sampling | BLOCKED (Kaggle auth) | **USE_LATER** — Reject inference lane (G9); second priority |
| 3 | **HMDA 2022** | CFPB public (no auth) | ~12M applications | action_taken: denied vs originated | **2** — limited application features; no credit bureau data | Application date, property year | **5** — race, sex, ethnicity (mandatory HMDA disclosure); age bands | **2** — mandatory fields complete; voluntary demographics have suppression | **1** — NO DEFAULT OUTCOME; approval outcome only | **5** — real regulatory-grade demographics | **2** — no performance-based drift; approval rate drift only | **1** — N/A (no loan performance) | **4** — high regulatory relevance; ECOA/FHA alignment | **3** — no auth but very large (millions of rows); complex schema | ACCESSIBLE but complex | **USE_LATER** — Fairness/approval-rate lane only; not default modeling |
| 4 | **FICO HELOC** | FICO Explainability Challenge (PRIMARY PAGE OFFLINE) | ~10,459 | RiskPerformance: Good vs Bad | **2** — 23 anonymized bureau metrics | 6-month implied window; no explicit dates | **1** — NO demographic variables (anonymized) | **4** — structured missingness codes (-7/-8/-9) realistic for bureau data | **3** — real credit performance; but small and anonymized | **1** — no demographics | **2** — small; anonymized features; no temporal index | **1** — N/A (no rejected pool) | **2** — small, anonymized, outdated challenge | **2** — primary source offline; secondary mirrors exist | NOT DIRECTLY ACCESSIBLE | **FALLBACK** — small, no demographics; offline; use only if all else fails |
| 5 | **Give Me Some Credit** | Kaggle (auth required) | 150,000 train | SeriousDlqin2yrs: 90+ day delinquency in 2 years | **2** — 10 features only | None (cross-section snapshot) | age (explicit); no sex/race/geography | **3** — MonthlyIncome 20% missing; realistic | **3** — real US consumer default labels; simple feature set | **2** — age only; limited fairness scope | **2** — no temporal structure; single snapshot | **1** — N/A | **3** — legitimate competition data; simpler than Home Credit | **3** — Kaggle auth; single file | BLOCKED (Kaggle auth) | **FALLBACK** — simpler than Home Credit; good backup if all else fails |
| 6 | **Taiwan Default** ⭐ | UCI ML Repository (NO AUTH) | **30,000** | default payment next month (binary) | **3** — 23 features; 6-month payment panel; single table | **6-month panel** (PAY_0–6, BILL_AMT1–6, PAY_AMT1–6): realistic temporal structure | **SEX** (male/female), **EDUCATION** (4 levels), **MARRIAGE** (3 types), **AGE** (21–79) | **1** — zero null values (data quality issues in EDUCATION/MARRIAGE codes instead) | **4** — real credit card default labels; reasonable feature set | **4** — real SEX, AGE, EDUCATION, MARRIAGE; noticeable default rate gap by sex (M 24.2% vs F 20.8%) | **4** — 6-month payment panel enables realistic temporal/drift experiments | **2** — no rejected pool | **3** — credit card (not consumer loan); Taiwan market; 2005 data; smaller than Home Credit | **1** — UCI, HTTP direct download, single XLS file; already downloaded | ✓ DOWNLOADED | **USE_NOW** ⭐ — immediate real-data integration; real labels, real demographics, no auth |
| 7 | **German Credit** | UCI Statlog (NO AUTH) | **1,000** | creditworthiness: good (1) vs bad (2) | **1** — 20 cryptic features; 1994 German bank data | None | Age (explicit); sex (categorical in some encodings) | **1** — low missingness; but ancient data | **1** — too small; 1994 data; 30% default rate unrealistic | **2** — age/sex present but sample too small | **1** — no temporal structure | **1** — N/A | **1** — recognized as toy dataset by any senior interviewer | **1** — single file, no auth | ACCESSIBLE | **EXCLUDE** — 1,000 rows; 1994 data; toy scale; interview-damaging if cited as primary |

---

## DECISION RATIONALE

### Why Taiwan Default → USE_NOW

Taiwan Default is the only dataset that simultaneously satisfies:
1. **Downloaded, verified, ready** — `data/public/taiwan_credit_default.xls` exists (5.5MB, 30,000 rows confirmed)
2. **Real default labels** — binary outcome from actual credit card payments; no synthetic DGP ceiling
3. **Real demographic variables** — SEX, AGE, EDUCATION, MARRIAGE are all present and usable
4. **Temporal structure** — 6-month payment panel enables realistic temporal feature engineering and drift simulation
5. **No authentication barrier** — UCI, direct download, reproducible by anyone reviewing the portfolio
6. **Genuine demographic signal** — male default rate (24.2%) significantly exceeds female (20.8%), creating a real fairness analysis story

**Trade-off acknowledged:** Credit card default prediction (Taiwan, 2005) is a different financial product and geography than consumer loan default (Home Credit, Eastern Europe, 2016). The dataset decision matrix records this honestly. PulseGuard's claim boundary will reflect: "Taiwan credit card default data — not Home Credit." This is not a deficiency; it proves the pipeline works on real data with a clear data provenance statement.

### Why Home Credit → USE_LATER (not USE_NOW)

Home Credit remains the ideal primary real-data lane because:
- It matches the synthetic DGP structure exactly (same feature names, same default rate, same context)
- It is the dataset for which the source-reference metrics (SR-1: AUC 0.7663) were computed
- Re-running G4–G6 on Home Credit would directly enable comparison against SR-1 through SR-7

However, Kaggle CLI is unavailable in the automated environment. Manual download requires user action. Decision: document the path, integrate when available.

### Why LendingClub → USE_LATER (reject inference lane)

LendingClub's unique value is the rejected loan pool — the only public dataset with both accepted-and-funded applications and rejected applications. This directly addresses PulseGuard's documented G0 limitation (reject inference). This belongs in a G9 extension, not in the G6 champion/challenger evaluation.

### Why German Credit → EXCLUDE

Any senior credit risk interviewer will recognize German Credit as a 1,000-row demo dataset from 1994. Citing it as primary evidence would undermine credibility rather than establish it.

---

## TWO-LANE ARCHITECTURE (POST G5.5)

| Lane | Dataset | Role | Gates |
|------|---------|------|-------|
| **Synthetic harness** | `synthetic_home_credit_like` (DGP) | Injected failure testing; controlled leakage/drift/calibration protocol | G3, G3.1, G4 drift simulation, G5 proxy fairness |
| **Real data (immediate)** | Taiwan Default (`data/public/taiwan_credit_default.xls`) | Business-realistic champion/challenger evaluation; real demographic fairness | G6, G7 (decision engine) |
| **Real data (future)** | Home Credit (Kaggle) | Source-reference reproduction; gold-standard portfolio claim | G4–G6 re-run when accessible |
| **Reject inference** | LendingClub rejected pool | Selection bias correction, reject inference extension | G9 |
| **Approval fairness** | HMDA | Regulatory-grade fairness on lending decisions | G9+ |

---

## INTERVIEW CLAIM TRANSITION (POST G5.5)

### Before G5.5 (synthetic only):
> "PulseGuard trains on synthetic_home_credit_like data modeled after Home Credit's feature structure."

### After G5.5 + Taiwan integration (recommended):
> "PulseGuard has two data lanes. The synthetic lane uses a calibrated logistic DGP to test protocol correctness — injected leakage, controlled drift, proxy fairness. The real-data lane uses the UCI Taiwan credit card default dataset (30,000 clients, 6-month payment history, real demographic variables: sex, age, education) to produce business-credible champion/challenger evaluation and genuine fairness analysis. When Home Credit becomes available, the pipeline runs identically — only the data source changes."

---

## FORBIDDEN CLAIMS AFTER G5.5

- Do NOT claim Taiwan results as "Home Credit results"
- Do NOT claim Taiwan credit card default patterns are representative of consumer loan default (different product, geography, year)
- Do NOT use Taiwan demographic fairness findings to make claims about real populations
- Do NOT remove the synthetic harness; it remains the controlled failure-mode test environment
