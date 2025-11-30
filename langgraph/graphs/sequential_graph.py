"""Sequential graph pattern: Agents working in chain order."""

from typing import TypedDict

from langgraph.graph import StateGraph, END

from langgraph.agents.researcher_agent import ResearcherAgent
from langgraph.agents.writer_agent import WriterAgent
from langgraph.agents.reviewer_agent import ReviewerAgent
from langgraph.state.agent_state import AgentState


class SequentialState(TypedDict):
    """State for the sequential workflow."""

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


def create_sequential_graph():
    """Create a sequential workflow graph.

    Pattern: Researcher → Writer → Reviewer

    This pattern is ideal for content pipelines where each stage
    builds upon the previous one in a linear fashion.

    Returns:
        Compiled StateGraph for sequential execution.
    """
    # Initialize agents
    researcher = ResearcherAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()

    # Define node functions
    def research_node(state: dict) -> dict:
        """Execute the research phase."""
        agent_state = AgentState(**state)
        result = researcher.process(agent_state)
        return result.model_dump()

    def write_node(state: dict) -> dict:
        """Execute the writing phase."""
        agent_state = AgentState(**state)
        result = writer.process(agent_state)
        return result.model_dump()

    def review_node(state: dict) -> dict:
        """Execute the review phase."""
        agent_state = AgentState(**state)
        result = reviewer.process(agent_state)
        # Set final output from draft after review
        result.final_output = result.draft_content
        return result.model_dump()

    # Build the graph
    workflow = StateGraph(SequentialState)

    # Add nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("writer", write_node)
    workflow.add_node("reviewer", review_node)

    # Define sequential edges
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_edge("reviewer", END)

    return workflow.compile()


def run_sequential_pipeline(task: str) -> dict:
    """Run the sequential pipeline with a given task.

    Args:
        task: The task or topic to process.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_sequential_graph()

    initial_state = {
        "messages": [],
        "current_task": task,
        "research_results": [],
        "draft_content": "",
        "review_feedback": "",
        "final_output": "",
        "quality_score": 0.0,
        "iteration_count": 0,
        "max_iterations": 1,
        "metadata": {},
    }

    result = graph.invoke(initial_state)
    return result
