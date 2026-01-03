"""
Unit tests for HTTPClient
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from xpay.http_client import HTTPClient
from xpay.types.config import XPayConfig
from xpay.exceptions import (
    AuthenticationError,
    ValidationError,
    NetworkError,
    APIError,
    TimeoutError,
)


class TestHTTPClientInit:
    """Test HTTPClient initialization."""

    def test_client_initialization(self):
        """Test HTTP client can be initialized."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123",
            timeout=30
        )
        client = HTTPClient(config)
        
        assert client.config == config
        assert client._session is None

    def test_session_lazy_initialization(self):
        """Test session is lazily initialized."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        # Session should be None initially
        assert client._session is None
        
        # Accessing session property should create it
        session = client.session
        assert session is not None
        assert isinstance(session, requests.Session)


class TestHTTPClientEnvironmentDetection:
    """Test environment detection from API key."""

    def test_detect_sandbox_from_sk_sandbox_prefix(self):
        """Test sandbox detection from sk_sandbox_ prefix."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        assert client.detect_environment() == "sandbox"

    def test_detect_live_from_sk_live_prefix(self):
        """Test live detection from sk_live_ prefix."""
        config = XPayConfig(
            api_key="sk_live_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        assert client.detect_environment() == "live"

    def test_detect_sandbox_from_xpay_sandbox_prefix(self):
        """Test sandbox detection from xpay_sandbox_ prefix."""
        config = XPayConfig(
            api_key="xpay_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        assert client.detect_environment() == "sandbox"

    def test_detect_live_from_xpay_live_prefix(self):
        """Test live detection from xpay_live_ prefix."""
        config = XPayConfig(
            api_key="xpay_live_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        assert client.detect_environment() == "live"

    def test_default_to_sandbox_for_unknown(self):
        """Test defaults to sandbox for unknown key format."""
        config = XPayConfig(
            api_key="unknown_key_format",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        assert client.detect_environment() == "sandbox"

    def test_explicit_environment_override(self):
        """Test explicit environment takes precedence."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123",
            environment="live"  # Override despite sandbox key
        )
        client = HTTPClient(config)
        
        assert client.detect_environment() == "live"


class TestHTTPClientHeaders:
    """Test header generation."""

    def test_get_headers_sandbox(self):
        """Test headers for sandbox environment."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        headers = client.get_headers()
        
        assert headers["X-API-Key"] == "sk_sandbox_test123"
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Environment"] == "sandbox"
        assert "User-Agent" in headers
        assert "X-SDK-Version" in headers

    def test_get_headers_live(self):
        """Test headers for live environment."""
        config = XPayConfig(
            api_key="sk_live_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        headers = client.get_headers()
        
        assert headers["X-Environment"] == "live"


class TestHTTPClientBaseUrl:
    """Test base URL handling."""

    def test_custom_base_url(self):
        """Test custom base URL is used when provided."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123",
            base_url="https://custom-api.example.com"
        )
        client = HTTPClient(config)
        
        assert client.get_base_url() == "https://custom-api.example.com"

    def test_default_sandbox_url(self):
        """Test default sandbox URL when no custom URL."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        base_url = client.get_base_url()
        # Should be a valid URL (sandbox default)
        assert base_url.startswith("http")


class TestHTTPClientRequests:
    """Test HTTP request methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123",
            base_url="https://api.example.com"
        )
        self.client = HTTPClient(self.config)

    @patch('xpay.http_client.HTTPClient.session')
    def test_get_request(self, mock_session):
        """Test GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        mock_session.request.return_value = mock_response
        
        result = self.client.get("/v1/test")
        
        mock_session.request.assert_called_once()
        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["method"] == "GET"
        assert "/v1/test" in call_kwargs["url"]
        assert result["success"] is True
        assert result["data"]["id"] == "123"

    @patch('xpay.http_client.HTTPClient.session')
    def test_post_request_with_data(self, mock_session):
        """Test POST request with data."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "pay_123"}
        mock_session.request.return_value = mock_response
        
        data = {"amount": "10.00", "currency": "USD"}
        result = self.client.post("/v1/payments", data)
        
        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["method"] == "POST"
        assert call_kwargs["json"] == data
        assert result["success"] is True

    @patch('xpay.http_client.HTTPClient.session')
    def test_put_request(self, mock_session):
        """Test PUT request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "name": "Updated"}
        mock_session.request.return_value = mock_response
        
        data = {"name": "Updated"}
        result = self.client.put("/v1/test/123", data)
        
        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["method"] == "PUT"

    @patch('xpay.http_client.HTTPClient.session')
    def test_delete_request(self, mock_session):
        """Test DELETE request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"deleted": True}
        mock_session.request.return_value = mock_response
        
        result = self.client.delete("/v1/test/123")
        
        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["method"] == "DELETE"


class TestHTTPClientErrorHandling:
    """Test error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123",
            base_url="https://api.example.com"
        )
        self.client = HTTPClient(self.config)

    @patch('xpay.http_client.HTTPClient.session')
    def test_401_raises_authentication_error(self, mock_session):
        """Test 401 raises AuthenticationError."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_session.request.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            self.client.get("/v1/test")

    @patch('xpay.http_client.HTTPClient.session')
    def test_400_raises_validation_error(self, mock_session):
        """Test 400 raises ValidationError."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request data"}
        mock_session.request.return_value = mock_response
        
        with pytest.raises(ValidationError, match="Invalid request data"):
            self.client.post("/v1/test", {"invalid": True})

    @patch('xpay.http_client.HTTPClient.session')
    def test_500_raises_api_error(self, mock_session):
        """Test 500 raises APIError."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_session.request.return_value = mock_response
        
        with pytest.raises(APIError, match="Internal server error"):
            self.client.get("/v1/test")

    @patch('xpay.http_client.HTTPClient.session')
    def test_404_raises_api_error(self, mock_session):
        """Test 404 raises APIError."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}
        mock_session.request.return_value = mock_response
        
        with pytest.raises(APIError, match="Not found"):
            self.client.get("/v1/notfound")

    @patch('xpay.http_client.HTTPClient.session')
    def test_timeout_raises_timeout_error(self, mock_session):
        """Test timeout raises TimeoutError."""
        mock_session.request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(TimeoutError, match="timeout"):
            self.client.get("/v1/test")

    @patch('xpay.http_client.HTTPClient.session')
    def test_connection_error_raises_network_error(self, mock_session):
        """Test connection error raises NetworkError."""
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(NetworkError, match="Connection error"):
            self.client.get("/v1/test")

    @patch('xpay.http_client.HTTPClient.session')
    def test_invalid_json_response(self, mock_session):
        """Test invalid JSON response raises APIError."""
        import json as json_module
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json_module.JSONDecodeError("Not JSON", "", 0)
        mock_session.request.return_value = mock_response
        
        with pytest.raises(APIError, match="Invalid JSON"):
            self.client.get("/v1/test")


class TestHTTPClientSessionManagement:
    """Test session management."""

    def test_close_session(self):
        """Test closing the session."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        # Access session to create it
        _ = client.session
        assert client._session is not None
        
        # Close session
        client.close()
        assert client._session is None

    def test_close_when_no_session(self):
        """Test closing when no session exists."""
        config = XPayConfig(
            api_key="sk_sandbox_test123",
            merchant_id="merchant_123"
        )
        client = HTTPClient(config)
        
        # Should not raise error
        client.close()
        assert client._session is None
