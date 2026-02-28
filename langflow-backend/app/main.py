"""
LangFlow Backend API - FastAPI Application

This backend provides endpoints for managing and executing LangFlow flows.

Security Notes:
- CORS is configured for development (localhost origins)
- For production, restrict CORS origins to specific domains
- Add authentication/authorization before production deployment
- Validate all flow JSON schemas before execution
- Consider rate limiting for API endpoints
- Implement proper error handling and logging

Validation Notes:
- Flow JSON should be validated against a schema
- User inputs should be sanitized
- File uploads should be size-limited
- Flow execution should have timeouts
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Backend API",
    description="API for managing and executing LangFlow flows",
    version="1.0.0",
)

# CORS Configuration - DEVELOPMENT ONLY
# TODO: For production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flows directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True)

# Check if langflow is available
LANGFLOW_AVAILABLE = False
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("✅ LangFlow module successfully imported")
except ImportError as e:
    logger.warning(f"⚠️  LangFlow module not available: {e}")
    logger.warning("API will run in simulation mode")


# Pydantic models
class FlowResponse(BaseModel):
    """Response model for flow operations"""
    flow_name: str
    message: str
    timestamp: str


class FlowListItem(BaseModel):
    """Model for flow list item"""
    name: str
    created: str
    size: int


class FlowRunResult(BaseModel):
    """Model for flow execution result"""
    flow_name: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    simulated: bool = False


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LangFlow Backend API",
        "version": "1.0.0",
        "langflow_available": LANGFLOW_AVAILABLE,
        "endpoints": {
            "docs": "/docs",
            "save_flow": "POST /save_flow/",
            "list_flows": "GET /list_flows/",
            "get_flow": "GET /get_flow/{flow_name}",
            "run_flow": "POST /run_flow/",
        }
    }


@app.post("/save_flow/", response_model=FlowResponse)
async def save_flow(
    flow_name: str = Form(...),
    flow_json: UploadFile = File(...)
):
    """
    Save a LangFlow flow definition
    
    Args:
        flow_name: Name for the flow (without .json extension)
        flow_json: JSON file containing the flow definition
    
    Returns:
        FlowResponse with save confirmation
    
    Security Considerations:
    - Validate flow_name to prevent directory traversal
    - Limit file size to prevent DoS
    - Validate JSON schema before saving
    """
    # Validate flow name (prevent directory traversal)
    if "/" in flow_name or "\\" in flow_name or ".." in flow_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid flow name. Must not contain path separators."
        )
    
    # Ensure .json extension
    if not flow_name.endswith(".json"):
        flow_name = f"{flow_name}.json"
    
    try:
        # Read and validate JSON
        content = await flow_json.read()
        flow_data = json.loads(content)
        
        # Save to flows directory
        flow_path = FLOWS_DIR / flow_name
        with open(flow_path, "w") as f:
            json.dump(flow_data, f, indent=2)
        
        logger.info(f"Saved flow: {flow_name}")
        
        return FlowResponse(
            flow_name=flow_name,
            message=f"Flow '{flow_name}' saved successfully",
            timestamp=datetime.utcnow().isoformat()
        )
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format"
        )
    except Exception as e:
        logger.error(f"Error saving flow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save flow: {str(e)}"
        )


@app.get("/list_flows/", response_model=List[FlowListItem])
async def list_flows():
    """
    List all saved flows
    
    Returns:
        List of FlowListItem objects with flow metadata
    """
    try:
        flows = []
        for flow_path in FLOWS_DIR.glob("*.json"):
            stat = flow_path.stat()
            flows.append(FlowListItem(
                name=flow_path.name,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                size=stat.st_size
            ))
        
        # Sort by creation time (newest first)
        flows.sort(key=lambda x: x.created, reverse=True)
        
        logger.info(f"Listed {len(flows)} flows")
        return flows
    
    except Exception as e:
        logger.error(f"Error listing flows: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list flows: {str(e)}"
        )


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow definition
    
    Args:
        flow_name: Name of the flow to retrieve
    
    Returns:
        Flow JSON definition
    
    Security Considerations:
    - Validate flow_name to prevent directory traversal
    """
    # Validate flow name
    if "/" in flow_name or "\\" in flow_name or ".." in flow_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid flow name"
        )
    
    # Ensure .json extension
    if not flow_name.endswith(".json"):
        flow_name = f"{flow_name}.json"
    
    flow_path = FLOWS_DIR / flow_name
    
    if not flow_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Flow '{flow_name}' not found"
        )
    
    try:
        with open(flow_path, "r") as f:
            flow_data = json.load(f)
        
        logger.info(f"Retrieved flow: {flow_name}")
        return flow_data
    
    except Exception as e:
        logger.error(f"Error retrieving flow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve flow: {str(e)}"
        )


@app.post("/run_flow/", response_model=FlowRunResult)
async def run_flow(
    flow_name: str = Form(...),
    user_input: str = Form(...),
    flow_json: Optional[UploadFile] = File(None)
):
    """
    Execute a flow with user input
    
    Args:
        flow_name: Name of the flow to execute
        user_input: Input text for the flow
        flow_json: Optional flow JSON (uses saved flow if not provided)
    
    Returns:
        FlowRunResult with execution results
    
    Security Considerations:
    - Implement execution timeouts
    - Validate and sanitize user_input
    - Rate limit this endpoint
    - Monitor resource usage during execution
    
    Note:
    - If langflow module is unavailable, returns simulated response
    """
    # Validate inputs
    if not user_input or user_input.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="user_input is required and cannot be empty"
        )
    
    try:
        # Get flow data
        if flow_json:
            # Use uploaded flow
            content = await flow_json.read()
            flow_data = json.loads(content)
            logger.info(f"Using uploaded flow for execution")
        else:
            # Load saved flow
            if "/" in flow_name or "\\" in flow_name or ".." in flow_name:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid flow name"
                )
            
            if not flow_name.endswith(".json"):
                flow_name = f"{flow_name}.json"
            
            flow_path = FLOWS_DIR / flow_name
            
            if not flow_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Flow '{flow_name}' not found"
                )
            
            with open(flow_path, "r") as f:
                flow_data = json.load(f)
            
            logger.info(f"Loaded flow from: {flow_name}")
        
        # Execute flow if langflow is available
        if LANGFLOW_AVAILABLE:
            try:
                # Load and run the flow
                flow = load_flow_from_json(flow_data)
                result = flow(user_input)
                
                logger.info(f"Flow executed successfully: {flow_name}")
                
                return FlowRunResult(
                    flow_name=flow_name,
                    success=True,
                    result={"output": result},
                    simulated=False
                )
            
            except Exception as e:
                logger.error(f"Flow execution error: {e}")
                return FlowRunResult(
                    flow_name=flow_name,
                    success=False,
                    error=str(e),
                    simulated=False
                )
        else:
            # Simulated response when langflow is not available
            logger.warning(f"Running in simulation mode for flow: {flow_name}")
            
            return FlowRunResult(
                flow_name=flow_name,
                success=True,
                result={
                    "output": f"[SIMULATED] Processed input: '{user_input}'",
                    "message": "LangFlow module not available. This is a simulated response.",
                    "flow_name": flow_name,
                    "nodes_executed": len(flow_data.get("nodes", [])) if isinstance(flow_data, dict) else 0
                },
                simulated=True
            )
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format in flow data"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running flow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run flow: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "langflow_available": LANGFLOW_AVAILABLE,
        "flows_directory": str(FLOWS_DIR),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
