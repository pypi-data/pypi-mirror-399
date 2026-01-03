"""
X-Pay SDK Configuration and Types
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class XPayConfig(BaseModel):
    """Configuration for X-Pay SDK client."""
    
    api_key: str = Field(..., description="X-Pay API key")
    merchant_id: Optional[str] = Field(None, description="Merchant ID")
    environment: Optional[Literal["sandbox", "live"]] = Field(
        None, description="Environment (auto-detected from API key if not provided)"
    )
    base_url: Optional[str] = Field(None, description="Base API URL")
    timeout: Optional[int] = Field(30, description="Request timeout in seconds")
    
    model_config = ConfigDict(extra="forbid")


# Environment detection patterns
API_KEY_PATTERNS = {
    "sandbox": ["pk_sandbox_", "sk_sandbox_", "xpay_sandbox_"],
    "live": ["pk_live_", "sk_live_", "xpay_live_"],
}

# Default URLs
DEFAULT_URLS = {
    "sandbox": "https://server.xpay-bits.com",  # Use hosted X-Pay API for examples/dev
    "live": "https://api.xpay-bits.com",  # For production (when available)
}

# Supported currencies with metadata
SUPPORTED_CURRENCIES = {
    "USD": {
        "name": "US Dollar",
        "symbol": "$", 
        "decimal_places": 2,
        "smallest_unit_name": "cents",
    },
    "GHS": {
        "name": "Ghanaian Cedi",
        "symbol": "₵",
        "decimal_places": 2, 
        "smallest_unit_name": "pesewas",
    },
    "EUR": {
        "name": "Euro",
        "symbol": "€",
        "decimal_places": 2,
        "smallest_unit_name": "cents", 
    },
    "GBP": {
        "name": "British Pound",
        "symbol": "£",
        "decimal_places": 2,
        "smallest_unit_name": "pence",
    },
    "NGN": {
        "name": "Nigerian Naira", 
        "symbol": "₦",
        "decimal_places": 2,
        "smallest_unit_name": "kobo",
    },
    "LRD": {
        "name": "Liberian Dollar",
        "symbol": "L$",
        "decimal_places": 2,
        "smallest_unit_name": "cents",
    },
}

# Payment method to currency mapping
PAYMENT_METHOD_CURRENCIES = {
    "stripe": {
        "supported_currencies": ["USD", "EUR", "GBP", "GHS"],
        "default_currency": "USD",
        "regions": ["US", "EU", "GB", "GH"],
    },
    "momo": {
        "supported_currencies": ["GHS"],
        "default_currency": "GHS", 
        "regions": ["GH"],
    },
    "momo_liberia": {
        "supported_currencies": ["USD", "LRD"],
        "default_currency": "USD",
        "regions": ["LR"], 
    },
    "momo_nigeria": {
        "supported_currencies": ["NGN"],
        "default_currency": "NGN",
        "regions": ["NG"],
    },
    "xpay_wallet": {
        "supported_currencies": ["USD", "GHS", "EUR", "NGN"],
        "default_currency": "USD", 
        "regions": ["US", "GH", "EU", "NG"],
    },
}
