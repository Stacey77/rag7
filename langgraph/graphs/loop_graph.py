"""Loop graph pattern: Iterative improvement until quality threshold."""

from typing import Literal, TypedDict

from langgraph.graph import StateGraph, END

from langgraph.agents.writer_agent import WriterAgent
from langgraph.agents.reviewer_agent import ReviewerAgent
from langgraph.config import get_settings
from langgraph.state.agent_state import AgentState


class LoopState(TypedDict):
    """State for the loop workflow."""

    messages: list
    current_task: str
    research_results: list
    draft_content: str
    review_feedback: str
    final_output: str
    quality_score: float
    iteration_count: int
    max_iterations: int
    metadata: dict


def create_loop_graph(quality_threshold: float = None, max_iterations: int = None):
    """Create a loop workflow graph for iterative refinement.

    Pattern: Writer → Reviewer → (loop back to Writer if quality < threshold)

    This pattern is ideal for tasks requiring iterative improvement
    until a quality threshold is reached.

    Args:
        quality_threshold: Minimum quality score to exit loop (default from config).
        max_iterations: Maximum iterations before forced exit (default from config).

    Returns:
        Compiled StateGraph for loop execution.
    """
    settings = get_settings()
    if quality_threshold is None:
        quality_threshold = settings.quality_threshold
    if max_iterations is None:
        max_iterations = settings.agent_max_iterations

    # Initialize agents
    writer = WriterAgent()
    reviewer = ReviewerAgent(quality_threshold=quality_threshold)

    # Define node functions
    def write_node(state: dict) -> dict:
        """Execute the writing phase."""
        agent_state = AgentState(**state)
        result = writer.process(agent_state)
        return result.model_dump()

    def review_node(state: dict) -> dict:
        """Execute the review phase."""
        agent_state = AgentState(**state)
        result = reviewer.process(agent_state)
        return result.model_dump()

    def should_continue(state: dict) -> Literal["writer", "end"]:
        """Determine if loop should continue based on quality."""
        quality = state.get("quality_score", 0.0)
        iterations = state.get("iteration_count", 0)

        if quality >= quality_threshold:
            return "end"
        if iterations >= max_iterations:
            return "end"
        return "writer"

    def finalize_node(state: dict) -> dict:
        """Finalize the output when loop completes."""
        agent_state = AgentState(**state)
        agent_state.final_output = agent_state.draft_content
        return agent_state.model_dump()

    # Build the graph
    workflow = StateGraph(LoopState)

    # Add nodes
    workflow.add_node("writer", write_node)
    workflow.add_node("reviewer", review_node)
    workflow.add_node("finalize", finalize_node)

    # Define loop structure
    workflow.set_entry_point("writer")
    workflow.add_edge("writer", "reviewer")

    # Conditional edge: continue loop or exit
    workflow.add_conditional_edges(
        "reviewer",
        should_continue,
        {
            "writer": "writer",
            "end": "finalize",
        }
    )

    workflow.add_edge("finalize", END)

    return workflow.compile()


def run_loop_pipeline(
    task: str,
    quality_threshold: float = 0.8,
    max_iterations: int = 5
) -> dict:
    """Run the loop pipeline with a given task.

    Args:
        task: The task or topic to process.
        quality_threshold: Minimum quality score to exit loop.
        max_iterations: Maximum iterations before forced exit.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_loop_graph(quality_threshold, max_iterations)

    initial_state = {
        "messages": [],
        "current_task": task,
        "research_results": [],
        "draft_content": "",
        "review_feedback": "",
        "final_output": "",
        "quality_score": 0.0,
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "metadata": {},
    }

    result = graph.invoke(initial_state)
    return result
