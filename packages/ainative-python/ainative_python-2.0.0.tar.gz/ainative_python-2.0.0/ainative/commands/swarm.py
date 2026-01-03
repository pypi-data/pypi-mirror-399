"""
Swarm Management CLI Commands

Commands for managing agent swarms (list, create, delete, scale, analytics).
"""

import click
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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


@click.group(name="swarm")
def swarm_group():
    """Manage agent swarms."""
    pass


@swarm_group.command(name="list")
@click.option("--project-id", help="Filter by project ID")
@click.option("--status", help="Filter by status")
@click.option("--format", type=click.Choice(["table", "json"]), default="table",
              help="Output format")
def list_swarms(project_id: Optional[str], status: Optional[str], format: str):
    """List all swarms."""
    try:
        client = get_client()
        result = client.agent_swarm.list_swarms(
            project_id=project_id,
            status=status
        )

        swarms = result.get("swarms", [])

        if format == "json":
            click.echo(json.dumps(swarms, indent=2))
        else:
            table = Table(title="Agent Swarms")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Status", style="green")
            table.add_column("Agents", justify="right")
            table.add_column("Project", style="dim")

            for swarm in swarms:
                table.add_row(
                    swarm.get("id", ""),
                    swarm.get("name", ""),
                    swarm.get("status", ""),
                    str(swarm.get("agent_count", 0)),
                    swarm.get("project_id", "")
                )

            console.print(table)
            console.print(f"\nTotal: {len(swarms)} swarms")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@swarm_group.command(name="create")
@click.argument("name")
@click.option("--project-id", required=True, help="Project ID")
@click.option("--objective", required=True, help="Swarm objective")
@click.option("--agents", help="Comma-separated agent types")
def create_swarm(name: str, project_id: str, objective: str, agents: Optional[str]):
    """Create a new swarm."""
    try:
        client = get_client()

        agent_list = []
        if agents:
            for agent_type in agents.split(","):
                agent_list.append({"type": agent_type.strip()})

        result = client.agent_swarm.start_swarm(
            project_id=project_id,
            agents=agent_list,
            objective=objective,
            config={"name": name}
        )

        console.print(Panel(
            f"[green]✓[/green] Swarm created: {result.get('swarm_id')}",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@swarm_group.command(name="delete")
@click.argument("swarm_id")
@click.option("--force", is_flag=True, help="Force deletion without cleanup")
def delete_swarm(swarm_id: str, force: bool):
    """Delete a swarm."""
    try:
        if not force:
            click.confirm(f"Delete swarm {swarm_id}?", abort=True)

        client = get_client()
        result = client.agent_swarm.delete_swarm(swarm_id, force=force)

        console.print(Panel(
            f"[green]✓[/green] Swarm deleted: {swarm_id}",
            title="Success"
        ))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@swarm_group.command(name="scale")
@click.argument("swarm_id")
@click.option("--agents", required=True, help="Agent counts (e.g., researcher=5,coder=3)")
def scale_swarm(swarm_id: str, agents: str):
    """Scale swarm agent counts."""
    try:
        agent_counts = {}
        for pair in agents.split(","):
            agent_type, count = pair.split("=")
            agent_counts[agent_type.strip()] = int(count)

        client = get_client()
        result = client.agent_swarm.scale_swarm(swarm_id, agent_counts)

        console.print(Panel(
            f"[green]✓[/green] Swarm scaled successfully",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@swarm_group.command(name="analytics")
@click.argument("swarm_id")
@click.option("--time-range", default="7d", help="Time range (1d, 7d, 30d, all)")
@click.option("--metrics", help="Comma-separated metric types")
def get_analytics(swarm_id: str, time_range: str, metrics: Optional[str]):
    """Get swarm analytics."""
    try:
        client = get_client()

        metric_list = metrics.split(",") if metrics else None
        result = client.agent_swarm.get_analytics(
            swarm_id,
            metric_types=metric_list,
            time_range=time_range
        )

        console.print(Panel(
            f"Analytics for swarm: {swarm_id}",
            title="Swarm Analytics"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
