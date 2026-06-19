"""
llm_governance_assistant.py — Local LM Studio governance assistant for PulseGuard.

ASSISTIVE_ONLY: This module assists human analysts with policy Q&A and
adverse action drafting. It NEVER makes or overrides credit decisions.

Requirements:
    - LM Studio running locally (https://lmstudio.ai)
    - Server started at localhost:1234
    - rank_bm25 installed: pip install rank_bm25

Usage:
    from src.pulseguard.llm_governance_assistant import GovernanceAssistant
    assistant = GovernanceAssistant()
    response = assistant.query_policy("What is the max DTI threshold?")
    draft = assistant.draft_adverse_action(decision_context)
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.pulseguard.policy_rag import PolicyRAG


# ── Constants ───────────────────────────────────────────────────────────────

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
DEFAULT_MODEL = "local-model"          # LM Studio uses this as the model ID
DEFAULT_TEMPERATURE = 0.1              # Low temp for factual/policy responses
DEFAULT_MAX_TOKENS = 600
TOP_K_CHUNKS = 4

SYSTEM_PROMPT = """You are PulseGuard's credit risk governance assistant. You operate in ASSISTIVE_ONLY mode.

STRICT RULES:
1. Answer ONLY from the provided policy context. Do not use outside knowledge.
2. If the context does not contain the answer, respond exactly: "ABSTAIN: The policy documents do not address this question."
3. Never make, recommend, or override credit decisions.
4. Always cite the source document and section for each factual claim.
5. Use precise, regulatory language.
6. Do not invent numbers, thresholds, ratios, or requirements.
7. If uncertain, say so and recommend consulting a compliance officer.

You are ASSISTIVE_ONLY. Decision authority rests with human underwriters."""

ADVERSE_ACTION_SYSTEM = """You are PulseGuard's adverse action notice drafting assistant. You operate in ASSISTIVE_ONLY mode.

Draft a clear, compliant adverse action notice based on the provided risk factors and policy context.
The draft MUST:
- State the primary adverse factors in plain language (no model jargon)
- Reference the applicant's rights under ECOA/FCRA if applicable
- Not include the probability score or internal model name
- Not use discriminatory language
- Be clearly marked as DRAFT — requires human review before sending

The draft must NOT:
- State a final decision (human must review)
- Include PII beyond what is provided
- Reference protected characteristics
"""


# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class GovernanceResponse:
    """Structured response from the governance assistant."""
    query: str
    answer: str
    citations: List[str]
    abstained: bool
    governance_tag: str = 'ASSISTIVE_ONLY'
    decision_authority: str = 'HUMAN_UNDERWRITER'
    model_cannot: List[str] = field(default_factory=lambda: [
        'approve_application',
        'decline_application',
        'override_score_band',
        'waive_policy_requirement',
    ])
    raw_context_used: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'query': self.query,
            'answer': self.answer,
            'citations': self.citations,
            'abstained': self.abstained,
            'governance_tag': self.governance_tag,
            'decision_authority': self.decision_authority,
            'model_cannot': self.model_cannot,
        }

    def __str__(self) -> str:
        lines = [
            f"[ASSISTIVE_ONLY | Decision authority: {self.decision_authority}]",
            f"Query: {self.query}",
            f"{'⚠ ABSTAINED' if self.abstained else 'Answer'}: {self.answer}",
        ]
        if self.citations:
            lines.append(f"Citations: {'; '.join(self.citations)}")
        return '\n'.join(lines)


@dataclass
class AdverseActionDraft:
    """Draft adverse action notice — REQUIRES HUMAN REVIEW before sending."""
    applicant_id: str
    draft_text: str
    adverse_factors: List[str]
    requires_human_review: bool = True
    governance_tag: str = 'ASSISTIVE_ONLY_DRAFT'

    def __str__(self) -> str:
        return (
            f"=== DRAFT ADVERSE ACTION NOTICE (REQUIRES HUMAN REVIEW) ===\n"
            f"Applicant ID: {self.applicant_id}\n\n"
            f"{self.draft_text}\n\n"
            f"[Tag: {self.governance_tag}]"
        )


# ── LM Studio API client ────────────────────────────────────────────────────

def _lm_studio_chat(
    messages: List[Dict],
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    base_url: str = LM_STUDIO_BASE_URL,
) -> str:
    """
    Call LM Studio's OpenAI-compatible chat completions endpoint.
    Uses only stdlib (urllib) — no openai package required.
    """
    payload = json.dumps({
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': False,
    }).encode('utf-8')

    req = urllib.request.Request(
        url=f'{base_url}/chat/completions',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data['choices'][0]['message']['content'].strip()
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Cannot reach LM Studio at {base_url}. "
            f"Ensure LM Studio is running and server is started. Error: {e}"
        )


def check_lm_studio_health(base_url: str = LM_STUDIO_BASE_URL) -> bool:
    """Check if LM Studio server is reachable."""
    try:
        req = urllib.request.Request(f'{base_url}/models')
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


# ── Governance Assistant ────────────────────────────────────────────────────

class GovernanceAssistant:
    """
    Local LM Studio governance assistant for PulseGuard.

    Combines BM25 policy retrieval with a local LLM for grounded,
    citation-backed answers to policy and governance questions.

    ASSISTIVE_ONLY — never makes credit decisions.
    OFFLINE — all processing on local machine, no data egress.
    """

    def __init__(
        self,
        policy_dir: str = 'data/policy_docs',
        lm_studio_url: str = LM_STUDIO_BASE_URL,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        self.rag = PolicyRAG(policy_dir=policy_dir)
        self.lm_url = lm_studio_url
        self.model = model
        self.temperature = temperature
        self._rag_loaded = False

    def _ensure_rag(self):
        if not self._rag_loaded:
            self.rag.load()
            self._rag_loaded = True

    def query_policy(self, query: str) -> GovernanceResponse:
        """
        Answer a policy question using BM25 retrieval + local LLM.

        If no relevant policy found (BM25 score < threshold), returns ABSTAIN.
        If LM Studio is not available, returns retrieval-only response.
        """
        self._ensure_rag()

        # 1. Retrieve relevant policy chunks
        retrieval = self.rag.query(query)
        context = self.rag.format_context(retrieval)

        # 2. Collect citations from retrieved chunks
        citations = []
        if not retrieval.abstain:
            citations = [
                f"{chunk.source_file} § {chunk.section}"
                for chunk in retrieval.chunks
            ]

        # 3. If abstain threshold not met, return abstain immediately
        if retrieval.abstain:
            return GovernanceResponse(
                query=query,
                answer=f"ABSTAIN: {retrieval.abstain_reason}",
                citations=[],
                abstained=True,
                raw_context_used=None,
            )

        # 4. Call LM Studio for grounded answer
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': (
                f"POLICY CONTEXT:\n{context}\n\n"
                f"QUESTION: {query}\n\n"
                "Answer based ONLY on the policy context above. "
                "Cite source document and section for each claim."
            )},
        ]

        try:
            answer = _lm_studio_chat(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                base_url=self.lm_url,
            )
        except ConnectionError as e:
            # Fallback: return top retrieved chunk without LLM
            answer = (
                f"[LM Studio unavailable — retrieval-only fallback]\n\n"
                f"Most relevant policy excerpt:\n{retrieval.chunks[0].text}"
            )

        # Check if LLM itself abstained
        abstained = answer.strip().upper().startswith('ABSTAIN')

        return GovernanceResponse(
            query=query,
            answer=answer,
            citations=citations if not abstained else [],
            abstained=abstained,
            raw_context_used=context,
        )

    def draft_adverse_action(
        self,
        applicant_id: str,
        score_band: str,
        adverse_factors: List[str],
        policy_context: Optional[str] = None,
    ) -> AdverseActionDraft:
        """
        Draft an adverse action notice based on SHAP-derived adverse factors.

        IMPORTANT: Output is a DRAFT. Human underwriter must review and edit
        before sending to applicant. Never auto-send.

        Args:
            applicant_id: Application reference (not PII)
            score_band: Risk band (RED, AMBER_HIGH, etc.)
            adverse_factors: List of human-readable adverse factors from SHAP
            policy_context: Optional retrieved policy context for ECOA/FCRA refs
        """
        factors_text = '\n'.join(f'- {f}' for f in adverse_factors)

        messages = [
            {'role': 'system', 'content': ADVERSE_ACTION_SYSTEM},
            {'role': 'user', 'content': (
                f"Application ID: {applicant_id}\n"
                f"Risk Band: {score_band}\n\n"
                f"PRIMARY ADVERSE FACTORS (from model explanation):\n{factors_text}\n\n"
                + (f"POLICY CONTEXT:\n{policy_context}\n\n" if policy_context else "")
                + "Draft an adverse action notice. Mark clearly as DRAFT. "
                  "Convert factor names to plain English. Include ECOA rights statement."
            )},
        ]

        try:
            draft_text = _lm_studio_chat(
                messages=messages,
                model=self.model,
                temperature=0.2,   # Slightly more temperature for natural language
                max_tokens=800,
                base_url=self.lm_url,
            )
        except ConnectionError:
            draft_text = (
                "[LM Studio unavailable — template fallback]\n\n"
                f"Dear Applicant,\n\n"
                f"We are unable to approve your application at this time. "
                f"The primary reasons are:\n{factors_text}\n\n"
                f"You have the right to obtain a free copy of your credit report. "
                f"Please contact us for more information.\n\n"
                f"[DRAFT — requires human review and editing]"
            )

        return AdverseActionDraft(
            applicant_id=applicant_id,
            draft_text=draft_text,
            adverse_factors=adverse_factors,
        )

    def health_check(self) -> Dict[str, Any]:
        """Check system health: LM Studio connectivity and RAG corpus."""
        self._ensure_rag()
        lm_ok = check_lm_studio_health(self.lm_url)
        rag_stats = self.rag.stats()
        return {
            'lm_studio_reachable': lm_ok,
            'lm_studio_url': self.lm_url,
            'rag_corpus': rag_stats,
            'governance_tag': 'ASSISTIVE_ONLY',
            'status': 'READY' if lm_ok and rag_stats.get('loaded') else 'DEGRADED',
        }


# ── CLI demo ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("PulseGuard LM Studio Governance Assistant")
    print("=" * 50)

    assistant = GovernanceAssistant(policy_dir='data/policy_docs')
    health = assistant.health_check()
    print(f"Health: {json.dumps(health, indent=2)}\n")

    # Demo 1: Policy Q&A
    response = assistant.query_policy("What is the maximum FOIR threshold for approval?")
    print(response)
    print()

    # Demo 2: Adverse action draft
    draft = assistant.draft_adverse_action(
        applicant_id='APP_DEMO_001',
        score_band='RED',
        adverse_factors=[
            'High instalment payment late ratio (INST_LATE_RATIO = 0.42)',
            'Low external credit bureau score composite (EXT_SOURCE_MEAN = 0.21)',
            'Requested credit amount high relative to stated income (CREDIT_TO_INCOME = 8.2)',
        ],
    )
    print(draft)
