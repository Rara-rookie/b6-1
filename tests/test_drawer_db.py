import unittest
import tempfile
import os
import sys
import sqlite3
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from drawer_db.service import do_init, do_seed, do_queries
from drawer_db.db import connect
from drawer_db.errors import DrawerError
from drawer_db.main import main


class TestDrawerDB(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_case1_init_creates_four_tables(self):
        do_init(self.db_path)
        conn = connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            self.assertEqual(sorted(tables), ["book", "category", "member", "rental"])
        finally:
            conn.close()

    def test_case2_init_seed_row_counts(self):
        do_init(self.db_path)
        do_seed(self.db_path)
        conn = connect(self.db_path)
        try:
            member_count = conn.execute("SELECT COUNT(*) FROM member").fetchone()[0]
            category_count = conn.execute("SELECT COUNT(*) FROM category").fetchone()[0]
            book_count = conn.execute("SELECT COUNT(*) FROM book").fetchone()[0]
            rental_count = conn.execute("SELECT COUNT(*) FROM rental").fetchone()[0]
            
            self.assertEqual(member_count, 10)
            self.assertEqual(category_count, 10)
            self.assertEqual(book_count, 10)
            self.assertEqual(rental_count, 12)
        finally:
            conn.close()

    def test_case3_foreign_key_violations(self):
        do_init(self.db_path)
        conn = connect(self.db_path)
        try:
            # FK 위반: 존재하지 않는 category_id
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO book (title, category_id) VALUES ('Test', 999)"
                )
                conn.commit()
            conn.rollback()
            
            # FK 위반: 존재하지 않는 member_id
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO rental (member_id, book_id, rented_at, is_overdue) VALUES (999, 1, '2024-01-01', 0)"
                )
                conn.commit()
            conn.rollback()
        finally:
            conn.close()

        # FK 위반: 대여 기록이 있는 member 삭제 시도
        do_seed(self.db_path)
        conn = connect(self.db_path)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM member WHERE id = 1")
                conn.commit()
            conn.rollback()
        finally:
            conn.close()

    def test_case4_unique_and_check_violations(self):
        do_init(self.db_path)
        do_seed(self.db_path)
        conn = connect(self.db_path)
        try:
            # 기존 회원의 이메일로 중복 삽입 시도
            existing_email = conn.execute(
                "SELECT email FROM member LIMIT 1"
            ).fetchone()[0]
            
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO member (name, email) VALUES ('Duplicate', ?)",
                    (existing_email,)
                )
                conn.commit()
            conn.rollback()
            
            # CHECK 위반: is_overdue=2
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO rental (member_id, book_id, rented_at, is_overdue) VALUES (1, 1, '2024-01-01', 2)"
                )
                conn.commit()
            conn.rollback()
        finally:
            conn.close()

    def test_case5_seed_without_schema_raises_drawer_error(self):
        # 스키마 없는 새 db에 seed 실행
        conn = connect(self.db_path)
        conn.close()
        
        with self.assertRaises(DrawerError) as context:
            do_seed(self.db_path)
        
        error_str = str(context.exception)
        self.assertTrue(
            "no such table" in error_str,
            f"Expected 'no such table' in error message, got: {error_str}"
        )

    def test_case6_queries_output_has_all_15_headers(self):
        output = do_queries(self.db_path)
        
        for i in range(1, 16):
            header = f"=== Q{i}:"
            self.assertIn(
                header, output,
                f"Expected '{header}' in queries output"
            )

    def test_case7_main_return_values(self):
        # 잘못된 명령어: 반환값 1
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            return_code = main(["badcmd", "x.db"])
        self.assertEqual(return_code, 1)
        
        # init 명령어: 반환값 0
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            return_code = main(["init", self.db_path])
        self.assertEqual(return_code, 0)


if __name__ == "__main__":
    unittest.main()
