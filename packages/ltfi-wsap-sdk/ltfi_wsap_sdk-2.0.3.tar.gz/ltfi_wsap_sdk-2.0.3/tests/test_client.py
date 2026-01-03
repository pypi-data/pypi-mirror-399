"""
Tests for LTFI-WSAP Client
"""
import pytest
import responses
from ltfi_wsap import Client, AuthenticationError, NotFoundError
from ltfi_wsap.models import Entity, DisclosureLevel


class TestClient:
    def setup_method(self):
        """Setup test client"""
        self.client = Client(
            api_key="test-api-key",
            base_url="https://api.test.com"
        )

    def test_client_initialization_with_api_key(self):
        """Test client initialization with API key"""
        client = Client(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.ltfi.ai"

    def test_client_initialization_no_api_key_raises_error(self):
        """Test client raises error without API key"""
        with pytest.raises(AuthenticationError):
            Client()

    @responses.activate
    def test_list_entities(self):
        """Test listing entities"""
        mock_response = {
            "count": 1,
            "results": [{
                "id": 1,
                "entity_id": "test-uuid",
                "entity_type": "company",
                "display_name": "Test Company",
                "slug": "test-company-123",
                "parent_entity": None,
                "created_by": 1,
                "is_active": True,
                "is_published": True,
                "is_verified": False,
                "template_id": None,
                "inherits_from_parent": False,
                "wsap_data": {},
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }]
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/entities/",
            json=mock_response,
            status=200
        )
        
        result = self.client.list_entities()
        assert result["count"] == 1
        assert len(result["results"]) == 1

    @responses.activate
    def test_get_entity(self):
        """Test getting a specific entity"""
        mock_entity = {
            "id": 1,
            "entity_id": "test-uuid",
            "entity_type": "company",
            "display_name": "Test Company",
            "slug": "test-company-123",
            "parent_entity": None,
            "created_by": 1,
            "is_active": True,
            "is_published": True,
            "is_verified": False,
            "template_id": None,
            "inherits_from_parent": False,
            "wsap_data": {},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/entities/test-company-123/",
            json=mock_entity,
            status=200
        )
        
        entity = self.client.get_entity("test-company-123")
        assert isinstance(entity, Entity)
        assert entity.display_name == "Test Company"

    @responses.activate
    def test_get_entity_not_found(self):
        """Test getting non-existent entity raises error"""
        responses.add(
            responses.GET,
            "https://api.test.com/api/entities/nonexistent/",
            status=404
        )
        
        with pytest.raises(NotFoundError):
            self.client.get_entity("nonexistent")

    @responses.activate
    def test_authentication_error_on_401(self):
        """Test authentication error handling"""
        responses.add(
            responses.GET,
            "https://api.test.com/api/entities/",
            status=401
        )
        
        with pytest.raises(AuthenticationError):
            self.client.list_entities()

    @responses.activate
    def test_initiate_verification(self):
        """Test initiating domain verification"""
        mock_verification = {
            "id": "verification-uuid",
            "entity": 1,
            "domain": "example.com",
            "verification_token": "test-token",
            "txt_record_name": "_wsap-verify.example.com",
            "txt_record_value": "wsap-verify=test-token",
            "verification_method": "dns",
            "status": "pending",
            "verified_at": None,
            "attempts": 0,
            "max_attempts": 3
        }
        
        responses.add(
            responses.POST,
            "https://api.test.com/api/verification/initiate/",
            json=mock_verification,
            status=200
        )
        
        result = self.client.initiate_verification("example.com")
        assert result["domain"] == "example.com"
        assert result["status"] == "pending"