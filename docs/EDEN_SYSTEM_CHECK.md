# 에덴 시스템 점검 (solar/eden)

**점검일**: 문서 작성 시점  
**목적**: solar 폴더 내 에덴(Eden) 시스템 구현 상태·연동·데모를 한 번에 점검한다.

---

## 1. 구조 요약

| 경로 | 역할 |
|------|------|
| **solar/eden/** | 창세기 2장 — Day1~7 완성 행성 위 에이전트·환경 레이어 |
| eden/firmament.py | 궁창(Raqia): 상층 수증기 캐노피, H2O·albedo·UV·mutation_factor |
| eden/flood.py | 대홍수 이벤트: 궁창 붕괴 → FloodEngine, FloodSnapshot |
| eden/initial_conditions.py | antediluvian/postdiluvian/flood_peak 초기조건 |
| eden/geography.py | 에덴 시대 지형·자기장 좌표·노출 지역(베링, 순다, 북해 등) |
| eden/search.py | 에덴 탐색 엔진: 파라미터 상태 → EdenCriteria 판정 → EdenCandidate 수집 |

---

## 2. 실행 점검 결과

| 항목 | 결과 | 비고 |
|------|------|------|
| `from solar.eden import make_firmament, make_flood_engine, ...` | ✅ | __init__ export 정상 |
| `python -m solar.eden.eden_demo` | ✅ 7/7 PASS | 궁창→대홍수→홍수후 전이, 극지 빙하 검증 |
| `python -m solar.eden.eden_search_demo` | ✅ 정상 종료 | 에덴 vs 현재 점수, antediluvian 탐색, postdiluvian 0통과 |
| solar/day7 → eden 연동 | ✅ | runner에서 `eden.geography.magnetic_protection_factor`, `eden.initial_conditions.make_antediluvian` 사용 |
| Lint (solar/eden) | ✅ | 에러 없음 |

---

## 3. 데모 검증 항목 (eden_demo)

- 에덴 T > 25°C, 홍수 해수면 > 50m, 돌연변이 배수 > 50x  
- 홍수후 T < 20°C, 빙하 형성 > 0.02  
- 에덴 빙하밴드 0/12, 홍수후 빙하밴드 > 0  

→ **7/7 PASS** 확인됨.

---

## 4. 에덴 탐색 (eden_search_demo)

- 에덴(antediluvian): score=1.000, 판정=PASS  
- 현재(postdiluvian): score=0.000, 판정=FAIL  
- antediluvian 공간 탐색: 1296 조합 → 20개 통과, 상위 5개 후보 출력  
- postdiluvian 탐색: 0개 통과 (예상된 결과)  

→ **동작 정상**.

---

## 5. Day7와의 연동

- **day7/runner.py**  
  - `from ..eden.geography import magnetic_protection_factor`  
  - (옵션) `from solar.eden.initial_conditions import make_antediluvian`  
- f_land 에덴=0.40, 기준점(250ppm/308K) 등 문서·주석과 일치.

---

## 6. 문서·개념

- **docs/EDEN_CONCEPT.md**: Adam=Observer, Eve=Controller, lineage 설계 정리됨.  
- **solar/eden/__init__.py**: 챕터 구조(Day1~7 vs Eden), 환경 3단계(antediluvian/flood/postdiluvian) 주석 명시.

---

## 7. 결론

- **에덴 시스템**: solar/eden 내 firmament, flood, initial_conditions, geography, search 구현·export·데모 모두 **정상**.  
- **Day7 연동**: runner에서 eden 지리·초기조건 사용, 의존성·import **문제 없음**.  
- **다음 확장**: EDEN_CONCEPT.md 기준으로 adam.py(Observer), eve.py(Controller), lineage.py 는 **예정 구조**로 두고, 필요 시 구현하면 됨.

이 문서는 점검용 스냅샷이다. 구현 추가·변경 시 이 표를 갱신하면 된다.
