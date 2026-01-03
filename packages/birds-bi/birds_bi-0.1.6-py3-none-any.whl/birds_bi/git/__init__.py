"""Git integration for Birds BI.

Provides tools for detecting changes in a Birds BI repository and 
determining which components need to be deployed.
"""

from .changes import get_changes_from_file
from .models import Change, Changes

__all__ = [
    "Change",
    "Changes",
    "get_changes_from_file",
]
