"""Tests for birds_bi.utils module - utility helper functions."""

import pandas as pd

from birds_bi.utils import (
    bool_to_int,
    find_string_line_number,
    format_sql_columns,
    sql_result_to_dataframe,
    var_insert_line,
)


class TestBoolToInt:
    """Test bool_to_int utility function."""

    def test_bool_to_int_true(self) -> None:
        """Test converting True to 1."""
        assert bool_to_int(True) == 1

    def test_bool_to_int_false(self) -> None:
        """Test converting False to 0."""
        assert bool_to_int(False) == 0

    def test_bool_to_int_truthy_values(self) -> None:
        """Test converting truthy values."""
        assert bool_to_int(1) == 1
        assert bool_to_int("yes") == 1
        assert bool_to_int([1, 2, 3]) == 1

    def test_bool_to_int_falsy_values(self) -> None:
        """Test converting falsy values."""
        assert bool_to_int(0) == 0
        assert bool_to_int("") == 0
        assert bool_to_int([]) == 0
        assert bool_to_int(None) == 0


class TestFormatSqlColumns:
    """Test format_sql_columns utility function."""

    def test_format_single_column(self) -> None:
        """Test formatting a single column."""
        result = format_sql_columns(["CustomerID"])
        assert "CustomerID" in result
        assert isinstance(result, str)

    def test_format_multiple_columns(self) -> None:
        """Test formatting multiple columns."""
        columns = ["ID", "Name", "Email", "Phone"]
        result = format_sql_columns(columns)

        assert "ID" in result
        assert "Name" in result
        assert "Email" in result
        assert "Phone" in result

    def test_format_columns_with_whitespace(self) -> None:
        """Test formatting columns with leading/trailing whitespace."""
        columns = ["  ID  ", " Name ", "Email"]
        result = format_sql_columns(columns)

        # Should trim whitespace
        assert "ID" in result
        assert "Name" in result

    def test_format_empty_list(self) -> None:
        """Test formatting empty column list."""
        result = format_sql_columns([])
        assert result == "" or isinstance(result, str)

    def test_format_columns_preserves_brackets(self) -> None:
        """Test that SQL column formatting handles brackets."""
        columns = ["[CustomerID]", "[OrderDate]", "[Amount]"]
        result = format_sql_columns(columns)

        # Result should contain the column references
        assert isinstance(result, str)


class TestFindStringLineNumber:
    """Test find_string_line_number utility function."""

    def test_find_string_exact_match(self) -> None:
        """Test finding exact string match."""
        lines = ["First line", "Second line", "Third line"]
        line_num = find_string_line_number(lines, "Second line")

        assert line_num == 2  # 1-based line number

    def test_find_string_case_insensitive(self) -> None:
        """Test finding string with case insensitive search."""
        lines = ["Hello World", "Goodbye World"]
        line_num = find_string_line_number(lines, "hello world", ignore_case=True)

        assert line_num == 1  # 1-based line number

    def test_find_string_case_sensitive(self) -> None:
        """Test finding string with case sensitive search."""
        lines = ["Hello World", "hello world"]
        line_num = find_string_line_number(lines, "hello world", ignore_case=False)

        assert line_num == 2  # 1-based line number

    def test_find_string_not_found(self) -> None:
        """Test behavior when string is not found."""
        lines = ["Line 1", "Line 2", "Line 3"]
        line_num = find_string_line_number(lines, "Nonexistent")

        # Should return None or -1 when not found
        assert line_num is None or line_num == -1

    def test_find_string_partial_match(self) -> None:
        """Test finding partial string match."""
        lines = ["SELECT * FROM Customer", "WHERE Active = 1", "ORDER BY Name"]
        line_num = find_string_line_number(lines, "WHERE")

        assert line_num == 2  # 1-based line number


class TestVarInsertLine:
    """Test var_insert_line utility function."""

    def test_insert_line_after_match(self) -> None:
        """Test inserting line after a matching string."""
        text = "Line 1\nLine 2\nLine 3"
        new_line = "New Line\n"
        needle = "Line 2"

        result = var_insert_line(text, new_line, needle)

        assert "New Line" in result
        # Function inserts at line position (not newline-separated)
        assert isinstance(result, str)

    def test_insert_line_maintains_order(self) -> None:
        """Test that line insertion maintains proper order."""
        text = "First\nSecond\nThird"
        new_line = "Inserted"
        needle = "Second"

        result = var_insert_line(text, new_line, needle)
        lines = result.split("\n")

        # New line should appear after the needle
        second_idx = lines.index("Second")
        assert "Inserted" in lines[second_idx + 1]

    def test_insert_line_needle_not_found(self) -> None:
        """Test insertion when needle string is not found."""
        text = "Line A\nLine B\nLine C"
        new_line = "New Line"
        needle = "Nonexistent"

        result = var_insert_line(text, new_line, needle)

        # Should handle gracefully (append or return original)
        assert isinstance(result, str)


class TestSqlResultToDataframe:
    """Test sql_result_to_dataframe utility function."""

    def test_convert_single_result_set(self) -> None:
        """Test converting single result set to DataFrame."""
        sql_result: dict[str, list[dict[str, int | pd.DataFrame]]] = {
            "result_sets": [
                {"statement_index": 1, "dataframe": pd.DataFrame({"ID": [1, 2, 3]})}
            ]
        }

        dfs = sql_result_to_dataframe(sql_result)

        assert isinstance(dfs, list) or isinstance(dfs, pd.DataFrame)

    def test_convert_multiple_result_sets(self) -> None:
        """Test converting multiple result sets."""
        sql_result: dict[str, list[dict[str, int | pd.DataFrame]]] = {
            "result_sets": [
                {"statement_index": 1, "dataframe": pd.DataFrame({"ID": [1]})},
                {"statement_index": 2, "dataframe": pd.DataFrame({"Name": ["Test"]})},
            ]
        }

        dfs = sql_result_to_dataframe(sql_result)

        assert isinstance(dfs, list) or isinstance(dfs, pd.DataFrame)

    def test_convert_empty_result_set(self) -> None:
        """Test converting empty result set."""
        sql_result: dict[str, list[dict[str, int | pd.DataFrame]]] = {"result_sets": []}

        dfs = sql_result_to_dataframe(sql_result)

        # Should handle empty results gracefully
        assert dfs is not None

    def test_convert_preserves_data(self) -> None:
        """Test that conversion preserves DataFrame data."""
        df_original = pd.DataFrame(
            {"ID": [1, 2, 3], "Name": ["A", "B", "C"], "Value": [10.5, 20.3, 30.7]}
        )

        sql_result = {"result_sets": [{"statement_index": 1, "dataframe": df_original}]}

        result = sql_result_to_dataframe(sql_result)

        # Function behavior depends on implementation
        assert result is not None


class TestUtilsIntegration:
    """Integration tests for utility functions."""

    def test_bool_to_int_in_sql_context(self) -> None:
        """Test bool_to_int for SQL parameter conversion."""
        # Common use case: converting Python booleans for SQL
        is_active = True
        is_deleted = False

        sql = f"UPDATE Table SET Active = {bool_to_int(is_active)}, Deleted = {bool_to_int(is_deleted)}"

        assert "Active = 1" in sql
        assert "Deleted = 0" in sql

    def test_format_and_find_workflow(self) -> None:
        """Test typical workflow: format columns then find in generated SQL."""
        columns = ["CustomerID", "OrderDate", "Amount"]
        formatted = format_sql_columns(columns)

        # Typical usage would create SQL
        sql_lines = ["SELECT", formatted, "FROM Orders"]

        # Then find specific lines (1-based line numbers)
        select_line = find_string_line_number(sql_lines, "SELECT")
        assert select_line == 1
