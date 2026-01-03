"""
AINative SDK Main Client

Core client for interacting with AINative Studio APIs.
"""

from typing import Optional, Dict, Any, Union
import httpx
from urllib.parse import urljoin
import json
import time
from dataclasses import dataclass

from .auth import AuthConfig, APIKeyAuth
from .exceptions import (
    APIError,
    NetworkError,
    RateLimitError,
    AuthenticationError,
)
from .zerodb import ZeroDBClient
from .agent_swarm import AgentSwarmClient
from .agent_orchestration import AgentOrchestrationClient
from .agent_coordination import AgentCoordinationClient
from .agent_learning import AgentLearningClient
from .agent_state import AgentStateClient


@dataclass
class ClientConfig:
    """Configuration for the AINative client."""
    
    base_url: str = "https://api.ainative.studio"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    debug: bool = False
    
    def __post_init__(self):
        """Validate and normalize configuration."""
        # Ensure base URL doesn't end with slash
        self.base_url = self.base_url.rstrip("/")
        
        # Add API version if not present (and doesn't already contain /api/)
        if "/api/" not in self.base_url:
            self.base_url = f"{self.base_url}/api/v1"


class AINativeClient:
    """Main client for AINative Studio API operations."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        organization_id: Optional[str] = None,
        config: Optional[ClientConfig] = None,
        auth_config: Optional[AuthConfig] = None,
    ):
        """
        Initialize AINative client.
        
        Args:
            api_key: Your AINative API key
            api_secret: Your AINative API secret (optional, for enhanced security)
            base_url: Override default API base URL
            organization_id: Organization ID for multi-tenant scenarios
            config: Custom client configuration
            auth_config: Custom authentication configuration
        """
        # Set up configuration
        self.config = config or ClientConfig()
        if base_url:
            self.config.base_url = base_url
        
        # Set up authentication
        if auth_config:
            self.auth_config = auth_config
        else:
            self.auth_config = AuthConfig(
                api_key=api_key,
                api_secret=api_secret,
            )
        
        self.auth = APIKeyAuth(self.auth_config)
        self.organization_id = organization_id
        
        # Initialize HTTP client
        self._client = httpx.Client(
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )
        
        # Initialize sub-clients
        self._zerodb: Optional[ZeroDBClient] = None
        self._agent_swarm: Optional[AgentSwarmClient] = None
        self._agent_orchestration: Optional[AgentOrchestrationClient] = None
        self._agent_coordination: Optional[AgentCoordinationClient] = None
        self._agent_learning: Optional[AgentLearningClient] = None
        self._agent_state: Optional[AgentStateClient] = None
    
    @property
    def zerodb(self) -> ZeroDBClient:
        """Get ZeroDB operations client."""
        if not self._zerodb:
            self._zerodb = ZeroDBClient(self)
        return self._zerodb
    
    @property
    def agent_swarm(self) -> AgentSwarmClient:
        """Get Agent Swarm operations client."""
        if not self._agent_swarm:
            self._agent_swarm = AgentSwarmClient(self)
        return self._agent_swarm

    @property
    def agent_orchestration(self) -> AgentOrchestrationClient:
        """Get Agent Orchestration operations client."""
        if not self._agent_orchestration:
            self._agent_orchestration = AgentOrchestrationClient(self)
        return self._agent_orchestration

    @property
    def agent_coordination(self) -> AgentCoordinationClient:
        """Get Agent Coordination operations client."""
        if not self._agent_coordination:
            self._agent_coordination = AgentCoordinationClient(self)
        return self._agent_coordination

    @property
    def agent_learning(self) -> AgentLearningClient:
        """Get Agent Learning operations client."""
        if not self._agent_learning:
            self._agent_learning = AgentLearningClient(self)
        return self._agent_learning

    @property
    def agent_state(self) -> AgentStateClient:
        """Get Agent State operations client."""
        if not self._agent_state:
            self._agent_state = AgentStateClient(self)
        return self._agent_state
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments for httpx
        
        Returns:
            Response data as dictionary
        
        Raises:
            APIError: For API-related errors
            NetworkError: For network-related errors
            RateLimitError: When rate limit is exceeded
        """
        # Build full URL
        url = urljoin(self.config.base_url, endpoint.lstrip("/"))
        
        # Prepare headers
        request_headers = self.auth.get_headers()
        if headers:
            request_headers.update(headers)
        
        # Add organization ID if set
        if self.organization_id:
            request_headers["X-Organization-ID"] = self.organization_id
        
        # Make request with retries
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    **kwargs
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError(retry_after=retry_after)
                
                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API credentials")
                
                # Handle other errors
                if response.status_code >= 400:
                    raise APIError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )
                
                # Parse and return response
                if response.text:
                    return response.json()
                return {}
                
            except httpx.NetworkError as e:
                last_error = NetworkError(f"Network error: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                raise last_error
            
            except httpx.TimeoutException:
                last_error = NetworkError("Request timed out")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                raise last_error
        
        if last_error:
            raise last_error
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self.request("PATCH", endpoint, data=data, **kwargs)
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        return self.get("/health")
    
    def close(self):
        """Close the HTTP client connection."""
        self._client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()