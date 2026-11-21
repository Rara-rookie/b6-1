-- [설계 요약]
-- 관계 저장: 엑셀은 시트마다 관련 값을 복사해 적기 쉽지만 관계형 DB 는 FK 로 다른 테이블의 행을 참조하므로 한 곳만 고치면 연결된 의미가 함께 유지된다.
-- 중복: 엑셀은 같은 카테고리 이름이 도서 행마다 반복되기 쉽지만 DB 는 category 테이블의 한 행만 두고 book 이 그 id 를 참조한다.
-- 무결성: 엑셀은 잘못된 값 입력을 막기 어렵지만 DB 는 NOT NULL·UNIQUE·CHECK·FK 제약으로 잘못된 데이터를 거부할 수 있다.
-- 재현: 엑셀은 수작업 순서에 따라 결과가 달라지기 쉽지만 DB 는 SQL 스크립트로 같은 구조와 데이터를 다시 만들 수 있다.
-- 정규화 트레이드오프: 중복이 줄고 수정이 한 곳에서 끝나도록 테이블을 나누는 대신 조회할 때는 흩어진 정보를 다시 JOIN 해야 한다.
-- 정규화 트레이드오프: 쓰기 일관성을 얻는 대신 읽기 쿼리는 더 길어질 수 있으므로 자주 함께 보는 정보는 조인 비용을 이해하고 설계해야 한다.
-- FK 정책: ON DELETE 를 따로 지정하지 않았으므로 기본값(NO ACTION)이 적용되어 대여 기록이 있는 회원·도서는 삭제가 거부된다.
-- PK/FK 구분: PK 는 각 행을 유일하게 식별하는 기준 키이고 FK 는 다른 테이블의 PK 를 가리켜 관계를 만든다.
-- 예시 쿼리: r.member_id = m.id 는 rental 의 FK 가 member 의 PK 를 가리킨다는 뜻이다.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS rental;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS category;

-- 회원: 도서 대여 대상인 사람들의 정보 관리
CREATE TABLE member (
    id INTEGER PRIMARY KEY, -- 엔티티 정체성: 행을 유일하게 식별하는 기본키
    name TEXT NOT NULL, -- 회원 이름, 문자열 저장
    email TEXT NOT NULL UNIQUE -- 회원 이메일, 중복 불가, 고유 연락처 식별
);

-- 카테고리: 도서의 분류 체계 저장소
CREATE TABLE category (
    id INTEGER PRIMARY KEY, -- 엔티티 정체성: 행을 유일하게 식별하는 기본키
    name TEXT NOT NULL UNIQUE -- 카테고리 이름은 중복 불가, 문자열 저장
);

-- 도서: 대여 가능한 책들의 정보 저장
-- 정규화: 카테고리 이름을 반복 저장하지 않고 category_id 로만 참조(1NF·2NF·3NF)
CREATE TABLE book (
    id INTEGER PRIMARY KEY, -- 엔티티 정체성: 행을 유일하게 식별하는 기본키
    title TEXT NOT NULL, -- 도서 제목, 문자열 저장
    category_id INTEGER NOT NULL, -- 카테고리 테이블의 행을 가리키는 외래키 참조
    FOREIGN KEY (category_id) REFERENCES category(id)
);

-- 대여 기록: 회원이 언제 어느 책을 빌렸는지, 반납했는지, 연체 여부 기록
-- 정규화: 회원 정보·도서 정보·카테고리 정보를 반복 저장하지 않고 member_id·book_id 로만 참조(1NF·2NF·3NF)
CREATE TABLE rental (
    id INTEGER PRIMARY KEY, -- 엔티티 정체성: 행을 유일하게 식별하는 기본키
    member_id INTEGER NOT NULL, -- 회원 테이블의 행을 가리키는 외래키 참조
    book_id INTEGER NOT NULL, -- 도서 테이블의 행을 가리키는 외래키 참조
    rented_at DATE NOT NULL, -- 대여 날짜, SQLite 에 DATE 타입이 없어 ISO 8601 형식('YYYY-MM-DD') 텍스트로 저장하면 문자열 비교와 julianday() 함수로 날짜 계산 가능
    returned_at DATE, -- 반납 날짜, NULL 이면 미반납, 같은 이유로 텍스트 저장
    is_overdue INTEGER NOT NULL, -- SQLite 에 BOOLEAN 타입이 없어 INTEGER 0(정상) 또는 1(연체)로 저장
    FOREIGN KEY (member_id) REFERENCES member(id),
    FOREIGN KEY (book_id) REFERENCES book(id),
    CHECK (is_overdue IN (0, 1)) -- is_overdue 값이 0 또는 1 만 허용
);
