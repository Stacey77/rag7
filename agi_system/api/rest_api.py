"""
AGI System - REST API
FastAPI-based REST API for the AGI system
"""
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uvicorn
from loguru import logger

from agi_system import AGISystem, create_agi_system


# Pydantic models for API
class UserInputRequest(BaseModel):
    """User input request model"""
    input: str = Field(..., description="User input text")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")


class GoalRequest(BaseModel):
    """Goal setting request model"""
    description: str = Field(..., description="Goal description")
    priority: str = Field("medium", description="Priority: low, medium, high, critical")


class KnowledgeRequest(BaseModel):
    """Knowledge addition request model"""
    content: str = Field(..., description="Knowledge content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class StructuredKnowledgeRequest(BaseModel):
    """Structured knowledge request model"""
    subject: str = Field(..., description="Subject entity")
    predicate: str = Field(..., description="Relation/predicate")
    object: str = Field(..., description="Object entity")


class QueryRequest(BaseModel):
    """Query request model"""
    query: str = Field(..., description="Query string")
    method: str = Field("hybrid", description="Query method: vector, graph, hybrid")
    k: int = Field(5, description="Number of results")


class ReasoningRequest(BaseModel):
    """Reasoning request model"""
    query: str = Field(..., description="Query to reason about")
    reasoning_type: str = Field("symbolic", description="Reasoning type: symbolic, emotional, hybrid")


# Create FastAPI app
app = FastAPI(
    title="AGI System API",
    description="REST API for the AGI System with Symbolic and Emotional Reasoning",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global AGI system instance
agi_system: Optional[AGISystem] = None


@app.on_event("startup")
async def startup_event():
    """Initialize AGI system on startup"""
    global agi_system
    logger.info("Starting AGI System API...")
    agi_system = create_agi_system()
    logger.info("AGI System API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AGI System API...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AGI System API",
        "version": "0.1.0",
        "status": "running",
        "description": "AGI System with Symbolic and Emotional Reasoning"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    return {
        "status": "healthy",
        "system": "operational"
    }


@app.post("/process")
async def process_input(request: UserInputRequest):
    """
    Process user input through the AGI system
    
    Returns comprehensive analysis including emotional, symbolic reasoning, and knowledge retrieval
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        result = agi_system.process_input(request.input, request.context)
        return result
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/goal/set")
async def set_goal(request: GoalRequest):
    """
    Set a high-level goal for the AGI agent
    
    Returns the goal ID
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        goal_id = agi_system.set_goal(request.description, request.priority)
        return {
            "goal_id": goal_id,
            "description": request.description,
            "priority": request.priority,
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error setting goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/goal/execute")
async def execute_goal(goal_id: Optional[str] = None):
    """
    Execute a goal autonomously
    
    If no goal_id provided, executes the active goal
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        result = agi_system.execute_goal(goal_id)
        return result
    except Exception as e:
        logger.error(f"Error executing goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/add")
async def add_knowledge(request: KnowledgeRequest):
    """
    Add knowledge to the system
    
    Returns the document ID
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        doc_id = agi_system.add_knowledge(request.content, request.metadata)
        return {
            "doc_id": doc_id,
            "status": "added"
        }
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/add_structured")
async def add_structured_knowledge(request: StructuredKnowledgeRequest):
    """
    Add structured knowledge (triple) to knowledge graph
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        agi_system.add_structured_knowledge(
            request.subject,
            request.predicate,
            request.object
        )
        return {
            "subject": request.subject,
            "predicate": request.predicate,
            "object": request.object,
            "status": "added"
        }
    except Exception as e:
        logger.error(f"Error adding structured knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/query")
async def query_knowledge(request: QueryRequest):
    """
    Query the knowledge base
    
    Supports vector, graph, and hybrid search methods
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        result = agi_system.query_knowledge(request.query, request.method)
        return result
    except Exception as e:
        logger.error(f"Error querying knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reason")
async def reason(request: ReasoningRequest):
    """
    Perform reasoning on a query
    
    Supports symbolic, emotional, and hybrid reasoning
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        result = agi_system.reason(request.query, request.reasoning_type)
        return result
    except Exception as e:
        logger.error(f"Error performing reasoning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """
    Get comprehensive system status
    
    Returns status of all subsystems
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        status = agi_system.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/consolidate")
async def consolidate_memories():
    """
    Consolidate memories from short-term to long-term
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        result = agi_system.consolidate_memories()
        return result
    except Exception as e:
        logger.error(f"Error consolidating memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/graph/export")
async def export_knowledge_graph():
    """
    Export the knowledge graph
    """
    if agi_system is None:
        raise HTTPException(status_code=503, detail="AGI System not initialized")
    
    try:
        graph = agi_system.export_knowledge_graph()
        return graph
    except Exception as e:
        logger.error(f"Error exporting knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server"""
    uvicorn.run(
        "agi_system.api.rest_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_api(reload=True)
