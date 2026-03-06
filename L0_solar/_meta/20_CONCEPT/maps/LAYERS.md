# solar/ 레이어 ↔ 실제 경로 매핑

**흐름**: **행성 탐사** → **천지창조 day1~7** → **에덴·OS·언더월드** → **궁창 환경시대** → **노아 대홍수 이벤트**.  
**천지창조 7일 + 그 전 로직 직관 정리**: → **[LAYER_FLOW.md](../../../LAYER_FLOW.md)** (solar 루트).

---

## 1. 시간 축 (5단계)

| 순서 | 개념 | 구현 경로 (solar/) |
|------|------|--------------------|
| 01 | 행성 탐사 | _01_beginnings/joe |
| 02 | 천지창조 day1~7 | _02_creation_days/day1~day7, physics, fields, surface, bridge, engines |
| 03 | 에덴·OS·언더월드 | _03_eden_os_underworld/eden, biosphere, cognitive, governance, monitoring, underworld |
| 04 | 궁창 환경시대 | _04_firmament_era (re-export), 구현: _03_eden_os_underworld.eden |
| 05 | 노아 대홍수 이벤트 | _05_noah_flood (re-export), 구현: _03_eden_os_underworld.eden |

---

## 2. 창조일(1~7일) → 경로 (전부 _02_creation_days, 에덴만 _03)

| 일차 | 경로 |
|------|------|
| 0(이전) | _01_beginnings/joe |
| 1일 | _02_creation_days/day1 |
| 2일 | _02_creation_days/day2, fields |
| 3일 | _02_creation_days/day3 (surface는 day3/surface) |
| 4일 | _02_creation_days/day4 |
| 5일 | _02_creation_days/day5 |
| 6일 | _02_creation_days/day6, _03_eden_os_underworld/eden |
| 7일 | _02_creation_days/day7 |

---

## 3. 의존 방향

- data → core ← em, atmosphere, surface, cognitive  
- eden은 firmament, creation_layers, underworld(hades) 사용.  
- 자세한 의존은 각 패키지 `__init__.py` 및 docs 참고.
