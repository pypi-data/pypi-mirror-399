from dataclasses import dataclass
from typing import Literal

from birds_bi.repo.component import Component


@dataclass
class Change:
    deploy_action: Literal["staging", "components"]
    component: Component


@dataclass
class Changes:
    deploy_dwh: bool
    deploy_tabular: bool
    components: list[Change]
