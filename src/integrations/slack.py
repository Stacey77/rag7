"""Slack integration for sending messages and managing channels."""
import logging
from typing import Any, Dict, List, Optional

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from .base import BaseIntegration, IntegrationFunction, FunctionParameter

logger = logging.getLogger(__name__)


class SlackIntegration(BaseIntegration):
    """
    Slack integration using slack_sdk for async operations.
    
    Required configuration:
    - slack_bot_token: Bot User OAuth Token (xoxb-...)
    
    Setup instructions:
    1. Create a Slack App at https://api.slack.com/apps
    2. Add Bot Token Scopes: chat:write, channels:read, users:read
    3. Install app to workspace and copy Bot User OAuth Token
    4. Add token to .env as SLACK_BOT_TOKEN
    
    Documentation: https://api.slack.com/docs
    """
    
    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize Slack integration.
        
        Args:
            bot_token: Slack bot token (xoxb-...). If None, integration will be disabled.
        """
        super().__init__()
        self.bot_token = bot_token
        self.client: Optional[AsyncWebClient] = None
        
        if self.bot_token:
            self.client = AsyncWebClient(token=self.bot_token)
            logger.info("Slack integration initialized with bot token")
        else:
            logger.warning("Slack integration initialized without bot token - integration disabled")
    
    def get_functions(self) -> List[IntegrationFunction]:
        """Get available Slack functions."""
        return [
            IntegrationFunction(
                name="send_message",
                description="Send a message to a Slack channel",
                parameters=[
                    FunctionParameter(
                        name="channel",
                        type="string",
                        description="Channel ID or name (e.g., #general or C1234567890)",
                        required=True
                    ),
                    FunctionParameter(
                        name="text",
                        type="string",
                        description="Message text to send",
                        required=True
                    ),
                    FunctionParameter(
                        name="thread_ts",
                        type="string",
                        description="Optional thread timestamp to reply in a thread",
                        required=False
                    )
                ]
            ),
            IntegrationFunction(
                name="list_channels",
                description="List all channels in the workspace",
                parameters=[
                    FunctionParameter(
                        name="limit",
                        type="integer",
                        description="Maximum number of channels to return (default: 100)",
                        required=False
                    )
                ]
            )
        ]
    
    async def execute(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a Slack function.
        
        Args:
            function_name: Name of function (send_message, list_channels)
            **kwargs: Function arguments
            
        Returns:
            Result dictionary with success, data, and optional error
        """
        if not self.client:
            return {
                "success": False,
                "error": "Slack integration not configured - missing bot token",
                "data": None
            }
        
        try:
            if function_name == "send_message":
                return await self._send_message(**kwargs)
            elif function_name == "list_channels":
                return await self._list_channels(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}",
                    "data": None
                }
        except SlackApiError as e:
            logger.error(f"Slack API error in {function_name}: {e}")
            return {
                "success": False,
                "error": f"Slack API error: {e.response['error']}",
                "data": None
            }
        except Exception as e:
            logger.error(f"Unexpected error in {function_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def _send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Channel ID or name
            text: Message text
            thread_ts: Optional thread timestamp for replies
            
        Returns:
            Result with message details
        """
        # Remove # prefix if present
        if channel.startswith("#"):
            channel = channel[1:]
        
        response = await self.client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        
        return {
            "success": True,
            "data": {
                "channel": response["channel"],
                "timestamp": response["ts"],
                "message": text
            },
            "error": None
        }
    
    async def _list_channels(self, limit: int = 100) -> Dict[str, Any]:
        """
        List channels in the workspace.
        
        Args:
            limit: Maximum number of channels to return
            
        Returns:
            Result with list of channels
        """
        response = await self.client.conversations_list(
            limit=limit,
            exclude_archived=True
        )
        
        channels = [
            {
                "id": ch["id"],
                "name": ch["name"],
                "is_private": ch.get("is_private", False)
            }
            for ch in response["channels"]
        ]
        
        return {
            "success": True,
            "data": {"channels": channels},
            "error": None
        }
    
    async def health_check(self) -> bool:
        """Check if Slack integration is healthy."""
        if not self.client:
            return False
        
        try:
            response = await self.client.auth_test()
            return response["ok"]
        except Exception as e:
            logger.error(f"Slack health check failed: {e}")
            return False
