| 요구사항 | 상태 | 근거 |
|---|---|---|
| 최소 4개 테이블 설계, 각 테이블 PK | 충족 | `sql/schema.sql`에 member, category, book, rental 4개 테이블 정의, 모두 `id INTEGER PRIMARY KEY` |
| 2개 이상 FK로 1:N 관계 | 충족 | `sql/schema.sql`: `book.category_id → category(id)`, `rental.member_id → member(id)`, `rental.book_id → book(id)` 총 3개 FK |
| 컬럼 타입 의미에 맞게 선택 | 충족 | `sql/schema.sql`: TEXT, INTEGER, DATE 사용 (`rented_at DATE`, `email TEXT` 등) |
| NOT NULL 1개 이상 | 충족 | `sql/schema.sql`: `name TEXT NOT NULL` 등 다수 |
| UNIQUE 1개 이상 | 충족 | `sql/schema.sql`: `email TEXT NOT NULL UNIQUE`, `category.name ... UNIQUE` |
| FK 실제 동작 | 충족 | `db.py connect()`에서 `PRAGMA foreign_keys = ON` 실행 |
| 스키마 생성 스크립트 1개 파일 | 충족 | `sql/schema.sql` CREATE TABLE로 구성 |
| 샘플 데이터 INSERT 스크립트 1개 파일 | 충족 | `sql/seed.sql` 존재, 부모 테이블 먼저 입력 |
| 각 테이블 최소 10행 이상 | 미흡 | `sql/seed.sql`: member/category/book 각 10행이나 rental은 12행(충족)이지만, 실행 결과 `seed d2.db` [실패], `init d1.db` [실패]로 실제 데이터 적재가 검증되지 않음 |
| init 명령 단독 동작 | 미흡 | 실행 결과 `[실패] drawer_db.main init d1.db` — init 단독 실행이 기대 출력을 내지 못함 |
| seed 명령 동작 | 미흡 | 실행 결과 `[실패] drawer_db.main seed d2.db`, `[실패] drawer_db.main seed d8.db (no such table: member)` — seed가 선행 init 없이 실패 |
| 기본 조회 4개 이상 (WHERE, ORDER BY, LIMIT) | 충족 | `sql/queries.sql` Q1~Q4: ORDER BY, WHERE, LIMIT 5 포함 |
| 조인 4개 이상 (INNER 2+, LEFT 1+) | 충족 | `sql/queries.sql` Q5~Q8: INNER JOIN 3개(Q5,Q6,Q7), LEFT JOIN(Q8) |
| 집계 3개 이상 (COUNT/SUM/AVG 중 2개+ + GROUP BY) | 충족 | `sql/queries.sql` Q9,Q10 COUNT+GROUP BY, Q11 AVG+GROUP BY |
| 서브쿼리 1개 이상 | 충족 | `sql/queries.sql` Q12: `WHERE id NOT IN (SELECT member_id FROM rental)` |
| UPDATE, DELETE 2개 이상 | 충족 | `sql/queries.sql` Q13 UPDATE, Q14 DELETE, 실행 결과 완료 메시지 확인 |
| 인덱스 1개 이상 + 적용 이유 1줄 | 충족 | `sql/queries.sql` Q15 `CREATE INDEX idx_rental_member_id`, 주석에 이유 명시 |
| 쿼리마다 한 줄 설명 | 충족 | `sql/queries.sql` 각 쿼리 앞 `--` 주석, 실행 결과 `=== Q11: ... ===` 헤더 출력 |
| 쿼리 15개 SQL 1개 파일 | 충족 | `sql/queries.sql` Q1~Q15 존재, `queries` 명령 [통과] |
| 실행 결과 확인 자료(텍스트) | 충족 | `queries d3.db` [통과], Q1~Q15 결과 텍스트 출력 확인 |
| 백엔드 프레임워크 미사용 | 충족 | 금지 규칙 검사 [통과], sqlite3 표준 라이브러리만 사용 |
| 뷰/프로시저/트리거 미사용 | 충족 | 금지 규칙 `CREATE VIEW/TRIGGER/PROCEDURE` [통과] |
