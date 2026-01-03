"""
Payments resource for X-Pay SDK
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal

from ..http_client import HTTPClient
from ..models import (
    PaymentRequest, 
    Payment, 
    PaymentMethods,
    PaymentListResponse,
)
from ..exceptions import ValidationError, InvalidCurrencyError, InvalidPaymentMethodError
from ..types.config import PAYMENT_METHOD_CURRENCIES, SUPPORTED_CURRENCIES
from ..utils.currency import CurrencyUtils


class PaymentsResource:
    """Resource for managing payments."""
    
    def __init__(self, client: HTTPClient, merchant_id: str) -> None:
        self.client = client
        self.merchant_id = merchant_id
    
    def get_default_currency(self, payment_method: str) -> str:
        """Get default currency for a payment method."""
        method_config = PAYMENT_METHOD_CURRENCIES.get(payment_method)
        if not method_config:
            raise InvalidPaymentMethodError(payment_method)
        return str(method_config["default_currency"])
    
    def validate_currency(self, payment_method: str, currency: str) -> None:
        """Validate currency for payment method."""
        method_config = PAYMENT_METHOD_CURRENCIES.get(payment_method)
        if not method_config:
            raise InvalidPaymentMethodError(payment_method)
        
        if currency not in method_config["supported_currencies"]:
            supported = ", ".join(method_config["supported_currencies"])
            raise InvalidCurrencyError(
                f"Currency {currency} not supported for {payment_method}. "
                f"Supported: {supported}"
            )
    
    def create(self, payment_data: PaymentRequest) -> Payment:
        """Create a new payment."""
        # Convert to dict for processing
        data = payment_data.model_dump(exclude_unset=True)
        
        # Auto-assign currency if not provided
        if not data.get("currency"):
            data["currency"] = self.get_default_currency(data["payment_method"])
        
        # Validate currency for payment method
        self.validate_currency(data["payment_method"], data["currency"])
        
        # Make API request
        endpoint = f"/v1/api/merchants/{self.merchant_id}/payments"
        response = self.client.post(endpoint, data)
        
        return Payment(**response["data"])
    
    def retrieve(self, payment_id: str) -> Payment:
        """Retrieve a payment by ID."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/payments/{payment_id}"
        response = self.client.get(endpoint)
        
        return Payment(**response["data"])
    
    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
    ) -> PaymentListResponse:
        """List payments with optional filters."""
        params: Dict[str, str] = {}
        
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)
        if status:
            params["status"] = status
        if customer_id:
            params["customer_id"] = customer_id
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        
        endpoint = f"/v1/api/merchants/{self.merchant_id}/payments"
        response = self.client.get(endpoint, params)
        
        return PaymentListResponse(**response["data"])
    
    def cancel(self, payment_id: str) -> Payment:
        """Cancel a payment (if supported by payment method)."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/payments/{payment_id}/cancel"
        response = self.client.post(endpoint)
        
        return Payment(**response["data"])
    
    def get_payment_methods(self, country: Optional[str] = None) -> PaymentMethods:
        """Get available payment methods for this merchant."""
        params = {}
        if country:
            params["country"] = country
        
        endpoint = f"/v1/api/merchants/{self.merchant_id}/payment-methods"
        response = self.client.get(endpoint, params)
        
        return PaymentMethods(**response["data"])
    
    def get_supported_currencies(self, payment_method: str) -> List[str]:
        """Get supported currencies for a payment method."""
        method_config = PAYMENT_METHOD_CURRENCIES.get(payment_method)
        if not method_config:
            raise InvalidPaymentMethodError(payment_method)
        return list(method_config["supported_currencies"])
    
    def confirm(
        self,
        payment_id: str,
        confirmation_data: Optional[Dict[str, Any]] = None,
    ) -> Payment:
        """Confirm a payment (for payment methods that require confirmation)."""
        endpoint = f"/v1/payments/{payment_id}/confirm"
        response = self.client.post(endpoint, confirmation_data)
        
        return Payment(**response["data"])
    
    # Currency utility methods
    @staticmethod
    def to_smallest_unit(amount: Decimal, currency: str) -> int:
        """Convert amount to smallest currency unit (e.g., dollars to cents)."""
        return CurrencyUtils.to_smallest_unit(amount, currency)
    
    @staticmethod
    def from_smallest_unit(amount: int, currency: str) -> Decimal:
        """Convert amount from smallest currency unit (e.g., cents to dollars)."""
        return CurrencyUtils.from_smallest_unit(amount, currency)
    
    @staticmethod
    def format_amount(
        amount: Decimal, 
        currency: str, 
        from_smallest_unit: bool = True
    ) -> str:
        """Format amount for display with currency symbol."""
        return CurrencyUtils.format_amount(amount, currency, from_smallest_unit)