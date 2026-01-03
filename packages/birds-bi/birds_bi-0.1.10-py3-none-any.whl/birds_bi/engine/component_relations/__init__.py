"""Component relationship utilities for Birds BI.

Provides functions to discover relationships between data warehouse components,
such as which facts link to dimensions and which facts use specific stage tables.
"""

from .linked_facts import get_linked_facts
from .linked_stage_tables import get_linked_stage_tables

__all__ = [
    "get_linked_facts",
    "get_linked_stage_tables",
]
