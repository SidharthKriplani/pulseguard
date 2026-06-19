# G9A — Governance Assistant Demo

**Gate:** G9A | Purpose: Demonstrate LM Studio governance assistant capabilities  
**Mode:** ASSISTIVE_ONLY — all outputs require human review

---

## Setup

```bash
# 1. Install dependencies
pip install rank_bm25

# 2. Start LM Studio
# - Open LM Studio
# - Load a model (e.g. Mistral-7B-Instruct or Llama-3-8B-Instruct)
# - Local Server → Start Server (port 1234)

# 3. Verify server
curl http://localhost:1234/v1/models

# 4. Run demo
python src/pulseguard/llm_governance_assistant.py
```

---

## Demo 1: Policy Q&A

### Query: Maximum FOIR Threshold

```python
from src.pulseguard.policy_rag import PolicyRAG

rag = PolicyRAG(policy_dir='data/policy_docs').load()
result = rag.query("What is the maximum FOIR threshold for automatic decline?")

print(f"Abstain: {result.abstain}")
print(f"Top BM25 score: {result.top_score:.3f}")
print(rag.format_context(result))
```

**Expected output (with sample_credit_policy.md indexed):**
```
Abstain: False
Top BM25 score: 0.87

[Source 1: sample_credit_policy.md | Section: FOIR Limits | Relevance: 0.87]
Applications with ANNUITY_TO_INCOME ratio exceeding 0.45 are subject to enhanced 
underwriting review. Applications with ratio exceeding 0.60 require senior credit 
officer sign-off. Ratios exceeding 0.75 are declined without exception.

[Source 2: sample_credit_policy.md | Section: Affordability Constraints | ...]
...
```

### Query: PSI Trigger Threshold

```python
result = rag.query("At what PSI threshold does retraining get triggered?")
print(rag.format_context(result))
```

**Expected retrieved chunk:**
```
"The model must be submitted for retraining review when any of the following occur:
PSI > 0.20 on any top-10 feature for two consecutive months..."
[Source: sample_credit_policy.md § Model Governance]
```

### Query: Out-of-scope (Abstain)

```python
result = rag.query("What is the default rate for Home Credit in Vietnam?")
print(f"Abstain: {result.abstain}")
print(result.abstain_reason)
```

**Expected output:**
```
Abstain: True
Top BM25 score (0.18) below abstain threshold (0.50).
No sufficiently relevant policy found.
```

The assistant abstains rather than hallucinating. The correct answer is "not in our policy corpus — check Kaggle dataset documentation."

---

## Demo 2: Full Governance Assistant (LM Studio)

```python
from src.pulseguard.llm_governance_assistant import GovernanceAssistant

assistant = GovernanceAssistant(policy_dir='data/policy_docs')

# Health check
health = assistant.health_check()
print(f"LM Studio reachable: {health['lm_studio_reachable']}")
print(f"Policy chunks loaded: {health['rag_corpus']['chunks']}")

# Policy Q&A
response = assistant.query_policy(
    "What are the ECOA requirements for adverse action notices?"
)
print(response)
```

**Expected LM Studio response (grounded in policy):**
```
[ASSISTIVE_ONLY | Decision authority: HUMAN_UNDERWRITER]
Query: What are the ECOA requirements for adverse action notices?
Answer: Under ECOA and Regulation B (per PulseGuard Credit Policy §5.1), when an 
adverse action is taken, the applicant must receive: (1) a statement of the action 
taken, (2) the creditor's name and address, (3) a statement of ECOA rights, and 
(4) either specific decline reasons or notification of the right to request reasons 
within 60 days. Adverse action notices must be dispatched within 30 days of the 
credit decision.
Citations: sample_credit_policy.md § ECOA / Regulation B Requirements
```

---

## Demo 3: Adverse Action Draft

```python
draft = assistant.draft_adverse_action(
    applicant_id='APP_TEST_001',
    score_band='RED',
    adverse_factors=[
        'High instalment late payment rate (INST_LATE_RATIO = 0.42)',
        'Low external credit bureau composite score (EXT_SOURCE_MEAN = 0.21)',
        'Requested credit amount high relative to income (CREDIT_TO_INCOME = 8.2)',
        'History of application refusals (PREV_REFUSAL_RATE = 0.67)',
    ],
)
print(draft)
```

**Expected draft output:**
```
=== DRAFT ADVERSE ACTION NOTICE (REQUIRES HUMAN REVIEW) ===
Applicant ID: APP_TEST_001

Dear Applicant,

We have carefully reviewed your credit application and are unable to approve it 
at this time. The primary reasons for this decision are:

1. Payment History: Our records indicate a pattern of late payments on previous 
   credit obligations.
2. Credit Score: Your credit bureau score is below the minimum threshold required 
   for this product.
3. Debt-to-Income Ratio: The requested credit amount is high relative to your 
   stated income.
4. Application History: Previous credit applications have been declined by lenders.

You have the right to obtain a free copy of your credit report within 60 days by 
contacting the relevant credit reporting agency. If you believe any information in 
your credit file is inaccurate, you have the right to dispute it.

This decision was made in accordance with the Equal Credit Opportunity Act (ECOA).

[DRAFT — Requires human review and editing before sending]
[Tag: ASSISTIVE_ONLY_DRAFT]
```

---

## What the Governance Assistant Cannot Do

```python
# These will be refused by design:
assistant.query_policy("Approve application APP_001")
# → "ABSTAIN: The policy documents do not contain approval authority."

assistant.query_policy("Override the RED band for this applicant")  
# → "ABSTAIN: Override authority rests with human underwriters per §4.2."

# It cannot access applicant PII:
# The assistant only sees: score_band, adverse_factors, applicant_id (opaque ref)
# It never sees: name, SSN, address, income figures, SK_ID_CURR mappings
```

---

## RAG Without LM Studio (Retrieval-Only Mode)

If LM Studio is not running, `PolicyRAG` still works for retrieval:

```python
from src.pulseguard.policy_rag import PolicyRAG

rag = PolicyRAG().load()
result = rag.query("What is the KS statistic requirement for production?")
# Returns retrieved chunks with scores — no LLM needed
print(result.chunks[0].text[:300])
```

This is useful for:
- Testing the retrieval pipeline without LM Studio
- Batch policy auditing (retrieve relevant sections for all policy questions)
- Integration testing (CI/CD without LLM dependency)

---

*G9A Example — Governance Assistant Demo | Part of PulseGuard.*
