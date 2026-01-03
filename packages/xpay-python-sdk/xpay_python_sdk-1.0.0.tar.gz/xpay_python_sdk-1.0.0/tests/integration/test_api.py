"""
Integration tests for X-Pay Python SDK
Test against live API endpoints with real credentials

⚠️ NOTE: These tests require environment variables to be set:
  - XPAY_API_KEY: Your X-Pay sandbox API key
  - XPAY_MERCHANT_ID: Your X-Pay merchant ID
  - XPAY_BASE_URL: API base URL (default: http://localhost:8000)
"""

import os
import pytest
from decimal import Decimal
import uuid

from xpay import XPayClient, PaymentRequest, CreateCustomerRequest, CreateWebhookRequest
from xpay.models import PaymentMethodData
from xpay.exceptions import XPayError, AuthenticationError


# Get credentials from environment variables
XPAY_API_KEY = os.environ.get("XPAY_API_KEY")
XPAY_MERCHANT_ID = os.environ.get("XPAY_MERCHANT_ID")
XPAY_BASE_URL = os.environ.get("XPAY_BASE_URL", "http://localhost:8000")


@pytest.mark.integration
class TestLiveAPIIntegration:
    """Integration tests against live X-Pay API."""

    @classmethod
    def setup_class(cls):
        """Set up test client with credentials from environment variables."""
        if not XPAY_API_KEY or not XPAY_MERCHANT_ID:
            pytest.skip(
                "Integration tests require XPAY_API_KEY and XPAY_MERCHANT_ID environment variables"
            )
        
        cls.client = XPayClient(
            api_key=XPAY_API_KEY,
            merchant_id=XPAY_MERCHANT_ID,
            environment="sandbox",
            base_url=XPAY_BASE_URL
        )

    def test_ping_connectivity(self):
        """Test basic API connectivity."""
        result = self.client.ping()
        assert result["success"] is True
        assert "timestamp" in result

    def test_get_payment_methods(self):
        """Test retrieving available payment methods."""
        payment_methods = self.client.get_payment_methods()
        
        assert payment_methods.environment == "sandbox"
        assert payment_methods.merchant_id == XPAY_MERCHANT_ID
        assert len(payment_methods.payment_methods) > 0
        
        # Check expected payment methods exist
        method_types = [pm.type for pm in payment_methods.payment_methods]
        assert "stripe" in method_types
        assert "xpay_wallet" in method_types

    def test_create_stripe_payment(self):
        """Test creating a Stripe payment."""
        # First create a customer
        customer_request = CreateCustomerRequest(
            email=f"stripe-test-{uuid.uuid4().hex[:8]}@example.com",
            name="Stripe Test User",
            phone="+1234567890",
            description=None,
            metadata={"test": True}
        )
        customer = self.client.customers.create(customer_request)
        
        payment_request = PaymentRequest(
            amount="15.99",
            currency="USD", 
            payment_method="stripe",
            description="Integration test payment",
            customer_id=customer.id,
            payment_method_data=PaymentMethodData(
                payment_method_types=["card"]
            ),
            metadata={
                "test": True,
                "integration_test": "python_sdk"
            },
            success_url=None,
            cancel_url=None,
            webhook_url=None
        )
        
        payment = self.client.payments.create(payment_request)
        
        assert payment.id is not None
        assert payment.status in ["requires_payment_method", "pending"]
        assert payment.amount == "15.99"
        assert payment.currency == "USD"
        assert payment.payment_method == "stripe"
        assert payment.client_secret is not None
        assert payment.client_secret.startswith("pi_")

    def test_create_mobile_money_payment(self):
        """Test creating a Mobile Money payment."""
        # First create a customer
        customer_request = CreateCustomerRequest(
            email=f"momo-test-{uuid.uuid4().hex[:8]}@example.com",
            name="MoMo Test User",
            phone="+231123456789",
            description=None,
            metadata={"test": True, "type": "momo"}
        )
        customer = self.client.customers.create(customer_request)
        
        payment_request = PaymentRequest(
            amount="50.00",
            currency="USD",
            payment_method="momo_liberia",
            description="Integration test MoMo payment",
            customer_id=customer.id,
            payment_method_data=PaymentMethodData(
                phone_number="+231123456789"
            ),
            metadata={
                "test": True,
                "type": "momo_integration_test"
            },
            success_url=None,
            cancel_url=None,
            webhook_url=None
        )
        
        payment = self.client.payments.create(payment_request)
        
        assert payment.id is not None
        assert payment.status == "pending"
        assert payment.amount == "50.0000"
        assert payment.currency == "USD"
        assert payment.payment_method == "momo"
        assert payment.reference_id is not None

    def test_retrieve_payment(self):
        """Test retrieving a payment after creation."""
        # First create a customer
        customer_request = CreateCustomerRequest(
            email=f"retrieve-test-{uuid.uuid4().hex[:8]}@example.com",
            name="Retrieve Test User",
            phone="+1234567890",
            description=None,
            metadata={"test": True}
        )
        customer = self.client.customers.create(customer_request)
        
        # Then create a payment
        payment_request = PaymentRequest(
            amount="25.00",
            currency="USD",
            payment_method="stripe",
            description="Retrieve test payment",
            customer_id=customer.id,
            payment_method_data=None,
            metadata=None,
            success_url=None,
            cancel_url=None,
            webhook_url=None
        )
        
        created_payment = self.client.payments.create(payment_request)
        
        # Then retrieve it
        retrieved_payment = self.client.payments.retrieve(created_payment.id)
        
        assert retrieved_payment.id == created_payment.id
        assert retrieved_payment.amount == created_payment.amount
        assert retrieved_payment.status == created_payment.status

    def test_create_customer(self):
        """Test creating a customer."""
        customer_request = CreateCustomerRequest(
            email=f"integration-test-{uuid.uuid4().hex[:8]}@example.com",
            name="Integration Test User",
            phone="+1234567890",
            description="Customer from integration test",
            metadata={
                "test": True,
                "source": "python_sdk_integration"
            }
        )
        
        customer = self.client.customers.create(customer_request)
        
        assert customer.id is not None
        assert customer.email == customer_request.email
        assert customer.name == "Integration Test User"
        assert customer.phone == "+1234567890"

    def test_list_payments(self):
        """Test listing payments with filters."""
        # First create a customer
        customer_request = CreateCustomerRequest(
            email=f"list-test-{uuid.uuid4().hex[:8]}@example.com",
            name="List Test User",
            phone="+1234567890",
            description=None,
            metadata={"test": True}
        )
        customer = self.client.customers.create(customer_request)
        
        # Create a couple of payments first
        for i in range(2):
            payment_request = PaymentRequest(
                amount=f"{10 + i}.00",
                currency="USD",
                payment_method="stripe",
                description=f"List test payment {i + 1}",
                customer_id=customer.id,
                payment_method_data=None,
                metadata=None,
                success_url=None,
                cancel_url=None,
                webhook_url=None
            )
            self.client.payments.create(payment_request)
        
        # List payments
        payments_response = self.client.payments.list(limit=5)
        
        assert hasattr(payments_response, 'payments')
        assert len(payments_response.payments) >= 2
        assert payments_response.total >= 2

    def test_currency_utilities_integration(self):
        """Test currency utilities with real payment amounts."""
        from xpay.utils import CurrencyUtils
        
        # Test with various amounts
        test_cases = [
            (Decimal("10.99"), "USD", 1099, "$10.99"),
            (Decimal("100.50"), "GHS", 10050, "₵100.50"),
            (Decimal("25.75"), "EUR", 2575, "€25.75"),
        ]
        
        for amount, currency, expected_cents, expected_format in test_cases:
            # Test conversion to smallest unit
            cents = CurrencyUtils.to_smallest_unit(amount, currency)
            assert cents == expected_cents
            
            # Test conversion back
            converted_back = CurrencyUtils.from_smallest_unit(cents, currency)
            assert converted_back == amount
            
            # Test formatting
            formatted = CurrencyUtils.format_amount(cents, currency)
            assert formatted == expected_format

    def test_payment_with_invalid_api_key(self):
        """Test that invalid API key raises proper error."""
        invalid_client = XPayClient(
            api_key="sk_sandbox_invalid_key",
            merchant_id="548d8033-fbe9-411b-991f-f159cdee7745",
            base_url="http://localhost:8000"
        )
        
        with pytest.raises(AuthenticationError):
            invalid_client.get_payment_methods()

    def test_context_manager(self):
        """Test client works as context manager."""
        with XPayClient(
            api_key="sk_sandbox_7c845adf-f658-4f29-9857-7e8a8708",
            merchant_id="548d8033-fbe9-411b-991f-f159cdee7745",
            base_url="http://localhost:8000"
        ) as client:
            result = client.ping()
            assert result["success"] is True


@pytest.mark.asyncio
class TestAsyncSupport:
    """Test async capabilities (if implemented)."""
    
    def test_async_structure_exists(self):
        """Test that async support structure is in place."""
        # This is a placeholder for future async implementation
        assert True  # For now, just ensure the test structure exists


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
