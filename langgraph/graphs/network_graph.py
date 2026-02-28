"""Network graph pattern: Interconnected agents with bidirectional communication."""

from typing import Literal, TypedDict, Any

from langgraph.graph import StateGraph, END

from langgraph.agents.researcher_agent import ResearcherAgent
from langgraph.agents.writer_agent import WriterAgent
from langgraph.agents.reviewer_agent import ReviewerAgent
from langgraph.agents.router_agent import RouterAgent
from langgraph.agents.aggregator_agent import AggregatorAgent
from langgraph.state.agent_state import AgentState


class NetworkState(TypedDict):
    """State for the network workflow."""

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
    route: str
    task_type: str
    active_agents: list
    communication_log: list
    metadata: dict


def create_network_graph():
    """Create a network workflow graph.

    Pattern: Interconnected agents where any agent can communicate
    with any other agent based on needs.

    This pattern is ideal for complex problems requiring
    dynamic collaboration between specialists.

    Returns:
        Compiled StateGraph for network execution.
    """
    # Initialize agents
    router = RouterAgent()
    researcher = ResearcherAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()
    aggregator = AggregatorAgent()

    # Define node functions with inter-agent communication
    def coordinator_node(state: dict) -> dict:
        """Coordinate network and determine next active agent."""
        agent_state = AgentState(**state)

        # Initialize communication log if needed
        if "communication_log" not in state:
            state["communication_log"] = []

        # Determine next step based on current state
        active_agents = state.get("active_agents", [])

        if not state.get("research_results"):
            state["metadata"]["next_agent"] = "researcher"
        elif not state.get("draft_content"):
            state["metadata"]["next_agent"] = "writer"
        elif state.get("quality_score", 0) < 0.8 and state.get("iteration_count", 0) < 3:
            state["metadata"]["next_agent"] = "reviewer"
        else:
            state["metadata"]["next_agent"] = "aggregator"

        # Log communication
        state["communication_log"].append({
            "from": "coordinator",
            "to": state["metadata"]["next_agent"],
            "message": f"Routing task to {state['metadata']['next_agent']}",
        })

        return state

    def researcher_node(state: dict) -> dict:
        """Researcher in the network."""
        agent_state = AgentState(**state)
        result = researcher.process(agent_state)

        # Log communication
        result_dict = result.model_dump()
        if "communication_log" not in result_dict:
            result_dict["communication_log"] = []
        result_dict["communication_log"].append({
            "from": "researcher",
            "to": "network",
            "message": "Research complete, results available",
        })

        return result_dict

    def writer_node(state: dict) -> dict:
        """Writer in the network."""
        agent_state = AgentState(**state)
        result = writer.process(agent_state)

        # Log communication
        result_dict = result.model_dump()
        if "communication_log" not in result_dict:
            result_dict["communication_log"] = []
        result_dict["communication_log"].append({
            "from": "writer",
            "to": "network",
            "message": "Draft complete, ready for review",
        })

        return result_dict

    def reviewer_node(state: dict) -> dict:
        """Reviewer in the network."""
        agent_state = AgentState(**state)
        result = reviewer.process(agent_state)

        # Log communication with feedback
        result_dict = result.model_dump()
        if "communication_log" not in result_dict:
            result_dict["communication_log"] = []
        result_dict["communication_log"].append({
            "from": "reviewer",
            "to": "network",
            "message": f"Review complete. Score: {result.quality_score}",
        })

        return result_dict

    def aggregator_node(state: dict) -> dict:
        """Aggregator finalizes network output."""
        agent_state = AgentState(**state)
        result = aggregator.process(agent_state)

        # Log communication
        result_dict = result.model_dump()
        if "communication_log" not in result_dict:
            result_dict["communication_log"] = []
        result_dict["communication_log"].append({
            "from": "aggregator",
            "to": "network",
            "message": "Final output aggregated",
        })

        return result_dict

    def route_to_next(state: dict) -> Literal[
        "researcher", "writer", "reviewer", "aggregator", "end"
    ]:
        """Route to the next agent in the network."""
        next_agent = state.get("metadata", {}).get("next_agent", "researcher")
        if next_agent == "aggregator" and state.get("final_output"):
            return "end"
        return next_agent

    def determine_next_step(state: dict) -> Literal[
        "coordinator", "end"
    ]:
        """Determine if we need more coordination or are done."""
        if state.get("final_output"):
            return "end"
        return "coordinator"

    # Build the network graph
    workflow = StateGraph(NetworkState)

    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("aggregator", aggregator_node)

    # Define network connections
    workflow.set_entry_point("coordinator")

    # Coordinator routes to any agent
    workflow.add_conditional_edges(
        "coordinator",
        route_to_next,
        {
            "researcher": "researcher",
            "writer": "writer",
            "reviewer": "reviewer",
            "aggregator": "aggregator",
            "end": END,
        }
    )

    # All agents can loop back to coordinator for next decision
    workflow.add_conditional_edges(
        "researcher",
        determine_next_step,
        {"coordinator": "coordinator", "end": END}
    )
    workflow.add_conditional_edges(
        "writer",
        determine_next_step,
        {"coordinator": "coordinator", "end": END}
    )
    workflow.add_conditional_edges(
        "reviewer",
        determine_next_step,
        {"coordinator": "coordinator", "end": END}
    )
    workflow.add_edge("aggregator", END)

    return workflow.compile()


def run_network_pipeline(task: str) -> dict:
    """Run the network pipeline with a given task.

    Args:
        task: The task or topic to process.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_network_graph()

    initial_state = {
        "messages": [],
        "current_task": task,
        "research_results": [],
        "draft_content": "",
        "review_feedback": "",
        "final_output": "",
        "quality_score": 0.0,
        "iteration_count": 0,
        "max_iterations": 5,
        "aggregated_results": [],
        "route": None,
        "task_type": None,
        "active_agents": [],
        "communication_log": [],
        "metadata": {},
    }

    result = graph.invoke(initial_state)
    return result
