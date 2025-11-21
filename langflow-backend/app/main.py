"""
Ragamuffin Backend - FastAPI Application

This backend provides flow management and execution endpoints for the Ragamuffin platform.

SECURITY WARNINGS:
- This is a development scaffold. DO NOT use in production without proper security!
- Add authentication and authorization before production deployment
- Validate all flow JSON structures before execution
- Sandbox flow execution to prevent code injection
- Restrict available tools and modules in flows
- Implement rate limiting and input validation
- Use environment variables for sensitive configuration
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="Flow management and execution API for Ragamuffin AI platform",
    version="0.1.0"
)

# SECURITY WARNING: This CORS configuration is permissive for local development only!
# In production, replace with specific allowed origins and implement proper CSRF protection.
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

# Flows directory - mounted as volume in Docker
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Ragamuffin Backend API",
        "version": "0.1.0"
    }


@app.post("/save_flow/")
async def save_flow(file: UploadFile = File(...)):
    """
    Save a flow JSON file to the flows directory.
    
    SECURITY WARNINGS:
    - Validate JSON structure before saving
    - Implement file size limits
    - Sanitize filenames to prevent path traversal
    - Add authentication in production
    - Consider encrypting sensitive flow data
    """
    try:
        # SECURITY: Validate filename is present
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        # SECURITY: Validate file extension (basic check)
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Only JSON files are accepted"
            )
        
        # SECURITY: Sanitize filename to prevent path traversal
        # Path().name automatically extracts just the basename, removing any directory components
        safe_filename = Path(file.filename).name
        
        # Additional validation: ensure no hidden files or empty names
        if not safe_filename or safe_filename.startswith('.'):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        
        # Read and validate JSON content
        content = await file.read()
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format"
            )
        
        # Save file to flows directory
        file_path = FLOWS_DIR / safe_filename
        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=2)
        
        logger.info(f"Flow saved: {safe_filename}")
        return {
            "status": "success",
            "filename": safe_filename,
            "path": str(file_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving flow: {str(e)}")


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flow files.
    
    SECURITY WARNINGS:
    - Add authentication in production
    - Implement pagination for large lists
    - Consider access control per flow
    """
    try:
        flow_files = [
            f.name for f in FLOWS_DIR.glob("*.json")
            if f.is_file()
        ]
        
        return {
            "status": "success",
            "flows": sorted(flow_files),
            "count": len(flow_files)
        }
    
    except Exception as e:
        logger.error(f"Error listing flows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing flows: {str(e)}")


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow by name.
    
    SECURITY WARNINGS:
    - Add authentication in production
    - Validate flow_name to prevent path traversal
    - Implement access control per flow
    """
    try:
        # SECURITY: Sanitize filename
        # Path().name automatically extracts just the basename, removing any directory components
        safe_filename = Path(flow_name).name
        
        # Additional validation: ensure no hidden files or empty names
        if not safe_filename or safe_filename.startswith('.'):
            raise HTTPException(
                status_code=400,
                detail="Invalid flow name"
            )
        
        file_path = FLOWS_DIR / safe_filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{flow_name}' not found"
            )
        
        with open(file_path, "r") as f:
            flow_data = json.load(f)
        
        return {
            "status": "success",
            "flow_name": safe_filename,
            "flow_data": flow_data
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
    
    CRITICAL SECURITY WARNINGS:
    - This endpoint executes arbitrary code from flow definitions!
    - NEVER use in production without proper sandboxing
    - Validate flow structure before execution
    - Restrict available tools and modules
    - Implement resource limits (CPU, memory, time)
    - Add authentication and authorization
    - Log all executions for audit
    - Consider using a separate sandboxed environment
    
    This implementation attempts to use langflow if available, but falls back
    to a simulated response if langflow is not installed. This allows the
    backend to run without langflow for testing the API structure.
    """
    try:
        # Read flow file content
        content = await flow_file.read()
        
        # Validate JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid flow JSON format"
            )
        
        # SECURITY: Basic validation of flow structure
        # In production, implement comprehensive validation
        if not isinstance(flow_data, dict):
            raise HTTPException(
                status_code=400,
                detail="Flow must be a JSON object"
            )
        
        # Attempt to import and use langflow
        try:
            from langflow.load import load_flow_from_json
            
            # SECURITY WARNING: This executes arbitrary code from the flow!
            # In production, this MUST be sandboxed and validated!
            
            # Save temporary flow file
            temp_flow_path = FLOWS_DIR / f"temp_{flow_file.filename}"
            with open(temp_flow_path, "w") as f:
                json.dump(flow_data, f)
            
            try:
                # Load and execute flow
                flow = load_flow_from_json(str(temp_flow_path))
                result = flow(user_input)
                
                # Clean up temp file
                temp_flow_path.unlink()
                
                # SECURITY: Ensure result is JSON-serializable
                # This prevents leaking non-serializable objects
                serializable_result = {
                    "status": "success",
                    "result": str(result) if result is not None else None,
                    "flow_name": flow_file.filename,
                    "user_input": user_input,
                    "execution_mode": "langflow"
                }
                
                return serializable_result
            
            except Exception as flow_error:
                # Clean up temp file
                if temp_flow_path.exists():
                    temp_flow_path.unlink()
                
                logger.error(f"Flow execution error: {str(flow_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Flow execution failed: {str(flow_error)}"
                )
        
        except ImportError:
            # LangFlow not available - return simulated response
            logger.warning(
                "LangFlow not available. Returning simulated response. "
                "Install langflow to enable real flow execution."
            )
            
            return {
                "status": "success",
                "result": f"[SIMULATED] Processed input: '{user_input}' using flow '{flow_file.filename}'",
                "flow_name": flow_file.filename,
                "user_input": user_input,
                "execution_mode": "simulated",
                "note": "LangFlow not installed. This is a simulated response. Install langflow package to enable real execution."
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running flow: {str(e)}"
        )


# Additional utility endpoints

@app.delete("/delete_flow/{flow_name}")
async def delete_flow(flow_name: str):
    """
    Delete a flow file.
    
    SECURITY WARNINGS:
    - Add authentication in production
    - Validate flow_name to prevent path traversal
    - Implement access control and audit logging
    """
    try:
        # SECURITY: Sanitize filename
        # Path().name automatically extracts just the basename, removing any directory components
        safe_filename = Path(flow_name).name
        
        # Additional validation: ensure no hidden files or empty names
        if not safe_filename or safe_filename.startswith('.'):
            raise HTTPException(
                status_code=400,
                detail="Invalid flow name"
            )
        
        file_path = FLOWS_DIR / safe_filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Flow '{flow_name}' not found"
            )
        
        file_path.unlink()
        logger.info(f"Flow deleted: {safe_filename}")
        
        return {
            "status": "success",
            "message": f"Flow '{flow_name}' deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting flow: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
