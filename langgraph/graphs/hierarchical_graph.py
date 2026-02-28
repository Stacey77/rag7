"""Hierarchical graph pattern: Manager-worker structure with delegation."""

from typing import Literal, TypedDict

from langgraph.graph import StateGraph, END

from langgraph.agents.researcher_agent import ResearcherAgent
from langgraph.agents.writer_agent import WriterAgent
from langgraph.agents.reviewer_agent import ReviewerAgent
from langgraph.agents.aggregator_agent import AggregatorAgent
from langgraph.agents.base_agent import BaseAgent
from langgraph.state.agent_state import AgentState


class HierarchicalState(TypedDict):
    """State for the hierarchical workflow."""

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
    worker_assignments: dict
    manager_notes: str
    phase: str
    metadata: dict


MANAGER_SYSTEM_PROMPT = """You are a project manager coordinating a team of specialized agents.

Your responsibilities:
1. Break down complex tasks into subtasks
2. Assign work to appropriate team members
3. Monitor progress and quality
4. Make decisions about workflow direction
5. Consolidate final deliverables

Team members available:
- Researcher: Gathers information and data
- Writer: Creates written content
- Reviewer: Reviews and provides feedback

Output your management decisions clearly with:
PHASE: [research|writing|review|complete]
DIRECTION: [your instructions for the next phase]"""


class ManagerAgent(BaseAgent):
    """Manager agent that coordinates worker agents."""

    def __init__(self):
        """Initialize the manager agent."""
        super().__init__(
            name="manager",
            system_prompt=MANAGER_SYSTEM_PROMPT,
        )

    def process(self, state: AgentState) -> AgentState:
        """Coordinate work and make management decisions."""
        task = state.current_task
        current_phase = state.metadata.get("phase", "start")

        # Prepare management prompt
        management_prompt = f"""Coordinate the following task:

Task: {task}

Current Phase: {current_phase}
Research Results: {len(state.research_results)} items
Draft Available: {"Yes" if state.draft_content else "No"}
Quality Score: {state.quality_score}

Determine the next phase and provide direction."""

        response = self.invoke_llm(management_prompt)

        # Extract phase from response
        phase = self._extract_phase(response)
        state.metadata["phase"] = phase
        state.metadata["manager_notes"] = response

        state = self.add_message_to_state(
            state,
            content=response,
            metadata={"agent_type": "manager", "phase": phase},
        )

        return state

    def _extract_phase(self, response: str) -> str:
        """Extract phase from manager response."""
        try:
            if "PHASE:" in response.upper():
                phase_part = response.upper().split("PHASE:")[1].strip()
                phase = phase_part.split()[0].strip().lower()
                if phase in ["research", "writing", "review", "complete"]:
                    return phase
        except (IndexError, ValueError):
            pass
        return "research"


def create_hierarchical_graph():
    """Create a hierarchical workflow graph.

    Pattern: Manager → [Research | Writing | Review] → Manager (repeat)

    This pattern is ideal for complex projects requiring
    coordination and iterative refinement under supervision.

    Returns:
        Compiled StateGraph for hierarchical execution.
    """
    # Initialize agents
    manager = ManagerAgent()
    researcher = ResearcherAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()
    aggregator = AggregatorAgent()

    # Define node functions
    def manager_node(state: dict) -> dict:
        """Manager makes coordination decisions."""
        agent_state = AgentState(**state)
        if "phase" not in agent_state.metadata:
            agent_state.metadata["phase"] = "start"
        result = manager.process(agent_state)
        return result.model_dump()

    def research_node(state: dict) -> dict:
        """Worker executes research."""
        agent_state = AgentState(**state)
        result = researcher.process(agent_state)
        result.metadata["phase"] = "writing"  # Progress to next phase
        return result.model_dump()

    def write_node(state: dict) -> dict:
        """Worker executes writing."""
        agent_state = AgentState(**state)
        result = writer.process(agent_state)
        result.metadata["phase"] = "review"  # Progress to next phase
        return result.model_dump()

    def review_node(state: dict) -> dict:
        """Worker executes review."""
        agent_state = AgentState(**state)
        result = reviewer.process(agent_state)
        if result.quality_score >= 0.8:
            result.metadata["phase"] = "complete"
        else:
            result.metadata["phase"] = "writing"
        return result.model_dump()

    def finalize_node(state: dict) -> dict:
        """Finalize the output."""
        agent_state = AgentState(**state)
        result = aggregator.process(agent_state)
        return result.model_dump()

    def route_from_manager(state: dict) -> Literal[
        "research", "writing", "review", "finalize"
    ]:
        """Route based on manager's phase decision."""
        phase = state.get("metadata", {}).get("phase", "research")
        if phase == "complete":
            return "finalize"
        if phase in ["research", "writing", "review"]:
            return phase
        return "research"

    # Build the graph
    workflow = StateGraph(HierarchicalState)

    # Add nodes
    workflow.add_node("manager", manager_node)
    workflow.add_node("research", research_node)
    workflow.add_node("writing", write_node)
    workflow.add_node("review", review_node)
    workflow.add_node("finalize", finalize_node)

    # Define hierarchical structure
    workflow.set_entry_point("manager")

    # Manager routes to appropriate worker
    workflow.add_conditional_edges(
        "manager",
        route_from_manager,
        {
            "research": "research",
            "writing": "writing",
            "review": "review",
            "finalize": "finalize",
        }
    )

    # Workers report back to manager (or finalize)
    workflow.add_edge("research", "manager")
    workflow.add_edge("writing", "manager")
    workflow.add_edge("review", "manager")
    workflow.add_edge("finalize", END)

    return workflow.compile()


def run_hierarchical_pipeline(task: str, max_iterations: int = 10) -> dict:
    """Run the hierarchical pipeline with a given task.

    Args:
        task: The task or topic to process.
        max_iterations: Maximum manager iterations.

    Returns:
        Final state after pipeline completion.
    """
    graph = create_hierarchical_graph()

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
        "aggregated_results": [],
        "worker_assignments": {},
        "manager_notes": "",
        "phase": "start",
        "metadata": {"phase": "start"},
    }

    result = graph.invoke(initial_state)
    return result
