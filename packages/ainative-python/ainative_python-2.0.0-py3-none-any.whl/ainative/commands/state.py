"""
Agent State CLI Commands

Commands for agent state management.
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


@click.group(name="state")
def state_group():
    """Agent state management."""
    pass


@state_group.command(name="get")
@click.option("--agent-id", required=True, help="Agent ID")
@click.option("--state-id", help="Specific state ID (optional)")
def get_state(agent_id: str, state_id: Optional[str]):
    """Get agent state."""
    try:
        client = get_client()
        result = client.agent_state.get_state(agent_id=agent_id, state_id=state_id)

        console.print(Panel(
            json.dumps(result, indent=2),
            title=f"Agent State - {agent_id}"
        ))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@state_group.command(name="checkpoint")
@click.option("--agent-id", required=True, help="Agent ID")
@click.option("--name", required=True, help="Checkpoint name")
@click.option("--data", required=True, help="State data (JSON string)")
@click.option("--description", help="Optional description")
def create_checkpoint(agent_id: str, name: str, data: str, description: Optional[str]):
    """Create a state checkpoint."""
    try:
        client = get_client()
        state_data = json.loads(data)

        result = client.agent_state.create_checkpoint(
            agent_id=agent_id,
            checkpoint_name=name,
            state_data=state_data,
            description=description
        )

        console.print(Panel(
            f"[green]✓[/green] Checkpoint created: {result.get('checkpoint_id')}",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@state_group.command(name="restore")
@click.argument("checkpoint_id")
def restore_checkpoint(checkpoint_id: str):
    """Restore from a checkpoint."""
    try:
        client = get_client()
        result = client.agent_state.restore_checkpoint(checkpoint_id)

        console.print(Panel(
            f"[green]✓[/green] State restored from checkpoint",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@state_group.command(name="list")
@click.option("--agent-id", required=True, help="Agent ID")
@click.option("--checkpoints", is_flag=True, help="List checkpoints instead of states")
@click.option("--format", type=click.Choice(["table", "json"]), default="table",
              help="Output format")
def list_states(agent_id: str, checkpoints: bool, format: str):
    """List agent states or checkpoints."""
    try:
        client = get_client()

        if checkpoints:
            result = client.agent_state.list_checkpoints(agent_id=agent_id)
            items = result.get("checkpoints", [])
            title = "Checkpoints"
        else:
            result = client.agent_state.list_states(agent_id=agent_id)
            items = result.get("states", [])
            title = "States"

        if format == "json":
            click.echo(json.dumps(items, indent=2))
        else:
            table = Table(title=title)
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Created", style="dim")

            for item in items:
                table.add_row(
                    item.get("id", "")[:12],
                    item.get("name", item.get("checkpoint_name", "")),
                    item.get("created_at", "")
                )

            console.print(table)
            console.print(f"\nTotal: {len(items)} {title.lower()}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
