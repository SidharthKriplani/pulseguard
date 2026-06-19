# G8 — Monitoring and Incident Policy
## PulseGuard · Taiwan Default Credit Decision Model

**Model ID:** `pulseguard-taiwan-xgb-platt-v1`
**Policy ID:** `taiwan_real_data_v1.0`
**Gate:** G8 — Model Risk Governance
**Date:** June 2026

---

> **Portfolio scope note:** The monitoring triggers below are operationally defined and technically implemented (PSI at G4; ECE at G6). They describe what a production monitoring system would run. In the PulseGuard portfolio, the G4 drift lifecycle (`scripts/seed_lifecycle.py` + `scripts/drift_monitor.py`) demonstrates the monitoring kernel. Production telemetry is simulated, not observed.

---

## 1. Monitoring Architecture

```
[Scored Applications] → [Feature Store Snapshot]
         ↓                        ↓
   [Score Monitor]         [PSI Monitor]
         ↓                        ↓
   [ECE Monitor]          [Approval Rate Monitor]
         ↓                        ↓
         └──────→ [Alert Aggregator] ←──────┘
                          ↓
                  [Alert Severity Router]
                          ↓
            [WARN: Log] / [ALERT: On-Call] / [CRITICAL: Freeze]
```

All monitors are **independent**. A CRITICAL from any single monitor triggers model freeze regardless of other monitor states.

---

## 2. Monitor Definitions and Thresholds

### 2.1 PSI — Population Stability Index (Feature Distribution Drift)

**Purpose:** Detect when the input feature distribution has shifted from the training reference distribution.

**Reference distribution:** Training split (18,000 rows), computed per feature at G6 build time.
**Production measurement:** Each scored batch (weekly minimum; daily in production).
**Method:** 10 equal-frequency quantile bins; PSI = Σ (actual% − expected%) × ln(actual% / expected%); eps=1e-8 on zero bins.

**Primary monitored features (highest model impact):**

| Feature | PSI WARN | PSI ALERT | Rationale |
|---------|----------|-----------|-----------|
| `PAY_0` | > 0.10 | > 0.20 | Strongest predictive feature; most sensitive to economic shocks |
| `PAY_2` | > 0.10 | > 0.20 | Second-most predictive; 2-month lag provides early warning |
| `LIMIT_BAL` | > 0.15 | > 0.25 | Credit limit campaigns produce fast distribution shift |
| `BILL_AMT1` | > 0.15 | > 0.25 | Statement balance tracks LIMIT_BAL; secondary monitor |

**Secondary monitored features (all remaining 19 features):**

| Feature Group | PSI WARN | PSI ALERT |
|--------------|----------|-----------|
| PAY_3 through PAY_6 | > 0.12 | > 0.22 |
| BILL_AMT2 through BILL_AMT6 | > 0.15 | > 0.25 |
| PAY_AMT1 through PAY_AMT6 | > 0.15 | > 0.25 |
| AGE | > 0.20 | > 0.35 |
| SEX, EDUCATION, MARRIAGE | > 0.10 | > 0.20 |

**Baseline from G4 synthetic lifecycle:** Day 7 EXT_SOURCE_2 PSI=0.1532 → WARN ✓; Day 14 PSI=0.2974 → ALERT ✓. These thresholds are validated operationally in the G4 drift kernel.

**Artifact:** `outputs/evidence/g4_drift_report.json` · `outputs/plots/g4_drift_psi_ext_source_2.png`

---

### 2.2 ECE — Expected Calibration Error (Calibration Drift)

**Purpose:** Detect when the model's probability estimates no longer correspond to observed default rates. Calibration drift makes threshold labels (e.g., "PD=0.20 ≈ 20% default probability") inaccurate.

**Baseline (G6 test set):** ECE = 0.0112 (10-bin equal-width calibration).
**Measurement window:** Monthly, on all accounts with resolved labels (i.e., where the T+1 outcome is known).
**Minimum sample for reliable ECE:** N ≥ 1,000 resolved accounts per measurement window.

| ECE Level | Threshold | Severity | Action |
|-----------|-----------|---------|--------|
| Normal | ≤ 0.025 | OK | Log and continue |
| Calibration warn | 0.025 – 0.050 | WARN | Investigate score distribution; increase monitoring frequency |
| Calibration alert | 0.051 – 0.100 | ALERT | Mandatory recalibration review; consider Platt re-fit on recent data |
| Calibration critical | > 0.100 | CRITICAL | Freeze threshold policy; all APPROVE decisions escalated to REVIEW until recalibrated |

**Why ECE > 0.05 is the ALERT trigger:** G6 raw XGBoost ECE=0.208 caused PD scores that were uninformative for threshold setting. If calibration drifts back toward 0.05, the stated 20%/40% thresholds begin to lose their interpretable meaning. ECE > 0.10 means the model is as miscalibrated as a naive baseline.

---

### 2.3 Score Distribution Drift

**Purpose:** Detect regime changes in the output score distribution that may indicate upstream data pipeline changes, population shift, or model drift separate from feature-level PSI.

**Reference:** Test-set calibrated PD score distribution from G6 (mean=0.221, std to be computed at deployment).
**Measurement:** Weekly on scored batch.
**Method:** KS test (scipy.stats.ks_2samp) between production score distribution and reference.

| Condition | Threshold | Severity |
|-----------|-----------|---------|
| Score distribution KS | > 0.05 | WARN |
| Score distribution KS | > 0.10 | ALERT |
| Mean score shift | > 5 pp from reference mean (0.221) | WARN |
| Mean score shift | > 10 pp | ALERT |

---

### 2.4 Approval Rate Drift

**Purpose:** Detect unexpected changes in routing outcomes that may indicate policy drift, data pipeline changes, or model behaviour change.

**Reference rates (G7 test set):** APPROVE=65.1% / REVIEW=19.0% / REJECT=15.9%

| Condition | Threshold | Severity | Action |
|-----------|-----------|---------|--------|
| Approval rate change | > 5 pp month-over-month | WARN | Investigate score distribution and feature PSI |
| Approval rate change | > 10 pp | ALERT | Policy review; check for pipeline data issue |
| Review rate change | > 5 pp | WARN | Model behaviour investigation |
| Reject rate change | > 5 pp | WARN | Investigate; may indicate population shift |

**Special watch:** A sudden approval rate **increase** without ECE improvement is a red flag — it may indicate the model is systematically underscoring default risk (e.g., due to PAY_0 distribution shift making the population appear less risky).

---

### 2.5 Delayed Label Monitoring (Observed Default Rate)

**Purpose:** Compare predicted default rate in the APPROVE zone with the observed default rate once T+1 labels arrive (typically 1–3 months after scoring). This is the ultimate model validity check.

**Reference (G7 test set):** Observed DR in APPROVE zone = 10.7%; REVIEW zone = 27.2%; REJECT zone = 62.7%.

| Condition | Threshold | Severity | Action |
|-----------|-----------|---------|--------|
| Approve zone observed DR | > 20% (2× baseline) sustained 2+ months | WARN | Calibration review |
| Approve zone observed DR | > 25% sustained 3+ months | ALERT | Mandatory model review; consider freeze |
| Approve zone observed DR | > 35% | CRITICAL | Immediate model freeze; rollback |
| Approve zone rank-order failure | Higher-score decile has lower observed DR | ALERT | Model discrimination has inverted; immediate review |

**Implementation note:** In the PulseGuard portfolio, delayed labels are simulated at G4 (30-day synthetic lifecycle). In a real deployment, this monitor requires a label resolution pipeline with a 30–90 day lookback window and a minimum of N=500 resolved decisions per zone per measurement period.

---

## 3. Alert Severity Levels

| Severity | Definition | Response SLA |
|---------|------------|-------------|
| **OK** | All monitors within normal range | No action; scheduled log review |
| **WARN** | One or more monitors approaching threshold | Alert on-call team within 4 hours; investigation by next business day |
| **ALERT** | One or more monitors exceeded threshold | On-call response within 1 hour; root cause report within 2 business days |
| **CRITICAL** | Any monitor in critical state | Immediate response (< 30 min); model freeze under evaluation; rollback decision within 4 hours |

**Alert aggregation rule:** The highest severity across all monitors determines the system-level severity. A single CRITICAL from ECE puts the entire system in CRITICAL state.

---

## 4. Response Actions by Monitor and Severity

### 4.1 PSI Alerts

| Severity | Immediate Action | Owner |
|---------|-----------------|-------|
| WARN | Log; check data pipeline for upstream changes; continue scoring with increased frequency | Monitoring Owner |
| ALERT | Notify Model Owner and Risk Owner; investigate affected features; assess whether score distribution is also shifted; hold pending investigation | Monitoring Owner + Model Owner |
| CRITICAL | Immediate model freeze; activate fallback policy; notify Decision Owner; root cause in 24h | All roles |

### 4.2 ECE Alerts

| Severity | Immediate Action | Owner |
|---------|-----------------|-------|
| WARN | Increase monitoring to daily; prepare recent labelled cohort for Platt re-fit | Model Owner |
| ALERT | Recalibration review session within 48h; Platt re-fit on most recent 3-month labelled cohort; test ECE on holdout before redeployment | Model Owner + Risk Owner |
| CRITICAL | Freeze threshold policy decisions; all auto-APPROVE decisions routed to REVIEW; emergency re-fit and validation required | All roles |

### 4.3 Score Distribution / Approval Rate Alerts

| Severity | Immediate Action | Owner |
|---------|-----------------|-------|
| WARN | Correlation analysis: is score shift explained by PSI? Is approval rate shift consistent with score shift? | Monitoring Owner |
| ALERT | Cross-functional review: Data Owner checks pipeline; Model Owner checks feature drift; Decision Owner reviews policy impact | All roles |

### 4.4 Observed DR Alerts (Delayed Label)

| Severity | Immediate Action | Owner |
|---------|-----------------|-------|
| WARN | Month-over-month observed DR trend report; review whether score decile rank order is preserved | Model Owner |
| ALERT | Full recalibration review; threshold policy review; Risk Owner must sign off before continued auto-APPROVE | Risk Owner + Decision Owner |
| CRITICAL | Freeze approve zone; all accounts route to REVIEW; retroactive review of past 30 days' APPROVE decisions | All roles |

---

## 5. Model Freeze Conditions

Any of the following conditions independently triggers model freeze (all decisions routed to REVIEW):

| Condition | Trigger Value |
|-----------|--------------|
| ECE on recent cohort | > 0.10 |
| PAY_0 PSI | > 0.30 |
| Approve zone observed DR | > 35% |
| Approval rate change | > 15 pp in 30 days |
| Rank-order failure in score deciles | Any decile inversion |
| Data pipeline failure | Any FAIL in feature production |

**Freeze procedure:**
1. Halt auto-APPROVE and auto-REJECT routing
2. All applications route to REVIEW queue
3. Monitoring Owner notifies Decision Owner, Model Owner, Risk Owner within 30 minutes
4. Root cause investigation opened
5. Model freeze remains active until Risk Owner signs off on resumption

---

## 6. Retraining Review Conditions

Model retraining is **not automatic**. It requires a governed review decision.

**Conditions that trigger a retraining review:**
1. ECE ALERT sustained for 2+ consecutive measurement periods
2. PAY_0 PSI ALERT sustained for 3+ consecutive measurement periods
3. Approve zone observed DR ALERT sustained for 2+ consecutive months
4. Decision Owner requests policy recalibration due to economic regime change
5. Scheduled annual review (SR 26-2 recommends ongoing monitoring tied to changing conditions)

**Retraining review process:**
1. Risk Owner reviews current model performance vs. proposed retrain
2. If retrain approved: new champion/challenger run (equivalent to G6 gate) on most recent data
3. New model must pass all 4 promotion gates vs. current champion
4. New Platt calibration fit on most recent val cohort
5. New threshold cost analysis (equivalent to G7 gate) before redeployment
6. Evidence ledger updated with new model version and all artifacts

**No retraining condition (model remains current):**
- All monitors in OK/WARN range for 6+ consecutive months
- Annual review shows no material performance degradation vs. baseline metrics

---

## 7. Monitoring Artifacts

| Artifact | Status | Gate | Location |
|----------|--------|------|----------|
| Synthetic drift lifecycle (30 days, PSI/KS) | ✓ BUILT | G4 | `outputs/evidence/g4_drift_report.json` |
| PSI plot for EXT_SOURCE_2 synthetic drift | ✓ BUILT | G4 | `outputs/plots/g4_drift_psi_ext_source_2.png` |
| Calibration curve plot (Taiwan Default) | ✓ BUILT | G6 | `outputs/plots/g6_calibration_curve.png` |
| Policy bands plot (score decile reliability) | ✓ BUILT | G7 | `outputs/plots/g7_taiwan_policy_bands.png` |
| Drift monitor script | ✓ BUILT | G4 | `scripts/drift_monitor.py` |
| Production monitoring dashboard | DEFERRED | G9 | — |
| Real-time PSI alerting system | DEFERRED | G9 | — |
| Delayed label pipeline | DEFERRED | G9 | — |
