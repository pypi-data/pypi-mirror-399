"""
X-Pay SDK Custom Exceptions
"""

from typing import Optional, Any, Dict


class XPayError(Exception):
    """Base exception for X-Pay SDK errors."""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.status = status
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"XPayError({self.code}): {self.message}"
    
    def __repr__(self) -> str:
        return (
            f"XPayError(message={self.message!r}, code={self.code!r}, "
            f"status={self.status}, details={self.details!r})"
        )


class AuthenticationError(XPayError):
    """Raised when API authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, code="AUTHENTICATION_ERROR", **kwargs)


class ValidationError(XPayError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str = "Validation failed", **kwargs: Any) -> None:
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)


class NetworkError(XPayError):
    """Raised when network request fails."""
    
    def __init__(self, message: str = "Network error", **kwargs: Any) -> None:
        super().__init__(message, code="NETWORK_ERROR", **kwargs)


class APIError(XPayError):
    """Raised when API returns an error response."""
    
    def __init__(
        self, 
        message: str = "API error", 
        status: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(message, code="API_ERROR", status=status, **kwargs)


class TimeoutError(XPayError):
    """Raised when request times out."""
    
    def __init__(self, message: str = "Request timeout", **kwargs: Any) -> None:
        super().__init__(message, code="TIMEOUT_ERROR", **kwargs)


class InvalidCurrencyError(ValidationError):
    """Raised when an invalid currency is provided."""
    
    def __init__(self, currency: str, **kwargs: Any) -> None:
        message = f"Invalid currency: {currency}"
        super().__init__(message, code="INVALID_CURRENCY", **kwargs)


class InvalidPaymentMethodError(ValidationError):
    """Raised when an invalid payment method is provided."""
    
    def __init__(self, payment_method: str, **kwargs: Any) -> None:
        message = f"Invalid payment method: {payment_method}"  
        super().__init__(message, code="INVALID_PAYMENT_METHOD", **kwargs)


class WebhookVerificationError(XPayError):
    """Raised when webhook signature verification fails."""
    
    def __init__(self, message: str = "Webhook verification failed", **kwargs: Any) -> None:
        super().__init__(message, code="WEBHOOK_VERIFICATION_ERROR", **kwargs)