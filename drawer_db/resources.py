from pathlib import Path

from .errors import DrawerError


def read_sql(name: str) -> str:
    sql_dir = Path(__file__).resolve().parent / "sql"
    file_path = sql_dir / name
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DrawerError(
            f"SQL 파일을 찾을 수 없습니다: {name}",
            hint=str(file_path),
        ) from exc
    except OSError as exc:
        raise DrawerError(
            f"SQL 파일을 읽을 수 없습니다: {name}",
            hint=str(exc),
        ) from exc


def schema_sql() -> str:
    return read_sql("schema.sql")


def seed_sql() -> str:
    return read_sql("seed.sql")


def queries_sql() -> str:
    return read_sql("queries.sql")
