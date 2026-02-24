"""Base integration class for all external service integrations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class FunctionParameter(BaseModel):
    """Schema for function parameters."""
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


class IntegrationFunction(BaseModel):
    """Schema for integration function definition."""
    name: str
    description: str
    parameters: List[FunctionParameter]


class BaseIntegration(ABC):
    """
    Abstract base class for all integrations.
    
    Each integration should:
    1. Inherit from this class
    2. Implement the execute() method
    3. Define available functions via get_functions()
    4. Convert functions to OpenAI format via to_openai_functions()
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the integration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace("Integration", "").lower()
    
    @abstractmethod
    async def execute(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a function from this integration.
        
        Args:
            function_name: Name of the function to execute
            **kwargs: Function arguments
            
        Returns:
            Result dictionary with 'success', 'data', and optional 'error' keys
        """
        pass
    
    @abstractmethod
    def get_functions(self) -> List[IntegrationFunction]:
        """
        Get list of available functions in this integration.
        
        Returns:
            List of IntegrationFunction objects
        """
        pass
    
    def to_openai_functions(self) -> List[Dict[str, Any]]:
        """
        Convert integration functions to OpenAI function calling format.
        
        Returns:
            List of function definitions in OpenAI format
        """
        openai_functions = []
        
        for func in self.get_functions():
            # Build properties dict for parameters
            properties = {}
            required = []
            
            for param in func.parameters:
                param_def = {
                    "type": param.type,
                    "description": param.description
                }
                if param.enum:
                    param_def["enum"] = param.enum
                
                properties[param.name] = param_def
                
                if param.required:
                    required.append(param.name)
            
            # Build OpenAI function definition
            openai_func = {
                "name": f"{self.name}_{func.name}",
                "description": func.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
            
            openai_functions.append(openai_func)
        
        return openai_functions
    
    async def health_check(self) -> bool:
        """
        Check if the integration is properly configured and accessible.
        
        Returns:
            True if integration is healthy, False otherwise
        """
        # Default implementation - can be overridden by subclasses
        return True
