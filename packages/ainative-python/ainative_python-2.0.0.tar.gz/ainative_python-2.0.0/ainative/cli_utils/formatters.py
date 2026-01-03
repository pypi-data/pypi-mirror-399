"""
Diff Formatters

Rich console formatters for displaying database diffs with colors.
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


console = Console()


class DiffFormatter:
    """Format database diffs for rich console output."""

    def __init__(self):
        """Initialize formatter."""
        self.console = console

    def format_schema_diff(self, schema_diff: Dict[str, Any]):
        """
        Format and display schema differences.

        Args:
            schema_diff: Schema diff dictionary from DatabaseDiff
        """
        if schema_diff.get("error"):
            self.console.print(f"[red]Schema Error:[/red] {schema_diff['error']}")
            return

        tables_to_create = schema_diff.get("tables_to_create", [])
        tables_to_drop = schema_diff.get("tables_to_drop", [])
        tables_to_alter = schema_diff.get("tables_to_alter", [])

        if not (tables_to_create or tables_to_drop or tables_to_alter):
            self.console.print("[dim]Schema: No changes[/dim]")
            return

        # Header
        self.console.print("\n[bold]Schema:[/bold]")

        # Tables to create
        if tables_to_create:
            for table in tables_to_create:
                fields = table.get("schema", {}).get("fields", {})
                field_str = ", ".join(
                    f"{name}: {ftype}" for name, ftype in fields.items()
                )
                self.console.print(
                    f" [green]+[/green] Create table: [bold]{table['table_name']}[/bold] "
                    f"({field_str})"
                )

        # Tables to alter
        if tables_to_alter:
            for table in tables_to_alter:
                table_name = table["table_name"]
                added = table.get("added_fields", [])
                removed = table.get("removed_fields", [])
                type_changes = table.get("type_changes", [])

                changes = []
                if added:
                    changes.append(f"add columns: {', '.join(added)}")
                if removed:
                    changes.append(f"remove columns: {', '.join(removed)}")
                if type_changes:
                    type_str = ", ".join(
                        f"{tc['field']} ({tc['old_type']} → {tc['new_type']})"
                        for tc in type_changes
                    )
                    changes.append(f"change types: {type_str}")

                change_desc = "; ".join(changes)
                self.console.print(
                    f" [yellow]~[/yellow] Alter table: [bold]{table_name}[/bold] "
                    f"({change_desc})"
                )

        # Tables to drop
        if tables_to_drop:
            for table in tables_to_drop:
                self.console.print(
                    f" [red]-[/red] Drop table: [bold]{table['table_name']}[/bold]"
                )

    def format_data_diff(self, data_diff: Dict[str, Any]):
        """
        Format and display data differences.

        Args:
            data_diff: Data diff dictionary from DatabaseDiff
        """
        if data_diff.get("error"):
            self.console.print(f"[red]Data Error:[/red] {data_diff['error']}")
            return

        total_new = data_diff.get("total_new_rows", 0)
        total_updated = data_diff.get("total_updated_rows", 0)
        total_deleted = data_diff.get("total_deleted_rows", 0)
        table_details = data_diff.get("table_details", [])

        if total_new == 0 and total_updated == 0 and total_deleted == 0:
            self.console.print("[dim]Data: No changes[/dim]")
            return

        # Header
        self.console.print("\n[bold]Data:[/bold]")

        # Summary
        if total_new > 0:
            self.console.print(f" [green]+[/green] {total_new} new rows")
        if total_updated > 0:
            self.console.print(f" [yellow]~[/yellow] {total_updated} updated rows")
        if total_deleted > 0:
            self.console.print(f" [red]-[/red] {total_deleted} deleted rows")

        # Table-level details (if there are multiple tables)
        if len(table_details) > 1:
            self.console.print("\n[dim]  By table:[/dim]")
            for detail in table_details:
                parts = []
                if detail["new_rows"] > 0:
                    parts.append(f"[green]+{detail['new_rows']}[/green]")
                if detail["updated_rows"] > 0:
                    parts.append(f"[yellow]~{detail['updated_rows']}[/yellow]")
                if detail["deleted_rows"] > 0:
                    parts.append(f"[red]-{detail['deleted_rows']}[/red]")

                changes = " ".join(parts)
                self.console.print(
                    f"    {detail['table_name']}: {changes} "
                    f"[dim](local: {detail['local_count']}, "
                    f"cloud: {detail['cloud_count']})[/dim]"
                )

    def format_vectors_diff(self, vectors_diff: Dict[str, Any]):
        """
        Format and display vector differences.

        Args:
            vectors_diff: Vectors diff dictionary from DatabaseDiff
        """
        if vectors_diff.get("error"):
            self.console.print(f"[red]Vectors Error:[/red] {vectors_diff['error']}")
            return

        total_upserts = vectors_diff.get("total_upserts", 0)
        total_deletes = vectors_diff.get("total_deletes", 0)
        namespace_details = vectors_diff.get("namespace_details", [])

        if total_upserts == 0 and total_deletes == 0:
            self.console.print("[dim]Vectors: No changes[/dim]")
            return

        # Header
        self.console.print("\n[bold]Vectors:[/bold]")

        # Summary
        if total_upserts > 0:
            self.console.print(f" [green]+[/green] Upsert {total_upserts} embeddings")
        if total_deletes > 0:
            self.console.print(f" [red]-[/red] Delete {total_deletes} stale vectors")

        # Namespace details (if multiple namespaces)
        if len(namespace_details) > 1:
            self.console.print("\n[dim]  By namespace:[/dim]")
            for detail in namespace_details:
                parts = []
                if detail["upserts"] > 0:
                    parts.append(f"[green]+{detail['upserts']}[/green]")
                if detail["deletes"] > 0:
                    parts.append(f"[red]-{detail['deletes']}[/red]")

                changes = " ".join(parts)
                self.console.print(
                    f"    {detail['namespace']}: {changes} "
                    f"[dim](local: {detail['local_count']}, "
                    f"cloud: {detail['cloud_count']})[/dim]"
                )

    def format_summary_table(
        self,
        schema_diff: Dict[str, Any],
        data_diff: Dict[str, Any],
        vectors_diff: Dict[str, Any]
    ):
        """
        Format an overall summary table.

        Args:
            schema_diff: Schema diff dictionary
            data_diff: Data diff dictionary
            vectors_diff: Vectors diff dictionary
        """
        table = Table(title="Sync Plan Summary", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Changes", justify="right")

        # Schema
        schema_changes = (
            len(schema_diff.get("tables_to_create", [])) +
            len(schema_diff.get("tables_to_alter", [])) +
            len(schema_diff.get("tables_to_drop", []))
        )
        table.add_row("Schema", str(schema_changes))

        # Data
        data_changes = (
            data_diff.get("total_new_rows", 0) +
            data_diff.get("total_updated_rows", 0) +
            data_diff.get("total_deleted_rows", 0)
        )
        table.add_row("Data Rows", str(data_changes))

        # Vectors
        vector_changes = (
            vectors_diff.get("total_upserts", 0) +
            vectors_diff.get("total_deletes", 0)
        )
        table.add_row("Vectors", str(vector_changes))

        self.console.print(table)
