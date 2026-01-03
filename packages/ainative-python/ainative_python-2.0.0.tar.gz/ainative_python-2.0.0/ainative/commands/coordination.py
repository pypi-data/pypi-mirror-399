"""
Agent Coordination CLI Commands

Commands for agent coordination (messages, workload, sync).
"""

import click
import json
from typing import Optional
from rich.console import Console
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


@click.group(name="coord")
def coordination_group():
    """Agent coordination operations."""
    pass


@coordination_group.command(name="message")
@click.option("--from", "from_agent", required=True, help="Sender agent ID")
@click.option("--to", "to_agent", required=True, help="Recipient agent ID")
@click.option("--message", required=True, help="Message content")
@click.option("--type", "msg_type", default="info", help="Message type")
def send_message(from_agent: str, to_agent: str, message: str, msg_type: str):
    """Send message between agents."""
    try:
        client = get_client()
        result = client.agent_coordination.send_message(
            from_agent_id=from_agent,
            to_agent_id=to_agent,
            message=message,
            message_type=msg_type
        )

        console.print(Panel(
            f"[green]✓[/green] Message sent",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@coordination_group.command(name="workload")
@click.option("--agent-id", help="Specific agent ID (optional)")
def get_workload(agent_id: Optional[str]):
    """Get agent workload statistics."""
    try:
        client = get_client()
        result = client.agent_coordination.get_agent_workload(agent_id=agent_id)

        console.print(Panel(
            json.dumps(result, indent=2),
            title="Agent Workload"
        ))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@coordination_group.command(name="distribute")
@click.option("--tasks", required=True, help="Task IDs (comma-separated)")
@click.option("--agents", required=True, help="Agent IDs (comma-separated)")
@click.option("--strategy", default="round_robin", help="Distribution strategy")
def distribute_workload(tasks: str, agents: str, strategy: str):
    """Distribute tasks across agents."""
    try:
        client = get_client()
        task_list = [t.strip() for t in tasks.split(",")]
        agent_list = [a.strip() for a in agents.split(",")]

        result = client.agent_coordination.distribute_workload(
            tasks=task_list,
            agents=agent_list,
            strategy=strategy
        )

        console.print(Panel(
            f"[green]✓[/green] Workload distributed",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
