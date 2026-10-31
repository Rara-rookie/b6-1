INSERT INTO member (id, name, email) VALUES
  (1, '김민수', 'member1@example.com'),
  (2, '이영희', 'member2@example.com'),
  (3, '박철수', 'member3@example.com'),
  (4, '최지은', 'member4@example.com'),
  (5, '정현우', 'member5@example.com'),
  (6, '강수진', 'member6@example.com'),
  (7, '윤재호', 'member7@example.com'),
  (8, '임보라', 'member8@example.com'),
  (9, '한동석', 'member9@example.com'),
  (10, '오미란', 'member10@example.com');

INSERT INTO category (id, name) VALUES
  (1, '소설'),
  (2, '시'),
  (3, '에세이'),
  (4, '역사'),
  (5, '과학'),
  (6, '경제'),
  (7, '예술'),
  (8, '자기계발'),
  (9, '여행'),
  (10, '만화');

INSERT INTO book (id, title, category_id) VALUES
  (1, '토지', 1),
  (2, '데미안', 1),
  (3, '진달래꽃', 2),
  (4, '어린왕자', 1),
  (5, '코스모스', 5),
  (6, '총균쇠', 4),
  (7, '국부론', 6),
  (8, '아프니까청춘이다', 8),
  (9, '먼나라이웃나라', 10),
  (10, '나미야잡화점의기적', 1);

INSERT INTO rental (id, member_id, book_id, rented_at, returned_at, is_overdue) VALUES
  (1, 1, 1, '2024-01-05', '2024-01-15', 0),
  (2, 2, 2, '2024-01-10', NULL, 0),
  (3, 3, 3, '2024-02-01', NULL, 1),
  (4, 1, 5, '2024-02-10', '2024-02-20', 0),
  (5, 4, 6, '2024-02-15', NULL, 1),
  (6, 5, 4, '2024-03-01', '2024-03-05', 0),
  (7, 2, 7, '2024-03-10', NULL, 0),
  (8, 6, 8, '2024-03-12', '2024-03-22', 0),
  (9, 1, 9, '2024-03-15', NULL, 1),
  (10, 7, 10, '2024-03-20', '2024-03-30', 0),
  (11, 8, 1, '2024-04-01', NULL, 0),
  (12, 3, 2, '2024-04-05', NULL, 0);
