"""
Unit tests for X-Pay Python SDK
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from xpay import XPayClient, XPayError, AuthenticationError, ValidationError
from xpay.models import PaymentRequest, Payment
from xpay.utils import CurrencyUtils


class TestXPayClient:
    """Test XPayClient initialization and basic functionality."""

    def test_client_initialization(self):
        """Test client can be initialized with required parameters."""
        client = XPayClient(
            api_key="sk_sandbox_test123",
            merchant_id="merchant123",
            environment="sandbox"
        )
        
        assert client.config.api_key == "sk_sandbox_test123"
        assert client.merchant_id == "merchant123"
        assert client.client.detect_environment() == "sandbox"

    def test_client_requires_api_key(self):
        """Test client raises error when API key is missing."""
        with pytest.raises(ValidationError, match="API key is required"):
            XPayClient(api_key="")

    def test_environment_detection_from_api_key(self):
        """Test environment is detected from API key prefix."""
        # Sandbox keys
        sandbox_client = XPayClient(api_key="sk_sandbox_test123", merchant_id="test_merchant")
        assert sandbox_client.client.detect_environment() == "sandbox"
        
        # Live keys
        live_client = XPayClient(api_key="sk_live_test123", merchant_id="test_merchant")
        assert live_client.client.detect_environment() == "live"
        
        # Default to sandbox
        default_client = XPayClient(api_key="unknown_key_format", merchant_id="test_merchant")
        assert default_client.client.detect_environment() == "sandbox"

    @patch('xpay.http_client.HTTPClient.get')
    def test_ping_success(self, mock_get):
        """Test ping method with successful response."""
        mock_get.return_value = {
            "success": True,
            "data": {"timestamp": "2024-01-01T00:00:00Z"}
        }
        
        client = XPayClient(api_key="sk_sandbox_test123", merchant_id="test_merchant")
        result = client.ping()
        
        assert result["success"] is True
        assert "timestamp" in result
        mock_get.assert_called_once_with("/v1/healthz")


class TestPaymentsResource:
    """Test PaymentsResource functionality."""

    def setup_method(self):
        """Set up test client."""
        self.client = XPayClient(
            api_key="sk_sandbox_test123",
            merchant_id="merchant123"
        )

    @patch('xpay.http_client.HTTPClient.post')
    def test_create_payment_success(self, mock_post):
        """Test successful payment creation."""
        mock_payment_data = {
            "id": "pay_123",
            "status": "pending",
            "amount": "10.00",
            "currency": "USD",
            "payment_method": "stripe",
            "description": "Test payment",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_post.return_value = {"success": True, "data": mock_payment_data}

        payment_request = PaymentRequest(
            amount="10.00",
            currency="USD",
            payment_method="stripe",
            description="Test payment",
            customer_id=None,
            payment_method_data=None,
            metadata=None,
            success_url=None,
            cancel_url=None,
            webhook_url=None
        )

        payment = self.client.payments.create(payment_request)
        
        assert isinstance(payment, Payment)
        assert payment.id == "pay_123"
        assert payment.amount == "10.00"
        assert payment.currency == "USD"

    def test_create_payment_auto_currency(self):
        """Test payment creation with auto-assigned currency."""
        payment_request = PaymentRequest(
            amount="10.00",
            payment_method="stripe",  # Default currency should be USD
            description="Test payment",
            currency=None,
            customer_id=None,
            payment_method_data=None,
            metadata=None,
            success_url=None,
            cancel_url=None,
            webhook_url=None
        )
        
        # This should not raise an error and should auto-assign USD
        assert payment_request.payment_method == "stripe"

    def test_invalid_payment_method(self):
        """Test validation of invalid payment method."""
        with pytest.raises(ValueError, match="Invalid payment method"):
            PaymentRequest(
                amount="10.00",
                payment_method="invalid_method",
                description="Test payment",
                currency=None,
                customer_id=None,
                payment_method_data=None,
                metadata=None,
                success_url=None,
                cancel_url=None,
                webhook_url=None
            )

    @patch('xpay.http_client.HTTPClient.get')
    def test_retrieve_payment(self, mock_get):
        """Test payment retrieval."""
        mock_payment_data = {
            "id": "pay_123",
            "status": "completed",
            "amount": "10.00",
            "currency": "USD",
            "payment_method": "stripe",
            "description": "Test payment",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_get.return_value = {"success": True, "data": mock_payment_data}

        payment = self.client.payments.retrieve("pay_123")
        
        assert payment.id == "pay_123"
        assert payment.status == "completed"
        mock_get.assert_called_once_with("/v1/api/merchants/merchant123/payments/pay_123")


class TestCurrencyUtils:
    """Test currency utility functions."""

    def test_to_smallest_unit(self):
        """Test conversion to smallest currency unit."""
        # USD: 2 decimal places
        assert CurrencyUtils.to_smallest_unit(Decimal("10.50"), "USD") == 1050
        assert CurrencyUtils.to_smallest_unit(Decimal("0.01"), "USD") == 1
        
        # GHS: 2 decimal places  
        assert CurrencyUtils.to_smallest_unit(Decimal("25.75"), "GHS") == 2575

    def test_from_smallest_unit(self):
        """Test conversion from smallest currency unit."""
        # USD
        assert CurrencyUtils.from_smallest_unit(1050, "USD") == Decimal("10.50")
        assert CurrencyUtils.from_smallest_unit(1, "USD") == Decimal("0.01")
        
        # GHS
        assert CurrencyUtils.from_smallest_unit(2575, "GHS") == Decimal("25.75")

    def test_format_amount(self):
        """Test amount formatting with currency symbols."""
        # USD
        assert CurrencyUtils.format_amount(1050, "USD", from_smallest_unit=True) == "$10.50"
        assert CurrencyUtils.format_amount(Decimal("10.50"), "USD", from_smallest_unit=False) == "$10.50"
        
        # GHS
        assert CurrencyUtils.format_amount(2575, "GHS", from_smallest_unit=True) == "₵25.75"
        
        # EUR
        assert CurrencyUtils.format_amount(1000, "EUR", from_smallest_unit=True) == "€10.00"

    def test_invalid_currency(self):
        """Test handling of invalid currency codes."""
        with pytest.raises(Exception):  # Should raise InvalidCurrencyError
            CurrencyUtils.to_smallest_unit(Decimal("10.00"), "INVALID")

    def test_validate_currency(self):
        """Test currency validation."""
        assert CurrencyUtils.validate_currency("USD") is True
        assert CurrencyUtils.validate_currency("GHS") is True
        assert CurrencyUtils.validate_currency("INVALID") is False

    def test_get_supported_currencies(self):
        """Test getting list of supported currencies."""
        currencies = CurrencyUtils.get_supported_currencies()
        assert "USD" in currencies
        assert "GHS" in currencies
        assert "EUR" in currencies
        assert isinstance(currencies, list)


class TestErrorHandling:
    """Test error handling and exceptions."""

    def test_xpay_error_creation(self):
        """Test XPayError creation and attributes."""
        error = XPayError(
            message="Test error",
            code="TEST_ERROR",
            status=400,
            details={"field": "invalid"}
        )
        
        assert str(error) == "XPayError(TEST_ERROR): Test error"
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status == 400
        assert error.details == {"field": "invalid"}

    def test_authentication_error(self):
        """Test AuthenticationError specifics."""
        error = AuthenticationError("Invalid API key")
        
        assert error.code == "AUTHENTICATION_ERROR"
        assert error.message == "Invalid API key"

    def test_validation_error(self):
        """Test ValidationError specifics."""
        error = ValidationError("Missing required field", details={"field": "amount"})
        
        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Missing required field"
        assert error.details == {"field": "amount"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])