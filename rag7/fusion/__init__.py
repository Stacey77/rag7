"""Response fusion layer for combining outputs from multiple LLMs."""
from typing import List, Optional
from collections import Counter
import difflib
from rag7.models import (
    LLMResponse, FusedResponse, FusionStrategy
)
from rag7.config import config_manager


class ResponseFusion:
    """Combines and validates outputs from multiple agents."""
    
    def __init__(self):
        self.config = config_manager.get_fusion_config()
    
    def fuse_responses(
        self,
        responses: List[LLMResponse],
        strategy: Optional[FusionStrategy] = None
    ) -> FusedResponse:
        """Fuse multiple responses using specified strategy."""
        if not responses:
            raise ValueError("No responses to fuse")
        
        if len(responses) == 1:
            return self._single_response_fusion(responses[0])
        
        fusion_strategy = strategy or FusionStrategy(self.config.default_strategy)
        
        if fusion_strategy == FusionStrategy.VOTING:
            return self._voting_fusion(responses)
        elif fusion_strategy == FusionStrategy.RANKING:
            return self._ranking_fusion(responses)
        elif fusion_strategy == FusionStrategy.MERGING:
            return self._merging_fusion(responses)
        elif fusion_strategy == FusionStrategy.FIRST:
            return self._first_fusion(responses)
        else:
            raise ValueError(f"Unknown fusion strategy: {fusion_strategy}")
    
    def _single_response_fusion(self, response: LLMResponse) -> FusedResponse:
        """Handle single response case."""
        return FusedResponse(
            final_content=response.content,
            individual_responses=[response],
            fusion_strategy=FusionStrategy.FIRST,
            total_cost=response.cost,
            total_latency_ms=response.latency_ms,
            confidence_score=1.0
        )
    
    def _voting_fusion(self, responses: List[LLMResponse]) -> FusedResponse:
        """Use voting to select most common response."""
        # Calculate similarity between responses
        contents = [r.content for r in responses]
        
        # Find most similar group of responses
        similarity_scores = {}
        for i, content in enumerate(contents):
            similarity_scores[i] = 0
            for j, other_content in enumerate(contents):
                if i != j:
                    ratio = difflib.SequenceMatcher(None, content, other_content).ratio()
                    similarity_scores[i] += ratio
        
        # Select response with highest total similarity
        best_idx = max(similarity_scores, key=similarity_scores.get)
        selected_response = responses[best_idx]
        
        # Calculate confidence based on agreement
        max_score = similarity_scores[best_idx]
        confidence = max_score / (len(responses) - 1) if len(responses) > 1 else 1.0
        
        total_cost = sum(r.cost for r in responses)
        total_latency = sum(r.latency_ms for r in responses)
        
        return FusedResponse(
            final_content=selected_response.content,
            individual_responses=responses,
            fusion_strategy=FusionStrategy.VOTING,
            total_cost=total_cost,
            total_latency_ms=total_latency,
            confidence_score=min(confidence, 1.0),
            metadata={
                "selected_provider": selected_response.provider.value,
                "similarity_scores": similarity_scores
            }
        )
    
    def _ranking_fusion(self, responses: List[LLMResponse]) -> FusedResponse:
        """Rank responses based on quality metrics and provider weights."""
        weights = self.config.weights
        
        # Score each response
        scored_responses = []
        for response in responses:
            provider_weight = weights.get(response.provider.value, 1.0)
            
            # Quality score based on length, provider weight, and cost efficiency
            content_length_score = min(len(response.content) / 1000, 1.0)
            cost_efficiency = 1.0 / (response.cost + 0.001)  # Avoid division by zero
            
            score = (provider_weight * 0.5 + 
                    content_length_score * 0.3 + 
                    cost_efficiency * 0.2)
            
            scored_responses.append((score, response))
        
        # Sort by score descending
        scored_responses.sort(key=lambda x: x[0], reverse=True)
        best_response = scored_responses[0][1]
        best_score = scored_responses[0][0]
        
        total_cost = sum(r.cost for r in responses)
        total_latency = sum(r.latency_ms for r in responses)
        
        return FusedResponse(
            final_content=best_response.content,
            individual_responses=responses,
            fusion_strategy=FusionStrategy.RANKING,
            total_cost=total_cost,
            total_latency_ms=total_latency,
            confidence_score=min(best_score, 1.0),
            metadata={
                "selected_provider": best_response.provider.value,
                "ranking_scores": {r[1].provider.value: r[0] for r in scored_responses}
            }
        )
    
    def _merging_fusion(self, responses: List[LLMResponse]) -> FusedResponse:
        """Merge multiple responses into a comprehensive answer."""
        # Combine responses with attribution
        merged_content = "# Synthesized Response from Multiple LLMs\n\n"
        
        for i, response in enumerate(responses, 1):
            merged_content += f"## Response from {response.provider.value} ({response.model})\n"
            merged_content += f"{response.content}\n\n"
        
        # Add summary section
        merged_content += "## Summary\n"
        merged_content += "This response combines insights from multiple AI models. "
        merged_content += f"Consulted {len(responses)} models: "
        merged_content += ", ".join([r.provider.value for r in responses])
        merged_content += ".\n"
        
        total_cost = sum(r.cost for r in responses)
        total_latency = sum(r.latency_ms for r in responses)
        
        return FusedResponse(
            final_content=merged_content,
            individual_responses=responses,
            fusion_strategy=FusionStrategy.MERGING,
            total_cost=total_cost,
            total_latency_ms=total_latency,
            confidence_score=0.9,  # High confidence for merged responses
            metadata={
                "providers_consulted": [r.provider.value for r in responses]
            }
        )
    
    def _first_fusion(self, responses: List[LLMResponse]) -> FusedResponse:
        """Return the first successful response."""
        first_response = responses[0]
        
        total_cost = sum(r.cost for r in responses)
        total_latency = sum(r.latency_ms for r in responses)
        
        return FusedResponse(
            final_content=first_response.content,
            individual_responses=responses,
            fusion_strategy=FusionStrategy.FIRST,
            total_cost=total_cost,
            total_latency_ms=total_latency,
            confidence_score=0.8,
            metadata={
                "selected_provider": first_response.provider.value
            }
        )


# Global fusion instance
response_fusion = ResponseFusion()
