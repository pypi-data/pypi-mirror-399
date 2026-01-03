"""
Task Execution CLI Commands

Commands for task management (create, execute, status, list, sequence).
"""

import click
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

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


@click.group(name="task")
def task_group():
    """Manage agent tasks."""
    pass


@task_group.command(name="create")
@click.option("--agent-id", required=True, help="Agent instance ID")
@click.option("--type", "task_type", required=True, help="Task type")
@click.option("--description", required=True, help="Task description")
@click.option("--priority", default="medium", help="Task priority (low, medium, high, critical)")
@click.option("--context", help="Task context as JSON string")
def create_task(agent_id: str, task_type: str, description: str, priority: str, context: Optional[str]):
    """Create a new task."""
    try:
        client = get_client()

        context_data = {}
        if context:
            context_data = json.loads(context)

        result = client.agent_orchestration.create_task(
            agent_id=agent_id,
            task_type=task_type,
            description=description,
            context=context_data,
            priority=priority
        )

        console.print(Panel(
            f"[green]✓[/green] Task created: {result.get('task_id')}",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@task_group.command(name="execute")
@click.argument("task_id")
@click.option("--agent-id", help="Optional specific agent to use")
def execute_task(task_id: str, agent_id: Optional[str]):
    """Execute a task."""
    try:
        client = get_client()
        result = client.agent_orchestration.execute_task(task_id, agent_id=agent_id)

        console.print(Panel(
            f"[green]✓[/green] Task execution started",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@task_group.command(name="status")
@click.argument("task_id")
def get_status(task_id: str):
    """Get task status."""
    try:
        client = get_client()
        result = client.agent_orchestration.get_task_status(task_id)

        status = result.get("status", "unknown")
        status_color = {
            "pending": "yellow",
            "running": "blue",
            "completed": "green",
            "failed": "red"
        }.get(status, "white")

        console.print(Panel(
            f"Status: [{status_color}]{status}[/{status_color}]\n\n" +
            json.dumps(result, indent=2),
            title=f"Task {task_id}"
        ))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@task_group.command(name="list")
@click.option("--agent-id", help="Filter by agent ID")
@click.option("--status", help="Filter by status")
@click.option("--type", "task_type", help="Filter by task type")
@click.option("--format", type=click.Choice(["table", "json"]), default="table",
              help="Output format")
def list_tasks(agent_id: Optional[str], status: Optional[str], task_type: Optional[str], format: str):
    """List tasks."""
    try:
        client = get_client()
        result = client.agent_orchestration.list_tasks(
            agent_id=agent_id,
            status=status,
            task_type=task_type
        )

        tasks = result.get("tasks", [])

        if format == "json":
            click.echo(json.dumps(tasks, indent=2))
        else:
            table = Table(title="Tasks")
            table.add_column("ID", style="cyan")
            table.add_column("Type", style="bold")
            table.add_column("Status", style="green")
            table.add_column("Priority", justify="right")
            table.add_column("Agent", style="dim")

            for task in tasks:
                table.add_row(
                    task.get("id", "")[:12],
                    task.get("task_type", ""),
                    task.get("status", ""),
                    task.get("priority", ""),
                    task.get("agent_id", "")[:12]
                )

            console.print(table)
            console.print(f"\nTotal: {len(tasks)} tasks")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@task_group.command(name="sequence")
@click.option("--name", required=True, help="Sequence name")
@click.option("--tasks", required=True, help="Task IDs (comma-separated)")
@click.option("--mode", default="sequential", help="Execution mode (sequential, parallel, conditional)")
def create_sequence(name: str, tasks: str, mode: str):
    """Create a task sequence."""
    try:
        client = get_client()

        task_list = []
        for task_id in tasks.split(","):
            task_list.append({"task_id": task_id.strip()})

        result = client.agent_coordination.create_task_sequence(
            name=name,
            tasks=task_list,
            execution_mode=mode
        )

        console.print(Panel(
            f"[green]✓[/green] Sequence created: {result.get('sequence_id')}",
            title="Success"
        ))
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
