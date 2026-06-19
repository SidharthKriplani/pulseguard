# G0 — NEXT BUILD DECISION
## PulseGuard · What Happens After G0

---

## 1. G0 VERDICT

**G0 is complete. The project is ready for BeastMax execution with the following conditions:**

- The foundation is solid (7 control docs, correct architecture, honest positioning)
- Five existing control docs need targeted updates before G1 begins (listed below)
- The source projects are correctly assessed: RiskFrame is the backbone, FLL is the pre-training gate, LendFlow contributes FOIR + hard rules, NexusSupply is formula-only
- The technique tournament is written and settled: 14 techniques built, 4 deferred, 2 rejected
- The claim boundary is rigorous and remains the strongest axis
- The project is NOT gold-complete; evidence quality (Axis 7) is 3/10 — everything waits on G3–G8

---

## 2. REQUIRED UPDATES TO EXISTING CONTROL DOCS BEFORE G1

These are not rewrites. These are targeted additions based on G0 findings.

### `00_CONTROL_TOWER.md` — 3 additions required
1. Add JD keyword mapping table (from G0_MARKET_JD_AND_COMPANY_STANDARDS.md)
2. Update current status: "G0 complete. SR 26-2 aligned. Reject inference documented as boundary condition."
3. Add: "Regulatory reference: SR 26-2 (April 2026) — replaces SR 11-7"

### `01_BEASTMAX_PRD.md` — 4 additions required
1. Add SR 26-2 as the regulatory context in the Business Pain section
2. Add reject inference as Failure Mode #7
3. Add PSI multivariate blindspot as Failure Mode #8
4. Add retraining trigger and decommissioning plan to the Model Risk Lifecycle section

### `02_PROJECT_MIX_MAP.md` — 1 addition required
1. Clarify NexusSupply evaluation gap: CV AUC 1.00 on synthetic data with circular labels is NOT a real evaluation — do not carry this claim.

### `03_BUILD_GATES.md` — 3 additions required
1. G3: Add "synthetic timestamp extension for temporal checks to fire on Home Credit"
2. G7: Add "adverse action code awareness — ECOA Regulation B compliant reject reason codes"
3. G8: Add "retraining trigger definition and decommissioning plan to model card"

### `04_EVIDENCE_LEDGER.md` — 1 addition required
1. Add cost consequence column (qualitative dollar impact estimate for each claim)

### `06_CLAIM_BOUNDARY.md` — 2 additions required
1. Add reject inference to deferred claims with specific framing: "Known boundary — selection bias not corrected; documented in model card"
2. Add SR 26-2 alignment as an interview-safe claim: "Governance artifacts are designed to be SR 26-2 aligned; not claiming regulatory certification"

---

## 3. G1 EXECUTION PLAN (IMMEDIATE NEXT STEP)

**G1 — Repo Audit and Artifact Inventory**

G1 is now more focused after G0. The audit is not just "classify every file" — it is specifically designed to answer: what can we import/reuse directly from FeatureLeakageLens and RiskFrame, and what needs to be rebuilt?

**G1 specific deliverables (updated after G0):**

1. `docs/G1_repo_audit.md` — full inventory with:
   - FeatureLeakageLens: which modules to `pip install` vs. which to inspect source
   - RiskFrame: which scripts to port, which to adapt, which to rebuild
   - LendFlow: which functions to extract (FOIR engine, policy gate, decision router, audit logger)
   - NexusSupply: composite formula pattern documented as reference; no code ported

2. `docs/G1_dataset_plan.md`:
   - Confirm Home Credit Default Risk availability in workspace
   - If not available: generate synthetic dataset with same column schema and statistical properties (8% default rate, key features: EXT_SOURCE_2, AMT_CREDIT, AMT_INCOME_TOTAL, DAYS_BIRTH, DAYS_EMPLOYED, CODE_GENDER)
   - Plan for synthetic timestamp extension (which features get timestamps; what the timestamp represents)
   - Plan for synthetic lifecycle events (malformed batch, drift injection, policy change, delayed labels)

3. `scripts/verify_imports.py`:
   - Test: `import featureleakagelens`, `import xgboost`, `import lightgbm`, `import shap`, `import optuna`, `import scipy.stats`, `import sklearn`
   - Test: `from scipy.stats import ks_2samp` (for KS test)
   - Test: PSI computation on a tiny synthetic example (2 distributions, 10 bins → expected PSI value)

4. First evidence ledger entry:
   - Claim: "Repo audit complete"
   - Artifact: `docs/G1_repo_audit.md`
   - Confidence: HIGH (deterministic — either done or not)

---

## 4. CRITICAL SEQUENCING DECISIONS

### Decision 1: Home Credit dataset or synthetic?

**If Home Credit CSV files are present in the workspace:**
Use them. They are public and the project is documented as using this dataset. Home Credit is the strongest choice — 307,511 rows, 122 features, 8% default rate, well-documented column semantics.

**If Home Credit CSV files are not present:**
Generate a synthetic dataset with:
- 50,000 rows (enough for meaningful train/val/test split)
- 80 features (subset of Home Credit column schema)
- 8% default rate (controlled via class weight)
- Key features: EXT_SOURCE_2, EXT_SOURCE_3, AMT_CREDIT, AMT_INCOME_TOTAL, DAYS_BIRTH, DAYS_EMPLOYED, CODE_GENDER, NAME_INCOME_TYPE
- Label in metadata as "synthetic dataset, Home Credit schema, statistical properties preserved"

Do NOT claim Home Credit dataset if synthetic data is used.

### Decision 2: LangGraph or not?

**Decision: NOT.** LangGraph is dropped entirely from PulseGuard. The credit decision pipeline is implemented as sequential Python modules (`src/foir_engine.py`, `src/policy_gate.py`, `src/decision_router.py`). This is simpler, more transparent, more governance-friendly, and easier to test.

### Decision 3: RAG for policy lookup — when?

**Decision: DEFERRED to G7+ (Gold only).** MVP uses hardcoded FOIR thresholds and policy rules. The hardcoded rules are sufficient for the governance story. RAG adds value at Gold level — it makes policy citations retrievable rather than hardcoded. Build RAG only if G3–G7 are complete and time permits.

### Decision 4: FastAPI serving — when?

**Decision: G9.** MVP (G3–G8) focuses on the evidence artifacts and governance documents. FastAPI serving is important for the production-pattern story but is not required for the governance sign-off. Build at G9 when the core pipeline is stable.

---

## 5. RISK TABLE

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Home Credit dataset not in workspace | Medium | Low | Generate synthetic equivalent; clearly labeled |
| Temporal leakage checks don't fire on Home Credit | High | Medium | Add synthetic timestamps at G3; demonstrate FAIL path |
| ECE regression case doesn't reproduce | Low | High | RiskFrame has computed this — port carefully; if different, document new result |
| Delayed label validation is circular (labels derived from scores) | Medium | High | Design delayed labels independently of model scores at G8 |
| Interview defense (G9) not written in time | Medium | High | Write the 7 Q&A pairs from G0_MARKET_JD docs as a seed; expand incrementally |
| NexusSupply AUC 1.00 claim accidentally carried forward | Low | High | Check every artifact for NexusSupply evaluation claims; exclude all |

---

## 6. SUMMARY RECOMMENDATION

**Execute G1 immediately. The project is ready.**

Do not wait for more planning. The 8 G0 documents and the 7 control docs contain everything needed to build with confidence. The three most important decisions are already made:
1. RiskFrame is the backbone; port and refactor
2. LangGraph is dropped; sequential Python modules only
3. Evidence quality (Axis 7) is the most critical gap; G3–G8 close it

The project needs code, not more documentation.

**The first three things to build (in order):**
1. `scripts/verify_imports.py` — environment validation (30 minutes)
2. `scripts/leakage_audit.py` — FeatureLeakageLens on Home Credit (2 hours)
3. `scripts/train_champion.py` — XGBoost + Platt + ECE computation (4 hours)

After these three, the project has its first 3 evidence artifacts and the foundation is real.
