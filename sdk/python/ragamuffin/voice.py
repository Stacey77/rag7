"""
Voice/Retell.ai client for Ragamuffin SDK.
"""

from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .client import RagamuffinClient


class VoiceClient:
    """
    Voice/Retell.ai operations for Ragamuffin API.
    
    Example:
        >>> # Check Retell status
        >>> status = client.voice.status()
        
        >>> # List agents
        >>> agents = client.voice.agents()
        
        >>> # Start a web call
        >>> call = client.voice.create_web_call("agent_id")
    """

    def __init__(self, client: "RagamuffinClient"):
        self._client = client

    def status(self) -> dict:
        """
        Check Retell.ai configuration status.
        
        Returns:
            Configuration status (configured, api_key_set, etc.)
        """
        return self._client.request("GET", "/retell/status")

    def agents(self) -> dict:
        """
        List all Retell.ai agents.
        
        Returns:
            List of agent configurations
        """
        return self._client.request("GET", "/retell/agents")

    def get_agent(self, agent_id: str) -> dict:
        """
        Get details for a specific agent.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent configuration and details
        """
        return self._client.request("GET", f"/retell/agents/{agent_id}")

    def create_web_call(
        self,
        agent_id: str,
        metadata: Optional[dict] = None,
        dynamic_variables: Optional[dict] = None,
    ) -> dict:
        """
        Create a browser-based voice call.
        
        Args:
            agent_id: Retell agent ID
            metadata: Optional call metadata
            dynamic_variables: Optional dynamic variables for the agent
        
        Returns:
            Call information including access_token for web SDK
        """
        data = {"agent_id": agent_id}
        if metadata:
            data["metadata"] = metadata
        if dynamic_variables:
            data["dynamic_variables"] = dynamic_variables
        
        return self._client.request("POST", "/retell/web-call", json=data)

    def create_phone_call(
        self,
        agent_id: str,
        to_phone: str,
        from_phone: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create an outbound phone call.
        
        Args:
            agent_id: Retell agent ID
            to_phone: Destination phone number (E.164 format)
            from_phone: Optional source phone number
            metadata: Optional call metadata
        
        Returns:
            Call information
        """
        data = {
            "agent_id": agent_id,
            "to_phone": to_phone,
        }
        if from_phone:
            data["from_phone"] = from_phone
        if metadata:
            data["metadata"] = metadata
        
        return self._client.request("POST", "/retell/phone-call", json=data)

    def calls(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """
        List call history.
        
        Args:
            limit: Maximum number of calls to return
            offset: Offset for pagination
        
        Returns:
            List of calls with metadata
        """
        params = {"limit": limit, "offset": offset}
        return self._client.request("GET", "/retell/calls", params=params)

    def get_call(self, call_id: str) -> dict:
        """
        Get details for a specific call.
        
        Args:
            call_id: Call ID
        
        Returns:
            Call details including transcript if available
        """
        return self._client.request("GET", f"/retell/calls/{call_id}")

    def end_call(self, call_id: str) -> dict:
        """
        End an ongoing call.
        
        Args:
            call_id: Call ID to end
        
        Returns:
            Confirmation response
        """
        return self._client.request("POST", f"/retell/end-call/{call_id}")

    def voices(self) -> dict:
        """
        List available voices.
        
        Returns:
            List of voice options
        """
        return self._client.request("GET", "/retell/voices")
