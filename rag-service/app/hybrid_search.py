"""
Hybrid search combining dense (vector) and sparse (BM25) retrieval with fusion.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import Counter
import math
import re


@dataclass
class SearchResult:
    """Search result with score and metadata."""
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    source: str = "hybrid"  # "dense", "sparse", or "hybrid"


class BM25:
    """BM25 sparse retrieval implementation."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25.
        
        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.avgdl = 0
    
    def fit(self, corpus: List[str]):
        """
        Fit BM25 on a corpus.
        
        Args:
            corpus: List of documents
        """
        self.corpus = corpus
        self.doc_len = [len(self._tokenize(doc)) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 0
        
        # Calculate document frequencies
        df = Counter()
        for doc in corpus:
            tokens = set(self._tokenize(doc))
            df.update(tokens)
        
        # Calculate IDF
        num_docs = len(corpus)
        for term, freq in df.items():
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1)
    
    def search(self, query: str, top_k: int = 5) -> List[tuple]:
        """
        Search using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (index, score) tuples
        """
        query_tokens = self._tokenize(query)
        scores = []
        
        for i, doc in enumerate(self.corpus):
            doc_tokens = self._tokenize(doc)
            score = self._score(query_tokens, doc_tokens, i)
            scores.append((i, score))
        
        # Sort by score and return top k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def _score(self, query_tokens: List[str], doc_tokens: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a document."""
        score = 0.0
        doc_len = self.doc_len[doc_idx]
        
        # Count term frequencies in document
        doc_freqs = Counter(doc_tokens)
        
        for token in query_tokens:
            if token not in self.idf:
                continue
            
            tf = doc_freqs.get(token, 0)
            idf = self.idf[token]
            
            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += idf * (numerator / denominator)
        
        return score
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Lowercase and split on non-alphanumeric
        tokens = re.findall(r'\w+', text.lower())
        return tokens


class HybridSearch:
    """
    Hybrid search combining dense vector search with sparse BM25.
    """
    
    def __init__(
        self,
        alpha: float = 0.5,
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75
    ):
        """
        Initialize hybrid search.
        
        Args:
            alpha: Weight for dense search (1-alpha for sparse). Range [0, 1].
            bm25_k1: BM25 term frequency saturation
            bm25_b: BM25 length normalization
        """
        self.alpha = alpha
        self.bm25 = BM25(k1=bm25_k1, b=bm25_b)
        self.corpus = []
        self.corpus_metadata = []
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents for sparse retrieval.
        
        Args:
            documents: List of document dicts with 'text' and optional 'metadata'
        """
        self.corpus = [doc['text'] for doc in documents]
        self.corpus_metadata = [doc.get('metadata', {}) for doc in documents]
        self.bm25.fit(self.corpus)
    
    def search(
        self,
        query: str,
        dense_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining dense and sparse results.
        
        Args:
            query: Search query
            dense_results: Results from dense (vector) search
            top_k: Number of final results
            
        Returns:
            List of SearchResult objects
        """
        # Get sparse results
        sparse_results = self.bm25.search(query, top_k=top_k * 2)
        
        # Normalize scores
        dense_normalized = self._normalize_dense_scores(dense_results)
        sparse_normalized = self._normalize_sparse_scores(sparse_results)
        
        # Combine scores with RRF (Reciprocal Rank Fusion)
        combined = self._reciprocal_rank_fusion(
            dense_normalized,
            sparse_normalized,
            top_k=top_k
        )
        
        return combined
    
    def _normalize_dense_scores(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Normalize dense search scores."""
        if not results:
            return {}
        
        scores = {r['id']: r['score'] for r in results}
        max_score = max(scores.values()) if scores else 1.0
        min_score = min(scores.values()) if scores else 0.0
        
        # Min-max normalization
        if max_score > min_score:
            return {
                id: (score - min_score) / (max_score - min_score)
                for id, score in scores.items()
            }
        return scores
    
    def _normalize_sparse_scores(self, results: List[tuple]) -> Dict[str, float]:
        """Normalize sparse search scores."""
        if not results:
            return {}
        
        scores = {str(idx): score for idx, score in results}
        max_score = max(scores.values()) if scores else 1.0
        min_score = min(scores.values()) if scores else 0.0
        
        # Min-max normalization
        if max_score > min_score:
            return {
                id: (score - min_score) / (max_score - min_score)
                for id, score in scores.items()
            }
        return scores
    
    def _reciprocal_rank_fusion(
        self,
        dense_scores: Dict[str, float],
        sparse_scores: Dict[str, float],
        top_k: int = 5,
        k: int = 60
    ) -> List[SearchResult]:
        """
        Combine results using Reciprocal Rank Fusion.
        
        Args:
            dense_scores: Normalized dense search scores
            sparse_scores: Normalized sparse search scores
            top_k: Number of results to return
            k: RRF parameter (typically 60)
            
        Returns:
            List of SearchResult objects
        """
        # Get all unique document IDs
        all_ids = set(dense_scores.keys()) | set(sparse_scores.keys())
        
        # Calculate RRF scores
        rrf_scores = {}
        for doc_id in all_ids:
            dense_score = dense_scores.get(doc_id, 0.0)
            sparse_score = sparse_scores.get(doc_id, 0.0)
            
            # RRF formula: sum of 1/(k + rank) for each method
            # We use scores as proxy for inverse rank
            dense_rrf = dense_score / (k + (1 - dense_score)) if dense_score > 0 else 0
            sparse_rrf = sparse_score / (k + (1 - sparse_score)) if sparse_score > 0 else 0
            
            # Weighted combination
            rrf_scores[doc_id] = self.alpha * dense_rrf + (1 - self.alpha) * sparse_rrf
        
        # Sort and create results
        sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in sorted_ids:
            # Get document text
            try:
                idx = int(doc_id)
                if 0 <= idx < len(self.corpus):
                    text = self.corpus[idx]
                    metadata = self.corpus_metadata[idx]
                else:
                    text = "Document not found"
                    metadata = {}
            except (ValueError, IndexError):
                text = "Document not found"
                metadata = {}
            
            results.append(SearchResult(
                id=doc_id,
                text=text,
                score=score,
                metadata=metadata,
                source="hybrid"
            ))
        
        return results


def perform_hybrid_search(
    query: str,
    dense_results: List[Dict[str, Any]],
    corpus: List[Dict[str, Any]],
    top_k: int = 5,
    alpha: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Convenience function for hybrid search.
    
    Args:
        query: Search query
        dense_results: Results from vector search
        corpus: Full corpus for sparse search
        top_k: Number of results
        alpha: Weight for dense search (0-1)
        
    Returns:
        List of result dictionaries
    """
    hybrid_search = HybridSearch(alpha=alpha)
    hybrid_search.index_documents(corpus)
    results = hybrid_search.search(query, dense_results, top_k=top_k)
    
    return [
        {
            "id": r.id,
            "text": r.text,
            "score": r.score,
            "metadata": r.metadata,
            "source": r.source
        }
        for r in results
    ]
