"""
Customers resource for X-Pay SDK
"""

from typing import Optional, Dict, Any

from ..http_client import HTTPClient
from ..models import (
    Customer,
    CreateCustomerRequest,
    CustomerListResponse,
)


class CustomersResource:
    """Resource for managing customers."""
    
    def __init__(self, client: HTTPClient, merchant_id: str) -> None:
        self.client = client
        self.merchant_id = merchant_id
    
    def create(self, customer_data: CreateCustomerRequest) -> Customer:
        """Create a new customer."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/customers"
        response = self.client.post(endpoint, customer_data.model_dump())
        
        return Customer(**response["data"])
    
    def retrieve(self, customer_id: str) -> Customer:
        """Retrieve a customer by ID."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/customers/{customer_id}"
        response = self.client.get(endpoint)
        
        return Customer(**response["data"])
    
    def update(self, customer_id: str, update_data: dict) -> Customer:
        """Update a customer."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/customers/{customer_id}"
        response = self.client.put(endpoint, update_data)
        
        return Customer(**response["data"])
    
    def delete(self, customer_id: str) -> Dict[str, Any]:
        """Delete a customer."""
        endpoint = f"/v1/api/merchants/{self.merchant_id}/customers/{customer_id}"
        response = self.client.delete(endpoint)
        
        return response.get("data", {})
    
    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
    ) -> CustomerListResponse:
        """List customers with optional filters."""
        params: Dict[str, str] = {}
        
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)
        if email:
            params["email"] = email
        if name:
            params["name"] = name
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        
        endpoint = f"/v1/api/merchants/{self.merchant_id}/customers"
        response = self.client.get(endpoint, params)
        
        # Handle both direct list and wrapped response
        if isinstance(response["data"], list):
            return CustomerListResponse(customers=response["data"], total=len(response["data"]))
        return CustomerListResponse(**response["data"])