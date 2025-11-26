"""
GPT-4 Agent Implementation
Interfaces with OpenAI's GPT-4 API for the RAG7 multi-LLM architecture.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from openai import AsyncOpenAI, OpenAIError, APIError, RateLimitError, APIConnectionError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from agents.base import BaseLLMAgent, AgentRequest, AgentResponse


class GPT4Agent(BaseLLMAgent):
    """
    Agent for interfacing with OpenAI's GPT-4 API.
    
    This agent handles:
    - Request forwarding to GPT-4
    - Response processing
    - Error handling with retries
    - Logging of all operations
    """
    
    DEFAULT_MODEL = "gpt-4"
    DEFAULT_MAX_TOKENS = 2048
    DEFAULT_TEMPERATURE = 0.7
    MAX_RETRIES = 3
    
    def __init__(
        self,
        name: str = "gpt4-agent",
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the GPT-4 agent.
        
        Args:
            name: Name of this agent instance
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: GPT model to use (default: gpt-4)
            config: Additional configuration options
        """
        super().__init__(name, config)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            self.logger.error("OpenAI API key not provided")
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.logger.info(f"GPT-4 agent '{name}' initialized with model '{model}'")
    
    def validate_config(self) -> bool:
        """
        Validate that the agent is properly configured.
        
        Returns:
            True if configuration is valid
        """
        if not self.api_key:
            self.logger.error("API key not configured")
            return False
        
        if not self.model:
            self.logger.error("Model not specified")
            return False
        
        return True
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        reraise=True
    )
    async def _call_openai_api(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make the actual API call to OpenAI with retry logic.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            context: Additional context for the request
            
        Returns:
            Dictionary with response data
        """
        messages = []
        
        # Add system context if provided
        if context and "system_message" in context:
            messages.append({
                "role": "system",
                "content": context["system_message"]
            })
        
        # Add the user prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Add conversation history if provided
        if context and "history" in context:
            for msg in context["history"]:
                messages.append(msg)
        
        self.logger.debug(f"Calling OpenAI API with {len(messages)} messages")
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens or self.DEFAULT_MAX_TOKENS,
            temperature=temperature if temperature is not None else self.DEFAULT_TEMPERATURE
        )
        
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens if response.usage else None,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request and return a response.
        
        Args:
            request: The agent request to process
            
        Returns:
            AgentResponse with the result or error information
        """
        start_time = datetime.now()
        
        self.logger.info(f"Processing request: {request.prompt[:100]}...")
        
        try:
            # Validate configuration before processing
            if not self.validate_config():
                raise ValueError("Agent configuration is invalid")
            
            # Call OpenAI API with retry logic
            result = await self._call_openai_api(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                context=request.context
            )
            
            # Create successful response
            response = AgentResponse(
                content=result["content"],
                agent_name=self.name,
                model=result["model"],
                timestamp=datetime.now(),
                tokens_used=result["tokens_used"],
                metadata={
                    "finish_reason": result["finish_reason"],
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    **(request.metadata or {})
                },
                success=True
            )
            
            self.logger.info(
                f"Request processed successfully. "
                f"Tokens: {result['tokens_used']}, "
                f"Time: {response.metadata['processing_time']:.2f}s"
            )
            
            return response
            
        except RateLimitError as e:
            error_msg = f"Rate limit exceeded: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_response(error_msg, start_time)
            
        except APIConnectionError as e:
            error_msg = f"API connection error: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_response(error_msg, start_time)
            
        except APIError as e:
            error_msg = f"OpenAI API error: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_response(error_msg, start_time)
            
        except OpenAIError as e:
            error_msg = f"OpenAI error: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_response(error_msg, start_time)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.exception(error_msg)
            return self._create_error_response(error_msg, start_time)
    
    def _create_error_response(
        self,
        error_msg: str,
        start_time: datetime
    ) -> AgentResponse:
        """
        Create an error response.
        
        Args:
            error_msg: The error message
            start_time: When the request started
            
        Returns:
            AgentResponse indicating failure
        """
        return AgentResponse(
            content="",
            agent_name=self.name,
            model=self.model,
            timestamp=datetime.now(),
            error=error_msg,
            success=False,
            metadata={
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return information about agent capabilities.
        
        Returns:
            Dictionary describing agent capabilities
        """
        capabilities = super().get_capabilities()
        capabilities.update({
            "model": self.model,
            "max_retries": self.MAX_RETRIES,
            "default_max_tokens": self.DEFAULT_MAX_TOKENS,
            "default_temperature": self.DEFAULT_TEMPERATURE,
            "supports_async": True,
            "supports_context": True,
            "supports_history": True
        })
        return capabilities
