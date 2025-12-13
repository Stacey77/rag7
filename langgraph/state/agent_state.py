"""State management and checkpointing for the multi-agent system."""

from datetime import datetime
from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in the agent conversation."""

    role: Literal["user", "assistant", "system", "agent"]
    content: str
    agent_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


def add_messages(existing: list[Message], new: list[Message]) -> list[Message]:
    """Reducer function to add messages to the state."""
    return existing + new


class AgentState(BaseModel):
    """State shared across all agents in the graph.

    This state object is passed between agents and maintains
    conversation history, context, and metadata.
    """

    # Message history with reducer for appending
    messages: Annotated[list[Message], add_messages] = Field(default_factory=list)

    # Current task or query being processed
    current_task: str = ""

    # Results from different agents
    research_results: list[str] = Field(default_factory=list)
    draft_content: str = ""
    review_feedback: str = ""
    final_output: str = ""

    # Routing information
    route: Optional[str] = None
    task_type: Optional[str] = None

    # Quality metrics for loop pattern
    quality_score: float = 0.0
    iteration_count: int = 0
    max_iterations: int = 10

    # Aggregation data
    aggregated_results: list[dict[str, Any]] = Field(default_factory=list)

    # Human-in-the-loop
    needs_human_approval: bool = False
    human_feedback: Optional[str] = None
    is_approved: bool = False

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    checkpoint_id: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


class Checkpoint(BaseModel):
    """Checkpoint for persisting agent state."""

    checkpoint_id: str
    state: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


def create_checkpoint(state: AgentState, checkpoint_id: Optional[str] = None) -> Checkpoint:
    """Create a checkpoint from the current state.

    Args:
        state: The current agent state to checkpoint.
        checkpoint_id: Optional ID for the checkpoint. Generated if not provided.

    Returns:
        A Checkpoint object containing the serialized state.
    """
    if checkpoint_id is None:
        checkpoint_id = f"cp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return Checkpoint(
        checkpoint_id=checkpoint_id,
        state=state.model_dump(),
        metadata={"created_at": datetime.now().isoformat()},
    )
