"""
Agent Orchestration Module for AINative SDK

Provides interface for orchestrating AI agent instances and tasks.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from .client import AINativeClient


class AgentOrchestrationClient:
    """Client for Agent Orchestration operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize Agent Orchestration client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/agent-orchestration"

    def create_agent_instance(
        self,
        name: str,
        agent_type: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new agent instance.

        Args:
            name: Agent instance name
            agent_type: Type of agent (researcher, coder, reviewer, etc.)
            capabilities: List of agent capabilities
            config: Additional agent configuration

        Returns:
            Created agent instance details
        """
        data = {
            "name": name,
            "agent_type": agent_type,
            "capabilities": capabilities,
            "config": config or {},
        }

        return self.client.post(f"{self.base_path}/agents", data=data)

    def list_agent_instances(
        self,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List agent instances with optional filtering.

        Args:
            agent_type: Filter by agent type
            status: Filter by status (active, idle, error)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of agent instances with pagination metadata
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if agent_type:
            params["agent_type"] = agent_type
        if status:
            params["status"] = status

        return self.client.get(f"{self.base_path}/agents", params=params)

    def get_agent_instance(self, agent_id: str) -> Dict[str, Any]:
        """
        Get details of a specific agent instance.

        Args:
            agent_id: Agent instance ID

        Returns:
            Agent instance details
        """
        return self.client.get(f"{self.base_path}/agents/{agent_id}")

    def create_task(
        self,
        agent_id: str,
        task_type: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        priority: str = "medium",
    ) -> Dict[str, Any]:
        """
        Create a new task for an agent instance.

        Args:
            agent_id: Agent instance ID
            task_type: Type of task
            description: Task description
            context: Task context data
            priority: Task priority (low, medium, high, critical)

        Returns:
            Created task details
        """
        data = {
            "agent_id": agent_id,
            "task_type": task_type,
            "description": description,
            "context": context or {},
            "priority": priority,
        }

        return self.client.post(f"{self.base_path}/tasks", data=data)

    def execute_task(
        self,
        task_id: str,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task.

        Args:
            task_id: Task ID to execute
            agent_id: Optional specific agent to use

        Returns:
            Task execution result
        """
        data = {}
        if agent_id:
            data["agent_id"] = agent_id

        return self.client.post(
            f"{self.base_path}/tasks/{task_id}/execute",
            data=data
        )

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task execution status.

        Args:
            task_id: Task ID

        Returns:
            Task status and progress details
        """
        return self.client.get(f"{self.base_path}/tasks/{task_id}/status")

    def list_tasks(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List tasks with optional filtering.

        Args:
            agent_id: Filter by agent instance
            status: Filter by status (pending, running, completed, failed)
            task_type: Filter by task type
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of tasks with pagination metadata
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        if task_type:
            params["task_type"] = task_type

        return self.client.get(f"{self.base_path}/tasks", params=params)


__all__ = [
    "AgentOrchestrationClient",
]
