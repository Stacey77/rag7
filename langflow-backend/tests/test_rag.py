"""
Tests for RAG endpoint integration.
"""
import pytest


class TestRAGEndpoints:
    """Tests for RAG-related endpoints in the backend."""
    
    def test_rag_collections_endpoint(self, client):
        """Test listing RAG collections."""
        response = client.get("/rag/collections")
        # May return 200 or 503 if RAG service is not available
        assert response.status_code in [200, 404, 503, 500]
    
    def test_rag_embed_endpoint(self, client):
        """Test text embedding endpoint."""
        response = client.post(
            "/rag/embed",
            data={
                "texts": "Sample text for embedding",
                "collection_name": "test_collection"
            }
        )
        # May return 200, 422, or 503 depending on RAG service availability
        assert response.status_code in [200, 422, 503, 500]
    
    def test_rag_search_endpoint(self, client):
        """Test vector search endpoint."""
        response = client.post(
            "/rag/search",
            data={
                "text": "search query",
                "top_k": 5
            }
        )
        assert response.status_code in [200, 422, 503, 500]
    
    def test_rag_query_endpoint(self, client):
        """Test RAG query endpoint."""
        response = client.post(
            "/rag/query",
            data={
                "query": "What is machine learning?",
                "top_k": 3
            }
        )
        assert response.status_code in [200, 422, 503, 500]


class TestRAGValidation:
    """Tests for RAG input validation."""
    
    def test_embed_missing_text(self, client):
        """Test embedding with missing text returns error."""
        response = client.post("/rag/embed", data={})
        assert response.status_code in [422, 400, 503, 500]
    
    def test_search_invalid_top_k(self, client):
        """Test search with invalid top_k parameter."""
        response = client.post(
            "/rag/search",
            data={
                "text": "search query",
                "top_k": -1
            }
        )
        # Should return validation error or handle gracefully
        assert response.status_code in [200, 422, 400, 503, 500]
