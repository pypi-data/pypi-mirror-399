"""
ZeroDB Local Environment Inspection Commands

Commands for examining local ZeroDB environment state and service health.
"""

import click
import json
import socket
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


# Service configuration
SERVICES = {
    "postgresql": {
        "name": "PostgreSQL",
        "host": "localhost",
        "port": 5432,
        "health_check": "tcp"
    },
    "qdrant": {
        "name": "Qdrant",
        "host": "localhost",
        "port": 6333,
        "health_check": "http",
        "health_url": "http://localhost:6333/collections"
    },
    "minio": {
        "name": "MinIO",
        "host": "localhost",
        "port": 9000,
        "health_check": "http",
        "health_url": "http://localhost:9000/minio/health/live"
    },
    "redpanda": {
        "name": "RedPanda",
        "host": "localhost",
        "port": 9092,
        "health_check": "tcp"
    },
    "api": {
        "name": "API Server",
        "host": "localhost",
        "port": 8000,
        "health_check": "http",
        "health_url": "http://localhost:8000/health"
    }
}


def check_tcp_port(host: str, port: int, timeout: float = 2.0) -> Tuple[bool, Optional[str]]:
    """Check if a TCP port is open and accepting connections."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            return True, None
        else:
            return False, f"Port {port} not accepting connections"
    except socket.gaierror:
        return False, f"Hostname {host} could not be resolved"
    except socket.timeout:
        return False, f"Connection to {host}:{port} timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_http_endpoint(url: str, timeout: float = 2.0) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """Check if an HTTP endpoint is responding."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code < 400:
            try:
                data = response.json() if response.text else None
                return True, None, data
            except json.JSONDecodeError:
                return True, None, None
        else:
            return False, f"HTTP {response.status_code}", None
    except requests.exceptions.ConnectionError:
        return False, "Connection refused", None
    except requests.exceptions.Timeout:
        return False, "Request timeout", None
    except Exception as e:
        return False, str(e), None


def check_service_health(service_id: str) -> Dict[str, Any]:
    """Check health status of a service."""
    service = SERVICES.get(service_id)
    if not service:
        return {
            "service": service_id,
            "status": "unknown",
            "error": "Service configuration not found"
        }

    result = {
        "service": service["name"],
        "host": service["host"],
        "port": service["port"],
        "status": "unknown",
        "error": None,
        "data": None
    }

    if service["health_check"] == "tcp":
        is_up, error = check_tcp_port(service["host"], service["port"])
        result["status"] = "up" if is_up else "down"
        result["error"] = error
    elif service["health_check"] == "http":
        is_up, error, data = check_http_endpoint(service["health_url"])
        result["status"] = "up" if is_up else "down"
        result["error"] = error
        result["data"] = data

    return result


def format_status_indicator(status: str) -> str:
    """Format status with colored indicator."""
    if status == "up":
        return "[green]✅ UP[/green]"
    elif status == "down":
        return "[red]❌ DOWN[/red]"
    elif status == "warning":
        return "[yellow]⚠️ WARNING[/yellow]"
    else:
        return "[dim]❓ UNKNOWN[/dim]"


@click.group(name="inspect")
def inspect_group():
    """Examine local ZeroDB environment state."""
    pass


@inspect_group.command(name="config")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def inspect_config(output_json: bool):
    """Show current ZeroDB Local configuration."""
    import os

    config = {
        "environment": {
            "AINATIVE_API_KEY": "***" if os.getenv("AINATIVE_API_KEY") else "Not set",
            "AINATIVE_API_SECRET": "***" if os.getenv("AINATIVE_API_SECRET") else "Not set",
            "AINATIVE_BASE_URL": os.getenv("AINATIVE_BASE_URL", "Default"),
            "AINATIVE_ORG_ID": os.getenv("AINATIVE_ORG_ID", "Not set")
        },
        "services": {
            "PostgreSQL": f"localhost:{SERVICES['postgresql']['port']}",
            "Qdrant": f"localhost:{SERVICES['qdrant']['port']}",
            "MinIO": f"localhost:{SERVICES['minio']['port']}",
            "RedPanda": f"localhost:{SERVICES['redpanda']['port']}",
            "API Server": f"localhost:{SERVICES['api']['port']}"
        },
        "paths": {
            "config_dir": os.path.expanduser("~/.ainative"),
            "data_dir": os.path.expanduser("~/.ainative/data"),
            "logs_dir": os.path.expanduser("~/.ainative/logs")
        }
    }

    if output_json:
        click.echo(json.dumps(config, indent=2))
    else:
        console.print(Panel("[bold cyan]🔍 ZeroDB Local Configuration[/bold cyan]"))
        console.print()

        # Environment
        console.print("[bold]Environment Variables:[/bold]")
        for key, value in config["environment"].items():
            console.print(f"  • {key}: {value}")
        console.print()

        # Services
        console.print("[bold]Service Endpoints:[/bold]")
        for service, endpoint in config["services"].items():
            console.print(f"  • {service}: {endpoint}")
        console.print()

        # Paths
        console.print("[bold]File Paths:[/bold]")
        for path_name, path_value in config["paths"].items():
            console.print(f"  • {path_name}: {path_value}")


@inspect_group.command(name="services")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def inspect_services(output_json: bool):
    """Show all service health status."""
    results = {}

    for service_id in SERVICES.keys():
        health = check_service_health(service_id)
        results[service_id] = health

    if output_json:
        click.echo(json.dumps(results, indent=2))
    else:
        console.print()
        console.print(Panel("[bold cyan]🔍 ZeroDB Local Services[/bold cyan]"))
        console.print()

        table = Table(show_header=True, header_style="bold")
        table.add_column("Service", style="cyan", width=15)
        table.add_column("Status", width=15)
        table.add_column("Endpoint", style="dim", width=20)
        table.add_column("Details", width=30)

        for service_id, health in results.items():
            status_display = format_status_indicator(health["status"])
            endpoint = f"{health['host']}:{health['port']}"
            details = health.get("error", "Healthy") or "Healthy"

            table.add_row(
                health["service"],
                status_display,
                endpoint,
                details
            )

        console.print(table)
        console.print()


@inspect_group.command(name="db")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def inspect_db(output_json: bool):
    """Show PostgreSQL database statistics."""
    # Check PostgreSQL health first
    health = check_service_health("postgresql")

    if health["status"] != "up":
        if output_json:
            click.echo(json.dumps({"error": "PostgreSQL is not running", "status": "down"}, indent=2))
        else:
            console.print(f"[red]❌ PostgreSQL is not running[/red]")
            console.print(f"Details: {health.get('error', 'Unknown error')}")
        return

    # Try to get database stats via API
    try:
        api_health = check_service_health("api")
        if api_health["status"] == "up":
            # Try to get stats from API
            response = requests.get("http://localhost:8000/v1/admin/db/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()

                if output_json:
                    click.echo(json.dumps(stats, indent=2))
                else:
                    console.print()
                    console.print(Panel("[bold cyan]🗄️ PostgreSQL Database Statistics[/bold cyan]"))
                    console.print()

                    table = Table(show_header=True, header_style="bold")
                    table.add_column("Metric", style="cyan", width=25)
                    table.add_column("Value", width=30)

                    for key, value in stats.items():
                        table.add_row(key.replace("_", " ").title(), str(value))

                    console.print(table)
                    console.print()
                return
    except Exception as e:
        pass

    # Fallback: Show basic connection info
    db_info = {
        "status": "up",
        "host": health["host"],
        "port": health["port"],
        "connection": "Accepting connections",
        "note": "Start API server for detailed statistics"
    }

    if output_json:
        click.echo(json.dumps(db_info, indent=2))
    else:
        console.print()
        console.print(Panel("[bold cyan]🗄️ PostgreSQL Database[/bold cyan]"))
        console.print()
        console.print(f"[green]✅[/green] Status: Running")
        console.print(f"Endpoint: {db_info['host']}:{db_info['port']}")
        console.print(f"Connection: {db_info['connection']}")
        console.print()
        console.print(f"[dim]💡 {db_info['note']}[/dim]")
        console.print()


@inspect_group.command(name="vectors")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def inspect_vectors(output_json: bool):
    """Show vector index statistics from Qdrant."""
    # Check Qdrant health
    health = check_service_health("qdrant")

    if health["status"] != "up":
        if output_json:
            click.echo(json.dumps({"error": "Qdrant is not running", "status": "down"}, indent=2))
        else:
            console.print(f"[red]❌ Qdrant is not running[/red]")
            console.print(f"Details: {health.get('error', 'Unknown error')}")
        return

    # Try to get collection stats
    try:
        response = requests.get("http://localhost:6333/collections", timeout=5)
        if response.status_code == 200:
            data = response.json()
            collections = data.get("result", {}).get("collections", [])

            stats = {
                "status": "up",
                "total_collections": len(collections),
                "collections": []
            }

            # Get details for each collection
            for collection_info in collections:
                collection_name = collection_info.get("name")
                try:
                    coll_response = requests.get(f"http://localhost:6333/collections/{collection_name}", timeout=5)
                    if coll_response.status_code == 200:
                        coll_data = coll_response.json().get("result", {})
                        stats["collections"].append({
                            "name": collection_name,
                            "vectors_count": coll_data.get("vectors_count", 0),
                            "points_count": coll_data.get("points_count", 0),
                            "indexed_vectors_count": coll_data.get("indexed_vectors_count", 0)
                        })
                except:
                    pass

            if output_json:
                click.echo(json.dumps(stats, indent=2))
            else:
                console.print()
                console.print(Panel("[bold cyan]🔍 Qdrant Vector Index Statistics[/bold cyan]"))
                console.print()
                console.print(f"[green]✅[/green] Status: Running")
                console.print(f"Total Collections: {stats['total_collections']}")
                console.print()

                if stats["collections"]:
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("Collection", style="cyan")
                    table.add_column("Vectors", justify="right")
                    table.add_column("Points", justify="right")
                    table.add_column("Indexed", justify="right")

                    for coll in stats["collections"]:
                        table.add_row(
                            coll["name"],
                            str(coll["vectors_count"]),
                            str(coll["points_count"]),
                            str(coll["indexed_vectors_count"])
                        )

                    console.print(table)
                else:
                    console.print("[dim]No collections found[/dim]")
                console.print()
            return
    except Exception as e:
        pass

    # Fallback
    vector_info = {
        "status": "up",
        "host": health["host"],
        "port": health["port"],
        "note": "Could not retrieve collection statistics"
    }

    if output_json:
        click.echo(json.dumps(vector_info, indent=2))
    else:
        console.print()
        console.print(Panel("[bold cyan]🔍 Qdrant Vector Index[/bold cyan]"))
        console.print()
        console.print(f"[green]✅[/green] Status: Running")
        console.print(f"Endpoint: {vector_info['host']}:{vector_info['port']}")
        console.print()
        console.print(f"[yellow]⚠️[/yellow] {vector_info['note']}")
        console.print()


@inspect_group.command(name="sync")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def inspect_sync(output_json: bool):
    """Show sync status and last sync time."""
    import os
    from pathlib import Path

    # Check for sync state file
    sync_state_path = Path.home() / ".ainative" / "sync_state.json"

    if sync_state_path.exists():
        try:
            with open(sync_state_path, 'r') as f:
                sync_state = json.load(f)

            last_sync = sync_state.get("last_sync")
            if last_sync:
                last_sync_dt = datetime.fromisoformat(last_sync)
                time_since = datetime.now() - last_sync_dt

                if time_since < timedelta(minutes=5):
                    status = "synced"
                    status_text = "Recently synced"
                elif time_since < timedelta(hours=1):
                    status = "warning"
                    status_text = "Sync recommended"
                else:
                    status = "outdated"
                    status_text = "Sync needed"
            else:
                status = "never"
                status_text = "Never synced"
                last_sync_dt = None
        except Exception as e:
            status = "error"
            status_text = f"Error reading sync state: {str(e)}"
            last_sync_dt = None
            sync_state = {}
    else:
        status = "never"
        status_text = "Never synced"
        last_sync_dt = None
        sync_state = {}

    result = {
        "status": status,
        "status_text": status_text,
        "last_sync": str(last_sync_dt) if last_sync_dt else None,
        "sync_state_file": str(sync_state_path),
        "file_exists": sync_state_path.exists(),
        "details": sync_state
    }

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print()
        console.print(Panel("[bold cyan]🔄 Sync Status[/bold cyan]"))
        console.print()

        if status == "synced":
            console.print(f"[green]✅ {status_text}[/green]")
        elif status == "warning":
            console.print(f"[yellow]⚠️ {status_text}[/yellow]")
        elif status in ["outdated", "never"]:
            console.print(f"[red]❌ {status_text}[/red]")
        else:
            console.print(f"[dim]❓ {status_text}[/dim]")

        if last_sync_dt:
            console.print(f"Last Sync: {last_sync_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            console.print(f"Time Since: {str(time_since).split('.')[0]}")

        console.print(f"State File: {sync_state_path}")
        console.print(f"File Exists: {'Yes' if result['file_exists'] else 'No'}")
        console.print()

        if status != "synced":
            console.print("[dim]💡 Run 'ainative sync' to synchronize local and remote state[/dim]")
        console.print()
