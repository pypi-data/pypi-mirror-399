import sqlparse
from sqlparse.sql import Parenthesis


def find_subselects(token: Parenthesis) -> list[str]:
    subselects = []

    if isinstance(token, Parenthesis):
        inner = token.value[1:-1].strip()
        parsed_inner = sqlparse.parse(inner)
        if parsed_inner and parsed_inner[0].get_type() == "SELECT":
            subselects.append(inner)

    if hasattr(token, "tokens"):
        for t in token.tokens:
            subselects.extend(find_subselects(t))

    return subselects


def extract_sub_queries(sql: str) -> list[str]:
    token = sqlparse.parse(sql)[0]
    result = find_subselects(token)
    return result
