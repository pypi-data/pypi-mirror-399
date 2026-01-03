"""Data warehouse deployment utilities.

Provides functions to deploy components and staging tables to the data warehouse,
along with all deployment script generators.
"""

from . import deployment_scripts
from .deploy_component import deploy_component
from .deploy_staging import deploy_staging
from .deployment_scripts import (
    execute_add_dwh_component_script,
    execute_column_metadata_script,
    execute_deploy_script,
    execute_dwh_deployment_script,
    execute_fact_dimension_joins_script,
    execute_manual_mode_script,
    execute_post_deployment_script,
    execute_pre_deployment_script,
    execute_query_and_aliases_script,
    execute_query_columns_script,
    execute_stage_table_indexes_script,
    execute_start_logging_script,
    execute_stop_logging_script,
    execute_table_indexes_script,
    execute_validate_columns_script,
    execute_validate_query_script,
    generate_add_dwh_component_script,
    generate_column_metadata_script,
    generate_deploy_script,
    generate_dwh_deployment_script,
    generate_fact_dimension_joins_script,
    generate_manual_mode_script,
    generate_post_deployment_script,
    generate_pre_deployment_script,
    generate_query_and_aliases_script,
    generate_query_columns_script,
    generate_stage_table_indexes_script,
    generate_start_logging_script,
    generate_stop_logging_script,
    generate_table_indexes_script,
    generate_validate_columns_script,
    generate_validate_query_script,
)
from .models import DeployResult, StartLogging

__all__ = [
    # Submodule
    "deployment_scripts",
    # Main deployment functions
    "deploy_component",
    "deploy_staging",
    # Models
    "DeployResult",
    "StartLogging",
    # Generate functions
    "generate_add_dwh_component_script",
    "generate_column_metadata_script",
    "generate_deploy_script",
    "generate_dwh_deployment_script",
    "generate_fact_dimension_joins_script",
    "generate_manual_mode_script",
    "generate_post_deployment_script",
    "generate_pre_deployment_script",
    "generate_query_and_aliases_script",
    "generate_query_columns_script",
    "generate_stage_table_indexes_script",
    "generate_start_logging_script",
    "generate_stop_logging_script",
    "generate_table_indexes_script",
    "generate_validate_columns_script",
    "generate_validate_query_script",
    # Execute functions
    "execute_add_dwh_component_script",
    "execute_column_metadata_script",
    "execute_deploy_script",
    "execute_dwh_deployment_script",
    "execute_fact_dimension_joins_script",
    "execute_manual_mode_script",
    "execute_post_deployment_script",
    "execute_pre_deployment_script",
    "execute_query_and_aliases_script",
    "execute_query_columns_script",
    "execute_stage_table_indexes_script",
    "execute_start_logging_script",
    "execute_stop_logging_script",
    "execute_table_indexes_script",
    "execute_validate_columns_script",
    "execute_validate_query_script",
]
