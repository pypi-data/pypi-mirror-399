"""
Unit tests for agent operation SDK clients.

Tests for AgentOrchestrationClient, AgentCoordinationClient,
AgentLearningClient, and AgentStateClient.
"""

import pytest
from unittest.mock import Mock, patch
from ainative import AINativeClient
from ainative.agent_orchestration import AgentOrchestrationClient
from ainative.agent_coordination import AgentCoordinationClient
from ainative.agent_learning import AgentLearningClient
from ainative.agent_state import AgentStateClient


@pytest.fixture
def mock_client():
    """Create a mock AINative client."""
    client = Mock(spec=AINativeClient)
    client.get = Mock(return_value={"status": "success"})
    client.post = Mock(return_value={"status": "success"})
    client.put = Mock(return_value={"status": "success"})
    client.delete = Mock(return_value={"status": "success"})
    return client


class TestAgentOrchestrationClient:
    """Tests for AgentOrchestrationClient."""

    def test_init(self, mock_client):
        """Test client initialization."""
        client = AgentOrchestrationClient(mock_client)
        assert client.client == mock_client
        assert client.base_path == "/agent-orchestration"

    def test_create_agent_instance(self, mock_client):
        """Test creating an agent instance."""
        client = AgentOrchestrationClient(mock_client)

        result = client.create_agent_instance(
            name="TestAgent",
            agent_type="researcher",
            capabilities=["search", "analyze"],
            config={"model": "claude-3"}
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "/agent-orchestration/agents" in call_args[0][0]
        assert call_args[1]["data"]["name"] == "TestAgent"

    def test_list_agent_instances(self, mock_client):
        """Test listing agent instances."""
        client = AgentOrchestrationClient(mock_client)

        result = client.list_agent_instances(
            agent_type="researcher",
            status="active",
            limit=50
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "/agent-orchestration/agents" in call_args[0][0]
        assert call_args[1]["params"]["agent_type"] == "researcher"

    def test_get_agent_instance(self, mock_client):
        """Test getting a specific agent instance."""
        client = AgentOrchestrationClient(mock_client)

        result = client.get_agent_instance("agent-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()
        assert "agent-123" in mock_client.get.call_args[0][0]

    def test_create_task(self, mock_client):
        """Test creating a task."""
        client = AgentOrchestrationClient(mock_client)

        result = client.create_task(
            agent_id="agent-123",
            task_type="research",
            description="Research topic",
            context={"domain": "AI"},
            priority="high"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "/agent-orchestration/tasks" in call_args[0][0]
        assert call_args[1]["data"]["priority"] == "high"

    def test_execute_task(self, mock_client):
        """Test executing a task."""
        client = AgentOrchestrationClient(mock_client)

        result = client.execute_task("task-123", agent_id="agent-456")

        assert result["status"] == "success"
        mock_client.post.assert_called_once()
        assert "task-123" in mock_client.post.call_args[0][0]

    def test_get_task_status(self, mock_client):
        """Test getting task status."""
        client = AgentOrchestrationClient(mock_client)

        result = client.get_task_status("task-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()
        assert "task-123" in mock_client.get.call_args[0][0]

    def test_list_tasks(self, mock_client):
        """Test listing tasks."""
        client = AgentOrchestrationClient(mock_client)

        result = client.list_tasks(
            agent_id="agent-123",
            status="running",
            task_type="research"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["status"] == "running"


class TestAgentCoordinationClient:
    """Tests for AgentCoordinationClient."""

    def test_init(self, mock_client):
        """Test client initialization."""
        client = AgentCoordinationClient(mock_client)
        assert client.client == mock_client
        assert client.base_path == "/agent-coordination"

    def test_send_message(self, mock_client):
        """Test sending a message between agents."""
        client = AgentCoordinationClient(mock_client)

        result = client.send_message(
            from_agent_id="agent-1",
            to_agent_id="agent-2",
            message="Hello",
            message_type="request",
            metadata={"priority": "high"}
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "/agent-coordination/messages" in call_args[0][0]
        assert call_args[1]["data"]["message"] == "Hello"

    def test_get_messages(self, mock_client):
        """Test getting messages."""
        client = AgentCoordinationClient(mock_client)

        result = client.get_messages(
            agent_id="agent-123",
            direction="received"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_create_task_sequence(self, mock_client):
        """Test creating a task sequence."""
        client = AgentCoordinationClient(mock_client)

        tasks = [
            {"task_id": "task-1", "type": "research"},
            {"task_id": "task-2", "type": "analyze"}
        ]

        result = client.create_task_sequence(
            name="Research Flow",
            tasks=tasks,
            execution_mode="sequential"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["execution_mode"] == "sequential"

    def test_execute_sequence(self, mock_client):
        """Test executing a task sequence."""
        client = AgentCoordinationClient(mock_client)

        result = client.execute_sequence(
            sequence_id="seq-123",
            context={"data": "test"}
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_sequence_status(self, mock_client):
        """Test getting sequence status."""
        client = AgentCoordinationClient(mock_client)

        result = client.get_sequence_status("seq-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_list_sequences(self, mock_client):
        """Test listing sequences."""
        client = AgentCoordinationClient(mock_client)

        result = client.list_sequences(execution_mode="parallel")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_get_agent_workload(self, mock_client):
        """Test getting agent workload."""
        client = AgentCoordinationClient(mock_client)

        result = client.get_agent_workload(agent_id="agent-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_distribute_workload(self, mock_client):
        """Test distributing workload."""
        client = AgentCoordinationClient(mock_client)

        result = client.distribute_workload(
            tasks=["task-1", "task-2"],
            agents=["agent-1", "agent-2"],
            strategy="round_robin"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_sync_agents(self, mock_client):
        """Test synchronizing agents."""
        client = AgentCoordinationClient(mock_client)

        result = client.sync_agents(
            agent_ids=["agent-1", "agent-2"],
            checkpoint="checkpoint-1"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()


class TestAgentLearningClient:
    """Tests for AgentLearningClient."""

    def test_init(self, mock_client):
        """Test client initialization."""
        client = AgentLearningClient(mock_client)
        assert client.client == mock_client
        assert client.base_path == "/agent-learning"

    def test_record_interaction(self, mock_client):
        """Test recording an interaction."""
        client = AgentLearningClient(mock_client)

        result = client.record_interaction(
            agent_id="agent-123",
            interaction_type="query",
            input_data={"query": "test"},
            output_data={"response": "answer"}
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_interactions(self, mock_client):
        """Test getting interactions."""
        client = AgentLearningClient(mock_client)

        result = client.get_interactions(
            agent_id="agent-123",
            interaction_type="query"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_submit_feedback(self, mock_client):
        """Test submitting feedback."""
        client = AgentLearningClient(mock_client)

        result = client.submit_feedback(
            agent_id="agent-123",
            interaction_id="int-456",
            rating=5,
            feedback_type="quality",
            comments="Great response"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_feedback_summary(self, mock_client):
        """Test getting feedback summary."""
        client = AgentLearningClient(mock_client)

        result = client.get_feedback_summary(
            agent_id="agent-123",
            time_range="30d"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_get_performance_metrics(self, mock_client):
        """Test getting performance metrics."""
        client = AgentLearningClient(mock_client)

        result = client.get_performance_metrics(
            agent_id="agent-123",
            metric_types=["accuracy", "speed"],
            time_range="7d"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_compare_agents(self, mock_client):
        """Test comparing agents."""
        client = AgentLearningClient(mock_client)

        result = client.compare_agents(
            agent_ids=["agent-1", "agent-2"],
            metrics=["accuracy", "speed"],
            time_range="30d"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_learning_progress(self, mock_client):
        """Test getting learning progress."""
        client = AgentLearningClient(mock_client)

        result = client.get_learning_progress(agent_id="agent-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_export_learning_data(self, mock_client):
        """Test exporting learning data."""
        client = AgentLearningClient(mock_client)

        result = client.export_learning_data(
            agent_id="agent-123",
            format="json",
            include_raw_data=True
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()


class TestAgentStateClient:
    """Tests for AgentStateClient."""

    def test_init(self, mock_client):
        """Test client initialization."""
        client = AgentStateClient(mock_client)
        assert client.client == mock_client
        assert client.base_path == "/agent-state"

    def test_create_state(self, mock_client):
        """Test creating state."""
        client = AgentStateClient(mock_client)

        result = client.create_state(
            agent_id="agent-123",
            state_data={"key": "value"},
            state_type="checkpoint"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_state(self, mock_client):
        """Test getting state."""
        client = AgentStateClient(mock_client)

        result = client.get_state(agent_id="agent-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_get_state_by_id(self, mock_client):
        """Test getting state by ID."""
        client = AgentStateClient(mock_client)

        result = client.get_state(
            agent_id="agent-123",
            state_id="state-456"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()
        assert "state-456" in mock_client.get.call_args[0][0]

    def test_update_state(self, mock_client):
        """Test updating state."""
        client = AgentStateClient(mock_client)

        result = client.update_state(
            state_id="state-123",
            state_data={"updated": "data"}
        )

        assert result["status"] == "success"
        mock_client.put.assert_called_once()

    def test_delete_state(self, mock_client):
        """Test deleting state."""
        client = AgentStateClient(mock_client)

        result = client.delete_state(state_id="state-123")

        assert result["status"] == "success"
        mock_client.delete.assert_called_once()

    def test_list_states(self, mock_client):
        """Test listing states."""
        client = AgentStateClient(mock_client)

        result = client.list_states(
            agent_id="agent-123",
            state_type="checkpoint"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_create_checkpoint(self, mock_client):
        """Test creating a checkpoint."""
        client = AgentStateClient(mock_client)

        result = client.create_checkpoint(
            agent_id="agent-123",
            checkpoint_name="checkpoint-1",
            state_data={"key": "value"},
            description="Test checkpoint"
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_restore_checkpoint(self, mock_client):
        """Test restoring a checkpoint."""
        client = AgentStateClient(mock_client)

        result = client.restore_checkpoint(checkpoint_id="cp-123")

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_list_checkpoints(self, mock_client):
        """Test listing checkpoints."""
        client = AgentStateClient(mock_client)

        result = client.list_checkpoints(agent_id="agent-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_delete_checkpoint(self, mock_client):
        """Test deleting a checkpoint."""
        client = AgentStateClient(mock_client)

        result = client.delete_checkpoint(checkpoint_id="cp-123")

        assert result["status"] == "success"
        mock_client.delete.assert_called_once()


class TestAgentSwarmExpansion:
    """Tests for expanded AgentSwarmClient methods."""

    @pytest.fixture
    def swarm_client(self, mock_client):
        """Create swarm client."""
        from ainative.agent_swarm import AgentSwarmClient
        return AgentSwarmClient(mock_client)

    def test_list_swarms(self, swarm_client, mock_client):
        """Test listing swarms."""
        result = swarm_client.list_swarms(
            project_id="proj-123",
            status="running"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_delete_swarm(self, swarm_client, mock_client):
        """Test deleting swarm."""
        result = swarm_client.delete_swarm("swarm-123", force=True)

        assert result["status"] == "success"
        mock_client.delete.assert_called_once()

    def test_scale_swarm(self, swarm_client, mock_client):
        """Test scaling swarm."""
        result = swarm_client.scale_swarm(
            swarm_id="swarm-123",
            agent_counts={"researcher": 5, "coder": 3}
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_analytics(self, swarm_client, mock_client):
        """Test getting swarm analytics."""
        result = swarm_client.get_analytics(
            swarm_id="swarm-123",
            metric_types=["performance", "usage"],
            time_range="7d"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_execute_parallel_tasks(self, swarm_client, mock_client):
        """Test executing parallel tasks."""
        tasks = [
            {"task": "task-1"},
            {"task": "task-2"}
        ]

        result = swarm_client.execute_parallel_tasks(
            swarm_id="swarm-123",
            tasks=tasks,
            max_concurrency=5
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()

    def test_get_swarm_health(self, swarm_client, mock_client):
        """Test getting swarm health."""
        result = swarm_client.get_swarm_health("swarm-123")

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_update_swarm_config(self, swarm_client, mock_client):
        """Test updating swarm config."""
        result = swarm_client.update_swarm_config(
            swarm_id="swarm-123",
            config={"max_agents": 10}
        )

        assert result["status"] == "success"
        mock_client.put.assert_called_once()

    def test_get_agent_status(self, swarm_client, mock_client):
        """Test getting agent status."""
        result = swarm_client.get_agent_status(
            swarm_id="swarm-123",
            agent_id="agent-456"
        )

        assert result["status"] == "success"
        mock_client.get.assert_called_once()

    def test_broadcast_message(self, swarm_client, mock_client):
        """Test broadcasting message."""
        result = swarm_client.broadcast_message(
            swarm_id="swarm-123",
            message="Hello all",
            target_agents=["agent-1", "agent-2"]
        )

        assert result["status"] == "success"
        mock_client.post.assert_called_once()
