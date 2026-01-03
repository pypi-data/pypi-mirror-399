"""
Database Diff Logic

Computes differences between local and cloud database states including
schema, data, and vectors.
"""

from typing import Dict, Any, List, Optional, Set
from difflib import unified_diff
import json

from ..client import AINativeClient


class DatabaseDiff:
    """Compute differences between local and cloud databases."""

    def __init__(self, local_client: AINativeClient, cloud_client: AINativeClient):
        """
        Initialize database differ.

        Args:
            local_client: Client connected to local API
            cloud_client: Client connected to cloud API
        """
        self.local = local_client
        self.cloud = cloud_client

    def compute_schema_diff(self) -> Dict[str, Any]:
        """
        Compute schema differences between local and cloud.

        Returns:
            Dictionary containing:
            - tables_to_create: List of tables in local but not cloud
            - tables_to_drop: List of tables in cloud but not local
            - tables_to_alter: List of tables with schema changes
        """
        # Fetch table lists
        try:
            local_tables = self._fetch_tables(self.local)
            cloud_tables = self._fetch_tables(self.cloud)
        except Exception as e:
            return {
                "error": f"Failed to fetch tables: {str(e)}",
                "tables_to_create": [],
                "tables_to_drop": [],
                "tables_to_alter": []
            }

        local_names = {t["table_name"] for t in local_tables}
        cloud_names = {t["table_name"] for t in cloud_tables}

        # Tables to create (in local but not cloud)
        tables_to_create = []
        for table in local_tables:
            if table["table_name"] not in cloud_names:
                tables_to_create.append({
                    "table_name": table["table_name"],
                    "schema": table.get("schema", {}),
                    "description": table.get("description")
                })

        # Tables to drop (in cloud but not local)
        tables_to_drop = []
        for table in cloud_tables:
            if table["table_name"] not in local_names:
                tables_to_drop.append({
                    "table_name": table["table_name"]
                })

        # Tables to alter (schema changes)
        tables_to_alter = []
        local_map = {t["table_name"]: t for t in local_tables}
        cloud_map = {t["table_name"]: t for t in cloud_tables}

        for name in local_names & cloud_names:
            local_schema = local_map[name].get("schema", {})
            cloud_schema = cloud_map[name].get("schema", {})

            if local_schema != cloud_schema:
                # Compute field changes
                local_fields = set(local_schema.get("fields", {}).keys())
                cloud_fields = set(cloud_schema.get("fields", {}).keys())

                added_fields = local_fields - cloud_fields
                removed_fields = cloud_fields - local_fields

                # Check for type changes in existing fields
                type_changes = []
                for field in local_fields & cloud_fields:
                    local_type = local_schema.get("fields", {}).get(field)
                    cloud_type = cloud_schema.get("fields", {}).get(field)
                    if local_type != cloud_type:
                        type_changes.append({
                            "field": field,
                            "old_type": cloud_type,
                            "new_type": local_type
                        })

                tables_to_alter.append({
                    "table_name": name,
                    "added_fields": list(added_fields),
                    "removed_fields": list(removed_fields),
                    "type_changes": type_changes,
                    "local_schema": local_schema,
                    "cloud_schema": cloud_schema
                })

        return {
            "tables_to_create": tables_to_create,
            "tables_to_drop": tables_to_drop,
            "tables_to_alter": tables_to_alter
        }

    def compute_data_diff(self) -> Dict[str, Any]:
        """
        Compute data differences between local and cloud.

        Returns:
            Dictionary containing row counts and changes for each table
        """
        try:
            local_tables = self._fetch_tables(self.local)
            cloud_tables = self._fetch_tables(self.cloud)
        except Exception as e:
            return {
                "error": f"Failed to fetch tables: {str(e)}",
                "total_new_rows": 0,
                "total_updated_rows": 0,
                "total_deleted_rows": 0,
                "table_details": []
            }

        local_map = {t["table_name"]: t for t in local_tables}
        cloud_map = {t["table_name"]: t for t in cloud_tables}

        table_details = []
        total_new = 0
        total_updated = 0
        total_deleted = 0

        # Compare tables that exist in both
        for name in set(local_map.keys()) & set(cloud_map.keys()):
            local_count = local_map[name].get("row_count", 0)
            cloud_count = cloud_map[name].get("row_count", 0)

            # Simple heuristic: if local has more rows, they're "new"
            # In reality, we'd need to compare actual row data
            new_rows = max(0, local_count - cloud_count)
            deleted_rows = max(0, cloud_count - local_count)

            if new_rows > 0 or deleted_rows > 0:
                table_details.append({
                    "table_name": name,
                    "local_count": local_count,
                    "cloud_count": cloud_count,
                    "new_rows": new_rows,
                    "deleted_rows": deleted_rows,
                    "updated_rows": 0  # Would require row-level comparison
                })

                total_new += new_rows
                total_deleted += deleted_rows

        # Tables that only exist locally (all rows are "new")
        for name in set(local_map.keys()) - set(cloud_map.keys()):
            local_count = local_map[name].get("row_count", 0)
            if local_count > 0:
                table_details.append({
                    "table_name": name,
                    "local_count": local_count,
                    "cloud_count": 0,
                    "new_rows": local_count,
                    "deleted_rows": 0,
                    "updated_rows": 0
                })
                total_new += local_count

        return {
            "total_new_rows": total_new,
            "total_updated_rows": total_updated,
            "total_deleted_rows": total_deleted,
            "table_details": table_details
        }

    def compute_vectors_diff(self) -> Dict[str, Any]:
        """
        Compute vector differences between local and cloud.

        Returns:
            Dictionary containing vector statistics and changes
        """
        try:
            local_stats = self._fetch_vector_stats(self.local)
            cloud_stats = self._fetch_vector_stats(self.cloud)
        except Exception as e:
            return {
                "error": f"Failed to fetch vector stats: {str(e)}",
                "total_upserts": 0,
                "total_deletes": 0,
                "namespace_details": []
            }

        # Extract namespace stats
        local_namespaces = local_stats.get("namespaces", {})
        cloud_namespaces = cloud_stats.get("namespaces", {})

        namespace_details = []
        total_upserts = 0
        total_deletes = 0

        # All namespaces
        all_namespaces = set(local_namespaces.keys()) | set(cloud_namespaces.keys())

        for ns in all_namespaces:
            local_count = local_namespaces.get(ns, {}).get("vector_count", 0)
            cloud_count = cloud_namespaces.get(ns, {}).get("vector_count", 0)

            upserts = max(0, local_count - cloud_count)
            deletes = max(0, cloud_count - local_count)

            if upserts > 0 or deletes > 0:
                namespace_details.append({
                    "namespace": ns,
                    "local_count": local_count,
                    "cloud_count": cloud_count,
                    "upserts": upserts,
                    "deletes": deletes
                })

                total_upserts += upserts
                total_deletes += deletes

        return {
            "total_upserts": total_upserts,
            "total_deletes": total_deletes,
            "namespace_details": namespace_details,
            "local_total": local_stats.get("total_vectors", 0),
            "cloud_total": cloud_stats.get("total_vectors", 0)
        }

    def _fetch_tables(self, client: AINativeClient) -> List[Dict[str, Any]]:
        """
        Fetch all tables from a client.

        Args:
            client: AINative client instance

        Returns:
            List of table dictionaries
        """
        try:
            result = client.zerodb.tables.list_tables(limit=1000)
            return result.get("tables", [])
        except Exception as e:
            # If tables endpoint fails, return empty list
            return []

    def _fetch_vector_stats(self, client: AINativeClient) -> Dict[str, Any]:
        """
        Fetch vector statistics from a client.

        Args:
            client: AINative client instance

        Returns:
            Dictionary with vector statistics
        """
        try:
            # Get project ID from client's organization context
            # First, try to get list of projects
            projects_result = client.zerodb.projects.list(limit=1)
            projects = projects_result.get("projects", [])

            if not projects:
                # No projects available
                return {
                    "total_vectors": 0,
                    "namespaces": {}
                }

            # Use the first project for stats
            project_id = projects[0].get("id")
            result = client.zerodb.vectors.describe_index_stats(project_id=project_id)
            return result
        except Exception as e:
            # Return empty stats if not available
            return {
                "total_vectors": 0,
                "namespaces": {}
            }
