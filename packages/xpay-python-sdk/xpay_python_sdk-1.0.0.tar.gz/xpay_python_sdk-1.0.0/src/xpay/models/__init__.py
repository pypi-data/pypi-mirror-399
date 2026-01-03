"""
Pydantic models for X-Pay SDK requests and responses
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class PaymentMethodData(BaseModel):
    """Payment method specific data."""
    
    # Stripe specific
    payment_method_types: Optional[List[str]] = None
    
    # Mobile Money specific  
    phone_number: Optional[str] = None
    
    # X-Pay Wallet specific
    wallet_id: Optional[str] = None
    pin: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class PaymentRequest(BaseModel):
    """Request model for creating a payment."""
    
    amount: str = Field(..., description="Payment amount as string")
    currency: Optional[str] = Field(None, description="Currency code (auto-assigned if not provided)")
    payment_method: str = Field(..., description="Payment method type")
    description: Optional[str] = Field(None, description="Payment description")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    payment_method_data: Optional[PaymentMethodData] = Field(None, description="Payment method specific data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    success_url: Optional[str] = Field(None, description="Success redirect URL")
    cancel_url: Optional[str] = Field(None, description="Cancel redirect URL")
    webhook_url: Optional[str] = Field(None, description="Webhook notification URL")
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        allowed = [
            'stripe', 'momo', 'momo_liberia', 'momo_nigeria', 
            'momo_uganda', 'momo_rwanda', 'wallet', 'xpay_wallet'
        ]
        if v not in allowed:
            raise ValueError(f"Invalid payment method. Allowed: {', '.join(allowed)}")
        return v


class Payment(BaseModel):
    """Payment response model."""
    
    id: str
    status: str
    amount: str
    currency: str
    description: Optional[str] = None
    payment_method: str
    customer_id: Optional[str] = None
    client_secret: Optional[str] = None  # Stripe
    reference_id: Optional[str] = None   # Mobile Money
    transaction_url: Optional[str] = None
    instructions: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class PaymentMethodInfo(BaseModel):
    """Payment method information."""
    
    type: str
    name: str  
    description: str
    enabled: bool
    currencies: List[str]
    fees: Dict[str, str]


class PaymentMethods(BaseModel):
    """Available payment methods response."""
    
    payment_methods: List[PaymentMethodInfo]
    environment: str
    merchant_id: str


class CreateCustomerRequest(BaseModel):
    """Request model for creating a customer."""
    
    email: str = Field(..., description="Customer email address")
    name: str = Field(..., description="Customer full name")
    phone: Optional[str] = Field(None, description="Customer phone number")
    description: Optional[str] = Field(None, description="Customer description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")


class Customer(BaseModel):
    """Customer response model."""
    
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class CreateWebhookRequest(BaseModel):
    """Request model for creating a webhook endpoint."""
    
    url: str = Field(..., description="Webhook endpoint URL")
    events: List[str] = Field(..., description="List of events to subscribe to")
    description: Optional[str] = Field(None, description="Webhook description")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v
    
    @field_validator('events')
    @classmethod
    def validate_events(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one event must be specified")
        
        allowed_events = [
            'payment.created', 'payment.succeeded', 'payment.failed',
            'payment.cancelled', 'payment.refunded', 'refund.created',
            'refund.succeeded', 'refund.failed', 'customer.created',
            'customer.updated'
        ]
        
        for event in v:
            if event not in allowed_events:
                raise ValueError(f"Invalid event: {event}. Allowed: {', '.join(allowed_events)}")
        
        return v


class WebhookEndpoint(BaseModel):
    """Webhook endpoint response model."""
    
    id: str
    url: str
    events: List[str]
    environment: str
    is_active: bool
    secret: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None


# Payment list responses
class PaymentListResponse(BaseModel):
    """Response model for listing payments."""
    
    payments: List[Payment]
    total: int
    has_more: Optional[bool] = None


class CustomerListResponse(BaseModel):
    """Response model for listing customers."""
    
    customers: List[Customer]
    total: int  
    has_more: Optional[bool] = None


class WebhookListResponse(BaseModel):
    """Response model for listing webhooks."""
    
    webhooks: List[WebhookEndpoint]