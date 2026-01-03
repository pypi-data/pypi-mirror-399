"""
Agent Learning CLI Commands

Commands for agent learning and feedback.
"""

import click
import json
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..client import AINativeClient


console = Console()


def get_client() -> AINativeClient:
    """Get authenticated client."""
    import os
    from ..auth import AuthConfig

    api_key = os.getenv("AINATIVE_API_KEY")
    if not api_key:
        raise click.ClickException("AINATIVE_API_KEY environment variable not set")

    return AINativeClient(
        auth_config=AuthConfig(api_key=api_key),
        base_url=os.getenv("AINATIVE_BASE_URL"),
        organization_id=os.getenv("AINATIVE_ORG_ID")
    )


@click.group(name="learn")
def learning_group():
    """Agent learning and feedback."""
    pass


@learning_group.command(name="feedback")
@click.option("--agent-id", required=True, help="Agent ID")
@click.option("--interaction-id", required=True, help="Interaction ID")
@click.option("--rating", type=int, required=True, help="Rating (1-5)")
@click.option("--comments", help="Optional feedback comments")
def submit_feedback(agent_id: str, interaction_id: str, rating: int, comments: Optional[str]):
    """Submit feedback for an agent interaction."""
    try:
        if rating < 1 or rating > 5:
            raise click.ClickException("Rating must be between 1 and 5")

        client = get_client()
        result = client.agent_learning.submit_feedback(
            agent_id=agent_id,
            interaction_id=interaction_id,
            rating=rating,
            comments=comments
        )

        console.print(Panel(
            f"[green]✓[/green] Feedback submitted",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@learning_group.command(name="metrics")
@click.option("--agent-id", required=True, help="Agent ID")
@click.option("--time-range", default="7d", help="Time range (1d, 7d, 30d, 90d)")
@click.option("--metrics", help="Specific metrics (comma-separated)")
def get_metrics(agent_id: str, time_range: str, metrics: Optional[str]):
    """Get agent performance metrics."""
    try:
        client = get_client()
        metric_list = metrics.split(",") if metrics else None

        result = client.agent_learning.get_performance_metrics(
            agent_id=agent_id,
            metric_types=metric_list,
            time_range=time_range
        )

        console.print(Panel(
            json.dumps(result, indent=2),
            title=f"Performance Metrics - {agent_id}"
        ))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@learning_group.command(name="compare")
@click.option("--agents", required=True, help="Agent IDs to compare (comma-separated)")
@click.option("--metrics", required=True, help="Metrics to compare (comma-separated)")
@click.option("--time-range", default="7d", help="Time range")
def compare_agents(agents: str, metrics: str, time_range: str):
    """Compare multiple agents."""
    try:
        client = get_client()
        agent_list = [a.strip() for a in agents.split(",")]
        metric_list = [m.strip() for m in metrics.split(",")]

        result = client.agent_learning.compare_agents(
            agent_ids=agent_list,
            metrics=metric_list,
            time_range=time_range
        )

        console.print(Panel(
            json.dumps(result, indent=2),
            title="Agent Comparison"
        ))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
