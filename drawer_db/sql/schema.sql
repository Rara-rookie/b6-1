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
