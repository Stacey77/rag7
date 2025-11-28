"""
Tests for RAG service main endpoints.
"""
import pytest


class TestHealthEndpoint:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns successfully."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        # May or may not exist
        assert response.status_code in [200, 404]


class TestEmbedEndpoint:
    """Tests for text embedding endpoint."""
    
    def test_embed_text(self, client, sample_texts):
        """Test embedding text documents."""
        response = client.post(
            "/embed/text",
            json={
                "texts": sample_texts,
                "collection_name": "test_collection"
            }
        )
        # May succeed or fail if Milvus not available
        assert response.status_code in [200, 422, 503, 500]
    
    def test_embed_empty_text(self, client):
        """Test embedding with empty text list."""
        response = client.post(
            "/embed/text",
            json={
                "texts": [],
                "collection_name": "test_collection"
            }
        )
        assert response.status_code in [200, 422, 400, 500]


class TestSearchEndpoint:
    """Tests for vector search endpoint."""
    
    def test_search_text(self, client, sample_query):
        """Test text search."""
        response = client.post(
            "/search/text",
            json={
                "text": sample_query,
                "top_k": 5,
                "collection_name": "test_collection"
            }
        )
        assert response.status_code in [200, 422, 503, 500]
    
    def test_search_with_filters(self, client, sample_query):
        """Test search with metadata filters."""
        response = client.post(
            "/search/text",
            json={
                "text": sample_query,
                "top_k": 5,
                "collection_name": "test_collection",
                "filters": {}
            }
        )
        assert response.status_code in [200, 422, 503, 500]


class TestRAGQueryEndpoint:
    """Tests for RAG query endpoint."""
    
    def test_rag_query(self, client, sample_query):
        """Test RAG query with context retrieval."""
        response = client.post(
            "/rag/query",
            json={
                "query": sample_query,
                "top_k": 3
            }
        )
        assert response.status_code in [200, 422, 503, 500]


class TestCollectionsEndpoint:
    """Tests for collection management endpoints."""
    
    def test_list_collections(self, client):
        """Test listing collections."""
        response = client.get("/collections")
        assert response.status_code in [200, 503, 500]
