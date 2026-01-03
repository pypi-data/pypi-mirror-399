from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

from birds_bi.repo.models import (
    Column,
    DatabaseObject,
    DatabaseObjectColumn,
    Dimension,
    DimensionJoin,
    DwhDeploymentScript,
    PostDeploymentScript,
    PreDeploymentScript,
    QueryAlias,
    QueryColumn,
    QueryInformation,
    QueryLoadProcedures,
    TableDefinition,
    TableDefinitionColumn,
    TableIndex,
)

if TYPE_CHECKING:
    from birds_bi.repo.repository import Repository

Category = Literal["help", "dim", "fact"]


class Component:
    def __init__(self, *, repo: Repository, category: Category, base_name: str) -> None:
        self._repo: Repository = repo
        self.base_name: str = base_name
        self.category: Category = category
        self.database_object = self.get_database_object()
        self.load_procedures = self.get_load_procedures()
        self.queries = self.get_queries()
        self.query_columns = self.get_query_columns()
        self.dimensions = self.get_dimensions()
        self.load_type = self.get_load_type()
        self.manual_mode: bool = self.get_manual_mode()
        self.process_type = self.get_process_type()
        self.is_customized = self.get_is_customized()
        self.table_indexes = self.get_table_indexes()

    def __str__(self) -> str:
        return f"{self.category}.{self.base_name}"

    def __repr__(self) -> str:
        return f"{self.category}.{self.base_name}"

    @property
    def path(self) -> Path:
        # content/<category>/<component_component>
        return self._repo.content_path / self.category / self.base_name

    @cached_property
    def component_definition(self) -> dict[str, Any]:
        path: Path = (
            self._repo.content_path
            / self.category
            / self.base_name
            / "deployment"
            / "component_definition.json"
        )

        if not path.is_file():
            raise FileNotFoundError(f"Component definition not found: {path}")

        with path.open(encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))

    def get_load_type(self) -> str:
        return str(self.component_definition.get("load_type", 0))

    def get_manual_mode(self) -> bool:
        return bool(self.component_definition.get("manual_mode", False))

    def get_process_type(self) -> int:
        return int(self.component_definition.get("process_type", 0))

    def get_is_customized(self) -> int:
        return int(self.component_definition.get("is_customized", 0))

    def get_database_object(self) -> DatabaseObject:
        database_object = self.component_definition.get("database_object", {})
        return DatabaseObject(
            table_identifier=database_object.get("table_identifier", ""),
            columns=self.get_database_object_columns(),
            indexes=self.get_table_indexes(),
        )

    def get_database_object_columns(self) -> list[DatabaseObjectColumn]:
        database_object_columns = self.component_definition.get(
            "database_object", {}
        ).get("columns", [])

        return [
            DatabaseObjectColumn(
                column_name=database_object_column.get("column_name"),
                data_type=database_object_column.get("data_type"),
                nullable=database_object_column.get("nullable"),
                business_key=database_object_column.get("business_key"),
            )
            for database_object_column in database_object_columns
        ]

    def get_table_indexes(self) -> list[TableIndex]:
        table_indexes = self.component_definition.get("database_object", {}).get(
            "indexes"
        )
        return [
            TableIndex(
                name=index.get("name"),
                type=index.get("type"),
                columns=index.get("columns", []),
                included_columns=index.get("included_columns", []),
                fill_factor=index.get("fill_factor"),
                is_unique=index.get("is_unique"),
            )
            for index in table_indexes
        ]

    def get_load_procedures(self) -> list[QueryLoadProcedures]:
        load_procedures = self.component_definition.get("load_procedures", [])

        return [
            QueryLoadProcedures(
                sequence=load_procedure.get("sequence"),
                identifier=load_procedure.get("identifier"),
            )
            for load_procedure in load_procedures
        ]

    def get_queries(self) -> list[QueryInformation]:

        folder = (
            self.path
            if self.get_manual_mode()
            else self.path / "deployment" / "generated"
        )

        query_files = sorted(
            p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".sql"
        )

        if self.get_manual_mode():
            return [
                QueryInformation(
                    name=p.name.removesuffix(".sql"),
                    select_file_path=p.name,
                    sequence=-1,
                    aliases=[],
                    query=p.read_text(encoding="utf-8"),
                )
                for p in query_files
            ]

        queries = {p.name: p.read_text(encoding="utf-8") for p in query_files}
        query_information = self.component_definition.get("queries", [])

        return [
            QueryInformation(
                name=query.get("name"),
                select_file_path=query.get("select_file_path"),
                sequence=query.get("sequence"),
                aliases=[
                    QueryAlias(
                        name=alias.get("name"),
                        type=alias.get("type"),
                        index=index,
                    )
                    for index, alias in enumerate(query.get("aliases", []))
                ],
                query=queries.get(query.get("select_file_path", ""), ""),
            )
            for query in query_information
        ]

    def get_query_columns(self) -> list[QueryColumn]:
        query_columns = self.component_definition.get("query_columns", [])

        return [
            QueryColumn(
                column_name=query_column.get("column_name", ""),
                data_type_full=query_column.get("data_type_full", ""),
                type=query_column.get("type", ""),
            )
            for query_column in query_columns
        ]

    def get_dimensions(self) -> list[Dimension]:

        dimensions = self.component_definition.get("dimensions", [])

        if self.get_manual_mode() or self.category == "dim":
            return []

        return [
            Dimension(
                dimension=dimension.get("dimension"),
                role_playing=dimension.get("role_playing"),
                dimension_joins=[
                    DimensionJoin(
                        delta_column=dimension_join.get("delta_column"),
                        dimension_column=dimension_join.get("dimension_column"),
                    )
                    for dimension_join in dimension.get("dimension_joins", [])
                ],
            )
            for dimension in dimensions
        ]

    @property
    def columns(self) -> list[Column]:
        database_object = self.component_definition.get("database_object") or {}
        database_object_columns = database_object.get("columns", [])
        query_columns = self.component_definition.get("query_columns", [])

        nullable_by_name = {
            column.get("column_name"): column.get("nullable")
            for column in database_object_columns
            if column.get("column_name") is not None
        }

        return [
            Column(
                index=i,
                column_name=column.get("column_name"),
                data_type_full=column.get("data_type_full"),
                type=column.get("type"),
                nullable=(
                    False
                    if self.manual_mode
                    else bool(nullable_by_name.get(column.get("column_name"), False))
                ),
            )
            for i, column in enumerate(query_columns, start=1)
        ]

    @property
    def table_definitions(self) -> list[TableDefinition]:
        table_definition_path = Path(self.path / "deployment")
        table_definitions = []

        for table_definition_file in table_definition_path.iterdir():
            if (
                table_definition_file.is_file()
                and table_definition_file.stem.lower().startswith("table_definition")
            ):
                payload = json.loads(table_definition_file.read_text(encoding="utf-8"))

                table_definitions.append(
                    {
                        "schema": table_definition_file.stem.split(".")[-1],
                        "tables": payload.get("tables", []),
                    }
                )

        return [
            TableDefinition(
                schema=str(table_definition.get("schema") or ""),
                table_identifier=str(table.get("table_identifier") or ""),
                columns=[
                    TableDefinitionColumn(
                        column_name=column.get("column_name"),
                        data_type=column.get("data_type"),
                        character_maximum_length=column.get("character_maximum_length"),
                        numeric_precision=column.get("numeric_precision"),
                        numeric_scale=column.get("numeric_scale"),
                        nullable=column.get("nullable"),
                        business_key=column.get("business_key"),
                    )
                    for column in (table.get("columns") or [])
                ],
            )
            for table_definition in table_definitions
            for table in (table_definition.get("tables") or [])
        ]

    @property
    def pre_deployment_scripts(self) -> list[PreDeploymentScript]:
        pre_deployment_path = Path(self.path / "pre_deployment")

        if not pre_deployment_path.exists():
            return []

        return [
            PreDeploymentScript(
                name=script_file.name,
                file_path=script_file,
                sql=script_file.read_text(encoding="utf-8"),
                index=index,
            )
            for index, script_file in enumerate(sorted(pre_deployment_path.iterdir()))
            if script_file.is_file() and script_file.suffix.lower() == ".sql"
        ]

    @property
    def post_deployment_scripts(self) -> list[PostDeploymentScript]:
        post_deployment_path = Path(self.path / "post_deployment")

        if not post_deployment_path.exists():
            return []

        return [
            PostDeploymentScript(
                name=script_file.name,
                file_path=script_file,
                sql=script_file.read_text(encoding="utf-8"),
                index=index,
            )
            for index, script_file in enumerate(sorted(post_deployment_path.iterdir()))
            if script_file.is_file() and script_file.suffix.lower() == ".sql"
        ]

    @property
    def dwh_deployment_scripts(self) -> list[DwhDeploymentScript]:
        dwh_deployment_path = Path(self.path)

        return [
            DwhDeploymentScript(
                name=script_file.name,
                file_path=script_file,
                sqlpath=f"{self.category}\\{self.base_name}\\{script_file.name}",
                sql=script_file.read_text(encoding="utf-8"),
                index=index,
            )
            for index, script_file in enumerate(sorted(dwh_deployment_path.iterdir()))
            if script_file.is_file() and script_file.suffix.lower() == ".sql"
        ]
