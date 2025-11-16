"""
Epic Platform Backend - FastAPI Server

This backend provides flow management and execution capabilities for the Epic Platform.

SECURITY WARNINGS:
- NO AUTHENTICATION: All endpoints are open and unauthenticated (dev only!)
- NO AUTHORIZATION: No role-based access control
- NO FLOW VALIDATION: Uploaded flows are not validated or sandboxed
- ARBITRARY CODE EXECUTION: User flows can execute arbitrary code
- WIDE OPEN CORS: Configured for localhost development only

PRODUCTION RECOMMENDATIONS:
1. Add JWT/OAuth authentication to all endpoints
2. Implement flow JSON schema validation before execution
3. Sandbox flow execution in isolated containers/workers
4. Restrict CORS to production domains only
5. Move flow storage to database with versioning and access controls
6. Add audit logging for all flow operations
7. Implement rate limiting and request validation
8. Use secrets management for sensitive configuration

LANGFLOW FALLBACK:
If langflow is not available, /run_flow/ will return simulated responses and log warnings.
This allows the backend to run in environments without langflow installed.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import langflow, but gracefully handle if not available
LANGFLOW_AVAILABLE = False
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("✓ LangFlow is available for flow execution")
except ImportError as e:
    logger.warning(f"⚠️  LangFlow not available: {e}")
    logger.warning("⚠️  Flow execution will return simulated responses")

# Initialize FastAPI app
app = FastAPI(
    title="Epic Platform Backend API",
    description="Flow management and execution API for Epic Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# SECURITY WARNING: Wide open CORS for development!
# Production: Restrict to specific domains only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flow storage directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(parents=True, exist_ok=True)


# Models
class FlowInfo(BaseModel):
    """Flow metadata"""
    name: str
    size: int
    created: str
    modified: str


class FlowExecutionResult(BaseModel):
    """Result of flow execution"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    simulated: bool = False
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    langflow_available: bool
    flows_directory: str
    timestamp: str


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service status and configuration
    """
    return HealthResponse(
        status="healthy",
        langflow_available=LANGFLOW_AVAILABLE,
        flows_directory=str(FLOWS_DIR),
        timestamp=datetime.utcnow().isoformat()
    )


# Save flow endpoint
@app.post("/save_flow/")
async def save_flow(flow: UploadFile = File(...)):
    """
    Save a flow JSON file to the flows directory
    
    SECURITY WARNING: No validation is performed on uploaded files!
    Production requirements:
    - Validate JSON schema
    - Check file size limits
    - Scan for malicious content
    - Add authentication and authorization
    - Implement version control
    """
    try:
        # Read file content
        content = await flow.read()
        
        # Validate it's valid JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        # Generate safe filename
        filename = flow.filename
        if not filename or not filename.endswith('.json'):
            filename = f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save to flows directory
        flow_path = FLOWS_DIR / filename
        with open(flow_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Flow saved: {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "path": str(flow_path),
            "message": f"Flow '{filename}' saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save flow: {str(e)}")


# List flows endpoint
@app.get("/list_flows/", response_model=List[FlowInfo])
async def list_flows():
    """
    List all saved flow files
    Returns metadata for each flow
    """
    try:
        flows = []
        
        for flow_file in FLOWS_DIR.glob("*.json"):
            stat = flow_file.stat()
            flows.append(FlowInfo(
                name=flow_file.name,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
            ))
        
        # Sort by modified time, newest first
        flows.sort(key=lambda x: x.modified, reverse=True)
        
        return flows
        
    except Exception as e:
        logger.error(f"Error listing flows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list flows: {str(e)}")


# Get specific flow endpoint
@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow by name
    Returns the flow JSON content
    """
    try:
        # Validate filename to prevent path traversal
        if ".." in flow_name or "/" in flow_name or "\\" in flow_name:
            raise HTTPException(status_code=400, detail="Invalid flow name")
        
        flow_path = FLOWS_DIR / flow_name
        
        if not flow_path.exists():
            raise HTTPException(status_code=404, detail=f"Flow '{flow_name}' not found")
        
        with open(flow_path, 'r') as f:
            flow_data = json.load(f)
        
        return {
            "success": True,
            "flow_name": flow_name,
            "flow_data": flow_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve flow: {str(e)}")


# Run flow endpoint
@app.post("/run_flow/", response_model=FlowExecutionResult)
async def run_flow(
    flow_file: UploadFile = File(...),
    user_input: str = Form(...)
):
    """
    Execute a flow with user input
    
    SECURITY WARNING: This executes arbitrary code from user-provided flows!
    Production requirements:
    - Validate flow JSON schema
    - Sandbox execution in isolated containers
    - Implement strict tool whitelisting
    - Add timeout and resource limits
    - Audit log all executions
    - Require authentication and authorization
    
    FALLBACK BEHAVIOR:
    If LangFlow is not available, returns a simulated response with a warning.
    """
    try:
        # Read flow content
        content = await flow_file.read()
        
        # Validate JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON flow file")
        
        # If LangFlow is available, execute the flow
        if LANGFLOW_AVAILABLE:
            try:
                # Save to temporary file
                temp_flow_path = FLOWS_DIR / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(temp_flow_path, 'wb') as f:
                    f.write(content)
                
                # Load and run flow
                logger.info(f"Executing flow with input: {user_input}")
                flow = load_flow_from_json(str(temp_flow_path))
                result = flow(user_input)
                
                # Clean up temp file
                if temp_flow_path.exists():
                    temp_flow_path.unlink()
                
                logger.info(f"Flow executed successfully: {result}")
                
                return FlowExecutionResult(
                    success=True,
                    result=result,
                    simulated=False,
                    message="Flow executed successfully"
                )
                
            except Exception as e:
                logger.error(f"Flow execution failed: {e}")
                # Return simulated response on execution error
                return FlowExecutionResult(
                    success=False,
                    result=None,
                    error=str(e),
                    simulated=True,
                    message="Flow execution failed, returning simulated response"
                )
        
        # LangFlow not available - return simulated response
        else:
            logger.warning(f"Simulated flow execution - LangFlow not available")
            logger.warning(f"User input: {user_input}")
            
            simulated_result = {
                "response": f"[SIMULATED] Processed your input: '{user_input}'",
                "flow_name": flow_file.filename,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "This is a simulated response. Install langflow for real execution."
            }
            
            return FlowExecutionResult(
                success=True,
                result=simulated_result,
                simulated=True,
                message="LangFlow not available - returning simulated response"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in run_flow endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute flow: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Epic Platform Backend API",
        "version": "0.1.0",
        "status": "running",
        "langflow_available": LANGFLOW_AVAILABLE,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "save_flow": "POST /save_flow/",
            "list_flows": "GET /list_flows/",
            "get_flow": "GET /get_flow/{flow_name}",
            "run_flow": "POST /run_flow/"
        },
        "security_warning": "This API has NO authentication - for development only!"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
