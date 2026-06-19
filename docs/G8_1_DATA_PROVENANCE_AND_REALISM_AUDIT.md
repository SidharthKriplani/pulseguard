# G8.1 — Data Provenance and Dataset Realism Audit
## PulseGuard · Taiwan Default Credit Decision Model

**Gate:** G8.1 — Data Provenance Audit (BLOCKING gate before G9)
**Status:** PASS — 20/20 checks, provenance_status = "PASS"
**Date:** June 2026
**Audit script:** `scripts/run_g8_1_data_provenance_audit.py`
**Audit JSON:** `outputs/evidence/g8_1_data_provenance_audit.json`

---

> **Purpose of this document:** Answer definitively where the dataset came from, whether it is
> authentic, and whether the "real public data" claim is evidence-clean before G9 opens.
> G9 is BLOCKED until this gate passes.

---

## 1. Primary Provenance Question: Where Did the Dataset Come From?

**Answer (explicit, as required by G8.1 gate):**

> *"Where did the dataset come from if the user did not manually provide it?"*

The file `data/public/taiwan_credit_default.xls` was **downloaded programmatically by a prior
Claude agent session during the G5.5 gate** (session timestamp: 2026-06-16 21:25:21 UTC).
That session fetched the file from the UCI ML Repository at:

```
https://archive.ics.uci.edu/ml/machine-learning-databases/00350/
    default%20of%20credit%20card%20clients.xls
```

**The user did not manually provide this file.** It was fetched by the agent and placed into
`data/public/taiwan_credit_default.xls` during the G5.5 gate session. No `wget`, `curl`, or
Python download script was retained in `scripts/` at the time.

**Evidence chain for this claim:**
- File `mtime` = `2026-06-16T21:25:21Z` — timestamps align with the G5.5 session
- Source URL is documented in `scripts/g6_taiwan_adapter.py` output JSON field
- G8.1 re-downloaded the file from that exact URL and obtained identical SHA256 (see §3)
- No download script exists in `scripts/` — confirmed by `ls scripts/` during G8.1 forensics

---

## 2. How It Was Downloaded / Loaded

**Download:** Fetched programmatically by the prior Claude agent session via HTTP GET from the
UCI ML Repository direct XLS URL. No download script was retained.

**Load in all G6/G7 work:**
```python
df = pd.read_excel("data/public/taiwan_credit_default.xls", header=1, engine="xlrd")
df.columns = [c.strip() for c in df.columns]
```
- `header=1` skips the title row ("I-Cheng Yeh, ...") and uses row 2 as column names
- `engine="xlrd"` required for `.xls` (pre-OOXML Excel) format
- Strip applied to column names only — no data values modified

**No rows are added or removed before the train/val/test split.** The XLS is loaded verbatim.

---

## 3. Authenticity Verification (SHA256)

G8.1 ran a live re-download from the UCI URL and computed SHA256 of both the workspace copy
and the fresh download:

| File | SHA256 | Match |
|------|--------|-------|
| `data/public/taiwan_credit_default.xls` (workspace) | `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` | — |
| Fresh UCI download (G8.1 verification) | `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` | **EXACT MATCH** |

**Interpretation:** The workspace copy is byte-for-byte identical to the current UCI ML Repository
file. There is no tampering, no synthetic injection, no version drift.

**File metadata:**

| Field | Value |
|-------|-------|
| Path | `data/public/taiwan_credit_default.xls` |
| Size | 5,539,328 bytes (5.3 MB) |
| Modified (UTC) | 2026-06-16T21:25:21Z |
| Accessed (UTC) | 2026-06-16T21:25:32Z |

---

## 4. Full Check Results (20/20 PASS)

| # | Check | Result |
|---|-------|--------|
| 1 | File exists at expected path | PASS |
| 2 | File size = 5,539,328 bytes | PASS |
| 3 | SHA256 matches UCI reference | PASS |
| 4 | Metadata recorded (informational) | — |
| 5a | Row count = 30,000 | PASS |
| 5b | Column count = 25 | PASS |
| 5c | Column names match expected 25-col schema | PASS |
| 5d | Target column present | PASS |
| 6a | No missing values | PASS |
| 6b | No duplicate rows | PASS |
| 7a | Default rate = 0.2212 ± 0.0001 | PASS |
| 7b | Target class counts {0:23364, 1:6636} | PASS |
| 8a | ID column sequential 1..30000 | PASS |
| 8b | ID all unique | PASS |
| 9a | LIMIT_BAL mean = 167,484.32 (vs Yeh & Lien 2009) | PASS |
| 9b | AGE range [21, 79] | PASS |
| 10a | IDs within natural range (no synthetic IDs) | PASS |
| 10b | SEX encoding {1, 2} only | PASS |
| 10c | EDUCATION encoding in {0–6} | PASS |
| 11a | Split sizes 18k/6k/6k | PASS |
| 11b | Default rate consistent across splits | PASS |

---

## 5. Why Taiwan Default Is Acceptable as a Real-Public Bridge Lane

Taiwan Default satisfies four criteria that make it an acceptable bridge between fully synthetic
and production-grade real data:

**5.1 True observed outcomes.** All 30,000 accounts have observed 6-month payment default
outcomes (binary label confirmed via direct collection). This is not simulated, imputed, or
extrapolated — it is a real credit outcome observed over a defined horizon.

**5.2 Real payment behaviour signals.** The 23 features include real repayment history
(PAY_0 through PAY_6), real statement balances (BILL_AMT1–6), and real payment amounts
(PAY_AMT1–6). These are ledger-level records, not parametrically generated distributions.

**5.3 Authentic demographic attributes.** SEX, EDUCATION, MARRIAGE, and AGE are real
attributes of the accountholders, not synthetic proxies. This enables a genuine (not illustrative)
fairness audit at G9.

**5.4 Peer-reviewed and widely benchmarked.** The dataset has appeared in hundreds of
peer-reviewed papers since 2009. Its characteristics are well-documented, making anomalies
detectable. A model that performs significantly differently from published baselines on this
dataset would be flagged immediately.

**What "bridge lane" means:** Taiwan Default is strong enough to demonstrate real signal, real
calibration, and real fairness methodology — but it is not a production substitute (see §7).

---

## 6. Why Taiwan Default Is NOT the Strongest Final Dataset

Taiwan Default is a research bridge, not the destination. The following limitations constrain it:

| Limitation | Consequence |
|-----------|-------------|
| **2005 vintage (19+ year gap)** | Payment behaviour, credit infrastructure, and macroeconomic context have changed fundamentally. Model performance on current-market data is unknown. |
| **Single geography — Taiwan** | Payment culture, regulatory context, and credit scoring norms differ across jurisdictions. Not transferable without re-training. |
| **Single product — revolving credit cards** | Instalment loans, home loans, SME credit, and BNPL products have fundamentally different risk profiles. |
| **No income or EMI data** | FOIR (Fixed Obligation to Income Ratio) — the standard rule-based credit gate in many markets — cannot be computed from this data. |
| **Random (not temporal) train/test split** | Production validation requires an out-of-time split. Random split overestimates performance stability over time. |
| **No reject inference** | All 30,000 accounts were active cardholders with observed outcomes. A real deployment would only observe outcomes for approved applicants — selection bias not addressed. |
| **PAY_0 encoding ambiguity** | Values −2 and 0 are not explicitly defined in the original paper. Both are treated as "no delay" numerically, but this is an assumption. |
| **30,000 rows** | Adequate for methodology. Small by production standards (Home Credit: 307,511; typical bank portfolio: millions). Confidence intervals on metrics are correspondingly wider. |

---

## 7. Dataset Comparison: Taiwan Default vs Stronger Alternatives

| Dimension | Taiwan Default | Home Credit Default | LendingClub |
|-----------|---------------|---------------------|-------------|
| **Rows** | 30,000 | 307,511 | ~2.26M |
| **Vintage** | 2005 (single cohort) | 2007–2015 (multi-year) | 2007–2018 |
| **Geography** | Taiwan | Multiple (Eastern Europe focus) | USA |
| **Product** | Credit cards (revolving) | Consumer instalment loans | Peer-to-peer loans |
| **Income data** | No | Yes (income, employment) | Yes (stated income, DTI) |
| **Reject inference needed** | No (all active accounts) | Yes (approved-only sample) | Partial |
| **Fairness audit feasibility** | Moderate (SEX/EDUCATION/MARRIAGE available) | Moderate (CODE_GENDER available) | Limited (no demographic features in public data) |
| **Label quality** | High (bank ledger, binary, fixed horizon) | High (binary, fixed horizon) | Medium (multi-state loan status) |
| **Benchmark availability** | Yes (hundreds of papers, ~0.78 AUC typical) | Yes (Kaggle leaderboard public) | Yes (many papers) |
| **Public availability** | Yes (UCI, no auth required) | Yes (Kaggle, requires registration) | Yes (Kaggle / LendingClub website) |
| **PulseGuard status** | **PRIMARY lane — G6 champion trained** | Secondary reference (G5.5 research) | Not used |

**Recommendation for PulseGuard future work:** Home Credit Default Risk is the next logical step
for a stronger real-data lane. It is 10× larger, multi-year, includes income proxies, and has a
well-established Kaggle baseline for benchmarking. Reject inference is required — which becomes
a G9+ deliverable in its own right. LendingClub is the strongest US-market signal but lacks
demographic features for fairness auditing, making it harder to satisfy fair-lending requirements.

---

## 8. Should PulseGuard Add a Stronger Realism Lane Later?

**Yes — this is documented as a future gate requirement, not a current gap.**

The G5.5 lane decision deliberately positioned Taiwan Default as the primary real-data lane for
gates G6–G8. The rationale was:

1. Taiwan Default is immediately available with no authentication, Kaggle registration, or terms
   acceptance required — enabling fast, reproducible pipeline construction.
2. Its manageable size (30,000 rows) keeps training and evaluation latency low during methodology
   development.
3. Its well-documented characteristics make it a trustworthy methodology validation vehicle.

A stronger real-data lane (Home Credit or LendingClub) is appropriate as a **G9+ deliverable**
once the full methodology is validated end-to-end on Taiwan Default. Adding it would:
- Replace the G6 champion or create a secondary champion/challenger on a different dataset
- Require re-running the full G6/G7/G8 pipeline on the new dataset
- Demonstrate dataset-agnostic methodology (the stronger portfolio claim)

This is not a defect in the current architecture — it is the next planned maturity increment.

---

## 9. Provenance Status and Downstream Claim Impact

**Provenance status: PASS**

This PASS unlocks the following safe claims for G9 and portfolio use:

> **Safe claim:** "PulseGuard uses a verified real public credit-card default dataset
> (UCI Taiwan Default, SHA256-confirmed, byte-for-byte identical to the current UCI ML
> Repository file) as the primary decision lane."

> **Safe portfolio framing:** "The primary model was trained and validated on real payment
> history data — not simulated. The dataset is public, peer-reviewed, and widely benchmarked.
> SHA256 verification confirms data integrity."

**If this gate had returned FAIL,** all Taiwan lane claims would have been downgraded to
"unverified data lane" and G9 would remain blocked.

---

## 10. References

| Item | Reference |
|------|-----------|
| Dataset citation | Yeh, I-C.; Lien, C-H. (2009). "The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients." *Expert Systems with Applications*, 36(2), 2473–2480. DOI: [10.1016/j.eswa.2009.12.027](https://doi.org/10.1016/j.eswa.2009.12.027) |
| UCI dataset page | https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients |
| Direct XLS URL | https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls |
| Audit script | `scripts/run_g8_1_data_provenance_audit.py` |
| Audit evidence | `outputs/evidence/g8_1_data_provenance_audit.json` |
| SHA256 (workspace) | `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` |
| SHA256 (UCI live) | `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` |
| Match | **EXACT — byte-for-byte identical** |
