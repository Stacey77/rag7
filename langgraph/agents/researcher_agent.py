"""Researcher agent for gathering and analyzing information."""

from typing import Optional

from langchain_core.language_models import BaseChatModel

from langgraph.agents.base_agent import BaseAgent
from langgraph.state.agent_state import AgentState


RESEARCHER_SYSTEM_PROMPT = """You are a skilled research agent specializing in gathering and analyzing information.

Your responsibilities:
1. Research topics thoroughly using available tools and knowledge
2. Gather relevant facts, data, and insights
3. Organize findings in a clear, structured format
4. Provide citations and sources when available
5. Identify key themes and patterns in the information

When researching:
- Be thorough but focused on the task at hand
- Prioritize accuracy and relevance
- Present findings in a logical order
- Note any gaps or limitations in available information

Output your research findings in a structured format that can be used by other agents."""


class ResearcherAgent(BaseAgent):
    """Agent specialized in research and information gathering.

    This agent researches topics, gathers data, and provides
    structured findings for use by other agents in the system.
    """

    def __init__(
        self,
        name: str = "researcher",
        model: Optional[BaseChatModel] = None,
    ):
        """Initialize the researcher agent.

        Args:
            name: The name of the agent.
            model: Optional LLM model. Uses default if not provided.
        """
        super().__init__(
            name=name,
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
            model=model,
        )

    def process(self, state: AgentState) -> AgentState:
        """Conduct research based on the current task.

        Args:
            state: The current agent state with the research task.

        Returns:
            Updated state with research findings.
        """
        task = state.current_task

        # Prepare research prompt
        research_prompt = f"""Please research the following topic and provide comprehensive findings:

Topic: {task}

Provide your research findings including:
1. Key facts and information
2. Relevant context and background
3. Important considerations
4. Sources or references if applicable"""

        # Invoke LLM for research
        research_results = self.invoke_llm(research_prompt)

        # Update state with research results
        state.research_results = state.research_results + [research_results]

        # Add message to history
        state = self.add_message_to_state(
            state,
            content=research_results,
            metadata={"task": task, "agent_type": "researcher"},
        )

        return state
