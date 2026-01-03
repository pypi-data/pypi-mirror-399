from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

from birds_bi.repo.component import Component
from birds_bi.repo.repository import Repository

from .models import Change, Changes


def get_changes_from_file(repo: Repository, changed_files_path: str | Path) -> Changes:
    changed_files_path = (
        Path(str(changed_files_path).strip()).expanduser().resolve(strict=False)
    )

    changes = changed_files_path.read_text(encoding="utf-8").splitlines()

    deploy_dwh = False
    deploy_tabular = False
    components: list[Change] = []
    seen: set[tuple[str, str, str]] = set()

    for line in changes:
        parts = line.split("/")
        if len(parts) < 2:
            continue

        root = parts[0]

        if root == "content" and parts[2] != "README.md":
            deploy_dwh = True

            deploy_action: Literal["staging", "components"] = (
                "staging"
                if len(parts) > 4 and parts[4].startswith("table_definitions")
                else "components"
            )

            if parts[1] not in ("help", "dim", "fact"):
                continue
            category = cast(Literal["help", "dim", "fact"], parts[1])
            component = parts[2]

            seen_key = (category, component, deploy_action)

            if seen_key not in seen:
                components.append(
                    Change(
                        component=Component(
                            repo=repo,
                            category=category,
                            base_name=component,
                        ),
                        deploy_action=deploy_action,
                    )
                )
            else:
                seen.add(seen_key)

        elif root == "tabular":
            deploy_tabular = True

    return Changes(
        deploy_dwh=deploy_dwh,
        deploy_tabular=deploy_tabular,
        components=components,
    )
