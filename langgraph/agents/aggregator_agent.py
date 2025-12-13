"""Aggregator agent for consolidating multiple outputs."""

from typing import Any, Optional

from langchain_core.language_models import BaseChatModel

from langgraph.agents.base_agent import BaseAgent
from langgraph.state.agent_state import AgentState


AGGREGATOR_SYSTEM_PROMPT = """You are an expert at synthesizing and consolidating information from multiple sources.

Your responsibilities:
1. Combine outputs from multiple agents or sources
2. Identify common themes and key insights
3. Resolve any conflicts or contradictions
4. Create a unified, coherent summary
5. Highlight the most important findings

When aggregating:
- Identify overlapping and unique contributions
- Weigh information based on relevance and quality
- Create a logical structure for the combined output
- Preserve important nuances from individual sources
- Provide clear attribution when needed

Output a comprehensive synthesis that captures the best insights from all inputs."""


class AggregatorAgent(BaseAgent):
    """Agent specialized in consolidating multiple agent outputs.

    This agent takes outputs from multiple sources and creates
    a unified, coherent synthesis of the information.
    """

    def __init__(
        self,
        name: str = "aggregator",
        model: Optional[BaseChatModel] = None,
    ):
        """Initialize the aggregator agent.

        Args:
            name: The name of the agent.
            model: Optional LLM model. Uses default if not provided.
        """
        super().__init__(
            name=name,
            system_prompt=AGGREGATOR_SYSTEM_PROMPT,
            model=model,
        )

    def process(self, state: AgentState) -> AgentState:
        """Aggregate multiple outputs into a unified result.

        Args:
            state: The current agent state with multiple outputs.

        Returns:
            Updated state with aggregated results.
        """
        task = state.current_task

        # Collect all available outputs
        outputs = self._collect_outputs(state)

        # Prepare aggregation prompt
        aggregation_prompt = f"""Synthesize the following outputs into a unified, comprehensive result:

Original Task: {task}

Outputs to Aggregate:
{self._format_outputs(outputs)}

Create a comprehensive synthesis that:
1. Combines the key insights from all sources
2. Resolves any conflicts or contradictions
3. Provides a coherent, unified summary
4. Highlights the most important findings"""

        # Invoke LLM for aggregation
        aggregated_content = self.invoke_llm(aggregation_prompt)

        # Update state with aggregated result
        state.final_output = aggregated_content
        state.aggregated_results = outputs

        # Add message to history
        state = self.add_message_to_state(
            state,
            content=aggregated_content,
            metadata={
                "task": task,
                "agent_type": "aggregator",
                "source_count": len(outputs),
            },
        )

        return state

    def _collect_outputs(self, state: AgentState) -> list[dict[str, Any]]:
        """Collect all available outputs from the state.

        Args:
            state: The current agent state.

        Returns:
            List of outputs with source attribution.
        """
        outputs = []

        # Collect research results
        for i, research in enumerate(state.research_results):
            outputs.append({
                "source": f"Research #{i + 1}",
                "content": research,
            })

        # Collect draft content if available
        if state.draft_content:
            outputs.append({
                "source": "Draft Content",
                "content": state.draft_content,
            })

        # Collect review feedback if available
        if state.review_feedback:
            outputs.append({
                "source": "Review Feedback",
                "content": state.review_feedback,
            })

        return outputs

    def _format_outputs(self, outputs: list[dict[str, Any]]) -> str:
        """Format outputs for the aggregation prompt.

        Args:
            outputs: List of output dictionaries.

        Returns:
            Formatted string of all outputs.
        """
        if not outputs:
            return "No outputs available."

        formatted_parts = []
        for output in outputs:
            formatted_parts.append(
                f"--- {output['source']} ---\n{output['content']}"
            )
        return "\n\n".join(formatted_parts)
