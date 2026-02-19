"""
AGI System - Knowledge Layer with RAG Integration
Manages vector database, knowledge graph, and retrieval engine
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import time
from loguru import logger

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available")


@dataclass
class Document:
    """Represents a document in the knowledge base"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: float = field(default_factory=time.time)


class VectorDatabase:
    """Simple in-memory vector database"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.documents: Dict[str, Document] = {}
        self.vectors: Dict[str, List[float]] = {}
        logger.info(f"Vector Database initialized with dimension={dimension}")
    
    def add_document(self, doc_id: str, content: str, embedding: List[float], 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a document with its embedding"""
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}")
        
        document = Document(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )
        
        self.documents[doc_id] = document
        self.vectors[doc_id] = embedding
        
        logger.debug(f"Added document: {doc_id}")
        return doc_id
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents using cosine similarity"""
        if not self.vectors:
            return []
        
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query embedding dimension mismatch")
        
        # Calculate cosine similarity
        similarities = []
        for doc_id, doc_embedding in self.vectors.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((doc_id, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not NUMPY_AVAILABLE:
            # Simple implementation without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
        else:
            import numpy as np
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID"""
        return self.documents.get(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            del self.vectors[doc_id]
            logger.debug(f"Deleted document: {doc_id}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "total_size_bytes": sum(len(str(doc.content)) for doc in self.documents.values())
        }


class EmbeddingGenerator:
    """Generates embeddings for text (mock implementation)"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        logger.info(f"Embedding Generator initialized with dimension={dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (mock implementation using hash)"""
        # In production, this would use a real embedding model
        # For now, create a deterministic pseudo-embedding based on text hash
        import hashlib
        
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        
        # Create pseudo-random but deterministic embedding
        embedding = []
        for i in range(self.dimension):
            # Use hash and position to generate values
            value = ((hash_value + i) % 10000) / 10000.0 - 0.5
            embedding.append(value)
        
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        embedding = [x / norm for x in embedding]
        
        return embedding
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a query"""
        return self.generate_embedding(query)


class KnowledgeGraph:
    """Knowledge graph for structured knowledge"""
    
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: List[Tuple[str, str, str]] = []  # (subject, predicate, object)
        logger.info("Knowledge Graph initialized")
    
    def add_entity(self, entity_id: str, properties: Dict[str, Any]):
        """Add an entity to the knowledge graph"""
        self.entities[entity_id] = properties
        logger.debug(f"Added entity: {entity_id}")
    
    def add_relation(self, subject: str, predicate: str, obj: str):
        """Add a relation (triple) to the knowledge graph"""
        self.relations.append((subject, predicate, obj))
        logger.debug(f"Added relation: {subject} --[{predicate}]--> {obj}")
    
    def query_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Query an entity by ID"""
        return self.entities.get(entity_id)
    
    def query_relations(self, subject: Optional[str] = None, predicate: Optional[str] = None, 
                       obj: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Query relations matching the pattern"""
        results = []
        for s, p, o in self.relations:
            if subject and s != subject:
                continue
            if predicate and p != predicate:
                continue
            if obj and o != obj:
                continue
            results.append((s, p, o))
        return results
    
    def get_neighbors(self, entity_id: str) -> List[str]:
        """Get neighboring entities"""
        neighbors = set()
        for s, p, o in self.relations:
            if s == entity_id:
                neighbors.add(o)
            if o == entity_id:
                neighbors.add(s)
        return list(neighbors)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "num_entities": len(self.entities),
            "num_relations": len(self.relations),
            "avg_connections": len(self.relations) / max(len(self.entities), 1)
        }


class RetrievalEngine:
    """RAG retrieval engine"""
    
    def __init__(self, vector_db: VectorDatabase, knowledge_graph: KnowledgeGraph, 
                 embedding_generator: EmbeddingGenerator):
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph
        self.embedding_generator = embedding_generator
        logger.info("Retrieval Engine initialized")
    
    def add_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add knowledge to the system"""
        # Generate embedding
        embedding = self.embedding_generator.generate_embedding(content)
        
        # Add to vector database
        doc_id = f"doc_{int(time.time())}_{len(self.vector_db.documents)}"
        self.vector_db.add_document(doc_id, content, embedding, metadata)
        
        logger.info(f"Added knowledge: {doc_id}")
        return doc_id
    
    def retrieve(self, query: str, k: int = 5, use_graph: bool = False) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge for a query"""
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Search vector database
        similar_docs = self.vector_db.search(query_embedding, k)
        
        results = []
        for doc_id, similarity in similar_docs:
            doc = self.vector_db.get_document(doc_id)
            if doc:
                result = {
                    "id": doc_id,
                    "content": doc.content,
                    "similarity": similarity,
                    "metadata": doc.metadata
                }
                
                # Optionally enrich with knowledge graph
                if use_graph:
                    graph_info = self._enrich_with_graph(doc_id)
                    result["graph_context"] = graph_info
                
                results.append(result)
        
        logger.debug(f"Retrieved {len(results)} documents for query")
        return results
    
    def _enrich_with_graph(self, entity_id: str) -> Dict[str, Any]:
        """Enrich result with knowledge graph information"""
        entity_info = self.knowledge_graph.query_entity(entity_id)
        relations = self.knowledge_graph.query_relations(subject=entity_id)
        neighbors = self.knowledge_graph.get_neighbors(entity_id)
        
        return {
            "entity_info": entity_info,
            "relations": relations,
            "neighbors": neighbors
        }
    
    def hybrid_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector and graph search"""
        # Vector search
        vector_results = self.retrieve(query, k, use_graph=False)
        
        # Extract entities from query (simplified)
        query_words = query.lower().split()
        
        # Graph search
        graph_results = []
        for entity_id in self.knowledge_graph.entities:
            if any(word in entity_id.lower() for word in query_words):
                entity_info = self.knowledge_graph.query_entity(entity_id)
                graph_results.append({
                    "id": entity_id,
                    "type": "graph_entity",
                    "info": entity_info,
                    "relations": self.knowledge_graph.query_relations(subject=entity_id)
                })
        
        # Combine results
        combined = {
            "vector_results": vector_results,
            "graph_results": graph_results[:k],
            "query": query
        }
        
        return combined
    
    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get context for query (for RAG)"""
        results = self.retrieve(query, k=5)
        
        context_parts = []
        total_length = 0
        
        for result in results:
            content = result["content"]
            content_length = len(content.split())
            
            if total_length + content_length <= max_tokens:
                context_parts.append(content)
                total_length += content_length
            else:
                break
        
        context = "\n\n".join(context_parts)
        logger.debug(f"Generated context with {total_length} tokens")
        return context


class KnowledgeLayerRAG:
    """Main knowledge layer with RAG integration"""
    
    def __init__(self, embedding_dimension: int = 768):
        self.vector_db = VectorDatabase(dimension=embedding_dimension)
        self.knowledge_graph = KnowledgeGraph()
        self.embedding_generator = EmbeddingGenerator(dimension=embedding_dimension)
        self.retrieval_engine = RetrievalEngine(
            self.vector_db,
            self.knowledge_graph,
            self.embedding_generator
        )
        logger.info("Knowledge Layer RAG initialized")
    
    def ingest_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Ingest a document into the knowledge base"""
        return self.retrieval_engine.add_knowledge(content, metadata)
    
    def ingest_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Ingest multiple documents"""
        doc_ids = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            doc_id = self.ingest_document(content, metadata)
            doc_ids.append(doc_id)
        
        logger.info(f"Ingested {len(doc_ids)} documents")
        return doc_ids
    
    def query(self, query: str, k: int = 5, method: str = "vector") -> Dict[str, Any]:
        """Query the knowledge base"""
        if method == "vector":
            results = self.retrieval_engine.retrieve(query, k)
            return {"method": "vector", "results": results}
        elif method == "hybrid":
            results = self.retrieval_engine.hybrid_search(query, k)
            return {"method": "hybrid", "results": results}
        elif method == "graph":
            # Graph-only search
            query_words = query.lower().split()
            graph_results = []
            for entity_id in self.knowledge_graph.entities:
                if any(word in entity_id.lower() for word in query_words):
                    entity_info = self.knowledge_graph.query_entity(entity_id)
                    graph_results.append({
                        "id": entity_id,
                        "info": entity_info,
                        "relations": self.knowledge_graph.query_relations(subject=entity_id)
                    })
            return {"method": "graph", "results": graph_results[:k]}
        else:
            raise ValueError(f"Unknown query method: {method}")
    
    def add_structured_knowledge(self, subject: str, predicate: str, obj: str, 
                                 subject_props: Optional[Dict[str, Any]] = None,
                                 object_props: Optional[Dict[str, Any]] = None):
        """Add structured knowledge to the knowledge graph"""
        if subject_props:
            self.knowledge_graph.add_entity(subject, subject_props)
        if object_props:
            self.knowledge_graph.add_entity(obj, object_props)
        
        self.knowledge_graph.add_relation(subject, predicate, obj)
        logger.debug(f"Added structured knowledge: {subject} --[{predicate}]--> {obj}")
    
    def augmented_generation(self, query: str, max_context_tokens: int = 2000) -> Dict[str, Any]:
        """Perform retrieval-augmented generation"""
        # Retrieve context
        context = self.retrieval_engine.get_context(query, max_context_tokens)
        
        # In production, this would call an LLM with the context
        # For now, return the context and metadata
        return {
            "query": query,
            "context": context,
            "context_length": len(context.split()),
            "sources": len(self.retrieval_engine.retrieve(query, k=5))
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get knowledge layer statistics"""
        return {
            "vector_db": self.vector_db.get_stats(),
            "knowledge_graph": self.knowledge_graph.get_stats(),
            "total_knowledge_items": len(self.vector_db.documents) + len(self.knowledge_graph.entities)
        }
