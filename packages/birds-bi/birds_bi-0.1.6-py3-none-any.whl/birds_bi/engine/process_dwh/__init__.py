"""Data warehouse processing utilities.

Provides functions to execute DWH processing procedures for components.
"""

from .process_dwh_component import process_component, process_component_list

__all__ = [
    "process_component",
    "process_component_list",
]
