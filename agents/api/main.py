"""
Main API Application
"""
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from agents.core.agent_orchestrator import AgentOrchestrator
from agents.policy_agent import PolicyAgent
from agents.intent_agent import IntentAgent
from agents.deployment_agent import DeploymentAgent
from agents.compliance_agent import ComplianceAgent
from agents.inference_agent import InferenceAgent
from agents.config.settings import settings
from agents.api.routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting Agentic Infrastructure Platform")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator.get_instance()
    
    # Register agents
    if settings.enable_policy_agent:
        policy_agent = PolicyAgent(config={
            "use_opa": settings.use_opa,
            "opa_url": settings.opa_url
        })
        orchestrator.register_agent(policy_agent)
        logger.info("Registered Policy Agent")
    
    if settings.enable_intent_agent:
        intent_agent = IntentAgent(config={
            "use_ai": settings.use_ai,
            "api_key": settings.openai_api_key
        })
        orchestrator.register_agent(intent_agent)
        logger.info("Registered Intent Agent")
    
    if settings.enable_deployment_agent:
        deployment_agent = DeploymentAgent(config={
            "kubernetes": {
                "namespace": settings.k8s_namespace
            }
        })
        orchestrator.register_agent(deployment_agent)
        logger.info("Registered Deployment Agent")
    
    if settings.enable_compliance_agent:
        compliance_agent = ComplianceAgent()
        orchestrator.register_agent(compliance_agent)
        logger.info("Registered Compliance Agent")
    
    if settings.enable_inference_agent:
        inference_agent = InferenceAgent()
        orchestrator.register_agent(inference_agent)
        logger.info("Registered Inference Agent")
    
    # Start all agents
    asyncio.create_task(orchestrator.start_all_agents())
    
    logger.info("Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down platform")
    await orchestrator.stop_all_agents()
    logger.info("Platform shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Agentic Infrastructure Control Platform",
    description="Multi-Agent Governed Automation for Networks, Edge, and Cloud",
    version=settings.version,
    lifespan=lifespan
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "platform": settings.platform_name,
        "version": settings.version,
        "docs": "/docs",
        "api": "/api/v1"
    }


def main():
    """Main entry point"""
    import uvicorn
    
    uvicorn.run(
        "agents.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers if settings.environment == "production" else 1,
        reload=settings.environment == "development"
    )


if __name__ == "__main__":
    main()
