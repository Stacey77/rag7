"""
Retell.ai Voice AI Integration

This module provides integration with Retell.ai for voice-based AI conversations.
Retell.ai enables real-time voice AI with:
- Conversational AI phone calls
- Voice synthesis (TTS)
- Speech recognition (STT)
- Low-latency responses

⚠️ SECURITY NOTE:
- Store RETELL_API_KEY securely (never commit to repo)
- Use webhook signatures to verify callback authenticity
- Implement rate limiting on call endpoints
- Log all call events for audit

Documentation: https://docs.retell.ai/
"""

import os
import json
import logging
import hmac
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import httpx

logger = logging.getLogger(__name__)

# Retell.ai Configuration
RETELL_API_KEY = os.getenv("RETELL_API_KEY", "")
RETELL_API_BASE = "https://api.retellai.com"
RETELL_WEBHOOK_SECRET = os.getenv("RETELL_WEBHOOK_SECRET", "")


# ============================================================================
# Pydantic Models
# ============================================================================

class RetellAgent(BaseModel):
    """Retell AI Agent configuration"""
    agent_id: str
    agent_name: str
    voice_id: Optional[str] = None
    language: str = "en-US"
    ambient_sound: Optional[str] = None
    responsiveness: float = Field(default=1.0, ge=0.0, le=1.0)
    interruption_sensitivity: float = Field(default=1.0, ge=0.0, le=1.0)
    enable_backchannel: bool = True
    backchannel_frequency: float = Field(default=0.8, ge=0.0, le=1.0)
    backchannel_words: List[str] = Field(default_factory=lambda: ["yeah", "uh-huh", "ok"])
    reminder_trigger_ms: int = Field(default=10000, ge=1000, le=60000)
    reminder_max_count: int = Field(default=1, ge=0, le=5)
    boosted_keywords: List[str] = Field(default_factory=list)
    enable_voicemail_detection: bool = False
    webhook_url: Optional[str] = None
    post_call_analysis_data: List[str] = Field(default_factory=list)


class RetellCall(BaseModel):
    """Retell call information"""
    call_id: str
    agent_id: str
    call_status: str  # registered, ongoing, ended, error
    call_type: str  # web_call, phone_call
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    direction: Optional[str] = None  # inbound, outbound
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    disconnection_reason: Optional[str] = None


class CreateWebCallRequest(BaseModel):
    """Request to create a web-based call"""
    agent_id: str
    metadata: Optional[Dict[str, Any]] = None
    retell_llm_dynamic_variables: Optional[Dict[str, str]] = None


class CreatePhoneCallRequest(BaseModel):
    """Request to create a phone call"""
    agent_id: str
    from_number: str
    to_number: str
    metadata: Optional[Dict[str, Any]] = None
    retell_llm_dynamic_variables: Optional[Dict[str, str]] = None


class RegisterCallResponse(BaseModel):
    """Response from call registration"""
    call_id: str
    agent_id: str
    access_token: str  # WebSocket access token for web calls
    call_status: str


class WebhookEvent(BaseModel):
    """Retell webhook event"""
    event: str  # call_started, call_ended, call_analyzed
    call: Dict[str, Any]
    timestamp: int


# ============================================================================
# Retell API Client
# ============================================================================

class RetellClient:
    """
    Client for Retell.ai API
    
    Usage:
        client = RetellClient()
        
        # Create a web call
        call = await client.create_web_call(agent_id="agent_xxx")
        
        # Get call details
        call_info = await client.get_call(call.call_id)
        
        # List agents
        agents = await client.list_agents()
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or RETELL_API_KEY
        if not self.api_key:
            logger.warning("⚠️  RETELL_API_KEY not configured - Retell.ai features disabled")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def is_configured(self) -> bool:
        """Check if Retell is configured"""
        return bool(self.api_key)
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request to Retell"""
        if not self.is_configured:
            raise ValueError("Retell API key not configured")
        
        url = f"{RETELL_API_BASE}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code >= 400:
                logger.error(f"Retell API error: {response.status_code} - {response.text}")
                raise httpx.HTTPStatusError(
                    f"Retell API error: {response.text}",
                    request=response.request,
                    response=response
                )
            
            return response.json() if response.text else {}
    
    # -------------------------------------------------------------------------
    # Agent Management
    # -------------------------------------------------------------------------
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all Retell agents"""
        return await self._request("GET", "/list-agents")
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details"""
        return await self._request("GET", f"/get-agent/{agent_id}")
    
    async def create_agent(
        self,
        agent_name: str,
        llm_websocket_url: str,
        voice_id: str = "eleven_turbo_v2",
        language: str = "en-US",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new Retell agent
        
        Args:
            agent_name: Name for the agent
            llm_websocket_url: WebSocket URL for LLM responses
            voice_id: Voice to use for TTS
            language: Language code
            **kwargs: Additional agent configuration
        """
        data = {
            "agent_name": agent_name,
            "llm_websocket_url": llm_websocket_url,
            "voice_id": voice_id,
            "language": language,
            **kwargs
        }
        return await self._request("POST", "/create-agent", data)
    
    async def update_agent(
        self, 
        agent_id: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Update agent configuration"""
        return await self._request("PATCH", f"/update-agent/{agent_id}", kwargs)
    
    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent"""
        return await self._request("DELETE", f"/delete-agent/{agent_id}")
    
    # -------------------------------------------------------------------------
    # Call Management
    # -------------------------------------------------------------------------
    
    async def create_web_call(
        self,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        retell_llm_dynamic_variables: Optional[Dict[str, str]] = None
    ) -> RegisterCallResponse:
        """
        Create a web-based call (browser-based voice conversation)
        
        Returns an access token for WebSocket connection
        """
        data = {
            "agent_id": agent_id,
        }
        if metadata:
            data["metadata"] = metadata
        if retell_llm_dynamic_variables:
            data["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables
        
        response = await self._request("POST", "/v2/create-web-call", data)
        
        return RegisterCallResponse(
            call_id=response["call_id"],
            agent_id=response["agent_id"],
            access_token=response["access_token"],
            call_status="registered"
        )
    
    async def create_phone_call(
        self,
        agent_id: str,
        from_number: str,
        to_number: str,
        metadata: Optional[Dict[str, Any]] = None,
        retell_llm_dynamic_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create an outbound phone call
        
        Requires a verified phone number on your Retell account
        """
        data = {
            "agent_id": agent_id,
            "from_number": from_number,
            "to_number": to_number,
        }
        if metadata:
            data["metadata"] = metadata
        if retell_llm_dynamic_variables:
            data["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables
        
        return await self._request("POST", "/v2/create-phone-call", data)
    
    async def get_call(self, call_id: str) -> RetellCall:
        """Get call details including transcript"""
        response = await self._request("GET", f"/v2/get-call/{call_id}")
        
        return RetellCall(
            call_id=response["call_id"],
            agent_id=response["agent_id"],
            call_status=response.get("call_status", "unknown"),
            call_type=response.get("call_type", "unknown"),
            from_number=response.get("from_number"),
            to_number=response.get("to_number"),
            direction=response.get("direction"),
            start_timestamp=response.get("start_timestamp"),
            end_timestamp=response.get("end_timestamp"),
            transcript=response.get("transcript"),
            recording_url=response.get("recording_url"),
            disconnection_reason=response.get("disconnection_reason")
        )
    
    async def list_calls(
        self,
        filter_criteria: Optional[Dict[str, Any]] = None,
        sort_order: str = "descending",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List calls with optional filtering"""
        data = {
            "sort_order": sort_order,
            "limit": limit
        }
        if filter_criteria:
            data["filter_criteria"] = filter_criteria
        
        return await self._request("POST", "/v2/list-calls", data)
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End an ongoing call"""
        return await self._request("POST", f"/v2/end-call/{call_id}")
    
    # -------------------------------------------------------------------------
    # Phone Number Management
    # -------------------------------------------------------------------------
    
    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        """List all phone numbers"""
        return await self._request("GET", "/list-phone-numbers")
    
    async def get_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Get phone number details"""
        return await self._request("GET", f"/get-phone-number/{phone_number}")
    
    async def import_phone_number(
        self,
        phone_number: str,
        termination_uri: str
    ) -> Dict[str, Any]:
        """Import an existing phone number"""
        data = {
            "phone_number": phone_number,
            "termination_uri": termination_uri
        }
        return await self._request("POST", "/import-phone-number", data)
    
    # -------------------------------------------------------------------------
    # Voice Management
    # -------------------------------------------------------------------------
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices"""
        return await self._request("GET", "/list-voices")


# ============================================================================
# Webhook Verification
# ============================================================================

def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: Optional[str] = None
) -> bool:
    """
    Verify Retell webhook signature
    
    SECURITY: Always verify webhooks to prevent spoofing attacks
    """
    secret = secret or RETELL_WEBHOOK_SECRET
    if not secret:
        logger.warning("Webhook secret not configured - skipping verification")
        return True  # Skip verification if no secret
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


def parse_webhook_event(payload: Dict[str, Any]) -> WebhookEvent:
    """Parse webhook event from Retell"""
    return WebhookEvent(
        event=payload.get("event", "unknown"),
        call=payload.get("call", {}),
        timestamp=payload.get("timestamp", int(datetime.now().timestamp() * 1000))
    )


# ============================================================================
# Singleton Client
# ============================================================================

# Global client instance
_client: Optional[RetellClient] = None


def get_retell_client() -> RetellClient:
    """Get or create Retell client singleton"""
    global _client
    if _client is None:
        _client = RetellClient()
    return _client


# ============================================================================
# Utility Functions
# ============================================================================

def format_phone_number(number: str) -> str:
    """Format phone number to E.164 format"""
    # Remove non-digits
    digits = ''.join(filter(str.isdigit, number))
    
    # Add country code if missing
    if len(digits) == 10:  # US number without country code
        digits = "1" + digits
    
    return "+" + digits


def mask_phone_number(number: str) -> str:
    """Mask phone number for logging (show last 4 digits)"""
    if len(number) > 4:
        return "*" * (len(number) - 4) + number[-4:]
    return number
