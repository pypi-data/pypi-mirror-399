from birds_bi.db.models import DbConfig
from birds_bi.db.sql_execution import execute_sql_string
from birds_bi.repo.component import Component

TEMPLATE = """
declare @stage_table_indexes dbo.table_indexes
--stage_table_indexes

exec meta.add_all_stage_indexes @instance_id=1,@table_indexes=@stage_table_indexes,@debug=0,@instance_execution_id=${instance_execution_id}
"""


def generate_stage_table_indexes_script(
    component: Component, instance_execution_id: str
) -> str:  # noqa: ARG001
    """Return the static SQL template for stage table indexes."""

    return TEMPLATE.replace("${instance_execution_id}", instance_execution_id)


def execute_stage_table_indexes_script(
    component: Component,
    db_config: DbConfig,
    instance_execution_id: str,
) -> None:
    """Execute SQL for queries and alias definitions of a component."""

    sql = generate_stage_table_indexes_script(
        component=component,
        instance_execution_id=instance_execution_id,
    )

    execute_sql_string(
        db_config=db_config,
        sql=sql,
    )
