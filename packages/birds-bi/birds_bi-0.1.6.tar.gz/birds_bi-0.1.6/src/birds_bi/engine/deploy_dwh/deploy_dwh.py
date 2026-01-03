from birds_bi.db.models import DbConfig
from birds_bi.engine.deploy_dwh.deploy_component import deploy_component
from birds_bi.engine.deploy_dwh.deploy_staging import deploy_staging
from birds_bi.git.models import Changes
from birds_bi.repo.component import Component


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


def deploy_dwh_from_changes(changes: Changes, db_config: DbConfig) -> None:

    staging_components = []
    components = []

    if changes.deploy_dwh:
        for change in changes.components:
            if change.deploy_action == "staging":
                staging_components.append(change.component)
        for change in changes.components:
            if change.deploy_action == "components":
                components.append(change.component)

        staging_components = sort_components(staging_components)

        components = sort_components(
            get_unique_list_of_components(components=components)
        )

        for component in staging_components:
            deploy_staging(component=component, db_config=db_config)

        for component in components:
            deploy_component(component=component, db_config=db_config)
