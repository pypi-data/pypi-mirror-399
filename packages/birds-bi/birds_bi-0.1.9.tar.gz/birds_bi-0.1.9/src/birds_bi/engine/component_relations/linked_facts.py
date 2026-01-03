from birds_bi.repo.component import Component
from birds_bi.sql.joins import get_joins_from_sql


def get_unique_list_of_components(components: list[Component]) -> list[Component]:
    seen: set[tuple[str, str]] = set()
    result: list[Component] = []

    for component in components:
        key = (component.category, component.base_name)
        if key not in seen:
            seen.add(key)
            result.append(component)

    return result


def get_linked_facts(component: Component) -> list[Component]:
    linked_facts = []

    for fact in component._repo.get_components_from_category("fact"):
        if fact.manual_mode:
            for query in fact.queries:
                joins = get_joins_from_sql(query.query)
                for join in joins:
                    if (
                        join.table.lower().strip("").replace("[", "").replace("]", "")
                        == str(component).lower()
                    ):
                        linked_facts.append(fact)
        else:
            for dimension in fact.dimensions:
                if dimension.dimension.lower() == component.base_name.lower():
                    linked_facts.append(fact)
    unique_list = get_unique_list_of_components(linked_facts)
    return unique_list
