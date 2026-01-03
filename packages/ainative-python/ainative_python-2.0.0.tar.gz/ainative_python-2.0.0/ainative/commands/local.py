"""
ZeroDB Local Environment Management Commands

Commands for managing local Docker-based ZeroDB development environment.
"""

import os
import sys
import subprocess
import click
import json
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


console = Console()


# Service ports for health checks
SERVICE_PORTS = {
    "postgres": 5432,
    "qdrant": 6333,
    "minio": 9000,
    "redpanda": 9092,
    "embeddings": 8001,
    "zerodb-api": 8000,
    "dashboard": 3000,
}

# Service URLs for health checks
SERVICE_HEALTH_URLS = {
    "postgres": None,  # Use pg_isready
    "qdrant": "http://localhost:6333/healthz",
    "minio": "http://localhost:9000/minio/health/live",
    "redpanda": None,  # Use rpk command
    "embeddings": "http://localhost:8001/health",
    "zerodb-api": "http://localhost:8000/health",
    "dashboard": "http://localhost:3000",
}


def find_zerodb_local_path() -> Optional[Path]:
    """Auto-detect zerodb-local directory path."""
    # Check current directory
    cwd = Path.cwd()
    if (cwd / "docker-compose.yml").exists() and (cwd / ".env.local.example").exists():
        return cwd

    # Check parent directories
    for parent in cwd.parents:
        zerodb_local = parent / "zerodb-local"
        if zerodb_local.exists() and (zerodb_local / "docker-compose.yml").exists():
            return zerodb_local

    # Check common locations
    common_paths = [
        Path.home() / "core" / "zerodb-local",
        Path("/Users/aideveloper/core/zerodb-local"),
        Path("~/zerodb-local").expanduser(),
    ]

    for path in common_paths:
        if path.exists() and (path / "docker-compose.yml").exists():
            return path

    return None


def check_docker_running() -> bool:
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_port_listening(port: int) -> bool:
    """Check if a port is listening."""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            return result == 0
    except Exception:
        return False


def check_service_health(service: str, url: Optional[str]) -> str:
    """Check service health via HTTP endpoint."""
    if not url:
        # Check port only
        port = SERVICE_PORTS.get(service)
        if port and check_port_listening(port):
            return "healthy"
        return "down"

    try:
        import urllib.request
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                return "healthy"
            return "unhealthy"
    except Exception:
        return "down"


@click.group(name="local")
def local_group():
    """Manage local ZeroDB Docker environment."""
    pass


@local_group.command(name="init")
@click.option("--path", type=click.Path(), help="Path to zerodb-local directory")
@click.option("--force", is_flag=True, help="Overwrite existing .env.local file")
def init_environment(path: Optional[str], force: bool):
    """Initialize local Docker environment."""
    try:
        # Find zerodb-local path
        if path:
            zerodb_path = Path(path)
        else:
            zerodb_path = find_zerodb_local_path()

        if not zerodb_path or not zerodb_path.exists():
            console.print("[red]✗[/red] Could not find zerodb-local directory")
            console.print("\nSearched locations:")
            console.print("  • Current directory")
            console.print("  • Parent directories")
            console.print("  • ~/core/zerodb-local")
            console.print("\nUse --path to specify location manually")
            sys.exit(1)

        console.print(f"[cyan]Found zerodb-local at:[/cyan] {zerodb_path}")

        # Check Docker
        if not check_docker_running():
            console.print("[red]✗[/red] Docker is not running")
            console.print("Please start Docker Desktop and try again")
            sys.exit(1)

        console.print("[green]✓[/green] Docker is running")

        # Check docker-compose.yml
        compose_file = zerodb_path / "docker-compose.yml"
        if not compose_file.exists():
            console.print(f"[red]✗[/red] docker-compose.yml not found at {compose_file}")
            sys.exit(1)

        console.print("[green]✓[/green] docker-compose.yml found")

        # Create .env.local from example
        env_file = zerodb_path / ".env.local"
        example_file = zerodb_path / ".env.local.example"

        if env_file.exists() and not force:
            console.print(f"[yellow]![/yellow] .env.local already exists")
            console.print("Use --force to overwrite")
        else:
            if not example_file.exists():
                console.print(f"[red]✗[/red] .env.local.example not found")
                sys.exit(1)

            env_file.write_text(example_file.read_text())
            console.print(f"[green]✓[/green] Created .env.local from template")

        # Create data directories
        data_dir = zerodb_path / "data"
        data_dir.mkdir(exist_ok=True)

        for subdir in ["postgres", "qdrant", "minio", "redpanda", "embeddings"]:
            (data_dir / subdir).mkdir(exist_ok=True)

        console.print("[green]✓[/green] Created data directories")

        # Success message
        console.print()
        panel = Panel(
            "[green]Environment initialized successfully![/green]\n\n"
            "Next steps:\n"
            "  1. Review and update .env.local if needed\n"
            "  2. Run: ainative local up\n"
            "  3. Check status: ainative local status",
            title="Initialization Complete",
            border_style="green"
        )
        console.print(panel)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@local_group.command(name="up")
@click.option("--path", type=click.Path(), help="Path to zerodb-local directory")
@click.option("--detach/--no-detach", "-d/-D", default=True, help="Run in background")
@click.option("--build", is_flag=True, help="Build images before starting")
def start_services(path: Optional[str], detach: bool, build: bool):
    """Start local Docker services."""
    try:
        # Find zerodb-local path
        if path:
            zerodb_path = Path(path)
        else:
            zerodb_path = find_zerodb_local_path()

        if not zerodb_path:
            console.print("[red]✗[/red] Could not find zerodb-local directory")
            console.print("Run: ainative local init")
            sys.exit(1)

        # Check Docker
        if not check_docker_running():
            console.print("[red]✗[/red] Docker is not running")
            sys.exit(1)

        # Build command
        cmd = ["docker-compose"]

        if build:
            console.print("[cyan]Building images...[/cyan]")
            build_result = subprocess.run(
                ["docker-compose", "build"],
                cwd=zerodb_path,
                capture_output=True,
                text=True
            )
            if build_result.returncode != 0:
                console.print(f"[red]✗[/red] Build failed:\n{build_result.stderr}")
                sys.exit(1)
            console.print("[green]✓[/green] Build complete")

        # Start services
        console.print("[cyan]Starting services...[/cyan]")

        cmd.extend(["up"])
        if detach:
            cmd.append("-d")

        result = subprocess.run(
            cmd,
            cwd=zerodb_path,
            capture_output=detach,
            text=True
        )

        if result.returncode != 0:
            console.print(f"[red]✗[/red] Failed to start services")
            if result.stderr:
                console.print(result.stderr)
            sys.exit(1)

        if detach:
            console.print("[green]✓[/green] Services started in background")
            console.print()
            console.print("View logs: ainative local logs")
            console.print("Check status: ainative local status")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@local_group.command(name="down")
@click.option("--path", type=click.Path(), help="Path to zerodb-local directory")
@click.option("--volumes", is_flag=True, help="Remove volumes (deletes data)")
@click.confirmation_option(
    "--volumes",
    prompt="This will delete all data. Are you sure?"
)
def stop_services(path: Optional[str], volumes: bool):
    """Stop local Docker services."""
    try:
        # Find zerodb-local path
        if path:
            zerodb_path = Path(path)
        else:
            zerodb_path = find_zerodb_local_path()

        if not zerodb_path:
            console.print("[red]✗[/red] Could not find zerodb-local directory")
            sys.exit(1)

        # Stop services
        console.print("[cyan]Stopping services...[/cyan]")

        cmd = ["docker-compose", "down"]
        if volumes:
            cmd.append("-v")
            console.print("[yellow]![/yellow] Removing volumes (data will be deleted)")

        result = subprocess.run(
            cmd,
            cwd=zerodb_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            console.print(f"[red]✗[/red] Failed to stop services")
            console.print(result.stderr)
            sys.exit(1)

        console.print("[green]✓[/green] Services stopped")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@local_group.command(name="logs")
@click.argument("service", required=False)
@click.option("--path", type=click.Path(), help="Path to zerodb-local directory")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--tail", "-n", type=int, default=100, help="Number of lines to show")
def view_logs(service: Optional[str], path: Optional[str], follow: bool, tail: int):
    """View service logs."""
    try:
        # Find zerodb-local path
        if path:
            zerodb_path = Path(path)
        else:
            zerodb_path = find_zerodb_local_path()

        if not zerodb_path:
            console.print("[red]✗[/red] Could not find zerodb-local directory")
            sys.exit(1)

        # Build command
        cmd = ["docker-compose", "logs", f"--tail={tail}"]

        if follow:
            cmd.append("-f")

        if service:
            cmd.append(service)

        # Execute
        subprocess.run(cmd, cwd=zerodb_path)

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped following logs[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@local_group.command(name="status")
@click.option("--path", type=click.Path(), help="Path to zerodb-local directory")
@click.option("--json-output", "--json", is_flag=True, help="Output as JSON")
def show_status(path: Optional[str], json_output: bool):
    """Show service health status."""
    try:
        # Find zerodb-local path
        if path:
            zerodb_path = Path(path)
        else:
            zerodb_path = find_zerodb_local_path()

        if not zerodb_path:
            console.print("[red]✗[/red] Could not find zerodb-local directory")
            sys.exit(1)

        # Check Docker
        if not check_docker_running():
            console.print("[red]✗[/red] Docker is not running")
            sys.exit(1)

        # Get running containers
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            cwd=zerodb_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            console.print("[red]✗[/red] Failed to get service status")
            sys.exit(1)

        # Parse container status
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

        # Check health of each service
        status_data = []
        for service_name, port in SERVICE_PORTS.items():
            # Find container
            container = next((c for c in containers if service_name in c.get("Service", "")), None)

            if not container:
                status_data.append({
                    "service": service_name,
                    "status": "down",
                    "port": port,
                    "health": "down"
                })
                continue

            # Check health
            container_status = container.get("State", "unknown")
            health_url = SERVICE_HEALTH_URLS.get(service_name)
            health = check_service_health(service_name, health_url)

            status_data.append({
                "service": service_name,
                "status": container_status,
                "port": port,
                "health": health
            })

        # Output
        if json_output:
            click.echo(json.dumps(status_data, indent=2))
            return

        # Create table
        table = Table(title="ZeroDB Local Services", box=box.ROUNDED)
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Port", justify="right", style="dim")
        table.add_column("Health", style="bold")

        for item in status_data:
            # Status color
            status = item["status"]
            if status == "running":
                status_display = "[green]●[/green] Running"
            elif status == "down":
                status_display = "[red]●[/red] Down"
            else:
                status_display = f"[yellow]●[/yellow] {status}"

            # Health color
            health = item["health"]
            if health == "healthy":
                health_display = "[green]✓ Healthy[/green]"
            elif health == "unhealthy":
                health_display = "[yellow]! Unhealthy[/yellow]"
            else:
                health_display = "[red]✗ Down[/red]"

            table.add_row(
                item["service"],
                status_display,
                str(item["port"]),
                health_display
            )

        console.print(table)

        # Overall status
        all_healthy = all(item["health"] == "healthy" for item in status_data)
        if all_healthy:
            console.print("\n[green]✓ All services are healthy[/green]")
        else:
            console.print("\n[yellow]! Some services are not healthy[/yellow]")
            console.print("Run: ainative local logs [service] to investigate")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@local_group.command(name="reset")
@click.option("--path", type=click.Path(), help="Path to zerodb-local directory")
@click.confirmation_option(prompt="This will delete ALL local data. Are you sure?")
def reset_database(path: Optional[str]):
    """Reset local database (WARNING: deletes all data)."""
    try:
        # Find zerodb-local path
        if path:
            zerodb_path = Path(path)
        else:
            zerodb_path = find_zerodb_local_path()

        if not zerodb_path:
            console.print("[red]✗[/red] Could not find zerodb-local directory")
            sys.exit(1)

        console.print("[yellow]Resetting database...[/yellow]")

        # Stop services
        console.print("[cyan]1/3[/cyan] Stopping services...")
        subprocess.run(
            ["docker-compose", "down"],
            cwd=zerodb_path,
            capture_output=True
        )

        # Remove volumes
        console.print("[cyan]2/3[/cyan] Removing volumes...")
        subprocess.run(
            ["docker-compose", "down", "-v"],
            cwd=zerodb_path,
            capture_output=True
        )

        # Remove data directory
        data_dir = zerodb_path / "data"
        if data_dir.exists():
            import shutil
            shutil.rmtree(data_dir)
            data_dir.mkdir()
            console.print("[green]✓[/green] Data directory cleared")

        # Restart services
        console.print("[cyan]3/3[/cyan] Restarting services...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=zerodb_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            console.print(f"[red]✗[/red] Failed to restart services")
            console.print(result.stderr)
            sys.exit(1)

        console.print()
        console.print("[green]✓ Database reset complete[/green]")
        console.print("All data has been deleted and services restarted")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)
