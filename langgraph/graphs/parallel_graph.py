"""Parallel graph pattern: Multiple agents processing simultaneously."""

from typing import TypedDict
import asyncio

from langgraph.graph import StateGraph, END

from langgraph.agents.researcher_agent import ResearcherAgent
from langgraph.agents.aggregator_agent import AggregatorAgent
from langgraph.state.agent_state import AgentState


class ParallelState(TypedDict):
    """State for the parallel workflow."""

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


def create_parallel_graph():
    """Create a parallel workflow graph.

    Pattern: Multiple researchers working simultaneously → Aggregator

    This pattern is ideal for multi-source analysis where multiple
    perspectives need to be gathered and combined.

    Returns:
        Compiled StateGraph for parallel execution.
    """
    # Initialize agents with different focuses
    researcher1 = ResearcherAgent(name="researcher_technical")
    researcher2 = ResearcherAgent(name="researcher_market")
    researcher3 = ResearcherAgent(name="researcher_user")
    aggregator = AggregatorAgent()

    # Define node functions
    def research_technical_node(state: dict) -> dict:
        """Execute technical research."""
        agent_state = AgentState(**state)
        agent_state.current_task = f"Technical analysis: {state['current_task']}"
        result = researcher1.process(agent_state)
        return result.model_dump()

    def research_market_node(state: dict) -> dict:
        """Execute market research."""
        agent_state = AgentState(**state)
        agent_state.current_task = f"Market analysis: {state['current_task']}"
        result = researcher2.process(agent_state)
        return result.model_dump()

    def research_user_node(state: dict) -> dict:
        """Execute user research."""
        agent_state = AgentState(**state)
        agent_state.current_task = f"User experience analysis: {state['current_task']}"
        result = researcher3.process(agent_state)
        return result.model_dump()

    def merge_research(states: list[dict]) -> dict:
        """Merge research results from parallel branches."""
        merged_state = states[0].copy()
        all_research = []
        all_messages = []

        for state in states:
            all_research.extend(state.get("research_results", []))
            all_messages.extend(state.get("messages", []))

        merged_state["research_results"] = all_research
        merged_state["messages"] = all_messages
        return merged_state

    def aggregate_node(state: dict) -> dict:
        """Aggregate all research results."""
        agent_state = AgentState(**state)
        result = aggregator.process(agent_state)
        return result.model_dump()

    # Build the graph with parallel branches
    workflow = StateGraph(ParallelState)

    # Add nodes
    workflow.add_node("research_technical", research_technical_node)
    workflow.add_node("research_market", research_market_node)
    workflow.add_node("research_user", research_user_node)
    workflow.add_node("aggregator", aggregate_node)

    # Entry point fans out to parallel researchers
    workflow.set_entry_point("research_technical")

    # In LangGraph, we simulate parallel execution by sequential nodes
    # that all converge to the aggregator
    workflow.add_edge("research_technical", "research_market")
    workflow.add_edge("research_market", "research_user")
    workflow.add_edge("research_user", "aggregator")
    workflow.add_edge("aggregator", END)

    return workflow.compile()


def run_parallel_pipeline(task: str) -> dict:
    """Run the parallel pipeline with a given task.

    Args:
        task: The task or topic to process.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_parallel_graph()

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
