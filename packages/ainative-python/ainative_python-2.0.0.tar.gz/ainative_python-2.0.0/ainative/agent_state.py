"""
Agent State Module for AINative SDK

Provides interface for agent state management, checkpoints, and recovery.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from .client import AINativeClient


class AgentStateClient:
    """Client for Agent State operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize Agent State client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/agent-state"

    def create_state(
        self,
        agent_id: str,
        state_data: Dict[str, Any],
        state_type: str = "working",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create or update agent state.

        Args:
            agent_id: Agent ID
            state_data: State data to store
            state_type: Type of state (working, checkpoint, snapshot)
            metadata: Additional metadata

        Returns:
            Created state details
        """
        data = {
            "agent_id": agent_id,
            "state_data": state_data,
            "state_type": state_type,
            "metadata": metadata or {},
        }

        return self.client.post(f"{self.base_path}/states", data=data)

    def get_state(
        self,
        agent_id: str,
        state_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get agent state.

        Args:
            agent_id: Agent ID
            state_id: Optional specific state ID (if not provided, returns latest)

        Returns:
            Agent state data
        """
        if state_id:
            return self.client.get(f"{self.base_path}/states/{state_id}")
        else:
            params = {"agent_id": agent_id}
            return self.client.get(f"{self.base_path}/states/latest", params=params)

    def update_state(
        self,
        state_id: str,
        state_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update existing agent state.

        Args:
            state_id: State ID
            state_data: Updated state data

        Returns:
            Updated state details
        """
        data = {
            "state_data": state_data,
        }

        return self.client.put(f"{self.base_path}/states/{state_id}", data=data)

    def delete_state(
        self,
        state_id: str,
    ) -> Dict[str, Any]:
        """
        Delete agent state.

        Args:
            state_id: State ID to delete

        Returns:
            Deletion confirmation
        """
        return self.client.delete(f"{self.base_path}/states/{state_id}")

    def list_states(
        self,
        agent_id: str,
        state_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List agent states.

        Args:
            agent_id: Agent ID
            state_type: Filter by state type
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of states with pagination metadata
        """
        params = {
            "agent_id": agent_id,
            "limit": limit,
            "offset": offset,
        }

        if state_type:
            params["state_type"] = state_type

        return self.client.get(f"{self.base_path}/states", params=params)

    def create_checkpoint(
        self,
        agent_id: str,
        checkpoint_name: str,
        state_data: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a state checkpoint for recovery.

        Args:
            agent_id: Agent ID
            checkpoint_name: Checkpoint name
            state_data: State data to checkpoint
            description: Optional checkpoint description

        Returns:
            Created checkpoint details
        """
        data = {
            "agent_id": agent_id,
            "checkpoint_name": checkpoint_name,
            "state_data": state_data,
        }

        if description:
            data["description"] = description

        return self.client.post(f"{self.base_path}/checkpoints", data=data)

    def restore_checkpoint(
        self,
        checkpoint_id: str,
    ) -> Dict[str, Any]:
        """
        Restore agent state from a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to restore

        Returns:
            Restored state data
        """
        return self.client.post(
            f"{self.base_path}/checkpoints/{checkpoint_id}/restore"
        )

    def list_checkpoints(
        self,
        agent_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List agent checkpoints.

        Args:
            agent_id: Agent ID
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of checkpoints with pagination metadata
        """
        params = {
            "agent_id": agent_id,
            "limit": limit,
            "offset": offset,
        }

        return self.client.get(f"{self.base_path}/checkpoints", params=params)

    def delete_checkpoint(
        self,
        checkpoint_id: str,
    ) -> Dict[str, Any]:
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to delete

        Returns:
            Deletion confirmation
        """
        return self.client.delete(f"{self.base_path}/checkpoints/{checkpoint_id}")


__all__ = [
    "AgentStateClient",
]
