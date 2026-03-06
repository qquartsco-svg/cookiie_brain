# pipeline_phases — 파이프라인 단계 개념·코드 매핑

World Generation Pipeline 순서(precreation → … → monitoring) 각 단계가 **무슨 개념**인지, **실제 코드는 solar/ 어디**에 있는지 요약.

---

## 단계별 요약

| 단계 | 개념 | 실제 코드 경로 (solar/ 기준) |
|------|------|-----------------------------|
| **precreation** | 1일 이전 — 조(JOE) 거시 탐색 | `precreation/joe/` (행성 스트레스·불안정도) |
| **physics** | 행성 내부 — 루시퍼·심부 스냅샷 | `physics/lucifer_core/` → underworld/deep_monitor |
| **fields** | 궁창·대기·퍼머넌트 | `fields/firmament/` → eden/firmament (FirmamentLayer, Layer0Snapshot) |
| **surface** | 지표·바다·지형 | day3/surface, day3/biosphere |
| **biosphere** | 에덴·생태·생명나무 | `eden/` (EdenOS, 생명나무, 4대강, 체루빔 등) |
| **cognition** | MOE·체루빔·인지 | `cognitive/`, eden/eden_os/cherubim_guard, eden/search |
| **governance** | 하데스·룰·법칙 | `governance/hades/` → underworld/hades |
| **monitoring** | 언더월드·사이렌·경고 | `underworld/`, `monitoring/` → underworld/siren |

---

## 흐름 한 줄

**행성 형성(조) → 물리(심부) → 궁창(필드) → 지표·생물권 → 에덴·인지 → 통제(하데스) → 경고(사이렌).**

실행 순서는 `solar.PIPELINE_ORDER` 및 `solar/eden/creation_layers.py` 의 `run_creation_layers()` 참고.
