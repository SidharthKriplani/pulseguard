# PulseGuard — Gold Pass 3/4: Governance Report

**Gate:** GOLD_PASS_3 | **Status:** COMPLETE  
**Date:** 2026-06-17 | **Champion:** LightGBM_monotonic + Platt calibration  

---

## 1. Pass 3 Scope

Gold Pass 3 converts the tuned calibrated champion from Pass 2 into a full credit-risk governance artifact. It does not retune or re-select the model. It adds the governance layers required before any model proceeds toward deployment review: score-band policy, cost-sensitive decisioning, SHAP reason codes, fairness audit skeleton, drift monitoring baseline, and RAG/LLM governance demo.

---

## 2. Score Band Policy (Section B/C)

### Balanced Three-Zone Policy

| Band | PD Threshold | Test Applicants | Approval Rate | Band Default Rate |
|---|---|---|---|---|
| GREEN | PD < 0.20 | 55,183 (89.72%) | Auto-approve eligible | 5.77% |
| AMBER | 0.20 ≤ PD < 0.40 | 6,030 (9.80%) | Manual review | 26.96% |
| RED | PD ≥ 0.40 | 290 (0.47%) | Enhanced underwriting | 53.77% |

**Rationale for PD=0.20 as GREEN/AMBER boundary:** A calibrated PD of 0.20 carries a semantic interpretation — the model estimates a 20% probability of default for applicants near this boundary. The observed default rate in the GREEN band (5.77%) is materially below this, confirming the model is conservative in GREEN assignment. The policy is defensible to credit policy reviewers without requiring SHAP explanation.

**Limitations of threshold design:**
- Thresholds derived from a single test-set evaluation (no temporal validation).
- GREEN band DR of 5.77% exceeds a typical prime-only portfolio benchmark — threshold should be reviewed against actual portfolio risk appetite.
- No reject inference correction — GREEN band DR is estimated only on applicants the prior system approved.
- KS-optimal single threshold (0.0961) maximises discrimination but was not selected — it would approve 50.7% of applicants at a 5.61% default rate, which is operationally impractical.
- Cost-optimal threshold (0.47) was computed under SCENARIO_ASSUMPTIONS_NOT_REAL_BANK_ECONOMICS (C_bad=10, C_reject=1, C_review=0.3).

### Cost-Sensitive Decisioning

Under scenario-assumed economics:
- Cost-optimal threshold: **t = 0.47**
- Expected loss at t=0.47: **EL = 0.0807** per applicant
- Default capture rates: conservative t=0.20 → 55%, balanced t=0.30 → 44%, aggressive t=0.47 → 33%

These economics are scenario assumptions, not real bank parameters. Any production threshold must be calibrated against actual loss-given-default, cost-of-funds, and regulatory capital requirements.

---

## 3. SHAP Reason-Code Layer (Section D/E)

### Global Feature Importance

EXT_SOURCE_MEAN is the dominant predictor (mean |SHAP| = 0.510), approximately 3.6× the contribution of the next feature (CREDIT_TO_ANNUITY = 0.141). The top-5 features are:

1. EXT_SOURCE_MEAN — External credit bureau composite score
2. CREDIT_TO_ANNUITY — Credit-to-repayment-capacity ratio
3. CREDIT_TO_GOODS — Loan-to-goods-value ratio
4. INST_LATE_RATIO — Historical late-payment ratio
5. EXT_SOURCE_1 — External credit assessment 1

**Stability:** All five features appear in the top-5 across 30/30 bootstrap resamples (500 samples each). EXT_SOURCE_MEAN is rank-1 in 30/30 bootstraps. The reason-code set is highly stable and suitable for adverse action memo drafting.

### Local Case Summary

| Case | Band | PD | Actual Default | Primary Driver | SHAP |
|---|---|---|---|---|---|
| GREEN_APPROVE | GREEN | 0.0335 | No | EXT_SOURCE_MEAN | −0.829 (risk-decreasing) |
| AMBER_REVIEW | AMBER | 0.2056 | No | EXT_SOURCE_MEAN | +0.939 (risk-increasing) |
| RED_HIGH_RISK | RED | 0.4164 | No | EXT_SOURCE_MEAN | +1.300 (risk-increasing) |
| AMBER_CONFLICT | AMBER | 0.3475 | No | EXT_SOURCE_MEAN | +1.232 (risk-increasing) |

Note: The AMBER_CONFLICT case demonstrates the governance value of manual review — a good applicant (no default) in the AMBER band whose model score is driven by external bureau data that may lag recent credit improvements.

### Adverse Action Draft Policy

Top risk-increasing SHAP features map to ECOA-style reason codes:
- EXT_SOURCE_MEAN → "External credit bureau composite score below threshold"
- INST_LATE_RATIO → "High proportion of late instalment payments"
- CREDIT_TO_ANNUITY → "Credit amount high relative to annual repayment capacity"
- CREDIT_TO_GOODS → "Loan-to-goods-value ratio elevated"

**Hard rule:** All adverse action language must be reviewed and signed by a licensed credit officer. SHAP-based drafts are ASSISTIVE_ONLY and are NOT legally compliant adverse action notices.

---

## 4. Fairness and Proxy Audit Skeleton (Section F)

**Scope:** Proxy-variable audit. Home Credit dataset contains no protected-class labels (race, sex, national origin). This section is a governance skeleton, not a fairness certification.

### Key Observations

| Proxy | Spread | Alignment |
|---|---|---|
| Age (under-30 vs 50+) | Approval rate 80.5% vs 95.5% | Aligned with DR differential (11.5% vs 5.6%) |
| Employment (employed vs sentinel) | Approval rate 88.3% vs 96.2% | Unexpected — sentinel (EMPLOYED_YEARS≥50) has lower DR (5.2%) due to HC encoding of non-employed as 365243 days |
| Income tercile (low vs high) | Approval rate 89.0% vs 91.3% | Narrow spread; model not strongly income-stratifying |
| Region (rating 1 vs 3) | Approval rate 96.5% vs 81.7% | Aligned with DR differential (4.9% vs 11.2%) |

All observed approval rate differentials are directionally consistent with actual default rate differentials. No evidence of model amplifying disparities beyond base rates.

**Limitations:** No disparate impact ratio computable without protected-class labels. Full fairness audit requires demographic enrichment, ECOA / fair-lending legal review, and independent validator review. This model is NOT certified as fair-lending compliant.

---

## 5. Drift and Vintage Stress (Section G)

### Score Distribution Stability

| Comparison | PSI | Interpretation |
|---|---|---|
| val vs test | 0.0002 | STABLE — operationally relevant comparison |
| train vs val/test | ~8.10 | Artefact — Platt calibrator fit on val, not train |

The train PSI is an expected calibration artefact, not a drift signal. All top-10 feature PSIs between train and test are below 0.001 (STABLE). The model's score distribution is consistent across val and test cohorts.

### Discriminative Power Consistency

| Split | AUC | KS |
|---|---|---|
| Validation | 0.7734 | 0.4121 |
| Test | 0.7769 | 0.4141 |

Generalization gap: AUC +0.0035 test vs val — no overfitting to val signal.

**Monitoring recommendation:** In any production deployment, monthly PSI on score distribution and top-10 features should be tracked against the val/test baseline (PSI<0.10 = stable, 0.10–0.25 = monitor, >0.25 = escalate to Model Risk Committee).

---

## 6. RAG / LLM Governance Demo (Section H)

A BM25 + LLM governance assistant was implemented with a 5-document policy corpus. Six cases were demonstrated:

| Case | Band | RAG Hit | LLM Action |
|---|---|---|---|
| GREEN_APPROVE | GREEN | POL-001 | Drafted approval memo; hard-stop check recommended |
| AMBER_REVIEW | AMBER | POL-001 | Drafted review memo with top-3 SHAP drivers |
| RED_DECLINE | RED | POL-002 | Drafted adverse action language with 3 reason codes |
| CONFLICT_OVERRIDE | AMBER | POL-004 | Surfaced override protocol; credit officer authority noted |
| ABSTAIN | N/A | BM25=0.0 | Abstained — out-of-domain query, no policy citation generated |
| DRIFT_ALERT | MONITOR | POL-003 | Generated MRC escalation memo |

**Design principles enforced:**
- LLM never approves or rejects an applicant in any case.
- Abstain fires when BM25 top-score < 0.25 — prevents hallucinated policy citations.
- All outputs tagged ASSISTIVE_ONLY + HUMAN_REVIEW_REQUIRED + NOT_FINAL_DECISION.
- No applicant data sent to external API — demo operates on anonymised case summaries.

---

## 7. Pass 3 Evidence Inventory

| Evidence File | Content |
|---|---|
| `gold_pass3_threshold_scoreband_report.json` | GREEN/AMBER/RED band counts, default rates, rationale |
| `gold_pass3_cost_sensitive_decisioning.json` | 3-scenario cost tradeoffs, cost-optimal threshold |
| `gold_pass3_shap_reason_code_report.json` | Global top-20 SHAP + 4 local case reason codes |
| `gold_pass3_reason_code_stability.json` | 30-bootstrap stability: top-5 features at 30/30 |
| `gold_pass3_fairness_proxy_audit.json` | Age, income, employment, region proxy audit |
| `gold_pass3_drift_vintage_stress.json` | PSI, KS, AUC, ECE by split; top-10 feature PSI |
| `gold_pass3_rag_llm_demo_report.json` | 6-case RAG/LLM governance demo |
| `docs/PULSEGUARD_MODEL_CARD.md` | Model card (this pass) |
| `docs/PULSEGUARD_GOLD_PASS3_GOVERNANCE_REPORT.md` | This document |

---

## 8. Pass 3 Acceptance Verdict

| Criterion | Status | Notes |
|---|---|---|
| Score-band policy derived and documented | ✓ ACCEPT | GREEN<0.20, AMBER 0.20–0.40, RED≥0.40; DR semantics justified |
| Cost-sensitive decisioning | ✓ ACCEPT | Scenario economics, 3 tradeoffs, cost-optimal t=0.47 |
| SHAP reason-code report | ✓ ACCEPT | 4 local cases, 20 global features, all ASSISTIVE_ONLY |
| Reason-code stability | ✓ ACCEPT | Top-5 stable 30/30 bootstraps; EXT_SOURCE_MEAN rank-1 in 30/30 |
| Fairness audit | ✓ ACCEPT (SKELETON) | Proxy audit only; no protected-class labels; not a fairness certification |
| Drift/vintage stress | ✓ ACCEPT | Val-vs-test PSI=0.0002; all top-10 feature PSIs STABLE |
| RAG/LLM governance demo | ✓ ACCEPT | 6 cases; abstain fires; LLM never approves/rejects |
| Model card | ✓ ACCEPT | All required fields; limitations and forbidden claims documented |
| Hard rules preserved | ✓ ACCEPT | No model retuning, no test-set leakage, no production claims |
| Control docs updated | PENDING → Task 12 | 00_CONTROL_TOWER, 04_EVIDENCE_LEDGER, 06_CLAIM_BOUNDARY, G9A examples |

**Overall Pass 3 verdict: ACCEPT — `safe_to_pass4=true`**

---

## 9. What Pass 4 Will Address

- Final architecture documentation and portfolio writeup
- Executive summary for non-technical audience
- README consolidation and repo cleanup
- Optional: Gold Pass 4 stress tests (stress-test scenarios, sensitivity analysis)

---

## 10. Strongest Defensible Claim After Pass 3

> "I built a credit-risk ML governance stack on Home Credit Default Risk: a tuned LightGBM champion with monotone constraints, calibrated PD scores, score-band policy (GREEN/AMBER/RED), SHAP reason codes bootstrapped for stability, a fairness proxy audit skeleton, PSI drift baseline, and a BM25 RAG + LLM governance assistant that drafts adverse action memos for credit officer review — all under ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED governance constraints, with a model card and evidence ledger traceable to every claim."

---

*PulseGuard — Gold Pass 3 Governance Report | 2026-06-17 | PORTFOLIO PROJECT — NOT FOR PRODUCTION*
