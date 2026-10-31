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
python -m drawer_db.main seed d2.db
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

`results/` 폴더에 쿼리 15개의 실행 결과를 텍스트로 남긴다.

| 파일 | 내용 |
|---|---|
| `results/all_queries.txt` | `python -m drawer_db.main all drawer.db` 전체 출력 |
| `results/Q01.txt` ~ `results/Q15.txt` | 쿼리별 설명 헤더와 결과 표 |

`all` 은 매번 DB 를 새로 만들므로 같은 명령을 다시 실행하면 같은 결과가 나온다.

## 동작 특성

- 패키지 내부 import는 모두 상대 import를 사용한다.
- `queries`와 `all`은 수정/삭제 쿼리(Q13, Q14)의 영향이 누적되지 않도록 매번 DB를 재생성한다.
- `seed`는 스키마가 없는 DB에 단독 실행하면 실패할 수 있다.
- 출력은 표 형태 텍스트이며, DML/DDL은 완료 메시지로 표시한다.
