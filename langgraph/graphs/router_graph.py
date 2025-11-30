"""Router graph pattern: Agent that directs inputs to specialized paths."""

from typing import Literal, TypedDict

from langgraph.graph import StateGraph, END

from langgraph.agents.router_agent import RouterAgent
from langgraph.agents.researcher_agent import ResearcherAgent
from langgraph.agents.writer_agent import WriterAgent
from langgraph.state.agent_state import AgentState


class RouterState(TypedDict):
    """State for the router workflow."""

    messages: list
    current_task: str
    research_results: list
    draft_content: str
    review_feedback: str
    final_output: str
    quality_score: float
    iteration_count: int
    max_iterations: int
    route: str
    task_type: str
    metadata: dict


def create_router_graph():
    """Create a router workflow graph.

    Pattern: Router → [Research | Writing | Technical | Creative | Analysis]

    This pattern is ideal for systems that need to handle
    diverse types of requests with specialized handlers.

    Returns:
        Compiled StateGraph for router execution.
    """
    # Initialize agents
    router = RouterAgent()
    researcher = ResearcherAgent()
    writer = WriterAgent()

    # Define specialized handlers
    def router_node(state: dict) -> dict:
        """Execute the routing decision."""
        agent_state = AgentState(**state)
        result = router.process(agent_state)
        return result.model_dump()

    def research_handler(state: dict) -> dict:
        """Handle research-type tasks."""
        agent_state = AgentState(**state)
        result = researcher.process(agent_state)
        result.final_output = "\n".join(result.research_results)
        return result.model_dump()

    def writing_handler(state: dict) -> dict:
        """Handle writing-type tasks."""
        agent_state = AgentState(**state)
        result = writer.process(agent_state)
        result.final_output = result.draft_content
        return result.model_dump()

    def technical_handler(state: dict) -> dict:
        """Handle technical-type tasks."""
        agent_state = AgentState(**state)
        agent_state.current_task = f"Technical analysis: {agent_state.current_task}"
        result = researcher.process(agent_state)
        result.final_output = "\n".join(result.research_results)
        return result.model_dump()

    def creative_handler(state: dict) -> dict:
        """Handle creative-type tasks."""
        agent_state = AgentState(**state)
        agent_state.current_task = f"Creative approach: {agent_state.current_task}"
        result = writer.process(agent_state)
        result.final_output = result.draft_content
        return result.model_dump()

    def analysis_handler(state: dict) -> dict:
        """Handle analysis-type tasks."""
        agent_state = AgentState(**state)
        agent_state.current_task = f"Detailed analysis: {agent_state.current_task}"
        result = researcher.process(agent_state)
        result.final_output = "\n".join(result.research_results)
        return result.model_dump()

    def route_decision(state: dict) -> Literal[
        "research", "writing", "technical", "creative", "analysis"
    ]:
        """Determine which handler to route to based on router decision."""
        route = state.get("route", "research")
        if route not in ["research", "writing", "technical", "creative", "analysis"]:
            return "research"
        return route

    # Build the graph
    workflow = StateGraph(RouterState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("research", research_handler)
    workflow.add_node("writing", writing_handler)
    workflow.add_node("technical", technical_handler)
    workflow.add_node("creative", creative_handler)
    workflow.add_node("analysis", analysis_handler)

    # Define routing structure
    workflow.set_entry_point("router")

    # Conditional edges based on router decision
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "research": "research",
            "writing": "writing",
            "technical": "technical",
            "creative": "creative",
            "analysis": "analysis",
        }
    )

    # All handlers lead to end
    workflow.add_edge("research", END)
    workflow.add_edge("writing", END)
    workflow.add_edge("technical", END)
    workflow.add_edge("creative", END)
    workflow.add_edge("analysis", END)

    return workflow.compile()


def run_router_pipeline(task: str) -> dict:
    """Run the router pipeline with a given task.

    Args:
        task: The task or topic to process.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_router_graph()

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
        "route": None,
        "task_type": None,
        "metadata": {},
    }

    result = graph.invoke(initial_state)
    return result
