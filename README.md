# drawer_db

SQLite 기반 도서 대여 데이터베이스를 초기화하고, 샘플 데이터를 넣고, 핵심 SQL 15개를 실행 결과와 함께 출력하는 CLI 프로그램이다.

- 패키지: `drawer_db`
- 진입점: `drawer_db.main`
- 실행 명령: `python -m drawer_db.main`
- 외부 패키지: 없음 (`sqlite3` 포함 표준 라이브러리만 사용)
- SQL 파일 위치: `drawer_db/sql/`

## 실행 방법

기본 실행:

```bash
python -m drawer_db.main
```

인자 없이 실행하면 `all`과 동일하게 동작한다. 즉, DB를 재생성하고 샘플 데이터를 넣은 뒤 15개 쿼리 결과를 출력한다.

명령 형식:

```bash
python -m drawer_db.main [init|seed|queries|all] [db_path]
```

기본 DB 파일 경로:

- 지정하지 않으면 현재 폴더의 `drawer.db`

명령 목록:

- `init`: 스키마 생성
- `seed`: 샘플 데이터 입력
- `queries`: DB를 재생성한 뒤 샘플 데이터 입력 후 15개 쿼리 실행
- `all`: `queries`와 동일

예시:

```bash
python -m drawer_db.main init d1.db
python -m drawer_db.main seed d1.db   # init 으로 만든 같은 DB 에 입력
python -m drawer_db.main queries d3.db
python -m drawer_db.main all d4.db
```

## 주요 명령 예시와 실제 출력

### 1) 전체 실행

```bash
python -m drawer_db.main queries d3.db
```

실제 출력 일부:

```text
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
```

### 2) 인자 없이 실행

```bash
python -m drawer_db.main
```

실제 출력 일부:

```text
=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===
id | name | email
---+------+---------------------
9  | 한동석  | member9@example.com
10 | 오미란  | member10@example.com
```

### 3) 잘못된 명령

```bash
python -m drawer_db.main badcmd d7.db
```

실제 출력:

```text
알 수 없는 명령입니다. (hint: 사용법: python -m drawer_db.main [init|seed|queries|all] [db_path])
```

### 4) 스키마 없이 seed 실행

```bash
python -m drawer_db.main seed d8.db
```

실제 출력:

```text
SQL 스크립트 실행에 실패했습니다. (hint: no such table: member)
```

## 주제와 테이블 설계

주제는 도서 대여다. 테이블은 4개다.

### 1) `member`
회원 정보

컬럼:
- `id INTEGER PRIMARY KEY`
- `name TEXT NOT NULL`
- `email TEXT NOT NULL UNIQUE`

샘플 데이터 10행:
- `1 김민수`
- `2 이영희`
- `3 박철수`
- `4 최지은`
- `5 정현우`
- `6 강수진`
- `7 윤재호`
- `8 임보라`
- `9 한동석`
- `10 오미란`

### 2) `category`
도서 카테고리 정보

컬럼:
- `id INTEGER PRIMARY KEY`
- `name TEXT NOT NULL UNIQUE`

샘플 데이터 10행:
- 소설, 시, 에세이, 역사, 과학, 경제, 예술, 자기계발, 여행, 만화

### 3) `book`
도서 정보

컬럼:
- `id INTEGER PRIMARY KEY`
- `title TEXT NOT NULL`
- `category_id INTEGER NOT NULL`
- `FOREIGN KEY (category_id) REFERENCES category(id)`

샘플 데이터 10행:
- `토지`
- `데미안`
- `진달래꽃`
- `어린왕자`
- `코스모스`
- `총균쇠`
- `국부론`
- `아프니까청춘이다`
- `먼나라이웃나라`
- `나미야잡화점의기적`

### 4) `rental`
대여 기록 정보

컬럼:
- `id INTEGER PRIMARY KEY`
- `member_id INTEGER NOT NULL`
- `book_id INTEGER NOT NULL`
- `rented_at DATE NOT NULL`
- `returned_at DATE`
- `is_overdue INTEGER NOT NULL`
- `FOREIGN KEY (member_id) REFERENCES member(id)`
- `FOREIGN KEY (book_id) REFERENCES book(id)`
- `CHECK (is_overdue IN (0, 1))`

샘플 데이터 12행이 들어 있다.

## 1:N 관계 설명

이 프로젝트에는 1:N 관계가 3개 있다.

1. `category(1) -> book(N)`
   - 하나의 카테고리에 여러 권의 책이 속할 수 있다.
   - `book.category_id`가 `category.id`를 참조한다.

2. `member(1) -> rental(N)`
   - 한 회원은 여러 대여 기록을 가질 수 있다.
   - `rental.member_id`가 `member.id`를 참조한다.

3. `book(1) -> rental(N)`
   - 한 도서는 여러 대여 기록에 등장할 수 있다.
   - `rental.book_id`가 `book.id`를 참조한다.

## 제약조건

구현된 제약조건은 다음과 같다.

- `NOT NULL`
  - `member.name`
  - `member.email`
  - `category.name`
  - `book.title`
  - `book.category_id`
  - `rental.member_id`
  - `rental.book_id`
  - `rental.rented_at`
  - `rental.is_overdue`

- `UNIQUE`
  - `member.email`
  - `category.name`

- `FOREIGN KEY`
  - `book.category_id -> category.id`
  - `rental.member_id -> member.id`
  - `rental.book_id -> book.id`

- `CHECK`
  - `rental.is_overdue IN (0, 1)`

또한 모든 커넥션에서 `PRAGMA foreign_keys = ON`을 실행해 FK를 강제한다.

## 정규화 근거

한 장의 엑셀 시트에 회원, 도서, 카테고리를 모두 기록하면 같은 카테고리 이름과 회원 이름이 매번 반복되고, 카테고리 이름을 수정할 때 모든 관련 행을 일일이 고쳐야 하며, 수정 빠진 행이 생겨 불일치가 발생한다. 테이블을 분리하면 각 정보를 한 곳에서만 관리하므로 이 문제를 해결한다.

| 정규형 | 이 프로젝트 적용 | 설명 |
|--------|----------------|------|
| 1NF | member, category, book, rental 각 컬럼이 원자값(반복 그룹 없음) | 한 칸에 값 하나만 저장하고 대여 목록 같은 배열을 컬럼에 두지 않음 |
| 2NF | 모든 테이블의 기본키가 단일 컬럼 `id` 이므로 기본키 일부에만 종속되는 속성이 생길 수 없음 | rental 의 rented_at, returned_at, is_overdue 는 대여 한 건(`rental.id`)에만 종속되고, 회원·도서 정보는 member_id, book_id 로 분리해 둠 |
| 3NF | book 테이블에 category_id 만 두고 category 이름은 별도 테이블에 저장 | category_id → category 이름 이행 종속을 끊어 카테고리 수정 시 book 행을 건드리지 않음 |

## 컬럼 타입 선택 이유

| 컬럼 | 타입 | 이유 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 각 행을 유일하게 식별하는 기본키. SQLite 에서 행 번호(rowid)의 별칭이 되어 조회가 빠르다 |
| name, title, email | TEXT | 길이가 정해지지 않은 문자열을 저장한다. SQLite 는 TEXT 길이를 제한하지 않는다 |
| category_id, member_id, book_id | INTEGER | 다른 테이블의 id 를 참조하므로 정수 사용 |
| rented_at, returned_at | TEXT(DATE 속성으로 선언) | SQLite 는 날짜 전용 저장형이 없으므로 ISO 8601('YYYY-MM-DD') 형식 문자열로 저장하되, 문자열 대소 비교와 julianday() 함수로 기간 계산이 가능 |
| returned_at | NULL 허용 | NULL 값이면 아직 반납되지 않음을 표현 |
| is_overdue | INTEGER(0 또는 1) | SQLite 에 BOOLEAN 타입이 없으므로 정수 0(거짓), 1(참)로 표현하고 CHECK 제약조건으로 범위 제한 |

## PK 와 FK 의 차이

기본키(Primary Key)는 한 테이블 안에서 각 행 자체의 정체성을 정의하며 중복과 NULL 을 허용하지 않는다. 외래키(Foreign Key)는 다른 테이블의 기본키를 가리키는 참조로서, 존재하지 않는 값을 삽입할 수 없고 참조되는 행을 삭제할 수 없다.

이 프로젝트의 외래키는 `rental.member_id → member.id`, `rental.book_id → book.id`, `book.category_id → category.id` 총 3개다. SQLite 는 외래키 제약을 기본적으로 비활성화하므로 쿼리 실행 전에 `PRAGMA foreign_keys=ON;` 을 선언해야 한다. 외래키 제약을 위반하면 IntegrityError 예외가 발생하며, tests/test_drawer_db.py 에서 이를 검증해 잘못된 참조가 저장되지 않음을 확인한다.

## 관계형 데이터베이스와 엑셀 비교

| 관점 | 엑셀 | 관계형 DB |
|------|------|----------|
| 관계 저장 | 시트 간 VLOOKUP 수식을 사용해 값을 복사하므로 중복과 불일치 위험 | 외래키로 다른 테이블을 참조하므로 한 곳 수정이 즉시 반영 |
| 데이터 중복 | 같은 카테고리 이름이 매 행에 반복되어 저장 공간 낭비 | 정규화로 중복 제거, 같은 카테고리는 한 행만 저장 |
| 무결성 보장 | 검증 규칙을 켜지 않으면 잘못된 값을 자유롭게 입력 가능 | 제약조건(NOT NULL, CHECK, 외래키)이 문제 데이터 삽입을 거부 |
| 동시 사용 | 한 명이 파일을 열면 다른 사람은 읽기 전용이거나 대기 | 서버형 DB 는 다중 사용자가 동시에 쿼리를 실행한다. 이 프로젝트의 SQLite 는 읽기는 동시에 가능하고 쓰기는 한 번에 한 연결만 가능하다 |
| 대량 데이터 질의 | 필터와 정렬 위주라 여러 표를 엮는 질의가 번거롭다 | 인덱스와 JOIN 으로 여러 테이블을 엮어 조건 검색한다(Q15 인덱스: `results/explain_index.txt` 참고) |
| 감사와 재현 | 수식과 수작업이 섞여 어떻게 결과를 만들었는지 추적 어려움 | SQL 스크립트로 실행 내역을 기록하고 언제든 같은 결과를 재현 가능 |

데이터가 소수 행에 불과하고 한두 사람만 수정하는 경우 엑셀이 설치와 학습 비용이 낮아 더 실용적이다.

## 모듈 구조와 각 모듈의 책임

### `drawer_db/__init__.py`
패키지 초기화 파일. 비어 있다.

### `drawer_db/errors.py`
공용 예외 정의.

- `DrawerError(message: str, hint: str | None = None)`

메시지와 선택적 힌트를 함께 관리한다.

### `drawer_db/db.py`
SQLite 연결과 SQL 실행 헬퍼.

- `connect(db_path: str) -> sqlite3.Connection`
  - DB 연결
  - `PRAGMA foreign_keys = ON` 실행

- `exec_script(conn, script_sql) -> None`
  - `executescript`로 SQL 스크립트 실행
  - 실패 시 rollback 후 `DrawerError` 발생

- `run_query(conn, sql) -> tuple[list[str], list[tuple]]`
  - SELECT 결과 컬럼명과 행 목록 반환

### `drawer_db/resources.py`
패키지 내부 `sql/` 폴더에서 SQL 파일 텍스트를 읽는다.

- `read_sql(name: str) -> str`
- `schema_sql() -> str`
- `seed_sql() -> str`
- `queries_sql() -> str`

### `drawer_db/queries.py`
쿼리 파일을 분할하고 결과를 문자열로 포맷한다.

- `QueryItem`
  - 번호, 설명, SQL 저장

- `parse_queries(queries_sql_text: str) -> list[QueryItem]`
  - `queries.sql`의 주석 설명과 SQL을 쿼리 단위로 분리

- `format_result(columns, rows) -> str`
  - 테이블 형태 텍스트 출력 생성

- `run_all(conn) -> str`
  - 15개 쿼리를 순서대로 실행
  - 각 블록을 `=== Q{n}: {설명} ===` 형식으로 출력
  - `UPDATE`, `DELETE`, `CREATE INDEX`는 완료 메시지 출력

### `drawer_db/service.py`
상위 동작 조립.

- `do_init(db_path: str) -> None`
  - 기존 DB 파일 삭제 후 스키마 생성

- `do_seed(db_path: str) -> None`
  - 샘플 데이터 입력

- `do_queries(db_path: str) -> str`
  - `init -> seed -> queries` 순서 실행

- `do_all(db_path: str) -> str`
  - `do_queries` 호출

### `drawer_db/main.py`
CLI 진입점.

- `parse_args(argv: list[str]) -> tuple[str, str]`
  - 명령과 DB 경로 파싱

- `main(argv: list[str] | None = None) -> int`
  - 서비스 호출
  - 결과 출력
  - 예외 시 stderr 출력 및 종료 코드 1 반환

### `drawer_db/sql/schema.sql`
스키마 생성 SQL.

### `drawer_db/sql/seed.sql`
샘플 데이터 입력 SQL.

### `drawer_db/sql/queries.sql`
15개 핵심 SQL과 설명 주석.

## 요구사항별 구현 위치

### DB 환경 준비
- SQLite 사용: `drawer_db/db.py`
- 표준 라이브러리 `sqlite3` 사용
- 실행 진입점: `drawer_db/main.py`

### 최소 4개 테이블 설계
- `drawer_db/sql/schema.sql`
  - `member`
  - `category`
  - `book`
  - `rental`

### PK/FK/제약조건
- `drawer_db/sql/schema.sql`
- FK 활성화: `drawer_db/db.py`, `schema.sql`

### 샘플 데이터 입력
- `drawer_db/sql/seed.sql`
- 실행: `drawer_db/service.py -> do_seed`

### 쿼리 15개 작성
- `drawer_db/sql/queries.sql`
- 실행/출력: `drawer_db/queries.py`

### 쿼리 설명과 결과 출력
- 설명 파싱: `drawer_db/queries.py -> parse_queries`
- 결과 포맷: `drawer_db/queries.py -> format_result`
- 블록 출력 형식: `drawer_db/queries.py -> run_all`

### 수정/삭제 후 재현 가능한 실행
- `drawer_db/service.py -> do_queries`
- `queries`와 `all`은 매번 `init + seed` 후 실행

### 인덱스 생성
- `drawer_db/sql/queries.sql`의 Q15

## 쿼리 15개 목록

### 기본 조회
1. 회원 전체를 이름 오름차순으로 조회
2. 아직 반납되지 않은 대여 기록을 최신 대여일 순으로 5건 조회
3. 연체 상태인 대여 기록을 대여일 오름차순으로 조회
4. 제목에 `왕자`가 포함된 도서 조회

### 조인
5. `INNER JOIN`으로 대여 기록과 회원 정보 조회
6. `INNER JOIN`으로 대여 기록과 도서 정보 조회
7. `INNER JOIN` 3개 테이블로 회원별 대여 도서 목록 조회
8. `LEFT JOIN`으로 대여 기록이 없는 회원도 포함한 회원별 대여 현황 조회

### 집계
9. `GROUP BY`와 `COUNT`로 회원별 대여 횟수 집계
10. `GROUP BY`와 `COUNT`로 카테고리별 도서 수 집계
11. `AVG`와 `GROUP BY`로 회원별 평균 대여 기간 계산
   - SQLite 전용 `julianday` 함수 사용

### 서브쿼리
12. 한 번도 대여하지 않은 회원 조회

### 수정 및 삭제
13. 반납일이 없고 대여일이 `2024-03-01` 이전인 기록을 연체 상태로 수정
14. `id = 12`인 대여 기록 삭제

### 인덱스
15. `rental(member_id)`에 인덱스 생성
   - 이유: 회원별 대여 조회와 집계 성능 향상

## INNER JOIN 과 LEFT JOIN 의 차이

INNER JOIN 은 양쪽 테이블 조건이 모두 맞는 행만 결과에 포함하고, LEFT JOIN 은 왼쪽 테이블의 모든 행을 유지하되 오른쪽 테이블에 짝이 없으면 해당 컬럼을 NULL 로 채운다.

이 프로젝트에서 대여 기록이 없는 회원이 있다. 대여 기록이 없는 회원은 id 9(한동석)와 id 10(오미란)이다. Q5(INNER JOIN member 와 rental)는 이런 회원을 결과에서 제외하므로 12행이 나온다. 반면 Q8(LEFT JOIN member 와 rental)은 이 두 회원도 포함하되 rental 관련 컬럼(rental_id, book_id, rented_at)이 NULL 로 표시되어 14행이 나온다.

| 구분 | INNER JOIN(Q5~Q7) | LEFT JOIN(Q8) |
|------|-----------------|--------------|
| 결합 조건 | 양쪽 테이블 모두 일치하는 행만 | 왼쪽 테이블 행 전부, 오른쪽 미일치 행은 NULL |
| 회원별 대여 기록이 없을 때 | 그 회원이 결과에서 빠짐 | 그 회원은 나타나되 대여 컬럼이 NULL |
| 결과 행 수 | rental 12행과 같다(Q5 12행) | 대여 12행 + 대여 없는 회원 2명(id 9, 10) = 14행 |
| 사용 시기 | 두 테이블이 모두 값을 가진 완전한 데이터만 필요할 때 | 한쪽이 없어도 기록하되 조건을 만족하지 않는 데이터를 파악할 때 |

## GROUP BY 와 집계 함수

GROUP BY 는 기준 컬럼의 값이 같은 행들을 하나의 묶음으로 만들고, COUNT, SUM, AVG 같은 집계 함수가 각 묶음마다 단 하나의 값을 계산해 낸다.

COUNT(*) 는 NULL 을 포함해 묶음의 모든 행을 센다. COUNT(컬럼) 은 NULL 을 무시하고 NULL 이 아닌 값만 센다. Q9 에서 회원별 대여 횟수를 구할 때 LEFT JOIN 으로 대여 기록이 없는 회원도 포함했는데, COUNT(r.id) 를 썼으므로 그 회원의 r.id 는 NULL 이고 결과는 0 이 된다(id 9, 10). 만약 COUNT(*) 를 썼다면 LEFT JOIN 이 만든 NULL 행 1줄을 세어 1 이 되어 잘못된 결과가 나온다.

Q11 에서 회원별 평균 대여 기간을 구할 때 WHERE returned_at IS NOT NULL 조건을 넣는 이유는 반납되지 않은 기록을 제외하기 위함이다. returned_at 이 NULL 이면 대여 기간을 계산할 수 없으므로 이미 반납된 건만 평균에 포함해야 한다. AVG 는 NULL 값을 무시하지만, 명시적으로 미반납 기록을 필터링하는 것이 의도를 명확히 한다.

SELECT 에 쓰인 비집계 컬럼(COUNT, SUM 같은 함수를 쓰지 않은 컬럼)은 반드시 GROUP BY 에도 있어야 한다. 그래야 어느 묶음의 결과인지 알 수 있기 때문이다. Q9 에서 SELECT m.id, m.name, COUNT(r.id) 라 했으면 GROUP BY m.id, m.name 으로 써야 한다.

| 함수 | 설명 | NULL 처리 |
|------|------|---------|
| COUNT(*) | 묶음의 모든 행 개수 | NULL 도 센다 |
| COUNT(컬럼) | NULL 이 아닌 값의 개수 | NULL 을 제외하고 센다 |
| SUM | 값들의 합 | NULL 을 무시한다 |
| AVG | 값들의 평균 | NULL 을 무시하고 평균을 낸다 |
| MAX, MIN | 최댓값, 최솟값 | NULL 을 무시한다 |

## 쿼리 유형 한눈에 보기

| 번호 | 유형 | 핵심 구문 | 한 줄 요약 |
|------|------|---------|----------|
| Q1 | 단순 조회 | SELECT, ORDER BY | 회원을 이름 오름차순으로 조회 |
| Q2 | 조건 조회 | WHERE, IS NULL, ORDER BY, LIMIT | 미반납 기록을 최신 순 5건 조회 |
| Q3 | 조건 조회 | WHERE(=) | 연체 상태 기록을 대여일 순으로 조회 |
| Q4 | 패턴 검색 | LIKE | 제목에 특정 문자가 포함된 도서 조회 |
| Q5 | INNER JOIN 2개 테이블 | INNER JOIN, ON | 대여 기록과 회원 정보를 함께 조회 |
| Q6 | INNER JOIN 2개 테이블 | INNER JOIN, ON | 대여 기록과 도서 정보를 함께 조회 |
| Q7 | INNER JOIN 3개 테이블 | INNER JOIN 2번, ON | 회원, 대여, 도서를 한 행에 표시 |
| Q8 | LEFT JOIN | LEFT JOIN, ON | 대여 기록 없는 회원도 포함해 조회(14행) |
| Q9 | 집계(GROUP BY + COUNT) | GROUP BY, COUNT, LEFT JOIN | 회원별 대여 횟수 집계 |
| Q10 | 집계(GROUP BY + COUNT) | GROUP BY, COUNT, LEFT JOIN | 카테고리별 도서 수 집계 |
| Q11 | 집계(GROUP BY + AVG) | GROUP BY, AVG, WHERE, julianday | 회원별 평균 대여 기간 계산 |
| Q12 | 서브쿼리 | WHERE NOT IN, SELECT | 대여 기록이 없는 회원 찾기 |
| Q13 | 데이터 수정 | UPDATE, SET, WHERE | 조건에 맞는 연체 상태를 일괄 수정 |
| Q14 | 데이터 삭제 | DELETE, WHERE | 특정 대여 기록 삭제 |
| Q15 | 인덱스 생성 | CREATE INDEX IF NOT EXISTS | 조회 성능 향상을 위해 인덱스 생성 |

## 복잡한 쿼리 분해: Q7

```sql
SELECT r.id AS rental_id, m.name AS member_name, b.title AS book_title, r.rented_at, r.returned_at
FROM rental r
INNER JOIN member m ON r.member_id = m.id
INNER JOIN book b ON r.book_id = b.id
ORDER BY r.rented_at ASC, r.id ASC;
```

**단계 1** - FROM rental r: rental 테이블 12행에서 시작하고 별칭 r 부여. 컬럼은 id, member_id, book_id, rented_at, returned_at, is_overdue 총 6개.

**단계 2** - INNER JOIN member m ON r.member_id = m.id: 각 대여 기록의 member_id 와 member 테이블의 id 를 맞춰 회원 정보를 붙인다. 모든 대여 기록의 member_id 가 존재하는 회원을 가리키므로(외래키 제약) 버려지는 행이 없어 12행이고, 컬럼은 member 의 id, name, email 이 추가돼 9개가 된다.

**단계 3** - INNER JOIN book b ON r.book_id = b.id: 각 대여 기록의 book_id 와 book 테이블의 id 를 맞춰 도서 정보를 붙인다. 마찬가지로 12행 유지되고, book 의 id, title, category_id 가 추가돼 총 12개 컬럼이 된다.

**단계 4** - SELECT r.id AS rental_id, m.name AS member_name, b.title AS book_title, r.rented_at, r.returned_at: 필요한 컬럼 5개만 고르고 명확한 별칭을 붙인다. 12행 유지되며 컬럼은 5개로 줄어든다.

**단계 5** - ORDER BY r.rented_at ASC, r.id ASC: 먼저 대여일 오름차순으로 정렬하고, 같은 날짜라면 대여 ID 오름차순으로 2차 정렬한다. 행의 순서만 바뀌고 12행, 5개 컬럼은 변하지 않는다.

최종 결과는 12행이고, 각 행은 하나의 대여 기록에 그를 수행한 회원과 대여한 도서 정보가 모두 담겨 있다.

## SQL 파일 구성

### `schema.sql`
- 테이블 삭제 후 재생성
- PK/FK/NOT NULL/UNIQUE/CHECK 포함

### `seed.sql`
- 부모 테이블부터 입력
  - `member`
  - `category`
  - `book`
  - `rental`

### `queries.sql`
- 각 쿼리 앞에 한 줄 설명 주석
- Q1~Q15 순서 고정

## 실행 결과 캡처

`results/` 폴더에 쿼리 15개의 실행 결과를 텍스트와 이미지로 남긴다.

| 파일 | 내용 |
|---|---|
| `results/all_queries.txt` | `python -m drawer_db.main all drawer.db` 전체 출력 |
| `results/Q01.txt` ~ `results/Q15.txt` | 쿼리별 설명 헤더와 결과 표 |
| `results/screenshots/Q01.png` ~ `Q15.png` | 위 쿼리별 결과 텍스트를 터미널 화면 형태로 그린 이미지 |
| `results/screenshots/all_queries.png` | 전체 출력을 한 장으로 그린 이미지 |
| `results/screenshots/evidence_01_*.png` ~ `evidence_06_*.png` | `init`·`seed`, 스키마 없는 `seed` 실패, FK·UNIQUE·CHECK 위반, 자동 시험, `all` 실행, 인덱스 실행 계획 |
| `results/evidence/*.txt` | 위 증거 이미지의 텍스트 원본(`$ 명령`, 출력, 종료 코드) |
| `results/screenshots/README.md` | 모든 이미지의 목록과 텍스트 원본 대응표 |
| `results/explain_index.txt` | Q15 인덱스 생성 전후의 `EXPLAIN QUERY PLAN` 비교 |

이미지는 실제 화면을 찍은 것이 아니라 `results/*.txt` 를 `scripts/render_captures.py` 로 렌더링한 것이다. 텍스트와 이미지의 내용은 항상 같다. 다시 만들려면 다음을 실행한다(Pillow 필요: `pip install pillow`).

```bash
python scripts/explain_index.py
python scripts/capture_evidence.py
python scripts/render_captures.py
```

`all` 은 매번 DB 를 새로 만들므로 같은 명령을 다시 실행하면 같은 결과가 나온다.

### 인덱스 적용 전후

`SELECT * FROM rental WHERE member_id = 1` 의 실행 계획이 인덱스 생성 전에는 `SCAN rental`(전체 행 훑기), 생성 후에는 `SEARCH rental USING INDEX idx_rental_member_id (member_id=?)`(인덱스 탐색)로 바뀐다. 원본은 `results/explain_index.txt` 에 있다.

## 자동 시험

```bash
python -m unittest discover -s tests -v
```

`tests/test_drawer_db.py` 가 다음을 검증한다.

| 시험 | 내용 |
|---|---|
| 테이블 생성 | `init` 후 테이블 4개 존재 |
| 샘플 행 수 | `init`+`seed` 후 member/category/book 각 10행, rental 12행 |
| FK 위반 | 없는 `category_id`, 없는 `member_id` 로 INSERT, 대여 기록이 있는 회원 DELETE 가 모두 `IntegrityError` |
| UNIQUE·CHECK 위반 | 중복 email, `is_overdue = 2` 가 `IntegrityError` |
| seed 단독 실행 | 스키마가 없는 DB 에 `seed` 하면 `no such table` 오류 |
| 쿼리 출력 | `=== Q1:` ~ `=== Q15:` 헤더 15개 |
| 종료 코드 | 잘못된 명령은 1, `init` 은 0 |

## 동작 특성

- 패키지 내부 import는 모두 상대 import를 사용한다.
- `queries`와 `all`은 수정/삭제 쿼리(Q13, Q14)의 영향이 누적되지 않도록 매번 DB를 재생성한다.
- `seed`는 스키마가 있는 DB 에서만 동작한다. 스키마가 없는 DB 에 단독 실행하면 `no such table: member` 오류와 종료 코드 1 로 끝난다. 항상 `init` 을 먼저 실행하거나 `all` 을 사용한다.
- `init` 과 `seed` 는 성공해도 아무것도 출력하지 않는다. 결과는 `queries` 또는 `all` 로 확인한다.
- 출력은 표 형태 텍스트이며, DML/DDL은 완료 메시지로 표시한다.
