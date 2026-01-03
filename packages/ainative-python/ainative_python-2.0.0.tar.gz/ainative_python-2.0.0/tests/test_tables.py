"""
Tests for Table Operations in AINative SDK
"""

import pytest
from unittest.mock import MagicMock


class TestTableManagement:
    """Test table management operations (create, list, get, delete)"""

    def test_create_table(self, client, mock_httpx_client, sample_table_schema):
        """Test creating a new table"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"table_id": "550e8400-e29b-41d4-a716-446655440000", "status": "created"}'
        mock_response.json.return_value = {
            "table_id": "550e8400-e29b-41d4-a716-446655440000",
            "table_name": "users",
            "status": "created",
            "created_at": "2025-01-14T10:00:00Z"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.create_table(
            table_name="users",
            schema=sample_table_schema
        )

        assert result["status"] == "created"
        assert "table_id" in result
        assert result["table_name"] == "users"

    def test_create_table_with_description(self, client, mock_httpx_client, sample_table_schema):
        """Test creating a table with description"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"table_id": "550e8400-e29b-41d4-a716-446655440000"}'
        mock_response.json.return_value = {
            "table_id": "550e8400-e29b-41d4-a716-446655440000",
            "table_name": "users",
            "description": "User data table",
            "status": "created"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.create_table(
            table_name="users",
            schema=sample_table_schema,
            description="User data table"
        )

        assert result["description"] == "User data table"

    def test_list_tables(self, client, mock_httpx_client):
        """Test listing all tables"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"tables": []}'
        mock_response.json.return_value = {
            "tables": [
                {"table_id": "id1", "table_name": "users", "row_count": 100},
                {"table_id": "id2", "table_name": "products", "row_count": 50}
            ],
            "total": 2
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.list_tables()

        assert len(result["tables"]) == 2
        assert result["total"] == 2
        assert result["tables"][0]["table_name"] == "users"

    def test_list_tables_with_pagination(self, client, mock_httpx_client):
        """Test listing tables with pagination parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"tables": []}'
        mock_response.json.return_value = {
            "tables": [{"table_id": "id1", "table_name": "users", "row_count": 100}],
            "total": 50
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.list_tables(limit=10, offset=20)

        assert result["total"] == 50

    def test_get_table(self, client, mock_httpx_client, sample_table_response):
        """Test getting table details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = sample_table_response
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.get_table("users")

        assert result["table_name"] == "users"
        assert result["row_count"] == 100
        assert "schema" in result

    def test_delete_table(self, client, mock_httpx_client):
        """Test deleting a table with confirmation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "deleted"}'
        mock_response.json.return_value = {
            "status": "deleted",
            "rows_deleted": 100,
            "table_name": "old_table"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.delete_table("old_table", confirm=True)

        assert result["status"] == "deleted"
        assert result["rows_deleted"] == 100

    def test_delete_table_requires_confirmation(self, client):
        """Test that delete_table requires confirmation"""
        with pytest.raises(ValueError, match="confirmation"):
            client.zerodb.tables.delete_table("users", confirm=False)

    def test_table_exists(self, client, mock_httpx_client, sample_table_response):
        """Test checking if table exists"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = sample_table_response
        mock_httpx_client.request.return_value = mock_response

        exists = client.zerodb.tables.table_exists("users")

        assert exists is True

    def test_table_not_exists(self, client, mock_httpx_client):
        """Test checking if table does not exist"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"error": "not found"}'
        mock_httpx_client.request.return_value = mock_response

        exists = client.zerodb.tables.table_exists("nonexistent")

        assert exists is False


class TestRowOperations:
    """Test row operations (insert, query, update, delete)"""

    def test_insert_rows(self, client, mock_httpx_client, sample_rows):
        """Test inserting rows into table"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"inserted_count": 3}'
        mock_response.json.return_value = {
            "inserted_count": 3,
            "inserted_ids": ["id1", "id2", "id3"],
            "failed_count": 0,
            "status": "success"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.insert_rows("users", sample_rows)

        assert result["inserted_count"] == 3
        assert len(result["inserted_ids"]) == 3
        assert result["status"] == "success"

    def test_insert_rows_empty_raises_error(self, client):
        """Test that inserting empty rows raises error"""
        with pytest.raises(ValueError, match="cannot be empty"):
            client.zerodb.tables.insert_rows("users", [])

    def test_insert_rows_exceeds_limit(self, client):
        """Test that inserting too many rows raises error"""
        large_rows = [{"id": i} for i in range(1001)]

        with pytest.raises(ValueError, match="Maximum 1000 rows"):
            client.zerodb.tables.insert_rows("users", large_rows)

    def test_query_rows(self, client, mock_httpx_client, sample_query_results):
        """Test querying rows from table"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = sample_query_results
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.query_rows("users")

        assert len(result["rows"]) == 2
        assert result["total"] == 2
        assert result["has_more"] is False

    def test_query_rows_with_filter(self, client, mock_httpx_client, sample_query_results):
        """Test querying rows with filter"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = sample_query_results
        mock_httpx_client.request.return_value = mock_response

        filter_query = {"age": {"$gte": 25}}
        result = client.zerodb.tables.query_rows("users", filter=filter_query)

        assert len(result["rows"]) == 2

    def test_query_rows_with_sort(self, client, mock_httpx_client, sample_query_results):
        """Test querying rows with sorting"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = sample_query_results
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.query_rows(
            "users",
            sort={"age": -1}  # Descending
        )

        assert "rows" in result

    def test_query_rows_with_projection(self, client, mock_httpx_client):
        """Test querying rows with field projection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "rows": [
                {"name": "John", "email": "john@example.com"}
            ],
            "total": 1
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.query_rows(
            "users",
            projection={"name": 1, "email": 1, "_id": 0}
        )

        assert len(result["rows"]) == 1

    def test_update_rows(self, client, mock_httpx_client):
        """Test updating rows"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"modified_count": 5}'
        mock_response.json.return_value = {
            "modified_count": 5,
            "matched_count": 5,
            "status": "success"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.update_rows(
            "users",
            filter={"age": {"$lt": 18}},
            update={"$set": {"minor": True}}
        )

        assert result["modified_count"] == 5

    def test_update_rows_with_upsert(self, client, mock_httpx_client):
        """Test updating rows with upsert option"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"upserted_count": 1}'
        mock_response.json.return_value = {
            "modified_count": 0,
            "upserted_count": 1,
            "upserted_id": "new_id"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.update_rows(
            "users",
            filter={"email": "newuser@example.com"},
            update={"$set": {"name": "New User"}},
            upsert=True
        )

        assert result["upserted_count"] == 1

    def test_delete_rows(self, client, mock_httpx_client):
        """Test deleting rows"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"deleted_count": 3}'
        mock_response.json.return_value = {
            "deleted_count": 3,
            "status": "success"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.delete_rows(
            "users",
            filter={"age": {"$lt": 18}}
        )

        assert result["deleted_count"] == 3

    def test_delete_rows_with_limit(self, client, mock_httpx_client):
        """Test deleting rows with limit"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"deleted_count": 10}'
        mock_response.json.return_value = {
            "deleted_count": 10,
            "status": "success"
        }
        mock_httpx_client.request.return_value = mock_response

        result = client.zerodb.tables.delete_rows(
            "users",
            filter={"inactive": True},
            limit=10
        )

        assert result["deleted_count"] == 10

    def test_count_rows(self, client, mock_httpx_client):
        """Test counting rows in table"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "rows": [],
            "total": 150,
            "offset": 0,
            "limit": 0
        }
        mock_httpx_client.request.return_value = mock_response

        count = client.zerodb.tables.count_rows("users")

        assert count == 150

    def test_count_rows_with_filter(self, client, mock_httpx_client):
        """Test counting rows with filter"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "rows": [],
            "total": 25,
            "offset": 0,
            "limit": 0
        }
        mock_httpx_client.request.return_value = mock_response

        count = client.zerodb.tables.count_rows(
            "users",
            filter={"age": {"$gte": 18}}
        )

        assert count == 25


class TestTableIntegration:
    """Integration tests for table workflows"""

    def test_full_table_workflow(self, client, mock_httpx_client, sample_table_schema, sample_rows):
        """Test complete table workflow: create, insert, query, update, delete"""
        # Create table
        create_response = MagicMock()
        create_response.status_code = 200
        create_response.text = '{}'
        create_response.json.return_value = {
            "table_id": "550e8400-e29b-41d4-a716-446655440000",
            "table_name": "users",
            "status": "created"
        }

        # Insert rows
        insert_response = MagicMock()
        insert_response.status_code = 200
        insert_response.text = '{}'
        insert_response.json.return_value = {
            "inserted_count": 3,
            "inserted_ids": ["id1", "id2", "id3"]
        }

        # Query rows
        query_response = MagicMock()
        query_response.status_code = 200
        query_response.text = '{}'
        query_response.json.return_value = {
            "rows": sample_rows,
            "total": 3
        }

        # Update rows
        update_response = MagicMock()
        update_response.status_code = 200
        update_response.text = '{}'
        update_response.json.return_value = {
            "modified_count": 1
        }

        # Delete table
        delete_response = MagicMock()
        delete_response.status_code = 200
        delete_response.text = '{}'
        delete_response.json.return_value = {
            "status": "deleted",
            "rows_deleted": 3
        }

        # Set up mock responses in sequence
        mock_httpx_client.request.side_effect = [
            create_response,
            insert_response,
            query_response,
            update_response,
            delete_response
        ]

        # Execute workflow
        table = client.zerodb.tables.create_table("users", sample_table_schema)
        assert table["status"] == "created"

        insert_result = client.zerodb.tables.insert_rows("users", sample_rows)
        assert insert_result["inserted_count"] == 3

        query_result = client.zerodb.tables.query_rows("users")
        assert query_result["total"] == 3

        update_result = client.zerodb.tables.update_rows(
            "users",
            filter={"email": "user1@example.com"},
            update={"$set": {"age": 31}}
        )
        assert update_result["modified_count"] == 1

        delete_result = client.zerodb.tables.delete_table("users", confirm=True)
        assert delete_result["status"] == "deleted"
