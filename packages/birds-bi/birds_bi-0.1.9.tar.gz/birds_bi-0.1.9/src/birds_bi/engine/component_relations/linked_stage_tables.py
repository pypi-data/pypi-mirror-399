from birds_bi.repo.component import Component
from birds_bi.sql.create_scripts import extract_create_sql
from birds_bi.sql.from_table import extract_from_table
from birds_bi.sql.main_select import extract_main_select


def get_unique_List_of_components(components: list[Component]) -> list[Component]:
    seen: set[tuple[str, str]] = set()
    result: list[Component] = []

    for component in components:
        key = (component.category, component.base_name)
        if key not in seen:
            seen.add(key)
            result.append(component)

    return result


def get_linked_stage_tables(component: Component) -> list[Component]:

    stage_tables = [
        table_definition.table_identifier.split(".", 1)[1].lower()
        for table_definition in component.table_definitions
    ]

    linked_stage_tables = []

    for fact in component._repo.get_components_from_category("fact"):
        for query in fact.queries:
            if fact.manual_mode:
                if query.name.endswith("function.sql") or query.name.endswith(
                    "function"
                ):
                    select = extract_create_sql(query.query)
            else:
                if query.query:
                    select = query.query
            main_select = extract_main_select(select)
            from_table = extract_from_table(main_select)
            if (
                from_table.table.lower().replace("[", "").replace("]", "")
                in stage_tables
            ):
                linked_stage_tables.append(fact)
    unique_List = get_unique_List_of_components(linked_stage_tables)
    return unique_List
