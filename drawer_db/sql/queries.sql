-- Q1~Q4: 기본 조회
-- Q5~Q7: INNER JOIN
-- Q8: LEFT JOIN
-- Q9~Q11: 집계(GROUP BY)
-- Q12: 서브쿼리
-- Q13: UPDATE
-- Q14: DELETE
-- Q15: 인덱스
-- INNER JOIN 은 양쪽에 짝이 있는 행만 남기고 LEFT JOIN 은 왼쪽 행을 모두 남기며 짝이 없으면 오른쪽 컬럼이 NULL 이다.
-- GROUP BY 는 기준 컬럼 값이 같은 행을 한 묶음으로 만들고 집계 함수가 묶음마다 한 값을 낸다. COUNT(*) 는 행 수, COUNT(컬럼) 은 NULL 이 아닌 값만 센다, AVG 는 NULL 을 제외하고 평균한다, SELECT 의 비집계 컬럼은 GROUP BY 에 있어야 한다.
-- 각 쿼리 위의 `기대 결과` 줄은 seed.sql 기준 행 수다

-- [기대 결과] 10행
-- Q1. 회원 테이블에서 전체 회원을 이름 오름차순으로 조회한다.
SELECT id, name, email
FROM member
ORDER BY name ASC;

-- [기대 결과] 5행
-- Q2. 아직 반납되지 않은 대여 기록을 최신 대여일 순으로 5건 조회한다.
SELECT id, member_id, book_id, rented_at, returned_at, is_overdue
FROM rental
WHERE returned_at IS NULL
ORDER BY rented_at DESC
LIMIT 5;

-- [기대 결과] 3행
-- Q3. 연체 상태인 대여 기록만 대여일 오름차순으로 조회한다.
SELECT id, member_id, book_id, rented_at, returned_at, is_overdue
FROM rental
WHERE is_overdue = 1
ORDER BY rented_at ASC;

-- [기대 결과] 1행
-- Q4. 제목에 '왕자'가 포함된 도서를 조회한다.
SELECT id, title, category_id
FROM book
WHERE title LIKE '%왕자%'
ORDER BY id ASC;

-- [기대 결과] 12행
-- [INNER JOIN] 짝이 없는 회원·도서는 결과에서 빠진다. 모든 대여 기록이 유효한 회원을 가리키므로 12행이 그대로 남는다
-- Q5. INNER JOIN으로 대여 기록과 회원 정보를 함께 조회한다.
SELECT r.id AS rental_id, m.name AS member_name, r.book_id, r.rented_at, r.returned_at, r.is_overdue
FROM rental r
INNER JOIN member m ON r.member_id = m.id
ORDER BY r.id ASC;

-- [기대 결과] 12행
-- Q6. INNER JOIN으로 대여 기록과 도서 정보를 함께 조회한다.
SELECT r.id AS rental_id, b.title AS book_title, r.member_id, r.rented_at, r.returned_at, r.is_overdue
FROM rental r
INNER JOIN book b ON r.book_id = b.id
ORDER BY r.id ASC;

-- [기대 결과] 12행
-- [분해] 1) FROM rental r : 대여 12행에서 시작(컬럼 6개)
-- [분해] 2) INNER JOIN member m ON r.member_id = m.id : 회원 이름을 붙임, FK 라 버려지는 행 없이 12행(컬럼 9개)
-- [분해] 3) INNER JOIN book b ON r.book_id = b.id : 도서 제목을 붙임, 12행(컬럼 12개)
-- [분해] 4) SELECT : 필요한 5개 컬럼만 고르고 별칭을 붙임
-- [분해] 5) ORDER BY r.rented_at, r.id : 대여일, 같으면 id 순으로 정렬
-- [분해] 6) 결과 12행
-- Q7. INNER JOIN 3개 테이블로 회원별 대여 도서 목록을 조회한다.
SELECT r.id AS rental_id, m.name AS member_name, b.title AS book_title, r.rented_at, r.returned_at
FROM rental r
INNER JOIN member m ON r.member_id = m.id
INNER JOIN book b ON r.book_id = b.id
ORDER BY r.rented_at ASC, r.id ASC;

-- [기대 결과] 14행
-- [LEFT JOIN] 대여 기록이 없는 회원 id 9, 10 도 남고 rental 컬럼은 NULL 이 된다. 대여 12행 + 두 명 = 14행
-- Q8. LEFT JOIN으로 대여 기록이 없는 회원도 포함해 회원별 대여 현황을 조회한다.
SELECT m.id AS member_id, m.name AS member_name, r.id AS rental_id, r.book_id, r.rented_at
FROM member m
LEFT JOIN rental r ON m.id = r.member_id
ORDER BY m.id ASC, r.id ASC;

-- [기대 결과] 10행
-- [집계] COUNT(r.id) 는 NULL 을 세지 않아 대여가 없는 회원은 0 이 된다. COUNT(*) 였다면 LEFT JOIN 이 만든 NULL 행 1줄을 세어 1 이 되어 틀린다
-- Q9. GROUP BY와 COUNT로 회원별 대여 횟수를 집계한다.
SELECT m.id AS member_id, m.name AS member_name, COUNT(r.id) AS rental_count
FROM member m
LEFT JOIN rental r ON m.id = r.member_id
GROUP BY m.id, m.name
ORDER BY rental_count DESC, m.id ASC;

-- [기대 결과] 10행
-- Q10. GROUP BY와 COUNT로 카테고리별 도서 수를 집계한다.
SELECT c.id AS category_id, c.name AS category_name, COUNT(b.id) AS book_count
FROM category c
LEFT JOIN book b ON c.id = b.category_id
GROUP BY c.id, c.name
ORDER BY book_count DESC, c.id ASC;

-- [기대 결과] 4행
-- [집계] 반납되지 않은 건(returned_at IS NULL)은 기간을 계산할 수 없어 WHERE 로 먼저 제외한다. AVG 는 묶음마다 하나의 평균을 낸다
-- Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용)
SELECT m.id AS member_id, m.name AS member_name, AVG(julianday(r.returned_at) - julianday(r.rented_at)) AS avg_rental_days
FROM member m
INNER JOIN rental r ON m.id = r.member_id
WHERE r.returned_at IS NOT NULL
GROUP BY m.id, m.name
ORDER BY avg_rental_days DESC, m.id ASC;

-- [기대 결과] 2행
-- Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다.
SELECT id, name, email
FROM member
WHERE id NOT IN (
    SELECT member_id
    FROM rental
)
ORDER BY id ASC;

-- [기대 결과] 3행 수정
-- Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다.
UPDATE rental
SET is_overdue = 1
WHERE returned_at IS NULL
  AND rented_at < '2024-03-01';

-- [기대 결과] 1행 삭제
-- Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다.
DELETE FROM rental
WHERE id = 12;

-- [기대 결과] 인덱스 1개 생성(결과 행 없음)
-- [인덱스] WHERE member_id = ? 같은 조건에서 전체 스캔(SCAN) 대신 인덱스 탐색(SEARCH ... USING INDEX)으로 바뀐다. 전후 실행 계획은 results/explain_index.txt 에 있다
-- Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다.
CREATE INDEX IF NOT EXISTS idx_rental_member_id ON rental(member_id);
