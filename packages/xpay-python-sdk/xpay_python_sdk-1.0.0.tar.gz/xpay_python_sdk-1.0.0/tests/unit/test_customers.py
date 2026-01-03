"""
Unit tests for CustomersResource
"""

import pytest
from unittest.mock import Mock

from xpay.resources.customers import CustomersResource
from xpay.models import Customer, CreateCustomerRequest, CustomerListResponse


class TestCustomersResource:
    """Test CustomersResource functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.merchant_id = "test_merchant_123"
        self.customers = CustomersResource(self.mock_client, self.merchant_id)

    def test_create_customer(self):
        """Test creating a new customer."""
        customer_data = CreateCustomerRequest(
            email="test@example.com",
            name="John Doe",
            phone="+1234567890",
            description="Test customer",
            metadata={"tier": "premium"}
        )
        
        mock_response = {
            "success": True,
            "data": {
                "id": "cust_123",
                "email": "test@example.com",
                "name": "John Doe",
                "phone": "+1234567890",
                "description": "Test customer",
                "metadata": {"tier": "premium"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
        self.mock_client.post.return_value = mock_response
        
        result = self.customers.create(customer_data)
        
        self.mock_client.post.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers",
            customer_data.model_dump()
        )
        assert isinstance(result, Customer)
        assert result.id == "cust_123"
        assert result.email == "test@example.com"
        assert result.name == "John Doe"

    def test_create_customer_minimal(self):
        """Test creating customer with minimal required fields."""
        customer_data = CreateCustomerRequest(
            email="minimal@example.com",
            name="Jane Doe"
        )
        
        mock_response = {
            "success": True,
            "data": {
                "id": "cust_456",
                "email": "minimal@example.com",
                "name": "Jane Doe",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
        self.mock_client.post.return_value = mock_response
        
        result = self.customers.create(customer_data)
        
        assert result.email == "minimal@example.com"
        assert result.phone is None

    def test_retrieve_customer(self):
        """Test retrieving a customer by ID."""
        customer_id = "cust_123"
        mock_response = {
            "success": True,
            "data": {
                "id": customer_id,
                "email": "test@example.com",
                "name": "John Doe",
                "phone": "+1234567890",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.customers.retrieve(customer_id)
        
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers/{customer_id}"
        )
        assert result.id == customer_id
        assert result.email == "test@example.com"

    def test_update_customer(self):
        """Test updating a customer."""
        customer_id = "cust_123"
        update_data = {"name": "John Updated", "description": "Updated description"}
        
        mock_response = {
            "success": True,
            "data": {
                "id": customer_id,
                "email": "test@example.com",
                "name": "John Updated",
                "phone": "+1234567890",
                "description": "Updated description",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:01Z"
            }
        }
        self.mock_client.put.return_value = mock_response
        
        result = self.customers.update(customer_id, update_data)
        
        self.mock_client.put.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers/{customer_id}",
            update_data
        )
        assert result.name == "John Updated"
        assert result.description == "Updated description"

    def test_delete_customer(self):
        """Test deleting a customer."""
        customer_id = "cust_123"
        mock_response = {
            "success": True,
            "data": {"deleted": True}
        }
        self.mock_client.delete.return_value = mock_response
        
        result = self.customers.delete(customer_id)
        
        self.mock_client.delete.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers/{customer_id}"
        )
        assert result["deleted"] is True

    def test_list_customers_default(self):
        """Test listing customers with default parameters."""
        mock_response = {
            "success": True,
            "data": {
                "customers": [
                    {
                        "id": "cust_123",
                        "email": "test@example.com",
                        "name": "John Doe",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "has_more": False
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.customers.list()
        
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers",
            {}
        )
        assert isinstance(result, CustomerListResponse)
        assert len(result.customers) == 1
        assert result.total == 1

    def test_list_customers_with_filters(self):
        """Test listing customers with filter parameters."""
        mock_response = {
            "success": True,
            "data": {
                "customers": [],
                "total": 0,
                "has_more": False
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.customers.list(
            limit=10,
            offset=0,
            email="test@example.com"
        )
        
        expected_params = {
            "limit": "10",
            "offset": "0",
            "email": "test@example.com"
        }
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers",
            expected_params
        )

    def test_list_customers_with_date_filters(self):
        """Test listing customers with date range filters."""
        mock_response = {
            "success": True,
            "data": {
                "customers": [],
                "total": 0,
                "has_more": False
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.customers.list(
            created_after="2024-01-01",
            created_before="2024-12-31"
        )
        
        expected_params = {
            "created_after": "2024-01-01",
            "created_before": "2024-12-31"
        }
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers",
            expected_params
        )

    def test_list_customers_direct_list_response(self):
        """Test listing customers when API returns direct list."""
        mock_response = {
            "success": True,
            "data": [
                {
                    "id": "cust_123",
                    "email": "test@example.com",
                    "name": "John Doe",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.customers.list()
        
        assert isinstance(result, CustomerListResponse)
        assert len(result.customers) == 1
        assert result.total == 1

    def test_list_customers_with_name_filter(self):
        """Test listing customers filtered by name."""
        mock_response = {
            "success": True,
            "data": {
                "customers": [],
                "total": 0,
                "has_more": False
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.customers.list(name="John")
        
        expected_params = {"name": "John"}
        self.mock_client.get.assert_called_once_with(
            f"/v1/api/merchants/{self.merchant_id}/customers",
            expected_params
        )
