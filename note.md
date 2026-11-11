# drawer_db

SQLite 기반 도서 대여 데이터베이스 실습용 CLI 프로그램이다.  
스키마 생성, 샘플 데이터 입력, 핵심 SQL 15개 실행을 표준 라이브러리만으로 수행한다.

## 실행 방법

진입점:

- `python -m drawer_db.main`

명령 형식:

- `python -m drawer_db.main [init|seed|queries|all] [db_path]`

동작 규칙:

- 인자 없이 실행하면 `all`과 동일하게 동작한다.
- DB 파일 경로를 생략하면 기본값은 `drawer.db`이다.
- `queries`와 `all`은 실행 전에 항상 DB를 다시 만들고 샘플 데이터를 다시 넣은 뒤 Q1~Q15를 실행한다.

예시:

- `python -m drawer_db.main`
- `python -m drawer_db.main all`
- `python -m drawer_db.main init sample.db`
- `python -m drawer_db.main seed sample.db`
- `python -m drawer_db.main queries sample.db`

## 주제와 데이터 모델

주제는 도서 대여다.

테이블은 4개다.

- `member`: 회원
- `category`: 도서 카테고리
- `book`: 도서
- `rental`: 대여 기록

관계는 다음과 같다.

- `category (1) - book (N)`
- `member (1) - rental (N)`
- `book (1) - rental (N)`

이 구조는 “같은 정보를 반복 저장하지 않고”, 필요한 순간에 JOIN으로 연결해서 조회하기 위한 설계다.  
엑셀 한 장에 회원명, 카테고리명, 책 제목, 대여일을 모두 반복 저장하면 수정 시 불일치가 생기기 쉽다.  
반대로 테이블을 역할별로 나누고 PK/FK로 연결하면 중복을 줄이고 무결성을 유지할 수 있다.

## 이 과제로 배우는 개념의 원리와 이유

### 1. PK / FK / 1:N 관계

- PK(기본 키)는 각 행을 유일하게 식별한다.
- FK(외래 키)는 다른 테이블의 PK를 참조한다.
- 1:N 관계는 “하나의 부모 데이터에 여러 자식 데이터가 연결되는 구조”다.

이 프로그램에서는:

- `category.id` ← `book.category_id`
- `member.id` ← `rental.member_id`
- `book.id` ← `rental.book_id`

이 연결 덕분에 카테고리 없는 책, 회원 없는 대여 기록, 책 없는 대여 기록을 막을 수 있다.

근거 파일:

- `drawer_db/sql/schema.sql`

### 2. 제약조건과 무결성

제약조건은 잘못된 데이터를 DB 레벨에서 차단하기 위한 규칙이다.

적용된 제약조건:

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
- `CHECK`
  - `rental.is_overdue IN (0, 1)`
- `FOREIGN KEY`
  - `book.category_id → category(id)`
  - `rental.member_id → member(id)`
  - `rental.book_id → book(id)`

FK가 실제로 동작하도록 커넥션마다 `PRAGMA foreign_keys = ON`을 실행한다.

근거 파일:

- `drawer_db/sql/schema.sql`
- `drawer_db/db.py`

### 3. SELECT / INSERT / UPDATE / DELETE

SQL은 역할별로 나뉜다.

- `SELECT`: 조회
- `INSERT`: 데이터 입력
- `UPDATE`: 기존 데이터 수정
- `DELETE`: 기존 데이터 삭제

이 프로그램은 그 흐름을 모두 포함한다.

- 스키마 생성: `schema.sql`
- 샘플 입력: `seed.sql`
- 조회/조인/집계/서브쿼리/수정/삭제/인덱스: `queries.sql`

### 4. JOIN이 필요한 이유

테이블을 나누면 중복은 줄지만, 조회할 때 연결이 필요하다.  
JOIN은 분리 저장된 데이터를 한 번에 묶어서 보여준다.

예:

- 대여 기록 + 회원 이름
- 대여 기록 + 도서 제목
- 회원 + 대여 유무
- 카테고리 + 도서 수

이 구현에서는 `INNER JOIN`과 `LEFT JOIN`을 모두 사용한다.

### 5. GROUP BY와 집계

실무에서는 “몇 건인지”, “평균이 얼마인지”, “카테고리별로 어떻게 나뉘는지”를 자주 본다.  
`GROUP BY`는 같은 기준끼리 묶고, `COUNT`, `AVG` 같은 집계 함수는 그 묶음에 대한 숫자를 계산한다.

이 프로그램은 다음을 집계한다.

- 회원별 대여 횟수
- 카테고리별 도서 수
- 회원별 평균 대여 기간

### 6. 인덱스가 필요한 이유

인덱스는 조회 시 특정 컬럼을 더 빨리 찾기 위한 보조 구조다.  
대여 기록에서 회원 기준 조회가 자주 일어날 수 있으므로 `rental(member_id)`에 인덱스를 만든다.

근거 파일:

- `drawer_db/sql/queries.sql` Q15

## 구현이 개념을 어디서 어떻게 쓰는지

## 패키지 구조

- `drawer_db/__init__.py`
- `drawer_db/errors.py`
- `drawer_db/db.py`
- `drawer_db/resources.py`
- `drawer_db/queries.py`
- `drawer_db/service.py`
- `drawer_db/main.py`
- `drawer_db/sql/schema.sql`
- `drawer_db/sql/seed.sql`
- `drawer_db/sql/queries.sql`

## 모듈별 역할

### `drawer_db/main.py`

CLI 진입점이다.

- 명령과 DB 경로를 파싱한다.
- `init`, `seed`, `queries`, `all`을 분기한다.
- 인자 없으면 `all`로 처리한다.
- 잘못된 명령은 `DrawerError`로 안내한다.

핵심 함수:

- `parse_args(argv)`
- `main(argv=None)`

### `drawer_db/service.py`

상위 동작을 조립한다.

- `do_init(db_path)`: 기존 DB 파일이 있으면 삭제 후 스키마 생성
- `do_seed(db_path)`: 샘플 데이터 입력
- `do_queries(db_path)`: 매번 `init + seed` 후 쿼리 실행
- `do_all(db_path)`: `do_queries` 호출

여기서 `queries` 실행 전에 재초기화하는 이유는 Q13 `UPDATE`, Q14 `DELETE`, Q15 `CREATE INDEX`가 데이터 상태를 바꾸기 때문이다.

### `drawer_db/db.py`

SQLite 연결과 실행 헬퍼를 담당한다.

- `connect(db_path)`
  - `sqlite3.connect`
  - `PRAGMA foreign_keys = ON`
- `exec_script(conn, script_sql)`
  - 여러 SQL 문 실행
  - 실패 시 rollback
- `run_query(conn, sql)`
  - 결과 컬럼명과 행 반환

### `drawer_db/resources.py`

패키지 내부 `sql/` 폴더에서 SQL 텍스트를 읽는다.

- `schema_sql()`
- `seed_sql()`
- `queries_sql()`

실행 SQL이 파일에 고정되어 있어, 코드와 제출물의 근거를 분리해서 확인하기 쉽다.

### `drawer_db/queries.py`

`queries.sql`을 읽고 개별 쿼리로 나눈 뒤 결과를 텍스트로 포맷한다.

- `QueryItem`
- `parse_queries(queries_sql_text)`
- `format_result(columns, rows)`
- `run_all(conn)`

출력 형식은 각 쿼리마다 다음 헤더를 사용한다.

- `=== Q{n}: {설명} ===`

## SQL 파일 구성

### `drawer_db/sql/schema.sql`

스키마 정의 파일이다.

포함 내용:

- `DROP TABLE IF EXISTS`
- `CREATE TABLE member`
- `CREATE TABLE category`
- `CREATE TABLE book`
- `CREATE TABLE rental`
- PK / FK / NOT NULL / UNIQUE / CHECK

### `drawer_db/sql/seed.sql`

샘플 데이터 입력 파일이다.

입력 순서:

1. `member` 10행
2. `category` 10행
3. `book` 10행
4. `rental` 12행

부모 테이블을 먼저 넣는 이유는 FK 참조가 있기 때문이다.

포함된 실제 데이터 예:

- 회원: `김민수`, `이영희`, `박철수` ...
- 카테고리: `소설`, `시`, `에세이` ...
- 도서: `토지`, `데미안`, `어린왕자`, `코스모스` ...
- 대여 기록 12건

### `drawer_db/sql/queries.sql`

핵심 SQL 15개를 담는다.

구성:

- Q1~Q4: 기본 조회
- Q5~Q8: 조인
- Q9~Q11: 집계
- Q12: 서브쿼리
- Q13: UPDATE
- Q14: DELETE
- Q15: CREATE INDEX

Q11은 SQLite 전용 `julianday` 함수를 사용한다는 설명이 SQL 주석에 포함되어 있다.

## 15개 쿼리 요약

### 기본 조회

- Q1 회원 전체를 이름 오름차순 조회
- Q2 미반납 대여 기록을 최신 대여일 순 5건 조회
- Q3 연체 대여 기록 조회
- Q4 제목에 `왕자`가 포함된 도서 조회

### 조인

- Q5 대여 기록 + 회원 정보
- Q6 대여 기록 + 도서 정보
- Q7 대여 기록 + 회원 + 도서 3테이블 조인
- Q8 회원 기준 LEFT JOIN으로 대여 없는 회원까지 포함

### 집계

- Q9 회원별 대여 횟수
- Q10 카테고리별 도서 수
- Q11 회원별 평균 대여 기간

### 서브쿼리

- Q12 한 번도 대여하지 않은 회원 조회

### 수정 / 삭제 / 인덱스

- Q13 특정 조건의 미반납 기록을 연체 처리
- Q14 `id = 12` 대여 기록 삭제
- Q15 `rental(member_id)` 인덱스 생성

## 평가자가 물을 만한 질문과 답

### Q. 왜 테이블을 4개로 나눴나?

회원, 카테고리, 도서, 대여 기록은 역할이 다르기 때문이다.  
도서의 카테고리와 회원의 개인정보를 대여 기록마다 반복 저장하면 중복과 불일치가 생긴다.  
분리 후 FK로 연결하면 정합성을 유지하면서 JOIN으로 다시 묶어 조회할 수 있다.

근거:

- `drawer_db/sql/schema.sql`

### Q. 1:N 관계는 어디에 있나?

- `category.id` 하나에 여러 `book.category_id`
- `member.id` 하나에 여러 `rental.member_id`
- `book.id` 하나에 여러 `rental.book_id`

### Q. FK가 실제로 강제된다는 근거는?

`connect()`에서 커넥션마다 `PRAGMA foreign_keys = ON`을 실행한다.

근거:

- `drawer_db/db.py`

### Q. `seed`가 부모 테이블부터 들어가야 하는 이유는?

자식 테이블의 FK 값은 부모 PK가 먼저 존재해야 참조할 수 있기 때문이다.  
예를 들어 `rental.member_id`는 `member.id`가 먼저 있어야 한다.

근거:

- `drawer_db/sql/seed.sql`

### Q. `LEFT JOIN`은 왜 썼나?

대여 기록이 없는 회원도 결과에 포함하려고 사용했다.  
`INNER JOIN`이면 대여가 없는 회원은 빠진다.  
Q8과 Q9에서 이 차이를 확인할 수 있다.

근거:

- `drawer_db/sql/queries.sql`

### Q. 서브쿼리는 어디에 쓰였나?

Q12에서 `rental`에 한 번도 등장하지 않은 `member.id`를 찾는 데 사용했다.

근거:

- `drawer_db/sql/queries.sql`

### Q. 평균 대여 기간은 어떻게 계산했나?

Q11에서 반납된 건만 대상으로 `AVG(julianday(returned_at) - julianday(rented_at))`를 사용했다.  
`julianday`는 SQLite 전용 함수다.

근거:

- `drawer_db/sql/queries.sql`

### Q. 왜 `queries`가 매번 DB를 다시 만드나?

Q13, Q14, Q15는 상태를 바꾼다.  
재실행 시 결과가 달라지지 않도록 `do_queries()`가 먼저 `do_init()`과 `do_seed()`를 호출한다.

근거:

- `drawer_db/service.py`

### Q. 인덱스는 왜 `rental(member_id)`에 만들었나?

회원별 대여 현황, 회원별 집계처럼 `member_id` 기준 조회가 자연스럽기 때문이다.  
대여 테이블이 커질수록 이 컬럼의 검색 비용을 줄이는 의미가 있다.

근거:

- `drawer_db/sql/queries.sql` Q15

### Q. `seed d8.db`가 실패한 이유는?

`seed`는 스키마를 자동 생성하지 않는다.  
테이블이 없는 DB에 바로 `seed`를 실행하면 `member` 테이블이 없어서 실패한다.

실제 출력:

- `SQL 스크립트 실행에 실패했습니다. (hint: no such table: member)`

## 근거가 되는 파일 경로와 실행 출력

## 파일 경로 근거

- 스키마: `drawer_db/sql/schema.sql`
- 샘플 데이터: `drawer_db/sql/seed.sql`
- 쿼리 15개: `drawer_db/sql/queries.sql`
- FK 활성화 및 SQL 실행: `drawer_db/db.py`
- 쿼리 파싱/출력 포맷: `drawer_db/queries.py`
- 명령 조립: `drawer_db/service.py`
- CLI 진입점: `drawer_db/main.py`

## 실제 실행 출력 근거

다음 출력이 확인되었다.

### `python -m drawer_db.main queries d3.db`

출력 일부:

- `=== Q11: Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용) ===`
- `1 | 김민수 | 10.0`
- `6 | 강수진 | 10.0`
- `7 | 윤재호 | 10.0`
- `5 | 정현우 | 4.0`

이 출력은 Q11이 실제로 집계와 SQLite 날짜 함수를 사용함을 보여준다.

### 같은 실행에서 Q12 결과

- `=== Q12: Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다. ===`
- `9  | 한동석  | member9@example.com`
- `10 | 오미란  | member10@example.com`

이 출력은 서브쿼리로 “대여 기록이 없는 회원”을 찾는 결과다.

### 같은 실행에서 Q13~Q15 결과

- `=== Q13: ... ===`
- `UPDATE 실행 완료`

- `=== Q14: ... ===`
- `DELETE 실행 완료`

- `=== Q15: ... ===`
- `인덱스 생성 완료`

이 출력은 수정, 삭제, 인덱스 생성이 실제 실행됨을 보여준다.

### 기본 실행

- `python -m drawer_db.main`
- 결과에 `=== Q1:` 포함

인자 없이 실행하면 `all`처럼 동작한다는 근거다.

### 잘못된 명령 실행

- `python -m drawer_db.main badcmd d7.db`

실제 출력:

- `알 수 없는 명령입니다. (hint: 사용법: python -m drawer_db.main [init|seed|queries|all] [db_path])`

이 출력은 CLI가 허용 명령만 받도록 검증함을 보여준다.

### 스키마 없이 seed 실행

- `python -m drawer_db.main seed d8.db`

실제 출력:

- `SQL 스크립트 실행에 실패했습니다. (hint: no such table: member)`

이 출력은 스키마가 먼저 필요하다는 점과 예외 처리가 동작함을 보여준다.

## 확인할 수 있는 실제 데이터 예

샘플 데이터 기준으로 확인 가능한 값들:

- 회원명: `김민수`, `박철수`, `한동석`, `오미란`
- 도서명: `토지`, `데미안`, `어린왕자`, `코스모스`
- 카테고리명: `소설`, `과학`, `자기계발`, `만화`

실행 결과 근거에는 다음 문자열이 포함된다.

- `박철수`
- `토지`
- `=== Q1:`
- `=== Q15:`

## 제한 사항

구현에 포함되지 않은 것:

- 백엔드 프레임워크
- View
- Trigger
- Procedure
- 외부 패키지

사용 기술은 다음으로 제한된다.

- Python 표준 라이브러리
- SQLite
- `sqlite3`

## 제출물 관점에서 보는 대응

과제 요구 항목과 대응되는 실제 구성은 다음과 같다.

- 스키마 생성 SQL: `drawer_db/sql/schema.sql`
- 샘플 데이터 INSERT SQL: `drawer_db/sql/seed.sql`
- 쿼리 SQL: `drawer_db/sql/queries.sql`
- 실행 결과 텍스트: `python -m drawer_db.main queries [db_path]` 출력

이 프로그램은 SQL 파일과 실행
