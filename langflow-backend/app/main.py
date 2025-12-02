"""
FastAPI Backend for Ragamuffin - Flow Management and Execution
This API provides endpoints to save, list, retrieve, and run LangFlow JSON flows.

Security Notes:
- CORS is enabled for development with localhost origins
- For production: restrict CORS origins, add authentication, validate all inputs
- Flow validation: add JSON schema validation and sanitization
- File operations: implement proper error handling and path sanitization
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="API for managing and executing LangFlow agent flows",
    version="1.0.0"
)

# Configure CORS for development
# ⚠️ Security: Restrict these origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flows directory for persistence
FLOWS_DIR = Path("/app/flows")
FLOWS_DIR.mkdir(exist_ok=True)

# Attempt to import LangFlow functionality
LANGFLOW_AVAILABLE = False
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("✅ LangFlow imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ LangFlow import failed: {e}")
    logger.warning("Running in simulation mode - /run_flow/ will return simulated responses")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Ragamuffin Backend API",
        "status": "running",
        "langflow_available": LANGFLOW_AVAILABLE
    }


@app.post("/save_flow/")
async def save_flow(
    flow_name: str = Form(...),
    flow_json: UploadFile = File(...)
):
    """
    Save a LangFlow JSON flow definition to disk.
    
    Args:
        flow_name: Name to save the flow as (without .json extension)
        flow_json: JSON file containing the flow definition
    
    Returns:
        Success message with saved flow name
    
    Security Notes:
    - Validate flow_name to prevent path traversal attacks
    - Validate JSON structure before saving
    - Add authentication to restrict who can save flows
    """
    try:
        # Sanitize flow name (basic validation)
        # ⚠️ Security: Add more comprehensive validation
        flow_name = flow_name.strip().replace("/", "_").replace("\\", "_")
        
        if not flow_name:
            raise HTTPException(status_code=400, detail="Flow name cannot be empty")
        
        # Read and validate JSON
        content = await flow_json.read()
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Save to disk
        file_path = FLOWS_DIR / f"{flow_name}.json"
        with open(file_path, "w") as f:
            json.dump(flow_data, f, indent=2)
        
        logger.info(f"✅ Saved flow: {flow_name}")
        return {
            "message": "Flow saved successfully",
            "flow_name": flow_name,
            "path": str(file_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving flow: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving flow: {str(e)}")


@app.get("/list_flows/")
async def list_flows():
    """
    List all saved flow definitions.
    
    Returns:
        List of flow names (without .json extension)
    """
    try:
        flows = [
            f.stem for f in FLOWS_DIR.glob("*.json")
        ]
        flows.sort()
        
        logger.info(f"📋 Listed {len(flows)} flows")
        return {
            "flows": flows,
            "count": len(flows)
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing flows: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing flows: {str(e)}")


@app.get("/get_flow/{flow_name}")
async def get_flow(flow_name: str):
    """
    Retrieve a specific flow definition.
    
    Args:
        flow_name: Name of the flow to retrieve (without .json extension)
    
    Returns:
        Flow definition as JSON
    
    Security Notes:
    - Validate flow_name to prevent path traversal
    - Add authentication to restrict access
    """
    try:
        # Sanitize flow name
        # ⚠️ Security: Add more comprehensive validation
        flow_name = flow_name.strip().replace("/", "_").replace("\\", "_")
        
        file_path = FLOWS_DIR / f"{flow_name}.json"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Flow '{flow_name}' not found")
        
        with open(file_path, "r") as f:
            flow_data = json.load(f)
        
        logger.info(f"📖 Retrieved flow: {flow_name}")
        return {
            "flow_name": flow_name,
            "flow_data": flow_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving flow: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving flow: {str(e)}")


@app.post("/run_flow/")
async def run_flow(
    flow_json: UploadFile = File(...),
    user_input: str = Form(...)
):
    """
    Execute a LangFlow flow with user input.
    
    Args:
        flow_json: JSON file containing the flow definition
        user_input: User input to pass to the flow
    
    Returns:
        Flow execution result
    
    Security Notes:
    - Validate flow JSON structure
    - Sanitize user_input to prevent injection attacks
    - Add rate limiting to prevent abuse
    - Add authentication to restrict who can run flows
    - Consider sandboxing flow execution
    """
    try:
        # Read and validate JSON
        content = await flow_json.read()
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # If LangFlow is available, execute the flow
        if LANGFLOW_AVAILABLE:
            try:
                # Load and execute the flow
                # Note: This is a simplified example
                # ⚠️ Security: Add proper validation and sandboxing
                logger.info(f"🚀 Executing flow with input: {user_input[:50]}...")
                
                # Placeholder for actual flow execution
                # In a real implementation, you would use:
                # flow = load_flow_from_json(flow_data)
                # result = flow.run(user_input)
                
                result = {
                    "result": f"Processed: {user_input}",
                    "status": "success",
                    "note": "This is a placeholder response. Implement actual flow execution."
                }
                
                logger.info("✅ Flow executed successfully")
                return result
            
            except Exception as e:
                logger.error(f"❌ Error executing flow: {e}")
                raise HTTPException(status_code=500, detail=f"Error executing flow: {str(e)}")
        
        # If LangFlow is not available, return simulated response
        else:
            logger.warning("⚠️ Running in simulation mode (LangFlow not available)")
            return {
                "result": f"[SIMULATED] Processed input: {user_input}",
                "status": "simulated",
                "note": "LangFlow is not available. This is a simulated response.",
                "user_input": user_input,
                "flow_received": True
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in run_flow: {e}")
        raise HTTPException(status_code=500, detail=f"Error running flow: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ragamuffin Backend API",
        "langflow_available": LANGFLOW_AVAILABLE,
        "flows_directory": str(FLOWS_DIR),
        "flows_directory_exists": FLOWS_DIR.exists()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
