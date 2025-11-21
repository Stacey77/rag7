"""
Ragamuffin Backend API

This FastAPI application provides endpoints for managing and executing LangFlow flows.

SECURITY WARNINGS:
- This implementation is for DEVELOPMENT ONLY
- Production deployments MUST implement:
  * Authentication (JWT, OAuth)
  * Authorization and RBAC
  * Input validation and sanitization
  * Flow schema validation
  * Sandboxed execution (containers/workers)
  * Resource limits (CPU, memory, timeout)
  * Tool whitelisting
  * Rate limiting
  * Audit logging
  * Encrypted storage
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import langflow - graceful fallback if not available
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("LangFlow is available for flow execution")
except ImportError:
    LANGFLOW_AVAILABLE = False
    logger.warning("LangFlow is not available - /run_flow/ will return simulated responses")

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="Flow management and execution API for Ragamuffin",
    version="1.0.0"
)

# SECURITY NOTE: CORS configuration is permissive for local development
# In production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flows directory configuration
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "Ragamuffin Backend API",
        "status": "running",
        "version": "1.0.0",
        "langflow_available": LANGFLOW_AVAILABLE,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "langflow_available": LANGFLOW_AVAILABLE
    }


@app.post("/save_flow/")
async def save_flow(flow_file: UploadFile = File(...)):
    """
    Save a flow definition to the flows directory.
    
    SECURITY CONSIDERATIONS:
    - Validate flow schema before saving
    - Sanitize flow name to prevent path traversal
    - Implement authorization checks
    - Audit all save operations
    - Validate file size limits
    
    Args:
        flow_file: JSON file containing the flow definition
        
    Returns:
        Success message with flow name
    """
    try:
        # SECURITY: Validate file type
        if not flow_file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Only JSON files are allowed"
            )
        
        # SECURITY: Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(flow_file.filename)
        
        # Read and validate JSON
        content = await flow_file.read()
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format"
            )
        
        # SECURITY: Additional validation should be added here:
        # - Schema validation
        # - Component whitelisting
        # - Resource limit checks
        
        # Save flow to disk
        flow_path = FLOWS_DIR / safe_filename
        with open(flow_path, 'w') as f:
            json.dump(flow_data, f, indent=2)
        
        logger.info(f"Flow saved: {safe_filename}")
        
        return {
            "status": "success",
            "message": f"Flow saved successfully",
            "flow_name": safe_filename,
            "path": str(flow_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving flow: {str(e)}"
        )


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flows.
    
    Returns:
        List of flow names and metadata
    """
    try:
        flows = []
        for flow_file in FLOWS_DIR.glob("*.json"):
            stat = flow_file.stat()
            flows.append({
                "name": flow_file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(flow_file)
            })
        
        return {
            "status": "success",
            "count": len(flows),
            "flows": flows
        }
        
    except Exception as e:
        logger.error(f"Error listing flows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing flows: {str(e)}"
        )


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow definition.
    
    SECURITY CONSIDERATIONS:
    - Validate flow_name to prevent path traversal
    - Implement authorization checks
    - Audit access operations
    
    Args:
        flow_name: Name of the flow file
        
    Returns:
        Flow definition as JSON
    """
    try:
        # SECURITY: Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(flow_name)
        if not safe_filename.endswith('.json'):
            safe_filename += '.json'
        
        flow_path = FLOWS_DIR / safe_filename
        
        if not flow_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{safe_filename}' not found"
            )
        
        with open(flow_path, 'r') as f:
            flow_data = json.load(f)
        
        return {
            "status": "success",
            "flow_name": safe_filename,
            "flow": flow_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving flow: {str(e)}"
        )


@app.post("/run_flow/")
async def run_flow(
    flow_file: UploadFile = File(...),
    user_input: str = Form(...)
):
    """
    Execute a flow with user input.
    
    CRITICAL SECURITY WARNINGS:
    This endpoint executes arbitrary code and is EXTREMELY DANGEROUS without proper safeguards.
    
    REQUIRED PRODUCTION SAFEGUARDS:
    1. Sandboxing: Run flows in isolated containers or workers
    2. Resource Limits: Enforce CPU, memory, and time limits
    3. Tool Restrictions: Whitelist allowed components and tools
    4. Network Isolation: Restrict network access
    5. Input Validation: Sanitize all inputs thoroughly
    6. Authentication: Require authenticated requests
    7. Authorization: Implement permission checks
    8. Audit Logging: Log all execution attempts
    9. Rate Limiting: Prevent abuse
    10. Code Review: Review all flows before execution
    
    Args:
        flow_file: JSON file containing the flow definition
        user_input: User input to pass to the flow
        
    Returns:
        Flow execution result or simulated response
    """
    try:
        # Read flow file
        content = await flow_file.read()
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format"
            )
        
        # SECURITY: Validate user input
        if not user_input or len(user_input) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Invalid user input length"
            )
        
        if LANGFLOW_AVAILABLE:
            try:
                # WARNING: This executes arbitrary code from the flow
                # In production, this MUST run in a sandboxed environment
                logger.warning("Executing flow - ensure this is in a sandboxed environment!")
                
                # Load and execute the flow
                # NOTE: This is a simplified example
                # Real implementation needs proper error handling and sandboxing
                result = load_flow_from_json(flow_data, input_value=user_input)
                
                return {
                    "status": "success",
                    "message": "Flow executed successfully",
                    "result": str(result),
                    "user_input": user_input,
                    "execution_mode": "langflow"
                }
                
            except Exception as e:
                logger.error(f"Flow execution error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Flow execution failed: {str(e)}"
                )
        else:
            # Simulated response when LangFlow is not available
            logger.warning("LangFlow not available - returning simulated response")
            
            return {
                "status": "simulated",
                "message": "LangFlow not available - returning simulated response",
                "result": f"[SIMULATED] Processed input: '{user_input}' with flow '{flow_file.filename}'",
                "user_input": user_input,
                "execution_mode": "simulated",
                "warning": "This is a simulated response. Install LangFlow for actual execution."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in run_flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running flow: {str(e)}"
        )


# Additional utility endpoints

@app.delete("/delete_flow/{flow_name}")
async def delete_flow(flow_name: str):
    """
    Delete a flow (DEVELOPMENT ONLY - requires auth in production).
    
    Args:
        flow_name: Name of the flow to delete
        
    Returns:
        Success message
    """
    try:
        safe_filename = os.path.basename(flow_name)
        if not safe_filename.endswith('.json'):
            safe_filename += '.json'
        
        flow_path = FLOWS_DIR / safe_filename
        
        if not flow_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{safe_filename}' not found"
            )
        
        flow_path.unlink()
        logger.info(f"Flow deleted: {safe_filename}")
        
        return {
            "status": "success",
            "message": f"Flow '{safe_filename}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting flow: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
