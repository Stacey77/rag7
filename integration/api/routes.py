"""API routes for LangGraph integration."""

from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter()


class TaskRequest(BaseModel):
    """Request model for running agent patterns."""

    task: str = Field(..., description="The task or query to process")
    pattern: Literal[
        "sequential", "parallel", "loop", "router",
        "aggregator", "hierarchical", "network"
    ] = Field(default="sequential", description="Agent pattern to use")
    quality_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Quality threshold for loop pattern"
    )
    max_iterations: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum iterations for loop/hierarchical patterns"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional metadata to include in the request"
    )


class TaskResponse(BaseModel):
    """Response model for agent pattern execution."""

    success: bool
    pattern: str
    task: str
    final_output: str
    quality_score: float
    iteration_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class PatternInfo(BaseModel):
    """Information about an agent pattern."""

    name: str
    description: str


@router.get("/patterns", response_model=list[PatternInfo])
async def list_patterns():
    """List all available agent patterns."""
    return [
        PatternInfo(
            name="sequential",
            description="Agents working in chain order (Researcher → Writer → Reviewer)"
        ),
        PatternInfo(
            name="parallel",
            description="Multiple agents processing simultaneously"
        ),
        PatternInfo(
            name="loop",
            description="Iterative improvement until quality threshold"
        ),
        PatternInfo(
            name="router",
            description="Direct inputs to specialized handlers"
        ),
        PatternInfo(
            name="aggregator",
            description="Consolidate multiple agent outputs"
        ),
        PatternInfo(
            name="hierarchical",
            description="Manager-worker structure with delegation"
        ),
        PatternInfo(
            name="network",
            description="Interconnected agents with bidirectional communication"
        ),
    ]


@router.post("/run", response_model=TaskResponse)
async def run_pattern(request: TaskRequest):
    """Run an agent pattern with the specified task.

    This endpoint executes the selected pattern and returns the result.
    """
    try:
        # Import here to avoid circular imports
        from langgraph.graphs.sequential_graph import run_sequential_pipeline
        from langgraph.graphs.parallel_graph import run_parallel_pipeline
        from langgraph.graphs.loop_graph import run_loop_pipeline
        from langgraph.graphs.router_graph import run_router_pipeline
        from langgraph.graphs.aggregator_graph import run_aggregator_pipeline
        from langgraph.graphs.hierarchical_graph import run_hierarchical_pipeline
        from langgraph.graphs.network_graph import run_network_pipeline

        # Map patterns to runners
        pattern_runners = {
            "sequential": run_sequential_pipeline,
            "parallel": run_parallel_pipeline,
            "loop": lambda t: run_loop_pipeline(
                t,
                quality_threshold=request.quality_threshold,
                max_iterations=request.max_iterations
            ),
            "router": run_router_pipeline,
            "aggregator": run_aggregator_pipeline,
            "hierarchical": lambda t: run_hierarchical_pipeline(
                t,
                max_iterations=request.max_iterations
            ),
            "network": run_network_pipeline,
        }

        runner = pattern_runners.get(request.pattern)
        if not runner:
            raise HTTPException(status_code=400, detail=f"Unknown pattern: {request.pattern}")

        # Execute the pattern
        result = runner(request.task)

        return TaskResponse(
            success=True,
            pattern=request.pattern,
            task=request.task,
            final_output=result.get("final_output", ""),
            quality_score=result.get("quality_score", 0.0),
            iteration_count=result.get("iteration_count", 0),
            metadata=result.get("metadata", {}),
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import pattern module: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sequential")
async def run_sequential(request: TaskRequest):
    """Run the sequential pattern (Researcher → Writer → Reviewer)."""
    request.pattern = "sequential"
    return await run_pattern(request)


@router.post("/parallel")
async def run_parallel(request: TaskRequest):
    """Run the parallel pattern (multiple agents simultaneously)."""
    request.pattern = "parallel"
    return await run_pattern(request)


@router.post("/loop")
async def run_loop(request: TaskRequest):
    """Run the loop pattern (iterative improvement)."""
    request.pattern = "loop"
    return await run_pattern(request)


@router.post("/router")
async def run_router(request: TaskRequest):
    """Run the router pattern (smart routing to specialists)."""
    request.pattern = "router"
    return await run_pattern(request)


@router.post("/aggregator")
async def run_aggregator(request: TaskRequest):
    """Run the aggregator pattern (consolidate outputs)."""
    request.pattern = "aggregator"
    return await run_pattern(request)


@router.post("/hierarchical")
async def run_hierarchical(request: TaskRequest):
    """Run the hierarchical pattern (manager-worker)."""
    request.pattern = "hierarchical"
    return await run_pattern(request)


@router.post("/network")
async def run_network(request: TaskRequest):
    """Run the network pattern (interconnected agents)."""
    request.pattern = "network"
    return await run_pattern(request)
