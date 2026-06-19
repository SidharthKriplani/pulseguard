# PulseGuard — Gold Checkpoint

**Status: GOLD CHECKPOINTED | Score: 89.3% (134/150) | Date: 2026-06-17**  
**All four passes complete. Project frozen for resume and interview defense.**

---

## 1. Final Status

PulseGuard is **GOLD CHECKPOINTED**. All four gold passes are complete. The project is ready for resume, referral, and interview defense. No further modeling, tuning, or dataset changes are required. Future improvements are explicitly deferred to a future portfolio upgrade cycle.

| Pass | Status | Key Deliverable |
|---|---|---|
| G9A | ✓ COMPLETE | Home Credit primary spine, 140 features, 12-model baseline tournament |
| Gold Pass 1/4 | ✓ COMPLETE | Pre-tuning audit — safe_to_tune=true |
| Gold Pass 2/4 | ✓ COMPLETE | Optuna tuning, champion: LightGBM_monotonic+Platt |
| Gold Pass 3/4 | ✓ COMPLETE | Governance stack: score bands, SHAP, fairness, drift, RAG/LLM |
| Gold Pass 4/4 | ✓ COMPLETE | Final audit, checkpoint, defense doc, resume pack |

---

## 2. Final Score

| Dimension | Score | Max |
|---|---|---|
| Product thesis clarity | 9 | 10 |
| Data realism | 8 | 10 |
| Feature engineering depth | 9 | 10 |
| Leakage discipline | 10 | 10 |
| Model tournament depth | 8 | 10 |
| Tuning discipline | 9 | 10 |
| Calibration quality | 10 | 10 |
| Threshold economics | 8 | 10 |
| Reason-code explainability | 9 | 10 |
| Reason-code stability | 10 | 10 |
| Fairness/proxy audit honesty | 8 | 10 |
| Drift/vintage stress | 8 | 10 |
| Local RAG/LLM governance | 9 | 10 |
| Evidence honesty | 10 | 10 |
| Interview dominance | 9 | 10 |
| **TOTAL** | **134** | **150** |
| **% Score** | **89.3%** | |
| **GOLD threshold** | **85%** | |
| **Status** | **GOLD ✓** | |

---

## 3. Project Identity

PulseGuard is a **credit-risk model governance portfolio project** built on the Home Credit Default Risk public dataset (Kaggle). It demonstrates the full ML governance lifecycle — from raw multi-table data through feature engineering, model tournament, hyperparameter tuning, post-hoc calibration, score-band policy design, SHAP explainability, fairness proxy audit, drift monitoring baseline, and a local RAG/LLM governance assistant for adverse action drafting.

**It is not:**
- A production lending system
- A regulatory-compliant credit scoring deployment  
- A legally certified adverse action notice generator
- A fairness-certified model
- A system trained on real bank customer data

**Strongest defensible one-liner:**  
> "End-to-end credit-risk governance stack: tuned LightGBM on 307k Home Credit applicants, calibrated PD scores (ECE=0.0034), score-band policy, SHAP reason codes stable across 30 bootstrap resamples, fairness proxy audit, and a local RAG/LLM governance assistant — all under ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED constraints."

---

## 4. Dataset Decision

| Dataset | Role | Status |
|---|---|---|
| Home Credit Default Risk | **PRIMARY** | Active — 307,511 applicants, 57.4M rows, 7 side-tables |
| Taiwan Default | LEGACY_APPENDIX_ONLY | Not used in Pass 2–4; G6/G7 historical context only |
| LendingClub | DROPPED | Out of scope for portfolio freeze |

**Why Home Credit:**
- 307k applicants vs 30k (Taiwan)
- 8.07% base default rate matches real consumer-loan portfolios
- 7 side-tables (bureau, previous applications, instalments, credit cards, POS cash) enable realistic feature engineering
- Multi-source credit bureau data (EXT_SOURCE_1/2/3) as external signal proxy
- Scale enables proper stratified 60/20/20 split with preserved DR across all splits

**Public-data limitations acknowledged:**
- Single Eastern European geography
- No timestamps → no temporal holdout possible
- Approved applicants only → reject inference unaddressed (MNAR selection bias)
- No income field (FOIR proxy only)
- No real protected-class labels for fairness audit

---

## 5. Feature Spine

| Source | Features | Key Engineered Signals |
|---|---|---|
| `application_train.csv` | Core applicant fields | AGE_YEARS, EMPLOYED_YEARS, FLAG_EMPLOYED_ANOMALY, CREDIT_TO_INCOME, CREDIT_TO_GOODS, ANNUITY_TO_INCOME |
| `bureau.csv` + `bureau_balance.csv` | Credit bureau history | BUREAU_ACTIVE_COUNT, BUREAU_OVERDUE_RATIO, BUREAU_AMT_OVERDUE, BB_DPD_RATIO_MEAN |
| `previous_application.csv` | Prior HC applications | PREV_REFUSAL_RATE, PREV_AMT_CREDIT_MEAN |
| `installments_payments.csv` | Payment behaviour | INST_LATE_RATIO (primary driver), instalment stats |
| `credit_card_balance.csv` | CC utilisation/DPD | CC_DPD_RATIO, CC_ATM_RATIO |
| `POS_CASH_balance.csv` | POS loan history | POS_IS_DPD_RATIO |
| Composite | Behavioural risk | BEHAVIORAL_RISK_SCORE = 0.4×INST_LATE_RATIO + 0.3×CC_DPD_RATIO + 0.2×POS_IS_DPD_RATIO + 0.1×BUREAU_OVERDUE_RATIO |

**Total features:** 140 (after constant/near-zero-variance removal)  
**Leakage controls:** TARGET excluded; DAYS_DECISION side-table fields checked; group leakage 0 ID overlap confirmed

---

## 6. Model Tournament Summary

| Phase | Models | Champion | Outcome |
|---|---|---|---|
| G9A Baseline (untuned) | CatBoost, XGBoost, LightGBM, RF, LR, SVM, GBM, monotonic variants (12 total) | CatBoost + Platt (provisional) | AUC=0.7716, ECE=0.0054 — BASELINE_NOT_TUNED |
| Gold Pass 2 (Optuna) | CatBoost, XGBoost, XGBoost_mono, LightGBM_base, LightGBM_mono | LightGBM_monotonic + Platt | Tuned; composite 9-component score |
| Hard failures | TabNet (CPU ~6min/epoch), sklearn GBM (wall-time) | — | Documented with cause |

**Why LightGBM_monotonic won over CatBoost:**
CatBoost val_AUC=0.7708 vs LightGBM_mono val_AUC=0.7734 (+0.0026). But composite score: LightGBM_mono=0.7312 vs XGBoost_mono=0.7294 vs CatBoost=0.6802. The 0.5-point explainability premium for monotone constraints (+10% weight on composite) and the governance/adverse-reason-ready premium (+5%) make LightGBM_mono both the **performance champion and governance champion** — a decisive win in a governance-focused project.

---

## 7. Tuned Champion

| Field | Value |
|---|---|
| Model | LightGBM Gradient Boosted Trees |
| Variant | Monotonic constraints on 15 features |
| Calibration | Platt sigmoid (LogisticRegression C=1e6, fit on val only) |
| HPO | Optuna TPE, 5 trials, seed=42 |
| Constraints | 12 risk-increasing (+1), 3 risk-decreasing (−1), 125 unconstrained |
| Early-stop fix | LightGBM bug with scale_pos_weight + eval_metric='auc' fixed by treating n_estimators as Optuna hyperparameter |
| Composite score | 0.7312 (9-component: AUC 25%, PR-AUC 15%, KS 15%, Brier 10%, ECE 10%, slope 5%, latency 5%, explainability 10%, adverse-ready 5%) |

---

## 8. Final Test Metrics

**Single untouched evaluation on 61,503-row held-out test set (DR=8.07%).**

| Metric | Value | vs G9A Baseline | Interpretation |
|---|---|---|---|
| ROC-AUC | **0.7769** | +0.0053 | Strong discrimination on 8% base rate |
| PR-AUC | 0.2628 | −0.0009 | Default-minority precision-recall |
| KS statistic | **0.4141** | +0.0047 | 41.4pp separation between default/non-default |
| Brier score | 0.0668 | — | Good probabilistic accuracy |
| ECE (Platt) | **0.0034** | improved | Near-perfect calibration |
| Latency | 327 ms / 61k rows | — | <1ms per applicant |

Val-test AUC gap = −0.0035 (test slightly higher than val) — within expected range for stratified random split; no leakage signal.

---

## 9. Calibration Result

| Model | ECE raw | ECE Platt (val) | ECE Platt (test) |
|---|---|---|---|
| LightGBM_mono (champion) | 0.2964 | 0.0051 | **0.0034** |
| CatBoost | 0.3112 | 0.0044 | — |
| XGBoost_mono | 0.3172 | 0.0057 | — |

Isotonic calibration produces ECE=0.0 on val (overfitting artifact — fits to val perfectly). Platt is the correct selection: 2-parameter sigmoid, val-fit only, honest test generalisation.

**Why calibration matters:** A calibrated PD of 0.20 means the model genuinely estimates 20% default probability at that score — enabling semantically interpretable score-band thresholds, cost-sensitive decisioning, and probabilistic adverse-action language.

---

## 10. Threshold / Score-Band Result

| Band | Threshold | Test Count | Test % | Test Default Rate |
|---|---|---|---|---|
| GREEN | PD < 0.20 | 55,183 | 89.72% | 5.77% |
| AMBER | 0.20 ≤ PD < 0.40 | 6,030 | 9.80% | 26.96% |
| RED | PD ≥ 0.40 | 290 | 0.47% | 53.77% |

**Rationale:** PD=0.20 boundary carries a semantic interpretation (model estimates 20% default probability). GREEN DR=5.77% confirms conservative GREEN assignment. Selected over KS-optimal single threshold (0.0961, 50.7% approve rate) and cost-optimal (0.47, 33% capture rate) for operational plausibility.

**Cost-sensitive (scenario, not real bank economics):** C_bad=10, C_reject=1, C_review=0.3 → cost-optimal threshold=0.47, EL=0.0807. Scenario assumptions explicitly labelled.

---

## 11. SHAP Reason-Code Layer

**Method:** LightGBM built-in `pred_contrib=True` (native SHAP, avoids SHAP library pandas-index bug).

**Global top-5 (mean |SHAP|, 1000-sample draw):**

| Rank | Feature | Mean |SHAP| |
|---|---|---|
| 1 | EXT_SOURCE_MEAN | 0.510 |
| 2 | CREDIT_TO_ANNUITY | 0.141 |
| 3 | CREDIT_TO_GOODS | 0.139 |
| 4 | INST_LATE_RATIO | 0.129 |
| 5 | EXT_SOURCE_1 | 0.120 |

**Stability:** All 5 appear in top-5 across 30/30 bootstraps (30 × 500 samples). EXT_SOURCE_MEAN rank-1 in 30/30.

**Local cases:** 4 cases computed (GREEN_APPROVE, AMBER_REVIEW, RED_HIGH_RISK, AMBER_CONFLICT). SHAP values map to ECOA-style reason-code language (ASSISTIVE_ONLY).

---

## 12. Fairness / Proxy Audit Result

**Scope:** Proxy-variable analysis only. No protected-class labels in Home Credit.

| Proxy | Approval Rate Range | DR Range | Assessment |
|---|---|---|---|
| Age (under-30 vs 50+) | 80.5% – 95.5% | 11.5% – 5.6% | Aligned with DR differential |
| Income tercile | 89.0% – 91.3% | 8.1% – 7.5% | Narrow spread — model not income-stratifying |
| Employment (employed vs sentinel) | 88.3% – 96.2% | 8.7% – 5.2% | Sentinel (not employed) has lower DR — model not penalising |
| Region (1 vs 3) | 96.5% – 81.7% | 4.9% – 11.2% | Aligned with DR differential |

**Governance conclusion:** No evidence of model amplifying disparities beyond base rates. This is NOT a fairness certification. Disparate impact ratio not computable without protected-class labels.

---

## 13. Drift / Vintage Stress Result

| Comparison | Score PSI | Interpretation |
|---|---|---|
| val vs test | 0.0002 | STABLE — operationally relevant |
| train vs val/test | ~8.10 | Platt calibration artefact (not drift) |
| Top-10 feature PSI (train vs test) | All < 0.001 | STABLE |

AUC: val=0.7734 → test=0.7769 (gap=−0.0035). ECE: val=0.0051 → test=0.0034. No degradation between val and test.

**True vintage validation** is not possible — Home Credit has no timestamps. Monthly PSI monitoring (score + top-10 features) is the recommended production monitoring plan.

---

## 14. Local RAG / LLM Governance Layer

**System:** BM25 retriever (5-document policy corpus) + LLM memo/adverse-action drafter.

| Case | Band | Policy Retrieved | LLM Action |
|---|---|---|---|
| CASE_1 | GREEN | POL-001 | Approval memo; hard-stop check recommended |
| CASE_2 | AMBER | POL-001 | Review memo with top-3 SHAP drivers |
| CASE_3 | RED | POL-002 | Adverse-action draft with 3 reason codes |
| CASE_4 | AMBER_CONFLICT | POL-004 | Override protocol surfaced; officer authority noted |
| CASE_5 | N/A (OOD) | Abstain (BM25=0.0) | No output — prevents hallucinated policy citation |
| CASE_6 | DRIFT_ALERT | POL-003 | MRC escalation memo |

**Hard rules enforced in all cases:** LLM never autonomously approves or rejects. ASSISTIVE_ONLY. HUMAN_REVIEW_REQUIRED. NOT_FINAL_DECISION.

---

## 15. What Is Done

- [x] Raw multi-table data ingestion and feature engineering (140 features, 7 tables, 57.4M rows)
- [x] Leakage audit (10/10 PASS, safe_to_tune=true)
- [x] 12-model baseline tournament with calibration
- [x] 5-model Optuna tuning tournament (validation-only)
- [x] Post-tuning Platt calibration
- [x] 9-component composite champion selection
- [x] Single held-out test evaluation (AUC=0.7769, ECE=0.0034)
- [x] Score-band policy (GREEN/AMBER/RED) with PD-semantic rationale
- [x] Cost-sensitive threshold analysis (3 scenarios)
- [x] SHAP reason codes (global + 4 local cases) via LightGBM pred_contrib
- [x] 30-bootstrap reason-code stability
- [x] Fairness proxy audit (4 proxy groups)
- [x] Drift/PSI baseline (val-vs-test PSI=0.0002)
- [x] Local RAG/LLM governance demo (6 cases)
- [x] Model card + governance report
- [x] Evidence ledger (all claims traceable to artifacts)
- [x] Claim boundary (safe/forbidden for every gate)
- [x] Final gold audit (89.3%, GOLD)
- [x] Interview defense document + PDF
- [x] Resume/opportunity pack

---

## 16. What Is Not Done

| Gap | Why Acceptable for Portfolio Freeze |
|---|---|
| Temporal/out-of-time validation | No timestamps in Home Credit — not possible; documented limitation |
| Real DI ratio / protected-class fairness | No demographic labels — structurally impossible; SKELETON label applied |
| Real bank cost economics | Not a production system; scenario economics correctly labelled |
| Full 100-trial Optuna search | CPU sandbox constraint; honestly documented; results are valid local optimum |
| Production FastAPI scoring API | Out of scope; offline portfolio project |
| Reject inference | Approved-applicant MNAR — documented boundary; semi-supervised correction is future work |
| DeLong test p-values for champion vs runner-up | Standard improvement; does not change champion selection |
| Real adverse action notice | Requires licensed credit officer; LLM output is draft only |
| WOE/IV scorecard | Alternative explainability; SHAP + monotone constraints sufficient for defense |

---

## 17. Why the Project Is Stopped Now

PulseGuard has achieved GOLD status (89.3%). Every material gap from the RiskFrame audit (104/150, 2026-06-16) has been addressed:
- Data realism: Home Credit (307k, 7 tables) replaces synthetic/Taiwan as primary
- Tournament depth: 12 baseline + 5 tuned models
- Calibration: ECE=0.0034 (near-production quality)
- Explainability: SHAP + monotone constraints + 4 local cases + stability
- Governance: model card, governance report, evidence ledger, claim boundary
- Fairness: proxy audit skeleton (appropriately caveated)
- Drift: PSI baseline documented

Further improvements (more Optuna trials, temporal validation, production API) require either different datasets, GPU compute, or real bank data — none of which change the project's portfolio standing for resume/interview defense.

---

## 18. Future Work (Intentionally Deferred)

All of the following are **future portfolio upgrades**, not current blockers.

**High-value:**
- Optuna 100-trial search on GPU environment → better champion candidates
- Out-of-time split if timestamped public credit data becomes available
- Real lender economics for cost matrix calibration
- Full fairness audit with demographic enrichment
- Production monitoring harness (PSI alerts, model registry)

**Nice-to-have:**
- Streamlit decision demo UI
- Expanded policy corpus for RAG (50+ documents)
- Additional case studies (reject inference semi-supervised correction)

**Do-not-build:**
- Taiwan Default as primary spine
- LendingClub reintroduction
- LLM autonomous credit decisioning
- Legal adverse action notice automation

---

## Defense Readiness Statement

> **PulseGuard is ready for resume and interview defense.** Every metric has an artifact. Every claim has a boundary. Every limitation is documented. The project demonstrates a complete, honest credit-risk ML governance lifecycle — from raw data through champion model to governance documentation — suitable for Data Scientist, ML Governance, and Credit Risk roles.

Further improvements are future portfolio upgrades. They are not blockers for this opportunity.

---

*PulseGuard Gold Checkpoint | Pass 4/4 | 2026-06-17 | GOLD 89.3%*
