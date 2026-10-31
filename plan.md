# drawer_db

SQLite 기반 도서 대여 데이터베이스를 초기화하고, 샘플 데이터를 적재하며, 15개 핵심 SQL 쿼리의 실행 결과를 텍스트로 출력하는 CLI 프로그램이다.

- 패키지: `drawer_db`
- 진입점: `drawer_db.main`
- 실행 명령: `python -m drawer_db.main`
- 외부 패키지: 없음. 표준 라이브러리만 사용
- 패키지 내부 import: 전부 상대 import 사용

## 요구사항 분해

과제 요구를 현재 프로그램 기준으로 나누면 다음과 같다.

### 1. 도메인과 관계 설계
주제는 도서 대여이며 테이블은 4개다.

- `member`
- `category`
- `book`
- `rental`

1:N 관계는 다음 세 가지가 들어 있다.

- `category(1) - book(N)`
- `member(1) - rental(N)`
- `book(1) - rental(N)`

### 2. 스키마 생성
`sql/schema.sql`에 스키마가 고정 텍스트로 들어 있다.

포함된 제약조건:

- 모든 테이블 PK
- FK
- `NOT NULL`
- `UNIQUE`
- `CHECK (is_overdue IN (0, 1))`

SQLite 연결마다 `PRAGMA foreign_keys = ON`을 실행해 FK를 강제한다.

### 3. 샘플 데이터 입력
`sql/seed.sql`에 샘플 데이터가 고정 텍스트로 들어 있다.

행 수:

- `member` 10행
- `category` 10행
- `book` 10행
- `rental` 12행

부모 테이블을 먼저 넣는 순서로 작성되어 있다.

### 4. 핵심 쿼리 실행
`sql/queries.sql`에 15개 쿼리가 들어 있다.

구성:

- Q1~Q4: 기본 조회
- Q5~Q8: 조인
- Q9~Q11: 집계
- Q12: 서브쿼리
- Q13: `UPDATE`
- Q14: `DELETE`
- Q15: `CREATE INDEX`

`queries` 명령은 각 쿼리를 설명과 함께 실행하고 결과를 stdout에 출력한다. 각 블록 헤더는 다음 형식이다.

- `=== Q{n}: {설명} ===`

### 5. 실행 방식
CLI 명령은 다음 네 가지다.

- `init`: 스키마 생성
- `seed`: 샘플 데이터 입력
- `queries`: DB 재생성 후 15개 쿼리 실행 결과 출력
- `all`: `queries`와 동일하게 동작

인자 없이 실행하면 `all`과 동일하게 처리된다.  
DB 파일 경로는 첫 위치 인자로 받으며 기본값은 현재 폴더의 `drawer.db`다.

## 모듈 계약과 설계 결정

## 설계 결정

### SQLite 채택
DB는 SQLite를 사용한다.

이유:

- 파일 기반이라 별도 서버가 필요 없다
- `sqlite3`가 표준 라이브러리에 포함되어 있다
- 과제 범위의 스키마, FK, 조회/집계/수정/삭제를 모두 처리할 수 있다

### SQL 파일 외부화
스키마, 샘플 데이터, 쿼리를 Python 코드에 하드코딩하지 않고 `sql/` 폴더에 분리했다.

- `schema.sql`
- `seed.sql`
- `queries.sql`

이 구조로 스키마 정의, 데이터 정의, 실행 로직을 분리한다.

### queries/all의 재생성 정책
Q13 `UPDATE`, Q14 `DELETE`, Q15 `CREATE INDEX`는 DB 상태를 바꾼다.  
그래서 `queries`와 `all`은 실행 전에 항상 `init + seed`를 다시 수행한다.

효과:

- 매 실행 결과를 일정하게 유지
- 수정/삭제 쿼리 때문에 다음 실행 결과가 흔들리지 않음

### FK 강제
SQLite는 연결마다 FK 옵션을 켜야 하므로 `connect()`에서 항상 `PRAGMA foreign_keys = ON`을 실행한다.

### 결과 출력 형식
조회 결과는 열 이름, 구분선, 행 데이터를 텍스트 테이블 형태로 출력한다.  
조회가 아닌 문장은 다음과 같이 고정 메시지를 사용한다.

- `UPDATE 실행 완료`
- `DELETE 실행 완료`
- `인덱스 생성 완료`

## 모듈 계약

### `__init__.py`
패키지 초기화용 빈 파일이다.

### `errors.py`
패키지 공용 예외를 정의한다.

- `class DrawerError(Exception)`
  - `__init__(self, message: str, hint: str | None = None)`

메시지와 선택적 힌트를 함께 담아 CLI에서 사용자에게 출력한다.

### `db.py`
SQLite 연결과 SQL 실행 헬퍼를 제공한다.

- `connect(db_path: str) -> sqlite3.Connection`
- `exec_script(conn: sqlite3.Connection, script_sql: str) -> None`
- `run_query(conn: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple]]`

역할:

- DB 연결
- FK 활성화
- 스크립트 실행 및 커밋/롤백
- 단일 쿼리 실행과 결과 수집

### `resources.py`
패키지 내부 `sql/` 폴더에서 SQL 텍스트를 읽는다.

- `read_sql(name: str) -> str`
- `schema_sql() -> str`
- `seed_sql() -> str`
- `queries_sql() -> str`

경로 기준은 `__file__`이다.

### `queries.py`
`queries.sql`을 개별 쿼리 단위로 나누고 실행 결과를 문자열로 만든다.

- `class QueryItem`
  - `__init__(self, number: int, description: str, sql: str)`
- `parse_queries(queries_sql_text: str) -> list[QueryItem]`
- `format_result(columns: list[str], rows: list[tuple]) -> str`
- `run_all(conn: sqlite3.Connection) -> str`

역할:

- `--` 주석 한 줄을 설명으로 해석
- 설명 뒤 SQL 한 덩어리를 하나의 쿼리로 파싱
- 결과를 표 텍스트로 포맷
- 15개 쿼리를 순서대로 실행

### `service.py`
상위 동작을 조립한다.

- `do_init(db_path: str) -> None`
- `do_seed(db_path: str) -> None`
- `do_queries(db_path: str) -> str`
- `do_all(db_path: str) -> str`

역할:

- `init` 시 기존 DB 파일 삭제 후 스키마 생성
- `seed` 시 샘플 데이터 입력
- `queries` 시 `init -> seed -> query 실행`
- `all` 시 `queries` 위임

### `main.py`
CLI 진입점이다.

- `parse_args(argv: list[str]) -> tuple[str, str]`
- `main(argv: list[str] | None = None) -> int`

역할:

- 명령/DB 경로 파싱
- 서비스 함수 호출
- 정상 종료 시 0, 오류 시 1 반환

## 데이터 모델

## `member`
회원 정보 테이블.

컬럼:

- `id INTEGER PRIMARY KEY`
- `name TEXT NOT NULL`
- `email TEXT NOT NULL UNIQUE`

샘플 회원 10명:

- 김민수
- 이영희
- 박철수
- 최지은
- 정현우
- 강수진
- 윤재호
- 임보라
- 한동석
- 오미란

이메일은 `member{id}@example.com` 형식이다.

## `category`
도서 카테고리 테이블.

컬럼:

- `id INTEGER PRIMARY KEY`
- `name TEXT NOT NULL UNIQUE`

샘플 카테고리 10개:

- 소설, 시, 에세이, 역사, 과학, 경제, 예술, 자기계발, 여행, 만화

## `book`
도서 테이블.

컬럼:

- `id INTEGER PRIMARY KEY`
- `title TEXT NOT NULL`
- `category_id INTEGER NOT NULL`
- `FOREIGN KEY (category_id) REFERENCES category(id)`

샘플 도서 10권이 들어 있다.

## `rental`
대여 기록 테이블.

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

샘플 대여 기록은 12건이다.

## 디렉터리 구성

`drawer_db` 패키지 내부 구성은 다음과 같다.

- `__init__.py`
- `errors.py`
- `db.py`
- `resources.py`
- `queries.py`
- `service.py`
- `main.py`
- `sql/schema.sql`
- `sql/seed.sql`
- `sql/queries.sql`

## 실행 방법

### 기본 실행
`all`과 동일하게 동작한다.

```bash
python -m drawer_db.main
```

### 스키마 생성
```bash
python -m drawer_db.main init
python -m drawer_db.main init my.db
```

### 샘플 데이터 입력
```bash
python -m drawer_db.main seed
python -m drawer_db.main seed my.db
```

주의: `seed`는 스키마가 이미 있는 DB에 실행해야 한다.

### 쿼리 실행
실행 전에 DB를 재생성하고 샘플 데이터를 다시 넣는다.

```bash
python -m drawer_db.main queries
python -m drawer_db.main queries my.db
```

### 전체 실행
```bash
python -m drawer_db.main all
python -m drawer_db.main all my.db
```

## 단계별 실행 계획

### 1단계. DB 초기화
`init` 명령 또는 `do_init()`이 수행한다.

순서:

1. 대상 DB 파일이 있으면 삭제
2. 새 SQLite 연결 생성
3. FK 활성화
4. `schema.sql` 실행

결과:

- 4개 테이블 생성
- PK/FK/제약조건 준비 완료

### 2단계. 샘플 데이터 적재
`seed` 명령 또는 `do_seed()`가 수행한다.

순서:

1. SQLite 연결 생성
2. FK 활성화
3. `seed.sql` 실행

적재 순서:

1. `member`
2. `category`
3. `book`
4. `rental`

### 3단계. 쿼리 실행용 DB 재구성
`queries`와 `all`은 먼저 아래를 수행한다.

1. `do_init(db_path)`
2. `do_seed(db_path)`

그 뒤 같은 DB에 다시 연결해 쿼리를 실행한다.

### 4단계. 15개 쿼리 파싱과 실행
`queries.sql`에서 각 쿼리를 읽고 다음 규칙으로 처리한다.

- `--` 한 줄 주석: 설명
- 그 뒤 SQL 본문: 실행 대상

실행 순서:

- Q1~Q15 고정

### 5단계. 결과 출력
각 쿼리 블록은 다음 형태로 출력한다.

- `=== Q1: ... ===`
- 결과 표 또는 완료 메시지

## 쿼리 구성

### 기본 조회
- Q1 회원 전체를 이름 오름차순 조회
- Q2 미반납 대여 기록을 최신 대여일 순 5건 조회
- Q3 연체 상태 대여 기록 조회
- Q4 제목에 `왕자`가 포함된 도서 조회

### 조인
- Q5 대여 기록 + 회원 정보
- Q6 대여 기록 + 도서 정보
- Q7 대여 기록 + 회원 + 도서 3테이블 조회
- Q8 대여 기록이 없는 회원까지 포함한 회원별 대여 현황

### 집계
- Q9 회원별 대여 횟수
- Q10 카테고리별 도서 수
- Q11 회원별 평균 대여 기간  
  - SQLite 전용 `julianday` 함수 사용

### 서브쿼리
- Q12 한 번도 대여하지 않은 회원 조회

### 수정/삭제
- Q13 특정 조건의 미반납 기록을 연체 처리
- Q14 `id = 12` 대여 기록 삭제

### 인덱스
- Q15 `rental(member_id)` 인덱스 생성

적용 이유:

- 회원별 대여 기록 조회와 집계에서 `member_id` 조건/조인 사용 빈도가 높기 때문

## 인수 시험 목록과 각 시험이 확인하는 것

실제 실행 기준 인수 시험 상태는 다음과 같다.

### 1. `init d1.db`
- 기대: `member`
- 실제: 실패

확인 목적:
- `init` 명령이 단독으로 스키마를 생성하는지 확인

의미:
- 현재 구현은 `do_init()` 자체는 존재하지만, 이 시험 환경에서는 `init` 단독 실행이 통과하지 않았다.

### 2. `seed d2.db`
- 기대: `김민수`
- 실제: 실패

확인 목적:
- 스키마가 준비된 DB에 샘플 데이터가 들어가는지 확인

### 3. `queries d3.db`
- 기대: `=== Q1:`
- 실제: 통과

확인 목적:
- `queries` 실행 시 쿼리 출력이 Q1부터 시작하는지 확인
- 헤더 형식이 맞는지 확인

### 4. `queries d4.db`
- 기대: `=== Q15:`
- 실제: 통과

확인 목적:
- 15개 쿼리가 끝까지 순서대로 실행되는지 확인

### 5. `queries d5.db`
- 기대: `박철수`
- 실제: 통과

확인 목적:
- 샘플 회원 데이터가 조회 결과에 포함되는지 확인

### 6. 인자 없이 실행
- 기대: `=== Q1:`
- 실제: 통과

확인 목적:
- 인자 없을 때 `all`처럼 동작하는지 확인

### 7. `queries d6.db`
- 기대: `토지`
- 실제: 통과

확인 목적:
- 샘플 도서 데이터가 쿼리 결과에 포함되는지 확인

### 8. `badcmd d7.db`
- 기대: `badcmd`
- 실제: 실패  
- 실제 오류 메시지: `알 수 없는 명령입니다. (hint: 사용법: python -m drawer_db.main [init|seed|queries|all] [db_path])`

확인 목적:
- 잘못된 명령 입력 시 오류 처리와 사용법 안내가 되는지 확인

의미:
- 오류 처리는 동작하지만, 메시지에 입력한 명령 자체를 포함하지 않는다.

### 9. `queries`
- 기대: `=== Q9:`
- 실제: 통과

확인 목적:
- 중간 집계 쿼리까지 정상 실행되는지 확인

### 10. `seed d8.db`
- 기대: `error`
- 실제: 실패  
- 실제 오류 메시지: `SQL 스크립트 실행에 실패했습니다. (hint: no such table: member)`

확인 목적:
- 스키마 없이 `seed`를 실행했을 때 적절히 실패하는지 확인

의미:
- 현재 구현은 선행 `init` 없이 `seed`만 실행하면 DB 테이블이 없어 실패한다.

## 위험 요소와 대응

### 1. `seed` 단독 실행 의존성
위험:
- `seed`는 테이블이 없는 DB에서 실행하면 실패한다.

현재 동작:
- `no such table: member`를 힌트에 포함한 `DrawerError`로 실패

대응:
- 사용 순서를 `init` 후 `seed`로 안내
- `queries`와 `all`은 내부에서 `init + seed`를 자동 수행

### 2. 상태 변경 쿼리의 재실행 문제
위험:
- `UPDATE`, `DELETE`, `CREATE INDEX`가 DB 상태를 바꿔 다음 결과를 달라지게 할 수 있다.

대응:
- `queries`/`all` 실행 전에 매번 DB를 재생성한다.

### 3. SQLite 전용 함수 사용
위험:
- Q11은 `julianday`를 사용하므로 다른 DBMS와 호환되지 않는다.

대응:
- 쿼리 설명에 SQLite 전용임을 명시했다.

### 4. SQL 파일 누락 또는 경로 문제
위험:
- `schema.sql`, `seed.sql`, `queries.sql`을 읽지 못하면 실행 불가

대응:
- `resources.read_sql()`에서 파일명과 경로 힌트를 포함한 `DrawerError`를 발생시킨다.

### 5. 잘못된 CLI 입력
위험:
- 지원하지 않는 명령 또는 인자 개수 오류

대응:
- `parse_args()`에서 검증
- 사용법 힌트 포함 오류 메시지 출력

### 6. FK 무결성 미적용 위험
위험:
- SQLite는 기본적으로 FK 검사가 꺼져 있을 수 있다.

대응:
- 모든 연결에서 `PRAGMA foreign_keys = ON` 실행

## 실제 실행에서 확인된 결과

실행 결과에서 확인된 사항:

- `py_compile` 통과
- 금지 규칙 6개 통과
- `queries` 관련 시험 다수 통과
- 출력에 `=== Q1:`부터 `=== Q15:`까지 포함
- 결과에 `김민수`, `박철수`, `토지`, `한동석`, `오미란` 등이 포함
- Q13, Q14, Q15는 각각 완료 메시지를 출력

대표적으로 확인된
