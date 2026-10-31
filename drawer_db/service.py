from .db import connect, exec_script
from .queries import run_all
from .resources import schema_sql, seed_sql


def do_init(db_path: str) -> None:
    import os

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = connect(db_path)
    try:
        exec_script(conn, schema_sql())
    finally:
        conn.close()


def do_seed(db_path: str) -> None:
    conn = connect(db_path)
    try:
        exec_script(conn, seed_sql())
    finally:
        conn.close()


def do_queries(db_path: str) -> str:
    do_init(db_path)
    do_seed(db_path)

    conn = connect(db_path)
    try:
        return run_all(conn)
    finally:
        conn.close()


def do_all(db_path: str) -> str:
    return do_queries(db_path)
