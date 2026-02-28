"""
Ragamuffin Backend API

FastAPI application for managing and executing LangFlow flows.

SECURITY NOTES:
- This is a development server. Do NOT use in production without proper security measures.
- All flows should be validated before execution to prevent code injection.
- Consider sandboxing flow execution in an isolated environment.
- Whitelist allowed tools and functions to prevent unauthorized operations.
- Add authentication (JWT/OAuth) before deploying to production.
- Use a database or S3 for production-grade persistence instead of filesystem.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="API for managing and executing LangFlow flows",
    version="1.0.0",
)

# SECURITY: Configure CORS for localhost development
# TODO: In production, restrict origins to specific domains
# TODO: Add authentication middleware (JWT/OAuth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for persisted flows
# SECURITY: Ensure this directory has proper permissions
# TODO: For production, use a database or S3 for flow storage
FLOWS_DIR = Path(os.getenv("FLOWS_DIR", "/app/flows"))
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Try to import langflow for flow execution
# If not available, we'll use a simulated response
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("LangFlow package is available for flow execution")
except ImportError:
    LANGFLOW_AVAILABLE = False
    logger.warning(
        "LangFlow package is not installed. /run_flow/ will return simulated responses. "
        "Install with: pip install langflow"
    )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Ragamuffin Backend",
        "langflow_available": LANGFLOW_AVAILABLE,
    }


@app.post("/save_flow/")
async def save_flow(flow_file: UploadFile = File(...)):
    """
    Save a flow JSON file to the flows directory.
    
    SECURITY NOTES:
    - Validate the JSON structure before saving
    - Sanitize the filename to prevent path traversal attacks
    - Consider scanning the flow for dangerous operations
    - In production, store flows in a database with proper access controls
    """
    # SECURITY: Validate file extension
    if not flow_file.filename or not flow_file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .json files are allowed.",
        )
    
    # SECURITY: Sanitize filename to prevent path traversal
    safe_filename = Path(flow_file.filename).name
    if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )
    
    try:
        content = await flow_file.read()
        
        # SECURITY: Validate JSON structure
        # TODO: Add schema validation for flow structure
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON content.",
            )
        
        # SECURITY: Basic validation - ensure it looks like a flow
        # TODO: Implement comprehensive flow validation
        # TODO: Check for dangerous nodes/operations
        # TODO: Whitelist allowed tools and integrations
        
        # Save the flow
        flow_path = FLOWS_DIR / safe_filename
        with open(flow_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved flow: {safe_filename}")
        return {"message": f"Flow '{safe_filename}' saved successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {e}")
        raise HTTPException(status_code=500, detail="Error saving flow")


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flows.
    
    SECURITY NOTES:
    - In production, implement pagination
    - Add access controls to filter flows by user/role
    """
    try:
        flows = [f.name for f in FLOWS_DIR.glob("*.json")]
        return {"flows": flows}
    except Exception as e:
        logger.error(f"Error listing flows: {e}")
        raise HTTPException(status_code=500, detail="Error listing flows")


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Get a specific flow by name.
    
    SECURITY NOTES:
    - Sanitize flow_name to prevent path traversal
    - In production, verify user has access to the flow
    """
    # SECURITY: Sanitize flow name
    safe_name = Path(flow_name).name
    if ".." in safe_name or "/" in safe_name or "\\" in safe_name:
        raise HTTPException(status_code=400, detail="Invalid flow name")
    
    flow_path = FLOWS_DIR / safe_name
    
    if not flow_path.exists():
        raise HTTPException(status_code=404, detail="Flow not found")
    
    try:
        with open(flow_path, "r") as f:
            flow_data = json.load(f)
        return {"flow_name": safe_name, "flow_data": flow_data}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing flow")
    except Exception as e:
        logger.error(f"Error getting flow: {e}")
        raise HTTPException(status_code=500, detail="Error getting flow")


@app.post("/run_flow/")
async def run_flow(
    flow_file: UploadFile = File(...),
    user_input: str = Form(...),
):
    """
    Execute a flow with user input.
    
    SECURITY NOTES:
    - CRITICAL: Running untrusted flows is a security risk!
    - Validate the flow before execution
    - Sandbox the execution environment
    - Whitelist allowed tools and integrations
    - Implement rate limiting
    - Add timeouts to prevent infinite loops
    - Monitor resource usage
    - Log all executions for auditing
    
    If langflow is not installed, returns a simulated response.
    """
    # SECURITY: Validate file
    if not flow_file.filename or not flow_file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .json files are allowed.",
        )
    
    try:
        content = await flow_file.read()
        
        # SECURITY: Validate JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")
        
        # SECURITY: Basic input validation
        # TODO: Implement input sanitization
        # TODO: Add input length limits
        if not user_input or len(user_input) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Invalid input. Input must be between 1 and 10000 characters.",
            )
        
        if LANGFLOW_AVAILABLE:
            # SECURITY: Execute in a sandboxed environment in production
            # TODO: Add timeout handling
            # TODO: Add resource limits
            # TODO: Run in isolated process/container
            try:
                flow = load_flow_from_json(flow_data)
                result = flow(user_input)
                logger.info(f"Flow executed successfully for input: {user_input[:50]}...")
                return {"result": str(result), "simulated": False}
            except Exception as e:
                logger.error(f"Error executing flow: {e}")
                raise HTTPException(status_code=500, detail=f"Flow execution error: {str(e)}")
        else:
            # Simulated response when langflow is not available
            logger.warning(
                "Returning simulated response - langflow is not installed. "
                "Install langflow for actual flow execution."
            )
            return {
                "result": f"[SIMULATED] Received input: '{user_input}'. "
                          f"LangFlow is not installed. Install with 'pip install langflow' "
                          f"for actual flow execution.",
                "simulated": True,
                "warning": "LangFlow is not installed. This is a simulated response.",
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in run_flow: {e}")
        raise HTTPException(status_code=500, detail="Error running flow")


# SECURITY: Add these endpoints before production deployment:
# TODO: POST /auth/login - User authentication
# TODO: POST /auth/refresh - Token refresh
# TODO: GET /flows/user/{user_id} - List flows by user
# TODO: DELETE /flow/{flow_name} - Delete flow with access control
# TODO: PUT /flow/{flow_name} - Update flow with validation
