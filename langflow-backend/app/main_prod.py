"""
Production-ready Ragamuffin Backend API

FastAPI application for managing and executing LangFlow flows with production features:
- JWT authentication
- Environment-based configuration
- Enhanced security
- Rate limiting support
- Health checks
"""

import json
import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import authentication module
from app.auth import (
    ENABLE_AUTH,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    User,
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "10000"))

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ragamuffin Backend API",
    description="Production API for managing and executing LangFlow flows",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)

# CORS Configuration
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8080,http://localhost:3000,http://127.0.0.1:8080,http://127.0.0.1:3000"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

logger.info(f"CORS allowed origins: {allowed_origins}")
logger.info(f"Authentication enabled: {ENABLE_AUTH}")
logger.info(f"Environment: {ENVIRONMENT}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for persisted flows
FLOWS_DIR = Path(os.getenv("FLOWS_DIR", "/app/flows"))
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Try to import langflow for flow execution
try:
    from langflow.load import load_flow_from_json
    LANGFLOW_AVAILABLE = True
    logger.info("LangFlow package is available for flow execution")
except ImportError:
    LANGFLOW_AVAILABLE = False
    logger.warning(
        "LangFlow package is not installed. /run_flow/ will return simulated responses."
    )


# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Ragamuffin Backend",
        "environment": ENVIRONMENT,
        "langflow_available": LANGFLOW_AVAILABLE,
        "authentication_enabled": ENABLE_AUTH,
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check for monitoring.
    
    Returns service status, dependencies, and configuration.
    """
    return {
        "status": "healthy",
        "service": "ragamuffin-backend",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "dependencies": {
            "langflow": LANGFLOW_AVAILABLE,
            "flows_directory": str(FLOWS_DIR),
            "flows_directory_exists": FLOWS_DIR.exists(),
        },
        "security": {
            "authentication_enabled": ENABLE_AUTH,
        }
    }


@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Default credentials (CHANGE IN PRODUCTION):
    - username: admin
    - password: changeme
    """
    if not ENABLE_AUTH:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentication is disabled. Set ENABLE_AUTH=true to enable."
        )
    
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User {user.username} logged in successfully")
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information."""
    if not ENABLE_AUTH:
        return {"message": "Authentication is disabled"}
    
    return current_user


@app.post("/save_flow/")
async def save_flow(
    flow_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Save a flow JSON file to the flows directory.
    
    Requires authentication if ENABLE_AUTH=true.
    """
    # Validate file extension
    if not flow_file.filename or not flow_file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .json files are allowed.",
        )
    
    # Sanitize filename
    safe_filename = Path(flow_file.filename).name
    if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    
    try:
        content = await flow_file.read()
        
        # Validate JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content.")
        
        # Save the flow
        flow_path = FLOWS_DIR / safe_filename
        with open(flow_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved flow: {safe_filename}")
        if current_user:
            logger.info(f"Flow saved by user: {current_user.username}")
        
        return {"message": f"Flow '{safe_filename}' saved successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving flow: {e}")
        raise HTTPException(status_code=500, detail="Error saving flow")


@app.get("/list_flows/")
async def list_flows(current_user: User = Depends(get_current_active_user)):
    """
    List all saved flows.
    
    Requires authentication if ENABLE_AUTH=true.
    """
    try:
        flows = [f.name for f in FLOWS_DIR.glob("*.json")]
        return {"flows": flows, "count": len(flows)}
    except Exception as e:
        logger.error(f"Error listing flows: {e}")
        raise HTTPException(status_code=500, detail="Error listing flows")


@app.get("/get_flow/{flow_name}")
async def get_flow(
    flow_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific flow by name.
    
    Requires authentication if ENABLE_AUTH=true.
    """
    # Sanitize flow name
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
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute a flow with user input.
    
    CRITICAL SECURITY WARNINGS:
    - Running untrusted flows is a SEVERE security risk - can execute arbitrary code!
    - In production, this endpoint should:
      1. Be restricted to admin users only
      2. Validate flow structure against a schema
      3. Whitelist allowed nodes/tools
      4. Run flows in sandboxed environment (Docker, VM, etc.)
      5. Implement rate limiting per user
      6. Monitor resource usage (CPU, memory, network)
      7. Set execution timeouts
      8. Log all executions for audit trail
    
    Requires authentication if ENABLE_AUTH=true.
    """
    # SECURITY: In production, check if user is admin
    # if ENABLE_AUTH and (not current_user or not current_user.is_admin):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate file
    if not flow_file.filename or not flow_file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .json files are allowed.",
        )
    
    try:
        content = await flow_file.read()
        
        # Validate JSON
        try:
            flow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")
        
        # SECURITY: Validate flow structure
        # TODO: Implement comprehensive flow validation
        # - Check for dangerous operations (file system access, network calls, etc.)
        # - Validate against allowed node types
        # - Check for infinite loops or recursive calls
        # - Validate resource limits
        
        # Validate input length
        if not user_input or len(user_input) > MAX_INPUT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input. Input must be between 1 and {MAX_INPUT_LENGTH} characters.",
            )
        
        if LANGFLOW_AVAILABLE:
            try:
                # SECURITY: Execute in sandboxed environment in production!
                # Consider using:
                # - Docker containers with resource limits
                # - Kubernetes pods with network policies
                # - Virtual machines
                # - AWS Lambda with IAM restrictions
                # - Google Cloud Functions
                
                flow = load_flow_from_json(flow_data)
                result = flow(user_input)
                
                logger.info(f"Flow executed successfully")
                if current_user:
                    logger.info(f"Flow executed by user: {current_user.username}")
                
                return {"result": str(result), "simulated": False}
            except Exception as e:
                logger.error(f"Error executing flow: {e}")
                raise HTTPException(status_code=500, detail=f"Flow execution error: {str(e)}")
        else:
            # Simulated response
            logger.warning("Returning simulated response - langflow is not installed.")
            return {
                "result": f"[SIMULATED] Received input: '{user_input[:100]}...'. "
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


# Additional production endpoints can be added here:
# - DELETE /flow/{flow_name} - Delete a flow
# - PUT /flow/{flow_name} - Update a flow
# - GET /flows/search - Search flows
# - POST /flows/validate - Validate flow structure
