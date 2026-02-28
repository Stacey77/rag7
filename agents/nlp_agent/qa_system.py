"""Question answering system for NLP."""
from __future__ import annotations

import logging
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """A document in the knowledge base."""
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    source: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Answer:
    """An answer to a question."""
    answer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question: str = ""
    answer_text: str = ""
    source_doc_id: str = ""
    source_passage: str = ""
    confidence: float = 0.0
    answer_type: str = "extractive"  # "extractive" | "generative" | "no_answer"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "what", "who", "where", "when", "why", "how", "which",
    "does", "do", "did", "will", "would", "could", "should",
    "can", "may", "might", "have", "has", "had", "it", "its",
    "i", "you", "we", "they", "he", "she", "in", "on", "at",
    "to", "for", "of", "with", "by", "from", "and", "or", "but",
}

_QUESTION_TYPES: Dict[str, List[str]] = {
    "factual": ["what", "who", "where", "when", "which"],
    "reasoning": ["why", "how"],
    "boolean": ["is", "are", "does", "do", "can", "will", "has"],
    "quantitative": ["how many", "how much", "how often", "what percentage"],
}


def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r"\b\w+\b", text)]


def _clean_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 2]


def _tfidf_similarity(query_tokens: List[str], doc_tokens: List[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    query_set = Counter(query_tokens)
    doc_counter = Counter(doc_tokens)
    doc_len = len(doc_tokens)
    score = 0.0
    for token, qcount in query_set.items():
        tf = doc_counter.get(token, 0) / doc_len
        score += tf * qcount
    return score / (len(query_set) + 1e-9)


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 10]


def _classify_question(question: str) -> str:
    q_lower = question.lower().strip()
    for qtype, starters in _QUESTION_TYPES.items():
        if any(q_lower.startswith(s) for s in starters):
            return qtype
    return "factual"


class TFIDFRetriever:
    """Retrieves relevant passages using TF-IDF similarity."""

    def retrieve(self, query: str, documents: List[Document], top_k: int = 3) -> List[Tuple[Document, float, str]]:
        query_tokens = _clean_tokens(_tokenize(query))
        scored: List[Tuple[float, Document, str]] = []

        for doc in documents:
            sentences = _split_sentences(doc.content)
            for sent in sentences:
                sent_tokens = _clean_tokens(_tokenize(sent))
                score = _tfidf_similarity(query_tokens, sent_tokens)
                if score > 0:
                    scored.append((score, doc, sent))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [(doc, score, passage) for score, doc, passage in scored[:top_k]]


class ExtractiveReader:
    """Extracts the answer span from a passage."""

    def read(self, question: str, passage: str) -> Tuple[str, float]:
        q_tokens = _clean_tokens(_tokenize(question))
        sentences = _split_sentences(passage)
        if not sentences:
            return passage[:200], 0.3

        # Score each sentence by overlap with question keywords
        scored: List[Tuple[float, str]] = []
        for sent in sentences:
            sent_tokens = _clean_tokens(_tokenize(sent))
            overlap = len(set(q_tokens) & set(sent_tokens))
            score = overlap / max(len(q_tokens), 1)
            scored.append((score, sent))

        scored.sort(reverse=True)
        best_score, best_sent = scored[0]
        return best_sent, min(0.95, 0.4 + best_score * 0.6)


class BooleanAnswerer:
    """Handles yes/no questions."""

    _POSITIVE_SIGNALS = {"yes", "true", "correct", "always", "does", "is", "can", "will", "has"}
    _NEGATIVE_SIGNALS = {"no", "not", "false", "never", "cannot", "won't", "doesn't", "isn't"}

    def answer(self, question: str, passage: str) -> Tuple[str, float]:
        passage_lower = passage.lower()
        pos = sum(1 for w in self._POSITIVE_SIGNALS if w in passage_lower)
        neg = sum(1 for w in self._NEGATIVE_SIGNALS if w in passage_lower)
        if pos > neg:
            return "Yes", 0.6 + min(0.3, pos * 0.05)
        if neg > pos:
            return "No", 0.6 + min(0.3, neg * 0.05)
        return "It depends on the context.", 0.4


class QASystem:
    """
    Question answering system combining TF-IDF retrieval and
    extractive reading with support for multiple QA modes.
    """

    def __init__(self) -> None:
        self._documents: List[Document] = []
        self._retriever = TFIDFRetriever()
        self._reader = ExtractiveReader()
        self._boolean = BooleanAnswerer()
        logger.info("QASystem initialized")

    def add_document(self, title: str, content: str, source: str = "",
                     tags: Optional[List[str]] = None) -> Document:
        doc = Document(title=title, content=content, source=source, tags=tags or [])
        self._documents.append(doc)
        logger.debug("Added document '%s' (%d chars)", title, len(content))
        return doc

    def add_documents(self, docs: List[Dict[str, Any]]) -> List[Document]:
        return [self.add_document(**d) for d in docs]

    def answer(self, question: str, top_k: int = 3) -> Answer:
        if not self._documents:
            return Answer(question=question, answer_text="No knowledge base loaded.",
                          confidence=0.0, answer_type="no_answer")

        question_type = _classify_question(question)
        retrieved = self._retriever.retrieve(question, self._documents, top_k=top_k)

        if not retrieved:
            return Answer(question=question, answer_text="I couldn't find relevant information.",
                          confidence=0.1, answer_type="no_answer")

        best_doc, retrieval_score, best_passage = retrieved[0]

        if question_type == "boolean":
            answer_text, reader_confidence = self._boolean.answer(question, best_passage)
        else:
            answer_text, reader_confidence = self._reader.read(question, best_passage)

        confidence = (retrieval_score * 0.5 + reader_confidence * 0.5)
        return Answer(
            question=question,
            answer_text=answer_text,
            source_doc_id=best_doc.doc_id,
            source_passage=best_passage[:300],
            confidence=confidence,
            answer_type="extractive",
            metadata={
                "question_type": question_type,
                "retrieval_score": retrieval_score,
                "source_title": best_doc.title,
                "candidates": len(retrieved),
            },
        )

    def batch_answer(self, questions: List[str]) -> List[Answer]:
        return [self.answer(q) for q in questions]

    def search_documents(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        retrieved = self._retriever.retrieve(query, self._documents, top_k=top_k)
        seen: Dict[str, float] = {}
        for doc, score, _ in retrieved:
            if doc.doc_id not in seen or seen[doc.doc_id] < score:
                seen[doc.doc_id] = score
        return [(next(d for d in self._documents if d.doc_id == did), score)
                for did, score in sorted(seen.items(), key=lambda x: -x[1])]

    def clear(self) -> None:
        self._documents.clear()

    @property
    def document_count(self) -> int:
        return len(self._documents)
