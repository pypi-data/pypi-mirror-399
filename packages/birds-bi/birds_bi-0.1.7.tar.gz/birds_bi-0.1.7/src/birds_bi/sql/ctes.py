import sqlparse
from sqlparse.sql import Identifier, Parenthesis
from sqlparse.tokens import Comment, Keyword, Whitespace

from .models import Cte


def extract_ctes(sql: str) -> list[Cte]:

    statement = sqlparse.parse(sql)[0]

    ctes: list[Cte] = []

    # remove whitespace & comments at top level
    tokens = [
        t
        for t in statement.tokens
        if t.ttype not in Whitespace and t.ttype not in Comment
    ]

    # 1. find the WITH keyword (Keyword.CTE)
    with_idx = None
    for i, t in enumerate(tokens):
        # IMPORTANT: use "in Keyword", not "is Keyword"
        if t.ttype in Keyword and t.normalized.upper() == "WITH":
            with_idx = i
            break

    if with_idx is None:
        return ctes  # no CTEs found

    # 2. token after WITH should be IdentifierList or Identifier
    next_token = None
    for t in tokens[with_idx + 1 :]:
        if t.ttype not in Whitespace and t.ttype not in Comment:
            next_token = t
            break

    if isinstance(next_token, Identifier):
        idents = list(next_token.get_identifiers())
    elif isinstance(next_token, Identifier):
        idents = [next_token]
    else:
        idents = []

    # 3. pull out name + inner SELECT for each CTE
    for ident in idents:
        name = ident.get_name()  # e.g. CTE_OppurtunityCreationDate

        # find the (...) that contains the CTE body
        paren = next((t for t in ident.tokens if isinstance(t, Parenthesis)), None)
        if paren:
            # strip outer parentheses
            cte_sql = paren.value[1:-1].strip()
        else:
            cte_sql = str(ident).strip()

        cte = Cte(
            name=name,
            sql=cte_sql,
        )
        ctes.append(cte)

    return ctes
