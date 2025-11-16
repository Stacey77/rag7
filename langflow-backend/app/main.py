"""
Epic Platform - FastAPI Backend for LangFlow Operations

This backend provides RESTful API endpoints to manage and execute LangFlow flows.

Endpoints:
- POST /save_flow/ - Save a LangFlow JSON flow
- GET /list_flows/ - List all saved flows
- GET /get_flow/{flow_name} - Retrieve a specific flow
- POST /run_flow/ - Execute a flow with user input

Security Notes:
- CORS is enabled for development. Restrict origins in production.
- Flow validation should be added before production deployment.
- Consider adding authentication and authorization.
- Validate flow_data to prevent malicious JSON.
- Sanitize user inputs before executing flows.

Language Fallback:
- If langflow is not installed, the /run_flow/ endpoint returns a simulated response.
- A warning is logged when langflow import fails.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import langflow, gracefully handle if not available
LANGFLOW_AVAILABLE = False
try:
    from langflow.load import run_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("✅ LangFlow successfully imported")
except ImportError:
    logger.warning("⚠️  LangFlow not available. /run_flow/ will return simulated responses.")

# Initialize FastAPI app
app = FastAPI(
    title="Epic Platform - LangFlow Backend",
    description="RESTful API for managing and executing LangFlow flows",
    version="1.0.0",
)

# Configure CORS
# ⚠️ SECURITY: Restrict these origins in production
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flows storage directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic models
class FlowData(BaseModel):
    """Model for flow data"""
    flow_name: str = Field(..., description="Name of the flow")
    flow_data: Dict[str, Any] = Field(..., description="LangFlow JSON data")

class RunFlowRequest(BaseModel):
    """Model for running a flow"""
    flow_data: Dict[str, Any] = Field(..., description="LangFlow JSON data")
    user_input: str = Field(..., description="User input to pass to the flow")

class FlowResponse(BaseModel):
    """Model for flow response"""
    success: bool
    message: str
    data: Optional[Any] = None

# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Epic Platform - LangFlow Backend",
        "version": "1.0.0",
        "langflow_available": LANGFLOW_AVAILABLE,
    }

# Save Flow endpoint
@app.post("/save_flow/", response_model=FlowResponse)
async def save_flow(flow: FlowData):
    """
    Save a LangFlow JSON flow to disk
    
    Args:
        flow: FlowData containing flow_name and flow_data
    
    Returns:
        FlowResponse with success status and message
    
    Security Notes:
    - Validate flow_name to prevent path traversal attacks
    - Consider adding flow schema validation
    - Add authentication before production deployment
    """
    try:
        # Sanitize flow name (basic validation)
        flow_name = flow.flow_name.strip().replace("/", "_").replace("\\", "_")
        if not flow_name or flow_name.startswith("."):
            raise HTTPException(status_code=400, detail="Invalid flow name")
        
        # Save flow to file
        flow_path = FLOWS_DIR / f"{flow_name}.json"
        with open(flow_path, "w") as f:
            json.dump(flow.flow_data, f, indent=2)
        
        logger.info(f"✅ Flow saved: {flow_name}")
        return FlowResponse(
            success=True,
            message=f"Flow '{flow_name}' saved successfully",
            data={"flow_name": flow_name, "path": str(flow_path)}
        )
    
    except Exception as e:
        logger.error(f"❌ Error saving flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save flow: {str(e)}")

# List Flows endpoint
@app.get("/list_flows/", response_model=FlowResponse)
async def list_flows():
    """
    List all saved flows
    
    Returns:
        FlowResponse with list of flow names
    """
    try:
        flows = []
        for flow_file in FLOWS_DIR.glob("*.json"):
            flow_name = flow_file.stem
            flows.append({
                "name": flow_name,
                "path": str(flow_file),
                "size": flow_file.stat().st_size,
            })
        
        logger.info(f"📋 Listed {len(flows)} flows")
        return FlowResponse(
            success=True,
            message=f"Found {len(flows)} flows",
            data={"flows": flows, "count": len(flows)}
        )
    
    except Exception as e:
        logger.error(f"❌ Error listing flows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list flows: {str(e)}")

# Get Flow endpoint
@app.get("/get_flow/{flow_name}", response_model=FlowResponse)
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow by name
    
    Args:
        flow_name: Name of the flow to retrieve
    
    Returns:
        FlowResponse with flow data
    
    Security Notes:
    - Validate flow_name to prevent path traversal
    """
    try:
        # Sanitize flow name
        flow_name = flow_name.strip().replace("/", "_").replace("\\", "_")
        flow_path = FLOWS_DIR / f"{flow_name}.json"
        
        if not flow_path.exists():
            raise HTTPException(status_code=404, detail=f"Flow '{flow_name}' not found")
        
        with open(flow_path, "r") as f:
            flow_data = json.load(f)
        
        logger.info(f"📥 Retrieved flow: {flow_name}")
        return FlowResponse(
            success=True,
            message=f"Flow '{flow_name}' retrieved successfully",
            data={"flow_name": flow_name, "flow_data": flow_data}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve flow: {str(e)}")

# Run Flow endpoint
@app.post("/run_flow/", response_model=FlowResponse)
async def run_flow(request: RunFlowRequest):
    """
    Execute a LangFlow flow with user input
    
    Args:
        request: RunFlowRequest containing flow_data and user_input
    
    Returns:
        FlowResponse with execution result
    
    Security Notes:
    - Validate flow_data structure
    - Sanitize user_input to prevent injection attacks
    - Consider rate limiting to prevent abuse
    - Add timeout to prevent long-running flows
    
    Language Fallback:
    - If langflow is not installed, returns a simulated response
    """
    try:
        if not LANGFLOW_AVAILABLE:
            # Simulated response when LangFlow is not available
            logger.warning("⚠️  LangFlow not available, returning simulated response")
            return FlowResponse(
                success=True,
                message="Flow executed (simulated - LangFlow not installed)",
                data={
                    "result": f"Simulated response to: {request.user_input}",
                    "note": "Install langflow to execute real flows",
                    "user_input": request.user_input,
                }
            )
        
        # Execute flow with LangFlow
        # Note: This is a simplified example. Adjust based on your LangFlow version
        logger.info(f"🚀 Executing flow with input: {request.user_input[:50]}...")
        
        try:
            # Execute the flow
            result = run_flow_from_json(
                flow=json.dumps(request.flow_data),
                input_value=request.user_input,
                fallback_to_env_vars=True,
            )
            
            logger.info("✅ Flow executed successfully")
            return FlowResponse(
                success=True,
                message="Flow executed successfully",
                data={
                    "result": result,
                    "user_input": request.user_input,
                }
            )
        
        except Exception as langflow_error:
            logger.error(f"❌ LangFlow execution error: {str(langflow_error)}")
            return FlowResponse(
                success=False,
                message=f"Flow execution failed: {str(langflow_error)}",
                data={"error": str(langflow_error)}
            )
    
    except Exception as e:
        logger.error(f"❌ Error running flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "langflow_available": LANGFLOW_AVAILABLE,
        "flows_directory": str(FLOWS_DIR),
        "flows_count": len(list(FLOWS_DIR.glob("*.json"))),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
