from typing import Literal

from birds_bi.db.models import DbConfig
from birds_bi.engine.deploy_dwh.deployment_scripts import (
    execute_add_dwh_component_script,
    execute_column_metadata_script,
    execute_deploy_script,
    execute_stage_table_indexes_script,
    execute_start_logging_script,
    execute_stop_logging_script,
)
from birds_bi.repo.component import Component


def deploy_staging(component: Component, db_config: DbConfig) -> None:

    error = None
    status: Literal["S", "F"] = "S"
    load_type = component.load_type

    logging = execute_start_logging_script(
        component=component,
        db_config=db_config,
    )
    try:
        component_id = execute_add_dwh_component_script(
            component=component,
            load_type=load_type,
            instance_execution_id=logging.instance_execution_id,
            db_config=db_config,
        )

        execute_column_metadata_script(
            component=component,
            instance_execution_id=logging.instance_execution_id,
            db_config=db_config,
        )

        execute_stage_table_indexes_script(
            component=component,
            instance_execution_id=logging.instance_execution_id,
            db_config=db_config,
        )

        execute_deploy_script(
            component_execution_id=logging.component_execution_id,
            component_id=component_id,
            instance_execution_id=logging.instance_execution_id,
            deploy_action="staging",
            db_config=db_config,
        )

    except Exception as e:
        status = "F"
        error = e

    execute_stop_logging_script(
        component=component,
        instance_execution_id=logging.instance_execution_id,
        component_execution_id=logging.component_execution_id,
        status=status,
        db_config=db_config,
    )

    if error:
        raise Exception(error)
