# G8 — Human Review and Override Policy
## PulseGuard · Taiwan Default Credit Decision Model

**Model ID:** `pulseguard-taiwan-xgb-platt-v1`
**Policy ID:** `taiwan_real_data_v1.0`
**Gate:** G8 — Model Risk Governance
**Date:** June 2026

---

> **Portfolio scope note:** This policy defines the human review workflow as it would operate in a production lending environment. In the PulseGuard portfolio, the REVIEW zone is simulated — no real underwriters review decisions. The logging schema and reason codes below are production-pattern artifacts that demonstrate governance discipline.

---

## 1. Decision Workflow Overview

```
Applicant → [Model Score (PD)] → [Policy Router]
                                        │
               ┌────────────────────────┼────────────────────────┐
               ▼                        ▼                        ▼
          PD < 0.20               0.20 ≤ PD < 0.40          PD ≥ 0.40
          AUTO-APPROVE            REVIEW QUEUE              AUTO-REJECT
               │                        │                        │
               ▼                        ▼                        ▼
        [Log + Disburse]      [Underwriter Review]        [Log + Decline]
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                          APPROVE             REJECT
                       (with log)           (with log)
                              │
                         ┌────┴────┐
                         ▼         ▼
                    Standard    Escalate
                    Approval    (if borderline
                                 with risk flag)
```

**Role of humans in this architecture:**
- Auto-APPROVE and auto-REJECT are model-driven decisions with no human in the loop
- REVIEW-zone decisions are human-driven, informed by (but not bound by) the model score
- All three zones produce audit trail entries
- Humans can override auto-decisions only via the escalation pathway (Section 6)

---

## 2. APPROVE Zone (PD < 0.20)

**Decision:** Credit extended automatically.
**Human involvement:** None in standard flow. Human triggered only via escalation (Section 6).
**Logging:** Every APPROVE is logged with the fields in Section 7 (Audit Trail).

**What the model guarantees in this zone:**
- Calibrated PD < 0.20 means the model estimates < 20% probability of default
- G7 test-set data: APPROVE zone observed DR = 10.7% — confirms calibration reliability at this threshold
- Approval rate in this zone: 65.1% of all applicants

**Risk exposure note:** The APPROVE zone is not zero-risk. 10.7% of APPROVE decisions are expected to result in default. The expected loss from this zone is priced into the C_bad cost matrix. An observed DR > 20% over 3+ consecutive months triggers a WARN (see Monitoring Policy).

---

## 3. REJECT Zone (PD ≥ 0.40)

**Decision:** Credit declined automatically.
**Human involvement:** None in standard flow. Human triggered only via escalation (Section 6).
**Logging:** Every REJECT is logged.

**What the model guarantees in this zone:**
- Calibrated PD ≥ 0.40 means the model estimates ≥ 40% probability of default
- G7 test-set data: REJECT zone observed DR = 62.7%
- Reject rate in this zone: 15.9% of all applicants

**Important boundary:** Auto-REJECT decisions must not be communicated to applicants as final in any real-world system without an adverse-action notice framework (see Limitations Policy). In the PulseGuard portfolio, no real applicants receive decisions.

---

## 4. REVIEW Zone (0.20 ≤ PD < 0.40) — Human Review Mandatory

**Decision:** Referred to manual underwriting. The underwriter makes the final APPROVE or REJECT decision.
**Human involvement:** Required. No auto-disposition in this zone.
**Population:** 19.0% of all applicants (G7 test-set reference).
**Observed DR in review zone:** 27.2% — genuinely borderline cohort.

### 4.1 Information the Reviewer Receives

The reviewer's decision interface presents the following:

| Field | Value Shown | Notes |
|-------|-------------|-------|
| Calibrated PD score | Numeric, 2 decimal places (e.g., "0.31") | Calibrated probability; not raw XGBoost score |
| LIMIT_BAL | NT dollar credit limit | Raw value |
| PAY_0 through PAY_6 | Payment status codes | −2 to 8; display with meaning labels (e.g., "−1 = paid in full") |
| BILL_AMT1 through BILL_AMT6 | Monthly statement balances | NT dollar amounts |
| PAY_AMT1 through PAY_AMT6 | Monthly actual payments | NT dollar amounts |
| AGE | Integer | Presented for context only; not a decision factor |
| EDUCATION | Ordinal category | Presented for context only |
| MARRIAGE | Ordinal category | Presented for context only |
| Credit utilization | BILL_AMT1 / LIMIT_BAL (%) | Computed display field; not in training features as a ratio |
| Payment-to-balance ratio | PAY_AMT1 / BILL_AMT1 (%) where BILL_AMT1 > 0 | Computed display field |
| Decision zone | "REVIEW" | Context for reviewer |
| Referral reason (if escalation) | Reason code from Section 6 | Only shown for escalated cases |

### 4.2 Information the Reviewer Does NOT Receive

| Field | Reason Withheld |
|-------|----------------|
| SEX | Must not be used as a decision factor (ECOA / Regulation B analogue) |
| Raw XGBoost score (uncalibrated) | Only calibrated probability is decision-relevant |
| SHAP values | Not computed in current build; would require G9 SHAP integration |
| Comparison to "similar" applicants | No peer group comparison in current architecture |
| Prior application history | Not available in Taiwan Default dataset |

---

## 5. What Reviewers Must Not Do

The following reviewer behaviours are explicitly prohibited and, if observed in log analysis, trigger a review process:

| Prohibited Behaviour | Why Prohibited | Detection Method |
|---------------------|----------------|-----------------|
| Use SEX as a decision factor | Protected characteristic; potential ECOA violation | Override reason code audit; demographic parity monitoring |
| Approve PD > 0.40 without escalation | Would bypass the policy gate; creates unlogged risk exposure | Override log; system validates PD at submission |
| Reject PD < 0.20 without escalation | Would override auto-APPROVE; bypasses calibrated model | Override log; rare — flag for review |
| Submit override with reason code "OTHER" as the only reason | Insufficient audit trail; must use specific reason codes | Override reason code distribution monitoring |
| Approve based solely on EDUCATION or MARRIAGE | Potential proxy discrimination | Override reason code + demographic correlation audit |
| Approve without reading full payment history panel | Negligent decision | Reviewer must confirm "payment history reviewed" checkbox |

---

## 6. Override Logging Schema

Every review-zone decision produces an override log record. Override records are tamper-evident (hash-chained JSONL) and immutable.

```json
{
  "override_id":        "uuid-v4",
  "timestamp_utc":      "2026-06-17T02:30:00Z",
  "model_id":           "pulseguard-taiwan-xgb-platt-v1",
  "policy_id":          "taiwan_real_data_v1.0",
  "application_id":     "APP-XXXXXXX",
  "calibrated_pd":      0.31,
  "model_zone":         "REVIEW",
  "reviewer_id":        "REVIEWER-HASH",
  "decision":           "APPROVE",
  "reason_codes":       ["RC-03", "RC-07"],
  "reason_narrative":   "Strong payment history in recent 3 months; utilization improving; within acceptable risk band.",
  "payment_history_reviewed": true,
  "time_to_decision_seconds": 187,
  "escalated":          false,
  "escalation_reason":  null,
  "sha256_prev":        "abc123...",
  "sha256_this":        "def456..."
}
```

**Required fields:** All fields above are mandatory. An incomplete record is flagged as a process failure.

---

## 7. Override Reason Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| RC-01 | Strong recent payment improvement | PAY_0 through PAY_2 show recent recovery trend |
| RC-02 | High credit limit relative to utilization | LIMIT_BAL >> BILL_AMT1; low utilization in context of score |
| RC-03 | Payment amount exceeds minimum consistently | PAY_AMT shows full payment pattern despite delayed status codes |
| RC-04 | Isolated exceptional month | Single outlier payment event; otherwise clean panel |
| RC-05 | Administrative error in payment status | PAY_0 coding anomaly (−2 / 0 encoding issue) suspected |
| RC-06 | High-exposure account — human judgment required | LIMIT_BAL > 2σ above mean; policy override for large exposure |
| RC-07 | Borderline score with strong fundamentals | PD in 0.20–0.25 range; compelling payment and utilization data |
| RC-08 | Drift condition active — elevated caution | PSI alert in force; reviewer applying additional scrutiny |
| RC-09 | Reject with strong default signal confirmation | PD in 0.35–0.40 range; payment history confirms high risk |
| RC-10 | Escalation initiated — risk officer review | Case escalated per Section 8; reviewer cannot make final decision |
| RC-99 | Other (requires narrative ≥ 50 words) | Use only when no other code applies; narrative mandatory |

---

## 8. Audit Trail Fields

Every decision (auto or reviewed) generates an audit trail record. Review decisions additionally include override fields.

| Field | Type | Description |
|-------|------|-------------|
| `decision_id` | UUID | Unique per decision event |
| `timestamp_utc` | ISO 8601 | Decision timestamp in UTC |
| `model_id` | String | `pulseguard-taiwan-xgb-platt-v1` |
| `policy_id` | String | `taiwan_real_data_v1.0` |
| `policy_version` | String | Semver of threshold policy |
| `application_id` | String | Anonymised application identifier |
| `calibrated_pd` | Float [0,1] | Calibrated probability from Platt model |
| `model_zone` | Enum | `APPROVE` / `REVIEW` / `REJECT` |
| `final_decision` | Enum | `APPROVE` / `REJECT` / `PENDING_REVIEW` |
| `decision_type` | Enum | `AUTO` / `HUMAN_REVIEW` / `ESCALATION` |
| `reviewer_id` | String | Hashed reviewer ID (human decisions only) |
| `reason_codes` | Array[String] | Override reason codes (human decisions only) |
| `reason_narrative` | String | Free text narrative (human decisions; required for RC-99) |
| `payment_history_reviewed` | Boolean | Reviewer confirmation (human decisions only) |
| `escalated` | Boolean | Whether case was escalated to risk officer |
| `drift_alert_active` | Boolean | Whether any monitor was in WARN/ALERT at decision time |
| `psi_pay0_at_decision` | Float | PSI value for PAY_0 at time of decision |
| `ece_at_decision` | Float | Last computed ECE at time of decision |
| `sha256_prev` | String | Hash of previous record (tamper-evidence chain) |
| `sha256_this` | String | Hash of this record |

**Retention:** All audit records are immutable and retained for the model lifecycle plus 5 years (standard model risk governance retention).

---

## 9. Escalation Path

**When escalation is required:**

| Condition | Trigger | Escalation Target |
|-----------|---------|------------------|
| Score boundary proximity | 0.18 ≤ PD < 0.22 or 0.38 ≤ PD < 0.42 AND any PAY_0 = 8 | Senior underwriter |
| High-exposure borderline | LIMIT_BAL > NT$800,000 AND PD in REVIEW zone | Risk officer |
| Drift condition active | Any monitor in ALERT AND reviewer is uncertain | Risk officer |
| Reviewer uncertainty | Reviewer cannot justify with available reason codes | Senior underwriter |
| Potential policy violation | Reviewer suspects systematic bias in decisions | Compliance officer |

**Escalation procedure:**
1. Reviewer selects reason code RC-10 and initiates escalation in decision interface
2. Case transferred to escalation queue with full audit record and reviewer narrative
3. Escalation target reviews within 1 business day (production SLA)
4. Escalation decision logged as a separate audit record with escalation flag
5. Original reviewer notified of escalation outcome

---

## 10. Override Rate Monitoring

Override rates are a model health signal. Abnormal rates indicate process or model issues.

| Metric | Reference (G7 test) | Warn Threshold | Alert Threshold |
|--------|---------------------|----------------|-----------------|
| REVIEW zone APPROVE rate | ~50% (1:1 assumption in G7 EL) | > 75% | > 90% |
| REVIEW zone REJECT rate | ~50% | < 10% | < 5% |
| Escalation rate | < 5% of REVIEW cases | > 15% | > 25% |
| RC-99 (Other) rate | < 10% of override records | > 20% | > 30% |
| Time-to-decision < 30 seconds | < 5% of REVIEW cases | > 20% | > 40% |

**Fast decision flag:** If more than 20% of review decisions complete in under 30 seconds, reviewers are not reading the payment panel. This triggers a process review — not a model flag.

**Override concentration:** If more than 40% of APPROVE overrides come from a single reviewer in a 30-day window, flag for audit. Consistent override patterns by individual reviewer are a model risk red flag.
