import re


def extract_create_sql(script: str | None) -> str:
    """
    Returns the body of a CREATE VIEW / CREATE FUNCTION script:
    - For VIEW: the SELECT (everything after AS)
    - For FUNCTION: everything after AS (e.g., RETURNS ... AS BEGIN ... / RETURN ...)
    Stops at GO or end-of-file.
    """
    if not script:
        return ""

    script = script.replace("\r\n", "\n")

    # 1) Extract CREATE VIEW/FUNCTION block (including its header)
    create_block_pattern = re.compile(
        r"(?is)\bCREATE\s+(VIEW|FUNCTION)\b[\s\S]*?(?=^\s*GO\s*$|\Z)", re.MULTILINE
    )
    m = create_block_pattern.search(script)
    if not m:
        return ""

    create_block = m.group(0).strip()

    # Remove a trailing GO if it somehow got included
    create_block = re.sub(r"(?im)^\s*GO\s*$", "", create_block).strip()

    # 2) Return everything after AS
    # (Use a word-boundary AS match, on its own token, case-insensitive)
    as_split = re.split(r"(?is)\bAS\b", create_block, maxsplit=1)
    if len(as_split) < 2:
        # No AS found; return the whole block (or "" depending on your preference)
        return create_block

    body = as_split[1].strip()

    # Optional: remove a leading BEGIN for functions if you only want inner statements
    # body = re.sub(r'(?is)^\s*BEGIN\b', '', body).strip()

    return body
