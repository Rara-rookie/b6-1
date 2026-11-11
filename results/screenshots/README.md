# 실행 결과 스크린샷

모든 이미지는 같은 이름의 텍스트 원본을 `scripts/render_captures.py` 로 터미널 화면 형태로 그린 것이다.
텍스트 원본은 `scripts/capture_evidence.py` 와 `python -m drawer_db.main all` 이 실제 명령을 실행해 만든다.

## 쿼리 15개 실행 결과

| 이미지 | 내용 | 텍스트 원본 |
|---|---|---|
| ![Q01](Q01.png) | Q1 실행 결과 | `../Q01.txt` |
| ![Q02](Q02.png) | Q2 실행 결과 | `../Q02.txt` |
| ![Q03](Q03.png) | Q3 실행 결과 | `../Q03.txt` |
| ![Q04](Q04.png) | Q4 실행 결과 | `../Q04.txt` |
| ![Q05](Q05.png) | Q5 실행 결과 | `../Q05.txt` |
| ![Q06](Q06.png) | Q6 실행 결과 | `../Q06.txt` |
| ![Q07](Q07.png) | Q7 실행 결과 | `../Q07.txt` |
| ![Q08](Q08.png) | Q8 실행 결과 | `../Q08.txt` |
| ![Q09](Q09.png) | Q9 실행 결과 | `../Q09.txt` |
| ![Q10](Q10.png) | Q10 실행 결과 | `../Q10.txt` |
| ![Q11](Q11.png) | Q11 실행 결과 | `../Q11.txt` |
| ![Q12](Q12.png) | Q12 실행 결과 | `../Q12.txt` |
| ![Q13](Q13.png) | Q13 실행 결과 | `../Q13.txt` |
| ![Q14](Q14.png) | Q14 실행 결과 | `../Q14.txt` |
| ![Q15](Q15.png) | Q15 실행 결과 | `../Q15.txt` |
| ![all_queries](all_queries.png) | 전체 실행 출력(`python -m drawer_db.main all`) | `../all_queries.txt` |

## 명령 실행 증거

| 이미지 | 보여주는 것 | 텍스트 원본 |
|---|---|---|
| ![init, seed](evidence_01_init_seed.png) | `init`, `seed` 단독 실행과 테이블별 행 수(10, 10, 10, 12) | `../evidence/01_init_seed.txt` |
| ![seed without schema](evidence_02_seed_without_schema.png) | 스키마 없는 DB 에 `seed` 하면 `no such table: member`, 종료 코드 1 | `../evidence/02_seed_without_schema.txt` |
| ![FK violation](evidence_03_fk_violation.png) | FK·UNIQUE·CHECK 위반이 `IntegrityError` 로 거부됨 | `../evidence/03_fk_violation.txt` |
| ![unittest](evidence_04_unittest.png) | 자동 시험 7건 통과 | `../evidence/04_unittest.txt` |
| ![all run](evidence_05_all_run.png) | `all` 실행(앞부분)과 종료 코드 0 | `../evidence/05_all_run.txt` |
| ![explain index](evidence_06_explain_index.png) | Q15 인덱스 전후 실행 계획(`SCAN` → `SEARCH ... USING INDEX`) | `../evidence/06_explain_index.txt` |

## 다시 만들기

```bash
python scripts/capture_evidence.py
python scripts/render_captures.py   # Pillow 필요: pip install pillow
```
