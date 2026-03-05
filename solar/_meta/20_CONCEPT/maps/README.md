# maps — 레이어↔폴더 매핑

이 폴더에는 **개념 레이어**와 **solar/ 실제 경로**를 대응시키는 표·문서를 둠.

---

## 문서 구조 (역할 분리)

| 문서 | 역할 |
|------|------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 시스템 개요, 전체 흐름, 검증(verify_imports), Quick Test |
| **[LAYER_FLOW.md](LAYER_FLOW.md)** | 시간 흐름 (Pre-Creation → Creation Days → Eden → Firmament → Flood) |
| **[FOLDER_MAP.md](FOLDER_MAP.md)** | 실제 폴더·코드 위치 (트리 구조) |
| **[TERRAFORMING_EXPLORER_FLOW.md](TERRAFORMING_EXPLORER_FLOW.md)** | 테라포밍 탐색기: 조(JOE) → 모(MOE) → 체루빔 흐름 |
| **[JOE_PHYSICS_EXPANSION.md](JOE_PHYSICS_EXPANSION.md)** | 조(JOE) 물리 확장 방향 (9단계 Physics-First Planet Evaluation) |
| **[JOE_REVERSE_MODE.md](JOE_REVERSE_MODE.md)** | 역방향: 현재 지구 → 초기 상태 추적 + 정보 추적 엔진 연동 설계 (추정/동화) |
| **[JOE_FEEDBACK_REFERENCE.md](JOE_FEEDBACK_REFERENCE.md)** | JOE 설계 피드백 항목별 반영 참조 (팩트→역할→확장) |
| **[JOE_SNAPSHOT_SCHEMA_V02.md](JOE_SNAPSHOT_SCHEMA_V02.md)** | JOE 표준 스냅샷 스키마 v0.2 (CORE + 확장 키) |
| **[JOE_ENGINE_PHYSICS_SPEC.md](JOE_ENGINE_PHYSICS_SPEC.md)** | Joe_Engine에 구현된 물리 법칙·개념 정확한 명세 (독립 엔진 vs solar/joe) |
| **[JOE_HISTORICAL_RECONSTRUCTOR_INTEGRATION.md](JOE_HISTORICAL_RECONSTRUCTOR_INTEGRATION.md)** | 역사 추적 엔진(HistoricalDataReconstructor) ↔ JOE 연동 가능성 분석 |
| **LAYERS.md** | 레이어 순서·경로 일람표 (기존) |

---

## 빠른 참조 (개념 → 경로)

| 개념 | solar/ 경로 |
|------|-------------|
| 조(JOE)·precreation | _01_beginnings/joe |
| 천지창조 Day1~7 | _02_creation_days/day1~day7, bridge, engines, fields, physics |
| 지표·surface | _02_creation_days/day3/surface |
| 에덴·생물권·인지·통치 | _03_eden_os_underworld/eden, biosphere, cognitive, governance, monitoring, underworld |
| 궁창 시대 | _04_firmament_era (구현: _03/eden/firmament) |
| 노아 홍수 | _05_noah_flood (구현: _03/eden/flood) |

상세는 [ARCHITECTURE.md](ARCHITECTURE.md), [LAYER_FLOW.md](LAYER_FLOW.md), [FOLDER_MAP.md](FOLDER_MAP.md) 참고.
