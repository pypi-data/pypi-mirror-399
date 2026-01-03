"""
AINative SDK Authentication Module

Handles API key authentication and authorization for AINative Studio APIs.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
import hashlib
import hmac
import base64


@dataclass
class AuthConfig:
    """Configuration for authentication."""
    
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    environment: str = "production"
    auto_refresh: bool = True
    timeout: int = 30
    
    def __post_init__(self):
        """Load from environment variables if not provided."""
        if not self.api_key:
            self.api_key = os.getenv("AINATIVE_API_KEY")
        if not self.api_secret:
            self.api_secret = os.getenv("AINATIVE_API_SECRET")
        
        # Validate environment
        valid_environments = ["production", "staging", "development", "local"]
        if self.environment not in valid_environments:
            raise ValueError(f"Invalid environment: {self.environment}")
    
    @property
    def is_configured(self) -> bool:
        """Check if authentication is properly configured."""
        return bool(self.api_key)


class APIKeyAuth:
    """Handles API key authentication for requests."""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self._token_cache: Optional[Dict[str, Any]] = None
        self._token_expiry: float = 0
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        if not self.config.api_key:
            raise ValueError("API key not configured")
        
        headers = {
            "X-API-Key": self.config.api_key,
            "X-SDK-Version": "0.1.0",
            "X-SDK-Language": "Python",
        }
        
        # Add signature if API secret is provided
        if self.config.api_secret:
            timestamp = str(int(time.time()))
            signature = self._generate_signature(timestamp)
            headers.update({
                "X-Timestamp": timestamp,
                "X-Signature": signature,
            })
        
        return headers
    
    def _generate_signature(self, timestamp: str) -> str:
        """Generate HMAC signature for request."""
        message = f"{self.config.api_key}{timestamp}"
        signature = hmac.new(
            self.config.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def get_bearer_token(self) -> Optional[str]:
        """Get Bearer token if using OAuth flow (future enhancement)."""
        # Placeholder for future OAuth implementation
        return None
    
    def validate_credentials(self) -> bool:
        """Validate that credentials are properly configured."""
        return self.config.is_configured
    
    def refresh_token(self) -> bool:
        """Refresh authentication token if needed (future enhancement)."""
        # Placeholder for future token refresh logic
        return True


class MultiTenantAuth(APIKeyAuth):
    """Extended authentication for multi-tenant scenarios."""
    
    def __init__(self, config: AuthConfig, organization_id: Optional[str] = None):
        super().__init__(config)
        self.organization_id = organization_id or os.getenv("AINATIVE_ORG_ID")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers including organization context."""
        headers = super().get_headers()
        
        if self.organization_id:
            headers["X-Organization-ID"] = self.organization_id
        
        return headers