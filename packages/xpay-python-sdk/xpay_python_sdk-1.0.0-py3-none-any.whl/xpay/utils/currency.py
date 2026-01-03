"""
Currency utilities for X-Pay SDK
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union

from ..exceptions import InvalidCurrencyError
from ..types.config import SUPPORTED_CURRENCIES


class CurrencyUtils:
    """Utility functions for currency operations."""
    
    @staticmethod
    def to_smallest_unit(amount: Union[Decimal, float, str, int], currency: str) -> int:
        """
        Convert amount to smallest currency unit (e.g., dollars to cents).
        
        Args:
            amount: Amount to convert
            currency: Currency code (e.g., 'USD', 'GHS')
            
        Returns:
            Amount in smallest unit as integer
            
        Raises:
            InvalidCurrencyError: If currency is not supported
        """
        if currency not in SUPPORTED_CURRENCIES:
            raise InvalidCurrencyError(currency)
        
        currency_info = SUPPORTED_CURRENCIES[currency]
        decimal_places = currency_info["decimal_places"]
        
        # Convert to Decimal for precision
        if isinstance(amount, str):
            decimal_amount = Decimal(amount)
        else:
            decimal_amount = Decimal(str(amount))
        
        # Multiply by 10^decimal_places and round
        multiplier = Decimal(10) ** Decimal(str(decimal_places))
        result = decimal_amount * multiplier
        
        # Round to nearest integer (banker's rounding)
        return int(result.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    
    @staticmethod
    def from_smallest_unit(amount: int, currency: str) -> Decimal:
        """
        Convert amount from smallest currency unit (e.g., cents to dollars).
        
        Args:
            amount: Amount in smallest unit
            currency: Currency code (e.g., 'USD', 'GHS')
            
        Returns:
            Amount as Decimal
            
        Raises:
            InvalidCurrencyError: If currency is not supported
        """
        if currency not in SUPPORTED_CURRENCIES:
            raise InvalidCurrencyError(currency)
        
        currency_info = SUPPORTED_CURRENCIES[currency]
        decimal_places = currency_info["decimal_places"]
        
        # Divide by 10^decimal_places
        divisor = Decimal(10) ** Decimal(str(decimal_places))
        return Decimal(amount) / divisor
    
    @staticmethod
    def format_amount(
        amount: Union[Decimal, int, float, str],
        currency: str,
        from_smallest_unit: bool = True,
    ) -> str:
        """
        Format amount for display with currency symbol.
        
        Args:
            amount: Amount to format
            currency: Currency code
            from_smallest_unit: Whether amount is in smallest unit
            
        Returns:
            Formatted amount string with currency symbol
            
        Raises:
            InvalidCurrencyError: If currency is not supported
        """
        if currency not in SUPPORTED_CURRENCIES:
            raise InvalidCurrencyError(currency)
        
        currency_info = SUPPORTED_CURRENCIES[currency]
        symbol = currency_info["symbol"]
        decimal_places = currency_info["decimal_places"]
        
        # Convert amount to Decimal
        if from_smallest_unit and isinstance(amount, int):
            display_amount = CurrencyUtils.from_smallest_unit(amount, currency)
        else:
            if isinstance(amount, str):
                display_amount = Decimal(amount)
            else:
                display_amount = Decimal(str(amount))
        
        # Format with appropriate decimal places
        format_str = f"{{:.{decimal_places}f}}"
        formatted_amount = format_str.format(display_amount)
        
        return f"{symbol}{formatted_amount}"
    
    @staticmethod
    def validate_currency(currency: str) -> bool:
        """
        Validate if currency is supported.
        
        Args:
            currency: Currency code to validate
            
        Returns:
            True if currency is supported
        """
        return currency in SUPPORTED_CURRENCIES
    
    @staticmethod
    def get_currency_info(currency: str) -> dict:
        """
        Get currency information.
        
        Args:
            currency: Currency code
            
        Returns:
            Dictionary with currency information
            
        Raises:
            InvalidCurrencyError: If currency is not supported
        """
        if currency not in SUPPORTED_CURRENCIES:
            raise InvalidCurrencyError(currency)
        
        return SUPPORTED_CURRENCIES[currency].copy()
    
    @staticmethod
    def get_supported_currencies() -> list[str]:
        """
        Get list of all supported currencies.
        
        Returns:
            List of supported currency codes
        """
        return list(SUPPORTED_CURRENCIES.keys())
