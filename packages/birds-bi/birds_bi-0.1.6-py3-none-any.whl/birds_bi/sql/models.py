from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SqlBatch:
    index: int
    sql: str


@dataclass
class Cte:
    name: str
    sql: str


@dataclass
class JoinInfo:
    join_type: str  # e.g. "LEFT JOIN", "INNER JOIN", "JOIN"
    table: str  # raw table token as it appears (e.g. "[dbo].[stage_x]" or "stage_x")
    alias: str | None  # None if no alias detected
    on_parts: list[str]


@dataclass(frozen=True, slots=True)
class FromTable:
    schema: str | None
    table: str
    full_name: str
    alias: str | None
