"""Router agent for directing tasks to appropriate handlers."""

from typing import Literal, Optional

from langchain_core.language_models import BaseChatModel

from langgraph.agents.base_agent import BaseAgent
from langgraph.state.agent_state import AgentState


ROUTER_SYSTEM_PROMPT = """You are an intelligent task router that analyzes incoming requests and directs them to the appropriate specialized handler.

Your responsibilities:
1. Analyze the nature and requirements of incoming tasks
2. Classify tasks into appropriate categories
3. Determine the best processing path
4. Provide reasoning for routing decisions

Available routes:
- research: For tasks requiring information gathering and analysis
- writing: For content creation and documentation tasks
- technical: For code, technical analysis, or development tasks
- creative: For creative content, brainstorming, or ideation
- analysis: For data analysis, reports, or evaluations

When routing:
- Consider the primary objective of the task
- Identify key requirements and skills needed
- Select the most appropriate specialized path
- Explain your routing decision briefly

Output format:
ROUTE: [route_name]
REASON: [brief explanation]"""


class RouterAgent(BaseAgent):
    """Agent specialized in routing tasks to appropriate handlers.

    This agent analyzes incoming tasks and determines the best
    processing path based on task type and requirements.
    """

    VALID_ROUTES = ["research", "writing", "technical", "creative", "analysis"]

    def __init__(
        self,
        name: str = "router",
        model: Optional[BaseChatModel] = None,
    ):
        """Initialize the router agent.

        Args:
            name: The name of the agent.
            model: Optional LLM model. Uses default if not provided.
        """
        super().__init__(
            name=name,
            system_prompt=ROUTER_SYSTEM_PROMPT,
            model=model,
        )

    def process(self, state: AgentState) -> AgentState:
        """Analyze task and determine routing.

        Args:
            state: The current agent state with the task.

        Returns:
            Updated state with routing information.
        """
        task = state.current_task

        # Prepare routing prompt
        routing_prompt = f"""Analyze the following task and determine the appropriate route:

Task: {task}

Available routes: {', '.join(self.VALID_ROUTES)}

Provide your routing decision in the format:
ROUTE: [route_name]
REASON: [brief explanation]"""

        # Invoke LLM for routing decision
        routing_response = self.invoke_llm(routing_prompt)

        # Extract route from response
        route = self._extract_route(routing_response)
        task_type = self._determine_task_type(route)

        # Update state with routing information
        state.route = route
        state.task_type = task_type

        # Add message to history
        state = self.add_message_to_state(
            state,
            content=routing_response,
            metadata={
                "task": task,
                "agent_type": "router",
                "route": route,
                "task_type": task_type,
            },
        )

        return state

    def _extract_route(self, response: str) -> str:
        """Extract route from routing response.

        Args:
            response: The routing response text.

        Returns:
            Extracted route, defaulting to 'research' if not found.
        """
        try:
            if "ROUTE:" in response.upper():
                route_part = response.upper().split("ROUTE:")[1].strip()
                route = route_part.split()[0].strip().lower()
                if route in self.VALID_ROUTES:
                    return route
        except (IndexError, ValueError):
            pass
        return "research"  # Default route

    def _determine_task_type(
        self, route: str
    ) -> Literal["content", "technical", "analysis"]:
        """Map route to a task type category.

        Args:
            route: The determined route.

        Returns:
            Task type category.
        """
        task_type_map = {
            "research": "analysis",
            "writing": "content",
            "technical": "technical",
            "creative": "content",
            "analysis": "analysis",
        }
        return task_type_map.get(route, "content")

    def get_route(self, state: AgentState) -> str:
        """Get the routing decision for graph edge routing.

        Args:
            state: The current agent state.

        Returns:
            The route name for conditional edge routing.
        """
        return state.route or "research"
