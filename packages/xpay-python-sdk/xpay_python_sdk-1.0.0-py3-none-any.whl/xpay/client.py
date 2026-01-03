"""
Main X-Pay SDK client
"""

from typing import Optional, Dict, Any, Literal

from .http_client import HTTPClient
from .resources import PaymentsResource, WebhooksResource, CustomersResource
from .types.config import XPayConfig
from .models import PaymentMethods
from .exceptions import ValidationError


class XPayClient:
    """Main X-Pay SDK client."""
    
    def __init__(
        self,
        api_key: str,
        merchant_id: Optional[str] = None,
        environment: Optional[Literal["sandbox", "live"]] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize X-Pay client.
        
        Args:
            api_key: X-Pay API key
            merchant_id: Merchant ID (optional, can be extracted from API key)
            environment: Environment ('sandbox' or 'live', auto-detected if not provided)
            base_url: Custom base URL for API requests
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        # Create configuration
        self.config = XPayConfig(
            api_key=api_key,
            merchant_id=merchant_id,
            environment=environment,
            base_url=base_url,
            timeout=timeout or 30,
        )
        
        # Extract or use provided merchant ID
        self.merchant_id = merchant_id or self._extract_merchant_id_from_api_key(api_key)
        
        # Initialize HTTP client
        self.client = HTTPClient(self.config)
        
        # Initialize resource clients
        self.payments = PaymentsResource(self.client, self.merchant_id)
        self.webhooks = WebhooksResource(self.client, self.merchant_id)
        self.customers = CustomersResource(self.client, self.merchant_id)
    
    def _extract_merchant_id_from_api_key(self, api_key: str) -> str:
        """
        Extract merchant ID from API key.
        
        Raises:
            ValidationError: If merchant_id is not provided
        """
        if self.config.merchant_id:
            return self.config.merchant_id
        raise ValidationError(
            "Merchant ID is required. Get your merchant ID from the X-Pay dashboard."
        )
    
    def ping(self) -> Dict[str, Any]:
        """
        Test API connectivity and authentication.
        
        Returns:
            Dictionary with success status and timestamp
        """
        response = self.client.get("/v1/healthz")
        return {
            "success": response["success"],
            "timestamp": response.get("data", {}).get("timestamp") or "unknown"
        }
    
    def get_payment_methods(self, country: Optional[str] = None) -> PaymentMethods:
        """
        Get payment methods available for this merchant.
        
        Args:
            country: Optional country code to filter methods
            
        Returns:
            PaymentMethods object with available methods
        """
        return self.payments.get_payment_methods(country)
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        self.client.close()
    
    def __enter__(self) -> "XPayClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# Alias for convenience
XPay = XPayClient
