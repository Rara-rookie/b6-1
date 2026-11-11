from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from drawer_db.db import connect  # noqa: E402
from drawer_db.service import do_init, do_seed  # noqa: E402

RESULTS_DIR = ROOT / "results" / "evidence"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _shorten_output(text: str) -> str:
    lines = text.splitlines()
    if len(lines) <= 15:
        return text
    shortened = lines[:14] + ["... (이하 생략)"]
    return "\n".join(shortened) + "\n"


def _format_block(display_command: str, output: str, returncode: int, truncate: bool = False) -> str:
    body = _shorten_output(output) if truncate else output
    parts = [f"$ {display_command}"]
    if body:
        parts.append(body.rstrip("\n"))
    parts.append(f"(종료 코드 {returncode})")
    return "\n".join(parts)


def _run_command(
    args: list[str],
    display_command: str,
    *,
    cwd: Path,
    stderr_to_stdout: bool = False,
    truncate: bool = False,
) -> str:
    completed = subprocess.run(
        args,
        cwd=str(cwd),
        env=_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if stderr_to_stdout else subprocess.PIPE,
        encoding="utf-8",
        errors="strict",
    )
    output = completed.stdout if stderr_to_stdout else completed.stdout
    if not stderr_to_stdout and completed.stderr:
        output += completed.stderr
    return _format_block(display_command, output, completed.returncode, truncate=truncate)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_query_table(db_path: Path) -> str:
    sql = (
        "SELECT 'member' AS t, COUNT(*) AS n FROM member "
        "UNION ALL SELECT 'category', COUNT(*) FROM category "
        "UNION ALL SELECT 'book', COUNT(*) FROM book "
        "UNION ALL SELECT 'rental', COUNT(*) FROM rental"
    )
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(sql).fetchall()
    finally:
        conn.close()

    t_width = max(len("t"), *(len(str(row[0])) for row in rows))
    n_width = max(len("n"), *(len(str(row[1])) for row in rows))
    header = f"{'t'.ljust(t_width)} | {'n'.ljust(n_width)}"
    divider = f"{'-' * t_width}-+-{'-' * n_width}"
    body = [f"{str(t).ljust(t_width)} | {str(n).ljust(n_width)}" for t, n in rows]
    table = "\n".join([header, divider, *body]) + "\n"
    display = '$ sqlite3 d1.db "SELECT ... COUNT(*) ..."'
    return "\n".join([display, table.rstrip("\n"), "(종료 코드 0)"])


def _capture_01() -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "d1.db"
        blocks = [
            _run_command(
                [sys.executable, "-m", "drawer_db.main", "init", str(db_path)],
                "python -m drawer_db.main init d1.db",
                cwd=ROOT,
            ),
            _run_command(
                [sys.executable, "-m", "drawer_db.main", "seed", str(db_path)],
                "python -m drawer_db.main seed d1.db",
                cwd=ROOT,
            ),
            _make_query_table(db_path),
        ]
        return "\n\n".join(blocks) + "\n"


def _capture_02() -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "d8.db"
        return (
            _run_command(
                [sys.executable, "-m", "drawer_db.main", "seed", str(db_path)],
                "python -m drawer_db.main seed d8.db",
                cwd=ROOT,
                stderr_to_stdout=True,
            )
            + "\n"
        )


def _capture_03() -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "fk.db"
        do_init(str(db_path))
        do_seed(str(db_path))

        sqls = [
            "INSERT INTO book (id, title, category_id) VALUES (99, 'x', 999)",
            "INSERT INTO rental (id, member_id, book_id, rented_at, is_overdue) VALUES (99, 999, 1, '2024-05-01', 0)",
            "DELETE FROM member WHERE id = 1",
            "INSERT INTO member (id, name, email) VALUES (99, 'dup', 'member1@example.com')",
            "INSERT INTO rental (id, member_id, book_id, rented_at, is_overdue) VALUES (98, 1, 1, '2024-05-01', 2)",
        ]

        lines: list[str] = []
        conn = connect(str(db_path))
        try:
            for sql in sqls:
                lines.append(f"sqlite> {sql}")
                try:
                    conn.execute(sql)
                    conn.commit()
                except sqlite3.IntegrityError as exc:
                    conn.rollback()
                    lines.append(f"IntegrityError: {exc}")
        finally:
            conn.close()

        lines.append("(PRAGMA foreign_keys = ON 상태, 모든 위반이 거부됨)")
        return "\n".join(lines) + "\n"


def _capture_04() -> str:
    return (
        _run_command(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            "python -m unittest discover -s tests -v",
            cwd=ROOT,
            stderr_to_stdout=True,
        )
        + "\n"
    )


def _capture_05() -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "drawer.db"
        return (
            _run_command(
                [sys.executable, "-m", "drawer_db.main", "all", str(db_path)],
                "python -m drawer_db.main all drawer.db",
                cwd=ROOT,
                truncate=True,
            )
            + "\n"
        )


def _capture_06() -> str:
    source = ROOT / "results" / "explain_index.txt"
    if source.exists():
        body = source.read_text(encoding="utf-8")
    else:
        completed = subprocess.run(
            [sys.executable, "scripts/explain_index.py"],
            cwd=str(ROOT),
            env=_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="strict",
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stdout)
        if not source.exists():
            raise FileNotFoundError(source)
        body = source.read_text(encoding="utf-8")
    return _format_block("python scripts/explain_index.py", body, 0) + "\n"


def main() -> int:
    captures = [
        ("01_init_seed.txt", _capture_01),
        ("02_seed_without_schema.txt", _capture_02),
        ("03_fk_violation.txt", _capture_03),
        ("04_unittest.txt", _capture_04),
        ("05_all_run.txt", _capture_05),
        ("06_explain_index.txt", _capture_06),
    ]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    failed = False

    for filename, producer in captures:
        path = RESULTS_DIR / filename
        try:
            content = producer()
            _write_text(path, content)
            written.append(str(path.relative_to(ROOT)))
        except Exception:
            failed = True

    for item in written:
        print(item)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
