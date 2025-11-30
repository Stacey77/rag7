"""Aggregator graph pattern: Consolidates multiple agent outputs."""

from typing import TypedDict

from langgraph.graph import StateGraph, END

from langgraph.agents.researcher_agent import ResearcherAgent
from langgraph.agents.writer_agent import WriterAgent
from langgraph.agents.aggregator_agent import AggregatorAgent
from langgraph.state.agent_state import AgentState


class AggregatorState(TypedDict):
    """State for the aggregator workflow."""

    messages: list
    current_task: str
    research_results: list
    draft_content: str
    review_feedback: str
    final_output: str
    quality_score: float
    iteration_count: int
    max_iterations: int
    aggregated_results: list
    metadata: dict


def create_aggregator_graph():
    """Create an aggregator workflow graph.

    Pattern: [Multiple Agents] → Aggregator → Final Output

    This pattern is ideal for report generation where insights
    from multiple specialists need to be combined.

    Returns:
        Compiled StateGraph for aggregator execution.
    """
    # Initialize agents
    researcher = ResearcherAgent()
    writer = WriterAgent()
    aggregator = AggregatorAgent()

    # Define node functions
    def research_node(state: dict) -> dict:
        """Execute research phase."""
        agent_state = AgentState(**state)
        result = researcher.process(agent_state)
        return result.model_dump()

    def write_node(state: dict) -> dict:
        """Execute writing phase in parallel with research."""
        agent_state = AgentState(**state)
        # Writer works independently on the task
        result = writer.process(agent_state)
        return result.model_dump()

    def aggregate_node(state: dict) -> dict:
        """Aggregate all outputs into final result."""
        agent_state = AgentState(**state)
        result = aggregator.process(agent_state)
        return result.model_dump()

    # Build the graph
    workflow = StateGraph(AggregatorState)

    # Add nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("writer", write_node)
    workflow.add_node("aggregator", aggregate_node)

    # Define aggregation flow
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "aggregator")
    workflow.add_edge("aggregator", END)

    return workflow.compile()


def run_aggregator_pipeline(task: str) -> dict:
    """Run the aggregator pipeline with a given task.

    Args:
        task: The task or topic to process.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_aggregator_graph()

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
        "aggregated_results": [],
        "metadata": {},
    }

    result = graph.invoke(initial_state)
    return result
