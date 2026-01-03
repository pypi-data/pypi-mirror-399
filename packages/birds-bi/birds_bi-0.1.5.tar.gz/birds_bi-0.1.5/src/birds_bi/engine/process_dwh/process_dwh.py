from birds_bi.db.models import DbConfig
from birds_bi.engine.component_relations.linked_facts import get_linked_facts
from birds_bi.engine.component_relations.linked_stage_tables import (
    get_linked_stage_tables,
)
from birds_bi.git.models import Changes
from birds_bi.repo.component import Component

from .process_dwh_component import process_component_list


def sort_components(components: list[Component]) -> list[Component]:
    order = ["help", "dim", "fact"]

    rank = {value: i for i, value in enumerate(order)}

    sorted_components = sorted(components, key=lambda t: rank.get(t.category, 10**9))

    return sorted_components


def get_unique_list_of_components(components: list[Component]) -> list[Component]:
    seen: set[tuple[str, str]] = set()
    result: list[Component] = []

    for component in components:
        key = (component.category, component.base_name)
        if key not in seen:
            seen.add(key)
            result.append(component)

    return result


def process_dwh_from_changes(changes: Changes, db_config: DbConfig) -> None:

    staging_components = []
    components = []

    if changes.deploy_dwh:
        for change in changes.components:
            if change.deploy_action == "staging":
                staging_components.append(change.component)
        for change in changes.components:
            if change.deploy_action == "components":
                components.append(change.component)

        for component in components:
            if component.category == "dim":
                linked_facts = get_linked_facts(component=component)
                for fact in linked_facts:
                    components.append(fact)

        for component in staging_components:
            linked_facts = get_linked_stage_tables(component=component)
            for fact in linked_facts:
                components.append(fact)

        components = get_unique_list_of_components(components=components)

        process_component_list(
            component_list=staging_components,
            db_config=db_config,
            process_action="staging",
            load_type=0,
        )

        process_component_list(
            component_list=components,
            db_config=db_config,
            process_action="components",
            load_type=0,
        )
