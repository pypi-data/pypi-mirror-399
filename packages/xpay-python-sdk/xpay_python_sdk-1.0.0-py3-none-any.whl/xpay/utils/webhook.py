"""
Webhook utilities for X-Pay SDK
"""

import hmac
import hashlib
import json
from typing import Union, Dict, Any

from ..exceptions import WebhookVerificationError


class WebhookUtils:
    """Utility functions for webhook operations."""
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """
        Verify webhook signature using HMAC-SHA256.
        
        Args:
            payload: Raw webhook payload as string
            signature: Signature from X-Webhook-Signature header
            secret: Webhook secret from dashboard
            
        Returns:
            True if signature is valid
        """
        try:
            # Remove 'sha256=' prefix if present
            expected_signature = signature
            if signature.startswith('sha256='):
                expected_signature = signature[7:]
            
            # Create HMAC with SHA256
            computed_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures in constant time
            return hmac.compare_digest(computed_signature, expected_signature)
            
        except Exception:
            return False
    
    @staticmethod
    def construct_event(
        payload: str, 
        signature: str, 
        secret: str
    ) -> Dict[str, Any]:
        """
        Construct and verify webhook event.
        
        Args:
            payload: Raw webhook payload as string
            signature: Signature from X-Webhook-Signature header  
            secret: Webhook secret from dashboard
            
        Returns:
            Parsed webhook event data
            
        Raises:
            WebhookVerificationError: If signature verification fails
        """
        # Verify signature first
        if not WebhookUtils.verify_signature(payload, signature, secret):
            raise WebhookVerificationError("Invalid webhook signature")
        
        try:
            # Parse JSON payload
            event: Dict[str, Any] = json.loads(payload)
            return event
        except json.JSONDecodeError as e:
            raise WebhookVerificationError(f"Invalid JSON payload: {str(e)}")
    
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """
        Generate webhook signature for testing purposes.
        
        Args:
            payload: Webhook payload as string
            secret: Webhook secret
            
        Returns:
            HMAC-SHA256 signature with sha256= prefix
        """
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"