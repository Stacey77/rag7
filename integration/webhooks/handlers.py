"""Webhook handlers for n8n integration."""

from datetime import datetime
from typing import Any, Callable, Optional
import hashlib
import hmac

from pydantic import BaseModel, Field


class TaskWebhook(BaseModel):
    """Webhook payload for task execution."""

    task: str
    pattern: str = "sequential"
    callback_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class ApprovalWebhook(BaseModel):
    """Webhook payload for human approval."""

    task_id: str
    approved: bool
    feedback: Optional[str] = None
    approver: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class WebhookHandler:
    """Handler for incoming webhooks from n8n.

    This class manages webhook processing, including
    signature validation and callback execution.
    """

    def __init__(self, secret: Optional[str] = None):
        """Initialize the webhook handler.

        Args:
            secret: Optional secret for webhook signature validation.
        """
        self.secret = secret
        self._callbacks: dict[str, Callable] = {}

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for a specific event type.

        Args:
            event_type: Type of webhook event.
            callback: Function to call when event is received.
        """
        self._callbacks[event_type] = callback

    def validate_signature(self, payload: bytes, signature: str) -> bool:
        """Validate webhook signature for security.

        Args:
            payload: Raw webhook payload.
            signature: Signature from the request header.

        Returns:
            True if signature is valid, False otherwise.
        """
        if not self.secret:
            return True  # No validation if secret not configured

        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def handle_task_webhook(self, webhook: TaskWebhook) -> dict[str, Any]:
        """Handle an incoming task webhook.

        Args:
            webhook: The task webhook payload.

        Returns:
            Response containing task execution result.
        """
        from langgraph.main import run_pattern

        try:
            result = run_pattern(webhook.pattern, webhook.task)

            response = {
                "success": True,
                "task": webhook.task,
                "pattern": webhook.pattern,
                "final_output": result.get("final_output", ""),
                "quality_score": result.get("quality_score", 0.0),
                "timestamp": datetime.now().isoformat(),
            }

            # Execute callback if registered
            if "task_complete" in self._callbacks:
                await self._callbacks["task_complete"](response)

            return response

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def handle_approval_webhook(self, webhook: ApprovalWebhook) -> dict[str, Any]:
        """Handle an approval webhook from human-in-the-loop workflow.

        Args:
            webhook: The approval webhook payload.

        Returns:
            Response confirming approval handling.
        """
        response = {
            "success": True,
            "task_id": webhook.task_id,
            "approved": webhook.approved,
            "feedback": webhook.feedback,
            "timestamp": datetime.now().isoformat(),
        }

        # Execute callback if registered
        if "approval_received" in self._callbacks:
            await self._callbacks["approval_received"](response)

        return response

    async def send_callback(self, url: str, data: dict[str, Any]) -> bool:
        """Send a callback to the specified URL.

        Args:
            url: Callback URL.
            data: Data to send in the callback.

        Returns:
            True if callback was successful, False otherwise.
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0,
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False
