"""
HTTP client for X-Pay API requests
"""

import json
import time
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    XPayError, 
    AuthenticationError,
    ValidationError, 
    NetworkError,
    APIError,
    TimeoutError,
)
from .types.config import XPayConfig, API_KEY_PATTERNS, DEFAULT_URLS


class HTTPClient:
    """HTTP client for making requests to X-Pay API."""
    
    def __init__(self, config: XPayConfig) -> None:
        self.config = config
        self._session: Optional[requests.Session] = None
    
    @property
    def session(self) -> requests.Session:
        """Get or create requests session with retry configuration."""
        if self._session is None:
            self._session = requests.Session()
            
            # Configure retries
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=0.3,
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        
        return self._session
    
    def get_base_url(self) -> str:
        """Get base URL for API requests."""
        if self.config.base_url:
            return self.config.base_url
        
        environment = self.detect_environment()
        return DEFAULT_URLS.get(environment, DEFAULT_URLS["sandbox"])
    
    def detect_environment(self) -> str:
        """Detect environment from API key prefix."""
        if self.config.environment:
            return self.config.environment
        
        api_key = self.config.api_key
        
        # Check for sandbox patterns
        for pattern in API_KEY_PATTERNS["sandbox"]:
            if api_key.startswith(pattern):
                return "sandbox"
        
        # Check for live patterns  
        for pattern in API_KEY_PATTERNS["live"]:
            if api_key.startswith(pattern):
                return "live"
        
        # Default to sandbox for development
        return "sandbox"
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        environment = self.detect_environment()
        
        return {
            "X-API-Key": self.config.api_key,
            "Content-Type": "application/json",
            "User-Agent": "xpay-python-sdk/1.0.0",
            "X-SDK-Version": "1.0.0",
            "X-Environment": environment,
        }
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = urljoin(self.get_base_url(), endpoint)
        headers = self.get_headers()
        
        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers,
            "timeout": self.config.timeout,
        }
        
        if data and method.upper() != "GET":
            request_kwargs["json"] = data
        
        if params:
            request_kwargs["params"] = params
        
        try:
            response = self.session.request(**request_kwargs)  # type: ignore
            
            # Handle different response status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check your API key.",
                    status=response.status_code
                )
            elif response.status_code == 400:
                error_data = self._parse_error_response(response)
                raise ValidationError(
                    error_data.get("message", "Validation failed"),
                    status=response.status_code,
                    details=error_data
                )
            elif 400 <= response.status_code < 500:
                error_data = self._parse_error_response(response)
                raise APIError(
                    error_data.get("message", f"Client error: {response.status_code}"),
                    status=response.status_code,
                    details=error_data
                )
            elif response.status_code >= 500:
                error_data = self._parse_error_response(response)
                raise APIError(
                    error_data.get("message", f"Server error: {response.status_code}"),
                    status=response.status_code,
                    details=error_data
                )
            
            # Success - parse response
            try:
                result = response.json()
                # Backend returns data directly, wrap in our expected format
                return {
                    "success": True,
                    "data": result,
                    "message": None,
                    "error": None
                }
            except json.JSONDecodeError:
                raise APIError(
                    "Invalid JSON response from server",
                    status=response.status_code
                )
                
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timeout")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")
    
    def _parse_error_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse error response from API."""
        try:
            return response.json()  # type: ignore
        except json.JSONDecodeError:
            return {"message": response.text or f"HTTP {response.status_code}"}
    
    def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        return self.request("GET", endpoint, params=params)
    
    def post(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return self.request("POST", endpoint, data=data)
    
    def put(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PUT request.""" 
        return self.request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self.request("DELETE", endpoint)
    
    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()
            self._session = None