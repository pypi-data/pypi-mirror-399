"""
Agent Identity CLI Commands

Commands for managing agent identities (list, show, create, export, preview).
"""

import click
import json
import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..agent_identity_system import AgentRegistry, AgentIdentity, SeedPrompt


console = Console()


@click.group(name="agents")
def agents_group():
    """Manage agent identities and configurations."""
    pass


@agents_group.command(name="list")
@click.option("--format", type=click.Choice(["table", "json"]), default="table",
              help="Output format")
def list_agents(format: str):
    """List all available agent identities."""
    try:
        registry = AgentRegistry()
        agent_ids = registry.list_agents()

        if format == "json":
            output = []
            for agent_id in agent_ids:
                agent = registry.get_identity(agent_id)
                output.append({
                    "id": agent.id,
                    "name": agent.name,
                    "role": agent.role_title,
                    "emoji": agent.emoji,
                })
            click.echo(json.dumps(output, indent=2))
        else:
            table = Table(title="Agent Identities")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Role", style="dim")
            table.add_column("Emoji", justify="center")

            for agent_id in agent_ids:
                agent = registry.get_identity(agent_id)
                table.add_row(
                    agent.id,
                    agent.name,
                    agent.role_title,
                    agent.emoji
                )

            console.print(table)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@agents_group.command(name="show")
@click.argument("agent_id")
@click.option("--format", type=click.Choice(["panel", "json"]), default="panel",
              help="Output format")
def show_agent(agent_id: str, format: str):
    """Show detailed information about an agent."""
    try:
        registry = AgentRegistry()
        agent = registry.get_identity(agent_id)

        if not agent:
            click.echo(f"Error: Agent '{agent_id}' not found", err=True)
            return

        if format == "json":
            output = {
                "id": agent.id,
                "name": agent.name,
                "role_title": agent.role_title,
                "color": agent.color,
                "emoji": agent.emoji,
                "secondary_emoji": agent.secondary_emoji,
                "expertise": agent.expertise,
                "temperature": agent.temperature,
                "thinking_style": agent.thinking_style,
                "verbosity": agent.verbosity,
            }
            click.echo(json.dumps(output, indent=2))
        else:
            content = f"""
[bold]Role:[/bold] {agent.role_title}
[bold]Emoji:[/bold] {agent.emoji} {agent.secondary_emoji}
[bold]Color:[/bold] {agent.color}
[bold]Thinking Style:[/bold] {agent.thinking_style}
[bold]Temperature:[/bold] {agent.temperature}
[bold]Verbosity:[/bold] {agent.verbosity}

[bold]Expertise:[/bold]
{chr(10).join('  • ' + e for e in agent.expertise)}
            """
            panel = agent.create_panel(content.strip(), title=f"{agent.emoji} {agent.name}")
            console.print(panel)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@agents_group.command(name="create")
@click.option("--id", required=True, help="Agent identifier (lowercase, no spaces)")
@click.option("--name", required=True, help="Display name")
@click.option("--role", required=True, help="Role title")
@click.option("--color", required=True, help="Hex color code (e.g., #FF6B6B)")
@click.option("--emoji", required=True, help="Primary emoji")
@click.option("--expertise", multiple=True, help="Areas of expertise")
@click.option("--temperature", type=float, default=0.5, help="Model temperature")
@click.option("--output", type=click.Path(), help="Output file path (YAML)")
def create_agent(id: str, name: str, role: str, color: str, emoji: str,
                expertise: tuple, temperature: float, output: Optional[str]):
    """Create a new custom agent identity."""
    try:
        agent = AgentIdentity(
            id=id,
            name=name,
            role_title=role,
            color=color,
            emoji=emoji,
            expertise=list(expertise),
            temperature=temperature
        )

        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "role_title": agent.role_title,
            "color": agent.color,
            "emoji": agent.emoji,
            "secondary_emoji": agent.secondary_emoji,
            "expertise": agent.expertise,
            "temperature": agent.temperature,
            "thinking_style": agent.thinking_style,
            "verbosity": agent.verbosity,
        }

        if output:
            output_path = Path(output)
            output_path.write_text(yaml.dump(agent_data, default_flow_style=False))
            click.echo(f"Agent saved to: {output}")
        else:
            click.echo(yaml.dump(agent_data, default_flow_style=False))

        console.print(Panel(f"[green]✓[/green] Agent '{name}' created successfully!",
                           style=color))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@agents_group.command(name="export")
@click.argument("agent_id")
@click.option("--output", type=click.Path(), help="Output file path")
@click.option("--format", type=click.Choice(["yaml", "json"]), default="yaml",
              help="Export format")
def export_agent(agent_id: str, output: Optional[str], format: str):
    """Export an agent identity to file."""
    try:
        registry = AgentRegistry()
        agent = registry.get_identity(agent_id)

        if not agent:
            click.echo(f"Error: Agent '{agent_id}' not found", err=True)
            return

        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "role_title": agent.role_title,
            "color": agent.color,
            "emoji": agent.emoji,
            "secondary_emoji": agent.secondary_emoji,
            "expertise": agent.expertise,
            "temperature": agent.temperature,
            "thinking_style": agent.thinking_style,
            "verbosity": agent.verbosity,
        }

        if format == "json":
            content = json.dumps(agent_data, indent=2)
        else:
            content = yaml.dump(agent_data, default_flow_style=False)

        if output:
            Path(output).write_text(content)
            click.echo(f"Agent exported to: {output}")
        else:
            click.echo(content)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@agents_group.command(name="preview")
@click.argument("agent_id")
@click.option("--message", default="Sample output from this agent",
              help="Test message to display")
def preview_agent(agent_id: str, message: str):
    """Preview an agent's visual styling."""
    try:
        registry = AgentRegistry()
        agent = registry.get_identity(agent_id)

        if not agent:
            click.echo(f"Error: Agent '{agent_id}' not found", err=True)
            return

        # Show name
        console.print(agent.format_name())
        console.print()

        # Show panel with message
        panel = agent.create_panel(message)
        console.print(panel)
        console.print()

        # Show status
        console.print(agent.format_status("Working on task..."))
        console.print(agent.format_status("Task completed!"))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
