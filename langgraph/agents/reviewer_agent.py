"""Reviewer agent for quality review and feedback."""

from typing import Optional

from langchain_core.language_models import BaseChatModel

from langgraph.agents.base_agent import BaseAgent
from langgraph.state.agent_state import AgentState


REVIEWER_SYSTEM_PROMPT = """You are a meticulous content reviewer and editor with expertise in quality assurance.

Your responsibilities:
1. Review content for accuracy, clarity, and completeness
2. Check for logical flow and coherent structure
3. Identify areas that need improvement or clarification
4. Provide constructive feedback with specific suggestions
5. Assess overall quality and readiness for publication

When reviewing:
- Be thorough but constructive
- Provide specific, actionable feedback
- Acknowledge strengths as well as areas for improvement
- Consider the target audience and purpose
- Rate content quality on a scale of 0.0 to 1.0

Your output should include:
1. Overall quality score (0.0 to 1.0)
2. Strengths of the content
3. Areas for improvement
4. Specific suggestions for revision
5. Final recommendation (approve/revise)"""


class ReviewerAgent(BaseAgent):
    """Agent specialized in content review and quality feedback.

    This agent reviews draft content, provides feedback,
    and assesses quality for iterative improvement.
    """

    def __init__(
        self,
        name: str = "reviewer",
        model: Optional[BaseChatModel] = None,
        quality_threshold: float = 0.8,
    ):
        """Initialize the reviewer agent.

        Args:
            name: The name of the agent.
            model: Optional LLM model. Uses default if not provided.
            quality_threshold: Minimum quality score for approval.
        """
        super().__init__(
            name=name,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            model=model,
        )
        self.quality_threshold = quality_threshold

    def process(self, state: AgentState) -> AgentState:
        """Review content and provide feedback.

        Args:
            state: The current agent state with draft content.

        Returns:
            Updated state with review feedback and quality score.
        """
        task = state.current_task
        draft = state.draft_content

        # Prepare review prompt
        review_prompt = f"""Please review the following content:

Original Task: {task}

Content to Review:
{draft}

Iteration: {state.iteration_count + 1}

Provide:
1. Quality score (0.0 to 1.0) - Start your response with "SCORE: X.X"
2. Strengths
3. Areas for improvement
4. Specific revision suggestions
5. Final recommendation"""

        # Invoke LLM for review
        review_response = self.invoke_llm(review_prompt)

        # Extract quality score from response
        quality_score = self._extract_quality_score(review_response)

        # Update state with review feedback
        state.review_feedback = review_response
        state.quality_score = quality_score
        state.iteration_count = state.iteration_count + 1

        # Add message to history
        state = self.add_message_to_state(
            state,
            content=review_response,
            metadata={
                "task": task,
                "agent_type": "reviewer",
                "quality_score": quality_score,
                "iteration": state.iteration_count,
            },
        )

        return state

    def _extract_quality_score(self, response: str) -> float:
        """Extract quality score from review response.

        Args:
            response: The review response text.

        Returns:
            Extracted quality score, defaulting to 0.5 if not found.
        """
        try:
            # Look for "SCORE: X.X" pattern
            if "SCORE:" in response.upper():
                score_part = response.upper().split("SCORE:")[1].strip()
                score_str = score_part.split()[0].strip()
                score = float(score_str)
                return max(0.0, min(1.0, score))  # Clamp to 0-1
        except (IndexError, ValueError):
            pass
        return 0.5  # Default score if extraction fails

    def should_continue_loop(self, state: AgentState) -> bool:
        """Determine if the loop should continue based on quality.

        Args:
            state: The current agent state.

        Returns:
            True if quality threshold not met and iterations remaining.
        """
        if state.quality_score >= self.quality_threshold:
            return False
        if state.iteration_count >= state.max_iterations:
            return False
        return True
