"""
Agent Learning Module for AINative SDK

Provides interface for agent learning, feedback, and performance tracking.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from .client import AINativeClient


class AgentLearningClient:
    """Client for Agent Learning operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize Agent Learning client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/agent-learning"

    def record_interaction(
        self,
        agent_id: str,
        interaction_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record an agent interaction for learning.

        Args:
            agent_id: Agent ID
            interaction_type: Type of interaction
            input_data: Input data for the interaction
            output_data: Output/response data
            metadata: Additional metadata

        Returns:
            Recorded interaction details
        """
        data = {
            "agent_id": agent_id,
            "interaction_type": interaction_type,
            "input_data": input_data,
            "output_data": output_data,
            "metadata": metadata or {},
        }

        return self.client.post(f"{self.base_path}/interactions", data=data)

    def get_interactions(
        self,
        agent_id: str,
        interaction_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get agent interactions.

        Args:
            agent_id: Agent ID
            interaction_type: Filter by interaction type
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of interactions with pagination metadata
        """
        params = {
            "agent_id": agent_id,
            "limit": limit,
            "offset": offset,
        }

        if interaction_type:
            params["interaction_type"] = interaction_type

        return self.client.get(f"{self.base_path}/interactions", params=params)

    def submit_feedback(
        self,
        agent_id: str,
        interaction_id: str,
        rating: int,
        feedback_type: str = "quality",
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit feedback for an agent interaction.

        Args:
            agent_id: Agent ID
            interaction_id: Interaction ID
            rating: Feedback rating (1-5)
            feedback_type: Type of feedback (quality, accuracy, speed, helpfulness)
            comments: Optional feedback comments

        Returns:
            Feedback submission confirmation
        """
        data = {
            "agent_id": agent_id,
            "interaction_id": interaction_id,
            "rating": rating,
            "feedback_type": feedback_type,
        }

        if comments:
            data["comments"] = comments

        return self.client.post(f"{self.base_path}/feedback", data=data)

    def get_feedback_summary(
        self,
        agent_id: str,
        time_range: str = "7d",
    ) -> Dict[str, Any]:
        """
        Get feedback summary for an agent.

        Args:
            agent_id: Agent ID
            time_range: Time range (1d, 7d, 30d, 90d, all)

        Returns:
            Feedback summary statistics
        """
        params = {
            "agent_id": agent_id,
            "time_range": time_range,
        }

        return self.client.get(f"{self.base_path}/feedback/summary", params=params)

    def get_performance_metrics(
        self,
        agent_id: str,
        metric_types: Optional[List[str]] = None,
        time_range: str = "7d",
    ) -> Dict[str, Any]:
        """
        Get agent performance metrics.

        Args:
            agent_id: Agent ID
            metric_types: Specific metric types to retrieve
            time_range: Time range (1d, 7d, 30d, 90d, all)

        Returns:
            Performance metrics data
        """
        params = {
            "agent_id": agent_id,
            "time_range": time_range,
        }

        if metric_types:
            params["metric_types"] = ",".join(metric_types)

        return self.client.get(f"{self.base_path}/performance", params=params)

    def compare_agents(
        self,
        agent_ids: List[str],
        metrics: List[str],
        time_range: str = "7d",
    ) -> Dict[str, Any]:
        """
        Compare performance metrics across multiple agents.

        Args:
            agent_ids: List of agent IDs to compare
            metrics: List of metrics to compare
            time_range: Time range for comparison

        Returns:
            Comparative performance data
        """
        data = {
            "agent_ids": agent_ids,
            "metrics": metrics,
            "time_range": time_range,
        }

        return self.client.post(f"{self.base_path}/compare", data=data)

    def get_learning_progress(
        self,
        agent_id: str,
    ) -> Dict[str, Any]:
        """
        Get agent learning progress and improvement trends.

        Args:
            agent_id: Agent ID

        Returns:
            Learning progress data
        """
        return self.client.get(f"{self.base_path}/agents/{agent_id}/progress")

    def export_learning_data(
        self,
        agent_id: str,
        format: str = "json",
        include_raw_data: bool = False,
    ) -> Dict[str, Any]:
        """
        Export agent learning data.

        Args:
            agent_id: Agent ID
            format: Export format (json, csv, parquet)
            include_raw_data: Include raw interaction data

        Returns:
            Export data or download URL
        """
        params = {
            "format": format,
            "include_raw_data": str(include_raw_data).lower(),
        }

        return self.client.get(
            f"{self.base_path}/agents/{agent_id}/export",
            params=params
        )


__all__ = [
    "AgentLearningClient",
]
