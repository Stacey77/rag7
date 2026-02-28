"""
LangFlow Backend - FastAPI Application

This backend provides endpoints for managing and executing LangFlow flows.

SECURITY WARNINGS:
- This is a DEVELOPMENT scaffold only
- NO authentication implemented
- NO flow validation
- NO sandboxed execution
- CORS allows all localhost origins
- Flows execute with full system access
- DO NOT deploy to production without security hardening

Required for Production:
1. Add authentication (OAuth2, JWT, API keys)
2. Validate flows before execution (check for malicious code)
3. Sandbox flow execution (Docker, gVisor, resource limits)
4. Restrict CORS to specific domains
5. Implement rate limiting
6. Add input validation and sanitization
7. Enable logging and monitoring
8. Use HTTPS/TLS
9. Implement proper error handling
10. Regular security audits
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Backend API",
    description="API for managing and executing LangFlow flows",
    version="1.0.0"
)

# SECURITY WARNING: CORS is wide open for localhost development
# In production, restrict to specific domains:
# allow_origins=["https://yourdomain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flow storage directory
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Try to import langflow - graceful fallback if not available
try:
    from langflow.load import run_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("LangFlow library loaded successfully")
except ImportError:
    LANGFLOW_AVAILABLE = False
    logger.warning(
        "LangFlow library not available - will use simulated responses. "
        "This is acceptable for frontend development but not for production."
    )


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "LangFlow Backend API",
        "langflow_available": LANGFLOW_AVAILABLE
    }


@app.post("/save_flow/")
async def save_flow(flow_file: UploadFile = File(...)):
    """
    Save an uploaded flow JSON file.
    
    SECURITY WARNING: No validation performed on uploaded flows.
    In production, validate flow structure and check for malicious code.
    """
    try:
        # Read file content
        content = await flow_file.read()
        
        # SECURITY WARNING: No validation performed
        # Production: Validate JSON structure, check for malicious code
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        # Save to flows directory
        filename = flow_file.filename
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        file_path = FLOWS_DIR / filename
        
        # SECURITY WARNING: No sanitization of filename
        # Production: Sanitize filename, check for path traversal
        with open(file_path, 'w') as f:
            json.dump(flow_data, f, indent=2)
        
        logger.info(f"Flow saved: {filename}")
        
        return {
            "status": "success",
            "filename": filename,
            "path": str(file_path)
        }
    
    except Exception as e:
        logger.error(f"Error saving flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving flow: {str(e)}")


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flow files.
    
    SECURITY WARNING: No authentication - anyone can list flows.
    In production, require authentication and filter by user permissions.
    """
    try:
        flows = [f.name for f in FLOWS_DIR.glob("*.json")]
        return {"flows": flows}
    
    except Exception as e:
        logger.error(f"Error listing flows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing flows: {str(e)}")


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow's content.
    
    SECURITY WARNING: No authentication or authorization.
    In production, verify user has permission to access this flow.
    """
    try:
        # SECURITY WARNING: No path traversal protection
        # Production: Sanitize flow_name, prevent directory traversal
        if not flow_name.endswith('.json'):
            flow_name = f"{flow_name}.json"
        
        file_path = FLOWS_DIR / flow_name
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Flow not found: {flow_name}")
        
        with open(file_path, 'r') as f:
            flow_data = json.load(f)
        
        return {
            "filename": flow_name,
            "content": flow_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving flow: {str(e)}")


@app.post("/run_flow/")
async def run_flow(
    flow_file: UploadFile = File(...),
    user_input: str = Form(...)
):
    """
    Execute a flow with user input.
    
    SECURITY WARNINGS:
    - No authentication required
    - No flow validation performed
    - No sandboxing - flows execute with full system access
    - No resource limits (CPU, memory, time)
    - No input sanitization
    
    Production Requirements:
    1. Authenticate user
    2. Validate flow structure
    3. Sandbox execution (Docker container, gVisor, resource limits)
    4. Sanitize user_input
    5. Set execution timeout
    6. Monitor resource usage
    7. Log all executions
    8. Implement rate limiting
    """
    try:
        # Read and parse flow file
        content = await flow_file.read()
        
        # SECURITY WARNING: No validation of flow structure
        # Production: Validate flow, check for malicious components
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        # Save temporarily for execution
        temp_path = FLOWS_DIR / f"temp_{flow_file.filename}"
        with open(temp_path, 'w') as f:
            json.dump(flow_data, f)
        
        # Execute flow or return simulated response
        if LANGFLOW_AVAILABLE:
            try:
                # SECURITY WARNING: No sandboxing, no timeout, full system access
                # Production: Execute in isolated container with resource limits
                logger.info(f"Executing flow with input: {user_input[:50]}...")
                
                result = run_flow_from_json(
                    flow=str(temp_path),
                    input_value=user_input,
                    fallback_to_env_vars=True
                )
                
                # Clean up temp file
                temp_path.unlink(missing_ok=True)
                
                return {
                    "status": "success",
                    "result": str(result),
                    "simulated": False
                }
            
            except Exception as e:
                # Clean up temp file
                temp_path.unlink(missing_ok=True)
                logger.error(f"Error executing flow: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error executing flow: {str(e)}"
                )
        else:
            # Simulated response for development when langflow not available
            logger.warning(
                "Using simulated response - LangFlow library not available. "
                "This is acceptable for frontend development."
            )
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            # Return simulated response
            simulated_result = (
                f"Simulated response: Hello! This is a simulated flow response for "
                f"development purposes. Your input was: '{user_input}'. "
                f"In production, this would execute the actual LangFlow flow."
            )
            
            return {
                "status": "success",
                "result": simulated_result,
                "simulated": True,
                "warning": "LangFlow library not available - using simulated response"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in run_flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running flow: {str(e)}")


@app.get("/health")
async def detailed_health():
    """Detailed health check with system information."""
    return {
        "status": "healthy",
        "langflow_available": LANGFLOW_AVAILABLE,
        "flows_directory": str(FLOWS_DIR),
        "flows_count": len(list(FLOWS_DIR.glob("*.json")))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
