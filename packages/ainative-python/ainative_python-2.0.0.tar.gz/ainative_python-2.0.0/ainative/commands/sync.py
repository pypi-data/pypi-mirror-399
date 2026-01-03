"""
Sync CLI Commands

Commands for synchronizing local and cloud database environments.
"""

import click
import json
from typing import Optional
from rich.console import Console

from ..client import AINativeClient
from ..cli_utils.diff import DatabaseDiff
from ..cli_utils.formatters import DiffFormatter


console = Console()


def get_client(base_url: Optional[str] = None) -> AINativeClient:
    """Get authenticated client with optional base URL override."""
    import os
    from ..auth import AuthConfig

    api_key = os.getenv("AINATIVE_API_KEY")
    if not api_key:
        raise click.ClickException("AINATIVE_API_KEY environment variable not set")

    return AINativeClient(
        auth_config=AuthConfig(api_key=api_key),
        base_url=base_url,
        organization_id=os.getenv("AINATIVE_ORG_ID")
    )


@click.group(name="sync")
def sync_group():
    """Database synchronization commands."""
    pass


@sync_group.command(name="plan")
@click.option(
    "--local-url",
    default="http://localhost:8000",
    help="Local API URL (default: http://localhost:8000)"
)
@click.option(
    "--cloud-url",
    default="https://api.ainative.studio",
    help="Cloud API URL (default: https://api.ainative.studio)"
)
@click.option(
    "--schema",
    is_flag=True,
    help="Show schema diff only"
)
@click.option(
    "--data",
    is_flag=True,
    help="Show data diff only"
)
@click.option(
    "--vectors",
    is_flag=True,
    help="Show vectors diff only"
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output as JSON"
)
def sync_plan(
    local_url: str,
    cloud_url: str,
    schema: bool,
    data: bool,
    vectors: bool,
    json_output: bool
):
    """
    Show diff between local and cloud environments.

    Compares database schema, data, and vectors between local development
    environment and cloud production. Use flags to filter specific types.

    Examples:
        ainative sync plan
        ainative sync plan --schema
        ainative sync plan --data --vectors
        ainative sync plan --json
    """
    try:
        # If no specific flags set, show all
        show_all = not (schema or data or vectors)

        console.print("\n[bold cyan]🔍 Sync Plan (Local → Cloud)[/bold cyan]\n")

        # Fetch data from local and cloud
        console.print("[dim]Fetching local database state...[/dim]")
        local_client = get_client(local_url)

        console.print("[dim]Fetching cloud database state...[/dim]")
        cloud_client = get_client(cloud_url)

        # Compute diffs
        differ = DatabaseDiff(local_client, cloud_client)

        # Get schema diff
        schema_diff = None
        if show_all or schema:
            schema_diff = differ.compute_schema_diff()

        # Get data diff
        data_diff = None
        if show_all or data:
            data_diff = differ.compute_data_diff()

        # Get vectors diff
        vectors_diff = None
        if show_all or vectors:
            vectors_diff = differ.compute_vectors_diff()

        # Format and display output
        formatter = DiffFormatter()

        if json_output:
            # JSON output
            output = {
                "schema": schema_diff,
                "data": data_diff,
                "vectors": vectors_diff
            }
            click.echo(json.dumps(output, indent=2))
        else:
            # Rich formatted output
            if schema_diff:
                formatter.format_schema_diff(schema_diff)

            if data_diff:
                formatter.format_data_diff(data_diff)

            if vectors_diff:
                formatter.format_vectors_diff(vectors_diff)

            # Show summary
            console.print("\n[dim]Use `ainative sync apply` to execute.[/dim]")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        if "--verbose" in click.get_current_context().args:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()
