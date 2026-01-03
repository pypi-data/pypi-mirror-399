"""
ZeroDB Tables Module

Handles NoSQL table operations including CRUD operations for tables and rows.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from ..client import AINativeClient


class TablesClient:
    """Client for ZeroDB NoSQL table operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize tables client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/zerodb/tables"

    # Table Management Operations

    def create_table(
        self,
        table_name: str,
        schema: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new NoSQL table.

        Args:
            table_name: Unique table name
            schema: Table schema definition with fields and indexes
                Example: {
                    "fields": {
                        "email": "string",
                        "name": "string",
                        "age": "number"
                    },
                    "indexes": ["email"]
                }
            description: Optional table description

        Returns:
            Created table information including table_id

        Example:
            >>> client.zerodb.tables.create_table(
            ...     "users",
            ...     schema={
            ...         "fields": {"email": "string", "name": "string", "age": "number"},
            ...         "indexes": ["email"]
            ...     }
            ... )
        """
        data = {
            "table_name": table_name,
            "schema": schema,
        }

        if description:
            data["description"] = description

        return self.client.post(self.base_path, data=data)

    def list_tables(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List all tables in the project.

        Args:
            limit: Maximum number of results (default: 100)
            offset: Pagination offset (default: 0)

        Returns:
            Dictionary with 'tables' list and 'total' count

        Example:
            >>> tables = client.zerodb.tables.list_tables(limit=50)
            >>> for table in tables['tables']:
            ...     print(f"{table['table_name']}: {table['row_count']} rows")
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        return self.client.get(self.base_path, params=params)

    def get_table(
        self,
        table_id: str,
    ) -> Dict[str, Any]:
        """
        Get table details and metadata.

        Args:
            table_id: Table ID or table name

        Returns:
            Table details including schema, row_count, and statistics

        Example:
            >>> table = client.zerodb.tables.get_table("users")
            >>> print(f"Schema: {table['schema']}")
            >>> print(f"Rows: {table['row_count']}")
        """
        return self.client.get(f"{self.base_path}/{table_id}")

    def delete_table(
        self,
        table_id: str,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """
        Delete a table and all its data.

        Args:
            table_id: Table ID or table name
            confirm: Must be True to confirm deletion (safety check)

        Returns:
            Deletion result with number of rows deleted

        Example:
            >>> result = client.zerodb.tables.delete_table("old_table", confirm=True)
            >>> print(f"Deleted {result['rows_deleted']} rows")
        """
        if not confirm:
            raise ValueError(
                "Table deletion requires confirmation. "
                "Set confirm=True to proceed."
            )

        data = {"confirm": True}
        return self.client.delete(f"{self.base_path}/{table_id}", data=data)

    # Row Operations

    def insert_rows(
        self,
        table_name: str,
        rows: List[Dict[str, Any]],
        return_ids: bool = True,
    ) -> Dict[str, Any]:
        """
        Insert rows into a table.

        Args:
            table_name: Table name
            rows: List of row objects to insert (max 1000 per request)
            return_ids: Whether to return inserted row IDs

        Returns:
            Insert result with inserted_count and optional row IDs

        Example:
            >>> rows = [
            ...     {"email": "user@example.com", "name": "John", "age": 30},
            ...     {"email": "jane@example.com", "name": "Jane", "age": 25}
            ... ]
            >>> result = client.zerodb.tables.insert_rows("users", rows)
            >>> print(f"Inserted {result['inserted_count']} rows")
        """
        if not rows:
            raise ValueError("rows cannot be empty")

        if len(rows) > 1000:
            raise ValueError("Maximum 1000 rows per request")

        data = {
            "rows": rows,
            "return_ids": return_ids,
        }

        return self.client.post(f"{self.base_path}/{table_name}/rows", data=data)

    def query_rows(
        self,
        table_name: str,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, int]] = None,
        limit: int = 100,
        offset: int = 0,
        projection: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Query rows from a table with filters and sorting.

        Args:
            table_name: Table name
            filter: MongoDB-style query filter
                Example: {"age": {"$gte": 25}, "status": "active"}
            sort: Sort specification
                Example: {"created_at": -1} for descending
            limit: Maximum results (default: 100)
            offset: Pagination offset (default: 0)
            projection: Field projection (which fields to return)
                Example: {"name": 1, "email": 1, "_id": 0}

        Returns:
            Query results with rows, total count, and pagination info

        Example:
            >>> # Query users over 25, sorted by age descending
            >>> results = client.zerodb.tables.query_rows(
            ...     "users",
            ...     filter={"age": {"$gte": 25}},
            ...     sort={"age": -1},
            ...     limit=10
            ... )
            >>> for row in results['rows']:
            ...     print(f"{row['name']}: {row['age']}")
        """
        data = {
            "limit": limit,
            "offset": offset,
        }

        if filter:
            data["filter"] = filter

        if sort:
            data["sort"] = sort

        if projection:
            data["projection"] = projection

        return self.client.post(f"{self.base_path}/{table_name}/query", data=data)

    def update_rows(
        self,
        table_name: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        """
        Update rows matching the filter.

        Args:
            table_name: Table name
            filter: MongoDB-style query filter to match rows
            update: Update operations
                Example: {"$set": {"age": 31}, "$inc": {"login_count": 1}}
            upsert: Insert if not found (default: False)

        Returns:
            Update result with count of modified rows

        Example:
            >>> # Update age for specific user
            >>> result = client.zerodb.tables.update_rows(
            ...     "users",
            ...     filter={"email": "user@example.com"},
            ...     update={"$set": {"age": 31}}
            ... )
            >>> print(f"Updated {result['modified_count']} rows")
        """
        data = {
            "filter": filter,
            "update": update,
            "upsert": upsert,
        }

        return self.client.put(f"{self.base_path}/{table_name}/rows", data=data)

    def delete_rows(
        self,
        table_name: str,
        filter: Dict[str, Any],
        limit: int = 0,
    ) -> Dict[str, Any]:
        """
        Delete rows matching the filter.

        Args:
            table_name: Table name
            filter: MongoDB-style query filter to match rows
            limit: Maximum rows to delete (0 = all matching, default)

        Returns:
            Delete result with count of deleted rows

        Example:
            >>> # Delete inactive users
            >>> result = client.zerodb.tables.delete_rows(
            ...     "users",
            ...     filter={"age": {"$lt": 18}}
            ... )
            >>> print(f"Deleted {result['deleted_count']} rows")
        """
        data = {
            "filter": filter,
            "limit": limit,
        }

        return self.client.request(
            "DELETE",
            f"{self.base_path}/{table_name}/rows",
            data=data
        )

    # Utility Methods

    def count_rows(
        self,
        table_name: str,
        filter: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Count rows in a table matching optional filter.

        Args:
            table_name: Table name
            filter: Optional query filter

        Returns:
            Number of matching rows

        Example:
            >>> count = client.zerodb.tables.count_rows("users", {"age": {"$gte": 18}})
            >>> print(f"Adult users: {count}")
        """
        result = self.query_rows(
            table_name,
            filter=filter,
            limit=0  # Don't return actual rows, just count
        )
        return result.get("total", 0)

    def table_exists(
        self,
        table_name: str,
    ) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Table name to check

        Returns:
            True if table exists, False otherwise

        Example:
            >>> if client.zerodb.tables.table_exists("users"):
            ...     print("Users table exists")
        """
        try:
            self.get_table(table_name)
            return True
        except Exception:
            return False
