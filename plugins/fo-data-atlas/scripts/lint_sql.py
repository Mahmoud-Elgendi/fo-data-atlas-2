"""Bounded static checks for Atlas SELECT SQL; never executes SQL or proves semantics."""
import argparse
import json
from pathlib import Path
import re
import sys

from atlas import load_schema

KEYWORDS = set("SELECT DISTINCT TOP FROM LEFT RIGHT FULL INNER OUTER CROSS JOIN ON WHERE AND OR NOT IS NULL AS WITH UNION ALL GROUP BY HAVING ORDER ASC DESC CASE WHEN THEN ELSE END IN EXISTS BETWEEN LIKE OVER PARTITION ROWS RANGE UNBOUNDED PRECEDING FOLLOWING CURRENT ROW OFFSET FETCH NEXT ONLY CAST CONVERT TRY_CAST TRY_CONVERT COALESCE NULLIF UPPER LOWER SUM COUNT COUNT_BIG MIN MAX AVG ABS ROUND DATEADD DATEDIFF YEAR MONTH DAY DECIMAL NUMERIC VARCHAR NVARCHAR INT BIGINT BIT DATE DATETIME2 ASC DESC".split())
MUTATIONS = set("INSERT UPDATE DELETE MERGE CREATE ALTER DROP TRUNCATE EXEC EXECUTE GRANT REVOKE DENY BACKUP RESTORE INTO".split())
TOKEN = re.compile(r"--[^\n]*|/\*.*?\*/|'(?:''|[^'])*'|\[(?:\]\]|[^\]])*\]|\"(?:\"\"|[^\"])*\"|[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|[^\s]", re.S)
METADATA_COLUMNS = {"OptionSetName", "Option", "IsUserLocalizedLabel", "LocalizedLabelLanguageCode",
                    "LocalizedLabel", "GlobalOptionSetName", "EntityName", "ExternalValue"}


def tokens(sql):
    return [m.group() for m in TOKEN.finditer(sql) if not m.group().startswith(("--", "/*"))]


def identifier(token):
    return token[1:-1].replace("]]", "]").replace('""', '"') if token.startswith(("[", '"')) else token


def check(sql, schema, require_company=False, link_sources=False, case_exceptions=None):
    # Explicit owner convention, granted only for exact identifiers in the supplied schema.
    exceptions = {('dbo', 'GlobalOptionsetMetadata'): METADATA_COLUMNS}
    for item in case_exceptions or []:
        key = (item['schema'], item['table'])
        columns = set(item.get('columns', []))
        if key not in schema or not columns.issubset(schema[key]):
            raise ValueError('Case exception is not present in exact target schema: ' + '.'.join(key))
        exceptions[key] = columns
    values = tokens(sql)
    aliases = {identifier(values[i + 1]) for i, token in enumerate(values[:-1]) if token.upper() == "AS"}
    issues, sources = [], []
    depth, depths = 0, []
    for token in values:
        if token == ")": depth -= 1
        depths.append(depth)
        if token == "(": depth += 1
    for i, token in enumerate(values):
        bare = identifier(token)
        quoted = token.startswith(("[", '"', "'"))
        qualified = (i > 0 and values[i - 1] == ".") or (i + 1 < len(values) and values[i + 1] == ".")
        alias = i > 0 and values[i - 1].upper() == "AS"
        if not quoted and not qualified and not alias and bare not in aliases:
            if token.upper() in MUTATIONS:
                issues.append("Only SELECT queries are supported; found " + token)
            if token.upper() in KEYWORDS and token != token.upper():
                issues.append("Uppercase SQL keyword/function required: " + token)
        if token.upper() not in {"FROM", "JOIN"} or i + 3 >= len(values): continue
        if values[i + 2] != ".":
            if values[i + 1] != "(": issues.append("Review unqualified source or CTE: " + values[i + 1])
            continue
        s, table = identifier(values[i + 1]), identifier(values[i + 3])
        key = (s, table)
        if (s != s.lower() or table != table.lower()) and key not in exceptions:
            issues.append("Lowercase physical source required: " + s + "." + table)
        if key not in schema: issues.append("Source absent from exact target schema: " + s + "." + table)
        j = i + 4
        if j < len(values) and values[j].upper() == "AS": j += 1
        candidate = identifier(values[j]) if j < len(values) else table
        aliasname = candidate if re.fullmatch(r"\w+", candidate) and candidate.upper() not in KEYWORDS else table
        before = [v.upper() for v in values[max(0, i - 2):i]]
        nullable = token.upper() == "JOIN" and "LEFT" in before
        sources.append({"schema": s, "table": table, "alias": aliasname, "depth": depths[i], "left_join": nullable})
    for source in sources:
        cols = schema.get((source["schema"], source["table"]), {})
        if link_sources and any(c.lower() == "isdelete" and c != "IsDelete" for c in cols):
            issues.append("Resolve target deletion-column casing; the required spelling is IsDelete: " + source["alias"])
        for i in range(len(values) - 2):
            if identifier(values[i]) != source["alias"] or values[i + 1] != ".": continue
            col = identifier(values[i + 2])
            if col == "*":
                issues.append("Confirm an explicit field list instead of alias.*")
            elif col not in cols:
                issues.append("Column absent from exact target schema: " + source["alias"] + "." + col)
            elif col != col.lower() and col != "IsDelete" and col not in exceptions.get((source['schema'], source['table']), set()):
                issues.append("Lowercase physical column required: " + col)
        if link_sources and "IsDelete" in cols:
            filters = []
            for i in range(len(values) - 4):
                if [identifier(v) for v in values[i:i + 5]] == [source["alias"], ".", "IsDelete", "IS", "NULL"] and depths[i] == source["depth"]:
                    filters.append(i)
            if not filters: issues.append("Missing qualified IsDelete IS NULL filter for " + source["alias"])
            if source["left_join"]:
                for i in filters:
                    prior = [v.upper() for n, v in enumerate(values[:i]) if depths[n] == source["depth"] and v.upper() in {"ON", "WHERE", "HAVING"}]
                    if prior and prior[-1] != "ON": issues.append("LEFT JOIN deletion filter must stay in ON/subquery: " + source["alias"])
    if require_company:
        compact = " ".join(values)
        if not re.search(r"UPPER \( (?:\w+ \. )?dataareaid \) AS Company\b", compact):
            issues.append("Required output: UPPER(dataareaid) AS Company (qualification allowed)")
    if not any(v.upper() == "SELECT" for v in values): issues.append("No SELECT query found; this may be a blocked scaffold")
    return {"issues": sorted(set(issues)), "sources": sources, "passed": not issues,
            "scope": "Bounded checks for schema-qualified sources and qualified columns; CTEs/complex scopes need review. Not a SQL parser or business validation.",
            "runtime_validated": False, "business_reconciled": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql", type=Path); parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--require-company", action="store_true"); parser.add_argument("--link-sources", action="store_true")
    parser.add_argument("--project", type=Path, help="Read explicit identifier_case_exceptions from .fo-data-atlas/project.json.")
    args = parser.parse_args()
    try:
        exceptions = None
        if args.project:
            config = json.loads((args.project / '.fo-data-atlas' / 'project.json').read_text(encoding='utf-8-sig'))
            exceptions = config.get('identifier_case_exceptions', [])
        result = check(args.sql.read_text(encoding="utf-8-sig"), load_schema(args.schema), args.require_company, args.link_sources, exceptions)
        print(json.dumps(result, indent=2)); return 0 if result["passed"] else 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())
