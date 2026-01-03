"""
Agent Swarm Module for AINative SDK

Provides interface for orchestrating and managing AI agent swarms.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional
from enum import Enum

if TYPE_CHECKING:
    from ..client import AINativeClient


class AgentType(Enum):
    """Types of agents available in the swarm."""
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    ANALYST = "analyst"
    DESIGNER = "designer"
    ORCHESTRATOR = "orchestrator"


class SwarmStatus(Enum):
    """Status of agent swarm."""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentSwarmClient:
    """Main client for Agent Swarm operations."""
    
    def __init__(self, client: "AINativeClient"):
        """
        Initialize Agent Swarm client.
        
        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/agent-swarm"
    
    def start_swarm(
        self,
        project_id: str,
        agents: List[Dict[str, Any]],
        objective: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start a new agent swarm.
        
        Args:
            project_id: Project ID
            agents: List of agent configurations
            objective: Swarm objective/goal
            config: Additional swarm configuration
        
        Returns:
            Swarm initialization details
        """
        data = {
            "project_id": project_id,
            "agents": agents,
            "objective": objective,
            "config": config or {},
        }
        
        return self.client.post(f"{self.base_path}/start", data=data)
    
    def orchestrate(
        self,
        swarm_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate agents for a specific task.
        
        Args:
            swarm_id: Swarm ID
            task: Task description
            context: Task context
            agents: Specific agents to use (optional)
        
        Returns:
            Orchestration result
        """
        data = {
            "swarm_id": swarm_id,
            "task": task,
            "context": context or {},
        }
        
        if agents:
            data["agents"] = agents
        
        return self.client.post(f"{self.base_path}/orchestrate", data=data)
    
    def get_status(self, swarm_id: str) -> Dict[str, Any]:
        """
        Get swarm status.
        
        Args:
            swarm_id: Swarm ID
        
        Returns:
            Swarm status details
        """
        return self.client.get(f"{self.base_path}/{swarm_id}/status")
    
    def get_metrics(
        self,
        swarm_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get swarm performance metrics.
        
        Args:
            swarm_id: Optional swarm ID filter
            project_id: Optional project ID filter
        
        Returns:
            Swarm metrics
        """
        params = {}
        if swarm_id:
            params["swarm_id"] = swarm_id
        if project_id:
            params["project_id"] = project_id
        
        return self.client.get(f"{self.base_path}/metrics", params=params)
    
    def get_agent_types(self) -> List[Dict[str, Any]]:
        """
        Get available agent types and their capabilities.
        
        Returns:
            List of agent types with descriptions
        """
        response = self.client.get(f"{self.base_path}/agent-types")
        return response.get("agent_types", [])
    
    def configure_agent(
        self,
        swarm_id: str,
        agent_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Configure a specific agent.
        
        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID
            config: Agent configuration
        
        Returns:
            Configuration result
        """
        return self.client.put(
            f"{self.base_path}/{swarm_id}/agents/{agent_id}/config",
            data=config
        )
    
    def set_agent_prompt(
        self,
        swarm_id: str,
        agent_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set agent prompt configuration.
        
        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID
            prompt: Main prompt
            system_prompt: System prompt (optional)
        
        Returns:
            Prompt configuration result
        """
        data = {"prompt": prompt}
        if system_prompt:
            data["system_prompt"] = system_prompt
        
        return self.client.post(
            f"{self.base_path}/{swarm_id}/agents/{agent_id}/prompt",
            data=data
        )
    
    def stop_swarm(self, swarm_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Stop an agent swarm.
        
        Args:
            swarm_id: Swarm ID
            force: Force stop without cleanup
        
        Returns:
            Stop confirmation
        """
        data = {"force": force}
        return self.client.post(f"{self.base_path}/{swarm_id}/stop", data=data)
    
    def pause_swarm(self, swarm_id: str) -> Dict[str, Any]:
        """
        Pause an agent swarm.
        
        Args:
            swarm_id: Swarm ID
        
        Returns:
            Pause confirmation
        """
        return self.client.post(f"{self.base_path}/{swarm_id}/pause")
    
    def resume_swarm(self, swarm_id: str) -> Dict[str, Any]:
        """
        Resume a paused swarm.
        
        Args:
            swarm_id: Swarm ID
        
        Returns:
            Resume confirmation
        """
        return self.client.post(f"{self.base_path}/{swarm_id}/resume")
    
    def get_swarm_history(
        self,
        swarm_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get swarm execution history.
        
        Args:
            swarm_id: Swarm ID
            limit: Maximum number of history entries
        
        Returns:
            List of history entries
        """
        params = {"limit": limit}
        response = self.client.get(
            f"{self.base_path}/{swarm_id}/history",
            params=params
        )
        return response.get("history", [])
    
    def get_agent_communications(
        self,
        swarm_id: str,
        agent_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get agent communication logs.
        
        Args:
            swarm_id: Swarm ID
            agent_id: Optional specific agent ID
        
        Returns:
            List of communication entries
        """
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        
        response = self.client.get(
            f"{self.base_path}/{swarm_id}/communications",
            params=params
        )
        return response.get("communications", [])
    
    def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        capabilities: List[str],
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a custom agent template.

        Args:
            name: Agent name
            agent_type: Type of agent
            capabilities: List of capabilities
            prompt: Agent prompt
            config: Additional configuration

        Returns:
            Created agent details
        """
        data = {
            "name": name,
            "type": agent_type.value,
            "capabilities": capabilities,
            "prompt": prompt,
            "config": config or {},
        }

        return self.client.post(f"{self.base_path}/agents", data=data)

    def list_swarms(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List all swarms with optional filtering.

        Args:
            project_id: Filter by project ID
            status: Filter by status
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of swarms with pagination metadata
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if project_id:
            params["project_id"] = project_id
        if status:
            params["status"] = status

        return self.client.get(self.base_path, params=params)

    def delete_swarm(self, swarm_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete a swarm.

        Args:
            swarm_id: Swarm ID to delete
            force: Force deletion without cleanup

        Returns:
            Deletion confirmation
        """
        params = {"force": str(force).lower()}
        return self.client.delete(f"{self.base_path}/{swarm_id}", params=params)

    def scale_swarm(
        self,
        swarm_id: str,
        agent_counts: Dict[str, int],
    ) -> Dict[str, Any]:
        """
        Scale swarm by adjusting agent counts.

        Args:
            swarm_id: Swarm ID
            agent_counts: Dictionary mapping agent types to desired counts

        Returns:
            Scaling operation result
        """
        data = {"agent_counts": agent_counts}
        return self.client.post(f"{self.base_path}/{swarm_id}/scale", data=data)

    def get_analytics(
        self,
        swarm_id: str,
        metric_types: Optional[List[str]] = None,
        time_range: str = "7d",
    ) -> Dict[str, Any]:
        """
        Get swarm analytics and performance metrics.

        Args:
            swarm_id: Swarm ID
            metric_types: Specific metrics to retrieve
            time_range: Time range (1d, 7d, 30d, all)

        Returns:
            Analytics data
        """
        params = {"time_range": time_range}

        if metric_types:
            params["metric_types"] = ",".join(metric_types)

        return self.client.get(f"{self.base_path}/{swarm_id}/analytics", params=params)

    def execute_parallel_tasks(
        self,
        swarm_id: str,
        tasks: List[Dict[str, Any]],
        max_concurrency: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks in parallel across swarm.

        Args:
            swarm_id: Swarm ID
            tasks: List of task definitions
            max_concurrency: Maximum concurrent executions

        Returns:
            Parallel execution results
        """
        data = {
            "tasks": tasks,
        }

        if max_concurrency:
            data["max_concurrency"] = max_concurrency

        return self.client.post(
            f"{self.base_path}/{swarm_id}/tasks/parallel",
            data=data
        )

    def get_swarm_health(self, swarm_id: str) -> Dict[str, Any]:
        """
        Get swarm health status.

        Args:
            swarm_id: Swarm ID

        Returns:
            Health status details
        """
        return self.client.get(f"{self.base_path}/{swarm_id}/health")

    def update_swarm_config(
        self,
        swarm_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update swarm configuration.

        Args:
            swarm_id: Swarm ID
            config: New configuration settings

        Returns:
            Updated configuration
        """
        return self.client.put(f"{self.base_path}/{swarm_id}/config", data=config)

    def get_agent_status(
        self,
        swarm_id: str,
        agent_id: str,
    ) -> Dict[str, Any]:
        """
        Get detailed status of a specific agent in the swarm.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID

        Returns:
            Agent status details
        """
        return self.client.get(f"{self.base_path}/{swarm_id}/agents/{agent_id}/status")

    def broadcast_message(
        self,
        swarm_id: str,
        message: str,
        target_agents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Broadcast a message to all or specific agents in swarm.

        Args:
            swarm_id: Swarm ID
            message: Message to broadcast
            target_agents: Optional list of specific agent IDs

        Returns:
            Broadcast confirmation
        """
        data = {"message": message}

        if target_agents:
            data["target_agents"] = target_agents

        return self.client.post(f"{self.base_path}/{swarm_id}/broadcast", data=data)


__all__ = [
    "AgentSwarmClient",
    "AgentType",
    "SwarmStatus",
]