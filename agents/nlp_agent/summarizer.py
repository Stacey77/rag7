"""Document summarization module."""
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
class SummaryConfig:
    """Configuration for summarization."""
    max_sentences: int = 5
    max_words: int = 150
    method: str = "extractive"   # "extractive" | "abstractive" | "hybrid"
    focus_keywords: List[str] = field(default_factory=list)
    include_title: bool = True


@dataclass
class SummaryResult:
    """Output of document summarization."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_text: str = ""
    summary: str = ""
    compression_ratio: float = 0.0
    sentence_count: int = 0
    word_count: int = 0
    key_phrases: List[str] = field(default_factory=list)
    method: str = "extractive"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "this", "that", "these", "those",
    "it", "its", "i", "you", "he", "she", "we", "they", "my", "your",
    "their", "our", "not", "no", "so", "if", "as", "up", "out", "about",
}


def _tokenize_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def _tokenize_words(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r"\b[a-zA-Z]\w+\b", text)]


def _word_frequency(words: List[str]) -> Dict[str, float]:
    filtered = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    counts = Counter(filtered)
    max_count = max(counts.values()) if counts else 1
    return {word: count / max_count for word, count in counts.items()}


def _sentence_score(sentence: str, word_freq: Dict[str, float],
                    focus_keywords: List[str]) -> float:
    words = _tokenize_words(sentence)
    base_score = sum(word_freq.get(w, 0.0) for w in words) / max(len(words), 1)
    keyword_bonus = sum(2.0 for kw in focus_keywords if kw.lower() in sentence.lower())
    position_factor = 1.0  # adjusted by caller
    return base_score + keyword_bonus * 0.2 * position_factor


class ExtractiveSummarizer:
    """TextRank-inspired extractive summarizer."""

    def summarize(self, text: str, config: SummaryConfig) -> str:
        sentences = _tokenize_sentences(text)
        if not sentences:
            return text[:config.max_words * 6]

        words = _tokenize_words(text)
        freq = _word_frequency(words)
        n = len(sentences)

        scored: List[Tuple[float, int, str]] = []
        for idx, sent in enumerate(sentences):
            # Boost first and last sentences (often contain key info)
            position_bonus = 1.3 if idx == 0 else (1.1 if idx == n - 1 else 1.0)
            score = _sentence_score(sent, freq, config.focus_keywords) * position_bonus
            scored.append((score, idx, sent))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_sentences = sorted(scored[:config.max_sentences], key=lambda x: x[1])

        summary = " ".join(sent for _, _, sent in top_sentences)
        # Truncate to word limit
        words_out = summary.split()
        if len(words_out) > config.max_words:
            summary = " ".join(words_out[:config.max_words]) + "..."
        return summary


class AbstractiveSummarizer:
    """Template-based abstractive summarizer (simulated)."""

    def summarize(self, text: str, config: SummaryConfig) -> str:
        words = _tokenize_words(text)
        freq = _word_frequency(words)
        top_words = sorted(freq, key=lambda w: freq[w], reverse=True)[:10]

        sentences = _tokenize_sentences(text)
        n_sent = len(sentences)

        if n_sent == 0:
            return "No content to summarize."

        # Pick the highest-scoring sentence as "thesis"
        scored = [(sum(freq.get(w, 0) for w in _tokenize_words(s)) / max(len(_tokenize_words(s)), 1), s)
                  for s in sentences]
        thesis = max(scored, key=lambda x: x[0])[1] if scored else sentences[0]

        key_topics = ", ".join(top_words[:5])
        summary = f"{thesis} The key topics discussed include: {key_topics}."
        words_out = summary.split()
        if len(words_out) > config.max_words:
            summary = " ".join(words_out[:config.max_words]) + "..."
        return summary


class KeyPhraseExtractor:
    """Extracts key phrases using n-gram frequency analysis."""

    def extract(self, text: str, n: int = 10) -> List[str]:
        words = _tokenize_words(text)
        freq = _word_frequency(words)
        # Bigrams
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)
                   if words[i] not in _STOPWORDS and words[i+1] not in _STOPWORDS]
        bigram_counts = Counter(bigrams)
        top_bigrams = [bg for bg, _ in bigram_counts.most_common(n // 2)]
        top_words = [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)
                     if w not in _STOPWORDS][:n // 2]
        return list(dict.fromkeys(top_bigrams + top_words))[:n]


class Summarizer:
    """
    Document summarization pipeline supporting extractive, abstractive,
    and hybrid modes with key phrase extraction.
    """

    def __init__(self) -> None:
        self._extractive = ExtractiveSummarizer()
        self._abstractive = AbstractiveSummarizer()
        self._key_phrase = KeyPhraseExtractor()
        logger.info("Summarizer initialized")

    def summarize(self, text: str, config: Optional[SummaryConfig] = None) -> SummaryResult:
        if config is None:
            config = SummaryConfig()
        if not text.strip():
            return SummaryResult(source_text=text, summary="Empty document.")

        if config.method == "extractive":
            summary = self._extractive.summarize(text, config)
        elif config.method == "abstractive":
            summary = self._abstractive.summarize(text, config)
        else:  # hybrid
            ext = self._extractive.summarize(text, SummaryConfig(max_sentences=3, max_words=100))
            abst = self._abstractive.summarize(text, SummaryConfig(max_sentences=2, max_words=60))
            summary = ext + " " + abst

        key_phrases = self._key_phrase.extract(text)
        src_words = len(text.split())
        sum_words = len(summary.split())

        return SummaryResult(
            source_text=text[:200] + "..." if len(text) > 200 else text,
            summary=summary,
            compression_ratio=1 - sum_words / max(src_words, 1),
            sentence_count=len(_tokenize_sentences(summary)),
            word_count=sum_words,
            key_phrases=key_phrases,
            method=config.method,
            metadata={"source_words": src_words, "summary_words": sum_words},
        )

    def batch_summarize(self, texts: List[str], config: Optional[SummaryConfig] = None) -> List[SummaryResult]:
        return [self.summarize(t, config) for t in texts]

    def summarize_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Summarize each section of a structured document."""
        return {title: self.summarize(content).summary for title, content in sections.items()}
