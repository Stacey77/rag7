"""
Ragamuffin RAG Service

Multimodal RAG service with Milvus integration for text, image, and document embeddings.

Features:
- Text embedding and retrieval
- Image embedding and retrieval
- PDF/Document processing
- Multimodal search
- Integration with Milvus vector database
"""

import os
import io
import logging
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin RAG Service",
    description="Multimodal RAG API with Milvus integration",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(exist_ok=True)

# Global variables
embedding_model = None
milvus_connected = False

# Pydantic models
class TextQuery(BaseModel):
    text: str
    top_k: int = 5
    collection_name: str = "text_embeddings"

class EmbedRequest(BaseModel):
    texts: List[str]
    collection_name: str = "text_embeddings"

class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


def connect_milvus():
    """Connect to Milvus database"""
    global milvus_connected
    try:
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        milvus_connected = True
        logger.info(f"✓ Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")
        milvus_connected = False
        return False


def load_embedding_model():
    """Load sentence transformer model"""
    global embedding_model
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"✓ Loaded embedding model: {EMBEDDING_MODEL}")
        return True
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return False


def create_text_collection(collection_name: str = "text_embeddings", dim: int = 384):
    """Create Milvus collection for text embeddings"""
    try:
        if utility.has_collection(collection_name):
            logger.info(f"Collection '{collection_name}' already exists")
            return Collection(collection_name)
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, description="Text embeddings collection")
        
        # Create collection
        collection = Collection(collection_name, schema)
        
        # Create index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        
        logger.info(f"✓ Created collection '{collection_name}'")
        return collection
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        return None


@app.on_event("startup")
async def startup_event():
    """Initialize connections and models on startup"""
    logger.info("Starting RAG service...")
    
    # Connect to Milvus
    connect_milvus()
    
    # Load embedding model
    load_embedding_model()
    
    # Create default collection
    if milvus_connected:
        create_text_collection()
    
    logger.info("✓ RAG service startup complete")


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "name": "Ragamuffin RAG Service",
        "version": "0.1.0",
        "status": "running",
        "milvus_connected": milvus_connected,
        "embedding_model": EMBEDDING_MODEL,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "embed_text": "POST /embed/text",
            "search_text": "POST /search/text",
            "embed_image": "POST /embed/image",
            "collections": "GET /collections"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if milvus_connected and embedding_model else "degraded",
        "milvus_connected": milvus_connected,
        "embedding_model_loaded": embedding_model is not None
    }


@app.post("/embed/text")
async def embed_text(request: EmbedRequest):
    """
    Generate embeddings for text and store in Milvus
    
    Multimodal RAG: Text embedding component
    """
    if not milvus_connected or not embedding_model:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Milvus or embedding model unavailable."
        )
    
    try:
        # Generate embeddings
        embeddings = embedding_model.encode(request.texts)
        
        # Store in Milvus
        collection = Collection(request.collection_name)
        
        # Prepare data
        ids = [f"text_{i}_{hash(text)}" for i, text in enumerate(request.texts)]
        entities = [
            ids,
            embeddings.tolist(),
            request.texts,
            ['{}'] * len(request.texts)  # Empty metadata
        ]
        
        # Insert
        collection.insert(entities)
        collection.flush()
        
        logger.info(f"Embedded and stored {len(request.texts)} texts")
        
        return {
            "status": "success",
            "count": len(request.texts),
            "collection": request.collection_name,
            "ids": ids
        }
    except Exception as e:
        logger.error(f"Error embedding text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/text")
async def search_text(query: TextQuery):
    """
    Search for similar texts using embedding similarity
    
    Multimodal RAG: Text retrieval component
    """
    if not milvus_connected or not embedding_model:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Milvus or embedding model unavailable."
        )
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode([query.text])[0]
        
        # Search in Milvus
        collection = Collection(query.collection_name)
        collection.load()
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=query.top_k,
            output_fields=["text", "metadata"]
        )
        
        # Format results
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "id": hit.id,
                    "text": hit.entity.get("text"),
                    "score": float(hit.distance),
                    "metadata": hit.entity.get("metadata", {})
                })
        
        logger.info(f"Found {len(search_results)} results for query")
        
        return {
            "status": "success",
            "query": query.text,
            "results": search_results
        }
    except Exception as e:
        logger.error(f"Error searching text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed/image")
async def embed_image(
    file: UploadFile = File(...),
    collection_name: str = Form("image_embeddings")
):
    """
    Generate embeddings for images
    
    Multimodal RAG: Image embedding component
    """
    if not milvus_connected or not embedding_model:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Milvus or embedding model unavailable."
        )
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to text description (simplified - in production use CLIP or similar)
        image_description = f"Image: {file.filename}, Size: {image.size}, Mode: {image.mode}"
        
        # Generate embedding from description
        embedding = embedding_model.encode([image_description])[0]
        
        # Store in Milvus
        collection = Collection(collection_name)
        
        image_id = f"img_{hash(file.filename)}"
        entities = [
            [image_id],
            [embedding.tolist()],
            [image_description],
            ['{"type": "image"}']
        ]
        
        collection.insert(entities)
        collection.flush()
        
        logger.info(f"Embedded and stored image: {file.filename}")
        
        return {
            "status": "success",
            "filename": file.filename,
            "id": image_id,
            "collection": collection_name
        }
    except Exception as e:
        logger.error(f"Error embedding image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections")
async def list_collections():
    """List all Milvus collections"""
    if not milvus_connected:
        raise HTTPException(status_code=503, detail="Milvus not connected")
    
    try:
        collections = utility.list_collections()
        
        collection_info = []
        for coll_name in collections:
            collection = Collection(coll_name)
            collection_info.append({
                "name": coll_name,
                "num_entities": collection.num_entities,
                "description": collection.description
            })
        
        return {
            "status": "success",
            "count": len(collections),
            "collections": collection_info
        }
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/query")
async def rag_query(
    query: str = Form(...),
    context_documents: Optional[List[str]] = Form(None),
    top_k: int = Form(5)
):
    """
    Multimodal RAG query endpoint
    
    Retrieves relevant context and generates response
    """
    if not milvus_connected or not embedding_model:
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )
    
    try:
        # Search for relevant documents
        query_embedding = embedding_model.encode([query])[0]
        
        collection = Collection("text_embeddings")
        collection.load()
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text"]
        )
        
        # Get retrieved context
        context = []
        for hits in results:
            for hit in hits:
                context.append(hit.entity.get("text"))
        
        # Simple response (in production, integrate with LLM)
        response = {
            "query": query,
            "retrieved_context": context,
            "response": f"Based on {len(context)} retrieved documents, here is the response to: {query}",
            "top_k": top_k
        }
        
        return response
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
