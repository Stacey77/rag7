"""
Ragamuffin Backend API

FastAPI backend for managing and executing LangFlow flows.

⚠️ SECURITY WARNING:
This is a development scaffold. For production:
- Add authentication and authorization
- Validate all flow JSON inputs
- Sandbox flow execution
- Implement rate limiting
- Review and audit uploaded flows
- Use proper secret management
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="Flow management and execution API for the Ragamuffin platform",
    version="0.1.0"
)

# SECURITY NOTE: CORS configuration is permissive for development
# In production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flows directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True)

# RAG Service configuration
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-service:8001")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")

# Check if langflow is available
LANGFLOW_AVAILABLE = False
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("✓ LangFlow runtime available")
except ImportError:
    logger.warning("⚠️  LangFlow runtime not available - will use simulated responses")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Ragamuffin Backend API",
        "version": "0.1.0",
        "status": "running",
        "langflow_available": LANGFLOW_AVAILABLE,
        "services": {
            "rag_service": RAG_SERVICE_URL,
            "n8n": N8N_URL
        },
        "endpoints": {
            "docs": "/docs",
            "save_flow": "POST /save_flow/",
            "list_flows": "GET /list_flows/",
            "get_flow": "GET /get_flow/{flow_name}",
            "run_flow": "POST /run_flow/",
            "rag_embed": "POST /rag/embed",
            "rag_search": "POST /rag/search",
            "rag_query": "POST /rag/query"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "langflow_available": LANGFLOW_AVAILABLE
    }


@app.post("/save_flow/")
async def save_flow(flow_file: UploadFile = File(...)):
    """
    Save a LangFlow JSON file to the flows directory.
    
    SECURITY NOTE: In production, validate flow content before saving.
    Untrusted flows may contain malicious code.
    """
    try:
        # SECURITY: Validate filename to prevent path traversal
        filename = os.path.basename(flow_file.filename)
        if not filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only .json files are allowed")
        
        # Read file content
        content = await flow_file.read()
        
        # SECURITY: Validate JSON structure
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Save to flows directory
        file_path = FLOWS_DIR / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"✓ Saved flow: {filename}")
        
        return {
            "status": "success",
            "filename": filename,
            "path": str(file_path),
            "size": len(content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save flow: {str(e)}")


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flow JSON files.
    """
    try:
        flows = []
        for file_path in FLOWS_DIR.glob("*.json"):
            stat = file_path.stat()
            flows.append({
                "name": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": str(file_path)
            })
        
        # Sort by modified time, newest first
        flows.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "status": "success",
            "count": len(flows),
            "flows": flows
        }
    
    except Exception as e:
        logger.error(f"Error listing flows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list flows: {str(e)}")


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow file by name.
    
    SECURITY NOTE: Validate flow_name to prevent path traversal attacks.
    """
    try:
        # SECURITY: Validate filename
        filename = os.path.basename(flow_name)
        if not filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only .json files are allowed")
        
        file_path = FLOWS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Flow not found: {flow_name}")
        
        # Read and return flow content
        with open(file_path, 'r') as f:
            flow_data = json.load(f)
        
        return {
            "status": "success",
            "filename": filename,
            "content": flow_data
        }
    
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in flow file")
    except Exception as e:
        logger.error(f"Error getting flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get flow: {str(e)}")


@app.post("/run_flow/")
async def run_flow(
    flow_file: UploadFile = File(...),
    user_input: str = Form(...)
):
    """
    Execute a flow with user input.
    
    ⚠️ CRITICAL SECURITY WARNINGS:
    - This endpoint executes arbitrary code from uploaded flows
    - In production, implement strict validation and sandboxing
    - Consider using containerized execution
    - Implement authentication and authorization
    - Add rate limiting
    - Audit all flow executions
    
    If LangFlow is not available, returns a simulated response.
    """
    try:
        # Read flow file
        content = await flow_file.read()
        
        # Validate JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Save temporary flow file
        temp_filename = f"temp_{flow_file.filename}"
        temp_path = FLOWS_DIR / temp_filename
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Execute flow
        if LANGFLOW_AVAILABLE:
            try:
                # SECURITY WARNING: This executes potentially untrusted code
                # Implement proper sandboxing in production
                logger.info(f"Executing flow with LangFlow: {flow_file.filename}")
                
                # Load and run flow
                flow = load_flow_from_json(str(temp_path))
                result = flow(user_input)
                
                # Clean up temp file
                temp_path.unlink()
                
                return {
                    "status": "success",
                    "flow": flow_file.filename,
                    "input": user_input,
                    "output": str(result),
                    "execution_mode": "langflow"
                }
            
            except Exception as e:
                logger.error(f"Error executing flow with LangFlow: {str(e)}")
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
                raise HTTPException(status_code=500, detail=f"Flow execution failed: {str(e)}")
        
        else:
            # LangFlow not available - return simulated response
            logger.warning(f"⚠️  Simulating flow execution (LangFlow not available): {flow_file.filename}")
            
            # Clean up temp file
            temp_path.unlink()
            
            return {
                "status": "success",
                "flow": flow_file.filename,
                "input": user_input,
                "output": f"[SIMULATED] This is a simulated response. LangFlow runtime is not available. Your input was: '{user_input}'",
                "execution_mode": "simulated",
                "warning": "LangFlow runtime not available - using simulated response"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in run_flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {str(e)}")


@app.delete("/delete_flow/{flow_name}")
async def delete_flow(flow_name: str):
    """
    Delete a specific flow file.
    
    SECURITY NOTE: Implement authorization before allowing deletions.
    """
    try:
        # SECURITY: Validate filename
        filename = os.path.basename(flow_name)
        if not filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only .json files are allowed")
        
        file_path = FLOWS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Flow not found: {flow_name}")
        
        # Delete file
        file_path.unlink()
        
        logger.info(f"✓ Deleted flow: {filename}")
        
        return {
            "status": "success",
            "message": f"Flow deleted: {filename}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete flow: {str(e)}")


# ============================================================================
# RAG Endpoints - Multimodal RAG with Milvus Integration
# ============================================================================

@app.post("/rag/embed")
async def rag_embed_text(texts: List[str] = Form(...), collection_name: str = Form("text_embeddings")):
    """
    Embed text documents into Milvus vector database.
    
    Multimodal RAG: Text embedding component
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/embed/text",
                json={"texts": texts, "collection_name": collection_name},
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG service error: {response.text}"
                )
            
            return response.json()
    
    except httpx.RequestError as e:
        logger.error(f"Error connecting to RAG service: {e}")
        raise HTTPException(
            status_code=503,
            detail="RAG service unavailable"
        )
    except Exception as e:
        logger.error(f"Error in rag_embed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/search")
async def rag_search_text(
    text: str = Form(...),
    top_k: int = Form(5),
    collection_name: str = Form("text_embeddings")
):
    """
    Search for similar text in the vector database.
    
    Multimodal RAG: Text retrieval component
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/search/text",
                json={
                    "text": text,
                    "top_k": top_k,
                    "collection_name": collection_name
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG service error: {response.text}"
                )
            
            return response.json()
    
    except httpx.RequestError as e:
        logger.error(f"Error connecting to RAG service: {e}")
        raise HTTPException(
            status_code=503,
            detail="RAG service unavailable"
        )
    except Exception as e:
        logger.error(f"Error in rag_search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/query")
async def rag_query(
    query: str = Form(...),
    top_k: int = Form(5)
):
    """
    Multimodal RAG query endpoint.
    
    Performs retrieval-augmented generation using Milvus vector store.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/rag/query",
                data={"query": query, "top_k": top_k},
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG service error: {response.text}"
                )
            
            result = response.json()
            
            logger.info(f"RAG query completed: {query}")
            
            return result
    
    except httpx.RequestError as e:
        logger.error(f"Error connecting to RAG service: {e}")
        raise HTTPException(
            status_code=503,
            detail="RAG service unavailable"
        )
    except Exception as e:
        logger.error(f"Error in rag_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/embed_image")
async def rag_embed_image(
    file: UploadFile = File(...),
    collection_name: str = Form("image_embeddings")
):
    """
    Embed image into Milvus vector database.
    
    Multimodal RAG: Image embedding component
    """
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            data = {"collection_name": collection_name}
            
            response = await client.post(
                f"{RAG_SERVICE_URL}/embed/image",
                files=files,
                data=data,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG service error: {response.text}"
                )
            
            return response.json()
    
    except httpx.RequestError as e:
        logger.error(f"Error connecting to RAG service: {e}")
        raise HTTPException(
            status_code=503,
            detail="RAG service unavailable"
        )
    except Exception as e:
        logger.error(f"Error in rag_embed_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/collections")
async def rag_list_collections():
    """List all Milvus collections"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RAG_SERVICE_URL}/collections",
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG service error: {response.text}"
                )
            
            return response.json()
    
    except httpx.RequestError as e:
        logger.error(f"Error connecting to RAG service: {e}")
        raise HTTPException(
            status_code=503,
            detail="RAG service unavailable"
        )
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
