import sqlparse
from sqlparse import tokens as T


def extract_main_select(sql: str) -> str | None:
    statements = sqlparse.parse(sql)
    if not statements:
        return None

    stmt = statements[0]
    tokens = list(stmt.tokens)

    start_idx = None
    paren_depth = 0

    for i, tok in enumerate(tokens):
        # Track top-level depth (ignore SELECTs inside parentheses)
        if tok.match(T.Punctuation, "("):
            paren_depth += 1
        elif tok.match(T.Punctuation, ")"):
            paren_depth = max(paren_depth - 1, 0)

        if paren_depth != 0:
            continue

        # Skip whitespace/comments but DO NOT strip them from output reconstruction
        if tok.is_whitespace or tok.ttype in (
            T.Newline,
            T.Comment,
            T.Comment.Single,
            T.Comment.Multiline,
        ):
            continue

        # Match SELECT robustly across sqlparse versions
        if tok.match(T.DML, "SELECT") or tok.match(T.Keyword, "SELECT"):
            start_idx = i
            break

    if start_idx is None:
        return None

    # Preserve original whitespace/newlines exactly
    return "".join(str(t) for t in tokens[start_idx:])
