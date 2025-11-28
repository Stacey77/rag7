"""
Result reranking using cross-encoder models and MMR for diversity.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class RankedResult:
    """A result with reranking score."""
    id: str
    text: str
    original_score: float
    rerank_score: float
    metadata: Optional[Dict[str, Any]] = None


class MaximalMarginalRelevance:
    """
    MMR (Maximal Marginal Relevance) for diversifying results.
    Balances relevance with diversity to avoid redundant results.
    """
    
    def __init__(self, lambda_param: float = 0.5):
        """
        Initialize MMR.
        
        Args:
            lambda_param: Balance between relevance (1.0) and diversity (0.0)
        """
        self.lambda_param = lambda_param
    
    def rerank(
        self,
        query_embedding: List[float],
        results: List[Dict[str, Any]],
        result_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[RankedResult]:
        """
        Rerank results using MMR.
        
        Args:
            query_embedding: Query embedding vector
            results: Original search results
            result_embeddings: Embeddings for each result
            top_k: Number of results to return
            
        Returns:
            List of RankedResult objects
        """
        if not results or not result_embeddings:
            return []
        
        # Convert to numpy arrays
        query_vec = np.array(query_embedding)
        doc_vecs = np.array(result_embeddings)
        
        # Calculate relevance scores (cosine similarity with query)
        relevance_scores = self._cosine_similarity_batch(query_vec, doc_vecs)
        
        selected_indices = []
        remaining_indices = list(range(len(results)))
        
        # Select top_k documents using MMR
        for _ in range(min(top_k, len(results))):
            if not remaining_indices:
                break
            
            mmr_scores = []
            for idx in remaining_indices:
                # Relevance component
                relevance = relevance_scores[idx]
                
                # Diversity component (max similarity with already selected)
                if selected_indices:
                    selected_vecs = doc_vecs[selected_indices]
                    max_sim = np.max(self._cosine_similarity_batch(
                        doc_vecs[idx],
                        selected_vecs
                    ))
                else:
                    max_sim = 0
                
                # MMR score
                mmr_score = (
                    self.lambda_param * relevance -
                    (1 - self.lambda_param) * max_sim
                )
                mmr_scores.append((idx, mmr_score))
            
            # Select document with highest MMR score
            best_idx, best_score = max(mmr_scores, key=lambda x: x[1])
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        # Create ranked results
        ranked_results = []
        for idx in selected_indices:
            result = results[idx]
            ranked_results.append(RankedResult(
                id=result.get('id', str(idx)),
                text=result.get('text', ''),
                original_score=result.get('score', 0.0),
                rerank_score=relevance_scores[idx],
                metadata=result.get('metadata')
            ))
        
        return ranked_results
    
    def _cosine_similarity_batch(
        self,
        vec: np.ndarray,
        matrix: np.ndarray
    ) -> np.ndarray:
        """Calculate cosine similarity between vector and matrix rows."""
        if vec.ndim == 1:
            vec = vec.reshape(1, -1)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
        
        # Normalize
        vec_norm = vec / (np.linalg.norm(vec, axis=1, keepdims=True) + 1e-10)
        matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
        
        # Compute cosine similarity
        similarities = np.dot(vec_norm, matrix_norm.T)
        return similarities.flatten()


class SimpleReranker:
    """
    Simple reranking based on query-document similarity.
    For production, consider using cross-encoder models like ms-marco-MiniLM.
    """
    
    def __init__(self, boost_exact_matches: bool = True):
        """
        Initialize reranker.
        
        Args:
            boost_exact_matches: Whether to boost scores for exact phrase matches
        """
        self.boost_exact_matches = boost_exact_matches
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[RankedResult]:
        """
        Rerank results based on simple heuristics.
        
        Args:
            query: Search query
            results: Original search results
            top_k: Number of results to return
            
        Returns:
            List of RankedResult objects
        """
        if not results:
            return []
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        reranked = []
        for result in results:
            text = result.get('text', '').lower()
            original_score = result.get('score', 0.0)
            
            # Calculate rerank score
            rerank_score = original_score
            
            # Boost exact phrase matches
            if self.boost_exact_matches and query_lower in text:
                rerank_score *= 1.5
            
            # Boost term coverage
            text_terms = set(text.split())
            term_coverage = len(query_terms & text_terms) / len(query_terms) if query_terms else 0
            rerank_score *= (1 + term_coverage * 0.3)
            
            # Boost shorter, more focused documents
            text_length = len(text.split())
            if text_length < 100:
                rerank_score *= 1.1
            
            reranked.append(RankedResult(
                id=result.get('id', ''),
                text=result.get('text', ''),
                original_score=original_score,
                rerank_score=rerank_score,
                metadata=result.get('metadata')
            ))
        
        # Sort by rerank score and return top k
        reranked.sort(key=lambda x: x.rerank_score, reverse=True)
        return reranked[:top_k]


def rerank_with_mmr(
    query_embedding: List[float],
    results: List[Dict[str, Any]],
    result_embeddings: List[List[float]],
    top_k: int = 5,
    lambda_param: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Convenience function for MMR reranking.
    
    Args:
        query_embedding: Query embedding vector
        results: Original search results
        result_embeddings: Embeddings for results
        top_k: Number of results to return
        lambda_param: MMR lambda parameter (relevance vs diversity)
        
    Returns:
        List of reranked result dictionaries
    """
    mmr = MaximalMarginalRelevance(lambda_param=lambda_param)
    ranked = mmr.rerank(query_embedding, results, result_embeddings, top_k)
    
    return [
        {
            "id": r.id,
            "text": r.text,
            "original_score": r.original_score,
            "rerank_score": r.rerank_score,
            "metadata": r.metadata
        }
        for r in ranked
    ]


def rerank_simple(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Convenience function for simple reranking.
    
    Args:
        query: Search query
        results: Original search results
        top_k: Number of results to return
        
    Returns:
        List of reranked result dictionaries
    """
    reranker = SimpleReranker()
    ranked = reranker.rerank(query, results, top_k)
    
    return [
        {
            "id": r.id,
            "text": r.text,
            "original_score": r.original_score,
            "rerank_score": r.rerank_score,
            "metadata": r.metadata
        }
        for r in ranked
    ]
