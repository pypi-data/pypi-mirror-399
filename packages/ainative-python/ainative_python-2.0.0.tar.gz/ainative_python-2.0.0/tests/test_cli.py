"""
Comprehensive CLI Integration Tests for AINative Python SDK
Tests all CLI commands, error handling, and user interactions
"""

import pytest
import json
import os
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from ainative.cli import cli
from ainative.exceptions import APIError, AuthenticationError


@pytest.fixture
def runner():
    """Create Click test runner"""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Mock AINativeClient for testing"""
    with patch('ainative.cli.AINativeClient') as mock:
        yield mock


@pytest.fixture
def mock_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv('AINATIVE_API_KEY', 'test-api-key')
    monkeypatch.setenv('AINATIVE_BASE_URL', 'https://api.test.ainative.studio')


# ============================================================================
# Configuration Commands Tests
# ============================================================================

class TestConfigCommands:
    """Test configuration management commands"""

    def test_config_show_default(self, runner):
        """Test config show with default values"""
        result = runner.invoke(cli, ['config', 'show'])
        assert result.exit_code == 0
        assert 'API Key:' in result.output
        assert 'Base URL:' in result.output

    def test_config_show_with_env(self, runner, mock_env):
        """Test config show with environment variables"""
        result = runner.invoke(cli, ['config', 'show'])
        assert result.exit_code == 0
        assert 'test-api-key' in result.output

    def test_config_set_api_key(self, runner):
        """Test setting API key"""
        result = runner.invoke(cli, ['config', 'set', 'api_key', 'new-key'])
        assert result.exit_code == 0
        assert 'AINATIVE_API_KEY' in result.output

    def test_config_set_base_url(self, runner):
        """Test setting base URL"""
        result = runner.invoke(cli, ['config', 'set', 'base_url', 'https://custom.api.com'])
        assert result.exit_code == 0
        assert 'AINATIVE_BASE_URL' in result.output

    def test_config_set_unknown_key(self, runner):
        """Test setting unknown configuration key"""
        result = runner.invoke(cli, ['config', 'set', 'unknown_key', 'value'])
        assert result.exit_code == 0
        assert 'Unknown configuration key' in result.output


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthCommand:
    """Test health check command"""

    def test_health_check_success(self, runner, mock_client, mock_env):
        """Test successful health check"""
        mock_instance = mock_client.return_value
        mock_instance.health_check.return_value = {
            'status': 'healthy',
            'version': '1.0.0'
        }

        result = runner.invoke(cli, ['health'])
        assert result.exit_code == 0
        assert 'API Health Status:' in result.output
        mock_instance.health_check.assert_called_once()

    def test_health_check_with_verbose(self, runner, mock_client, mock_env):
        """Test health check with verbose flag"""
        mock_instance = mock_client.return_value
        mock_instance.health_check.return_value = {'status': 'healthy'}

        result = runner.invoke(cli, ['-v', 'health'])
        assert result.exit_code == 0

    def test_health_check_api_error(self, runner, mock_client, mock_env):
        """Test health check with API error"""
        mock_instance = mock_client.return_value
        mock_instance.health_check.side_effect = APIError(
            message="Service unavailable",
            status_code=503
        )

        result = runner.invoke(cli, ['health'])
        assert result.exit_code == 0  # CLI handles errors gracefully
        assert 'API Error' in result.output


# ============================================================================
# Project Commands Tests
# ============================================================================

class TestProjectCommands:
    """Test project management commands"""

    def test_projects_list_success(self, runner, mock_client, mock_env):
        """Test listing projects"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.list.return_value = {
            'projects': [
                {'id': 'proj_1', 'name': 'Project 1'},
                {'id': 'proj_2', 'name': 'Project 2'}
            ]
        }

        result = runner.invoke(cli, ['projects', 'list'])
        assert result.exit_code == 0
        mock_instance.zerodb.projects.list.assert_called_once()

    def test_projects_list_with_options(self, runner, mock_client, mock_env):
        """Test listing projects with limit and offset"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.list.return_value = {'projects': []}

        result = runner.invoke(cli, ['projects', 'list', '--limit', '5', '--offset', '10'])
        assert result.exit_code == 0
        mock_instance.zerodb.projects.list.assert_called_with(
            limit=5,
            offset=10,
            status=None
        )

    def test_projects_create_success(self, runner, mock_client, mock_env):
        """Test creating a project"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.create.return_value = {
            'id': 'proj_123',
            'name': 'Test Project'
        }

        result = runner.invoke(cli, ['projects', 'create', 'Test Project'])
        assert result.exit_code == 0
        assert 'proj_123' in result.output
        mock_instance.zerodb.projects.create.assert_called_once()

    def test_projects_create_with_description(self, runner, mock_client, mock_env):
        """Test creating project with description"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.create.return_value = {'id': 'proj_123'}

        result = runner.invoke(cli, [
            'projects', 'create', 'Test Project',
            '--description', 'Test description'
        ])
        assert result.exit_code == 0

    def test_projects_create_with_metadata(self, runner, mock_client, mock_env):
        """Test creating project with JSON metadata"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.create.return_value = {'id': 'proj_123'}

        metadata = json.dumps({'key': 'value'})
        result = runner.invoke(cli, [
            'projects', 'create', 'Test Project',
            '--metadata', metadata
        ])
        assert result.exit_code == 0

    def test_projects_get_success(self, runner, mock_client, mock_env):
        """Test getting project details"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.get.return_value = {
            'id': 'proj_123',
            'name': 'Test Project',
            'status': 'active'
        }

        result = runner.invoke(cli, ['projects', 'get', 'proj_123'])
        assert result.exit_code == 0
        assert 'proj_123' in result.output

    def test_projects_suspend_success(self, runner, mock_client, mock_env):
        """Test suspending a project"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.suspend.return_value = {
            'id': 'proj_123',
            'status': 'suspended'
        }

        result = runner.invoke(cli, ['projects', 'suspend', 'proj_123'])
        assert result.exit_code == 0
        assert 'suspended' in result.output

    def test_projects_activate_success(self, runner, mock_client, mock_env):
        """Test activating a project"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.activate.return_value = {
            'id': 'proj_123',
            'status': 'active'
        }

        result = runner.invoke(cli, ['projects', 'activate', 'proj_123'])
        assert result.exit_code == 0
        assert 'activated' in result.output

    def test_projects_delete_with_confirmation(self, runner, mock_client, mock_env):
        """Test deleting project with confirmation"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.delete.return_value = {'success': True}

        result = runner.invoke(cli, ['projects', 'delete', 'proj_123'], input='y\n')
        assert result.exit_code == 0


# ============================================================================
# Vector Commands Tests
# ============================================================================

class TestVectorCommands:
    """Test vector operations commands"""

    def test_vectors_search_success(self, runner, mock_client, mock_env):
        """Test vector search"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.vectors.search.return_value = [
            {'id': 'vec_1', 'score': 0.95},
            {'id': 'vec_2', 'score': 0.87}
        ]

        result = runner.invoke(cli, [
            'vectors', 'search', 'proj_123',
            '0.1', '0.2', '0.3'
        ])
        assert result.exit_code == 0
        assert 'Found 2 results' in result.output

    def test_vectors_search_with_options(self, runner, mock_client, mock_env):
        """Test vector search with top-k and namespace"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.vectors.search.return_value = []

        result = runner.invoke(cli, [
            'vectors', 'search', 'proj_123',
            '0.1', '0.2', '0.3',
            '--top-k', '10',
            '--namespace', 'custom'
        ])
        assert result.exit_code == 0

    def test_vectors_search_no_query(self, runner, mock_client, mock_env):
        """Test vector search without query vector"""
        result = runner.invoke(cli, ['vectors', 'search', 'proj_123'])
        assert 'Query vector required' in result.output

    def test_vectors_stats_success(self, runner, mock_client, mock_env):
        """Test getting vector statistics"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.vectors.describe_index_stats.return_value = {
            'total_vectors': 1000,
            'dimension': 1536
        }

        result = runner.invoke(cli, ['vectors', 'stats', 'proj_123'])
        assert result.exit_code == 0
        assert 'Vector Index Statistics:' in result.output


# ============================================================================
# Memory Commands Tests
# ============================================================================

class TestMemoryCommands:
    """Test memory operations commands"""

    def test_memory_create_success(self, runner, mock_client, mock_env):
        """Test creating memory entry"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.memory.create.return_value = {
            'id': 'mem_123',
            'content': 'Test memory'
        }

        result = runner.invoke(cli, ['memory', 'create', 'Test memory'])
        assert result.exit_code == 0
        assert 'mem_123' in result.output

    def test_memory_create_with_tags(self, runner, mock_client, mock_env):
        """Test creating memory with tags"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.memory.create.return_value = {'id': 'mem_123'}

        result = runner.invoke(cli, [
            'memory', 'create', 'Test memory',
            '--tags', 'tag1,tag2,tag3'
        ])
        assert result.exit_code == 0

    def test_memory_create_with_priority(self, runner, mock_client, mock_env):
        """Test creating memory with priority"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.memory.create.return_value = {'id': 'mem_123'}

        result = runner.invoke(cli, [
            'memory', 'create', 'Critical issue',
            '--priority', 'critical'
        ])
        assert result.exit_code == 0

    def test_memory_search_success(self, runner, mock_client, mock_env):
        """Test searching memories"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.memory.search.return_value = [
            {'id': 'mem_1', 'content': 'Memory 1'},
            {'id': 'mem_2', 'content': 'Memory 2'}
        ]

        result = runner.invoke(cli, ['memory', 'search', 'test query'])
        assert result.exit_code == 0
        assert 'Found 2 memories' in result.output

    def test_memory_list_success(self, runner, mock_client, mock_env):
        """Test listing memories"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.memory.list.return_value = {
            'memories': [
                {'id': 'mem_1', 'content': 'Memory 1'}
            ]
        }

        result = runner.invoke(cli, ['memory', 'list'])
        assert result.exit_code == 0


# ============================================================================
# Agent Swarm Commands Tests
# ============================================================================

class TestSwarmCommands:
    """Test agent swarm operations commands"""

    def test_swarm_agent_types_success(self, runner, mock_client, mock_env):
        """Test listing agent types"""
        mock_instance = mock_client.return_value
        mock_instance.agent_swarm.get_agent_types.return_value = {
            'types': ['analyst', 'generator', 'reviewer']
        }

        result = runner.invoke(cli, ['swarm', 'agent-types'])
        assert result.exit_code == 0
        assert 'Available Agent Types:' in result.output

    def test_swarm_status_success(self, runner, mock_client, mock_env):
        """Test getting swarm status"""
        mock_instance = mock_client.return_value
        mock_instance.agent_swarm.get_status.return_value = {
            'id': 'swarm_123',
            'status': 'running'
        }

        result = runner.invoke(cli, ['swarm', 'status', 'swarm_123'])
        assert result.exit_code == 0
        assert 'running' in result.output


# ============================================================================
# Analytics Commands Tests
# ============================================================================

class TestAnalyticsCommands:
    """Test analytics and metrics commands"""

    def test_analytics_usage_success(self, runner, mock_client, mock_env):
        """Test getting usage analytics"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.analytics.get_usage.return_value = {
            'total_requests': 1000,
            'total_storage': 1024000
        }

        result = runner.invoke(cli, ['analytics', 'usage', '--project-id', 'proj_123'])
        assert result.exit_code == 0
        assert 'Usage Analytics' in result.output

    def test_analytics_costs_success(self, runner, mock_client, mock_env):
        """Test getting cost analysis"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.analytics.get_cost_analysis.return_value = {
            'total_cost': 25.50
        }

        result = runner.invoke(cli, ['analytics', 'costs', '--project-id', 'proj_123'])
        assert result.exit_code == 0
        assert 'Cost Analysis:' in result.output


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test CLI error handling"""

    def test_missing_api_key(self, runner, monkeypatch):
        """Test error when API key is missing"""
        monkeypatch.delenv('AINATIVE_API_KEY', raising=False)

        result = runner.invoke(cli, ['health'])
        assert 'AINATIVE_API_KEY environment variable not set' in result.output

    def test_authentication_error(self, runner, mock_client, mock_env):
        """Test handling authentication errors"""
        mock_instance = mock_client.return_value
        mock_instance.health_check.side_effect = AuthenticationError("Invalid API key")

        result = runner.invoke(cli, ['health'])
        assert 'Authentication Error' in result.output

    def test_api_error_with_details(self, runner, mock_client, mock_env):
        """Test API error with response body"""
        mock_instance = mock_client.return_value
        error = APIError(
            message="Bad request",
            status_code=400,
            response_body='{"detail": "Invalid project ID"}'
        )
        mock_instance.zerodb.projects.get.side_effect = error

        result = runner.invoke(cli, ['projects', 'get', 'invalid_id'])
        assert 'API Error' in result.output

    def test_generic_exception(self, runner, mock_client, mock_env):
        """Test handling generic exceptions"""
        mock_instance = mock_client.return_value
        mock_instance.health_check.side_effect = Exception("Unexpected error")

        result = runner.invoke(cli, ['health'])
        assert 'Unexpected error' in result.output


# ============================================================================
# Output Formatting Tests
# ============================================================================

class TestOutputFormatting:
    """Test output formatting options"""

    def test_json_output_format(self, runner, mock_client, mock_env):
        """Test JSON output format"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.list.return_value = {
            'projects': [{'id': 'proj_1', 'name': 'Project 1'}]
        }

        result = runner.invoke(cli, ['projects', 'list', '--format', 'json'])
        assert result.exit_code == 0
        # Verify it's valid JSON
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_table_output_format(self, runner, mock_client, mock_env):
        """Test table output format"""
        mock_instance = mock_client.return_value
        mock_instance.zerodb.projects.list.return_value = {
            'projects': [{'id': 'proj_1', 'name': 'Project 1'}]
        }

        result = runner.invoke(cli, ['projects', 'list', '--format', 'table'])
        assert result.exit_code == 0


# ============================================================================
# Integration Tests (require live API)
# ============================================================================

@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests with live API (requires API key)"""

    def test_full_project_workflow(self, runner):
        """Test complete project workflow"""
        # This test requires AINATIVE_API_KEY environment variable
        if not os.getenv('AINATIVE_API_KEY'):
            pytest.skip("AINATIVE_API_KEY not set")

        # Create project
        result = runner.invoke(cli, [
            'projects', 'create', 'CLI Test Project',
            '--description', 'Created by CLI integration test'
        ])
        assert result.exit_code == 0

        # List projects
        result = runner.invoke(cli, ['projects', 'list'])
        assert result.exit_code == 0
        assert 'CLI Test Project' in result.output


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test CLI performance"""

    def test_cli_startup_time(self, runner):
        """Test CLI startup time is reasonable"""
        import time
        start = time.time()
        result = runner.invoke(cli, ['--version'])
        duration = time.time() - start

        assert result.exit_code == 0
        assert duration < 1.0  # Should start in under 1 second

    def test_help_command_speed(self, runner):
        """Test help command performance"""
        import time
        start = time.time()
        result = runner.invoke(cli, ['--help'])
        duration = time.time() - start

        assert result.exit_code == 0
        assert duration < 0.5  # Help should be instant


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=ainative.cli', '--cov-report=term-missing'])
