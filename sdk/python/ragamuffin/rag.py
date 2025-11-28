"""
RAG (Retrieval-Augmented Generation) client for Ragamuffin SDK.
"""

from typing import TYPE_CHECKING, List, Optional, Union
from pathlib import Path

if TYPE_CHECKING:
    from .client import RagamuffinClient


class RAGClient:
    """
    RAG operations for Ragamuffin API.
    
    Example:
        >>> # Embed documents
        >>> client.rag.embed(["Doc 1", "Doc 2"], collection="my_docs")
        
        >>> # Search similar documents
        >>> results = client.rag.search("query text", top_k=5)
        
        >>> # RAG query with context retrieval
        >>> response = client.rag.query("What is machine learning?")
    """

    def __init__(self, client: "RagamuffinClient"):
        self._client = client

    def embed(
        self,
        texts: List[str],
        collection: str = "text_embeddings",
        metadata: Optional[List[dict]] = None,
    ) -> dict:
        """
        Embed text documents into vector database.
        
        Args:
            texts: List of text documents to embed
            collection: Collection name to store embeddings
            metadata: Optional metadata for each document
        
        Returns:
            Embedding result with IDs
        """
        data = {
            "texts": texts,
            "collection_name": collection,
        }
        if metadata:
            data["metadata"] = metadata
        
        return self._client.request("POST", "/rag/embed", json=data)

    def embed_image(
        self,
        image: Union[str, Path, bytes],
        collection: str = "image_embeddings",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Embed an image into vector database.
        
        Args:
            image: Image file path or bytes
            collection: Collection name to store embedding
            metadata: Optional metadata for the image
        
        Returns:
            Embedding result with ID
        """
        if isinstance(image, (str, Path)):
            with open(image, "rb") as f:
                image_bytes = f.read()
            filename = Path(image).name
        else:
            image_bytes = image
            filename = "image.jpg"
        
        files = {"file": (filename, image_bytes)}
        data = {"collection_name": collection}
        if metadata:
            data["metadata"] = str(metadata)
        
        return self._client.request(
            "POST",
            "/rag/embed_image",
            files=files,
            data=data,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        collection: Optional[str] = None,
        filter_expr: Optional[str] = None,
    ) -> dict:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return (1-100)
            collection: Optional collection to search in
            filter_expr: Optional Milvus filter expression
        
        Returns:
            Search results with scores
        """
        data = {
            "text": query,
            "top_k": top_k,
        }
        if collection:
            data["collection_name"] = collection
        if filter_expr:
            data["filter"] = filter_expr
        
        return self._client.request("POST", "/rag/search", json=data)

    def query(
        self,
        query: str,
        top_k: int = 5,
        collection: Optional[str] = None,
        use_hybrid: bool = True,
    ) -> dict:
        """
        Perform RAG query with context retrieval.
        
        Args:
            query: Question or query text
            top_k: Number of context documents to retrieve
            collection: Optional collection to query
            use_hybrid: Whether to use hybrid search (dense + sparse)
        
        Returns:
            Query response with generated answer and context
        """
        data = {
            "query": query,
            "top_k": top_k,
            "use_hybrid": use_hybrid,
        }
        if collection:
            data["collection_name"] = collection
        
        return self._client.request("POST", "/rag/query", json=data)

    def collections(self) -> dict:
        """
        List all available collections.
        
        Returns:
            List of collection names and statistics
        """
        return self._client.request("GET", "/rag/collections")

    def create_collection(
        self,
        name: str,
        dimension: int = 384,
        description: Optional[str] = None,
    ) -> dict:
        """
        Create a new vector collection.
        
        Args:
            name: Collection name
            dimension: Vector dimension (default: 384 for all-MiniLM-L6-v2)
            description: Optional collection description
        
        Returns:
            Created collection info
        """
        data = {
            "name": name,
            "dimension": dimension,
        }
        if description:
            data["description"] = description
        
        return self._client.request("POST", "/rag/collections", json=data)

    def delete_collection(self, name: str) -> dict:
        """
        Delete a collection.
        
        Args:
            name: Collection name to delete
        
        Returns:
            Deletion confirmation
        """
        return self._client.request("DELETE", f"/rag/collections/{name}")

    def collection_stats(self, name: str) -> dict:
        """
        Get statistics for a collection.
        
        Args:
            name: Collection name
        
        Returns:
            Collection statistics (count, dimension, etc.)
        """
        return self._client.request("GET", f"/rag/collections/{name}/stats")
