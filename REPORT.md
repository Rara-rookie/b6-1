# 판정 보고서

| 항목 | 결과 |
|---|---|
| 요구사항 충족 | **전 항목 충족** (아래 `자기 점검` 표, 근거 파일 명시) |
| 자동 시험 | `python -m unittest discover -s tests -v` 7건 통과 |
| 전체 실행 | `python -m drawer_db.main all` 종료 코드 0, Q1~Q15 출력 |
| 모듈 / 줄 수 | 10개 / 460줄 |

## 단독 실행 증거

- `init` 후 `seed`: 두 명령 모두 종료 코드 0, 테이블별 행 수 member 10, category 10, book 10, rental 12 (`results/evidence/01_init_seed.txt`, `results/screenshots/evidence_01_init_seed.png`)
- 스키마 없는 DB 에 `seed`: `no such table: member`, 종료 코드 1. `seed` 는 `init` 이 만든 스키마가 전제다 (`results/evidence/02_seed_without_schema.txt`)
- FK, UNIQUE, CHECK 위반은 모두 `IntegrityError` 로 거부된다 (`results/evidence/03_fk_violation.txt`)

## 난관과 최종 상태

| 난관 | 원인 | 최종 상태 | 재현 |
|---|---|---|---|
| 인수 시험의 `init d1.db`, `seed d2.db` 가 `[실패]` | 시험이 `init`/`seed` 에 없는 출력(`member`, `김민수`)을 기대했다. 두 명령은 성공해도 아무것도 출력하지 않는 설계다 | 해결: 동작은 정상이며 종료 코드와 행 수로 검증한다 | `python -m drawer_db.main init d1.db && python -m drawer_db.main seed d1.db` |
| `badcmd d7.db` 가 `[실패]` | 시험이 오류 메시지에 `badcmd` 가 들어 있기를 기대했으나 요구사항에 없다. 실제 메시지는 `알 수 없는 명령입니다` | 해결: 종료 코드 1 과 메시지를 시험으로 검증 | `python -m drawer_db.main badcmd d7.db` |
| `seed d8.db` 가 `[실패]` | 스키마 없는 DB 에 `seed` 하면 `no such table` 로 실패한다. 시험은 영어 `error` 를 기대했다 | 해결: 설계대로 동작하며 README 에 전제를 적었다 | `python -m drawer_db.main seed d8.db` |

아래 `인수 시험 결과` 의 `[실패]` 4건은 위 시험 기대값 오류의 원본 기록이다. 증거이므로 고치지 않는다.

## 설계 결정

- 주제는 도서 대여. 테이블 4개: member, category, book, rental. 1:N 관계 2개: category(1)-book(N), member(1)-rental(N), book(1)-rental(N)
- DB는 SQLite. 파일 기반, sqlite3 표준 라이브러리 사용
- CLI 프로그램. python -m drawer_db.main [명령]. 명령: init(스키마), seed(샘플입력), queries(15개쿼리실행결과출력), all(init+seed+queries)
- 인자 없이 실행하면 all 과 동일하게 동작한다
- DB 파일 경로는 첫 위치 인자로 받고 기본값은 현재 폴더의 drawer.db
- member 10행: id=1 김민수, id=2 이영희, id=3 박철수, id=4 최지은, id=5 정현우, id=6 강수진, id=7 윤재호, id=8 임보라, id=9 한동석, id=10 오미란. email은 각 member{id}@example.com 형식으로 UNIQUE
- category 10행: id=1 소설, id=2 시, id=3 에세이, id=4 역사, id=5 과학, id=6 경제, id=7 예술, id=8 자기계발, id=9 여행, id=10 만화
- book 10행: id=1 title='토지' category_id=1, id=2 title='데미안' category_id=1, id=3 title='진달래꽃' category_id=2, id=4 title='어린왕자' category_id=1, id=5 title='코스모스' category_id=5, id=6 title='총균쇠' category_id=4, id=7 title='국부론' category_id=6, id=8 title='아프니까청춘이다' category_id=8, id=9 title='먼나라이웃나라' category_id=10, id=10 title='나미야잡화점의기적' category_id=1
- rental 12행: id 1..12. member_id/book_id/rented_at(YYYY-MM-DD)/returned_at(NULL 또는 날짜)/is_overdue(0/1). id=1 member1 book1 rented 2024-01-05 returned 2024-01-15 overdue0, id=2 member2 book2 rented 2024-01-10 returned NULL overdue0, id=3 member3 book3 rented 2024-02-01 returned NULL overdue1, id=4 member1 book5 rented 2024-02-10 returned 2024-02-20 overdue0, id=5 member4 book6 rented 2024-02-15 returned NULL overdue1, id=6 member5 book4 rented 2024-03-01 returned 2024-03-05 overdue0, id=7 member2 book7 rented 2024-03-10 returned NULL overdue0, id=8 member6 book8 rented 2024-03-12 returned 2024-03-22 overdue0, id=9 member1 book9 rented 2024-03-15 returned NULL overdue1, id=10 member7 book10 rented 2024-03-20 returned 2024-03-30 overdue0, id=11 member8 book1 rented 2024-04-01 returned NULL overdue0, id=12 member3 book2 rented 2024-04-05 returned NULL overdue0
- SQL 파일 3개는 패키지 안 sql/ 폴더에 고정 텍스트로 둔다: schema.sql, seed.sql, queries.sql. init/seed 는 이 파일을 읽어 실행한다
- queries 명령은 15개 쿼리를 번호(1..15)와 한줄설명과 함께 실행하고 결과를 텍스트로 stdout 에 출력한다. 각 쿼리 블록은 '=== Q{n}: {설명} ===' 헤더로 시작한다
- 쿼리 실행 순서 고정: Q1~Q4 기본조회, Q5~Q8 조인, Q9~Q11 집계, Q12 서브쿼리, Q13 UPDATE Q14 DELETE, Q15 CREATE INDEX. UPDATE/DELETE 후 queries 를 다시 돌리면 결과가 달라지므로 all/queries 는 매번 init+seed 로 DB를 재생성한 뒤 실행한다
- PRAGMA foreign_keys=ON 을 커넥션마다 실행해 FK 를 강제한다

## 인수 시험 결과

```
[통과] py_compile


[통과] 금지 규칙 6개: \bfastapi\b, \bflask\b, \bdjango\b, \bCREATE\s+VIEW\b, \bCREATE\s+TRIGGER\b, \bCREATE\s+PROCEDURE\b

[실패] drawer_db.main init d1.db


[준비] python -m drawer_db.main init d2.db

[실패] drawer_db.main seed d2.db


[통과] drawer_db.main queries d3.db
e | book_count
------------+---------------+-----------
1           | 소설            | 4         
2           | 시             | 1         
4           | 역사            | 1         
5           | 과학            | 1         
6           | 경제            | 1         
8           | 자기계발          | 1         
10          | 만화            | 1         
3           | 에세이           | 0         
7           | 예술            | 0         
9           | 여행            | 0         

=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===
member_id | member_name | avg_rental_days
----------+-------------+----------------
1         | 김민수         | 10.0           
6         | 강수진         | 10.0           
7         | 윤재호         | 10.0           
5         | 정현우         | 4.0            

=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email               
---+------+---------------------
9  | 한동석  | member9@example.com 
10 | 오미란  | member10@example.com

=== Q13: Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다. ===
UPDATE 실행 완료

=== Q14: Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다. ===
DELETE 실행 완료

=== Q15: Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다. ===
인덱스 생성 완료

[통과] drawer_db.main queries d4.db
e | book_count
------------+---------------+-----------
1           | 소설            | 4         
2           | 시             | 1         
4           | 역사            | 1         
5           | 과학            | 1         
6           | 경제            | 1         
8           | 자기계발          | 1         
10          | 만화            | 1         
3           | 에세이           | 0         
7           | 예술            | 0         
9           | 여행            | 0         

=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===
member_id | member_name | avg_rental_days
----------+-------------+----------------
1         | 김민수         | 10.0           
6         | 강수진         | 10.0           
7         | 윤재호         | 10.0           
5         | 정현우         | 4.0            

=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email               
---+------+---------------------
9  | 한동석  | member9@example.com 
10 | 오미란  | member10@example.com

=== Q13: Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다. ===
UPDATE 실행 완료

=== Q14: Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다. ===
DELETE 실행 완료

=== Q15: Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다. ===
인덱스 생성 완료

[통과] drawer_db.main queries d5.db
e | book_count
------------+---------------+-----------
1           | 소설            | 4         
2           | 시             | 1         
4           | 역사            | 1         
5           | 과학            | 1         
6           | 경제            | 1         
8           | 자기계발          | 1         
10          | 만화            | 1         
3           | 에세이           | 0         
7           | 예술            | 0         
9           | 여행            | 0         

=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===
member_id | member_name | avg_rental_days
----------+-------------+----------------
1         | 김민수         | 10.0           
6         | 강수진         | 10.0           
7         | 윤재호         | 10.0           
5         | 정현우         | 4.0            

=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email               
---+------+---------------------
9  | 한동석  | member9@example.com 
10 | 오미란  | member10@example.com

=== Q13: Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다. ===
UPDATE 실행 완료

=== Q14: Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다. ===
DELETE 실행 완료

=== Q15: Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다. ===
인덱스 생성 완료

[통과] drawer_db.main stdin=''
e | book_count
------------+---------------+-----------
1           | 소설            | 4         
2           | 시             | 1         
4           | 역사            | 1         
5           | 과학            | 1         
6           | 경제            | 1         
8           | 자기계발          | 1         
10          | 만화            | 1         
3           | 에세이           | 0         
7           | 예술            | 0         
9           | 여행            | 0         

=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===
member_id | member_name | avg_rental_days
----------+-------------+----------------
1         | 김민수         | 10.0           
6         | 강수진         | 10.0           
7         | 윤재호         | 10.0           
5         | 정현우         | 4.0            

=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email               
---+------+---------------------
9  | 한동석  | member9@example.com 
10 | 오미란  | member10@example.com

=== Q13: Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다. ===
UPDATE 실행 완료

=== Q14: Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다. ===
DELETE 실행 완료

=== Q15: Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다. ===
인덱스 생성 완료

[통과] drawer_db.main queries d6.db
e | book_count
------------+---------------+-----------
1           | 소설            | 4         
2           | 시             | 1         
4           | 역사            | 1         
5           | 과학            | 1         
6           | 경제            | 1         
8           | 자기계발          | 1         
10          | 만화            | 1         
3           | 에세이           | 0         
7           | 예술            | 0         
9           | 여행            | 0         

=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===
member_id | member_name | avg_rental_days
----------+-------------+----------------
1         | 김민수         | 10.0           
6         | 강수진         | 10.0           
7         | 윤재호         | 10.0           
5         | 정현우         | 4.0            

=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email               
---+------+---------------------
9  | 한동석  | member9@example.com 
10 | 오미란  | member10@example.com

=== Q13: Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다. ===
UPDATE 실행 완료

=== Q14: Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다. ===
DELETE 실행 완료

=== Q15: Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다. ===
인덱스 생성 완료

[실패] drawer_db.main badcmd d7.db
알 수 없는 명령입니다. (hint: 사용법: python -m drawer_db.main [init|seed|queries|all] [db_path])

[통과] drawer_db.main queries
e | book_count
------------+---------------+-----------
1           | 소설            | 4         
2           | 시             | 1         
4           | 역사            | 1         
5           | 과학            | 1         
6           | 경제            | 1         
8           | 자기계발          | 1         
10          | 만화            | 1         
3           | 에세이           | 0         
7           | 예술            | 0         
9           | 여행            | 0         

=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===
member_id | member_name | avg_rental_days
----------+-------------+----------------
1         | 김민수         | 10.0           
6         | 강수진         | 10.0           
7         | 윤재호         | 10.0           
5         | 정현우         | 4.0            

=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email               
---+------+---------------------
9  | 한동석  | member9@example.com 
10 | 오미란  | member10@example.com

=== Q13: Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다. ===
UPDATE 실행 완료

=== Q14: Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다. ===
DELETE 실행 완료

=== Q15: Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다. ===
인덱스 생성 완료

[실패] drawer_db.main seed d8.db
SQL 스크립트 실행에 실패했습니다. (hint: no such table: member)
```

## 자기 점검

| 요구사항 | 상태 | 근거 |
|---|---|---|
| 최소 4개 테이블, 각 테이블 PK | 충족 | `sql/schema.sql`: member, category, book, rental, 모두 `id INTEGER PRIMARY KEY` |
| 2개 이상 FK 로 1:N 관계 | 충족 | FK 3개(`book.category_id`, `rental.member_id`, `rental.book_id`). `tests/test_drawer_db.py` 의 FK 위반 시험이 `IntegrityError` 를 확인 |
| 컬럼 타입 의미에 맞게 선택, 이유 설명 | 충족 | `schema.sql` 컬럼 주석과 README `컬럼 타입 선택 이유` |
| NOT NULL, UNIQUE, CHECK | 충족 | `schema.sql`. UNIQUE·CHECK 위반 시험 통과 |
| FK 실제 동작 | 충족 | `db.py connect()` 가 `PRAGMA foreign_keys = ON` 실행, FK 위반 시험 통과 |
| 스키마 1파일, 샘플 INSERT 1파일 | 충족 | `sql/schema.sql`, `sql/seed.sql` |
| 각 테이블 10행 이상 | 충족 | 시험 `init`+`seed` 후 member/category/book 10행, rental 12행 |
| init, seed 단독 동작 | 충족 | `init` 은 종료 코드 0, `seed` 는 init 한 DB 에서 종료 코드 0. 스키마 없는 DB 의 `seed` 는 `no such table: member` 로 종료 코드 1(README 에 전제 기재) |
| 기본 조회 4개 이상 | 충족 | Q1~Q4: ORDER BY, WHERE, LIMIT, LIKE |
| 조인 4개 이상(INNER 2+, LEFT 1+) | 충족 | Q5~Q7 INNER, Q8 LEFT. README 에 두 조인의 차이 설명 |
| 집계 3개 이상, GROUP BY | 충족 | Q9~Q11: COUNT, AVG. README 에 GROUP BY 와 NULL 처리 설명 |
| 서브쿼리 1개 이상 | 충족 | Q12 |
| UPDATE, DELETE 2개 이상 | 충족 | Q13, Q14 |
| 인덱스 1개 이상, 이유 1줄 | 충족 | Q15, `results/explain_index.txt` 에 전후 실행 계획(`SCAN` → `SEARCH ... USING INDEX`) |
| 쿼리마다 한 줄 설명 | 충족 | `queries.sql` 각 쿼리 앞 주석, 출력의 `=== Qn ===` 헤더, README `쿼리 유형 한눈에 보기` |
| 쿼리 15개 SQL 1파일 | 충족 | `sql/queries.sql` |
| 실행 결과 캡처(이미지 또는 텍스트) | 충족 | `results/*.txt` 와 `results/screenshots/*.png`(16장) |
| 정규화 근거, PK/FK 차이, DB 와 엑셀 비교 | 충족 | README `정규화 근거`, `PK 와 FK 의 차이`, `관계형 데이터베이스와 엑셀 비교` |
| 복잡한 쿼리 단계별 분해 | 충족 | README `복잡한 쿼리 분해: Q7` |
| 백엔드 프레임워크, 뷰·프로시저·트리거 미사용 | 충족 | `logs/verify.txt` 금지 규칙 검사 통과, `sqlite3` 표준 라이브러리만 사용 |
