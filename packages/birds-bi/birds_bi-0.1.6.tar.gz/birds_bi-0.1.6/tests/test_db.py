"""Tests for birds_bi.db module - database connection and execution utilities."""

import pytest

from birds_bi.db import (
    DbConfig,
    ResultSet,
    SqlExecutionResult,
    _build_connection_string,
)


class TestDbConfig:
    """Test DbConfig model and connection string building."""

    def test_dbconfig_default_values(self) -> None:
        """Test DbConfig initializes with correct defaults."""
        config = DbConfig(server="localhost", database="TestDB")

        assert config.server == "localhost"
        assert config.database == "TestDB"
        assert config.auth_method == "windows"
        assert config.driver == "ODBC Driver 18 for SQL Server"
        assert config.encrypt is False
        assert config.trust_server_certificate is True
        assert config.timeout_seconds == 30

    def test_dbconfig_windows_auth(self) -> None:
        """Test DbConfig with Windows authentication."""
        config = DbConfig(
            server="sql.example.com", database="Production", auth_method="windows"
        )

        assert config.auth_method == "windows"
        assert config.user is None
        assert config.password is None

    def test_dbconfig_sql_auth(self) -> None:
        """Test DbConfig with SQL Server authentication."""
        config = DbConfig(
            server="sql.example.com",
            database="Production",
            auth_method="sql",
            user="testuser",
            password="testpass123",
        )

        assert config.auth_method == "sql"
        assert config.user == "testuser"
        assert config.password == "testpass123"


class TestConnectionString:
    """Test connection string building."""

    def test_build_connection_string_windows_auth(self) -> None:
        """Test building connection string with Windows authentication."""
        config = DbConfig(server="localhost", database="TestDB", auth_method="windows")

        conn_str = _build_connection_string(config)

        assert "DRIVER={ODBC Driver 18 for SQL Server}" in conn_str
        assert "SERVER=localhost" in conn_str
        assert "DATABASE=TestDB" in conn_str
        assert "Trusted_Connection=yes" in conn_str
        assert "Connection Timeout=30" in conn_str
        assert "Encrypt=no" in conn_str
        assert "TrustServerCertificate=yes" in conn_str

    def test_build_connection_string_sql_auth(self) -> None:
        """Test building connection string with SQL authentication."""
        config = DbConfig(
            server="sqlserver.local",
            database="AppDB",
            auth_method="sql",
            user="appuser",
            password="SecurePass123!",
        )

        conn_str = _build_connection_string(config)

        assert "DRIVER={ODBC Driver 18 for SQL Server}" in conn_str
        assert "SERVER=sqlserver.local" in conn_str
        assert "DATABASE=AppDB" in conn_str
        assert "UID=appuser" in conn_str
        assert "PWD=SecurePass123!" in conn_str
        assert "Trusted_Connection" not in conn_str

    def test_build_connection_string_with_encryption(self) -> None:
        """Test building connection string with encryption enabled."""
        config = DbConfig(
            server="secure.sql.com",
            database="SecureDB",
            encrypt=True,
            trust_server_certificate=False,
        )

        conn_str = _build_connection_string(config)

        assert "Encrypt=yes" in conn_str
        assert "TrustServerCertificate=no" in conn_str

    def test_build_connection_string_sql_auth_missing_credentials(self) -> None:
        """Test that SQL auth without credentials raises ValueError."""
        config = DbConfig(server="localhost", database="TestDB", auth_method="sql")

        with pytest.raises(
            ValueError, match="SQL authentication requires both user and password"
        ):
            _build_connection_string(config)


class TestDataModels:
    """Test data model structures."""

    def test_result_set_creation(self) -> None:
        """Test ResultSet model creation."""
        import pandas as pd

        df = pd.DataFrame({"ID": [1, 2, 3], "Name": ["A", "B", "C"]})
        result_set = ResultSet(statement_index=1, dataframe=df)

        assert result_set.statement_index == 1
        assert len(result_set.dataframe) == 3
        assert list(result_set.dataframe.columns) == ["ID", "Name"]

    def test_sql_execution_result_creation(self) -> None:
        """Test SqlExecutionResult model creation."""
        import pandas as pd

        df = pd.DataFrame({"Count": [5]})
        result_sets = [ResultSet(statement_index=1, dataframe=df)]
        messages = ["Command completed successfully"]
        errors: list[str] = []

        result = SqlExecutionResult(
            statements_executed=1,
            rows_affected=5,
            result_sets=result_sets,
            messages=messages,
            errors=errors,
        )

        assert result.statements_executed == 1
        assert result.rows_affected == 5
        assert len(result.result_sets) == 1
        assert len(result.messages) == 1
        assert len(result.errors) == 0
        assert result.messages[0] == "Command completed successfully"
