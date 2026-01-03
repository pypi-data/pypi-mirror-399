"""
ZeroDB Projects Module

Handles project management operations in ZeroDB.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from ..client import AINativeClient


class ProjectStatus(Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectsClient:
    """Client for ZeroDB project operations."""
    
    def __init__(self, client: "AINativeClient"):
        """
        Initialize projects client.
        
        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/zerodb/projects"
    
    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[ProjectStatus] = None,
        organization_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all projects.
        
        Args:
            limit: Maximum number of projects to return
            offset: Number of projects to skip
            status: Filter by project status
            organization_id: Filter by organization ID
        
        Returns:
            Dictionary containing projects list and pagination info
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if status:
            params["status"] = status.value
        if organization_id:
            params["organization_id"] = organization_id
        
        return self.client.get(self.base_path, params=params)
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            metadata: Additional metadata
            config: Project configuration
        
        Returns:
            Created project details
        """
        data = {
            "name": name,
            "description": description or "",
            "metadata": metadata or {},
            "config": config or {},
        }
        
        return self.client.post(self.base_path, data=data)
    
    def get(self, project_id: str) -> Dict[str, Any]:
        """
        Get project details.
        
        Args:
            project_id: Project ID
        
        Returns:
            Project details
        """
        return self.client.get(f"{self.base_path}/{project_id}")
    
    def update(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update project details.
        
        Args:
            project_id: Project ID
            name: New project name
            description: New project description
            metadata: Updated metadata
            config: Updated configuration
        
        Returns:
            Updated project details
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        if config is not None:
            data["config"] = config
        
        return self.client.patch(f"{self.base_path}/{project_id}", data=data)
    
    def update_status(
        self,
        project_id: str,
        status: ProjectStatus,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            status: New status
            reason: Reason for status change
        
        Returns:
            Updated project details
        """
        data = {
            "status": status.value,
            "reason": reason,
        }
        
        return self.client.put(f"{self.base_path}/{project_id}/status", data=data)
    
    def suspend(self, project_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Suspend a project.
        
        Args:
            project_id: Project ID
            reason: Reason for suspension
        
        Returns:
            Updated project details
        """
        return self.update_status(project_id, ProjectStatus.SUSPENDED, reason)
    
    def activate(self, project_id: str) -> Dict[str, Any]:
        """
        Activate a suspended project.
        
        Args:
            project_id: Project ID
        
        Returns:
            Updated project details
        """
        return self.update_status(project_id, ProjectStatus.ACTIVE)
    
    def delete(self, project_id: str) -> Dict[str, Any]:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
        
        Returns:
            Deletion confirmation
        """
        return self.client.delete(f"{self.base_path}/{project_id}")
    
    def get_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Get project statistics.
        
        Args:
            project_id: Project ID
        
        Returns:
            Project statistics including storage, vectors, etc.
        """
        return self.client.get(f"{self.base_path}/{project_id}/statistics")
    
    def get_collections(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all collections for a project.
        
        Args:
            project_id: Project ID
        
        Returns:
            List of collections
        """
        response = self.client.get(f"{self.base_path}/{project_id}/collections")
        return response.get("collections", [])