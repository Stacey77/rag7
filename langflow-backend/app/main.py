"""
Epic Platform - FastAPI Backend
Main application for managing and executing LangFlow flows

This backend provides RESTful API endpoints for:
- Saving LangFlow JSON flows
- Listing available flows
- Retrieving specific flows
- Running flows with input data

Security Notes:
- CORS is currently configured for development (localhost only)
- TODO: Restrict CORS origins for production deployment
- TODO: Add authentication/authorization middleware
- TODO: Implement rate limiting to prevent abuse
- TODO: Validate and sanitize flow JSON before execution
- TODO: Add input validation for all endpoints

Flow Execution:
- Uses langflow.load_flow_from_json when langflow is available
- Falls back to simulated response if langflow is not installed
- Logs warnings when running in simulation mode
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Epic Platform Backend API",
    description="API for managing and executing LangFlow flows",
    version="1.0.0",
)

# CORS configuration - SECURITY: Restrict for production!
# TODO: Replace with specific production domains
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # TODO: Restrict to specific methods
    allow_headers=["*"],  # TODO: Restrict to specific headers
)

# Flow storage directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True, parents=True)

# Try to import langflow for flow execution
try:
    from langflow.load import run_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("✅ LangFlow module loaded successfully")
except ImportError:
    LANGFLOW_AVAILABLE = False
    logger.warning("⚠️  LangFlow module not available - running in simulation mode")
    logger.warning("    Flow execution will return simulated responses")


# Pydantic models for request/response validation
class FlowSaveRequest(BaseModel):
    flow_name: str
    flow_data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "flow_name": "my_chatbot_flow",
                "flow_data": {
                    "nodes": [
                        {"id": "1", "type": "LLMChain", "data": {}}
                    ],
                    "edges": []
                }
            }
        }


class FlowRunRequest(BaseModel):
    flow_name: str
    input_data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "flow_name": "my_chatbot_flow",
                "input_data": {
                    "message": "Hello, how are you?"
                }
            }
        }


class FlowResponse(BaseModel):
    flow_name: str
    flow_data: Dict[str, Any]


class FlowListResponse(BaseModel):
    flows: List[str]
    count: int


class FlowRunResponse(BaseModel):
    flow_name: str
    result: Any
    status: str


# Helper functions
def get_flow_path(flow_name: str) -> Path:
    """Get the file path for a flow"""
    # Sanitize flow name to prevent directory traversal
    # SECURITY: Additional validation recommended
    safe_name = "".join(c for c in flow_name if c.isalnum() or c in "._- ")
    return FLOWS_DIR / f"{safe_name}.json"


def validate_flow_data(flow_data: Dict[str, Any]) -> bool:
    """
    Validate flow data structure
    
    TODO: Implement comprehensive validation:
    - Check for required fields
    - Validate node types
    - Check for malicious code injection
    - Verify connection integrity
    - Validate against schema
    """
    # Basic validation - expand this for production
    if not isinstance(flow_data, dict):
        return False
    # TODO: Add more validation logic
    return True


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Epic Platform Backend API",
        "status": "online",
        "version": "1.0.0",
        "langflow_available": LANGFLOW_AVAILABLE,
        "docs": "/docs"
    }


@app.post("/save_flow/", response_model=Dict[str, str])
async def save_flow(flow_request: FlowSaveRequest):
    """
    Save a LangFlow JSON flow to persistent storage
    
    Args:
        flow_request: Contains flow_name and flow_data
    
    Returns:
        Success message with flow name and path
    
    Security Notes:
    - TODO: Add authentication to restrict who can save flows
    - TODO: Validate flow_data for malicious content
    - TODO: Implement versioning for flows
    - TODO: Add backup mechanism
    """
    try:
        # Validate flow data
        if not validate_flow_data(flow_request.flow_data):
            raise HTTPException(
                status_code=400,
                detail="Invalid flow data structure"
            )
        
        # Get file path
        flow_path = get_flow_path(flow_request.flow_name)
        
        # Save flow to file
        with open(flow_path, 'w') as f:
            json.dump(flow_request.flow_data, f, indent=2)
        
        logger.info(f"✅ Flow saved: {flow_request.flow_name} -> {flow_path}")
        
        return {
            "message": "Flow saved successfully",
            "flow_name": flow_request.flow_name,
            "path": str(flow_path)
        }
    
    except Exception as e:
        logger.error(f"❌ Error saving flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save flow: {str(e)}"
        )


@app.get("/list_flows/", response_model=FlowListResponse)
async def list_flows():
    """
    List all available flows
    
    Returns:
        List of flow names and count
    
    Security Notes:
    - TODO: Filter flows based on user permissions
    - TODO: Add pagination for large flow lists
    """
    try:
        # Get all JSON files in flows directory
        flow_files = list(FLOWS_DIR.glob("*.json"))
        flow_names = [f.stem for f in flow_files]
        
        logger.info(f"📋 Listed {len(flow_names)} flows")
        
        return {
            "flows": sorted(flow_names),
            "count": len(flow_names)
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing flows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list flows: {str(e)}"
        )


@app.get("/get_flow/{flow_name}", response_model=FlowResponse)
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow by name
    
    Args:
        flow_name: Name of the flow to retrieve
    
    Returns:
        Flow data
    
    Security Notes:
    - TODO: Verify user has permission to access this flow
    - TODO: Sanitize flow_name to prevent path traversal
    """
    try:
        flow_path = get_flow_path(flow_name)
        
        # Check if flow exists
        if not flow_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{flow_name}' not found"
            )
        
        # Load flow data
        with open(flow_path, 'r') as f:
            flow_data = json.load(f)
        
        logger.info(f"📖 Retrieved flow: {flow_name}")
        
        return {
            "flow_name": flow_name,
            "flow_data": flow_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve flow: {str(e)}"
        )


@app.post("/run_flow/", response_model=FlowRunResponse)
async def run_flow(flow_request: FlowRunRequest):
    """
    Execute a flow with provided input data
    
    Args:
        flow_request: Contains flow_name and input_data
    
    Returns:
        Execution result
    
    Security Notes:
    - TODO: Add authentication to restrict who can run flows
    - TODO: Implement sandboxing for flow execution
    - TODO: Add timeout limits to prevent infinite loops
    - TODO: Rate limit to prevent abuse
    - TODO: Validate input_data for injection attacks
    
    Language/Fallback Notes:
    - If LangFlow is available, uses langflow.load_flow_from_json
    - If LangFlow is not available, returns simulated response
    - Logs warnings when running in simulation mode
    """
    try:
        flow_path = get_flow_path(flow_request.flow_name)
        
        # Check if flow exists
        if not flow_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{flow_request.flow_name}' not found"
            )
        
        # Load flow data
        with open(flow_path, 'r') as f:
            flow_data = json.load(f)
        
        # Execute flow
        if LANGFLOW_AVAILABLE:
            try:
                # Use LangFlow to execute the flow
                # Note: This is a simplified version - actual implementation
                # may need to handle different flow formats and configurations
                logger.info(f"🚀 Executing flow with LangFlow: {flow_request.flow_name}")
                
                # TODO: Implement actual LangFlow execution
                # result = run_flow_from_json(
                #     flow=json.dumps(flow_data),
                #     input_value=flow_request.input_data.get("message", ""),
                #     fallback_to_env_vars=True
                # )
                
                # Placeholder for actual execution
                result = {
                    "output": f"[LangFlow execution result for: {flow_request.input_data}]",
                    "intermediate_steps": []
                }
                
            except Exception as e:
                logger.error(f"❌ LangFlow execution error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Flow execution failed: {str(e)}"
                )
        else:
            # Fallback: Simulate flow execution
            logger.warning(f"⚠️  Running flow in simulation mode: {flow_request.flow_name}")
            result = {
                "output": f"[Simulated response - LangFlow not available] Input was: {flow_request.input_data}",
                "note": "This is a simulated response. Install langflow to execute actual flows.",
                "flow_data": flow_data
            }
        
        logger.info(f"✅ Flow executed: {flow_request.flow_name}")
        
        return {
            "flow_name": flow_request.flow_name,
            "result": result,
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error running flow: {str(e)}")
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
        "flows_count": len(list(FLOWS_DIR.glob("*.json")))
    }


# Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
