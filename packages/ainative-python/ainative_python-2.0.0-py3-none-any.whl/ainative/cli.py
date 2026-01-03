"""
AINative SDK Command Line Interface

Provides a comprehensive CLI for interacting with AINative Studio APIs.
"""

import os
import sys
import json
import click
from typing import Optional, List, Dict, Any
import numpy as np
from datetime import datetime, timedelta

from . import AINativeClient, __version__
from .auth import AuthConfig
from .exceptions import AINativeException, APIError, AuthenticationError
from .zerodb.memory import MemoryPriority
from .agent_swarm import AgentType


# Global client instance
client: Optional[AINativeClient] = None


def get_client() -> AINativeClient:
    """Get or create global client instance."""
    global client
    if client is None:
        # Load configuration
        api_key = os.getenv("AINATIVE_API_KEY")
        api_secret = os.getenv("AINATIVE_API_SECRET")
        base_url = os.getenv("AINATIVE_BASE_URL")
        org_id = os.getenv("AINATIVE_ORG_ID")
        
        if not api_key:
            click.echo("Error: AINATIVE_API_KEY environment variable not set", err=True)
            click.echo("Run: export AINATIVE_API_KEY=your-api-key", err=True)
            sys.exit(1)
        
        auth_config = AuthConfig(
            api_key=api_key,
            api_secret=api_secret
        )
        
        client = AINativeClient(
            auth_config=auth_config,
            base_url=base_url,
            organization_id=org_id
        )
    
    return client


def handle_error(error: Exception):
    """Handle and display errors consistently."""
    if isinstance(error, AuthenticationError):
        click.echo(f"Authentication Error: {error.message}", err=True)
        click.echo("Check your API key and try again.", err=True)
    elif isinstance(error, APIError):
        click.echo(f"API Error ({error.status_code}): {error.message}", err=True)
        if error.response_body:
            try:
                body = json.loads(error.response_body)
                if body.get("detail"):
                    click.echo(f"Details: {body['detail']}", err=True)
            except json.JSONDecodeError:
                pass
    elif isinstance(error, AINativeException):
        click.echo(f"Error: {error.message}", err=True)
    else:
        click.echo(f"Unexpected error: {str(error)}", err=True)


def format_output(data: Any, format_type: str = "json") -> str:
    """Format output data for display."""
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    elif format_type == "table":
        # Simple table formatting for lists
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                rows = []
                for item in data:
                    row = [str(item.get(header, "")) for header in headers]
                    rows.append(row)
                
                # Simple table display
                result = "\t".join(headers) + "\n"
                for row in rows:
                    result += "\t".join(row) + "\n"
                return result
        return json.dumps(data, indent=2, default=str)
    else:
        return str(data)


# Main CLI group
@click.group()
@click.version_option(version=__version__, prog_name="ainative")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """AINative SDK Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# Configuration commands
@cli.group()
def config():
    """Configuration management commands"""
    pass


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set configuration value"""
    if key == "api_key":
        click.echo(f"Set AINATIVE_API_KEY environment variable to: {value}")
        click.echo("Run: export AINATIVE_API_KEY=" + value)
    elif key == "base_url":
        click.echo(f"Set AINATIVE_BASE_URL environment variable to: {value}")
        click.echo("Run: export AINATIVE_BASE_URL=" + value)
    else:
        click.echo(f"Unknown configuration key: {key}")


@config.command()
def show():
    """Show current configuration"""
    config_items = [
        ("API Key", os.getenv("AINATIVE_API_KEY", "Not set")),
        ("API Secret", "***" if os.getenv("AINATIVE_API_SECRET") else "Not set"),
        ("Base URL", os.getenv("AINATIVE_BASE_URL", "Default")),
        ("Organization ID", os.getenv("AINATIVE_ORG_ID", "Not set")),
    ]
    
    for key, value in config_items:
        click.echo(f"{key}: {value}")


# Project commands
@cli.group()
def projects():
    """ZeroDB project management commands"""
    pass


@projects.command()
@click.option("--limit", default=10, help="Maximum number of projects to return")
@click.option("--offset", default=0, help="Number of projects to skip")
@click.option("--status", help="Filter by project status")
@click.option("--format", "output_format", default="json", type=click.Choice(["json", "table"]))
def list(limit, offset, status, output_format):
    """List projects"""
    try:
        client = get_client()
        from .zerodb.projects import ProjectStatus
        
        status_filter = None
        if status:
            try:
                status_filter = ProjectStatus(status)
            except ValueError:
                click.echo(f"Invalid status: {status}", err=True)
                return
        
        result = client.zerodb.projects.list(
            limit=limit,
            offset=offset,
            status=status_filter
        )
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e)


@projects.command()
@click.argument("name")
@click.option("--description", help="Project description")
@click.option("--metadata", help="Project metadata as JSON string")
def create(name, description, metadata):
    """Create a new project"""
    try:
        client = get_client()
        
        metadata_dict = {}
        if metadata:
            metadata_dict = json.loads(metadata)
        
        result = client.zerodb.projects.create(
            name=name,
            description=description,
            metadata=metadata_dict
        )
        
        click.echo(f"Created project: {result['id']}")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@projects.command()
@click.argument("project_id")
def get(project_id):
    """Get project details"""
    try:
        client = get_client()
        result = client.zerodb.projects.get(project_id)
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@projects.command()
@click.argument("project_id")
@click.option("--reason", help="Reason for suspension")
def suspend(project_id, reason):
    """Suspend a project"""
    try:
        client = get_client()
        result = client.zerodb.projects.suspend(project_id, reason=reason)
        click.echo(f"Project {project_id} suspended")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@projects.command()
@click.argument("project_id")
def activate(project_id):
    """Activate a suspended project"""
    try:
        client = get_client()
        result = client.zerodb.projects.activate(project_id)
        click.echo(f"Project {project_id} activated")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@projects.command()
@click.argument("project_id")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete(project_id):
    """Delete a project"""
    try:
        client = get_client()
        result = client.zerodb.projects.delete(project_id)
        click.echo(f"Project {project_id} deleted")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


# Vector commands
@cli.group()
def vectors():
    """Vector operations commands"""
    pass


@vectors.command()
@click.argument("project_id")
@click.argument("query", nargs=-1)
@click.option("--top-k", default=5, help="Number of results to return")
@click.option("--namespace", default="default", help="Vector namespace")
@click.option("--include-metadata", is_flag=True, default=True, help="Include metadata in results")
def search(project_id, query, top_k, namespace, include_metadata):
    """Search vectors (requires vector as space-separated numbers)"""
    try:
        client = get_client()
        
        if not query:
            click.echo("Error: Query vector required", err=True)
            click.echo("Example: ainative vectors search proj_123 0.1 0.2 0.3", err=True)
            return
        
        # Convert query to vector
        try:
            query_vector = [float(x) for x in query]
        except ValueError:
            click.echo("Error: Query must be numeric values", err=True)
            return
        
        results = client.zerodb.vectors.search(
            project_id=project_id,
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=include_metadata
        )
        
        click.echo(f"Found {len(results)} results:")
        click.echo(format_output(results))
        
    except Exception as e:
        handle_error(e)


@vectors.command()
@click.argument("project_id")
@click.argument("vector_file", type=click.File("r"))
@click.option("--namespace", default="default", help="Vector namespace")
@click.option("--metadata-file", type=click.File("r"), help="JSON file containing metadata")
def upsert(project_id, vector_file, namespace, metadata_file):
    """Upsert vectors from JSON file"""
    try:
        client = get_client()
        
        # Load vectors
        vectors_data = json.load(vector_file)
        
        # Load metadata if provided
        metadata = None
        if metadata_file:
            metadata = json.load(metadata_file)
        
        result = client.zerodb.vectors.upsert(
            project_id=project_id,
            vectors=vectors_data,
            metadata=metadata,
            namespace=namespace
        )
        
        click.echo("Vectors upserted successfully")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@vectors.command()
@click.argument("project_id")
@click.option("--namespace", help="Vector namespace")
def stats(project_id, namespace):
    """Get vector index statistics"""
    try:
        client = get_client()
        result = client.zerodb.vectors.describe_index_stats(
            project_id=project_id,
            namespace=namespace
        )
        
        click.echo("Vector Index Statistics:")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


# Memory commands
@cli.group()
def memory():
    """Memory operations commands"""
    pass


@memory.command()
@click.argument("content")
@click.option("--title", help="Memory title")
@click.option("--tags", help="Comma-separated tags")
@click.option("--priority", type=click.Choice(["low", "medium", "high", "critical"]), default="medium")
@click.option("--project-id", help="Project ID")
def create(content, title, tags, priority, project_id):
    """Create a new memory entry"""
    try:
        client = get_client()
        
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        priority_enum = MemoryPriority(priority)
        
        result = client.zerodb.memory.create(
            content=content,
            title=title,
            tags=tag_list,
            priority=priority_enum,
            project_id=project_id
        )
        
        click.echo(f"Created memory: {result['id']}")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@memory.command()
@click.argument("query")
@click.option("--limit", default=5, help="Number of results to return")
@click.option("--project-id", help="Project ID filter")
@click.option("--semantic", is_flag=True, default=True, help="Use semantic search")
def search(query, limit, project_id, semantic):
    """Search memory entries"""
    try:
        client = get_client()
        
        results = client.zerodb.memory.search(
            query=query,
            limit=limit,
            project_id=project_id,
            semantic=semantic
        )
        
        click.echo(f"Found {len(results)} memories:")
        click.echo(format_output(results))
        
    except Exception as e:
        handle_error(e)


@memory.command()
@click.option("--limit", default=10, help="Number of memories to return")
@click.option("--project-id", help="Project ID filter")
@click.option("--tags", help="Comma-separated tags filter")
@click.option("--priority", type=click.Choice(["low", "medium", "high", "critical"]))
def list(limit, project_id, tags, priority):
    """List memory entries"""
    try:
        client = get_client()
        
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        priority_filter = None
        if priority:
            priority_filter = MemoryPriority(priority)
        
        result = client.zerodb.memory.list(
            limit=limit,
            project_id=project_id,
            tags=tag_list,
            priority=priority_filter
        )
        
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


# Agent Swarm commands
@cli.group()
def swarm():
    """Agent swarm operations commands"""
    pass


@swarm.command("agent-types")
def agent_types():
    """List available agent types"""
    try:
        client = get_client()
        result = client.agent_swarm.get_agent_types()
        
        click.echo("Available Agent Types:")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@swarm.command()
@click.argument("project_id")
@click.argument("objective")
@click.argument("agents_file", type=click.File("r"))
@click.option("--config-file", type=click.File("r"), help="JSON file with swarm configuration")
def start(project_id, objective, agents_file, config_file):
    """Start agent swarm with agents from JSON file"""
    try:
        client = get_client()
        
        # Load agents configuration
        agents = json.load(agents_file)
        
        # Load swarm configuration if provided
        config = {}
        if config_file:
            config = json.load(config_file)
        
        result = client.agent_swarm.start_swarm(
            project_id=project_id,
            agents=agents,
            objective=objective,
            config=config
        )
        
        click.echo(f"Started swarm: {result['id']}")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@swarm.command()
@click.argument("swarm_id")
def status(swarm_id):
    """Get swarm status"""
    try:
        client = get_client()
        result = client.agent_swarm.get_status(swarm_id)
        
        click.echo(f"Swarm Status: {result.get('status', 'unknown')}")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@swarm.command()
@click.argument("swarm_id")
@click.argument("task")
@click.option("--context", help="Task context as JSON string")
@click.option("--agents", help="Comma-separated list of specific agent IDs")
def orchestrate(swarm_id, task, context, agents):
    """Orchestrate a task within the swarm"""
    try:
        client = get_client()
        
        context_dict = {}
        if context:
            context_dict = json.loads(context)
        
        agent_list = None
        if agents:
            agent_list = [agent.strip() for agent in agents.split(",")]
        
        result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task=task,
            context=context_dict,
            agents=agent_list
        )
        
        click.echo(f"Task orchestrated: {result.get('task_id', 'unknown')}")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@swarm.command()
@click.argument("swarm_id")
@click.confirmation_option(prompt="Are you sure you want to stop this swarm?")
def stop(swarm_id):
    """Stop an agent swarm"""
    try:
        client = get_client()
        result = client.agent_swarm.stop_swarm(swarm_id)
        
        click.echo(f"Swarm {swarm_id} stopped")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


# Analytics commands
@cli.group()
def analytics():
    """Analytics and metrics commands"""
    pass


@analytics.command()
@click.option("--project-id", help="Project ID filter")
@click.option("--days", default=30, help="Number of days to analyze")
@click.option("--granularity", default="daily", type=click.Choice(["hourly", "daily", "weekly", "monthly"]))
def usage(project_id, days, granularity):
    """Get usage analytics"""
    try:
        client = get_client()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        result = client.zerodb.analytics.get_usage(
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity
        )
        
        click.echo(f"Usage Analytics ({days} days, {granularity}):")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@analytics.command()
@click.option("--project-id", help="Project ID filter")
def costs(project_id):
    """Get cost analysis"""
    try:
        client = get_client()
        result = client.zerodb.analytics.get_cost_analysis(project_id=project_id)
        
        click.echo("Cost Analysis:")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


@analytics.command()
@click.argument("metric", type=click.Choice(["vectors", "queries", "storage", "errors"]))
@click.option("--project-id", help="Project ID filter")
@click.option("--days", default=30, help="Number of days to analyze")
def trends(metric, project_id, days):
    """Get trend data for specific metrics"""
    try:
        client = get_client()
        result = client.zerodb.analytics.get_trends(
            metric=metric,
            project_id=project_id,
            period=days
        )
        
        click.echo(f"{metric.title()} Trends ({days} days):")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


# Health check command
@cli.command()
def health():
    """Check API health status"""
    try:
        client = get_client()
        result = client.health_check()
        
        click.echo("API Health Status:")
        click.echo(format_output(result))
        
    except Exception as e:
        handle_error(e)


# Register new command groups
try:
    from .commands import (
        agents_group,
        swarm_group,
        task_group,
        coordination_group,
        learning_group,
        state_group,
        local_group,
        inspect_group,
        sync_group
    )
    cli.add_command(agents_group)
    cli.add_command(swarm_group)
    cli.add_command(task_group)
    cli.add_command(coordination_group)
    cli.add_command(learning_group)
    cli.add_command(state_group)
    cli.add_command(local_group)
    cli.add_command(inspect_group)
    cli.add_command(sync_group)
except ImportError as e:
    # CLI command groups not available
    # This is OK for initial usage
    pass


def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()