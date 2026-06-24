# PulseGuard — Opus 4.8 Audit Handoff
**For:** Claude Opus 4.8, high-effort multi-pass audit  
**Written by:** Claude Sonnet 4.6 (project executor)  
**Date:** 2026-06-23  
**Instruction:** Run N passes until zero new issues remain. Each pass should audit a different layer. Do not stop until you find nothing new.

---

## 0. WHAT YOU ARE AUDITING

PulseGuard is a **credit-risk model governance portfolio project** by Sidharth Kriplani. It is NOT a production system. It lives at:

```
/Users/ASUS/Documents/Professional/GitHub/beastmax (5)/pulseguard/
```

GitHub: `SidharthKriplani/pulseguard` (exact repo name TBC from remote)

The project has been through 5 Gold Passes (GP1–GP5) plus calibration forensics. It scored **GOLD at 89.3%** (134/150) on a 15-dimension governance audit. The audit harness is at `outputs/evidence/pulseguard_final_gold_audit.json`.

---

## 1. HARD CONSTRAINTS — NEVER VIOLATE THESE

These are absolute. Do not touch, re-open, or suggest changing:

1. **Do NOT retune the champion model.** Champion is LightGBM_monotonic (lgb_mono_champion.txt, 279 trees, 140 features). Frozen at Gold Pass 2.
2. **Do NOT change the champion.** Even if you find a metric slightly better elsewhere, the champion is locked.
3. **Do NOT re-open dataset strategy.** Home Credit Default Risk is the primary spine. Taiwan Default is legacy appendix only. LendingClub is dropped.
4. **Do NOT introduce Taiwan as primary** or LendingClub as anything.
5. **Do NOT claim the LLM makes credit decisions.** ASSISTIVE_ONLY is a hard rule. LLM drafts memos only.
6. **Do NOT claim production lending, compliance certification, legal adverse action, fairness certification, or real bank validation.**
7. **Always precede terminal commands with `cd "/Users/ASUS/Documents/Professional/GitHub/beastmax (5)/pulseguard"`**

---

## 2. PROJECT IDENTITY

**What it is:** End-to-end credit-risk ML governance stack on Home Credit Default Risk.  
**What it demonstrates:** Full governed ML lifecycle — data ingestion, feature engineering across 7 relational tables, leakage-audited splits, 12-model tournament, Optuna HPO, isotonic calibration, 9-component composite champion selection, score-band policy, SHAP reason codes, fairness proxy audit, PSI drift monitoring, local BM25+LLM governance assistant.

**What it is NOT:**
- Production lending system
- Regulatory-compliant credit scoring deployment
- Legally certified adverse action notice generator
- Fairness-certified model
- Real bank data

**One-liner (safe to use in any context):**
> "End-to-end credit-risk governance stack: tuned LightGBM on 307k Home Credit applicants, calibrated PD scores (ECE=0.0034), score-band policy, SHAP reason codes stable across 30 bootstrap resamples, fairness proxy audit, and a local RAG/LLM governance assistant — all under ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED constraints."

---

## 3. CHAMPION MODEL — LOCKED SPECS

| Field | Value |
|---|---|
| Model | LightGBM with 15 monotone constraints |
| Model file | `outputs/models/lgb_mono_champion.txt` |
| Feature count | 140 (verified: `bst.num_feature() == 140`) |
| Tree count | 279 (verified: `bst.num_trees() == 279`) |
| Calibration | Isotonic regression (NOT Platt — see forensics below) |
| Calibration files | `outputs/models/iso_x.npy` (shape 134,) · `outputs/models/iso_y.npy` (shape 134,) |
| Calibration serving | `np.interp(raw_prob, iso_x, iso_y)` — zero sklearn dependency |
| Training data | 184,506 applicants (60%, seed=42, stratified) |
| Val data | 61,502 applicants (20%) |
| Test data | 61,503 applicants (20%, evaluated exactly ONCE) |
| Test AUC | **0.7769** (0.776858 exact — from gold_pass2_final_untouched_test_report.json) |
| Test PR-AUC | **0.2628** (0.262773 exact) |
| Test KS | **0.4141** (0.414142 exact) |
| Test Brier | **0.0668** (0.066833 exact) |
| Test ECE | **0.0034** (0.003396 exact) |
| Val AUC | 0.7734 (0.773449) |
| Val ECE | 0.0051 (0.005086) |
| Composite score | **0.7312** (0.731249 exact) |
| Composite rank | #1 of 5 tuned models |
| Governance audit | GOLD — 89.3% (134/150) |

**Calibration forensics critical note:** The `gold_pass2_final_untouched_test_report.json` artifact says "Platt" — that was a documentation error discovered during Cloud Run deployment. The actual pkl (`champion_calibrated.pkl`) contains a `CalibratedClassifierCV` object (sklearn 1.6.1), but the **operationally correct calibration** is the isotonic calibration extracted to numpy arrays (`iso_x.npy`, `iso_y.npy`). The numpy interp is what the defense documentation refers to as the serving calibrator. ECE=0.0034 is the correct metric achieved by isotonic calibration on the test set.

**Monotone constraints (15 features):**
- +1 (risk-increasing): BUREAU_OVERDUE_RATIO, BUREAU_AMT_OVERDUE, BB_DPD_RATIO_MEAN, PREV_REFUSAL_RATE, INST_LATE_RATIO, CC_DPD_RATIO, POS_IS_DPD_RATIO, BUREAU_AMT_CREDIT_DEBT, REGION_RATING_CLIENT, REGION_RATING_CLIENT_W_CITY, REG_REGION_NOT_LIVE_REGION, LIVE_CITY_NOT_WORK_CITY (12 total)
- -1 (risk-decreasing): AGE_YEARS, EMPLOYED_YEARS, EXT_SOURCE_MEAN (3 total)

---

## 4. DATASET

| Field | Value |
|---|---|
| Name | Home Credit Default Risk |
| Source | Kaggle public competition |
| Applicants | 307,511 |
| Default rate | 8.07% |
| scale_pos_weight | 11.39 |
| Total raw rows | 57.4M across 7 tables |
| Geography | Single Eastern European portfolio |
| Timestamps | None — out-of-time split NOT possible |
| Split | Stratified random 60/20/20, seed=42 |

**7 source tables:**
1. `application_train.csv` — 307,511 rows — base applicant table
2. `bureau.csv` — 1.7M rows — credit bureau history
3. `bureau_balance.csv` — 27.3M rows — monthly bureau snapshots
4. `previous_application.csv` — 1.67M rows — prior HC applications
5. `installments_payments.csv` — 13.6M rows — payment history
6. `credit_card_balance.csv` — 3.84M rows — revolving card snapshots
7. `POS_CASH_balance.csv` — 10.0M rows — POS/cash advance history

**Key limitations (must not be hidden):**
- No temporal validation possible (no timestamps)
- Approved-applicant selection bias — MNAR reject inference unaddressed
- Single geography — no cross-market generalization
- No protected-class labels — fairness audit is proxy-only
- No income field — FOIR is proxy (credit/goods)

---

## 5. FULL FILE STRUCTURE

```
pulseguard/
├── OPUS_AUDIT_HANDOFF.md          ← this file
├── 00_CONTROL_TOWER.md            ← master project control doc
├── 01_BEASTMAX_PRD.md             ← PRD
├── 02_PROJECT_MIX_MAP.md          ← project portfolio map
├── 03_BUILD_GATES.md              ← gate definitions GP1–GP5
├── 04_EVIDENCE_LEDGER.md          ← claim → artifact mapping
├── 05_CLAUDE_KICKOFF_PROMPT.md    ← original kickoff
├── 06_CLAIM_BOUNDARY.md           ← safe/forbidden claim list
├── app.py                         ← FastAPI serving app (demo model)
├── Dockerfile                     ← Cloud Run container
├── requirements.txt               ← Python deps
├── src/
│   ├── feature_pipeline.py        ← ColumnTransformer (has 'from __future__ import annotations' fix)
│   └── pulseguard/
│       ├── policy_rag.py          ← BM25 retriever
│       └── llm_governance_assistant.py ← LLM governance layer
├── scripts/
│   ├── g9a_feature_engineering.py ← 140-feature factory (7 tables)
│   ├── g9a_model_tournament.py    ← 12-model baseline tournament
│   ├── leakage_audit.py           ← 10-check pre-tuning leakage audit
│   ├── group_leakage_check.py     ← SK_ID_CURR overlap check
│   ├── train_champion.py          ← Optuna HPO + calibration + champion selection
│   ├── gp5_preprocess_sequences.py ← GP5: instalment sequences to numpy
│   ├── gp5_augment_and_retrain.py ← GP5: LSTM embeddings → LightGBM retrain
│   ├── drift_monitor.py           ← PSI drift monitoring
│   ├── fairness_audit.py          ← proxy fairness audit
│   ├── build_defense_pdf_v5.py    ← PDF generator (26 sections, reportlab)
│   └── [various g6/g7/g8 scripts — legacy gates]
├── notebooks/
│   └── GP5_LSTM_encoder.ipynb     ← Colab T4 GPU LSTM training notebook
├── outputs/
│   ├── models/
│   │   ├── lgb_mono_champion.txt  ← CHAMPION MODEL (frozen)
│   │   ├── iso_x.npy              ← isotonic calibration X thresholds (shape 134)
│   │   ├── iso_y.npy              ← isotonic calibration Y values (shape 134)
│   │   ├── champion_calibrated.pkl ← sklearn pkl (version-locked, not served)
│   │   ├── lgb_gp5_172_challenger.txt ← GP5 challenger (172 features, NOT champion)
│   │   ├── iso_x_gp5_172_challenger.npy ← GP5 calibration arrays
│   │   ├── iso_y_gp5_172_challenger.npy
│   │   ├── lstm_encoder.pt        ← PyTorch LSTM encoder (Colab-trained)
│   │   ├── gp5_embeddings_train.npy ← 32-dim LSTM embeddings (train split)
│   │   ├── gp5_embeddings_val.npy
│   │   ├── gp5_embeddings_test.npy
│   │   ├── gp5_median_embedding.npy ← fallback for zero-history applicants
│   │   ├── champion_xgb.json      ← G4 demo model (XGBoost, for Cloud Run)
│   │   ├── preprocessor.pkl       ← G4 demo preprocessor (sklearn 1.9-compat)
│   │   └── feature_medians.json / feature_medians_172.json ← imputation values
│   ├── data/
│   │   ├── g9a_splits.pkl         ← train/val/test split indices
│   │   ├── bb_agg.parquet         ← bureau_balance aggregates
│   │   ├── bureau_agg.parquet     ← bureau aggregates
│   │   ├── cc_agg.parquet         ← credit card aggregates
│   │   ├── inst_agg.parquet       ← instalment aggregates
│   │   ├── pos_agg.parquet        ← POS cash aggregates
│   │   ├── prev_agg.parquet       ← previous application aggregates
│   │   ├── inst_sequences.npy     ← GP5 padded sequences (N×50×3)
│   │   ├── inst_sk_ids.npy        ← GP5 applicant IDs for sequences
│   │   └── gp5_splits.npz         ← GP5 train/val/test masks
│   └── evidence/                  ← ALL EVIDENCE ARTIFACTS (see Section 7)
├── docs/
│   ├── PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md ← V4 defense doc (30 sections, 1497 lines)
│   ├── PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.pdf ← old PDF (pre-v5)
│   ├── defense/
│   │   └── PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf ← NEW v5 PDF (38 pages)
│   ├── PULSEGUARD_MODEL_CARD.md   ← full model card
│   ├── PULSEGUARD_GOLD_CHECKPOINT.md ← freeze point doc
│   ├── PULSEGUARD_GOLD_PASS3_GOVERNANCE_REPORT.md
│   ├── PULSEGUARD_FAILURE_ARCHAEOLOGY.md ← 6 documented failures
│   ├── PULSEGUARD_FUTURE_BUILDS_BACKLOG.md
│   └── [G0–G9A planning/gate docs]
└── data/
    ├── home-credit-default-risk/   ← all 7 source CSVs
    ├── policy_docs/sample_credit_policy.md ← BM25 policy corpus
    └── synthetic_home_credit_like.csv ← G4 demo training data (50k rows)
```

---

## 6. GOLD PASS HISTORY

### GP1 — Leakage Audit & Baseline Tournament
- **Status:** COMPLETE
- **Key outcome:** 10/10 leakage audit PASS. safe_to_tune=true. 12-model tournament complete. CatBoost provisional champion (0.7716). LightGBM underperforming due to early-stopping bug (AUC=0.7203 — looked plausible, was wrong).
- **Artifacts:** `gold_pass1_leakage_audit.json`, `gold_pass1_data_spine_validation.json`, `gold_pass1_temporal_vintage_feasibility.json`, `gold_pass1_tournament_quality_audit.json`, `gold_pass1_rag_llm_governance_audit.json`, `gold_pass1_artifact_audit.json`

### GP2 — HPO + Calibration + Champion Selection
- **Status:** COMPLETE (FROZEN)
- **Key outcome:** Optuna TPE on 5 models. LightGBM early-stopping bug fixed (n_estimators as search param). LightGBM_monotonic wins composite (0.7312). Test AUC=0.7769, ECE=0.0034.
- **Trial counts:** LightGBM_base: 6 · LightGBM_mono: 5 · CatBoost: 8 · XGBoost: 4 · XGBoost_mono: 4 (CPU constraint; plan was 100)
- **Artifacts:** `gold_pass2_tuning_trace.json`, `gold_pass2_validation_model_comparison.json`, `gold_pass2_calibration_report.json`, `gold_pass2_champion_selection_report.json`, `gold_pass2_final_untouched_test_report.json`

### GP3 — Governance Layer
- **Status:** COMPLETE
- **Key outcome:** Score-band policy, SHAP reason codes (30-bootstrap stable), fairness proxy audit, PSI drift baseline, RAG/LLM 6-case demo, final GOLD audit.
- **Score bands:** GREEN <0.20 (89.72%, DR=5.77%) · AMBER 0.20–0.40 (9.80%, DR=26.96%) · RED ≥0.40 (0.47%, DR=53.77%)
- **SHAP top-5 (all 30/30 stable):** EXT_SOURCE_MEAN (0.510, rank-1 in 30/30) · CREDIT_TO_ANNUITY (0.141) · CREDIT_TO_GOODS (0.139) · INST_LATE_RATIO (0.129) · EXT_SOURCE_1 (0.120)
- **PSI:** val-vs-test = 0.0002 (STABLE). train-vs-val ~8.1 (calibration artifact, not drift)
- **Artifacts:** `gold_pass3_threshold_scoreband_report.json`, `gold_pass3_cost_sensitive_decisioning.json`, `gold_pass3_shap_reason_code_report.json`, `gold_pass3_reason_code_stability.json`, `gold_pass3_fairness_proxy_audit.json`, `gold_pass3_drift_vintage_stress.json`, `gold_pass3_rag_llm_demo_report.json`, `pulseguard_final_gold_audit.json`

### GP4 — Defense Documentation
- **Status:** COMPLETE
- **Key outcome:** 30-section interview defense doc (1497 lines). Sections added: adversarial Q&A, ML concept drill, implementation probes, behavioral STAR, role expansion (fraud/MLOps/risk), failures archaeology, deployment caveat (Q30A).
- **Files:** `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md` (V4)

### GP5 — LSTM Sequence Encoder Experiment
- **Status:** COMPLETE (negative result, documented)
- **Key outcome:** 1-layer LSTM on 13.6M instalment rows → 32-dim embeddings → 172-feature LightGBM challenger → AUC=0.7264 vs GP2 baseline 0.7769 (delta=−0.0505). GP2 champion retained.
- **Root cause of failure:** 35% applicants have zero instalment history → zero-padded sequences encode noise. Scalar aggregates (INST_LATE_RATIO) already in top-7 SHAP — LSTM learned redundant representation.
- **Files:** `notebooks/GP5_LSTM_encoder.ipynb` (Colab T4 GPU), `scripts/gp5_preprocess_sequences.py`, `scripts/gp5_augment_and_retrain.py`, `outputs/models/lgb_gp5_172_challenger.txt`, `outputs/models/lstm_encoder.pt`, `outputs/models/gp5_embeddings_*.npy`

### Calibration Forensics (post-GP5)
- **Status:** COMPLETE
- **What happened:** GP2 report said "Platt selected." Cloud Run deployment revealed serving probabilities diverged from training by up to 0.53. Forensic inspection of `champion_calibrated.pkl` confirmed `cal['selected'] = 'isotonic'`. The training report was wrong.
- **Fix:** Extracted isotonic calibrator as numpy arrays (`iso_x.npy`, `iso_y.npy`). `np.interp(raw_prob, iso_x, iso_y)` replicates `IsotonicRegression.predict()` exactly (max diff = 0.0). Zero sklearn dependency at serve time.
- **Defense doc update:** Section 8 corrected from Platt to isotonic. Section 30 added (calibration forensics). Q12 updated.

### Defense PDF v5
- **Status:** COMPLETE
- **File:** `docs/defense/PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf` (38 pages)
- **Generator:** `scripts/build_defense_pdf_v5.py` (reportlab Platypus, 26 sections)
- **Content:** Cover page, all 30 sections, 20 standard Q&As, 8 adversarial drills, 5 ML concept probes, 5 implementation probes, 4 behavioral STAR, full 140-feature catalogue, inline model card, API spec, role expansion (fraud/MLOps/risk), deployment caveat, failures table, GP5 LSTM, calibration forensics, implemented-vs-future roadmap, resume bullets

---

## 7. EVIDENCE ARTIFACTS — COMPLETE LEDGER

All in `outputs/evidence/`. Each must exist and contain valid JSON.

| Artifact | Key Numbers | Claim |
|---|---|---|
| `gold_pass1_leakage_audit.json` | 10/10 PASS, safe_to_tune=true | No target or post-outcome leakage |
| `gold_pass1_data_spine_validation.json` | 21/21 PASS, 0 SK_ID_CURR overlap | No entity leakage between splits |
| `gold_pass1_temporal_vintage_feasibility.json` | FEASIBILITY_LIMITED | No temporal split possible; documented |
| `gold_pass1_tournament_quality_audit.json` | CatBoost=0.7716 provisional baseline | 12-model tournament complete |
| `gold_pass1_rag_llm_governance_audit.json` | 10/10 PASS, abstain fires | BM25 abstain functional |
| `gold_pass1_artifact_audit.json` | 23/23 PASS | All GP1 artifacts present |
| `gold_pass2_tuning_trace.json` | 5 models, 4–8 trials, bug documented | Validation-only Optuna HPO |
| `gold_pass2_validation_model_comparison.json` | LGB_mono=0.7734 rank #1 | Champion by composite |
| `gold_pass2_calibration_report.json` | ECE vals documented | Calibration comparison |
| `gold_pass2_champion_selection_report.json` | Composite=0.7312, LGB_mono #1 | 9-component composite champion |
| `gold_pass2_final_untouched_test_report.json` | AUC=0.776858, ECE=0.003396 | Final test metrics |
| `gold_pass3_threshold_scoreband_report.json` | GREEN 89.72%, AMBER 9.80%, RED 0.47% | Score-band policy |
| `gold_pass3_cost_sensitive_decisioning.json` | t=0.47, EL=0.0807 (scenario) | Cost-sensitive analysis |
| `gold_pass3_shap_reason_code_report.json` | EXT_SOURCE_MEAN=0.510, 4 local cases | SHAP reason codes |
| `gold_pass3_reason_code_stability.json` | 30/30 top-5, 30/30 rank-1 | Bootstrap stability |
| `gold_pass3_fairness_proxy_audit.json` | 4 proxy groups, DR-aligned | Proxy fairness audit |
| `gold_pass3_drift_vintage_stress.json` | PSI=0.0002, all features STABLE | Drift baseline |
| `gold_pass3_rag_llm_demo_report.json` | 6 cases, abstain fires | RAG/LLM demo |
| `pulseguard_final_gold_audit.json` | 89.3%, GOLD, 134/150 | GOLD checkpoint |
| `leakage_report.json` | 10/10 PASS | Leakage audit raw |
| `group_leakage_report.json` | 0 overlap | Entity leakage |

---

## 8. DEPLOYMENT STATUS

### Live Cloud Run Endpoint
- **URL:** `https://pulseguard-api-98058433335.us-central1.run.app` (revision 00006-zrm)
- **Model served:** G4 XGBoost demo (`outputs/models/champion_xgb.json`)
- **Training data:** `data/synthetic_home_credit_like.csv` (50k synthetic rows)
- **Test AUC:** 0.6261 (on synthetic data — Bayes-optimal for the DGP)
- **Features:** 28 (NOT the 140-feature champion)
- **Champion NOT deployed:** GP2 LightGBM pkl artifacts serialized with sklearn 1.7.2 → incompatible with Python 3.9 deployment environment

### Deployment Bugs Fixed
1. `_pickle.UnpicklingError: STACK_GLOBAL requires str` → `app.py` was using `pickle.load()` for joblib artifacts → fixed to `joblib.load()`
2. `TypeError: unsupported operand type(s) for |` → `ColumnTransformer | None` is Python 3.10+ syntax → fixed with `from __future__ import annotations` in `src/feature_pipeline.py`
3. Champion pkl unloadable on Python 3.9 → solved by training G4 XGBoost demo model natively on Python 3.9

### Fix Path for Champion Deployment (FUTURE)
- Option A: ONNX export of lgb_mono_champion.txt → version-agnostic inference
- Option B: Retrain in Python 3.9/sklearn 1.6.1 environment (requires re-running GP2 — NOT currently permitted; model is frozen)

---

## 9. CLAIM BOUNDARY

### Safe to claim (verbatim, anytime)
1. "Tuned LightGBM_monotonic + Isotonic calibration: AUC=0.7769, PR-AUC=0.2628, KS=0.4141, ECE=0.0034 on 61k held-out test"
2. "Validation-only Optuna HPO; champion selected by 9-component composite score"
3. "Monotone constraints on 15 features support SR 26-2 directional interpretability"
4. "EXT_SOURCE_MEAN rank-1 SHAP driver in 30/30 bootstraps; top-5 features stable 30/30"
5. "Score-band policy: GREEN<0.20 (89.7%, DR=5.8%), AMBER 0.20–0.40 (9.8%, DR=27%), RED≥0.40 (0.5%, DR=54%)"
6. "RAG/LLM: abstains on OOD (BM25<0.25); LLM never makes credit decisions in 6 demo cases"
7. "Fairness proxy: approval-rate differentials aligned with DR differentials; no amplification"
8. "val-vs-test PSI=0.0002; all top-10 feature PSIs STABLE"
9. "PulseGuard scores GOLD at 89.3% (134/150) on 15-dimension governance audit"
10. "FastAPI endpoint at Cloud Run serves G4 XGBoost demo (AUC=0.6261, synthetic); GP2 champion NOT deployed due to sklearn version incompatibility — serving gap fully documented"

### Forbidden — never say these
1. Production lending system or live deployment
2. SR 26-2 certified or regulatory compliance certified
3. Legally compliant adverse action notice
4. Fairness certified or disparate impact compliant
5. Real bank data or real lender economics
6. Full vintage/out-of-time validation performed
7. LLM makes or influences credit decisions
8. 100 Optuna trials completed (actual: 4–8 per model)
9. CatBoost is the final champion (it is NOT)
10. AUC=0.7716 is the tuned result (that is the BASELINE untuned CatBoost)
11. Live endpoint AUC=0.7769 (it serves synthetic G4 demo at 0.6261)
12. The champion model is deployed (pkl is unloadable on Python 3.9)

---

## 10. WHAT TO AUDIT — PASS-BY-PASS GUIDE

### Pass 1 — Code Correctness Audit
**Check every script for correctness:**
- `scripts/g9a_feature_engineering.py` — are the 7 table merges correct? Is imputation train-only? Are monotone constraint feature names valid?
- `scripts/train_champion.py` — does Optuna objective use val set only? Is early stopping actually removed? Is calibrator fit on val only? Is test set evaluated exactly once?
- `scripts/leakage_audit.py` — do all 10 checks actually test what they claim?
- `src/feature_pipeline.py` — does `from __future__ import annotations` fix actually prevent the union type crash on Python 3.9?
- `app.py` — is the model loaded with `joblib.load()`? Does the response always include ASSISTIVE_ONLY tag? Does LLM response ever produce approve/reject language?
- `src/pulseguard/policy_rag.py` — does the BM25 abstain threshold actually fire when score < 0.25?
- `scripts/gp5_augment_and_retrain.py` — are LSTM embeddings correctly aligned to applicant IDs? Is zero-padding handled for 35% zero-history applicants?

### Pass 2 — Evidence Artifact Consistency Audit
**For each artifact in Section 7:**
- Does the file exist?
- Is it valid JSON?
- Do the key metrics inside match what the defense documentation claims?
- Does `gold_pass2_calibration_report.json` note that isotonic was selected (or does it still say Platt)? If it says Platt, that is the documentation error — does the defense doc acknowledge this?
- Does `gold_pass2_final_untouched_test_report.json` show AUC=0.776858, ECE=0.003396?
- Does `gold_pass2_champion_selection_report.json` show LightGBM_monotonic as champion with composite=0.731249?
- Does `pulseguard_final_gold_audit.json` show 89.3% GOLD?
- Cross-check: every metric quoted in `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md` must trace to an artifact.

### Pass 3 — Defense Document Consistency Audit
**Check `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md` (1497 lines, 30 sections):**
- Section 8 (Calibration): must say isotonic, not Platt — was this corrected after the forensics discovery?
- Q12 answer: must describe isotonic calibration as selected, not Platt
- Section 30 (Calibration Forensics): must exist and correctly describe the `cal['selected'] = 'isotonic'` forensic finding
- Section 29 (GP5 LSTM): must exist with correct AUC=0.7264, delta=−0.0505, GP2 retained
- All Q&A answers: do any claim forbidden things (production, 100 trials, Platt, CatBoost champion, etc.)?
- Q30A (endpoint AUC=0.62): does the answer correctly explain the serving gap?
- Resume bullets in Section 20: any unsafe claims?
- Claim boundary in Section 18: does it match Section 9 of this handoff exactly?

**Check `docs/defense/PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf` (38 pages):**
- Run `scripts/build_defense_pdf_v5.py` and verify it produces the PDF without errors
- Does page count stay ≥35? (currently 38)
- Does the cover page show correct stats (AUC=0.7769, ECE=0.0034, 307,511 applicants, 140 features, 7 tables, 57.4M rows, GOLD 89.3%)?
- Does every Q&A avoid the forbidden claims?
- Is Section 8 (calibration) showing isotonic, not Platt?

### Pass 4 — Model Card Audit
**Check `docs/PULSEGUARD_MODEL_CARD.md`:**
- Is calibration listed as isotonic (not Platt)?
- Are test metrics correct (AUC=0.7769, ECE=0.0034)?
- Is deployment status listed as "NOT deployed — sklearn version incompatibility"?
- Are all limitations documented: reject inference, no timestamps, proxy fairness only, single geography?
- Is it ASSISTIVE_ONLY throughout for LLM governance?

### Pass 5 — RAG/LLM Governance Audit
**Check `src/pulseguard/policy_rag.py` and `src/pulseguard/llm_governance_assistant.py`:**
- Does BM25 abstain when score < 0.25?
- Does the OUT_OF_DOMAIN case (Case 5 in the demo) produce zero output?
- Does any LLM output path produce language that could be read as "approve" or "reject"?
- Is ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED, NOT_FINAL_DECISION tagged on every output?
- Is there any code path where the LLM response bypasses the human review requirement?

### Pass 6 — SHAP & Calibration Technical Audit
**SHAP:**
- Verify `pred_contrib=True` is used (not external SHAP library)
- Verify output shape is (n_samples, 141) — 140 features + 1 bias column
- Verify EXT_SOURCE_MEAN is rank-1 in the global SHAP importance output
- Verify bootstrap stability: top-5 features all present in all 30 bootstraps
- Verify local case PDs: GREEN=0.0335, AMBER=0.2056, RED=0.4164, CONFLICT=0.3475

**Calibration:**
- Verify `iso_x.npy` shape is (134,), `iso_y.npy` shape is (134,)
- Verify `iso_x` range is ~[0.003, 0.97]
- Verify that `np.interp(raw_prob, iso_x, iso_y)` gives values in [0, 1]
- Verify that `lgb_mono_champion.txt` has 140 features and 279 trees
- Verify ECE calculation: if you apply np.interp to the test set raw scores, the resulting ECE should be ≈0.0034

### Pass 7 — Claim Integrity Sweep
**Sweep every .md file for these forbidden phrases:**
- "production" (allowed: "portfolio project", "not production")
- "Platt selected" or "Platt calibration" without the forensics caveat
- "100 trials" or "100 Optuna trials" as if completed
- "CatBoost champion" or "CatBoost is the champion"
- "AUC=0.7716 tuned" (that's the baseline CatBoost)
- "live deployment" or "deployed to production"
- "LLM decides" or "model approves" or "model rejects"
- "fairness certified" or "disparate impact compliant"
- "AUC=0.62 is the champion" (it's the demo)
- "Platt selected" in Section 8 (must say isotonic after forensics fix)

### Pass 8 — GP5 Experiment Integrity Audit
- Verify `outputs/models/lgb_gp5_172_challenger.txt` exists and has 172 features
- Verify `outputs/models/lstm_encoder.pt` exists
- Verify `outputs/models/gp5_embeddings_train.npy`, `gp5_embeddings_val.npy`, `gp5_embeddings_test.npy` exist
- Verify `outputs/data/inst_sequences.npy` exists (shape should be N×50×3 for applicants with history)
- Verify the GP5 retrain script correctly appends 32 LSTM columns to 140 features = 172
- Verify the monotone constraint extension: GP2 had 15 constraints; GP5 should extend with 32 zeros for LSTM dims
- Verify GP5 challenger AUC is documented as 0.7264 (not 0.7769)
- Verify GP2 champion is retained, not replaced

---

## 11. KNOWN ISSUES & THEIR STATUS

| Issue | Status | Resolution |
|---|---|---|
| `gold_pass2_calibration_report.json` says "Platt selected" | DOCUMENTATION ERROR — known, not fixed in artifact | Defense doc Section 8 and Section 30 acknowledge and correct it. Isotonic is the true calibrator. |
| `champion_calibrated.pkl` version-locked (sklearn 1.7.2) | KNOWN LIMITATION | Documented in deployment caveat. iso_x/iso_y numpy arrays are the serving solution. |
| GP2 LightGBM champion not deployed | KNOWN GAP | Fully documented in Section 27D of defense doc and in this handoff. |
| Trial count 4-8 vs 100-trial plan | KNOWN CONSTRAINT (CPU) | Documented in gold_pass2_tuning_trace.json and in all defense Q&As. |
| No temporal validation | KNOWN LIMITATION | Home Credit has no timestamps. Documented in model card, fairness, and leakage artifacts. |
| Reject inference unaddressed | KNOWN LIMITATION | MNAR bias documented in model card and failure modes. |
| Fairness is proxy-only | KNOWN LIMITATION | No protected-class labels. Proxy audit documented with SKELETON label. |
| GP5 LSTM produces AUC degradation | NEGATIVE RESULT — documented | GP2 champion retained. Section 29 and gp5_augment_and_retrain.py output document this. |
| train-vs-val PSI ~8.1 | CALIBRATION ARTIFACT | Explained in Section 13 of defense doc. val-vs-test PSI=0.0002 is the meaningful metric. |

---

## 12. CHAMPION MODEL VERIFICATION COMMANDS

```bash
cd "/Users/ASUS/Documents/Professional/GitHub/beastmax (5)/pulseguard"

# Verify champion model
python3 -c "
import lightgbm as lgb, numpy as np
bst = lgb.Booster(model_file='outputs/models/lgb_mono_champion.txt')
print('Features:', bst.num_feature())   # expect 140
print('Trees:', bst.num_trees())        # expect 279
iso_x = np.load('outputs/models/iso_x.npy')
iso_y = np.load('outputs/models/iso_y.npy')
print('iso_x shape:', iso_x.shape)     # expect (134,)
print('iso_y shape:', iso_y.shape)     # expect (134,)
print('iso_x range:', iso_x.min(), '-', iso_x.max())
"

# Verify GP5 challenger
python3 -c "
import lightgbm as lgb
bst = lgb.Booster(model_file='outputs/models/lgb_gp5_172_challenger.txt')
print('GP5 features:', bst.num_feature())  # expect 172
"

# Verify evidence artifacts exist and parse
python3 -c "
import json, os
artifacts = [
    'gold_pass1_leakage_audit.json',
    'gold_pass2_final_untouched_test_report.json',
    'gold_pass2_champion_selection_report.json',
    'gold_pass3_threshold_scoreband_report.json',
    'gold_pass3_shap_reason_code_report.json',
    'gold_pass3_reason_code_stability.json',
    'pulseguard_final_gold_audit.json',
]
for a in artifacts:
    path = f'outputs/evidence/{a}'
    exists = os.path.exists(path)
    if exists:
        with open(path) as f:
            d = json.load(f)
        print(f'OK: {a} ({len(str(d))} chars)')
    else:
        print(f'MISSING: {a}')
"

# Rebuild the defense PDF
python3 scripts/build_defense_pdf_v5.py

# Verify page count
pdfinfo docs/defense/PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf | grep Pages
# expect >= 35
```

---

## 13. KEY GOTCHAS FOR THE AUDITOR

1. **Calibration confusion:** Multiple places may still say "Platt calibration" because that was the original (wrong) report. The ground truth is isotonic, confirmed forensically. Section 30 of the defense doc covers this. The artifact `gold_pass2_calibration_report.json` is the source of the error — it is NOT corrected in the artifact itself (artifact is frozen), but the defense documentation acknowledges and corrects it.

2. **Two separate PDFs exist:**
   - `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.pdf` — old, pre-v5 (~34 pages)
   - `docs/defense/PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf` — NEW v5 (38 pages, use this one)

3. **Two calibrator files:**
   - `outputs/models/champion_calibrated.pkl` — sklearn CalibratedClassifierCV, version-locked, NOT served
   - `outputs/models/iso_x.npy` + `iso_y.npy` — numpy arrays, what IS served via np.interp

4. **GP5 files are challenger, NOT champion.** `lgb_gp5_172_challenger.txt` (172 features, AUC=0.7264) is the GP5 experiment. `lgb_mono_champion.txt` (140 features, AUC=0.7769) is the champion.

5. **The G4 XGBoost demo model** (`champion_xgb.json`) is what the Cloud Run endpoint serves. Do not confuse it with the GP2 LightGBM champion.

6. **`gold_pass2_final_untouched_test_report.json` says "Platt"** — this is the calibration documentation error. The calibrator actually used was isotonic, producing ECE=0.003396. The artifact key `ece_platt` is a naming mistake; the value 0.003396 is the actual isotonic ECE on the test set.

7. **EXT_SOURCE_MEAN** is an engineered feature (average of EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3), not a raw column. It is the rank-1 global SHAP driver.

8. **scale_pos_weight = 11.39** = (1 - 0.0807) / 0.0807 = (n_negatives / n_positives) in the training set.

9. **The early-stopping bug** produced AUC=0.7203 for LightGBM in the G9A baseline. This looked plausible (5 points below CatBoost). It was only diagnosed at GP2 when the fix produced AUC=0.7734. The bug is documented but the baseline artifact `g9a_model_tournament_report.json` still shows 0.7203 — that is correct; it's what the buggy baseline produced.

10. **The defense markdown** has a "Section 8" about calibration. Before the forensics discovery it said "Platt selected." After the forensics discovery it should say "Isotonic selected." Verify this is the case in the current file.

---

## 14. SUCCESS CRITERIA FOR AUDIT COMPLETION

The audit is complete when ALL of the following are true:

- [ ] All evidence artifacts in Section 7 exist, parse as valid JSON, and contain the expected key metrics
- [ ] `lgb_mono_champion.txt` has 140 features and 279 trees
- [ ] `iso_x.npy` shape (134,) and `iso_y.npy` shape (134,) verified
- [ ] `scripts/build_defense_pdf_v5.py` runs without errors and produces ≥35 pages
- [ ] Defense doc Section 8 says "isotonic" (not "Platt")
- [ ] Defense doc Section 30 exists and correctly describes the forensics discovery
- [ ] Defense doc Section 29 exists with GP5 AUC=0.7264, delta=−0.0505, GP2 retained
- [ ] No forbidden claims found in any .md file (sweep from Section 10 Pass 7)
- [ ] `app.py` uses `joblib.load()` (not `pickle.load()`)
- [ ] `src/feature_pipeline.py` has `from __future__ import annotations`
- [ ] RAG/LLM assistant: BM25 abstain threshold fires correctly for OOD queries
- [ ] Model card (`docs/PULSEGUARD_MODEL_CARD.md`) shows isotonic calibration and correct test metrics
- [ ] GP5 challenger file exists (`lgb_gp5_172_challenger.txt`, 172 features)
- [ ] All 8 audit passes from Section 10 completed with zero unresolved findings

If any check fails: fix it, document the fix, re-run the relevant pass. Repeat until zero failures remain.

---

## 15. PROHIBITED ACTIONS DURING AUDIT

- Do NOT retrain the champion model
- Do NOT change champion from LightGBM_monotonic
- Do NOT modify `outputs/evidence/` JSON artifacts (they are frozen ground truth)
- Do NOT modify `outputs/models/lgb_mono_champion.txt`
- Do NOT add Taiwan Default Risk as primary dataset
- Do NOT add LendingClub
- Do NOT claim LLM makes decisions
- Do NOT claim production deployment, regulatory certification, or fairness certification
- Do NOT change the Gold Pass 2 composite score criteria retroactively

**You may:**
- Fix documentation errors (calibration label Platt → isotonic)
- Fix code bugs in scripts (if the script is wrong but evidence artifacts are correct, fix the script)
- Add missing documentation
- Improve the defense PDF (re-run `build_defense_pdf_v5.py` with improvements)
- Flag inconsistencies with clear explanations
- Suggest additions to the defense doc Q&A

---

*Handoff written by Claude Sonnet 4.6 | PulseGuard session 2026-06-23*  
*Project executor: Sidharth Kriplani | For audit by Claude Opus 4.8 (high effort)*
