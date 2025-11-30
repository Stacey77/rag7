"""
Ragamuffin Backend - FastAPI Main Application

This module implements the FastAPI backend for managing and executing LangFlow workflows.

SECURITY WARNING: This is a development scaffold. Before production deployment:
- Implement proper authentication and authorization
- Add input validation and sanitization for all endpoints
- Configure CORS for specific domains only
- Add rate limiting to prevent abuse
- Implement flow validation and sandboxing
- Use secure file storage with access controls
- Add comprehensive logging and monitoring
- Validate file types and sizes on upload
- Sanitize file names to prevent directory traversal
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="Backend API for managing and executing LangFlow workflows",
    version="0.1.0"
)

# SECURITY NOTE: CORS is configured for localhost development only.
# In production, replace with specific allowed origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flow storage directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True)

# Try to import langflow for flow execution
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("LangFlow import successful - flow execution enabled")
except ImportError:
    LANGFLOW_AVAILABLE = False
    logger.warning(
        "LangFlow not available - flow execution will return simulated responses. "
        "Install langflow to enable real flow execution."
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Ragamuffin Backend API",
        "version": "0.1.0",
        "endpoints": {
            "docs": "/docs",
            "save_flow": "/save_flow/",
            "list_flows": "/list_flows/",
            "get_flow": "/get_flow/{flow_name}",
            "run_flow": "/run_flow/"
        },
        "langflow_available": LANGFLOW_AVAILABLE
    }


@app.post("/save_flow/")
async def save_flow(flow_file: UploadFile = File(...)):
    """
    Save a LangFlow workflow JSON file.
    
    SECURITY NOTES:
    - Validate file is actual JSON before saving
    - Sanitize filename to prevent directory traversal
    - Limit file size to prevent DoS
    - Validate flow schema/structure
    - Add authentication before production use
    
    Args:
        flow_file: Uploaded JSON file containing the flow definition
        
    Returns:
        Success message with flow name
    """
    try:
        # SECURITY: Validate file extension
        if not flow_file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .json files are allowed."
            )
        
        # SECURITY: Sanitize filename to prevent directory traversal
        filename = os.path.basename(flow_file.filename)
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename. Directory traversal not allowed."
            )
        
        # Read and validate JSON content
        content = await flow_file.read()
        
        # SECURITY: Limit file size (10MB max)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # SECURITY: Basic validation that it's a flow object
        # TODO: Add comprehensive schema validation
        if not isinstance(flow_data, dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid flow format. Expected JSON object."
            )
        
        # Save flow to disk
        flow_path = FLOWS_DIR / filename
        with open(flow_path, 'w') as f:
            json.dump(flow_data, f, indent=2)
        
        logger.info(f"Flow saved successfully: {filename}")
        
        return {
            "message": "Flow saved successfully",
            "flow_name": filename,
            "path": str(flow_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save flow: {str(e)}"
        )


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flow files.
    
    SECURITY NOTES:
    - Add authentication to prevent enumeration
    - Filter flows by user/permissions in production
    
    Returns:
        List of flow names with metadata
    """
    try:
        flows = []
        for flow_file in FLOWS_DIR.glob("*.json"):
            try:
                stat = flow_file.stat()
                flows.append({
                    "name": flow_file.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            except Exception as e:
                logger.warning(f"Error reading flow {flow_file.name}: {str(e)}")
                continue
        
        return {
            "flows": flows,
            "count": len(flows)
        }
        
    except Exception as e:
        logger.error(f"Error listing flows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list flows: {str(e)}"
        )


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Get a specific flow by name.
    
    SECURITY NOTES:
    - Validate flow_name to prevent directory traversal
    - Add authentication to control access
    - Validate user has permission to access this flow
    
    Args:
        flow_name: Name of the flow file
        
    Returns:
        Flow JSON data
    """
    try:
        # SECURITY: Sanitize flow name to prevent directory traversal
        flow_name = os.path.basename(flow_name)
        if '..' in flow_name or '/' in flow_name or '\\' in flow_name:
            raise HTTPException(
                status_code=400,
                detail="Invalid flow name. Directory traversal not allowed."
            )
        
        if not flow_name.endswith('.json'):
            flow_name += '.json'
        
        flow_path = FLOWS_DIR / flow_name
        
        if not flow_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{flow_name}' not found"
            )
        
        with open(flow_path, 'r') as f:
            flow_data = json.load(f)
        
        return {
            "flow_name": flow_name,
            "flow_data": flow_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get flow: {str(e)}"
        )


@app.post("/run_flow/")
async def run_flow(
    flow_file: UploadFile = File(...),
    user_input: str = Form(...)
):
    """
    Execute a LangFlow workflow with user input.
    
    SECURITY NOTES:
    - CRITICAL: Validate and sandbox flow execution
    - Limit execution time to prevent DoS
    - Validate user_input to prevent injection attacks
    - Add rate limiting per user/IP
    - Log all executions for audit
    - Consider using a separate execution environment
    
    Args:
        flow_file: Flow JSON file to execute
        user_input: User input text for the flow
        
    Returns:
        Flow execution result
    """
    try:
        # SECURITY: Validate file type
        if not flow_file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .json files are allowed."
            )
        
        # Read and parse flow
        content = await flow_file.read()
        
        # SECURITY: Limit file size
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # SECURITY: Validate user_input length
        if len(user_input) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Input too long. Maximum length is 10000 characters."
            )
        
        # Execute flow if LangFlow is available
        if LANGFLOW_AVAILABLE:
            try:
                # TODO: Add proper flow execution with timeout and sandboxing
                # This is a placeholder for actual LangFlow execution
                # Real implementation should:
                # - Use asyncio.wait_for() to timeout long-running flows
                # - Execute in isolated environment
                # - Validate flow before execution
                # - Sanitize all inputs and outputs
                
                logger.info(f"Executing flow with input: {user_input[:50]}...")
                
                # Placeholder for actual execution
                result = {
                    "status": "success",
                    "output": f"Flow executed with input: {user_input}",
                    "flow_name": flow_file.filename,
                    "note": "Real execution would happen here with load_flow_from_json"
                }
                
            except Exception as e:
                logger.error(f"Flow execution error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Flow execution failed: {str(e)}"
                )
        else:
            # LangFlow not available - return simulated response
            logger.warning(
                "LangFlow not available. Returning simulated response. "
                "Install langflow package to enable real flow execution."
            )
            result = {
                "status": "simulated",
                "output": f"Simulated response to: {user_input}",
                "flow_name": flow_file.filename,
                "note": "LangFlow not installed. This is a simulated response.",
                "warning": "Install langflow package for real flow execution"
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run flow: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "langflow_available": LANGFLOW_AVAILABLE,
        "flows_directory": str(FLOWS_DIR),
        "flows_count": len(list(FLOWS_DIR.glob("*.json")))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
