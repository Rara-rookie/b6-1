import sqlite3

from .errors import DrawerError


def connect(db_path: str) -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as exc:
        raise DrawerError("데이터베이스 연결에 실패했습니다.", hint=str(exc)) from exc


def exec_script(conn: sqlite3.Connection, script_sql: str) -> None:
    try:
        conn.executescript(script_sql)
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise DrawerError("SQL 스크립트 실행에 실패했습니다.", hint=str(exc)) from exc


def run_query(conn: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple]]:
    try:
        cursor = conn.execute(sql)
        columns = [description[0] for description in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows
    except sqlite3.Error as exc:
        raise DrawerError("SQL 쿼리 실행에 실패했습니다.", hint=str(exc)) from exc
