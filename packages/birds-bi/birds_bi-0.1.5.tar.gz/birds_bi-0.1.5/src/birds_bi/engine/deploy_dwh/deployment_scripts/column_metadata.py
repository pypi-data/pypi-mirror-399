from __future__ import annotations

from collections import defaultdict

from birds_bi.db.models import DbConfig
from birds_bi.db.sql_execution import execute_sql_string
from birds_bi.repo.component import Component
from birds_bi.repo.models import TableDefinition
from birds_bi.utils.bool_to_int import bool_to_int


def generate_column_metadata_script(
    component: Component, instance_execution_id: str
) -> str:  # noqa: ARG001
    """Generate SQL that populates column metadata for a component."""

    result = ""

    grouped: dict[str, list[TableDefinition]] = defaultdict(list)

    for table in component.table_definitions:
        grouped[table.schema].append(table)

    for schema, tables in grouped.items():

        declare_string = (
            f"declare @table_column_metadata_{schema} dbo.table_column_metadata\n"
            f"declare @data_connection_id{schema} INT;\n"
            f"select @data_connection_id{schema} = dc.data_connection_id "
            f"from meta.data_connections dc "
            f"left join meta.stage_schemas ss "
            f"on dc.stage_schema_id = ss.stage_schema_id "
            f"where ss.stage_schema = '{schema}';"
        )

        result += declare_string

        for table in tables:
            for column in table.columns:
                string = (
                    f"insert into @table_column_metadata_{schema} "
                    f"values("
                    f"0"
                    f",N'{table.table_identifier}'"
                    f",0"
                    f",N'{column.column_name}'"
                    f",N'{column.data_type}'"
                    f",{column.character_maximum_length}"
                    f",{column.numeric_precision}"
                    f",{column.numeric_scale}"
                    f",{bool_to_int(column.nullable)}"
                    f",{bool_to_int(column.business_key)})\n"
                )
                result += string

        exec_string = (
            f"exec meta.add_all_table_definitions "
            f"@data_connection_id=@data_connection_id{schema}"
            f",@component_category='{component.category}'"
            f",@component_name='{component.category}{component.base_name}'"
            f",@table_columns=@table_column_metadata_{schema}"
            f",@instance_execution_id={instance_execution_id}"
            f",@debug=0\n"
        )
        result += exec_string

    return result


def execute_column_metadata_script(
    component: Component,
    instance_execution_id: str,
    db_config: DbConfig,
) -> None:
    sql = generate_column_metadata_script(
        component=component,
        instance_execution_id=instance_execution_id,
    )

    execute_sql_string(db_config=db_config, sql=sql)
