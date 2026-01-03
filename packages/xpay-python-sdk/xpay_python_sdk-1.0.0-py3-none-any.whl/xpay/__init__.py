"""
X-Pay Python SDK

The official Python SDK for X-Pay payment processing platform.
Accept payments from multiple providers including Stripe, Mobile Money, 
and X-Pay Wallets with a unified API.
"""

__version__ = "1.0.0"

from .client import XPayClient
from .exceptions import (
    XPayError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    APIError,
)
from .models import (
    PaymentRequest,
    Payment,
    PaymentMethods,
    Customer,
    CreateCustomerRequest,
    WebhookEndpoint,
    CreateWebhookRequest,
)

# Main client alias for convenience
XPay = XPayClient

__all__ = [
    "XPayClient",
    "XPay",
    "XPayError",
    "AuthenticationError", 
    "ValidationError",
    "NetworkError",
    "APIError",
    "PaymentRequest",
    "Payment",
    "PaymentMethods",
    "Customer",
    "CreateCustomerRequest", 
    "WebhookEndpoint",
    "CreateWebhookRequest",
]