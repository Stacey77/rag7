"""Base agent class for the multi-agent system."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langgraph.config import get_settings
from langgraph.state.agent_state import AgentState, Message


class BaseAgent(ABC):
    """Abstract base class for all agents in the system.

    Provides common functionality for agent initialization,
    LLM interaction, and state management.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: Optional[BaseChatModel] = None,
    ):
        """Initialize the base agent.

        Args:
            name: The name of the agent.
            system_prompt: The system prompt defining agent behavior.
            model: Optional LLM model. Uses default if not provided.
        """
        self.name = name
        self.system_prompt = system_prompt
        settings = get_settings()

        if model is None:
            self.model = ChatOpenAI(
                model=settings.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                api_key=settings.openai_api_key or None,
            )
        else:
            self.model = model

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])

    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state.

        Args:
            state: The current agent state.

        Returns:
            Updated agent state after processing.
        """
        pass

    def invoke_llm(self, input_text: str) -> str:
        """Invoke the LLM with the given input.

        Args:
            input_text: The input text for the LLM.

        Returns:
            The LLM response as a string.
        """
        chain = self.prompt_template | self.model
        response = chain.invoke({"input": input_text})
        return response.content

    def add_message_to_state(
        self,
        state: AgentState,
        content: str,
        role: str = "agent",
        metadata: Optional[dict[str, Any]] = None,
    ) -> AgentState:
        """Add a message to the state's message history.

        Args:
            state: The current agent state.
            content: The message content.
            role: The role of the message sender.
            metadata: Optional metadata for the message.

        Returns:
            Updated state with the new message.
        """
        message = Message(
            role=role,
            content=content,
            agent_name=self.name,
            metadata=metadata or {},
        )
        state.messages = state.messages + [message]
        return state

    def __repr__(self) -> str:
        """Return string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
