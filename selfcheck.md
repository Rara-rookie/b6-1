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

## `logs/verify.txt` 의 [실패] 4건에 대하여

`init d1.db`, `seed d2.db`, `badcmd d7.db`, `seed d8.db` 는 자동 인수 시험이 요구사항에 없는 출력(`member`, `김민수`, `badcmd`, `error`)을 기대해서 실패로 기록된 것이다. 프로그램의 결함이 아니다. 원본 로그는 증거이므로 고치지 않고, 같은 동작을 `tests/test_drawer_db.py` 가 설계대로 검증한다(`python -m unittest discover -s tests -v`, 7건 통과).
