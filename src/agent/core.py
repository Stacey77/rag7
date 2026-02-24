"""Core conversational agent with OpenAI function calling."""
import logging
from typing import Any, Dict, List, Optional
import json

from openai import AsyncOpenAI

from .memory import AgentMemory
from ..integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    Conversational agent with OpenAI function calling and integration support.
    
    This agent:
    1. Maintains conversation context in memory
    2. Integrates with external services (Slack, Gmail, Notion)
    3. Uses OpenAI function calling to execute tools
    4. Provides a natural language interface to all capabilities
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        integrations: Optional[List[BaseIntegration]] = None,
        memory: Optional[AgentMemory] = None
    ):
        """
        Initialize the conversational agent.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            integrations: List of integration instances
            memory: Agent memory instance (creates new if None)
        """
        self.api_key = api_key
        self.model = model
        self.integrations = integrations or []
        self.memory = memory or AgentMemory(use_chromadb=False)
        
        # Initialize OpenAI client
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"Conversational agent initialized with model: {model}")
        else:
            self.client = None
            logger.warning("Conversational agent initialized without OpenAI API key")
        
        # Build function definitions from integrations
        self.functions = self._build_functions()
    
    def _build_functions(self) -> List[Dict[str, Any]]:
        """
        Build OpenAI function definitions from integrations.
        
        Returns:
            List of function definitions
        """
        functions = []
        for integration in self.integrations:
            integration_functions = integration.to_openai_functions()
            functions.extend(integration_functions)
            logger.debug(f"Loaded {len(integration_functions)} functions from {integration.name}")
        
        return functions
    
    def register_integration(self, integration: BaseIntegration):
        """
        Register a new integration with the agent.
        
        Args:
            integration: Integration instance to register
        """
        self.integrations.append(integration)
        self.functions = self._build_functions()
        logger.info(f"Registered integration: {integration.name}")
    
    async def chat(
        self,
        message: str,
        user_id: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Process a chat message and execute any required functions.
        
        This method:
        1. Adds user message to memory
        2. Calls OpenAI with conversation context and available functions
        3. Executes any function calls requested by the model
        4. Returns the assistant's response
        
        Args:
            message: User message
            user_id: Optional user identifier
            max_iterations: Maximum function calling iterations
            
        Returns:
            Response dictionary with:
            - response: Assistant's text response
            - function_calls: List of executed functions
            - error: Error message if any
        """
        if not self.client:
            return {
                "response": "Error: OpenAI API key not configured",
                "function_calls": [],
                "error": "Missing API key"
            }
        
        # Add user message to memory
        await self.memory.add_message(
            role="user",
            content=message,
            metadata={"user_id": user_id} if user_id else None
        )
        
        # Get conversation context
        messages = await self.memory.get_recent_messages(limit=10)
        openai_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]
        
        # Add system message if not present
        if not any(m["role"] == "system" for m in openai_messages):
            openai_messages.insert(0, {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant with access to various integrations. "
                    "You can send Slack messages, manage Gmail emails, and interact with Notion. "
                    "Use the available functions when appropriate to help the user."
                )
            })
        
        function_calls_executed = []
        
        # Iterate with function calling
        for iteration in range(max_iterations):
            try:
                # Call OpenAI
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    functions=self.functions if self.functions else None,
                    function_call="auto" if self.functions else None
                )
                
                message_response = response.choices[0].message
                
                # Check if function call is requested
                if message_response.function_call:
                    function_name = message_response.function_call.name
                    function_args = json.loads(message_response.function_call.arguments)
                    
                    logger.info(f"Executing function: {function_name} with args: {function_args}")
                    
                    # Execute the function
                    result = await self._execute_function(function_name, function_args)
                    
                    function_calls_executed.append({
                        "function": function_name,
                        "arguments": function_args,
                        "result": result
                    })
                    
                    # Add function call and result to messages
                    openai_messages.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": json.dumps(function_args)
                        }
                    })
                    openai_messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                    
                    # Continue iteration to get final response
                    continue
                
                # No function call - we have the final response
                assistant_message = message_response.content or ""
                
                # Add to memory
                await self.memory.add_message(
                    role="assistant",
                    content=assistant_message,
                    metadata={"user_id": user_id} if user_id else None
                )
                
                return {
                    "response": assistant_message,
                    "function_calls": function_calls_executed,
                    "error": None
                }
                
            except Exception as e:
                logger.error(f"Error in chat iteration {iteration}: {e}")
                return {
                    "response": f"Error: {str(e)}",
                    "function_calls": function_calls_executed,
                    "error": str(e)
                }
        
        # Max iterations reached
        return {
            "response": "Max function calling iterations reached",
            "function_calls": function_calls_executed,
            "error": "Max iterations exceeded"
        }
    
    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a function from an integration.
        
        Args:
            function_name: Function name in format "integration_function"
            arguments: Function arguments
            
        Returns:
            Function result
        """
        # Parse integration name and function name
        parts = function_name.split("_", 1)
        if len(parts) != 2:
            return {
                "success": False,
                "error": f"Invalid function name format: {function_name}",
                "data": None
            }
        
        integration_name, func_name = parts
        
        # Find the integration
        integration = None
        for integ in self.integrations:
            if integ.name == integration_name:
                integration = integ
                break
        
        if not integration:
            return {
                "success": False,
                "error": f"Integration not found: {integration_name}",
                "data": None
            }
        
        # Execute the function
        try:
            result = await integration.execute(func_name, **arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing {function_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Get list of all available functions from integrations.
        
        Returns:
            List of function metadata
        """
        available = []
        for integration in self.integrations:
            for func in integration.get_functions():
                available.append({
                    "integration": integration.name,
                    "name": func.name,
                    "full_name": f"{integration.name}_{func.name}",
                    "description": func.description,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type,
                            "description": p.description,
                            "required": p.required
                        }
                        for p in func.parameters
                    ]
                })
        return available
    
    async def get_integrations_status(self) -> List[Dict[str, Any]]:
        """
        Get health status of all integrations.
        
        Returns:
            List of integration status info
        """
        statuses = []
        for integration in self.integrations:
            is_healthy = await integration.health_check()
            statuses.append({
                "name": integration.name,
                "healthy": is_healthy,
                "functions_count": len(integration.get_functions())
            })
        return statuses
