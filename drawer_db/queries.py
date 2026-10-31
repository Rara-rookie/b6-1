import sqlite3

from .db import exec_script, run_query
from .resources import queries_sql


class QueryItem:
    def __init__(self, number: int, description: str, sql: str):
        self.number = number
        self.description = description
        self.sql = sql


def parse_queries(queries_sql_text: str) -> list[QueryItem]:
    items: list[QueryItem] = []
    lines = queries_sql_text.splitlines()
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()

        if not stripped:
            index += 1
            continue

        if not stripped.startswith("--"):
            index += 1
            continue

        description = stripped[2:].strip()
        index += 1

        sql_lines: list[str] = []
        while index < len(lines):
            raw_line = lines[index]
            current = raw_line.strip()

            if not current:
                if sql_lines:
                    sql_lines.append(raw_line)
                index += 1
                continue

            if current.startswith("--") and not sql_lines:
                break

            sql_lines.append(raw_line)
            if current.endswith(";"):
                index += 1
                break
            index += 1

        sql = "\n".join(sql_lines).strip()
        if sql:
            items.append(QueryItem(len(items) + 1, description, sql))

    return items


def format_result(columns: list[str], rows: list[tuple]) -> str:
    if not columns:
        return "(결과 없음)"

    str_rows = [[("NULL" if value is None else str(value)) for value in row] for row in rows]
    widths = [len(column) for column in columns]

    for row in str_rows:
        for index, value in enumerate(row):
            if index < len(widths):
                widths[index] = max(widths[index], len(value))

    header = " | ".join(columns[index].ljust(widths[index]) for index in range(len(columns)))
    separator = "-+-".join("-" * widths[index] for index in range(len(columns)))

    lines = [header, separator]

    for row in str_rows:
        line = " | ".join(row[index].ljust(widths[index]) for index in range(len(columns)))
        lines.append(line)

    if not rows:
        lines.append("(0 rows)")

    return "\n".join(lines)


def run_all(conn: sqlite3.Connection) -> str:
    items = parse_queries(queries_sql())
    blocks: list[str] = []

    for item in items:
        header = f"=== Q{item.number}: {item.description} ==="

        upper_sql = item.sql.lstrip().upper()
        if upper_sql.startswith("SELECT") or upper_sql.startswith("WITH"):
            columns, rows = run_query(conn, item.sql)
            body = format_result(columns, rows)
        else:
            exec_script(conn, item.sql)
            if upper_sql.startswith("CREATE INDEX"):
                body = "인덱스 생성 완료"
            elif upper_sql.startswith("UPDATE"):
                body = "UPDATE 실행 완료"
            elif upper_sql.startswith("DELETE"):
                body = "DELETE 실행 완료"
            else:
                body = "실행 완료"

        blocks.append(f"{header}\n{body}")

    return "\n\n".join(blocks)
