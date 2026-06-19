# G0 — GOLD ALIGNMENT AUDIT
## PulseGuard · 15-Axis Rubric Scoring

**Scoring date:** Pre-G1 (base control docs only, no code, no artifacts)
**Evaluator stance:** Staff-level risk DS interviewer / model risk committee

---

## SCORING LEGEND

| Score | Meaning |
|-------|---------|
| 9-10 | Gold-standard; nothing to add |
| 7-8 | Strong; minor gaps |
| 5-6 | Adequate foundation; material gaps |
| 3-4 | Weak; needs significant work |
| 1-2 | Missing or fundamentally wrong |

---

## AXIS 1: PRODUCT THESIS

**Score: 7/10**

**Current evidence:**
The control tower has a clear one-line identity and a flagship question: "Can a bank, fintech, risk, or ML governance team decide whether a model is safe to use...?" The PRD has a 7-stage decision workflow and five governance decisions (APPROVE/MONITOR/CHALLENGE/REJECT/ESCALATE).

**Gap:**
The product thesis does not yet lead with the governance angle — the SR 26-2 alignment. The current framing positions PulseGuard as a "risk decision and model-governance platform" but does not explicitly connect it to the real regulatory context that makes this problem important NOW (SR 26-2 rescinded SR 11-7 in April 2026). The negative-cost chain in the PRD is good but undersells the regulatory failure mode.

**Required next build action:**
Update `01_BEASTMAX_PRD.md`: lead with SR 26-2 framing; add regulatory failure mode (audit fails, model cannot be deployed, remediation takes months); sharpen product thesis to "the evidence-generation layer for SR 26-2 model lifecycle governance."

---

## AXIS 2: BUYER / JD ALIGNMENT

**Score: 6/10**

**Current evidence:**
The role table in `00_CONTROL_TOWER.md` lists: Risk DS, Fraud DS, Credit DS, ML Governance, Decision Scientist. The PRD identifies buyer as "risk DS or ML governance lead who must defend a model in a model risk committee."

**Gap:**
The JD alignment is at a surface level. The specific vocabulary that appears in FAANG/fintech JDs (fraud score calibration, label bias correction, case disposition logic, full model lifecycle ownership) is not reflected in the control docs. The target JD archetypes are correct but the calibration of what those roles actually expect is shallow.

**Required next build action:**
Update `00_CONTROL_TOWER.md`: add a JD keyword mapping table drawn from G0_MARKET_JD_AND_COMPANY_STANDARDS.md. Each key JD term should map to a PulseGuard module.

---

## AXIS 3: INDUSTRY REALISM

**Score: 7/10** *(updated from 5/10 after GitHub/blog research — see G0_GITHUB_BLOG_RESEARCH.md)*

**Current evidence:**
After G0 + blog research: SR 26-2 added to all relevant control docs; reject inference documented as a named boundary condition; ECOA Regulation B adverse action codes added to G7; PSI multivariate blindspot formally documented; Nubank and Stripe engineering blog validation of monitoring design patterns; DataRobot champion/challenger validation for banks specifically; SAIL reject inference paper (2025) as a concrete G9 reference.

**Industry citations now backing the design:**
- **Nubank Engineering Blog (2024):** "Policy/Decision Layer monitoring" directly validates PulseGuard's approval rate decomposition. Percentile monitoring validates G4 drift design.
- **Stripe (Jan 2025):** Slice monitoring at 16,000 dimensions confirms that aggregate PSI misses segment drift — validates PulseGuard's PSI blindspot documentation.
- **DataRobot:** Champion/challenger is a first-class MRM requirement at banks specifically.
- **SAIL (Annals of Operations Research, 2025):** Graph-based reject inference confirms documented G9 path.

**Remaining gap (why not 9/10):**
No company-specific engineer said "I built the equivalent of PulseGuard" — the validation is of individual components, not the integrated lifecycle. Industry realism is confirmed component-by-component; the integrated platform narrative is PulseGuard-original.

**Required next build action:**
Axis 3 score will reach 9/10 when artifacts are built and cited alongside the industry patterns they implement.

---

## AXIS 4: DATA REALISM

**Score: 6/10**

**Current evidence:**
Control docs correctly state: Home Credit Default Risk (public Kaggle), synthetic lifecycle events, synthetic review decisions. Honest positioning.

**Gap:**
The temporal leakage problem (Home Credit has no feature timestamps, so the FeatureLeakageLens temporal checks cannot fire natively) is not addressed. The selection bias problem (model trained on approved applicants only) is not mentioned anywhere in the current control docs. Synthetic timestamp extension is not planned.

**Required next build action:**
Add to `03_BUILD_GATES.md` G3: "Add synthetic timestamps to Home Credit features to demonstrate temporal FAIL path." Add reject inference to model card section in G8.

---

## AXIS 5: METHOD DEPTH

**Score: 7/10**

**Current evidence:**
The technique list in the original control docs covers: XGBoost, LightGBM, Optuna, Platt calibration, PSI, KS, DI, EOpp, SHAP, FOIR, policy versioning. This is a solid method set.

**Gap:**
Methods are listed but not evaluated against each other. No technique tournament existed before G0. Platt vs. isotonic regression tradeoff is not discussed. PSI multivariate blindspot is not acknowledged. Reject inference methods are not listed. The DeLong test for AUC comparison is mentioned but the p-value interpretation is not discussed.

**Required next build action:**
`G0_TECHNIQUE_TOURNAMENT.md` has been created. Reference it from `03_BUILD_GATES.md` as the technique rationale document.

---

## AXIS 6: TECHNIQUE TOURNAMENT QUALITY

**Score: 8/10** (after G0 document creation)

**Current evidence:**
`G0_TECHNIQUE_TOURNAMENT.md` covers 14 techniques, each with: problem solved, assumptions, why it belongs, failure modes, alternatives, business tradeoff, evidence to prove/kill, and build/defer/reject decision.

**Gap:**
Reject inference deserves a deeper treatment. Calibration by group (fairness depth) needs its own tournament entry. The Wasserstein distance vs PSI tradeoff needs more business consequence framing.

**Required next build action:**
Expand technique tournament at G9 to add reject inference variants; calibration by group; Wasserstein distance treatment.

---

## AXIS 7: EVIDENCE QUALITY

**Score: 3/10** (pre-build — nothing exists yet)

**Current evidence:**
`04_EVIDENCE_LEDGER.md` has 15 rows, all DEFERRED. No artifacts exist. The ledger is correctly structured but completely empty.

**Gap:**
Everything. No artifacts. No computed metrics. No plots. This is the biggest gap — and it is expected at this stage. But the gap is very real.

**Required next build action:**
This is what G3–G8 are for. Every gate closes one set of evidence rows. Highest priority: leakage_report.json (G3), calibration_report.json (G4), drift_report.json (G4), challenger_promotion_decision.json (G6), governance_signoff.md (G8).

---

## AXIS 8: EVALUATION QUALITY

**Score: 5/10**

**Current evidence:**
The PRD lists evaluation gates: PR AUC, ROC AUC, ECE, DI, EOpp gap, PSI, DeLong test p-value. These are the right metrics.

**Gap:**
No evaluation framework is written yet. The champion/challenger 5-gate promotion framework exists conceptually but the formal gate definition (what threshold? what reference dataset? what comparison window?) is not specified in code or schema. The DeLong test implementation is not specified. Delayed label validation framework is described but not designed in detail.

**Required next build action:**
At G6: write `scripts/champion_challenger_compare.py` with formal gate thresholds specified as constants, not magic numbers. Document DeLong test from scipy.stats. At G8: write delayed label validation framework.

---

## AXIS 9: BUSINESS CONSEQUENCE CHAIN

**Score: 6/10**

**Current evidence:**
The PRD has a "Negative-Cost Chain" section that maps failure modes to business consequences. The `06_CLAIM_BOUNDARY.md` has an implicit cost chain in the "Safe Interview Line" column.

**Gap:**
The cost chain is at the feature level ("if drift is not caught, approval rates miscalibrate") but not at the dollar level. "Miscalibrated approval rates" → how many extra approvals? → at what threshold default rate? → what is the estimated credit loss? A senior DS at a lending company thinks in dollar terms. The model evaluation reports should include: "if PSI ALERT is not acted on, estimated exposure to out-of-distribution scoring is N applications/day at expected bad rate X% above the model's predicted rate."

**Required next build action:**
Add a cost consequence column to the evidence ledger. At G7, compute the policy simulation with dollar consequence estimates on synthetic applications.

---

## AXIS 10: FAILURE-MODE COVERAGE

**Score: 6/10**

**Current evidence:**
The PRD lists 6 failure modes. The control tower lists forbidden claims. `06_CLAIM_BOUNDARY.md` is rigorous.

**Gap:**
The following failure modes from the research are NOT covered:
- Selection bias (reject inference failure mode)
- PSI multivariate blindspot (PSI stable, model degrading)
- Proxy bias via correlated feature (gender excluded, zip code included)
- Policy-model version conflation (approval rate change attributed to wrong cause)
- Calibration at the decision boundary vs. globally (ECE is global; threshold calibration needs local check)

**Required next build action:**
Add these failure modes to `01_BEASTMAX_PRD.md` Failure Modes section. Add PSI multivariate blindspot to monitoring design note in G4.

---

## AXIS 11: OPERATIONAL REALISM

**Score: 5/10**

**Current evidence:**
The 30-day lifecycle simulation plan is realistic. Day 4 malformed batch, Day 7 WARN, Day 12 policy change, Day 14 ALERT, Day 25 challenger comparison, Day 30 delayed labels — this is a credible operational simulation.

**Gap:**
No retraining trigger is defined. What causes a retraining? PSI ALERT sustained for how many batches? Model performance below what threshold? No decommissioning plan. No mention of data freshness requirements (how stale can training data be?). No mention of model versioning beyond v1.0/v1.1.

**Required next build action:**
Add retraining trigger and decommissioning plan to G8 model card. These are SR 26-2 requirements.

---

## AXIS 12: CLAIM SAFETY

**Score: 9/10**

**Current evidence:**
`06_CLAIM_BOUNDARY.md` is thorough and rigorous. Four-tier separation (resume/LinkedIn/interview/forbidden). Clear forbidden claims. All claims tagged DEFERRED until artifacts exist.

**Gap:**
Minor: the DeLong test p-value claim ("DeLong p ~0.07") needs to be clearly framed as "not statistically significant, hence champion retained" — not just stated as a number. The NexusSupply evaluation claim (CV AUC 1.00) is correctly identified as problematic and excluded.

**Required next build action:**
Minor wording update to DeLong test claim when it is moved from DEFERRED to BUILT status.

---

## AXIS 13: INTERVIEW DEFENSIBILITY

**Score: 4/10** (no defense document exists yet)

**Current evidence:**
`06_CLAIM_BOUNDARY.md` has interview-safe claims and a few Q&A pairs. The control docs reference an "Interview Defense" document in G9.

**Gap:**
No interview defense document exists. The 30+ Q&A document is critical and entirely absent. The "safe interview line" column in the evidence ledger is a good start but insufficient.

**Required next build action:**
G9 is the interview defense gate. But at G8, every evidence artifact should have a defensible claim line. The `G0_MARKET_JD_AND_COMPANY_STANDARDS.md` has 7 interview Q&A pairs — these should become the seed of the defense document.

---

## AXIS 14: DIFFERENTIATION / MEMORABILITY

**Score: 7/10**

**Current evidence:**
The project has clear differentiators: (1) ECE regression case (model that was HELD), (2) policy version log (rare), (3) leakage audit as pre-training gate, (4) 5-gate promotion framework.

**Gap:**
The project is not yet memorable as a story. "I built a credit risk platform" is forgotten immediately. "I built the only portfolio project I've seen that held a model with BETTER AUC because calibration regressed — and I can explain exactly why calibration matters more than AUC for a threshold-based decision system" is memorable.

The reject inference documentation, when added, will be the second most memorable element: "I'm the only candidate in this interview process who acknowledged that this model has never seen a rejected applicant."

**Required next build action:**
Sharpen the interview story (done in `G0_REVISED_BEASTMAX_PROPOSAL.md`). Ensure the ECE regression case and reject inference limitation are both surfaced prominently in the model card and governance sign-off.

---

## AXIS 15: BUILD FEASIBILITY

**Score: 8/10**

**Current evidence:**
The build plan (G1–G10) is realistic. The minimum build path (G3–G8, ~3 weeks) is achievable. The source projects provide most of the code to port. The datasets are public. Dependencies are standard (scikit-learn, xgboost, lightgbm, shap, optuna, scipy).

**Gap:**
Two risks:
1. The temporal leakage demonstration requires synthetic timestamp engineering for Home Credit — not blocking but adds 1-2 hours of extra work at G3.
2. The delayed label validation requires a careful synthetic label generation process — easy to get wrong (circular if labels are derived from scores).

**Required next build action:**
At G3: plan the synthetic timestamp extension before coding begins. At G8: design delayed label validation as a separate synthetic process, NOT derived from model scores.

---

## RUBRIC SUMMARY

| Axis | Score | Priority Gap |
|------|-------|-------------|
| 1. Product thesis | 7/10 | Add SR 26-2 framing to PRD |
| 2. Buyer/JD alignment | 6/10 | Add JD keyword mapping to control tower |
| 3. Industry realism | 7/10 | Nubank/Stripe/DataRobot citations; SR 26-2; reject inference documented (was 5/10) |
| 4. Data realism | 6/10 | Synthetic timestamps, selection bias documentation |
| 5. Method depth | 7/10 | Technique tournament now complete |
| 6. Technique tournament | 8/10 | Minor: reject inference, calibration by group |
| 7. Evidence quality | 3/10 | Nothing exists — G3–G8 are the answer |
| 8. Evaluation quality | 5/10 | Formal gate thresholds, DeLong implementation |
| 9. Business consequence chain | 6/10 | Dollar-level cost estimates at G7 |
| 10. Failure mode coverage | 6/10 | Selection bias, multivariate drift, proxy bias |
| 11. Operational realism | 5/10 | Retraining triggers, decommissioning plan |
| 12. Claim safety | 9/10 | Strong — minor wording improvements |
| 13. Interview defensibility | 4/10 | Defense document missing — G9 priority |
| 14. Differentiation | 7/10 | Sharpen story; add reject inference moment |
| 15. Build feasibility | 8/10 | Minor risks: timestamps, delayed labels |

**Current average: 6.4/10** *(Axis 3 updated from 5→7 after GitHub/blog research; 15-axis sum = 96, avg = 6.4)*

**Target after G1–G8: 8.0/10**

**Target after G9–G10 (Gold): 9.0/10**

---

## TOP 5 PRIORITY GAPS (ordered by impact)

1. **Evidence quality (Axis 7):** Nothing is built. G3–G8 must execute. No amount of documentation compensates for absent artifacts.
2. **Industry realism (Axis 3):** Score raised from 5→7 after blog/GitHub research (Nubank monitoring patterns, Stripe slice monitoring, DataRobot champion/challenger for banks). SR 26-2, reject inference, and ECOA are now documented. Remaining gap: artifacts need to exist for this to reach 9/10.
3. **Interview defensibility (Axis 13):** The 30+ Q&A defense document does not exist. This must be written at G9.
4. **Operational realism (Axis 11):** Retraining triggers and decommissioning plans are missing. Required for SR 26-2 alignment and for any MRM interview.
5. **Business consequence chain (Axis 9):** The cost chain stays at the qualitative level. Adding estimated dollar consequences (even synthetic) for the drift scenario would make the project significantly more memorable.
