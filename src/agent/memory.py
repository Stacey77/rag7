"""Agent memory management using ChromaDB with in-memory fallback."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    Agent memory using ChromaDB for vector storage with in-memory fallback.
    
    This class manages conversation history and allows for semantic search
    over past interactions. Falls back to simple in-memory storage if ChromaDB
    is not available.
    """
    
    def __init__(
        self,
        use_chromadb: bool = True,
        collection_name: str = "agent_memory",
        chroma_host: Optional[str] = None,
        chroma_port: Optional[int] = None
    ):
        """
        Initialize agent memory.
        
        Args:
            use_chromadb: Whether to use ChromaDB (falls back to in-memory if False)
            collection_name: Name of the ChromaDB collection
            chroma_host: ChromaDB host
            chroma_port: ChromaDB port
        """
        self.use_chromadb = use_chromadb
        self.collection_name = collection_name
        self.collection = None
        self.in_memory_storage: List[Dict[str, Any]] = []
        
        if use_chromadb:
            try:
                import chromadb
                
                # Try to connect to ChromaDB
                if chroma_host and chroma_port:
                    # Use HTTP client for remote ChromaDB
                    self.client = chromadb.HttpClient(
                        host=chroma_host,
                        port=chroma_port
                    )
                    logger.info(f"Connected to ChromaDB at {chroma_host}:{chroma_port}")
                else:
                    # Use persistent local client
                    self.client = chromadb.Client()
                    logger.info("Using local ChromaDB client")
                
                # Get or create collection
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"description": "RAG7 Agent conversation memory"}
                )
                logger.info(f"Using ChromaDB collection: {collection_name}")
                
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}. Falling back to in-memory storage.")
                self.use_chromadb = False
                self.collection = None
        else:
            logger.info("Using in-memory storage for agent memory")
    
    async def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a message to memory.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata (e.g., timestamp, user_id)
            
        Returns:
            Message ID
        """
        timestamp = datetime.utcnow().isoformat()
        message_id = f"{role}_{timestamp}_{len(self.in_memory_storage)}"
        
        message_data = {
            "id": message_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }
        
        if self.use_chromadb and self.collection:
            try:
                # Add to ChromaDB with embeddings
                self.collection.add(
                    ids=[message_id],
                    documents=[content],
                    metadatas=[{
                        "role": role,
                        "timestamp": timestamp,
                        **message_data["metadata"]
                    }]
                )
                logger.debug(f"Added message to ChromaDB: {message_id}")
            except Exception as e:
                logger.error(f"Failed to add message to ChromaDB: {e}")
                # Fall back to in-memory
                self.in_memory_storage.append(message_data)
        else:
            # In-memory storage
            self.in_memory_storage.append(message_data)
            logger.debug(f"Added message to in-memory storage: {message_id}")
        
        return message_id
    
    async def get_recent_messages(
        self,
        limit: int = 10,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages from memory.
        
        Args:
            limit: Maximum number of messages to return
            role: Optional role filter (user, assistant, system)
            
        Returns:
            List of messages
        """
        if self.use_chromadb and self.collection:
            try:
                # Query ChromaDB - get all and filter manually since get() doesn't support limit well
                results = self.collection.get(
                    where={"role": role} if role else None
                )
                
                messages = []
                if results and results["ids"]:
                    for i in range(len(results["ids"])):
                        messages.append({
                            "id": results["ids"][i],
                            "content": results["documents"][i],
                            "role": results["metadatas"][i].get("role"),
                            "timestamp": results["metadatas"][i].get("timestamp"),
                            "metadata": results["metadatas"][i]
                        })
                
                # Sort by timestamp and return most recent up to limit
                messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return messages[:limit]
                
            except Exception as e:
                logger.error(f"Failed to get messages from ChromaDB: {e}")
                # Fall through to in-memory
        
        # In-memory retrieval
        filtered = self.in_memory_storage
        if role:
            filtered = [m for m in filtered if m["role"] == role]
        
        return filtered[-limit:]
    
    async def search_similar(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar messages using semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of similar messages
        """
        if self.use_chromadb and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                messages = []
                if results and results["ids"]:
                    for i in range(len(results["ids"][0])):
                        messages.append({
                            "id": results["ids"][0][i],
                            "content": results["documents"][0][i],
                            "role": results["metadatas"][0][i].get("role"),
                            "timestamp": results["metadatas"][0][i].get("timestamp"),
                            "distance": results["distances"][0][i] if "distances" in results else None,
                            "metadata": results["metadatas"][0][i]
                        })
                
                return messages
                
            except Exception as e:
                logger.error(f"Failed to search ChromaDB: {e}")
        
        # Fallback: simple keyword search in in-memory storage
        query_lower = query.lower()
        matches = [
            m for m in self.in_memory_storage
            if query_lower in m["content"].lower()
        ]
        return matches[:limit]
    
    async def clear(self):
        """Clear all memory."""
        if self.use_chromadb and self.collection:
            try:
                # Delete collection and recreate
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "RAG7 Agent conversation memory"}
                )
                logger.info("ChromaDB collection cleared")
            except Exception as e:
                logger.error(f"Failed to clear ChromaDB: {e}")
        
        self.in_memory_storage.clear()
        logger.info("In-memory storage cleared")
    
    def get_conversation_context(
        self,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation as OpenAI message format.
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of messages in OpenAI format
        """
        # This is synchronous for compatibility
        # In real usage, call get_recent_messages async
        messages = self.in_memory_storage[-limit:]
        
        return [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]
