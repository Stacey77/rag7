"""Data discovery and full-text search for the data catalog."""
from __future__ import annotations

import logging
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SearchIndex:
    """Inverted index entry for a single term."""
    term: str = ""
    postings: Dict[str, float] = field(default_factory=dict)  # asset_id -> tf-idf score


@dataclass
class SearchResult:
    asset_id: str = ""
    name: str = ""
    asset_type: str = ""
    score: float = 0.0
    snippet: str = ""
    matched_fields: List[str] = field(default_factory=list)


@dataclass
class SearchResponse:
    results: List[SearchResult] = field(default_factory=list)
    total_hits: int = 0
    query: str = ""
    elapsed_ms: float = 0.0
    suggestions: List[str] = field(default_factory=list)


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"\b\w{2,}\b", text.lower())
    stopwords = {"the", "and", "or", "in", "of", "to", "a", "an", "is", "for", "with"}
    return [t for t in tokens if t not in stopwords]


def _generate_snippet(text: str, query_terms: List[str], max_len: int = 150) -> str:
    """Extract a text snippet highlighting query terms."""
    text_lower = text.lower()
    best_pos = 0
    for term in query_terms:
        pos = text_lower.find(term)
        if pos >= 0:
            best_pos = max(0, pos - 30)
            break
    snippet = text[best_pos: best_pos + max_len]
    if best_pos > 0:
        snippet = "..." + snippet
    if best_pos + max_len < len(text):
        snippet += "..."
    return snippet


class InvertedIndex:
    """TF-IDF inverted index for asset full-text search."""

    def __init__(self) -> None:
        self._index: Dict[str, Dict[str, float]] = defaultdict(dict)   # term -> {asset_id: tf}
        self._doc_lengths: Dict[str, int] = {}    # asset_id -> token count
        self._doc_count: int = 0
        self._df: Counter = Counter()              # term -> document frequency

    def add_document(self, asset_id: str, text: str, weight: float = 1.0) -> None:
        tokens = _tokenize(text)
        if not tokens:
            return
        counts = Counter(tokens)
        self._doc_lengths[asset_id] = len(tokens)
        self._doc_count += 1
        for term, count in counts.items():
            tf = count / len(tokens)
            self._index[term][asset_id] = tf * weight
            self._df[term] += 1

    def remove_document(self, asset_id: str) -> None:
        to_remove = []
        for term, postings in self._index.items():
            postings.pop(asset_id, None)
            if not postings:
                to_remove.append(term)
        for term in to_remove:
            del self._index[term]
        if asset_id in self._doc_lengths:
            del self._doc_lengths[asset_id]
            self._doc_count -= 1

    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """Return (asset_id, score) sorted by relevance."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        scores: Dict[str, float] = defaultdict(float)
        for term in query_tokens:
            if term not in self._index:
                # Try prefix match
                matching = [t for t in self._index if t.startswith(term)]
                for mt in matching:
                    idf = math.log((self._doc_count + 1) / (self._df.get(mt, 0) + 1))
                    for asset_id, tf in self._index[mt].items():
                        scores[asset_id] += tf * idf * 0.7  # partial match penalty
            else:
                idf = math.log((self._doc_count + 1) / (self._df.get(term, 0) + 1))
                for asset_id, tf in self._index[term].items():
                    scores[asset_id] += tf * idf

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def suggest(self, partial: str, max_suggestions: int = 5) -> List[str]:
        """Suggest query completions based on indexed terms."""
        prefix = partial.lower()
        matching = sorted(
            [t for t in self._index if t.startswith(prefix)],
            key=lambda t: -self._df[t]
        )
        return matching[:max_suggestions]


class FacetedSearch:
    """Faceted search supporting filter aggregations."""

    def __init__(self) -> None:
        self._facets: Dict[str, Dict[str, List[str]]] = {}  # facet_field -> {value -> [asset_ids]}

    def index(self, asset_id: str, facet_field: str, value: str) -> None:
        self._facets.setdefault(facet_field, {}).setdefault(value, []).append(asset_id)

    def filter(self, facet_field: str, value: str) -> List[str]:
        return self._facets.get(facet_field, {}).get(value, [])

    def aggregations(self, facet_field: str) -> Dict[str, int]:
        return {val: len(ids) for val, ids in self._facets.get(facet_field, {}).items()}


class DataCatalogSearch:
    """
    Full-featured data catalog search combining TF-IDF full-text search,
    faceted filtering, and query suggestion.
    """

    def __init__(self) -> None:
        self._index = InvertedIndex()
        self._facets = FacetedSearch()
        self._assets: Dict[str, Dict[str, Any]] = {}   # asset_id -> asset dict
        logger.info("DataCatalogSearch initialized")

    def index_asset(self, asset_id: str, name: str, description: str,
                     asset_type: str, owner: str = "",
                     tags: Optional[List[str]] = None,
                     properties: Optional[Dict[str, Any]] = None) -> None:
        self._assets[asset_id] = {
            "name": name, "description": description, "type": asset_type,
            "owner": owner, "tags": tags or [], "properties": properties or {},
        }
        # Index with field weights
        self._index.add_document(asset_id, name, weight=3.0)
        self._index.add_document(asset_id, description, weight=1.0)
        for tag in (tags or []):
            self._index.add_document(asset_id, tag, weight=2.0)
        prop_text = " ".join(str(v) for v in (properties or {}).values())
        if prop_text:
            self._index.add_document(asset_id, prop_text, weight=0.5)

        self._facets.index(asset_id, "type", asset_type)
        if owner:
            self._facets.index(asset_id, "owner", owner)
        for tag in (tags or []):
            self._facets.index(asset_id, "tag", tag)

    def remove_asset(self, asset_id: str) -> None:
        self._index.remove_document(asset_id)
        self._assets.pop(asset_id, None)

    def search(self, query: str, asset_type: Optional[str] = None,
               owner: Optional[str] = None, tags: Optional[List[str]] = None,
               top_k: int = 10) -> SearchResponse:
        import time
        start = time.perf_counter()
        raw_results = self._index.search(query, top_k=top_k * 3)

        # Apply facet filters
        filter_sets: List[set] = []
        if asset_type:
            filter_sets.append(set(self._facets.filter("type", asset_type)))
        if owner:
            filter_sets.append(set(self._facets.filter("owner", owner)))
        for tag in (tags or []):
            filter_sets.append(set(self._facets.filter("tag", tag)))

        results: List[SearchResult] = []
        query_terms = _tokenize(query)
        for asset_id, score in raw_results:
            if filter_sets and not all(asset_id in fs for fs in filter_sets):
                continue
            asset = self._assets.get(asset_id, {})
            text = asset.get("description", "")
            snippet = _generate_snippet(text, query_terms) if text else ""
            matched = [f for f in ["name", "description", "tags"]
                       if any(t in str(asset.get(f, "")).lower() for t in query_terms)]
            results.append(SearchResult(
                asset_id=asset_id,
                name=asset.get("name", ""),
                asset_type=asset.get("type", ""),
                score=score,
                snippet=snippet,
                matched_fields=matched,
            ))
            if len(results) >= top_k:
                break

        suggestions = self._index.suggest(query.split()[-1] if query.split() else "")
        elapsed_ms = (time.perf_counter() - start) * 1000
        return SearchResponse(
            results=results,
            total_hits=len(results),
            query=query,
            elapsed_ms=elapsed_ms,
            suggestions=suggestions,
        )

    def facet_counts(self, facet_field: str) -> Dict[str, int]:
        return self._facets.aggregations(facet_field)

    def suggest(self, partial: str) -> List[str]:
        return self._index.suggest(partial)
