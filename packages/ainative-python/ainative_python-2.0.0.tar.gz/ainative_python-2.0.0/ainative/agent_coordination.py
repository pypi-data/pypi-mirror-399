"""
Agent Coordination Module for AINative SDK

Provides interface for coordinating agent communication and task sequences.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from .client import AINativeClient


class AgentCoordinationClient:
    """Client for Agent Coordination operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize Agent Coordination client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/agent-coordination"

    def send_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message: str,
        message_type: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message between agents.

        Args:
            from_agent_id: Sender agent ID
            to_agent_id: Recipient agent ID
            message: Message content
            message_type: Type of message (info, request, response, error)
            metadata: Additional message metadata

        Returns:
            Message delivery confirmation
        """
        data = {
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "message": message,
            "message_type": message_type,
            "metadata": metadata or {},
        }

        return self.client.post(f"{self.base_path}/messages", data=data)

    def get_messages(
        self,
        agent_id: str,
        direction: str = "received",
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get messages for an agent.

        Args:
            agent_id: Agent ID
            direction: Message direction (sent, received, all)
            limit: Maximum number of messages
            offset: Pagination offset

        Returns:
            List of messages with pagination metadata
        """
        params = {
            "agent_id": agent_id,
            "direction": direction,
            "limit": limit,
            "offset": offset,
        }

        return self.client.get(f"{self.base_path}/messages", params=params)

    def create_task_sequence(
        self,
        name: str,
        tasks: List[Dict[str, Any]],
        execution_mode: str = "sequential",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a task sequence for coordinated execution.

        Args:
            name: Sequence name
            tasks: List of task definitions
            execution_mode: Execution mode (sequential, parallel, conditional)
            config: Additional sequence configuration

        Returns:
            Created task sequence details
        """
        data = {
            "name": name,
            "tasks": tasks,
            "execution_mode": execution_mode,
            "config": config or {},
        }

        return self.client.post(f"{self.base_path}/sequences", data=data)

    def execute_sequence(
        self,
        sequence_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task sequence.

        Args:
            sequence_id: Sequence ID to execute
            context: Execution context data

        Returns:
            Sequence execution result
        """
        data = {
            "context": context or {},
        }

        return self.client.post(
            f"{self.base_path}/sequences/{sequence_id}/execute",
            data=data
        )

    def get_sequence_status(self, sequence_id: str) -> Dict[str, Any]:
        """
        Get task sequence execution status.

        Args:
            sequence_id: Sequence ID

        Returns:
            Sequence status and progress details
        """
        return self.client.get(f"{self.base_path}/sequences/{sequence_id}/status")

    def list_sequences(
        self,
        execution_mode: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List task sequences with optional filtering.

        Args:
            execution_mode: Filter by execution mode
            status: Filter by status
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of sequences with pagination metadata
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if execution_mode:
            params["execution_mode"] = execution_mode
        if status:
            params["status"] = status

        return self.client.get(f"{self.base_path}/sequences", params=params)

    def get_agent_workload(
        self,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get agent workload statistics.

        Args:
            agent_id: Optional specific agent ID (if not provided, returns all agents)

        Returns:
            Workload statistics
        """
        params = {}
        if agent_id:
            params["agent_id"] = agent_id

        return self.client.get(f"{self.base_path}/agents/workload", params=params)

    def distribute_workload(
        self,
        tasks: List[str],
        agents: List[str],
        strategy: str = "round_robin",
    ) -> Dict[str, Any]:
        """
        Distribute tasks across multiple agents.

        Args:
            tasks: List of task IDs to distribute
            agents: List of agent IDs
            strategy: Distribution strategy (round_robin, least_loaded, capability_match)

        Returns:
            Task distribution plan
        """
        data = {
            "tasks": tasks,
            "agents": agents,
            "strategy": strategy,
        }

        return self.client.post(f"{self.base_path}/workload/distribute", data=data)

    def sync_agents(
        self,
        agent_ids: List[str],
        checkpoint: str,
    ) -> Dict[str, Any]:
        """
        Synchronize multiple agents at a checkpoint.

        Args:
            agent_ids: List of agent IDs to synchronize
            checkpoint: Checkpoint identifier

        Returns:
            Synchronization result
        """
        data = {
            "agent_ids": agent_ids,
            "checkpoint": checkpoint,
        }

        return self.client.post(f"{self.base_path}/sync", data=data)


__all__ = [
    "AgentCoordinationClient",
]
