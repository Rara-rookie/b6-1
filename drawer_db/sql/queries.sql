-- Q1. 회원 테이블에서 전체 회원을 이름 오름차순으로 조회한다.
SELECT id, name, email
FROM member
ORDER BY name ASC;

-- Q2. 아직 반납되지 않은 대여 기록을 최신 대여일 순으로 5건 조회한다.
SELECT id, member_id, book_id, rented_at, returned_at, is_overdue
FROM rental
WHERE returned_at IS NULL
ORDER BY rented_at DESC
LIMIT 5;

-- Q3. 연체 상태인 대여 기록만 대여일 오름차순으로 조회한다.
SELECT id, member_id, book_id, rented_at, returned_at, is_overdue
FROM rental
WHERE is_overdue = 1
ORDER BY rented_at ASC;

-- Q4. 제목에 '왕자'가 포함된 도서를 조회한다.
SELECT id, title, category_id
FROM book
WHERE title LIKE '%왕자%'
ORDER BY id ASC;

-- Q5. INNER JOIN으로 대여 기록과 회원 정보를 함께 조회한다.
SELECT r.id AS rental_id, m.name AS member_name, r.book_id, r.rented_at, r.returned_at, r.is_overdue
FROM rental r
INNER JOIN member m ON r.member_id = m.id
ORDER BY r.id ASC;

-- Q6. INNER JOIN으로 대여 기록과 도서 정보를 함께 조회한다.
SELECT r.id AS rental_id, b.title AS book_title, r.member_id, r.rented_at, r.returned_at, r.is_overdue
FROM rental r
INNER JOIN book b ON r.book_id = b.id
ORDER BY r.id ASC;

-- Q7. INNER JOIN 3개 테이블로 회원별 대여 도서 목록을 조회한다.
SELECT r.id AS rental_id, m.name AS member_name, b.title AS book_title, r.rented_at, r.returned_at
FROM rental r
INNER JOIN member m ON r.member_id = m.id
INNER JOIN book b ON r.book_id = b.id
ORDER BY r.rented_at ASC, r.id ASC;

-- Q8. LEFT JOIN으로 대여 기록이 없는 회원도 포함해 회원별 대여 현황을 조회한다.
SELECT m.id AS member_id, m.name AS member_name, r.id AS rental_id, r.book_id, r.rented_at
FROM member m
LEFT JOIN rental r ON m.id = r.member_id
ORDER BY m.id ASC, r.id ASC;

-- Q9. GROUP BY와 COUNT로 회원별 대여 횟수를 집계한다.
SELECT m.id AS member_id, m.name AS member_name, COUNT(r.id) AS rental_count
FROM member m
LEFT JOIN rental r ON m.id = r.member_id
GROUP BY m.id, m.name
ORDER BY rental_count DESC, m.id ASC;

-- Q10. GROUP BY와 COUNT로 카테고리별 도서 수를 집계한다.
SELECT c.id AS category_id, c.name AS category_name, COUNT(b.id) AS book_count
FROM category c
LEFT JOIN book b ON c.id = b.category_id
GROUP BY c.id, c.name
ORDER BY book_count DESC, c.id ASC;

-- Q11. AVG와 GROUP BY로 회원별 평균 대여 기간(반납된 건만)을 계산한다. (SQLite 전용: julianday 함수 사용)
SELECT m.id AS member_id, m.name AS member_name, AVG(julianday(r.returned_at) - julianday(r.rented_at)) AS avg_rental_days
FROM member m
INNER JOIN rental r ON m.id = r.member_id
WHERE r.returned_at IS NOT NULL
GROUP BY m.id, m.name
ORDER BY avg_rental_days DESC, m.id ASC;

-- Q12. 서브쿼리로 한 번도 대여하지 않은 회원을 조회한다.
SELECT id, name, email
FROM member
WHERE id NOT IN (
    SELECT member_id
    FROM rental
)
ORDER BY id ASC;

-- Q13. 반납일이 없고 대여일이 2024-03-01 이전인 기록을 연체 상태로 수정한다.
UPDATE rental
SET is_overdue = 1
WHERE returned_at IS NULL
  AND rented_at < '2024-03-01';

-- Q14. 테스트용으로 id가 12인 대여 기록을 삭제한다.
DELETE FROM rental
WHERE id = 12;

-- Q15. 조회 성능 향상을 위해 rental(member_id) 컬럼에 인덱스를 생성한다.
CREATE INDEX IF NOT EXISTS idx_rental_member_id ON rental(member_id);
