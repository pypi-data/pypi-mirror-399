"""SQL parsing and manipulation utilities for Birds BI.

Provides tools for splitting SQL scripts into batches, extracting query components,
and analyzing SQL structure.
"""

from .create_scripts import extract_create_sql
from .ctes import extract_ctes
from .from_table import extract_from_table
from .joins import get_joins_from_sql
from .main_select import extract_main_select
from .models import Cte, FromTable, JoinInfo, SqlBatch
from .split_sql_scripts import split_sql_batches
from .sub_queries import extract_sub_queries

__all__ = [
    # Models
    "Cte",
    "FromTable",
    "JoinInfo",
    "SqlBatch",
    # Functions
    "extract_create_sql",
    "extract_ctes",
    "extract_from_table",
    "extract_main_select",
    "extract_sub_queries",
    "get_joins_from_sql",
    "split_sql_batches",
]
