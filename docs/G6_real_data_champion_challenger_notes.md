# G6 — Real-Data Champion/Challenger Notes
## PulseGuard · Taiwan Default (PUBLIC_REAL_TAIWAN_DEFAULT)

**Gate:** G6 — Champion/Challenger on Real Data
**Status:** COMPLETE
**Date:** June 2026
**Data tag:** `PUBLIC_REAL_TAIWAN_DEFAULT`

---

## 1. Scope and Lane Assignment

Per G5.5 accepted architecture:

| Lane | Data | Role |
|------|------|------|
| **Real-data lane (primary G6 evidence)** | Taiwan Default (UCI) | Champion/challenger evaluation, calibration, threshold analysis |
| Synthetic harness (retained) | `synthetic_home_credit_like` | Injected failure tests only — leakage traps, drift injection, proxy fairness |

**Hard boundary:** G6 synthetic data metrics (ROC-AUC=0.6237 from G4) are NOT compared against G6 Taiwan metrics (ROC-AUC=0.7852). They are on different datasets with fundamentally different signal structures.

---

## 2. Dataset Provenance

| Property | Value |
|----------|-------|
| Source | UCI ML Repository (no auth) |
| File | `data/public/taiwan_credit_default.xls` |
| Rows | 30,000 |
| Features | 23 (after dropping ID) |
| Target | `default payment next month` (binary, 1=default) |
| Default rate | 22.12% (all splits: train/val/test ≈ 22.12%) |
| Missing values | 0 |
| Vintage | April–September 2005 |
| Geography | Taiwan |
| Product | Credit card revolving credit |
| Citation | Yeh & Lien (2009), Expert Systems with Applications 36(2), 2473–2480 |

**Known data quality notes:**
- EDUCATION codes 0, 5, 6 are undocumented in the original paper (affect 468 rows, 1.56%)
- MARRIAGE code 0 is undocumented (54 rows, 0.18%)
- PAY_AMT values of 0 may indicate no payment made vs. missing — treated as-is
- BILL_AMT values can be negative (credit balance after overpayment) — retained

---

## 3. Feature Set

**Input:** 23 columns from XLS (ID dropped before modeling)

**Categorical features (OneHotEncoded, handle_unknown=ignore):**
- `SEX` — 1=male, 2=female
- `EDUCATION` — 1=graduate school, 2=university, 3=high school, 4=others
- `MARRIAGE` — 1=married, 2=single, 3=others

**Numeric features (StandardScaler):**
- `LIMIT_BAL` — credit limit (NT$)
- `AGE` — age in years
- `PAY_0`, `PAY_2`–`PAY_6` — repayment status for Sep–Apr 2005 (ordinal; treated as numeric)
- `BILL_AMT1`–`BILL_AMT6` — bill statement amounts Sep–Apr 2005 (NT$)
- `PAY_AMT1`–`PAY_AMT6` — previous payment amounts Sep–Apr 2005 (NT$)

**Total post-OHE features:** ~29 (3 categoricals expand to ~9 columns via OHE; 17 numeric = 26 numeric total)

**Note:** PAY_0 through PAY_6 are ordinal payment status codes (-2 to 8). They are treated as numeric here. Their information content is strong — 6-month payment history is the primary default signal.

---

## 4. Split Discipline

| Split | Rows | Default Rate |
|-------|------|--------------|
| Train | 18,000 (60%) | 22.12% |
| Validation | 6,000 (20%) | 22.12% |
| Test | 6,000 (20%) | 22.12% |

**Method:** `train_test_split(stratify=y, random_state=42)` twice. Preprocessor fit on train only. Calibration fit on val only. All final metrics reported on held-out test only.

---

## 5. Models Trained

### 5.1 Logistic Regression (Baseline / Scorecard-Style)
- `LogisticRegression(C=0.1, class_weight='balanced', solver='lbfgs', max_iter=1000)`
- Represents a simpler linear-in-log-odds scorecard approach
- No calibration applied (LR outputs are probability-calibrated by construction)

### 5.2 XGBoost (Champion Candidate)
- `XGBClassifier(n_estimators=500, max_depth=5, lr=0.05, subsample=0.8, colsample_bytree=0.8)`
- `scale_pos_weight` = n_neg/n_pos to handle class imbalance
- `eval_metric=aucpr`, `early_stopping_rounds=50` on validation set
- **Best iteration: 57** (real data requires more trees than synthetic G4 — iteration 9 vs 57)
- Followed by **Platt sigmoid calibration** on validation set

### 5.3 LightGBM (Challenger)
- `LGBMClassifier(n_estimators=500, max_depth=5, lr=0.05, subsample=0.8, colsample_bytree=0.8)`
- `scale_pos_weight` = n_neg/n_pos
- Early stopping on AUC, 50 rounds
- **Best iteration: 9**
- Not calibrated (no Platt applied; note implication in Section 7)

---

## 6. Evaluation — Test Set Metrics

All metrics evaluated on held-out test set (6,000 rows, 22.12% default rate). Decision threshold = **0.35** (synthetic business threshold; PD ≥ 0.35 → REJECT prediction; not a real underwriting rule).

| Model | ROC-AUC | PR-AUC | Brier ↓ | ECE ↓ | Threshold | Precision | Recall | F1 |
|-------|---------|--------|---------|-------|-----------|-----------|--------|----|
| LR Baseline | 0.7283 | 0.5138 | 0.2047 | 0.2347 | 0.35 | — | — | — |
| XGBoost (raw) | 0.7852 | 0.5709 | 0.1778 | 0.2082 | 0.35 | — | — | — |
| LightGBM | 0.7742 | 0.5525 | 0.1553 | 0.1321 | 0.35 | — | — | — |
| **XGBoost (Platt)** ⭐ | **0.7852** | **0.5709** | **0.1329** | **0.0112** | 0.35 | — | — | — |

*Full confusion matrix values in `g6_champion_challenger_report.json`.*

### Key Findings

**1. Discrimination:** XGBoost and LightGBM both substantially outperform LR. XGBoost ROC-AUC 0.7852 vs. LR 0.7283 — a real signal gap on a harder real-data classification problem.

**2. Calibration gap (raw models):** All raw tree models have very high ECE (0.13–0.23). This is typical: tree models output raw scores that require calibration. LR is already miscalibrated at ECE 0.235 — likely due to class_weight='balanced' adjusting predictions toward 0.5.

**3. Platt calibration effect on champion:** XGBoost ECE drops from 0.2082 → **0.0112** — a **94.6% reduction** in calibration error. This is the largest calibration improvement observed in PulseGuard across any dataset. On real credit data, model scores are systematically biased without calibration — this validates the calibration gate as essential, not cosmetic.

**4. Brier improvement:** Platt also improves Brier: 0.1778 (raw) → 0.1329 (calibrated). This is a holistic improvement in probability accuracy, not just calibration in the narrow ECE sense.

**5. LightGBM naturally better calibrated than raw XGBoost:** LightGBM Brier=0.1553 (better than XGBoost raw 0.1778) and ECE=0.1321 (better than XGBoost raw 0.2082). LightGBM appears to produce more calibrated raw probabilities on this dataset — noted as a fairness point in the challenger assessment.

---

## 7. Champion/Challenger Decision Card

**Champion:** XGBoost (Platt calibrated)

**Promotion rule (4 gates):**
- Gate 1: PR-AUC delta vs. champion ≥ 0.001 (discrimination gate)
- Gate 2: ROC-AUC delta vs. champion ≥ 0.001 (discrimination gate)
- Gate 3: ECE increase ≤ 0.005 vs. champion **(BLOCKING — calibration gate)**
- Gate 4: Brier increase ≤ 0.003

| Challenger | Gate 1 PR-AUC Δ | Gate 2 ROC-AUC Δ | Gate 3 ECE Δ | Gate 4 Brier Δ | Decision |
|------------|----------------|------------------|--------------|----------------|----------|
| LR Baseline | −0.057 ❌ | −0.057 ❌ | +0.223 ❌ | +0.072 ❌ | **REJECT** |
| XGBoost (raw) | 0.000 ❌ | 0.000 ❌ | +0.197 ❌ | +0.045 ❌ | **REJECT** |
| LightGBM | −0.018 ❌ | −0.011 ❌ | +0.121 ❌ | +0.022 ❌ | **REJECT** |

**Decision: XGBoost (Platt calibrated) is retained as champion. No challenger promoted.**

**Important caveat on LightGBM comparison:** LightGBM was evaluated without Platt calibration while the champion has Platt calibration applied. The ECE gate failure for LightGBM (ECE=0.132 vs champion ECE=0.011) partially reflects this asymmetry. A fair comparison would also apply Platt calibration to LightGBM before re-running the gates. This is a documented next-step, not a false finding — it means "the current champion (XGBoost + Platt) is definitively better than uncalibrated LightGBM; whether calibrated LightGBM would exceed calibrated XGBoost on PR-AUC is not yet tested."

**Interview framing of LightGBM result:** "LightGBM challenger was held because it did not improve PR-AUC over the calibrated champion (Δ = −0.018). LightGBM shows better raw calibration than XGBoost before Platt is applied — which suggests a follow-up gate where both models are calibrated and then compared would be valuable at G9."

---

## 8. Calibration Notes

| Metric | XGBoost raw | XGBoost (Platt) | Improvement |
|--------|-------------|-----------------|-------------|
| ECE | 0.2082 | 0.0112 | **94.6% reduction** |
| Brier | 0.1778 | 0.1329 | **25.2% reduction** |
| ROC-AUC | 0.7852 | 0.7852 | unchanged (as expected) |
| PR-AUC | 0.5709 | 0.5709 | unchanged (as expected) |

**Calibration fit:** `CalibratedClassifierCV(xgb_model, cv='prefit', method='sigmoid')` on validation set (6,000 rows). Final ECE evaluated on held-out test set.

**Context:** In G4 (synthetic data), Platt calibration reduced ECE 86% (0.0111 → 0.0016). In G6 (real data), Platt calibration reduces ECE 94.6% (0.2082 → 0.0112). The starting ECE is much higher on real data because XGBoost's raw score range on a complex feature space is more compressed/biased than on a synthetic DGP. Platt's power is clearer on real data.

---

## 9. Comparison with Source Reference (SR-1)

| | This Gate | Source Reference (SR-1) | Notes |
|---|-----------|------------------------|-------|
| Dataset | Taiwan Default (UCI, 30k) | Home Credit (Kaggle, 307k) | Different dataset, product, vintage |
| ROC-AUC | **0.7852** | 0.7663 | Taiwan exceeds SR-1 despite 10× fewer rows |
| PR-AUC | **0.5709** | 0.2611 | Much higher — different base rate (22% vs 8%) |
| ECE (calibrated) | **0.0112** | ~0.0046 | SR-1 ECE is better — likely larger val set |

**Interpretation:** Taiwan Default ROC-AUC (0.7852) exceeds the Home Credit source reference (0.7663). This is expected: Taiwan credit card default has stronger 6-month payment history signals, and the base rate is higher (22% vs 8%), making classification slightly easier. This comparison is NOT "PulseGuard beats RiskFrame" — it is a different dataset. The correct interview answer separates these clearly.

**Do not claim:** "PulseGuard achieves 0.7852 AUC on Home Credit." Taiwan ≠ Home Credit.

---

## 10. Artifacts

| Artifact | Path | Size (approx) |
|----------|------|---------------|
| Data adapter script | `scripts/g6_taiwan_adapter.py` | — |
| Champion/challenger script | `scripts/g6_champion_challenger.py` | — |
| Data profile | `outputs/evidence/g6_taiwan_data_profile.json` | — |
| Champion/challenger report | `outputs/evidence/g6_champion_challenger_report.json` | — |
| Calibration report | `outputs/evidence/g6_calibration_report.json` | — |
| Calibration + ROC curves | `outputs/plots/g6_calibration_curve.png` | — |
| Model comparison bars | `outputs/plots/g6_model_comparison.png` | — |

---

## 11. Claim Boundary

### Safe G6 interview answers

**"What's your ROC-AUC on real data?"**
> "On the Taiwan credit card default dataset — 30,000 rows, 22% default rate, UCI public data — the XGBoost champion with Platt calibration achieves ROC-AUC 0.7852 and PR-AUC 0.5709. Platt calibration reduces ECE from 0.2082 to 0.0112, a 94.6% reduction. The LightGBM challenger does not improve PR-AUC over the calibrated champion, so the champion is retained."

**"How does your real-data performance compare to your synthetic results?"**
> "They can't be directly compared — different datasets with different feature structures and base rates. The synthetic lane achieves ROC-AUC 0.6237, which is near the Bayes ceiling for that synthetic DGP with 6 signal features. The real data lane achieves 0.7852 on Taiwan credit card data with 23 real features and 6-month payment history. The synthetic lane's job is to test protocol correctness; the real-data lane's job is to produce business-credible model evidence."

**"Why Taiwan Default and not Home Credit?"**
> "Home Credit is the ideal target — it matches the synthetic DGP's feature structure and has 307,511 rows. It requires Kaggle authentication, which I couldn't automate. Taiwan Default is a clean, auth-free UCI dataset with real credit card default labels and real demographic variables — sex, age, education, marriage. It demonstrates the pipeline works on real data with a clear provenance. I've documented the transition path to Home Credit explicitly."

### Forbidden G6 claims

- "PulseGuard achieves 0.7852 AUC on Home Credit" — this is Taiwan data
- "Real-world credit risk model" — this is research/portfolio, not production
- "Taiwan results prove the system is production-ready" — no
- "Better than competitor models" — no benchmark comparison was run
- "Calibrated ECE of 0.011 is the final production number" — held-out test on 6,000 rows only

---

## 12. Synthetic Harness Boundary (G6)

The synthetic `synthetic_home_credit_like` dataset is retained in PulseGuard for:
- G3 leakage audit (injected temporal FAIL test)
- G4 drift injection (Day 7 WARN, Day 14 ALERT)
- G5 proxy fairness audit (CODE_GENDER synthetic proxy)

It is NOT used as evidence in G6 champion/challenger. These lanes are separate. Do not mix G4 metrics with G6 metrics in any summary table or interview answer.

---

## 13. G7 Readiness Checklist

For G7 (Decision Policy Engine / Credit Underwriting Simulation):

- [x] Champion model trained and calibrated on real data
- [x] Decision threshold documented (0.35 for G6 evaluation purposes)
- [x] Data profile artifact exists
- [ ] FOIR engine needs to be adapted for credit card context (or documented as N/A — Taiwan is not installment loan)
- [ ] Hard rule gate: credit card context differs from consumer loan (income, FOIR less applicable; credit limit, payment history more applicable)
- [ ] Policy versioning: define credit card decision policy v1.0 before G7
- [ ] Note: Taiwan Default does not have income or EMI fields → FOIR cannot be computed as designed in G2; G7 must document this explicitly or use a proxy

**G7 scope note:** The G2 decision workflow was designed for consumer loan underwriting (FOIR, income, proposed EMI). Taiwan Default is credit card data — no proposed EMI, no FOIR in the standard sense. G7 must either adapt the decision policy for credit card context or document it as "FOIR module not applicable to Taiwan Default; decision policy uses PD threshold + credit limit + payment history instead."
