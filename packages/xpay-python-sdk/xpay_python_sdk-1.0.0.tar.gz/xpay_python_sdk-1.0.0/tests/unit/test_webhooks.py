"""
Unit tests for WebhooksResource
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import hmac
import hashlib

from xpay.resources.webhooks import WebhooksResource
from xpay.models import WebhookEndpoint, CreateWebhookRequest, WebhookListResponse
from xpay.utils.webhook import WebhookUtils
from xpay.exceptions import WebhookVerificationError


class TestWebhooksResource:
    """Test WebhooksResource functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.merchant_id = "test_merchant_123"
        self.webhooks = WebhooksResource(self.mock_client, self.merchant_id)

    def test_create_webhook(self):
        """Test creating a webhook endpoint."""
        webhook_data = CreateWebhookRequest(
            url="https://example.com/webhooks",
            events=["payment.succeeded", "payment.failed"],
            description="Test webhook"
        )
        
        mock_response = {
            "success": True,
            "data": {
                "id": "webhook_123",
                "url": "https://example.com/webhooks",
                "events": ["payment.succeeded", "payment.failed"],
                "description": "Test webhook",
                "environment": "sandbox",
                "is_active": True,
                "secret": "whsec_test123",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
        self.mock_client.post.return_value = mock_response
        
        result = self.webhooks.create(webhook_data)
        
        self.mock_client.post.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/webhooks",
            webhook_data.model_dump()
        )
        assert isinstance(result, WebhookEndpoint)
        assert result.id == "webhook_123"
        assert result.url == "https://example.com/webhooks"

    def test_list_webhooks(self):
        """Test listing all webhook endpoints."""
        mock_response = {
            "success": True,
            "data": {
                "webhooks": [
                    {
                        "id": "webhook_123",
                        "url": "https://example.com/webhooks",
                        "events": ["payment.succeeded"],
                        "environment": "sandbox",
                        "is_active": True,
                        "secret": "whsec_test123",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.webhooks.list()
        
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/webhooks"
        )
        assert isinstance(result, WebhookListResponse)
        assert len(result.webhooks) == 1

    def test_list_webhooks_with_direct_list_response(self):
        """Test listing webhooks when API returns direct list."""
        mock_response = {
            "success": True,
            "data": [
                {
                    "id": "webhook_123",
                    "url": "https://example.com/webhooks",
                    "events": ["payment.succeeded"],
                    "environment": "sandbox",
                    "is_active": True,
                    "secret": "whsec_test123",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.webhooks.list()
        
        assert isinstance(result, WebhookListResponse)

    def test_retrieve_webhook(self):
        """Test retrieving a webhook by ID."""
        webhook_id = "webhook_123"
        mock_response = {
            "success": True,
            "data": {
                "id": webhook_id,
                "url": "https://example.com/webhooks",
                "events": ["payment.succeeded"],
                "environment": "sandbox",
                "is_active": True,
                "secret": "whsec_test123",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.webhooks.retrieve(webhook_id)
        
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}"
        )
        assert result.id == webhook_id

    def test_update_webhook(self):
        """Test updating a webhook endpoint."""
        webhook_id = "webhook_123"
        update_data = {"events": ["payment.succeeded", "payment.failed", "refund.created"]}
        
        mock_response = {
            "success": True,
            "data": {
                "id": webhook_id,
                "url": "https://example.com/webhooks",
                "events": ["payment.succeeded", "payment.failed", "refund.created"],
                "environment": "sandbox",
                "is_active": True,
                "secret": "whsec_test123",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:01Z"
            }
        }
        self.mock_client.put.return_value = mock_response
        
        result = self.webhooks.update(webhook_id, update_data)
        
        self.mock_client.put.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}",
            update_data
        )
        assert len(result.events) == 3

    def test_delete_webhook(self):
        """Test deleting a webhook endpoint."""
        webhook_id = "webhook_123"
        mock_response = {
            "success": True,
            "data": {"deleted": True}
        }
        self.mock_client.delete.return_value = mock_response
        
        result = self.webhooks.delete(webhook_id)
        
        self.mock_client.delete.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}"
        )
        assert result["deleted"] is True

    def test_test_webhook(self):
        """Test testing a webhook endpoint."""
        webhook_id = "webhook_123"
        mock_response = {
            "success": True,
            "data": {"success": True, "response_code": 200}
        }
        self.mock_client.post.return_value = mock_response
        
        result = self.webhooks.test(webhook_id)
        
        self.mock_client.post.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/webhooks/{webhook_id}/test"
        )
        assert result["success"] is True


class TestWebhookSignatureVerification:
    """Test webhook signature verification."""

    def test_verify_signature_valid(self):
        """Test valid signature verification."""
        payload = '{"event": "payment.succeeded", "data": {"id": "pay_123"}}'
        secret = "whsec_test_secret_key"
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        result = WebhooksResource.verify_signature(payload, signature, secret)
        
        assert result is True

    def test_verify_signature_with_prefix(self):
        """Test signature verification with sha256= prefix."""
        payload = '{"event": "payment.succeeded"}'
        secret = "whsec_test_secret_key"
        
        # Generate valid signature with prefix
        signature_hash = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        signature = f"sha256={signature_hash}"
        
        result = WebhooksResource.verify_signature(payload, signature, secret)
        
        assert result is True

    def test_verify_signature_invalid(self):
        """Test invalid signature verification."""
        payload = '{"event": "payment.succeeded"}'
        invalid_signature = "invalid_signature_here"
        secret = "whsec_test_secret_key"
        
        result = WebhooksResource.verify_signature(payload, invalid_signature, secret)
        
        assert result is False

    def test_verify_signature_tampered_payload(self):
        """Test signature fails with tampered payload."""
        original_payload = '{"event": "payment.succeeded"}'
        tampered_payload = '{"event": "payment.failed"}'
        secret = "whsec_test_secret_key"
        
        # Generate signature for original payload
        signature = hmac.new(
            secret.encode('utf-8'),
            original_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Verify with tampered payload should fail
        result = WebhooksResource.verify_signature(tampered_payload, signature, secret)
        
        assert result is False

    def test_construct_event_valid(self):
        """Test constructing event with valid signature."""
        payload = '{"event": "payment.succeeded", "data": {"id": "pay_123"}}'
        secret = "whsec_test_secret_key"
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        result = WebhooksResource.construct_event(payload, signature, secret)
        
        assert result["event"] == "payment.succeeded"
        assert result["data"]["id"] == "pay_123"

    def test_construct_event_invalid_signature(self):
        """Test construct_event raises error with invalid signature."""
        payload = '{"event": "payment.succeeded"}'
        invalid_signature = "invalid_signature"
        secret = "whsec_test_secret_key"
        
        with pytest.raises(WebhookVerificationError, match="Invalid webhook signature"):
            WebhooksResource.construct_event(payload, invalid_signature, secret)

    def test_construct_event_invalid_json(self):
        """Test construct_event raises error with invalid JSON."""
        payload = "not valid json {"
        secret = "whsec_test_secret_key"
        
        # Generate signature for the invalid JSON string
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        with pytest.raises(WebhookVerificationError, match="Invalid JSON payload"):
            WebhooksResource.construct_event(payload, signature, secret)


class TestWebhookUtils:
    """Test WebhookUtils helper functions."""

    def test_generate_signature(self):
        """Test signature generation."""
        payload = '{"event": "test"}'
        secret = "test_secret"
        
        signature = WebhookUtils.generate_signature(payload, secret)
        
        assert signature.startswith("sha256=")
        # Verify the generated signature is valid
        assert WebhookUtils.verify_signature(payload, signature, secret) is True
