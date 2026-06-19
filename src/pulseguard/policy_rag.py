"""
policy_rag.py — BM25-based policy document retriever for PulseGuard governance assistant.

ASSISTIVE_ONLY: This module retrieves policy context for human review.
It does not make or recommend credit decisions.

Requirements:
    pip install rank_bm25

Usage:
    from src.pulseguard.policy_rag import PolicyRAG
    rag = PolicyRAG(policy_dir='data/policy_docs')
    result = rag.query("What is the maximum FOIR threshold?")
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PolicyChunk:
    """A chunked section of a policy document."""
    chunk_id: str
    source_file: str
    section: str
    text: str
    token_count: int


@dataclass
class RetrievalResult:
    """Result from a policy retrieval query."""
    query: str
    chunks: List[PolicyChunk]
    scores: List[float]
    top_score: float
    abstain: bool
    abstain_reason: Optional[str] = None


# ── Constants ───────────────────────────────────────────────────────────────

CHUNK_SIZE_WORDS = 120          # Target words per chunk
CHUNK_OVERLAP_WORDS = 25        # Words of overlap between consecutive chunks
ABSTAIN_THRESHOLD = 0.25        # Normalised BM25 score below which we abstain
                                # Calibrated for single-document corpus; increase to 0.5
                                # when corpus grows to 5+ policy documents.
TOP_K_DEFAULT = 4               # Default number of chunks to retrieve


# ── Chunking ────────────────────────────────────────────────────────────────

def _detect_section(text: str, chunk_start: str) -> str:
    """Extract nearest section heading before chunk_start in the text."""
    lines = text[:text.find(chunk_start)].split('\n')
    for line in reversed(lines):
        if line.startswith('#'):
            return line.lstrip('#').strip()
    return 'Introduction'


def chunk_document(file_path: str, text: str) -> List[PolicyChunk]:
    """
    Split a policy document into overlapping word-window chunks.
    Respects paragraph boundaries where possible.
    """
    fname = Path(file_path).name
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]

    chunks: List[PolicyChunk] = []
    buffer_words: List[str] = []
    chunk_idx = 0
    current_section = 'Introduction'

    for para in paragraphs:
        # Track section headings
        if para.startswith('#'):
            current_section = para.lstrip('#').strip()

        para_words = para.split()

        # If adding this paragraph overflows the chunk, flush first
        if len(buffer_words) + len(para_words) > CHUNK_SIZE_WORDS and buffer_words:
            chunk_text = ' '.join(buffer_words)
            chunks.append(PolicyChunk(
                chunk_id=f'{fname}::{chunk_idx}',
                source_file=fname,
                section=current_section,
                text=chunk_text,
                token_count=len(buffer_words),
            ))
            chunk_idx += 1
            # Keep overlap
            buffer_words = buffer_words[-CHUNK_OVERLAP_WORDS:]

        buffer_words.extend(para_words)

    # Flush remaining buffer
    if buffer_words:
        chunks.append(PolicyChunk(
            chunk_id=f'{fname}::{chunk_idx}',
            source_file=fname,
            section=current_section,
            text=' '.join(buffer_words),
            token_count=len(buffer_words),
        ))

    return chunks


# ── PolicyRAG ───────────────────────────────────────────────────────────────

class PolicyRAG:
    """
    BM25-based retriever over a directory of Markdown policy documents.

    Supports:
    - Indexing all .md files in a policy directory
    - BM25 retrieval with top-K chunks
    - Abstain logic when retrieval confidence is low
    - Source citations in results

    Not supported (by design):
    - Making credit decisions
    - Storing PII
    - Internet access
    """

    def __init__(self, policy_dir: str = 'data/policy_docs', top_k: int = TOP_K_DEFAULT):
        self.policy_dir = Path(policy_dir)
        self.top_k = top_k
        self.chunks: List[PolicyChunk] = []
        self.bm25 = None
        self._loaded = False

    def load(self) -> 'PolicyRAG':
        """Load and index all .md files in policy_dir."""
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError(
                "rank_bm25 is required: pip install rank_bm25"
            )

        if not self.policy_dir.exists():
            raise FileNotFoundError(f"Policy directory not found: {self.policy_dir}")

        md_files = list(self.policy_dir.glob('**/*.md'))
        if not md_files:
            raise ValueError(f"No .md files found in {self.policy_dir}")

        self.chunks = []
        for fpath in md_files:
            text = fpath.read_text(encoding='utf-8')
            file_chunks = chunk_document(str(fpath), text)
            self.chunks.extend(file_chunks)

        if not self.chunks:
            raise ValueError("No chunks created — policy documents may be empty.")

        tokenised = [c.text.lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenised)

        # Calibrate normalization ceiling using domain-representative seed queries.
        # These seeds are typical on-topic credit-policy queries that should always
        # return high scores from any credit policy corpus. The 90th-percentile of
        # their max raw scores * 1.15 is the practical ceiling (a perfect match
        # would score ~15% higher than the best seed query). Off-topic queries
        # score far below this ceiling, reliably triggering abstain.
        import numpy as np
        _SEED_QUERIES = [
            "credit score threshold approval decline policy",
            "income debt ratio annuity affordability",
            "default risk customer loan payment overdue",
            "adverse action notice ecoa regulation b",
            "model monitoring psi feature drift retraining",
            "fair lending disparate impact protected class",
        ]
        seed_max_scores = []
        for seed in _SEED_QUERIES:
            s = self.bm25.get_scores(seed.lower().split())
            seed_max_scores.append(float(s.max()))
        ceiling = float(np.percentile(seed_max_scores, 90)) * 1.15
        self._corpus_score_p95 = ceiling if ceiling > 0.5 else 1.0

        self._loaded = True
        print(f"[PolicyRAG] Loaded {len(md_files)} documents → {len(self.chunks)} chunks "
              f"(corpus_p95={self._corpus_score_p95:.2f})")
        return self

    def query(self, query: str, top_k: Optional[int] = None) -> RetrievalResult:
        """
        Retrieve top-K policy chunks relevant to a query.

        Returns a RetrievalResult with abstain=True if confidence is low.
        Always returns citations; never fabricates policy content.
        """
        if not self._loaded:
            self.load()

        k = top_k or self.top_k
        query_tokens = query.lower().split()
        raw_scores = self.bm25.get_scores(query_tokens)

        # Normalize against corpus-level calibration ceiling, not self-max.
        # This ensures off-topic queries score low (<0.5) and trigger abstain.
        norm_scores = raw_scores / self._corpus_score_p95

        top_indices = raw_scores.argsort()[::-1][:k]
        top_chunks = [self.chunks[i] for i in top_indices]
        top_scores = [float(norm_scores[i]) for i in top_indices]

        top_score = top_scores[0] if top_scores else 0.0
        abstain = top_score < ABSTAIN_THRESHOLD

        return RetrievalResult(
            query=query,
            chunks=top_chunks,
            scores=top_scores,
            top_score=top_score,
            abstain=abstain,
            abstain_reason=(
                f"Top BM25 score ({top_score:.3f}) below abstain threshold ({ABSTAIN_THRESHOLD}). "
                "No sufficiently relevant policy found."
            ) if abstain else None,
        )

    def format_context(self, result: RetrievalResult) -> str:
        """Format retrieved chunks as a prompt context block with citations."""
        if result.abstain:
            return f"[NO RELEVANT POLICY FOUND — ABSTAIN]\n{result.abstain_reason}"

        lines = []
        for i, (chunk, score) in enumerate(zip(result.chunks, result.scores), 1):
            lines.append(
                f"[Source {i}: {chunk.source_file} | Section: {chunk.section} | "
                f"Relevance: {score:.2f}]\n{chunk.text}\n"
            )
        return '\n'.join(lines)

    def stats(self) -> Dict:
        """Return corpus statistics."""
        if not self._loaded:
            return {'loaded': False}
        sources = list({c.source_file for c in self.chunks})
        return {
            'loaded': True,
            'documents': len(sources),
            'chunks': len(self.chunks),
            'avg_chunk_words': sum(c.token_count for c in self.chunks) // len(self.chunks),
            'sources': sources,
        }


# ── CLI demo ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    policy_dir = sys.argv[1] if len(sys.argv) > 1 else 'data/policy_docs'
    rag = PolicyRAG(policy_dir=policy_dir).load()
    print(f"\nCorpus stats: {rag.stats()}\n")

    demo_queries = [
        "What is the maximum FOIR threshold for approval?",
        "What happens when a model PSI exceeds 0.20?",
        "What are the adverse action notice requirements under ECOA?",
    ]

    for q in demo_queries:
        print(f"\nQuery: {q}")
        result = rag.query(q)
        print(f"Abstain: {result.abstain} | Top score: {result.top_score:.3f}")
        print(rag.format_context(result)[:500])
        print('---')
