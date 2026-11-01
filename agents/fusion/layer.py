"""
Response Fusion Layer
Merges and validates responses from multiple LLM agents.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

from agents.base import AgentResponse


@dataclass
class FusedResponse:
    """Represents a fused response from multiple agents."""
    content: str
    contributing_agents: List[str]
    timestamp: datetime
    confidence: float
    metadata: Dict[str, Any]
    individual_responses: List[AgentResponse]


class ResponseFusionLayer:
    """
    Fusion layer that combines responses from multiple LLM agents.
    
    This layer:
    - Collects responses from parallel agents
    - Validates response quality
    - Merges outputs using configurable strategies
    - Returns a unified response
    """
    
    def __init__(self, strategy: str = "consensus", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the fusion layer.
        
        Args:
            strategy: Fusion strategy ('consensus', 'best', 'weighted', 'concatenate')
            config: Configuration options
        """
        self.strategy = strategy
        self.config = config or {}
        self.logger = logging.getLogger("fusion_layer")
        self.logger.info(f"Fusion layer initialized with strategy: {strategy}")
    
    async def fuse_responses(
        self,
        responses: List[AgentResponse]
    ) -> FusedResponse:
        """
        Fuse multiple agent responses into a single response.
        
        Args:
            responses: List of responses from different agents
            
        Returns:
            FusedResponse containing the merged result
        """
        if not responses:
            raise ValueError("No responses to fuse")
        
        # Filter out failed responses
        successful_responses = [r for r in responses if r.success]
        
        if not successful_responses:
            self.logger.error("All agent responses failed")
            return self._create_failed_fusion(responses)
        
        self.logger.info(
            f"Fusing {len(successful_responses)} successful responses "
            f"out of {len(responses)} total"
        )
        
        # Apply fusion strategy
        if self.strategy == "consensus":
            return await self._consensus_fusion(successful_responses)
        elif self.strategy == "best":
            return await self._best_response_fusion(successful_responses)
        elif self.strategy == "weighted":
            return await self._weighted_fusion(successful_responses)
        elif self.strategy == "concatenate":
            return await self._concatenate_fusion(successful_responses)
        else:
            raise ValueError(f"Unknown fusion strategy: {self.strategy}")
    
    async def _consensus_fusion(
        self,
        responses: List[AgentResponse]
    ) -> FusedResponse:
        """
        Fuse responses by finding consensus/common elements.
        
        For now, this uses a simple approach of selecting the longest response.
        In production, this could use NLP techniques to find common themes.
        """
        # Simple consensus: choose the most comprehensive response
        best_response = max(responses, key=lambda r: len(r.content))
        
        return FusedResponse(
            content=best_response.content,
            contributing_agents=[r.agent_name for r in responses],
            timestamp=datetime.now(),
            confidence=len(responses) / (len(responses) + 1),  # Simple confidence metric
            metadata={
                "strategy": "consensus",
                "num_responses": len(responses),
                "selected_agent": best_response.agent_name
            },
            individual_responses=responses
        )
    
    async def _best_response_fusion(
        self,
        responses: List[AgentResponse]
    ) -> FusedResponse:
        """
        Select the best single response based on quality metrics.
        
        Currently uses token count as a proxy for quality.
        """
        # Select response with most tokens (assumed to be most detailed)
        best_response = max(
            responses,
            key=lambda r: r.tokens_used if r.tokens_used else len(r.content)
        )
        
        return FusedResponse(
            content=best_response.content,
            contributing_agents=[best_response.agent_name],
            timestamp=datetime.now(),
            confidence=0.9,  # High confidence when selecting best
            metadata={
                "strategy": "best",
                "selected_agent": best_response.agent_name,
                "tokens_used": best_response.tokens_used
            },
            individual_responses=responses
        )
    
    async def _weighted_fusion(
        self,
        responses: List[AgentResponse]
    ) -> FusedResponse:
        """
        Fuse responses using weighted combination.
        
        Weights can be configured per agent in the config.
        """
        weights = self.config.get("weights", {})
        
        # For text, we'll select based on weighted preference
        weighted_responses = []
        for response in responses:
            weight = weights.get(response.agent_name, 1.0)
            weighted_responses.append((response, weight))
        
        # Select highest weighted response
        best_response = max(weighted_responses, key=lambda x: x[1])[0]
        
        return FusedResponse(
            content=best_response.content,
            contributing_agents=[r.agent_name for r in responses],
            timestamp=datetime.now(),
            confidence=0.85,
            metadata={
                "strategy": "weighted",
                "selected_agent": best_response.agent_name,
                "weights": weights
            },
            individual_responses=responses
        )
    
    async def _concatenate_fusion(
        self,
        responses: List[AgentResponse]
    ) -> FusedResponse:
        """
        Concatenate all responses together.
        """
        separator = self.config.get("separator", "\n\n---\n\n")
        
        combined_content = separator.join([
            f"From {r.agent_name}:\n{r.content}"
            for r in responses
        ])
        
        return FusedResponse(
            content=combined_content,
            contributing_agents=[r.agent_name for r in responses],
            timestamp=datetime.now(),
            confidence=0.8,
            metadata={
                "strategy": "concatenate",
                "num_responses": len(responses)
            },
            individual_responses=responses
        )
    
    def _create_failed_fusion(
        self,
        responses: List[AgentResponse]
    ) -> FusedResponse:
        """
        Create a fusion response when all agents failed.
        """
        error_summary = "\n".join([
            f"{r.agent_name}: {r.error}"
            for r in responses if r.error
        ])
        
        return FusedResponse(
            content=f"All agents failed to process the request.\n\nErrors:\n{error_summary}",
            contributing_agents=[],
            timestamp=datetime.now(),
            confidence=0.0,
            metadata={
                "strategy": self.strategy,
                "all_failed": True,
                "num_failures": len(responses)
            },
            individual_responses=responses
        )
    
    def validate_response(self, response: AgentResponse) -> bool:
        """
        Validate a single agent response.
        
        Args:
            response: Response to validate
            
        Returns:
            True if response is valid
        """
        if not response.success:
            self.logger.warning(f"Response from {response.agent_name} failed: {response.error}")
            return False
        
        if not response.content or len(response.content.strip()) == 0:
            self.logger.warning(f"Response from {response.agent_name} is empty")
            return False
        
        return True
