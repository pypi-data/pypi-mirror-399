"""
AINative Python SDK

Official Python SDK for AINative Studio APIs including ZeroDB and Agent Swarm operations.
"""

__version__ = "2.0.0"
__author__ = "AINative Team"
__email__ = "support@ainative.studio"

from .client import AINativeClient
from .auth import AuthConfig, APIKeyAuth
from .exceptions import (
    AINativeException,
    AuthenticationError,
    APIError,
    NetworkError,
    ValidationError,
    RateLimitError,
)

# Convenience imports for common operations
from .zerodb import ZeroDBClient
from .agent_swarm import AgentSwarmClient
from .agent_orchestration import AgentOrchestrationClient
from .agent_coordination import AgentCoordinationClient
from .agent_learning import AgentLearningClient
from .agent_state import AgentStateClient

__all__ = [
    "AINativeClient",
    "AuthConfig",
    "APIKeyAuth",
    "AINativeException",
    "AuthenticationError",
    "APIError",
    "NetworkError",
    "ValidationError",
    "RateLimitError",
    "ZeroDBClient",
    "AgentSwarmClient",
    "AgentOrchestrationClient",
    "AgentCoordinationClient",
    "AgentLearningClient",
    "AgentStateClient",
]