"""Writer agent for content generation."""

from typing import Optional

from langchain_core.language_models import BaseChatModel

from langgraph.agents.base_agent import BaseAgent
from langgraph.state.agent_state import AgentState


WRITER_SYSTEM_PROMPT = """You are an expert content writer with skills in creating engaging, clear, and well-structured content.

Your responsibilities:
1. Generate high-quality written content based on provided research and requirements
2. Adapt writing style to match the intended audience and purpose
3. Ensure clarity, coherence, and proper structure
4. Incorporate provided research and data effectively
5. Maintain consistent tone and voice throughout

When writing:
- Start with a clear introduction that sets context
- Organize content logically with appropriate headings
- Use clear, concise language
- Support claims with evidence from research
- Conclude with key takeaways or next steps

Create content that is informative, engaging, and actionable."""


class WriterAgent(BaseAgent):
    """Agent specialized in content generation and writing.

    This agent takes research findings and requirements to
    produce well-structured, engaging written content.
    """

    def __init__(
        self,
        name: str = "writer",
        model: Optional[BaseChatModel] = None,
    ):
        """Initialize the writer agent.

        Args:
            name: The name of the agent.
            model: Optional LLM model. Uses default if not provided.
        """
        super().__init__(
            name=name,
            system_prompt=WRITER_SYSTEM_PROMPT,
            model=model,
        )

    def process(self, state: AgentState) -> AgentState:
        """Generate content based on research and task requirements.

        Args:
            state: The current agent state with research findings.

        Returns:
            Updated state with draft content.
        """
        task = state.current_task
        research = "\n\n".join(state.research_results) if state.research_results else ""

        # Prepare writing prompt
        writing_prompt = f"""Based on the following task and research, create well-written content:

Task: {task}

Research Findings:
{research if research else "No prior research provided. Please write based on your knowledge."}

Previous feedback (if any):
{state.review_feedback if state.review_feedback else "No previous feedback."}

Please write comprehensive, engaging content that addresses the task requirements."""

        # Invoke LLM for content generation
        draft_content = self.invoke_llm(writing_prompt)

        # Update state with draft
        state.draft_content = draft_content

        # Add message to history
        state = self.add_message_to_state(
            state,
            content=draft_content,
            metadata={"task": task, "agent_type": "writer"},
        )

        return state
