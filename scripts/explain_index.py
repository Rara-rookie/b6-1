import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from drawer_db.service import do_init, do_seed
from drawer_db.db import connect


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "explain_test.db")
        
        do_init(db_path)
        do_seed(db_path)
        
        conn = connect(db_path)
        try:
            output = []
            
            output.append("$ EXPLAIN QUERY PLAN SELECT * FROM rental WHERE member_id = 1")
            cursor = conn.execute("EXPLAIN QUERY PLAN SELECT * FROM rental WHERE member_id = 1")
            rows = cursor.fetchall()
            for row in rows:
                output.append(str(row))
            
            output.append("")
            output.append("$ CREATE INDEX idx_rental_member_id ON rental(member_id)")
            conn.execute("CREATE INDEX idx_rental_member_id ON rental(member_id)")
            conn.commit()
            output.append("")
            
            output.append("$ EXPLAIN QUERY PLAN SELECT * FROM rental WHERE member_id = 1")
            cursor = conn.execute("EXPLAIN QUERY PLAN SELECT * FROM rental WHERE member_id = 1")
            rows = cursor.fetchall()
            for row in rows:
                output.append(str(row))
            
            output.append("")
            output.append("전체 스캔이 인덱스 탐색으로 바뀐다")
            
            result_text = "\n".join(output)
            
            results_dir = Path(__file__).parent.parent / "results"
            results_dir.mkdir(exist_ok=True)
            
            output_file = results_dir / "explain_index.txt"
            output_file.write_text(result_text, encoding="utf-8")
            
            print(result_text)
        finally:
            conn.close()


if __name__ == "__main__":
    main()
