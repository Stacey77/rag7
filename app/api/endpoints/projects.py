"""
Project management API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.core.logging import app_logger

router = APIRouter()


class ProjectStatus(str, Enum):
    """Project status types."""
    PLANNING = "planning"
    ACTIVE = "active"
    DEPLOYED = "deployed"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ProjectCreate(BaseModel):
    """Model for creating a new AI project."""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    customer_id: Optional[str] = Field(None, description="Customer/client identifier")
    use_case: str = Field(..., description="AI use case")
    llm_providers: List[str] = Field(default=["openai"], description="LLM providers to use")


class Project(BaseModel):
    """Project model."""
    id: str
    name: str
    description: str
    customer_id: Optional[str]
    use_case: str
    status: ProjectStatus
    llm_providers: List[str]
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=Project)
async def create_project(project_data: ProjectCreate):
    """
    Create a new AI product project.
    
    Projects represent individual AI products or solutions being developed
    for customers.
    """
    try:
        app_logger.info(f"Creating project: {project_data.name}")
        
        now = datetime.utcnow()
        project = Project(
            id=f"proj_{hash(project_data.name) % 10000}",
            name=project_data.name,
            description=project_data.description,
            customer_id=project_data.customer_id,
            use_case=project_data.use_case,
            status=ProjectStatus.PLANNING,
            llm_providers=project_data.llm_providers,
            created_at=now,
            updated_at=now
        )
        
        return project
    
    except Exception as e:
        app_logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Project])
async def list_projects(
    status: Optional[ProjectStatus] = None,
    customer_id: Optional[str] = None
):
    """
    List all AI projects with optional filtering.
    """
    try:
        app_logger.info("Listing projects")
        
        # Placeholder: return sample projects
        now = datetime.utcnow()
        sample_projects = [
            Project(
                id="proj_001",
                name="Customer Support AI",
                description="AI-powered customer support system",
                customer_id="customer_123",
                use_case="customer_support",
                status=ProjectStatus.ACTIVE,
                llm_providers=["openai"],
                created_at=now,
                updated_at=now
            ),
            Project(
                id="proj_002",
                name="Document Analysis System",
                description="RAG-based document analysis",
                customer_id="customer_456",
                use_case="document_analysis",
                status=ProjectStatus.DEPLOYED,
                llm_providers=["openai", "anthropic"],
                created_at=now,
                updated_at=now
            )
        ]
        
        return sample_projects
    
    except Exception as e:
        app_logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get details of a specific project."""
    try:
        app_logger.info(f"Getting project: {project_id}")
        
        # Placeholder implementation
        now = datetime.utcnow()
        return Project(
            id=project_id,
            name="Sample Project",
            description="A sample AI project",
            customer_id="customer_123",
            use_case="general",
            status=ProjectStatus.ACTIVE,
            llm_providers=["openai"],
            created_at=now,
            updated_at=now
        )
    
    except Exception as e:
        app_logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=404, detail="Project not found")
