# G9A — LM Studio RAG / LLM Governance Layer

**Gate:** G9A | **Status:** COMPLETE | **Date:** 2026-06-17  
**Mode:** LOCAL, OFFLINE, ASSISTIVE_ONLY  
**Tag:** ASSISTIVE_ONLY — does NOT make credit decisions

---

## 1. Purpose and Scope

The LM Studio Governance Layer provides a **local, offline, privacy-preserving** interface for:

1. **Policy Q&A:** Analysts query the credit policy corpus — "What is our max DTI threshold?" — and get cited answers
2. **Decision rationale drafting:** Auto-draft adverse action notices grounded in SHAP factors and policy citations
3. **Model documentation:** Query model cards, feature definitions, and governance documents
4. **Regulatory reference:** SR 26-2, fair lending, ECOA/adverse action requirements

**What it does NOT do:**
- Make or override credit decisions
- Access applicant data (PII-free design)
- Connect to the internet or external APIs
- Store conversation history

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────┐
│           LM Studio Governance Assistant              │
│                                                      │
│  ┌─────────────────┐    ┌──────────────────────────┐ │
│  │  Policy Corpus  │    │    LM Studio (Local LLM) │ │
│  │  (Chunked MD)   │    │    OpenAI-compat API     │ │
│  │  - credit_policy│    │    localhost:1234         │ │
│  │  - model_cards  │◀───│    Model: Mistral-7B or  │ │
│  │  - SR_26_2_ref  │    │    Llama-3.1-8B or       │ │
│  │  - G9A docs     │    │    Phi-3-mini             │ │
│  └────────┬────────┘    └──────────────────────────┘ │
│           │                         ▲                 │
│  ┌────────▼────────┐               │                 │
│  │   BM25 Retriever│    ┌──────────┴───────────────┐ │
│  │   (rank_bm25)   │───▶│   Query + Context        │ │
│  │   Top-K chunks  │    │   Prompt Assembly        │ │
│  └─────────────────┘    └──────────────────────────┘ │
│                                    │                  │
│                         ┌──────────▼───────────────┐  │
│                         │  Response + Citations     │  │
│                         │  ABSTAIN if no evidence   │  │
│                         └──────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 3. LM Studio Setup

### 3.1 Requirements

- LM Studio installed (https://lmstudio.ai/)
- Local model downloaded: one of:
  - `mistralai/Mistral-7B-Instruct-v0.3` (recommended — best instruction following)
  - `meta-llama/Meta-Llama-3.1-8B-Instruct`
  - `microsoft/Phi-3-mini-4k-instruct` (for RAM-constrained environments)
- LM Studio server running: `localhost:1234` (OpenAI-compatible API)
- `rank_bm25` Python package installed (`pip install rank_bm25`)

### 3.2 Starting LM Studio Server

```bash
# In LM Studio:
# 1. File → Load Model → select Mistral-7B-Instruct
# 2. Local Server → Start Server (port 1234)
# 3. Verify: curl http://localhost:1234/v1/models

# Expected response:
# {"object":"list","data":[{"id":"mistral-7b-instruct-v0.3","object":"model",...}]}
```

---

## 4. Policy RAG Implementation

See: `src/pulseguard/policy_rag.py`

### 4.1 Document Chunking Strategy

```python
CHUNK_SIZE = 400      # tokens (approximate)
CHUNK_OVERLAP = 80    # tokens overlap between chunks
CHUNK_STRATEGY = 'paragraph'  # Split on double newline, then by sentence
```

Policy documents are chunked at paragraph boundaries with overlap to prevent context loss at chunk edges.

### 4.2 BM25 Retrieval

BM25 (Best Match 25) is used for retrieval because:
- **No GPU required** — pure CPU term frequency scoring
- **No embedding model needed** — deterministic, reproducible
- **Good keyword precision** — policy documents are keyword-rich
- **Fast at scale** — sub-millisecond on <10k chunks

```python
from rank_bm25 import BM25Okapi

# Index the policy corpus
corpus_tokenised = [doc.split() for doc in chunks]
bm25 = BM25Okapi(corpus_tokenised)

# Retrieve top-K relevant chunks
query_tokens = query.split()
scores = bm25.get_scores(query_tokens)
top_k_indices = scores.argsort()[-K:][::-1]
top_k_chunks = [chunks[i] for i in top_k_indices]
```

### 4.3 Abstain Behaviour

If no retrieved chunk scores above the relevance threshold, the assistant **must abstain**:

```python
ABSTAIN_THRESHOLD = 0.5  # BM25 score normalised

if max_score < ABSTAIN_THRESHOLD:
    return {
        'answer': 'ABSTAIN: No relevant policy found for this query.',
        'citations': [],
        'confidence': 'low',
        'action': 'Refer to compliance officer or model risk team.'
    }
```

This prevents hallucination on policy questions where no evidence exists.

---

## 5. Prompt Design

### 5.1 System Prompt

```
You are PulseGuard's credit risk governance assistant. You operate in ASSISTIVE_ONLY mode.

Rules:
- Answer ONLY from the provided policy context below.
- If the context does not contain the answer, respond: "ABSTAIN: The policy documents do not address this question."
- Never make or recommend credit decisions.
- Always cite the source document and section for each claim.
- Use precise, regulatory language.
- Do not invent numbers, thresholds, or requirements.
```

### 5.2 User Query Template

```
POLICY CONTEXT:
{retrieved_chunks_with_sources}

QUESTION: {user_query}

Answer based only on the policy context above. Cite source and section.
```

### 5.3 Example Interaction

**Query:** "What is the maximum FOIR threshold for approval?"

**Retrieved chunk (from sample_credit_policy.md §3.2):**
> "Applications with ANNUITY_TO_INCOME ratio exceeding 0.45 are subject to enhanced underwriting review. Applications with ratio exceeding 0.60 require senior credit officer sign-off."

**Response:**
> "Per the PulseGuard Credit Policy §3.2, the FOIR threshold for enhanced review is 0.45 (ANNUITY_TO_INCOME). Applications exceeding 0.60 require senior credit officer approval. There is no automatic decline threshold based on FOIR alone; it is used in conjunction with the risk band assignment.  
> *Source: sample_credit_policy.md §3.2 — Affordability Constraints*"

---

## 6. Governance Features

### 6.1 ASSISTIVE_ONLY Enforcement

All responses include:
```python
response['governance_tag'] = 'ASSISTIVE_ONLY'
response['decision_authority'] = 'HUMAN_UNDERWRITER'
response['model_cannot'] = [
    'approve_application',
    'decline_application', 
    'override_score_band',
    'waive_policy_requirement'
]
```

### 6.2 Adverse Action Notice Drafting

The governance assistant can draft adverse action notice language based on SHAP factors:

**Input:**
```python
{
    'applicant_id': 'APP_12345',
    'score_band': 'RED',
    'default_probability': 0.28,
    'top_adverse_factors': [
        'High instalment late payment rate (INST_LATE_RATIO=0.42)',
        'Low external credit score (EXT_SOURCE_MEAN=0.21)',
        'High debt-to-income ratio (CREDIT_TO_INCOME=8.2)'
    ]
}
```

**Draft output:**
> "Your application was not approved. The primary reasons are: (1) payment history showing a high rate of late payments on prior obligations; (2) external credit bureau score below our risk threshold; (3) requested credit amount high relative to stated income. You have the right to obtain a free credit report and dispute any inaccuracies."

This is a **draft** — requires human review before sending. Never auto-sent.

### 6.3 SR 26-2 Reference Integration

SR 26-2 (April 2026 Federal Reserve/FDIC/OCC Revised Model Risk Management Guidance) key provisions indexed in the policy corpus:

| Provision | Relevance to PulseGuard |
|---|---|
| Model validation independence | Champion model validated on held-out test set (not training data) |
| Conceptual soundness | Monotone constraints documented with domain rationale |
| Ongoing monitoring | PSI-based monitoring architecture defined |
| Model inventory | All models in tournament logged with status and metrics |
| Documentation standards | G9A docs constitute model documentation package |

---

## 7. Implementation Files

| File | Purpose |
|---|---|
| `src/pulseguard/policy_rag.py` | BM25 retriever, chunker, abstain logic |
| `src/pulseguard/llm_governance_assistant.py` | LM Studio API client, prompt assembly, response formatting |
| `data/policy_docs/sample_credit_policy.md` | Sample credit policy (indexable corpus) |

---

## 8. Interview Talking Points

**Q: Why local LM Studio instead of OpenAI API?**  
A: Credit applications contain PII. Sending applicant data to external API endpoints violates data privacy requirements. LM Studio runs the model fully offline — no data leaves the machine. The OpenAI-compatible API means the code requires zero changes to switch between local and cloud if requirements change.

**Q: Why BM25 instead of vector search?**  
A: For structured policy documents, BM25 outperforms dense retrieval on precise keyword queries ("What is the FOIR threshold?"). Vector search excels at semantic similarity — useful for conversational queries but adds GPU/embedding dependency. We chose the simpler, more auditable retrieval method first. Hybrid retrieval (BM25 + FAISS) is the next natural evolution.

**Q: What happens if the LM hallucinates?**  
A: Two mitigations: (1) ABSTAIN logic — if BM25 retrieval confidence is low, the assistant says so rather than guessing; (2) All responses must include a policy citation — if no citation exists, the response is flagged as ungrounded. A human must review all governance assistant outputs before any action is taken.

---

*Part of PulseGuard G9A Gate — LM Studio RAG/LLM Governance Layer.*
