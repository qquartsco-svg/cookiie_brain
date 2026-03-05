# solar/ 폴더 구성 — 직관적 흐름

**흐름**: **행성 탐사** → **천지창조 day1~7** → **에덴·OS·언더월드** → **궁창 환경시대** → **노아 대홍수 이벤트**

---

## 1. 폴더 순서 (한눈에)

| 순서 | 폴더 | 한글 | 내용 |
|------|------|------|------|
| 01 | **_01_beginnings** | 행성 탐사 | joe (_core=독립 엔진 동일 기어, observer, run, feature_layers) |
| 02 | **_02_creation_days** | 천지창조 day1~7 | day1~day7, physics, fields, bridge, engines (surface는 day3/surface에 있음) |
| 03 | **_03_eden_os_underworld** | 에덴·OS·언더월드 | eden, biosphere, cognitive, governance, monitoring, underworld |
| 04 | **_04_firmament_era** | 궁창 환경시대 | firmament·antediluvian re-export (구현: _03.eden) |
| 05 | **_05_noah_flood** | 노아 대홍수 이벤트 | flood 엔진·전이 re-export (구현: _03.eden) |

---

## 2. import

- `solar.day1`, `solar.eden`, `solar.underworld` 등 그대로 사용 가능.
- 실제 경로: `solar._01_beginnings`, `solar._02_creation_days.bridge`, `solar._03_eden_os_underworld.eden` 등.
- **흐름 엔진**: `solar.run_pipeline(steps_per_stage={...})` — 1→2→3→4→5 순서 실행. `solar.pipeline` 참고.
- **surface** (지표·알베도): `_02_creation_days/day3/surface/` — SurfaceSchema, effective_albedo. (빈 껍데기 `_02_creation_days/surface/` 제거됨)

---

## 3. 코드·문서 위치

- **코드** → 위 폴더 **안** (각 하위에 .py, README 있음).
- **개념·서사** → _meta/concept, _meta/20_CONCEPT.
- **전체 인덱스** → [INDEX_CODE_AND_DOCS.md](INDEX_CODE_AND_DOCS.md).
- **3문서 체계** (개요·시간흐름·폴더) → [_meta/20_CONCEPT/maps/README.md](_meta/20_CONCEPT/maps/README.md) (ARCHITECTURE, LAYER_FLOW, FOLDER_MAP).
- **점검 결과** → [AUDIT_REPORT.md](AUDIT_REPORT.md). import 검증: `python solar/verify_imports.py`
