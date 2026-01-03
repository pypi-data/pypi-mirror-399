"""
ZeroDB Module for AINative SDK

Provides high-level interface for ZeroDB operations including projects,
vectors, memory, and analytics.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import datetime

if TYPE_CHECKING:
    from ..client import AINativeClient

from .projects import ProjectsClient
from .vectors import VectorsClient
from .memory import MemoryClient
from .analytics import AnalyticsClient
from .tables import TablesClient


class ZeroDBClient:
    """Main client for ZeroDB operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize ZeroDB client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self._projects: Optional[ProjectsClient] = None
        self._vectors: Optional[VectorsClient] = None
        self._memory: Optional[MemoryClient] = None
        self._analytics: Optional[AnalyticsClient] = None
        self._tables: Optional[TablesClient] = None

    @property
    def projects(self) -> ProjectsClient:
        """Get projects operations client."""
        if not self._projects:
            self._projects = ProjectsClient(self.client)
        return self._projects

    @property
    def vectors(self) -> VectorsClient:
        """Get vectors operations client."""
        if not self._vectors:
            self._vectors = VectorsClient(self.client)
        return self._vectors

    @property
    def memory(self) -> MemoryClient:
        """Get memory operations client."""
        if not self._memory:
            self._memory = MemoryClient(self.client)
        return self._memory

    @property
    def analytics(self) -> AnalyticsClient:
        """Get analytics operations client."""
        if not self._analytics:
            self._analytics = AnalyticsClient(self.client)
        return self._analytics

    @property
    def tables(self) -> TablesClient:
        """Get NoSQL tables operations client."""
        if not self._tables:
            self._tables = TablesClient(self.client)
        return self._tables
    
    def health_check(self) -> Dict[str, Any]:
        """Check ZeroDB health status."""
        return self.client.get("/zerodb/health")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for ZeroDB."""
        return self.client.get("/zerodb/usage")


__all__ = [
    "ZeroDBClient",
    "ProjectsClient",
    "VectorsClient",
    "MemoryClient",
    "AnalyticsClient",
    "TablesClient",
]