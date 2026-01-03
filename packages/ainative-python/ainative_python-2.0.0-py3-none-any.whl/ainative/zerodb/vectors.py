"""
ZeroDB Vectors Module

Handles vector operations including upsert, search, and management.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional, Union
import numpy as np

if TYPE_CHECKING:
    from ..client import AINativeClient


class VectorsClient:
    """Client for ZeroDB vector operations."""
    
    def __init__(self, client: "AINativeClient"):
        """
        Initialize vectors client.
        
        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/zerodb/vectors"
    
    def upsert(
        self,
        project_id: str,
        vectors: List[Union[List[float], np.ndarray]],
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        namespace: str = "default",
    ) -> Dict[str, Any]:
        """
        Upsert vectors into the database.
        
        Args:
            project_id: Project ID
            vectors: List of vectors (as lists or numpy arrays)
            metadata: Optional metadata for each vector
            ids: Optional IDs for vectors (auto-generated if not provided)
            namespace: Namespace for vectors
        
        Returns:
            Upsert operation result
        """
        # Convert numpy arrays to lists if needed
        vector_data = []
        for i, vector in enumerate(vectors):
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
            
            item = {"vector": vector}
            
            if ids and i < len(ids):
                item["id"] = ids[i]
            
            if metadata and i < len(metadata):
                item["metadata"] = metadata[i]
            
            vector_data.append(item)
        
        data = {
            "project_id": project_id,
            "namespace": namespace,
            "items": vector_data,
        }
        
        return self.client.put(self.base_path, data=data)
    
    def search(
        self,
        project_id: str,
        vector: Union[List[float], np.ndarray],
        top_k: int = 10,
        namespace: str = "default",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_values: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            project_id: Project ID
            vector: Query vector
            top_k: Number of results to return
            namespace: Namespace to search in
            filter: Optional metadata filter
            include_metadata: Include metadata in results
            include_values: Include vector values in results
        
        Returns:
            List of search results with scores
        """
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        
        data = {
            "project_id": project_id,
            "vector": vector,
            "top_k": top_k,
            "namespace": namespace,
            "include_metadata": include_metadata,
            "include_values": include_values,
        }
        
        if filter:
            data["filter"] = filter
        
        response = self.client.post(f"{self.base_path}/search", data=data)
        return response.get("results", [])
    
    def get(
        self,
        project_id: str,
        ids: List[str],
        namespace: str = "default",
        include_metadata: bool = True,
        include_values: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get vectors by IDs.
        
        Args:
            project_id: Project ID
            ids: List of vector IDs
            namespace: Namespace
            include_metadata: Include metadata
            include_values: Include vector values
        
        Returns:
            List of vectors
        """
        params = {
            "project_id": project_id,
            "ids": ",".join(ids),
            "namespace": namespace,
            "include_metadata": include_metadata,
            "include_values": include_values,
        }
        
        response = self.client.get(self.base_path, params=params)
        return response.get("vectors", [])
    
    def delete(
        self,
        project_id: str,
        ids: Optional[List[str]] = None,
        namespace: str = "default",
        delete_all: bool = False,
        filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delete vectors.
        
        Args:
            project_id: Project ID
            ids: List of vector IDs to delete
            namespace: Namespace
            delete_all: Delete all vectors in namespace
            filter: Delete vectors matching filter
        
        Returns:
            Deletion result
        """
        data = {
            "project_id": project_id,
            "namespace": namespace,
        }
        
        if delete_all:
            data["delete_all"] = True
        elif ids:
            data["ids"] = ids
        elif filter:
            data["filter"] = filter
        else:
            raise ValueError("Must provide ids, filter, or delete_all=True")
        
        return self.client.delete(self.base_path, data=data)
    
    def update_metadata(
        self,
        project_id: str,
        id: str,
        metadata: Dict[str, Any],
        namespace: str = "default",
    ) -> Dict[str, Any]:
        """
        Update vector metadata.
        
        Args:
            project_id: Project ID
            id: Vector ID
            metadata: New metadata
            namespace: Namespace
        
        Returns:
            Update result
        """
        data = {
            "project_id": project_id,
            "id": id,
            "metadata": metadata,
            "namespace": namespace,
        }
        
        return self.client.patch(f"{self.base_path}/{id}/metadata", data=data)
    
    def describe_index_stats(
        self,
        project_id: str,
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Args:
            project_id: Project ID
            namespace: Optional namespace filter
        
        Returns:
            Index statistics
        """
        params = {"project_id": project_id}
        if namespace:
            params["namespace"] = namespace
        
        return self.client.get(f"{self.base_path}/stats", params=params)