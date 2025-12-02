"""FastAPI web interface for the RAG7 AI Agent Platform."""
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..utils.config import get_settings
from ..agent.core import ConversationalAgent
from ..agent.memory import AgentMemory
from ..integrations.slack import SlackIntegration
from ..integrations.gmail import GmailIntegration
from ..integrations.notion import NotionIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[ConversationalAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global agent
    
    # Load settings
    settings = get_settings()
    logger.info(f"Starting RAG7 AI Agent Platform in {settings.environment} mode")
    
    # Initialize memory
    memory = AgentMemory(
        use_chromadb=True,
        chroma_host=settings.chroma_host,
        chroma_port=settings.chroma_port
    )
    
    # Initialize integrations
    integrations = []
    
    # Slack integration
    if settings.slack_bot_token:
        slack = SlackIntegration(bot_token=settings.slack_bot_token)
        integrations.append(slack)
        logger.info("Slack integration enabled")
    else:
        logger.warning("Slack integration disabled - no bot token")
    
    # Gmail integration
    if settings.gmail_credentials_file or (settings.gmail_smtp_user and settings.gmail_smtp_password):
        gmail = GmailIntegration(
            credentials_file=settings.gmail_credentials_file,
            token_file=settings.gmail_token_file,
            smtp_user=settings.gmail_smtp_user,
            smtp_password=settings.gmail_smtp_password
        )
        integrations.append(gmail)
        logger.info("Gmail integration enabled")
    else:
        logger.warning("Gmail integration disabled - no credentials")
    
    # Notion integration
    if settings.notion_api_key:
        notion = NotionIntegration(
            api_key=settings.notion_api_key,
            database_id=settings.notion_database_id
        )
        integrations.append(notion)
        logger.info("Notion integration enabled")
    else:
        logger.warning("Notion integration disabled - no API key")
    
    # Initialize agent
    if settings.openai_api_key:
        agent = ConversationalAgent(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            integrations=integrations,
            memory=memory
        )
        logger.info(f"Agent initialized with {len(integrations)} integrations")
    else:
        logger.error("Cannot initialize agent - OpenAI API key not configured")
        agent = None
    
    yield
    
    # Cleanup
    logger.info("Shutting down RAG7 AI Agent Platform")


# Create FastAPI app
app = FastAPI(
    title="RAG7 AI Agent Platform",
    description="Conversational AI agent with integrations for Slack, Gmail, and Notion",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    function_calls: List[Dict[str, Any]] = []
    error: Optional[str] = None


class IntegrationStatus(BaseModel):
    """Integration status model."""
    name: str
    healthy: bool
    functions_count: int


class FunctionInfo(BaseModel):
    """Function information model."""
    integration: str
    name: str
    full_name: str
    description: str
    parameters: List[Dict[str, Any]]


# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "RAG7 AI Agent Platform",
        "version": "0.1.0",
        "status": "running",
        "agent_initialized": agent is not None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_ready": agent is not None,
        "openai_configured": bool(get_settings().openai_api_key)
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI agent.
    
    The agent will process the message, execute any required functions,
    and return a response.
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized - check OpenAI API key configuration"
        )
    
    try:
        result = await agent.chat(
            message=request.message,
            user_id=request.user_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/integrations", response_model=List[IntegrationStatus])
async def get_integrations():
    """
    Get status of all integrations.
    
    Returns health status and function count for each integration.
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )
    
    try:
        statuses = await agent.get_integrations_status()
        return [IntegrationStatus(**status) for status in statuses]
        
    except Exception as e:
        logger.error(f"Error getting integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/functions", response_model=List[FunctionInfo])
async def get_functions():
    """
    Get list of all available functions from integrations.
    
    Returns detailed information about each function including
    parameters and descriptions.
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )
    
    try:
        functions = agent.get_available_functions()
        return [FunctionInfo(**func) for func in functions]
        
    except Exception as e:
        logger.error(f"Error getting functions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket for real-time chat
class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Total: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific connection."""
        await websocket.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    
    Send JSON messages in format:
    {
        "message": "your message here",
        "user_id": "optional_user_id"
    }
    
    Receive JSON responses in format:
    {
        "type": "response|error",
        "response": "assistant response",
        "function_calls": [...],
        "error": null or error message
    }
    """
    await manager.connect(websocket)
    
    if not agent:
        await manager.send_message(websocket, {
            "type": "error",
            "error": "Agent not initialized - check configuration"
        })
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            message = data.get("message")
            user_id = data.get("user_id")
            
            if not message:
                await manager.send_message(websocket, {
                    "type": "error",
                    "error": "Message is required"
                })
                continue
            
            # Process message
            result = await agent.chat(
                message=message,
                user_id=user_id
            )
            
            # Send response
            await manager.send_message(websocket, {
                "type": "response",
                **result
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.send_message(websocket, {
                "type": "error",
                "error": str(e)
            })
        except:
            pass
        manager.disconnect(websocket)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.interfaces.web_api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
