"""
LTFI-WSAP Client

Main client for interacting with LTFI-WSAP API
"""
import os
from typing import Optional, Dict, Any, List
import requests
from urllib.parse import urljoin

from .models import (
    Entity, CreateEntityRequest, UpdateEntityRequest,
    Verification, WSAPData, DisclosureLevel
)
from .exceptions import (
    WSAPException, AuthenticationError, NotFoundError,
    ValidationError, RateLimitError
)


class Client:
    """
    LTFI-WSAP API Client
    
    Usage:
        from ltfi_wsap import Client
        
        # Using environment variable LTFI_WSAP_API_KEY
        client = Client()
        
        # Or provide API key directly
        client = Client(api_key="your-api-key")
        
        # For self-hosted instances
        client = Client(
            api_key="your-api-key",
            base_url="https://your-instance.com"
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.ltfi.ai",
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize LTFI-WSAP client
        
        Args:
            api_key: API key for authentication (defaults to LTFI_WSAP_API_KEY env var)
            base_url: Base URL for API (for self-hosted instances)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_key = api_key or os.getenv("LTFI_WSAP_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Set LTFI_WSAP_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "LTFI-WSAP-Python/2.0.0"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or token expired")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 400:
                raise ValidationError(response.json().get("detail", "Validation error"))
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", 60)
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
            elif response.status_code >= 500:
                raise WSAPException(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            
            # Return JSON if available, otherwise return text
            try:
                return response.json()
            except:
                return {"data": response.text}
                
        except requests.exceptions.RequestException as e:
            raise WSAPException(f"Request failed: {str(e)}")
    
    # ========== Authentication ==========
    
    def login(self, username: str, password: str) -> Dict[str, str]:
        """
        Login with username and password
        
        Returns:
            Dictionary with access and refresh tokens
        """
        return self._request(
            "POST",
            "/api/auth/token/",
            json={"username": username, "password": password}
        )
    
    def refresh_token(self, refresh_token: str) -> str:
        """Refresh access token"""
        result = self._request(
            "POST",
            "/api/auth/token/refresh/",
            json={"refresh": refresh_token}
        )
        return result.get("access")
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user"""
        return self._request("GET", "/api/auth/user/")
    
    def get_permissions(self) -> Dict[str, Any]:
        """Get current user's permissions"""
        return self._request("GET", "/api/auth/user/permissions/")
    
    # ========== Entities ==========
    
    def list_entities(
        self,
        page: int = 1,
        page_size: int = 20,
        entity_type: Optional[str] = None,
        is_verified: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List entities with filtering
        
        Args:
            page: Page number
            page_size: Items per page
            entity_type: Filter by type (company, nonprofit, etc)
            is_verified: Filter by verification status
            search: Search query
            
        Returns:
            Paginated list of entities
        """
        params = {"page": page, "page_size": page_size}
        if entity_type:
            params["entity_type"] = entity_type
        if is_verified is not None:
            params["is_verified"] = str(is_verified).lower()
        if search:
            params["search"] = search
            
        return self._request("GET", "/api/entities/", params=params)
    
    def get_entity(self, entity_id: str) -> Entity:
        """Get entity by ID or slug"""
        data = self._request("GET", f"/api/entities/{entity_id}/")
        return Entity(**data)
    
    def create_entity(self, request: CreateEntityRequest) -> Entity:
        """Create new entity"""
        data = self._request(
            "POST",
            "/api/entities/",
            json=request.dict(exclude_none=True)
        )
        return Entity(**data)
    
    def update_entity(self, entity_id: str, request: UpdateEntityRequest) -> Entity:
        """Update existing entity"""
        data = self._request(
            "PATCH",
            f"/api/entities/{entity_id}/",
            json=request.dict(exclude_none=True)
        )
        return Entity(**data)
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity"""
        self._request("DELETE", f"/api/entities/{entity_id}/")
        return True
    
    # ========== Verification ==========
    
    def initiate_verification(
        self,
        domain: str,
        method: str = "dns_txt"
    ) -> Verification:
        """
        Start domain verification process
        
        Args:
            domain: Domain to verify
            method: Verification method (dns_txt, html_meta, file)
            
        Returns:
            Verification object with instructions
        """
        data = self._request(
            "POST",
            "/api/verification/initiate/",
            json={"domain": domain, "method": method}
        )
        return Verification(**data)
    
    def verify_domain(self, domain: str) -> bool:
        """
        Check if domain is verified
        
        Returns:
            True if verified, False otherwise
        """
        result = self._request(
            "POST",
            "/api/verification/verify/",
            json={"domain": domain}
        )
        return result.get("verified", False)
    
    def get_verification_status(self, domain: str) -> Verification:
        """Get detailed verification status"""
        data = self._request("GET", f"/api/wsap/v2/{domain}/status/")
        return Verification(**data)
    
    # ========== WSAP Data ==========
    
    def generate_wsap(
        self,
        entity_id: str,
        disclosure_level: DisclosureLevel = DisclosureLevel.STANDARD
    ) -> WSAPData:
        """
        Generate WSAP data for entity
        
        Args:
            entity_id: Entity ID or slug
            disclosure_level: Level of information to include
            
        Returns:
            Generated WSAP data
        """
        data = self._request(
            "POST",
            "/api/wsap/generate/",
            json={
                "entity_id": entity_id,
                "disclosure_level": disclosure_level.value
            }
        )
        return WSAPData(**data)
    
    def fetch_wsap(self, domain: str) -> WSAPData:
        """
        Fetch public WSAP data for domain
        
        Args:
            domain: Verified domain
            
        Returns:
            Public WSAP data
        """
        # Clean domain
        domain = domain.replace("https://", "").replace("http://", "").strip("/")
        data = self._request("GET", f"/api/wsap/public/{domain}/")
        return WSAPData(**data)
    
    def get_wsap_url(self, domain: str) -> str:
        """Get public WSAP URL for domain"""
        return f"{self.base_url}/.well-known/wsap.json?domain={domain}"
    
    # ========== Health & Stats ==========
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return self._request("GET", "/api/wsap/api/health/")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self._request("GET", "/api/wsap/api/stats/")
    
    # ========== Utility Methods ==========
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()