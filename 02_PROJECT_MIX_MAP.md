# 02 — PROJECT MIX MAP
## PulseGuard · Source Project Consolidation

---

### Consolidation Table

| Source Project | Useful Assets | Weak / Redundant Assets | How It Maps into PulseGuard | Final Role |
|---------------|--------------|------------------------|----------------------------|------------|
| **riskframe_platform** | Champion/challenger framework (5-gate); Platt calibration + ECE; Optuna HPO with ECE regression case; PSI drift alerting (183 features); KS per-feature stats; Fairness audit (Disparate Impact, Equal Opportunity); Decision policy engine (APPROVE/REVIEW/REJECT) with version log; 30-day operational lifecycle; FastAPI serving with parity check; 22/22 tests; Delayed label validation | Standalone repo framing; Home Credit dataset pipeline (reusable, not unique) | **Core engine** — provides champion training, calibration, drift, fairness, policy, and lifecycle; all other projects plug into or extend this | Primary platform backbone |
| **featureleakagelens** | 7 leakage checks (2 tiers: WARN vs FAIL); Temporal availability FAIL check; Training future date scan FAIL check; `LeakageAuditConfig` API; Structured JSON/Markdown/HTML output; 23 tests; PyPI-published library | Standalone auditor framing (easily absorbed); Roadmap items (mutual information, group leakage) are deferred | **Pre-training gate** — runs before any model training; output attached to model card; FAIL blocks training | Gate G3 — Leakage detection kernel |
| **lendflow** | Deterministic-first design (FOIR recomputed from raw, hard rules no LLM); APPROVE/REFER/REJECT routing with explicit escalation conditions; Hybrid RAG over credit policy corpus (BM25 + ChromaDB + cross-encoder reranker); RAGAS faithfulness evaluation (0.91); PII redaction (Presidio); Tamper-evident JSONL audit trail; 7-node pipeline architecture; 95% routing accuracy on synthetic NBFC data | LangGraph agentic framing (absorbed, not the focus); NBFC/vehicle loan domain specifics (narrowed to credit decision principle); Raw LLM synthesis (not needed for deterministic components) | **Credit decision workflow** — FOIR engine and hard-rule gate become PulseGuard's underwriting decision simulation; hybrid RAG becomes policy lookup for governance decision support | Gate G7 — Credit/fraud decision simulation; Policy lookup layer |
| **nexussupply** | Multi-signal composite risk scoring formula (weighted fusion with documented weights); Altman Z-score 3-variant selection logic; XGBoost distillation from rule-based scores; Graph contagion propagation math (2-hop BFS with decay) | Supplier/procurement domain framing (not core to bank/fintech risk); FinBERT news sentiment (deferred — not in G1–G7 scope); ESG parsing (deferred); LangGraph 7-node pipeline (already have better version from LendFlow); Synthetic supplier dataset (separate domain) | **Optional third-party risk layer** — if counterparty/vendor risk is added to PulseGuard, the composite fusion formula and contagion math are reused; Altman Z logic reusable for borrower financial health scoring | **Selective absorb** — composite scoring formula and Altman Z variant selection are documented in PulseGuard's risk signal layer; full NexusSupply pipeline is deferred |

---

### Component Mapping: What Goes Where in PulseGuard

```
PulseGuard Module                    ← Source
─────────────────────────────────────────────────────────────
01. Feature Leakage Gate             ← FeatureLeakageLens (full)
02. Champion Training + HPO          ← RiskFrame (full)
03. Calibration Check                ← RiskFrame (full)
04. PSI Drift Monitor                ← RiskFrame (full)
05. Per-Feature KS Stats             ← RiskFrame (full)
06. Fairness Audit                   ← RiskFrame (full)
07. Decision Policy Engine           ← RiskFrame (full)
08. Champion/Challenger 5-Gate       ← RiskFrame (full)
09. FOIR Recomputation Engine        ← LendFlow (extracted)
10. Hard Rule Enforcement Gate       ← LendFlow (extracted)
11. Credit Policy RAG Lookup         ← LendFlow (extracted)
12. Escalation Logic                 ← LendFlow (extracted)
13. Audit Trail (JSONL)              ← LendFlow (pattern)
14. Governance Evidence Ledger       ← New (PulseGuard original)
15. Multi-Signal Risk Fusion         ← NexusSupply (formula only, deferred)
16. Altman Z Financial Health        ← NexusSupply (deferred)
17. Graph Contagion Risk             ← NexusSupply (deferred)
```

---

### Redundancy Resolution

| Conflict | Resolution |
|---------|-----------|
| RiskFrame and LendFlow both have audit trails | Use LendFlow's JSONL tamper-evident pattern as the standard; RiskFrame's `batch_scoring_runs.csv` becomes the drift/ops log |
| RiskFrame and LendFlow both have decision outputs | RiskFrame's APPROVE/REVIEW/REJECT = model-scored decision; LendFlow's APPROVE/REFER/REJECT = policy-enforced decision; they are different layers — both kept |
| NexusSupply XGBoost and RiskFrame XGBoost overlap | Different targets (supplier distress vs. credit default); RiskFrame model is the champion; NexusSupply financial scoring is deferred |
| LendFlow LangGraph pipeline vs. PulseGuard sequential modules | LangGraph framing is dropped; PulseGuard uses sequential Python modules; escalation state machine is preserved as decision logic only |

---

### What Is Not Absorbed

| Project | What Is Excluded | Reason |
|---------|-----------------|--------|
| NexusSupply | FinBERT news sentiment; ESG parsing; full supplier pipeline; LangGraph wiring | Out of scope for credit/fraud risk focus; deferred |
| LendFlow | LangGraph node graph; Presidio PII redaction (unless fraud use case added) | Architecture abstracted away; PII not needed for synthetic data pipeline |
| RiskFrame | Standalone repo identity | Absorbed fully; not referenced separately in interview |
| FeatureLeakageLens | Roadmap (mutual information, group leakage, walk-forward validator) | Deferred to G9+ |

---

### NexusSupply Decision: Selective Absorb, Not Forced

NexusSupply strengthens PulseGuard in one specific way: **the composite multi-signal fusion pattern**. When PulseGuard needs to score a borrower or counterparty using multiple independent signals (credit score, FOIR, bureau data, payment history), the NexusSupply formula is the right template.

It does **not** strengthen PulseGuard's core model-governance story. The supplier domain, FinBERT, ESG, and LangGraph components add complexity without adding interview depth for a risk DS or ML governance role.

Decision: absorb the fusion formula pattern into PulseGuard's risk signal layer design document; defer full NexusSupply integration to G9 (Deep Defense Kernel) only if the project reaches that gate.
