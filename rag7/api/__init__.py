"""FastAPI application for multi-LLM orchestration."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response
from contextlib import asynccontextmanager
from typing import Optional

from rag7.models import (
    LLMRequest, LLMResponse, MultiLLMRequest, FusedResponse,
    HealthCheck, ProviderMetrics, TaskComplexity
)
from rag7.orchestrator import orchestrator
from rag7.fusion import response_fusion
from rag7.monitoring import monitoring_service
from rag7.agents import agent_manager
from rag7.config import config_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    print("Starting Multi-LLM Orchestration Service...")
    print(f"Available providers: {agent_manager.get_available_agents()}")
    yield
    # Shutdown
    print("Shutting down Multi-LLM Orchestration Service...")


# Create FastAPI app
app = FastAPI(
    title="Multi-LLM Orchestration API",
    description="Comprehensive multi-LLM orchestration framework with GPT-4, Claude, and Gemini integration",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Multi-LLM Orchestration API",
        "version": "1.0.0",
        "description": "Orchestrate multiple LLMs with intelligent routing and response fusion",
        "endpoints": {
            "health": "/health",
            "generate": "/api/v1/generate",
            "multi_generate": "/api/v1/multi-generate",
            "metrics": "/api/v1/metrics",
            "providers": "/api/v1/providers"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    provider_health = await agent_manager.health_check_all()
    
    all_healthy = all(provider_health.values())
    status = "healthy" if all_healthy else "degraded"
    
    return HealthCheck(
        status=status,
        providers=provider_health
    )


@app.post("/api/v1/generate", response_model=LLMResponse)
async def generate(
    request: LLMRequest,
    task_complexity: Optional[TaskComplexity] = None,
    background_tasks: BackgroundTasks = None
):
    """Generate response from a single LLM with intelligent routing."""
    try:
        # Track active request
        selected_provider = orchestrator.router.select_provider(request, task_complexity)
        monitoring_service.metrics_collector.increment_active_requests(selected_provider)
        
        try:
            response = await orchestrator.execute_single(request, task_complexity)
            
            # Record metrics
            monitoring_service.record_request(
                provider=response.provider.value,
                model=response.model,
                tokens=response.tokens_used,
                cost=response.cost,
                latency_ms=response.latency_ms,
                success=True
            )
            
            return response
        finally:
            monitoring_service.metrics_collector.decrement_active_requests(selected_provider)
    
    except Exception as e:
        # Record failure
        if 'selected_provider' in locals():
            monitoring_service.metrics_collector.record_request(
                provider=selected_provider,
                model="unknown",
                tokens=0,
                cost=0.0,
                latency_ms=0.0,
                success=False
            )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/multi-generate", response_model=FusedResponse)
async def multi_generate(request: MultiLLMRequest):
    """Generate responses from multiple LLMs and fuse them."""
    try:
        # Determine which providers to use
        providers = request.providers
        if providers:
            providers = [p.value for p in providers]
        else:
            providers = agent_manager.get_available_agents()
        
        if not providers:
            raise HTTPException(status_code=400, detail="No providers available")
        
        # Track active requests
        for provider in providers:
            monitoring_service.metrics_collector.increment_active_requests(provider)
        
        try:
            # Create LLM request
            llm_request = LLMRequest(
                prompt=request.prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=request.system_prompt,
                metadata=request.metadata
            )
            
            # Execute on multiple providers
            if request.parallel:
                responses = await orchestrator.execute_parallel(llm_request, providers)
            else:
                responses = await orchestrator.execute_sequential(llm_request, providers)
            
            if not responses:
                raise HTTPException(status_code=500, detail="All providers failed")
            
            # Fuse responses
            fused = response_fusion.fuse_responses(responses, request.fusion_strategy)
            
            # Record metrics for all responses
            for response in responses:
                monitoring_service.record_request(
                    provider=response.provider.value,
                    model=response.model,
                    tokens=response.tokens_used,
                    cost=response.cost,
                    latency_ms=response.latency_ms,
                    success=True
                )
            
            return fused
        finally:
            # Decrement active requests
            for provider in providers:
                monitoring_service.metrics_collector.decrement_active_requests(provider)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/providers", response_model=dict)
async def list_providers():
    """List available LLM providers."""
    available = agent_manager.get_available_agents()
    
    provider_info = {}
    for provider in available:
        agent = agent_manager.get_agent(provider)
        if agent:
            provider_info[provider] = {
                "name": agent.name,
                "default_model": agent.provider.get_default_model(),
                "request_count": agent.request_count,
                "error_count": agent.error_count
            }
    
    return {
        "available_providers": available,
        "provider_details": provider_info
    }


@app.get("/api/v1/metrics", response_model=dict)
async def get_metrics():
    """Get comprehensive metrics and statistics."""
    return monitoring_service.get_summary()


@app.get("/api/v1/metrics/provider/{provider}", response_model=ProviderMetrics)
async def get_provider_metrics(provider: str):
    """Get metrics for a specific provider."""
    metrics = monitoring_service.metrics_collector.get_provider_metrics(provider)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Provider not found: {provider}")
    return metrics


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    metrics = monitoring_service.metrics_collector.export_prometheus_metrics()
    return Response(content=metrics, media_type="text/plain")


@app.get("/api/v1/config", response_model=dict)
async def get_config():
    """Get current configuration."""
    return {
        "router": config_manager.get_router_config().dict(),
        "fusion": config_manager.get_fusion_config().dict(),
        "monitoring": config_manager.get_monitoring_config().dict()
    }


if __name__ == "__main__":
    import uvicorn
    settings = config_manager.settings
    uvicorn.run(
        "rag7.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
