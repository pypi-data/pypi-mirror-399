"""
Webhooks resource for X-Pay SDK
"""

from typing import Optional, Dict, Any

from ..http_client import HTTPClient
from ..models import (
    WebhookEndpoint,
    CreateWebhookRequest,
    WebhookListResponse,
)
from ..utils.webhook import WebhookUtils


class WebhooksResource:
    """Resource for managing webhook endpoints."""
    
    def __init__(self, client: HTTPClient, merchant_id: str) -> None:
        self.client = client
        self.merchant_id = merchant_id
    
    def create(self, webhook_data: CreateWebhookRequest) -> WebhookEndpoint:
        """Create a new webhook endpoint."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/webhooks"
        response = self.client.post(endpoint, webhook_data.model_dump())
        
        return WebhookEndpoint(**response["data"])
    
    def list(self) -> WebhookListResponse:
        """List all webhook endpoints."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/webhooks"
        response = self.client.get(endpoint)
        
        # Handle both direct list and wrapped response
        if isinstance(response["data"], list):
            return WebhookListResponse(webhooks=response["data"])
        return WebhookListResponse(**response["data"])
    
    def retrieve(self, webhook_id: str) -> WebhookEndpoint:
        """Retrieve a webhook endpoint by ID."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}"
        response = self.client.get(endpoint)
        
        return WebhookEndpoint(**response["data"])
    
    def update(
        self,
        webhook_id: str,
        update_data: Dict[str, Any],
    ) -> WebhookEndpoint:
        """Update a webhook endpoint."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}"
        response = self.client.put(endpoint, update_data)
        
        return WebhookEndpoint(**response["data"])
    
    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook endpoint."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}"
        response = self.client.delete(endpoint)
        
        return response.get("data", {})
    
    def test(self, webhook_id: str) -> Dict[str, Any]:
        """Test a webhook endpoint.""" 
        endpoint = f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}/test"
        response = self.client.post(endpoint)
        
        return response.get("data", {})
    
    # Static webhook utility methods
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        return WebhookUtils.verify_signature(payload, signature, secret)
    
    @staticmethod
    def construct_event(
        payload: str, 
        signature: str, 
        secret: str
    ) -> Dict[str, Any]:
        """Construct and verify webhook event."""
        return WebhookUtils.construct_event(payload, signature, secret)