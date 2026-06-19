# 00 — CONTROL TOWER
## PulseGuard · BeastMax Foundation

---

### One-Line Identity

PulseGuard is a risk-decision and model-governance platform that makes the full ML lifecycle auditable — from pre-training feature validity through champion/challenger promotion, drift detection, fairness audit, and credit/fraud decision simulation — answering whether a model is safe to use, explainable, and compliant.

---

### Source Projects Merged

| Repo | Role in PulseGuard | Status |
|------|--------------------|--------|
| `riskframe_platform` | Core: champion/challenger, PSI drift, fairness, calibration, policy engine | **Primary — full absorb** |
| `featureleakagelens` | Pre-training gate: 7 leakage checks, temporal integrity | **Full absorb** |
| `lendflow` | Credit/underwriting decision workflow: FOIR engine, hard-rule enforcement, hybrid RAG policy lookup, escalation logic | **Full absorb** |
| `nexussupply` | Optional: multi-signal risk fusion (Altman Z, FinBERT, ESG, graph contagion) | **Selective absorb — third-party/counterparty risk layer only; not forced** |

---

### What Survives

From **RiskFrame:**
- Champion/challenger framework (XGBoost vs LightGBM, 5-gate promotion)
- Platt calibration + ECE scoring
- Optuna HPO with ECE regression documentation
- PSI drift alerting (Day 7 WARN, Day 14 ALERT)
- Per-feature KS statistics
- Fairness audit (Disparate Impact, Equal Opportunity gap)
- Decision policy engine (APPROVE / REVIEW / REJECT) with versioned threshold log
- 30-day operational lifecycle simulation
- FastAPI serving with training-serving parity check
- 22/22 test suite
- Delayed label validation (bad-rate-by-bucket vs. predicted)

From **FeatureLeakageLens:**
- 7 pre-training leakage checks (2 tiers: WARN vs FAIL)
- Temporal availability check and training future date scan (FAIL-level)
- Structured JSON/Markdown/HTML audit report
- `LeakageAuditConfig` API
- 23 tests

From **LendFlow:**
- Deterministic-first design principle (FOIR recomputed from raw, hard rules no LLM)
- APPROVE / REFER / REJECT routing logic with escalation conditions
- Hybrid RAG over credit policy corpus (BM25 + ChromaDB + cross-encoder reranker)
- RAGAS faithfulness evaluation (0.91)
- PII redaction layer (Presidio)
- Tamper-evident JSONL audit trail
- 7-node pipeline architecture as template for PulseGuard decision workflow

From **NexusSupply (selective):**
- Composite multi-signal risk scoring formula (weighted fusion)
- Altman Z-score variant selection logic (3 variants by industry)
- Graph contagion propagation concept (optional third-party risk layer)
- XGBoost distillation from rule-based scores

---

### What Is Killed / Deprecated

- Standalone repo identities — PulseGuard absorbs all of them; original repos are not deprecated but are superseded by the consolidated platform narrative
- LendFlow's LangGraph 7-node pipeline as a standalone agentic story — absorbed into PulseGuard's decision workflow module
- NexusSupply's supplier/procurement framing — only the risk signal fusion mechanics are retained; supply chain narrative is dropped unless it strengthens credit/counterparty risk
- NexusSupply's FinBERT news sentiment and ESG parsing — deferred; not core to G1–G7
- Any claim of real NBFC deployment (LendFlow), real bank production (RiskFrame), or regulatory certification

---

### Regulatory Context

**SR 26-2 (April 2026)** — The Federal Reserve, FDIC, and OCC issued revised interagency guidance on model risk management, replacing SR 11-7 (rescinded April 17, 2026). The new guidance is principles-based and explicitly requires:
- Complete model lifecycle governance as "one governed chain, not snapshots at handoff points"
- Champion/challenger frameworks to be "versioned and reproducible"
- Ongoing monitoring tied to changing conditions, not just annual reviews
- Traditional ML remains fully in scope; generative AI explicitly excluded as "novel and rapidly evolving"

PulseGuard is designed to demonstrate SR 26-2 aligned governance artifacts. It does not claim regulatory certification.

---

### Target Role / JD Archetype + JD Keyword Mapping

| Role | How PulseGuard Speaks to It | Key JD Keywords Satisfied |
|------|-----------------------------|-----------------------------|
| Risk Data Scientist | Champion/challenger, calibration, PSI drift, fairness audit, decision policy | Full model lifecycle ownership; PSI monitoring; calibration; fairness audit |
| Fraud Data Scientist | Rule-based hard gate + SHAP explainability + escalation logic | Fraud score calibration; case disposition logic; deterministic rule enforcement |
| Credit Data Scientist | FOIR engine, underwriting workflow, reject inference boundary, delayed label validation | Credit risk modeling; label bias awareness; model monitoring; governance |
| ML Governance / Model Risk | Feature leakage audit, evidence ledger, SR 26-2 aligned governance sign-off | Model risk governance; independent validation; champion/challenger versioning |
| Decision Scientist | Decision policy versioning, policy-consequence chain, approval rate decomposition | Policy-model decoupling; decision routing; business consequence chain |

**Known JD Gaps (not covered by PulseGuard):**
- Network / graph-based link analysis (fraud) — deferred to G9
- Reject inference implementation — documented as boundary condition; not built
- Real-time < 100ms fraud scoring — simulated offline; FastAPI serving at G9

---

### Final Flagship Claim

> PulseGuard is a production-simulated, research-grade risk decision and model governance platform that unifies feature leakage detection, champion/challenger promotion, calibrated scoring, PSI drift alerting, fairness auditing, and credit underwriting decision simulation into a single auditable system — designed to answer whether a model should be approved, monitored, challenged, or retired.

---

### Known Boundary Conditions (G0 Research Finding)

These are material limitations that must appear in the model card and interview. They are not forbidden — they are documented:

- **Reject inference:** Model is trained on approved applicants only (Home Credit). Rejected applicants have no observed outcomes. Selection bias is present and unmitigated. This is a known limitation; documented in model card; not corrected in portfolio version.
- **PSI multivariate blindspot:** PSI is a univariate drift measure. Multivariate joint distribution shift can occur while all per-feature PSIs appear stable. This is documented in the monitoring design; Wasserstein/MMD deferred to G9.
- **Fairness on synthetic dataset:** CODE_GENDER in Home Credit is a public dataset field, not a real protected class in a deployed system. Fairness analysis methodology is correct; results are dataset-specific.
- **Temporal leakage checks on Home Credit:** Home Credit lacks feature-level timestamps natively. Synthetic timestamps are added at G3 to demonstrate the FAIL path. This is clearly documented.

---

### Forbidden Claims

- "Deployed at a bank / NBFC / fintech"
- "Real loan decisions were made using this system"
- "Regulatory compliance certified (RBI / Basel / SR 11-7 / SR 26-2)"
- "Trained on real customer data"
- "Production PSI / drift / fairness metrics"
- "Real-world model approval or rejection"
- "Validated against actual default outcomes"
- "Reject inference implemented" (unless G9 implements it)
- "NexusSupply CV AUC 1.00 is a valid model evaluation result" (it is circular on synthetic data)

---

### Current Status

**🏆 GOLD PASS 4/4 COMPLETE — PROJECT FROZEN · GOLD CHECKPOINTED · 89.3% · READY FOR INTERVIEW DEFENSE**

**Gold Pass 4 Summary (Final Freeze):** Gold audit — 15-dimension scoring, total 134/150=89.3%, verdict=GOLD · Gold Checkpoint doc produced (18-section project freeze) · Future Builds Backlog produced (high-value / nice-to-have / do-not-build) · Interview Defense Document produced (20 sections, 30+ Q&As, 15 failure modes, evidence table, claim boundary) · Interview Defense PDF generated · Resume + Opportunity Pack produced (5 resume bullets, 3 LinkedIn bullets, 3 one-liners, 60s + 2min spoken answers, what-not-to-say, SQL/Python relevance notes) · All 4 control docs updated to GOLD CHECKPOINTED. No retraining. No champion change. No scope reopening.

**Gold Pass 3 Summary:** Score-band policy (GREEN<0.20 / AMBER 0.20–0.40 / RED≥0.40) on test set (89.72% / 9.80% / 0.47%; DR 5.77% / 26.96% / 53.77%) · Cost-sensitive decisioning (scenario economics, cost-optimal t=0.47) · SHAP reason codes via LightGBM pred_contrib — EXT_SOURCE_MEAN rank-1 in 30/30 bootstraps, top-5 features all 30/30 stable · Fairness proxy audit skeleton (age, income, employment, region — no protected-class labels, no certification) · Drift baseline — val-vs-test PSI=0.0002 STABLE; all top-10 feature PSIs STABLE · RAG/LLM governance demo — 6 cases, abstain fires on OOD query, LLM never approves/rejects · Model card + governance report produced · 7 evidence JSONs produced.

**Gold Pass 2 Summary:** 5 models tuned via Optuna TPE (CatBoost, XGBoost, XGBoost_monotonic, LightGBM_base, LightGBM_monotonic) · Validation-only champion selection · Post-tuning Platt calibration · Composite 9-component champion score · Champion: **LightGBM_monotonic + Platt** (val_AUC=0.7734, composite=0.7312) · Governance champion: **same model** (monotone constraints qualify as SR 26-2 governance champion) · Final test (untouched): AUC=0.7769, ECE=0.0034, KS=0.4141, PR-AUC=0.2628 · Val-Test gap=−0.0035 ACCEPTABLE · Δ vs G9A baseline: AUC+0.0053, KS+0.0047 · 5 evidence JSONs + 4 plots + champion report doc produced.

**Gold Pass 1 Summary:** 23/23 artifact audit PASS · 21/21 data spine PASS · 10/10 leakage PASS (safe_to_tune=true) · temporal feasibility FEASIBILITY_LIMITED (no true time proxy, documented) · tournament quality BASELINE_NOT_TUNED (full PR-AUC/KS/Brier/ECE extracted) · RAG/LLM governance 10/10 PASS (abstain bug fixed, calibrated) · Pass 2 tuning plan written. 7 evidence JSONs produced.

**G9A COMPLETE — Home Credit Default Risk is the PRIMARY data spine.**

**G9A Summary:** 307,511 applicants · 57.4M total rows · 140 features · 12-model tournament · Champion (provisional baseline): CatBoost+Platt (AUC=0.7716, ECE=0.0054, KS=0.41) · Governance alt: LightGBM_Monotonic+Platt (AUC=0.7203, ECE=0.0016, 15 monotone constraints) · LM Studio policy RAG built · 23 artifacts delivered. Champion is PROVISIONAL — final champion re-selected after Pass 2 tuning on val set only.

**Dataset decisions LOCKED (frozen at Gold Pass 4):** Home Credit=PRIMARY · Taiwan Default=LEGACY_APPENDIX_ONLY · LendingClub=DROPPED_FROM_CURRENT_SCOPE

**PROJECT STATUS: GOLD CHECKPOINTED — No further passes planned. Resume and interview defense ready.**

---

#### Gate Log

| Gate | Status | Artifacts | Models Trained | Metrics Generated |
|------|--------|-----------|---------------|------------------|
| G0 | ✓ COMPLETE | 9 research docs + 7 control docs | None | None |
| G1 | ✓ COMPLETE | G1_repo_audit.md · G1_dataset_plan.md · verify_imports.py | None | None |
| G2 | ✓ COMPLETE | G2_decision_workflow.md · G2_data_contracts.md · G2_risk_signal_design.md | None | None |
| G3 + G3.1 | ✓ COMPLETE | G3_leakage_detection_notes.md · leakage_audit.py · add_synthetic_timestamps.py · group_leakage_check.py · generate_synthetic_data.py · outputs/evidence/leakage_report.{json,md,html} · outputs/evidence/group_leakage_report.json · outputs/evidence/g3_1_dgp_calibration_report.json | None | 1 FAIL (temporal, injected) · 1 WARN (DAYS_ID_PUBLISH categorical proxy) · 0 INSUFFICIENT_INPUT · 29 features · group leakage PASS · default_rate=8.17% (calibrated; was 26% at G3) |
| G4 | ✓ COMPLETE | G4_champion_model_notes.md · G4_drift_monitoring_notes.md · src/feature_pipeline.py · scripts/train_champion.py · scripts/seed_lifecycle.py · scripts/drift_monitor.py · outputs/evidence/g4_champion_training_report.json · outputs/evidence/g4_calibration_report.json · outputs/evidence/g4_drift_report.json · outputs/plots/g4_calibration_curve.png · outputs/plots/g4_drift_psi_ext_source_2.png · outputs/models/{champion_xgb.json, champion_calibrated.pkl, preprocessor.pkl} | XGBoost champion (n=9 trees, early stopping) + Platt calibration | ROC-AUC=0.6237 · PR-AUC=0.1337 · ECE=0.00159 (calibrated) · Bayes ceiling=0.6261 · Day 7 WARN PSI=0.1532 · Day 14 ALERT PSI=0.2974 |
| G5 | ✓ COMPLETE | G5_fairness_audit_notes.md · scripts/fairness_audit.py · outputs/evidence/g5_fairness_report.json · outputs/plots/g5_score_distribution.png | Champion (calibrated) applied to test set | DI=1.0127 (PASS) · EOpp gap=2.2pp · PPV gap=0.2pp · CODE_GENDER rank #24/28 (gain=5.62; not a top driver) |
| G5.5 | ✓ COMPLETE | docs/G5_5_PUBLIC_DATASET_RESEARCH.md · docs/G5_5_DATASET_DECISION_MATRIX.md · outputs/evidence/g5_5_dataset_research_summary.json · data/public/taiwan_credit_default.xls | None (research gate) | 7 datasets evaluated · Taiwan Default = USE_NOW (downloaded, 30k rows, 22.12% DR, real demographics) · Home Credit = USE_LATER (Kaggle auth) · LendingClub = USE_LATER (G9 reject inference) · German Credit = EXCLUDE |
| G6 | ✓ COMPLETE | docs/G6_real_data_champion_challenger_notes.md · scripts/g6_taiwan_adapter.py · scripts/g6_champion_challenger.py · outputs/evidence/g6_taiwan_data_profile.json · outputs/evidence/g6_champion_challenger_report.json · outputs/evidence/g6_calibration_report.json · outputs/plots/g6_calibration_curve.png · outputs/plots/g6_model_comparison.png | XGBoost champion (57 trees, early stopping) + Platt calibration on Taiwan Default | ROC-AUC=0.7852 · PR-AUC=0.5709 · Brier=0.1329 · ECE raw=0.2082 → ECE calibrated=0.0112 (94.6% reduction) · LightGBM challenger HELD · LR baseline REJECTED |
| G7 | ✓ COMPLETE (taiwan_primary_patch_v1) | docs/G7_threshold_decision_policy_notes.md · scripts/g7_taiwan_threshold_patch.py · outputs/evidence/g7_taiwan_threshold_policy_report.json · outputs/evidence/g7_cost_sensitivity_report.json · outputs/plots/g7_taiwan_cost_curve.png · outputs/plots/g7_taiwan_policy_bands.png | None (threshold analysis uses G6 champion) | Policy: taiwan_real_data_v1.0 (PRIMARY lane) · Bayes-optimal θ* = C_reject/(C_bad+C_reject) = 1/11 ≈ 9% · 3-zone: APPROVE PD<0.20 (65.1%) / REVIEW 20–40% (19.0%) / REJECT PD≥40% (15.9%) · EL=1.140/app (C_bad=10, C_reject=1) · Observed DR: approve=10.7% / review=27.2% / reject=62.7% · Calibrated EL < raw EL across all thresholds · Synthetic = SECONDARY stress-test only |
| G8 | ✓ COMPLETE | docs/G8_MODEL_CARD.md · docs/G8_GOVERNANCE_SIGNOFF_PACKET.md · docs/G8_MONITORING_AND_INCIDENT_POLICY.md · docs/G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md · docs/G8_LIMITATIONS_AND_ADVERSE_ACTION_BOUNDARY.md · outputs/evidence/g8_governance_packet_summary.json | None (governance documentation gate) | launch_status=NOT_PRODUCTION_READY · governance_status=PENDING_SIGNOFF · 24/25 approval checklist items COMPLETE · 3/6 fairness items COMPLETE (Taiwan Default fairness deferred to G9) · 10 forbidden claims documented · 7 G9 requirements specified |
| G8.1 | ✓ COMPLETE | scripts/run_g8_1_data_provenance_audit.py · outputs/evidence/g8_1_data_provenance_audit.json · docs/G8_1_DATA_PROVENANCE_AND_REALISM_AUDIT.md | None (provenance audit gate) | provenance_status=PASS · 20/20 checks · SHA256 exact match to live UCI download · acquisition method documented (prior Claude agent session, G5.5) · no synthetic contamination · G9 UNBLOCKED |
| RISKFRAME_GOLD_AUDIT | ✓ COMPLETE | docs/PULSEGUARD_RISKFRAME_GOLD_AUDIT.md · outputs/evidence/pulseguard_riskframe_gold_audit.json | None (meta-audit gate) | Score=104/150 (69%) · Verdict=STRONG_NEEDS_MEAT_PASS · provenance_status=PASS · taiwan_realism_decision=BRIDGE_ONLY · 15 gaps documented · G9 confirmed next: Taiwan fairness + calibrated LightGBM + SHAP + KS · G10 Home Credit realism lane scheduled |
| G9 | SUPERSEDED by G9A | — | — | Original Taiwan fairness lane superseded by G9A Home Credit primary spine scope reset. Taiwan Default retained as LEGACY_APPENDIX_ONLY. |
| GOLD_PASS_1 | ✓ COMPLETE | outputs/evidence/gold_pass1_artifact_audit.json · gold_pass1_data_spine_validation.json · gold_pass1_leakage_audit.json · gold_pass1_temporal_vintage_feasibility.json · gold_pass1_tournament_quality_audit.json · gold_pass1_rag_llm_governance_audit.json · docs/PULSEGUARD_GOLD_PASS2_TUNING_PLAN.md | None (audit gate) | 23/23 artifact PASS · 21/21 data spine PASS · 10/10 leakage PASS · safe_to_tune=true · temporal=FEASIBILITY_LIMITED · tournament=BASELINE_NOT_TUNED · RAG=10/10 PASS · policy_rag.py abstain bug fixed (corpus ceiling calibration) |
| GOLD_PASS_2 | ✓ COMPLETE | outputs/evidence/gold_pass2_tuning_trace.json · gold_pass2_validation_model_comparison.json · gold_pass2_calibration_report.json · gold_pass2_champion_selection_report.json · gold_pass2_final_untouched_test_report.json · 4 plots · docs/PULSEGUARD_GOLD_PASS2_TUNED_CHAMPION_REPORT.md | LightGBM_monotonic CHAMPION (val_AUC=0.7734, composite=0.7312) + GOVERNANCE_CHAMPION (same model — monotone constraints qualify for SR 26-2 alignment) | Test AUC=0.7769 · PR-AUC=0.2628 · KS=0.4141 · Brier=0.0668 · ECE_platt=0.0034 · Val-Test gap=−0.0035 (ACCEPTABLE) · Δ vs G9A baseline: AUC+0.0053, KS+0.0047 · safe_to_pass3=true |
| GOLD_PASS_3 | ✓ COMPLETE | outputs/evidence/gold_pass3_threshold_scoreband_report.json · gold_pass3_cost_sensitive_decisioning.json · gold_pass3_shap_reason_code_report.json · gold_pass3_reason_code_stability.json · gold_pass3_fairness_proxy_audit.json · gold_pass3_drift_vintage_stress.json · gold_pass3_rag_llm_demo_report.json · docs/PULSEGUARD_MODEL_CARD.md · docs/PULSEGUARD_GOLD_PASS3_GOVERNANCE_REPORT.md | No retraining — governance layers added to Pass 2 champion | GREEN<0.20 (89.72%, DR=5.77%) · AMBER 0.20–0.40 (9.80%, DR=26.96%) · RED≥0.40 (0.47%, DR=53.77%) · SHAP top-5 stable 30/30 bootstraps · EXT_SOURCE_MEAN rank-1 30/30 · PSI val-vs-test=0.0002 STABLE · RAG/LLM 6-case demo · safe_to_pass4=true |
| GOLD_PASS_4 | ✓ COMPLETE — **🏆 GOLD CHECKPOINTED** | outputs/evidence/pulseguard_final_gold_audit.json · docs/PULSEGUARD_GOLD_CHECKPOINT.md · docs/PULSEGUARD_FUTURE_BUILDS_BACKLOG.md · docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md · docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.pdf · docs/PULSEGUARD_RESUME_OPPORTUNITY_PACK.md | No retraining · No champion change · No scope reopening | Gold audit: 134/150=89.3% GOLD · 15 dimensions scored · Perfect 10s: leakage_discipline, calibration_quality, reason_code_stability, evidence_honesty · Interview defense: 20 sections, 30+ Q&As, 15 failure modes · Resume pack: 5 bullets, 3 LinkedIn bullets, 60s + 2min spoken answers · PROJECT FROZEN |
| G9A | ✓ COMPLETE | docs/G9A_HOME_CREDIT_PRIMARY_SPINE.md · docs/G9A_HOME_CREDIT_FEATURE_FACTORY.md · docs/G9A_FULL_MODERN_MODEL_TOURNAMENT.md · docs/G9A_VINTAGE_TEMPORAL_REALISM_AUDIT.md · docs/G9A_CREDIT_INTELLIGENCE_ARCHITECTURE.md · docs/G9A_LM_STUDIO_RAG_LLM_GOVERNANCE_LAYER.md · src/pulseguard/policy_rag.py · src/pulseguard/llm_governance_assistant.py · data/policy_docs/sample_credit_policy.md · outputs/evidence/g9a_home_credit_data_audit.json · outputs/evidence/g9a_feature_factory_report.json · outputs/evidence/g9a_model_tournament_report.json · outputs/evidence/g9a_calibration_governance_report.json · outputs/evidence/g9a_shap_summary.json · outputs/plots/g9a_roc_curves.png · outputs/plots/g9a_calibration_curves.png · outputs/plots/g9a_shap_importance.png · docs/examples/G9A_INTERVIEW_QA.md · docs/examples/G9A_CLAIM_SAFE_EXAMPLES.md · docs/examples/G9A_GOVERNANCE_ASSISTANT_DEMO.md | CatBoost champion (AUC=0.7716, ECE=0.0054 post-Platt, KS=0.41) + LightGBM_Monotonic governance alt (AUC=0.7203, ECE=0.0016, 15 monotone constraints) | 12-model tournament · 2 HARD_FAIL (TabNet CPU, sklearn GBM) · SHAP top feature: EXT_SOURCE_3 · Calibration: ECE 0.32→0.0054 (CatBoost+Platt) · Dataset: 307,511 rows, 8.07% DR, 140 features, 57.4M total rows · scale_pos_weight=11.39 · Known limits: MNAR reject inference, no temporal split, single geography |

**Evidence ledger status (post-G9A):**
- Evidence ledger rows: #1 (repo audit) HIGH, #2 (leakage) HIGH, #3 (champion synthetic) HIGH, #4 (drift) HIGH, #5 (fairness) HIGH, #6 (G6 champion/challenger real data) HIGH, #7 (G7 threshold policy) HIGH, RISKFRAME_GOLD_AUDIT (meta) HIGH, G9A data audit HIGH, G9A feature factory HIGH, G9A model tournament HIGH, G9A calibration governance HIGH, G9A SHAP summary HIGH
- G5.5 meta-entry: dataset research = HIGH
- Models trained: (1) Synthetic lane — XGBoost champion (9 trees) + Platt on synthetic_home_credit_like; (2) Real-data lane — LR baseline + XGBoost (57 trees) + LightGBM (9 trees) + Platt on Taiwan Default
- Synthetic metrics: ROC-AUC=0.6237 · PR-AUC=0.1337 · ECE=0.00159 · Day7 PSI=0.1532 WARN · Day14 PSI=0.2974 ALERT · DI=1.0127 PASS
- Real-data metrics (Taiwan): ROC-AUC=0.7852 · PR-AUC=0.5709 · Brier=0.1329 · ECE calibrated=0.0112 (94.6% reduction from 0.2082) · Champion retained (LightGBM HELD, LR REJECTED)
- All RiskFrame/LendFlow/FLL source-reference numbers (SR-1 through SR-14) remain SOURCE_REFERENCE

---

#### G8 Summary — Model Risk Governance + Decision Accountability Pack

**Model ID:** `pulseguard-taiwan-xgb-platt-v1` · **Policy ID:** `taiwan_real_data_v1.0`
**Governance status:** `PENDING_SIGNOFF` · **Launch status:** `NOT_PRODUCTION_READY`

**5 governance documents produced:**
- **G8_MODEL_CARD.md** (21 KB): Model purpose, intended/OOS use, dataset (Taiwan Default, 30k rows, 22.12% DR, 2005), target definition, model family (XGBoost + Platt, 57 trees), 23 features, performance (ROC=0.7852, PR=0.5709, ECE=0.0112), calibration summary, threshold policy, fairness gap (Taiwan audit deferred), monitoring plan, known limitations (8), known failure modes (6), human review role, claim boundaries.
- **G8_GOVERNANCE_SIGNOFF_PACKET.md** (15 KB): 6 roles defined (Decision/Model/Risk/Data/Monitoring/Compliance owner); 4-section approval checklist (24/25 COMPLETE; Taiwan fairness = open gap); 10-item pre-launch checklist (0/10 satisfied = expected for portfolio project); 8 launch blockers; 7 mandatory-review triggers; threshold-change approval process; rollback/disable criteria (immediate disable conditions documented).
- **G8_MONITORING_AND_INCIDENT_POLICY.md** (13 KB): 5 independent monitors (PSI, ECE, score distribution, approval rate, delayed-label DR); PSI WARN/ALERT thresholds for PAY_0, PAY_2, LIMIT_BAL, BILL_AMT1 + 19 secondary features; ECE triggers (WARN=0.025, ALERT=0.05, CRITICAL=0.10); approve-zone DR triggers (WARN=20%, ALERT=25%, CRITICAL=35%); 4 severity levels (OK/WARN/ALERT/CRITICAL) with SLAs; freeze conditions; retraining review conditions.
- **G8_HUMAN_REVIEW_AND_OVERRIDE_POLICY.md** (13 KB): 3-zone workflow diagram; reviewer information access spec; information withheld (SEX, raw score); 6 prohibited reviewer behaviours; full override logging JSON schema; 10 override reason codes (RC-01 through RC-99); 8 audit trail fields; escalation path (4 escalation triggers); override rate monitoring (reference rates + WARN/ALERT thresholds).
- **G8_LIMITATIONS_AND_ADVERSE_ACTION_BOUNDARY.md** (15 KB): 5 explicit no-claim declarations (no production, no regulatory, no adverse-action automation, no fairness certification, no real bank economics); Taiwan Default limitations (8 items); synthetic harness limitations; 11-item what-would-be-needed-for-actual-deployment list.

**Machine-readable artifact:** `outputs/evidence/g8_governance_packet_summary.json` — 13 evidence artifacts logged, 10 forbidden claims, 7 G9 required deliverables, all monitoring triggers, all human review rules.

**Key G8 gap documented:** Taiwan Default fairness audit at G7 thresholds (SEX/EDUCATION/MARRIAGE approval rates at 0.20/0.40) not completed. Male DR=24.17%, female DR=20.78% — identical thresholds will produce different group outcomes; whether disparate impact applies is unknown. This is G9's first required deliverable.

---

#### G7 Summary — Threshold / Cost-Sensitive Decision Policy (taiwan_primary_patch_v1)

**Primary lane:** XGBoost (Platt calibrated) — G6 champion on Taiwan Default (`PUBLIC_REAL_TAIWAN_DEFAULT`).
**Secondary lane:** Synthetic harness — stress-test only; not the headline business policy.

**Cost notation (corrected):**
- C_bad = cost of approving a defaulter (bad-debt charge-off) — normalised to 10
- C_reject = cost of rejecting a good applicant (lost revenue) — normalised to 1
- C_review = manual review labour — normalised to 0.3
- Ratio C_bad/C_reject = 10:1 (base assumption)

**Bayes-optimal threshold formula:** θ* = C_reject / (C_bad + C_reject) = 1 / (10+1) ≈ 9%. Empirical sweep confirms min-EL at θ=0.10, approval rate=77.9%. Validates Platt calibration accuracy — theoretical optimum matches empirical sweep.

**Chosen 3-zone policy (`taiwan_real_data_v1.0` — PRIMARY lane):**
- APPROVE: PD < 0.20 → 65.1% of applicants; observed DR in zone = 10.7%
- REVIEW: 0.20 ≤ PD < 0.40 → 19.0% of applicants; observed DR = 27.2%
- REJECT: PD ≥ 0.40 → 15.9% of applicants; observed DR = 62.7%
- Expected loss: 1.140 per application (normalised, C_bad=10, C_reject=1)

**Calibration-aware decisioning:** Calibrated EL < raw EL across all thresholds. Raw XGBoost (ECE=0.208) cannot support interpretable thresholding. Calibrated (ECE=0.011): "PD=0.20 means ~20% true default probability" — confirmed in policy-bands decile check.

**Cost sensitivity (ratios tested: 2:1, 5:1, 10:1, 20:1):** Optimal θ moves 0.32→0.07 as ratio increases; approval rate stable ~78% across ratios.

**Retraining trigger:** PSI > 0.20 on PAY_0/PAY_2 OR observed default rate > 25% in approve cohort.

**Artifacts:** `docs/G7_threshold_decision_policy_notes.md` · `scripts/g7_taiwan_threshold_patch.py` · `outputs/evidence/g7_taiwan_threshold_policy_report.json` · `outputs/evidence/g7_cost_sensitivity_report.json` · `outputs/plots/g7_taiwan_cost_curve.png` · `outputs/plots/g7_taiwan_policy_bands.png`

---

#### G6 Summary — Real-Data Champion/Challenger

**Data lane:** `PUBLIC_REAL_TAIWAN_DEFAULT` — UCI Credit Card Default, 30,000 rows, 22.12% default rate, zero missing values.

**Split:** 18,000 / 6,000 / 6,000 (60/20/20, stratified, seed=42).

**Features:** 23 features (17 numeric + LIMIT_BAL + AGE + 6 payment status cols + 6 bill amounts + 6 payment amounts; 3 categorical: SEX, EDUCATION, MARRIAGE via OneHotEncoder; StandardScaler on numerics).

**Models trained:**
- LR Baseline: `LogisticRegression(C=0.1, class_weight='balanced')`
- XGBoost champion: `XGBClassifier(n_estimators=500, early_stopping_rounds=50, eval_metric=aucpr)` → best_iteration=57 + Platt sigmoid calibration on val
- LightGBM challenger: `LGBMClassifier(n_estimators=500, early_stopping_rounds=50)` → best_iteration=9

**Test-set metrics:**

| Model | ROC-AUC | PR-AUC | Brier | ECE |
|-------|---------|--------|-------|-----|
| LR Baseline | 0.7283 | 0.5138 | 0.2047 | 0.2347 |
| XGBoost (raw) | 0.7852 | 0.5709 | 0.1778 | 0.2082 |
| LightGBM | 0.7742 | 0.5525 | 0.1553 | 0.1321 |
| **XGBoost (Platt)** ⭐ | **0.7852** | **0.5709** | **0.1329** | **0.0112** |

**Platt calibration impact:** ECE 0.2082 → 0.0112 (94.6% reduction) — largest calibration improvement across all PulseGuard gates.

**Champion/challenger decision:** XGBoost (Platt) retained as champion. LightGBM HELD (ECE gate fails vs calibrated champion; uncalibrated comparison — noted as limitation). LR REJECTED.

**Key comparison to SR-1:** Taiwan ROC-AUC 0.7852 > Home Credit SR-1 0.7663. Noted as dataset-specific, not a model superiority claim.

**G7 scope note:** FOIR module not directly applicable to credit card context (no EMI/income in Taiwan Default). G7 must define credit card decision policy or document as scope boundary.

**Artifacts:** `docs/G6_real_data_champion_challenger_notes.md` · `outputs/evidence/g6_taiwan_data_profile.json` · `outputs/evidence/g6_champion_challenger_report.json` · `outputs/evidence/g6_calibration_report.json` · `outputs/plots/g6_calibration_curve.png` · `outputs/plots/g6_model_comparison.png`

---

#### G5.5 Summary — Public Dataset Realism Gate

**Purpose:** Establish a real/public data lane before G6 Champion/Challenger. Do not run G6 on synthetic-only data.

**Datasets evaluated:** 7 — Home Credit, LendingClub, HMDA 2022, FICO HELOC, Give Me Some Credit, Taiwan Default, German Credit.

**Decision outcome:**
- **USE_NOW (1):** Taiwan Default (UCI) — downloaded to `data/public/taiwan_credit_default.xls`; 30,000 rows; 22.12% default rate; real demographics (SEX, AGE, EDUCATION, MARRIAGE); male DR=24.17%, female DR=20.78%; 6-month payment panel; zero missing values; no auth required.
- **USE_LATER (3):** Home Credit (Kaggle auth; G4–G6 re-run target); LendingClub (G9 reject inference); HMDA (G9+ approval fairness lane only).
- **FALLBACK (2):** FICO HELOC (primary page offline; no demographics); Give Me Some Credit (Kaggle auth; feature-poor).
- **EXCLUDE (1):** German Credit (1,000 rows; 1994 data; toy scale).

**Two-lane architecture established:**
- Synthetic harness (G3–G5): controlled failure injection, known Bayes ceiling, protocol testing — RETAINED.
- Real data lane (G6+): Taiwan Default for business-realistic champion/challenger and genuine fairness audit — IMMEDIATE.

**Pending G6 decision:** Which lane does G6 run on? Recommended = Option C: Taiwan Default as primary G6 evidence; synthetic harness retained for injected failure tests only.

**Artifacts:** `docs/G5_5_PUBLIC_DATASET_RESEARCH.md` · `docs/G5_5_DATASET_DECISION_MATRIX.md` · `outputs/evidence/g5_5_dataset_research_summary.json` · `data/public/taiwan_credit_default.xls`

---

#### G5 Summary — Fairness Audit

**Group:** CODE_GENDER (F/M) — synthetic proxy attribute; p=[0.65, 0.35]; NOT in DGP logit; NOT a real protected class.

**Test set:** 10,000 rows (same 60/20/20 split, seed=42 as G4). F=6,444, M=3,556.

**Policy:** Synthetic v1.0 — APPROVE (PD<0.06) / REVIEW (0.06–0.28) / REJECT (PD≥0.28).

**Key results:**
- **Disparate Impact (F/M) = 1.0127 → PASS** (band 0.80–1.25)
- Equal Opportunity gap = 2.2 pp (TPR: F=88.2%, M=86.0%)
- Predictive Parity gap = 0.2 pp (PPV: F=9.2%, M=9.4%)
- ROC-AUC gap = 3.7 pp (F=0.637, M=0.600) — sampling variance in smaller M group
- ECE gap = 0.006 (both groups well-calibrated)
- **CODE_GENDER feature rank: #24/28** (gain=5.62 vs DAYS_EMPLOYED=27.21) — not a primary driver

**Hard rule verified:** No SHAP computed (G5-forbidden). XGBoost gain rank used as lightweight proxy.

**Artifacts:** `outputs/evidence/g5_fairness_report.json` (4,371 B) · `outputs/plots/g5_score_distribution.png`

---

#### G4 Summary — Champion Model + Drift Monitoring Kernel

**Dataset:** `synthetic_home_credit_like` — 50,000 rows, stratified 60/20/20 split, seed=42. Default rate: train=0.082, val=0.082, test=0.082. DGP intercept −4.20703 (calibrated at G3.1).

**Feature pipeline (`src/feature_pipeline.py`):** 28 training features — 20 numeric + 8 categorical. Leakage columns hard-excluded: `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` (G3 FAIL) and `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` (FOIR input). Preprocessor fit on train only.

**Champion model (`scripts/train_champion.py`):**
- XGBoostClassifier: n_estimators=1000, max_depth=5, lr=0.05, early_stopping_rounds=50, eval_metric=aucpr
- Best iteration: **9** (early stopping; Bayes-optimal ceiling=0.6261; 99.6% efficiency)
- Platt sigmoid calibration fit on validation set
- **ROC-AUC=0.6237 · PR-AUC=0.1337 · Brier=0.07381 · ECE raw=0.01105 · ECE calibrated=0.00159**
- Top feature: DAYS_EMPLOYED (gain 0.1366); second: EXT_SOURCE_2 — matches DGP signal design

**Drift kernel (`scripts/seed_lifecycle.py` + `scripts/drift_monitor.py`):**
- 30 daily batches of 2,000 rows; reference = training split (30,000 rows)
- PSI (10 equal-frequency bins) + KS per feature per day
- **Day 7 EXT_SOURCE_2 PSI=0.1532, KS=0.1935 → WARN ✓**
- **Day 14 EXT_SOURCE_2 PSI=0.2974, KS=0.2927 → ALERT ✓**
- Days 1–6: OK ✓; Days 7–13: all WARN ✓; Days 14–30: all ALERT ✓

**Source-reference boundary:** SR-1 (ROC-AUC 0.7663), SR-2 (PR-AUC 0.2611), SR-3 (ECE 0.0046), SR-6 (PSI 0.2358) remain SOURCE_REFERENCE. PulseGuard-built values are lower (AUC) due to synthetic DGP with 6 signal features vs. real Home Credit data with hundreds of features.

**Artifacts:** `outputs/evidence/g4_champion_training_report.json` (4,663 B) · `outputs/evidence/g4_calibration_report.json` (1,453 B) · `outputs/evidence/g4_drift_report.json` (110,360 B) · `outputs/plots/g4_calibration_curve.png` · `outputs/plots/g4_drift_psi_ext_source_2.png` · `outputs/models/champion_xgb.json` · `outputs/models/champion_calibrated.pkl` · `outputs/models/preprocessor.pkl`

---

#### G3.1 Summary — Synthetic DGP Calibration Patch

**Blocker resolved:** G3 was accepted but G4 was blocked because the DGP intercept −2.8 produced 26% default rate vs. 8% target.

**Method:** Binary search on logistic intercept using N=200,000; converged at **intercept = −4.20703** in 8 iterations. Verified on N=50,000 across 5 seeds (range: 7.86%–8.19%, mean 8.05%). Production run: **default_rate = 0.0817** (8.17%) ✓

**Leakage re-audit on calibrated data — all checks behave as required:**
- Temporal FAIL: PASS (still fires on EXTERNAL_BUREAU_QUERY_RESULT__INJECTED) ✓
- Group leakage clean split: PASS (0 overlap) ✓
- Group leakage injected contamination: FAIL (500 IDs, 4.762%) ✓
- DAYS_ID_PUBLISH WARN: still present (gap=0.667) ✓
- DAYS_EMPLOYED WARN: dropped (expected — gap falls below threshold at 8% rate; predictor retained)

**Artifact:** `outputs/evidence/g3_1_dgp_calibration_report.json` (3,309 bytes)
**G4 status: UNBLOCKED**

---

#### G3 Summary

**Dataset:** `synthetic_home_credit_like` (Kaggle CLI not available; synthetic fallback per G1_dataset_plan.md). 50,000 rows · 30 features + 4 synthetic augmentations. Default rate (train): 0.2600. **Known issue:** DGP intercept −2.8 produces 26% not 8% target rate; must be corrected to −4.5 before G4 training.

**FeatureLeakageLens (FLL) results — ACTUAL:**
- Overall status: **FAIL**
- 1 FAIL: `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` — temporal leakage (feature timestamp > outcome timestamp for all 50,000 rows; injected FAIL path as designed)
- 2 WARN: `DAYS_EMPLOYED` and `DAYS_ID_PUBLISH` — categorical proxy (target-rate gap 1.000; legitimate predictors, not leakage; WARN is expected, documented)
- 0 INSUFFICIENT_INPUT: split_col provided; all 7 checks could run
- 29 features checked (7 excluded via ignore_cols: ID, timestamps, SPLIT, SYNTHETIC field)

**PulseGuard group leakage check — ACTUAL:**
- SK_ID_CURR uniqueness: PASS (50,000 unique IDs)
- Clean 60/20/20 split: PASS (0 overlap between train and val)
- Contaminated split (INJECTED): FAIL (500 duplicated IDs, 4.762% of val contaminated)
- Overall: PASS (clean split is operative result)

**G4 pre-requisites identified:**
1. Correct DGP intercept from −2.8 to ~−4.5 and regenerate dataset
2. Exclude `EXTERNAL_BUREAU_QUERY_RESULT__INJECTED` and `EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC` from training features
3. Verify default_rate ≈ 8% before fitting any model

**Artifacts:** `docs/G3_leakage_detection_notes.md` · `scripts/leakage_audit.py` · `scripts/add_synthetic_timestamps.py` · `scripts/group_leakage_check.py` · `scripts/generate_synthetic_data.py` · `outputs/evidence/leakage_report.json` (2,725 B) · `outputs/evidence/leakage_report.md` (2,223 B) · `outputs/evidence/leakage_report.html` (2,717 B) · `outputs/evidence/group_leakage_report.json` (2,624 B)

---

#### G2 Summary

**PRD Gap found and patched:** `01_BEASTMAX_PRD.md` listed "G1–G5" as MVP scope but the decision policy engine is G7, not G5. MVP scope corrected to G1–G8. No other PRD gaps found.

- **`docs/G2_decision_workflow.md`** — 19-stage pipeline across 5 phases (Pre-Training → Training → Decision → Monitoring → Governance). All stages carry DEFERRED or SIMULATED labels. FOIR synthetic gap documented. Deferred component registry (10 items, all G9). Synthetic component registry (11 items: lifecycle batches, drift events, policy change, delayed labels, FOIR field, synthetic timestamps, injected leakage column, adverse action codes).
- **`docs/G2_data_contracts.md`** — Full schemas for all 9 module boundaries: feature set input (34 columns: 30 real/public + 4 synthetic augmentation), leakage audit output, champion model output, challenger output, drift report, fairness report, policy output (22 fields per application), audit/governance record (tamper-evident JSONL), evidence ledger index.
- **`docs/G2_risk_signal_design.md`** — 8 signal categories, 18 total signals. All DEFERRED. FOIR gap fully specified: `EXISTING_OBLIGATIONS_MONTHLY` is SYNTHETIC (5–25% of AMT_INCOME_TOTAL); interview phrasing documented. SHAP API compatibility note (shap.Explainer vs TreeExplainer for xgb 3.2). All 14 source-reference rows confirmed unchanged.

---

#### G1 Summary

- **`docs/G1_repo_audit.md`** — 50 assets classified across 4 source repos.
- **`docs/G1_dataset_plan.md`** — Home Credit preferred; synthetic fallback fully specified.
- **`scripts/verify_imports.py`** — 16/16 PASS, exit 0 (2026-06-16).

---

#### Evidence Ledger Status (post-G2)

**PulseGuard-built artifacts: 4 / 15**

- #1 (G1 repo audit) — **HIGH** — artifact exists
- #2 (G3 leakage audit + G3.1 DGP calibration) — **HIGH** — artifacts exist
- #3 (G4 champion model) — **HIGH** — g4_champion_training_report.json, g4_calibration_report.json
- #4 (G4 drift monitoring) — **HIGH** — g4_drift_report.json, g4_drift_psi_ext_source_2.png
- #5–#15 — **DEFERRED** — no build gate closed yet
- G2 design docs (3) — complete but are design artifacts, not evidence ledger entries

All SOURCE_REFERENCE rows (SR-1 through SR-14) remain unchanged. No RiskFrame metric has been re-run inside PulseGuard.

---

G0 Gold Alignment Audit score: **6.4/10 average** (15-axis rubric; Axis 3 Industry Realism raised from 5→7 after Nubank/Stripe/DataRobot engineering blog research). Target after G8: 8.0/10. Target after G10 (Gold): 9.0/10.

**Key industry validation from blog/GitHub research:**
- **Nubank Engineering Blog (2024):** "Policy/Decision Layer monitoring" = PulseGuard's approval rate decomposition. Percentile monitoring = G4 enhancement.
- **Stripe (Jan 2025):** Aggregate PSI misses segment degradation at production scale — directly validates PSI multivariate blindspot.
- **SAIL paper (Annals of Operations Research, 2025):** Graph-based reject inference = concrete G9 implementation path.
- **No open-source repo** combines leakage → calibration → drift → fairness → champion/challenger → governance sign-off as an integrated lifecycle platform.
