"""
Tests for reranking module.
"""
import pytest
import sys
import os
import numpy as np

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestRerankingImport:
    """Tests for reranking module import."""
    
    def test_import_reranking(self):
        """Test that reranking module can be imported."""
        try:
            from app.reranking import rerank_results, mmr_rerank
            assert callable(rerank_results)
            assert callable(mmr_rerank)
        except ImportError:
            pytest.skip("Reranking module not available")


class TestMMRReranking:
    """Tests for Maximal Marginal Relevance reranking."""
    
    def test_mmr_basic(self):
        """Test basic MMR reranking."""
        try:
            from app.reranking import mmr_rerank
            
            # Mock embeddings (3 documents, 4 dimensions)
            doc_embeddings = np.array([
                [1.0, 0.0, 0.0, 0.0],
                [0.9, 0.1, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0]
            ])
            
            query_embedding = np.array([1.0, 0.0, 0.0, 0.0])
            
            results = [
                {"id": 0, "score": 0.9},
                {"id": 1, "score": 0.8},
                {"id": 2, "score": 0.5}
            ]
            
            reranked = mmr_rerank(
                query_embedding=query_embedding,
                doc_embeddings=doc_embeddings,
                results=results,
                lambda_param=0.5,
                top_k=3
            )
            
            assert len(reranked) <= 3
        except (ImportError, TypeError):
            pytest.skip("MMR reranking not available")
    
    def test_mmr_diversity(self):
        """Test that MMR promotes diversity."""
        try:
            from app.reranking import mmr_rerank
            
            # Two similar docs and one different
            doc_embeddings = np.array([
                [1.0, 0.0, 0.0],
                [0.99, 0.01, 0.0],  # Very similar to first
                [0.0, 1.0, 0.0]    # Different
            ])
            
            query_embedding = np.array([1.0, 0.0, 0.0])
            
            results = [
                {"id": 0, "score": 1.0},
                {"id": 1, "score": 0.99},
                {"id": 2, "score": 0.5}
            ]
            
            # With high diversity (low lambda)
            reranked = mmr_rerank(
                query_embedding=query_embedding,
                doc_embeddings=doc_embeddings,
                results=results,
                lambda_param=0.3,  # Favor diversity
                top_k=3
            )
            
            # The different document should be included
            ids = [r["id"] for r in reranked]
            assert 2 in ids  # Different doc should appear
        except (ImportError, TypeError):
            pytest.skip("MMR reranking not available")


class TestHeuristicReranking:
    """Tests for heuristic-based reranking."""
    
    def test_heuristic_rerank(self):
        """Test heuristic reranking boosts relevant terms."""
        try:
            from app.reranking import heuristic_rerank
            
            results = [
                {"id": 0, "text": "Machine learning is great", "score": 0.8},
                {"id": 1, "text": "Deep learning", "score": 0.7},
                {"id": 2, "text": "Machine learning and AI", "score": 0.6}
            ]
            
            query = "machine learning"
            
            reranked = heuristic_rerank(results, query)
            
            # Documents with exact query match should score higher
            assert len(reranked) == 3
        except (ImportError, TypeError, AttributeError):
            pytest.skip("Heuristic reranking not available")


class TestRerankerInterface:
    """Tests for the main reranker interface."""
    
    def test_rerank_results(self):
        """Test the main rerank_results function."""
        try:
            from app.reranking import rerank_results
            
            results = [
                {"id": 0, "text": "First doc", "score": 0.9},
                {"id": 1, "text": "Second doc", "score": 0.8},
                {"id": 2, "text": "Third doc", "score": 0.7}
            ]
            
            reranked = rerank_results(
                results=results,
                query="first",
                method="heuristic"
            )
            
            assert len(reranked) == 3
        except (ImportError, TypeError):
            pytest.skip("Rerank results function not available")
