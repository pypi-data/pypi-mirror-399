"""
Test configuration and fixtures for X-Pay Python SDK tests
"""

import pytest
import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "success": True,
        "data": {
            "id": "test_123",
            "status": "completed",
            "amount": "10.00",
            "currency": "USD"
        }
    }


@pytest.fixture 
def test_client():
    """Test client with mock credentials."""
    from xpay import XPayClient
    return XPayClient(
        api_key="sk_sandbox_test123",
        merchant_id="test_merchant_123",
        environment="sandbox"
    )


@pytest.fixture
def live_client():
    """Live client with working credentials for integration tests."""
    from xpay import XPayClient
    return XPayClient(
        api_key="sk_sandbox_7c845adf-f658-4f29-9857-7e8a8708",
        merchant_id="548d8033-fbe9-411b-991f-f159cdee7745",
        environment="sandbox",
        base_url="http://localhost:8000"
    )


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "asyncio: marks tests as async tests")