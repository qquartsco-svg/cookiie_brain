# 지금까지 쌓아온 것 — 코드·서사·문서 위치

**이 파일만 열면** 코드 확인·수정·로직·리드미·서사를 어디서 보면 되는지 한눈에 보입니다.  
삭제된 건 없고, 전부 아래 경로에 있습니다.

---

## 1. 개념·서사·창조일 문서 (개념 축)

| 내용 | 경로 |
|------|------|
| **개념 (00_system ~ 04_onward)** | **solar/_meta/concept/** — 00_system, 01_light, 02_firmament, 03_surface, 04_onward 각 README |
| **창조일·파이프라인·레이어 매핑** | **solar/_meta/20_CONCEPT/** — creation_days, pipeline_phases, maps 각 README·LAYERS.md |
| **레이어↔경로 표** | solar/_meta/20_CONCEPT/maps/LAYERS.md |
| **행성 탐사 → 천지창조 → 에덴·OS·언더월드 → 궁창 → 노아 대홍수 흐름** | solar/LAYER_FLOW.md |

---

## 2. 코드 + 같은 레이어 README (로직·수식·서사)

코드와 **같은 폴더 안에** README가 있어서, 코드 확인·로직·서사를 같이 볼 수 있습니다.

| 레이어 | 코드·문서 위치 |
|--------|----------------|
| **행성 탐사** | solar/_01_beginnings/joe/ (observer.py, run.py). solar.planet_dynamics = solar.joe 별칭. |
| **천지창조 day1~7** | solar/_02_creation_days/day1~day7, physics, fields, bridge, engines/. surface·지표는 day3/surface. day6 포함 전부 _02. |
| **에덴·OS·언더월드** | solar/_03_eden_os_underworld/eden/, biosphere/, cognitive/, governance/, monitoring/, underworld/ |
| **궁창 환경시대** | solar/_04_firmament_era/ (re-export), 구현: _03_eden_os_underworld.eden |
| **노아 대홍수 이벤트** | solar/_05_noah_flood/ (re-export), 구현: _03_eden_os_underworld.eden |

---

## 3. 확인·수정·보안·로직 보는 방법

- **코드 확인·수정** → 위 표의 해당 레이어 폴더 열기 (예: _02_creation_days/day1/em/*.py).
- **로직·수식·알고리즘** → 같은 폴더의 README.md 또는 해당 모듈 .py.
- **서사·리드미** → 같은 레이어 README + _meta/concept/ + _meta/20_CONCEPT/.
- **전체 흐름** → solar/LAYER_FLOW.md, solar/_meta/20_CONCEPT/maps/LAYERS.md.

---

## 4. 요약

- **지금까지 만드신 문서·서사·개념** → **_meta/concept/** (00_system~04_onward), **_meta/20_CONCEPT/** (creation_days, pipeline_phases, maps). **사라진 것 없음.**
- **코드와 붙어 있는 README·로직** → 각 레이어 폴더(_01_beginnings ~ _05_noah_flood) **안**에 그대로 있음.
- **전체 구조가 헷갈릴 때** → 이 파일(INDEX_CODE_AND_DOCS.md)만 보면 됨.

이 인덱스만 따라가면 코드 확인·수정·보안·로직 확인·리드미·서사 전부 찾을 수 있게 되어 있음.
