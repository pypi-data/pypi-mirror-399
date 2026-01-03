from __future__ import annotations

import re

from .models import JoinInfo  # ON clause split into parts between ANDs

_TABLE_PART = r"(?:\[[^\]]+\]|\w+)"
_TABLE_TOKEN = rf"{_TABLE_PART}(?:\.{_TABLE_PART})*"

_JOIN_WITH_ALIAS_RE = re.compile(
    rf"(?i)(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)?\s*JOIN\s+({_TABLE_TOKEN})(?:\s+AS)?\s+(\w+)"
)
_JOIN_NO_ALIAS_RE = re.compile(
    rf"(?i)(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)?\s*JOIN\s+({_TABLE_TOKEN})"
)

_JOIN_TYPE_RE = re.compile(
    r"(?i)\b(LEFT|RIGHT|FULL|INNER|OUTER|CROSS)\s*JOIN\b|\bJOIN\b"
)
_ON_RE = re.compile(r"(?i)\bON\s+")
_KEYWORD_START_RE = re.compile(
    r"^\s*(JOIN|LEFT|RIGHT|FULL|INNER|OUTER|CROSS|WHERE|GROUP|ORDER|UNION|FROM)\b",
    re.IGNORECASE,
)


def get_joins_from_sql(sql: str) -> list[JoinInfo]:
    lines: list[str] = sql.split("\n")
    joins: list[JoinInfo] = []
    i: int = 0

    while i < len(lines):
        line: str = lines[i]

        # Match JOIN + table + alias (preferred), otherwise JOIN + table without alias
        join_match = _JOIN_WITH_ALIAS_RE.search(line)

        table_name: str | None = None
        alias: str | None = None
        join_start: int | None = None
        join_end: int | None = None

        if join_match:
            if "--" in line[: join_match.start()] or line.strip().startswith("--"):
                i += 1
                continue

            table_name = join_match.group(1)
            alias = join_match.group(2)
            join_start = join_match.start()
            join_end = join_match.end()
        else:
            join_match2 = _JOIN_NO_ALIAS_RE.search(line)
            if not join_match2:
                i += 1
                continue

            if "--" in line[: join_match2.start()] or line.strip().startswith("--"):
                i += 1
                continue

            table_name = join_match2.group(1)
            alias = None
            join_start = join_match2.start()
            join_end = join_match2.end()

        join_segment: str = line[join_start:join_end]
        jt_match = _JOIN_TYPE_RE.search(join_segment)
        join_type: str = jt_match.group(0).upper() if jt_match else "JOIN"
        join_type = re.sub(r"\s+", " ", join_type).strip()

        # Find ON clause - it might be on same line or next lines
        on_match = _ON_RE.search(line[join_end:])
        on_start_line: int = i
        on_start_col: int | None = (
            join_end + on_match.start() + len("ON ") if on_match else None
        )

        if not on_match:
            j: int = i + 1
            found_on: bool = False

            while j < len(lines) and not found_on:
                next_line: str = lines[j]
                stripped_next: str = next_line.strip()

                if stripped_next.startswith("--"):
                    j += 1
                    continue

                code_part: str = next_line
                if "--" in next_line:
                    comment_pos: int = next_line.find("--")
                    code_part = next_line[:comment_pos]

                on_match2 = _ON_RE.search(code_part)
                if on_match2:
                    on_start_line = j
                    on_start_col = on_match2.end()  # after "ON "
                    found_on = True
                    break

                j += 1

            if not found_on:
                joins.append(
                    JoinInfo(
                        join_type=join_type, table=table_name, alias=alias, on_parts=[]
                    )
                )
                i += 1
                continue

        # Collect ON clause content (from ON to next keyword, skipping comments)
        on_lines: list[tuple[int, str]] = []
        current_line_idx: int = on_start_line

        if on_start_line == i:
            remaining = line[join_end:]
            on_match_in_line = _ON_RE.search(remaining)
            if on_match_in_line:
                on_content_start: int = join_end + on_match_in_line.end()
                on_line_content: str = line[on_content_start:]
                if on_line_content.strip():
                    on_lines.append((i, on_line_content))
                current_line_idx = i + 1
            else:
                current_line_idx = i + 1
        else:
            on_line: str = lines[on_start_line]
            on_line_code: str = (
                on_line.split("--", 1)[0] if "--" in on_line else on_line
            )

            on_match_in_line = _ON_RE.search(on_line_code)
            if on_match_in_line:
                on_content_start = on_match_in_line.end()
                remaining2 = on_line[on_content_start:]
                if remaining2.strip():
                    on_lines.append((on_start_line, remaining2))
            else:
                remaining2 = (
                    on_line[on_start_col:]
                    if on_start_col is not None and on_start_col < len(on_line)
                    else ""
                )
                if remaining2.strip():
                    on_lines.append((on_start_line, remaining2))

            current_line_idx = on_start_line + 1

        j = current_line_idx
        found_end: bool = False

        while j < len(lines) and not found_end:
            next_line = lines[j]
            stripped_next = next_line.strip()

            if stripped_next and not stripped_next.startswith("--"):
                if "--" in stripped_next:
                    code_part = stripped_next.split("--", 1)[0].strip()
                    if code_part and _KEYWORD_START_RE.match(code_part):
                        found_end = True
                        break
                    on_lines.append((j, next_line))
                else:
                    if _KEYWORD_START_RE.match(stripped_next):
                        found_end = True
                        break
                    on_lines.append((j, next_line))
            else:
                on_lines.append((j, next_line))

            j += 1

        on_content: str = (
            "\n".join(content for _, content in on_lines) if on_lines else ""
        )
        raw_parts: list[str] = (
            re.split(r"(?i)\bAND\b", on_content) if on_content else []
        )
        on_parts: list[str] = [part.strip() for part in raw_parts if part.strip()]

        joins.append(
            JoinInfo(
                join_type=join_type, table=table_name, alias=alias, on_parts=on_parts
            )
        )

        i = on_lines[-1][0] + 1 if on_lines else i + 1

    return joins
