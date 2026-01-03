from __future__ import annotations

from .models import FromTable


def extract_from_table(tsql: str | None) -> FromTable:
    if not tsql:  # covers None and ""
        return FromTable(
            schema="N/A",
            table="N/A",
            full_name="N/A",
            alias="N/A",
        )

    sql = _strip_comments(tsql)
    if not sql:
        return FromTable(
            schema="N/A",
            table="N/A",
            full_name="N/A",
            alias="N/A",
        )

    pos = _find_from(sql)
    if pos is None:
        return FromTable(
            schema="N/A",
            table="N/A",
            full_name="N/A",
            alias="N/A",
        )

    parts, i = _read_qualified_ident(sql, pos)
    if not parts:
        return FromTable(
            schema="N/A",
            table="N/A",
            full_name="N/A",
            alias="N/A",
        )

    alias, _ = _read_optional_alias(sql, i)

    schema, table = _schema_table_from_parts(parts)
    full_name = ".".join(parts)
    return FromTable(schema=schema, table=table, full_name=full_name, alias=alias)


# -----------------------------
# Minimal helpers
# -----------------------------


def _strip_comments(sql: str) -> str:
    if not sql:
        return ""
    out: list[str] = []
    i = 0
    n = len(sql)
    in_string = False

    while i < n:
        ch = sql[i]

        if ch == "'":
            out.append(ch)
            i += 1
            in_string = not in_string
            while in_string and i < n:
                out.append(sql[i])
                if sql[i] == "'":
                    if i + 1 < n and sql[i + 1] == "'":  # escaped ''
                        out.append(sql[i + 1])
                        i += 2
                        continue
                    in_string = False
                i += 1
            continue

        if not in_string and i + 1 < n and sql[i : i + 2] == "--":
            i += 2
            while i < n and sql[i] not in "\r\n":
                i += 1
            continue

        if not in_string and i + 1 < n and sql[i : i + 2] == "/*":
            i += 2
            while i + 1 < n and sql[i : i + 2] != "*/":
                i += 1
            i = min(i + 2, n)
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def _find_from(sql: str) -> int | None:
    """Return index just after the top-level FROM keyword."""
    depth = 0
    i = 0
    n = len(sql)

    def is_word_char(c: str) -> bool:
        return c.isalnum() or c in {"_", "#", "@"}

    while i < n:
        ch = sql[i]
        if ch == "(":
            depth += 1
            i += 1
            continue
        if ch == ")":
            depth = max(0, depth - 1)
            i += 1
            continue

        if depth == 0 and sql[i : i + 4].lower() == "from":
            before_ok = i == 0 or not is_word_char(sql[i - 1])
            after_ok = i + 4 >= n or not is_word_char(sql[i + 4])
            if before_ok and after_ok:
                return i + 4
        i += 1

    return None


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i].isspace():
        i += 1
    return i


def _read_bracketed(s: str, i: int) -> tuple[str | None, int]:
    # expects '['
    j = s.find("]", i + 1)
    if j == -1:
        return None, i
    return s[i + 1 : j], j + 1


def _read_quoted(s: str, i: int) -> tuple[str | None, int]:
    # expects '"'
    j = s.find('"', i + 1)
    if j == -1:
        return None, i
    return s[i + 1 : j], j + 1


def _read_bare(s: str, i: int) -> tuple[str, int]:
    j = i
    while j < len(s) and (not s[j].isspace()) and s[j] not in ".,;()":
        j += 1
    return s[i:j], j


def _read_qualified_ident(sql: str, start: int) -> tuple[list[str], int]:
    """
    Read <part>(.<part>)* where part can be:
      - [bracketed identifier]
      - "quoted identifier"
      - bare identifier
    Returns (parts, next_index).
    """
    i = _skip_ws(sql, start)
    parts: list[str] = []

    while i < len(sql):
        if sql[i] == "[":
            part, i2 = _read_bracketed(sql, i)
            if part is None:
                break
            parts.append(part.strip())
            i = i2
        elif sql[i] == '"':
            part, i2 = _read_quoted(sql, i)
            if part is None:
                break
            parts.append(part.strip())
            i = i2
        else:
            part, i2 = _read_bare(sql, i)
            part = part.strip()
            if not part:
                break
            parts.append(part)
            i = i2

        i = _skip_ws(sql, i)

        # Continue only if next non-ws char is a dot
        if i < len(sql) and sql[i] == ".":
            i += 1
            i = _skip_ws(sql, i)
            continue

        break

    return parts, i


def _read_optional_alias(sql: str, start: int) -> tuple[str | None, int]:
    i = _skip_ws(sql, start)

    # optional AS
    if sql[i : i + 2].lower() == "as" and (i + 2 == len(sql) or sql[i + 2].isspace()):
        i = _skip_ws(sql, i + 2)

    # alias token (stop at punctuation)
    if i >= len(sql) or sql[i] in ",;()":
        return None, i

    if sql[i] == "[":
        alias, i2 = _read_bracketed(sql, i)
        return (alias.strip() if alias else None), i2

    if sql[i] == '"':
        alias, i2 = _read_quoted(sql, i)
        return (alias.strip() if alias else None), i2

    alias, i2 = _read_bare(sql, i)
    alias = alias.strip()
    if not alias:
        return None, i
    # Don’t treat clause keywords as alias
    if alias.lower() in {
        "where",
        "join",
        "left",
        "right",
        "inner",
        "outer",
        "full",
        "cross",
        "group",
        "order",
        "having",
    }:
        return None, i
    return alias, i2


def _schema_table_from_parts(parts: list[str]) -> tuple[str | None, str]:
    # table only
    if len(parts) == 1:
        return None, parts[0]
    # schema.table or db.schema.table -> schema, table
    return parts[-2], parts[-1]
