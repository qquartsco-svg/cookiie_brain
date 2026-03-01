# 다음 작업 확인 (에덴 탐색기 완성 이후)

**기준일**: 2026-02-27  
**전제**: 에덴 탐색기(search + exploration + Grid 연동) 완성, solar 폴더·블록체인 점검 완료.

---

## 1. Eden ↔ Day7 통합 시 필수

문서: `docs/EDEN_ENGINEERING_FINAL.md`

| 항목 | 내용 |
|------|------|
| **τ/albedo/ΔT 더블카운트 방지** | PlanetRunner(또는 Day7)에 Eden IC를 넘길 때, Eden이 계산한 τ, ε_a, T_surface_K, pole_eq_delta_K, albedo를 **그대로 사용**. Day2 AtmosphereColumn이 같은 τ를 다시 계산·누적하지 않도록 분기 추가. |
| **Runner/AtmosphereColumn 분기** | `init`/override가 있으면 그 값을 최종값으로 쓰고 τ/ε/T **재계산하지 않음**. 통합 시점에 Day2 코드에서 "Eden IC에서 온 τ"와 "Day2 자체 τ"가 둘 다 적용되는 구간이 없는지 **한 번 더 검사**. |
| **Flood 후 SabbathJudge 정책** | Flood가 끝난 뒤 postdiluvian 수렴 시, Day7 SabbathJudge가 Flood로 인한 비정상 상태를 '실패'로 볼지 '전이 이벤트'로 제외할지 **정책 결정**. |

→ **다음 작업**: Eden IC를 실제 Day7 PlanetRunner/AtmosphereColumn에 붙이고, 위 규칙대로 동작하는지 구현·검증.

---

## 2. 문서/핸드오버에 나온 다음 작업 후보

출처: `docs/HANDOVER_2026-02-26.md`, `docs/STATUS_CHECK_2026-02-26.md`

| 우선순위 | 항목 | 설명 |
|----------|------|------|
| 1순위 | `solar/atmosphere/README.md` 커밋·푸시 | PT 정의, 모델 스코프, τ 파라메트릭, C 유효값 (이미 반영 여부 확인 가능) |
| 2순위 | solar/README.md | 파일 구조에 atmosphere/ 반영, 레이어 다이어그램에 atmosphere 층, Phase 6a/6b 검증 로그 링크 |
| 2순위 | docs/FULL_CONCEPT_AND_STATUS.md | v1.5.0(또는 solar 전용)까지 업데이트 또는 범위 분리 |
| 3순위 | FluxInterface + SystemBalanceChecker | 에너지·질량 수지 검증 레이어 |
| 3순위 | PhaseController | Day/Night, 계절, 생장 위상에 따른 GPP scaling, seed germination, dormancy |
| 3순위 | Earth ↔ Spacecraft 모드 | Power_budget, Radiator_area 등 우주선 모드 |
| 3순위 | Biosphere–Atmosphere 단위 규약 고정 | planet_bridge 구현 내용을 문서로 공식화 |

---

## 3. 물리 스택 — 다음 기어 후보

출처: `docs/PHYSICS_STACK_AND_NEXT_GEAR.md`, `docs/ENVIRONMENT_STATUS_AND_NEXT.md`

| 후보 | 설명 | 의존성 |
|------|------|--------|
| Phase 6c: 구름/강수 | 알베도 피드백, 수증기→구름 | water_cycle, column |
| 수증기 피드백 강화 | CC + 경로 의존 | water_cycle |
| 광화학 (오존층) | UV → O₃, 스펙트럼 의존 | em, atmosphere |
| τ 밴드/스펙트럼 | 파라메트릭 → 물리 기반 | greenhouse |
| J4, J6 중력 고조파 | 세차 정밀도 향상 | core (solar/README 확장 가능성) |
| 장동 (달 교점 퇴행) | 세차 위 18.6년 진동 | core |
| 조석 소산 | Gyr 스케일 달 후퇴 + 지구 자전 감속 | core |

→ **다음 중 하나만** 넣어도 시스템이 “살아남”는 방향으로 기어 맞춰보기.

---

## 4. 에덴 다음 단계 (개념)

출처: `solar/day7/README.md`, `docs/EDEN_CONCEPT.md`, `docs/ADAM_EVE_SYSTEM.md`

| 단계 | 내용 |
|------|------|
| **Observer/Controller (Adam/Eve)** | Day7 supervisor 다음: 12밴드 상태를 읽고 이름 붙이는 observer, 이상 감지 → 피드백 생성 controller. |
| **계승** | 다음 세대 observer/controller 자동 생성 (ReproductionEngine 연동). |

→ **다음 작업**으로 삼을지 여부는 프로젝트 방향에 따라 선택.

---

## 5. 정리 — 지금 선택 가능한 “다음 작업”

| 번호 | 작업 | 성격 |
|------|------|------|
| **A** | **Eden IC → Day7 Runner/AtmosphereColumn 연동** | 통합 필수. 더블카운트 방지 규칙 구현·검증. |
| B | Flood 후 SabbathJudge 정책 (전이 이벤트 제외 여부) | 통합 시 정책 결정. |
| C | solar/README.md, FULL_CONCEPT_AND_STATUS.md 등 문서 동기화 | 2순위 문서. |
| D | FluxInterface / SystemBalanceChecker / PhaseController 등 | 핸드오버 후보. |
| E | Phase 6c 또는 수증기 피드백 등 다음 물리 기어 | 물리 스택 확장. |
| F | Adam/Eve (Observer/Controller) 설계·구현 | 에덴 다음 개념 단계. |

**권장**: 에덴 탐색기 완성 직후에는 **A (Eden ↔ Day7 통합 + 더블카운트 방지)** 를 다음 작업으로 두고, 그다음에 B·C를 보는 흐름이 자연스럽다.
