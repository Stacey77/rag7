"""
API Router aggregation.
"""
from fastapi import APIRouter
from app.api.endpoints import llm, agents, projects, deployments

router = APIRouter()

# Include sub-routers
router.include_router(llm.router, prefix="/llm", tags=["LLM"])
router.include_router(agents.router, prefix="/agents", tags=["Agents"])
router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(deployments.router, prefix="/deployments", tags=["Deployments"])
