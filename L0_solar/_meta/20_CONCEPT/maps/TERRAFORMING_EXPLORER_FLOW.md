# 테라포밍 탐색기 흐름: 조 → 모 → 체루빔

이 문서는 **행성 테라포밍 탐색기**의 서사·물리 흐름을 정의한다.  
파인만 물리학 강의의 **조(Joe)**·**모(Moe)** 관찰자 철학을 계승한다.

---

## 1. 전체 흐름 (한 줄)

```
조(JOE)  —  행성·우주 물리 탐사 (거시)
    ↓
모(MOE)  —  행성 내부 디테일 조건 탐사 (미시)
    ↓
체루빔  —  에덴 조성 가능성 지역 탐사 (접근 제어·가능 지역 라벨링)
```

= **테라포밍 탐색기**의 연속 단계.

---

## 2. 조 (JOE) — 행성 디테일·우주 조건 탐사

**역할**: 행성 형성 이전·이후의 **거시적 물리**를 탐사.  
필드장, 우주 조건, 중력 조건, 시간 조건, 대칭, 회전 등 **파인만 물리학 강의 기본 흐름**에 따른 행성의 탐사와 움직임 탐사.

**핵심**:
- 우주 필드장 탐사 (중력장, 복사, 자기장 환경)
- 정지 질량·회전 안정성 (M, R, ω, g, v_escape, centrifugal < g)
- 판 구조·압력 (σ_plate, P_w), 수권 비율 (W_surface/W_total), 변화율 (dW)
- **출력**: planet_stress, instability → 다음 단계(천지창조/궁창) 또는 **모**로 전달

**위치**:
- **독립 엔진**: `Joe_Engine` 폴더 (행성 테라포밍 탐색기 독립 모듈, 상용화 가능)
- **본편 서사**: `solar._01_beginnings.joe` (서사적으로 "태초 이전 탐색"으로 파이프라인 1단계)

**물리 확장 방향**: [JOE_PHYSICS_EXPANSION.md](JOE_PHYSICS_EXPANSION.md) 참고 (Cosmic Field → Mass/Rotation → … → Terraforming 단계).

---

## 3. 모 (MOE) — 행성 내부 디테일 조건 탐사

**역할**: 조가 거시적 안전성을 승인한 뒤, **행성 내부**의 세밀한 조건을 탐사.  
다른 관성계(이동 관측자)에서 본 결과·내부 구조를 분석.

**핵심**:
- 대기·지표·수문·기후 등 세부 환경
- 에덴 후보 파라미터 공간 탐색 (CO2, H2O, O2, albedo, f_land, UV_shield 등)
- **출력**: EdenCandidate, score, band_eden_score → 체루빔·에덴 OS로 전달

**위치**:
- `solar._03_eden_os_underworld.eden.search` (EdenSearchEngine, make_eden_search)
- `solar._03_eden_os_underworld.eden.exploration`
- 생물권·인지(MOE) 엔진: biosphere, cognitive

---

## 4. 체루빔 — 에덴 조성 가능성 지역 탐사

**역할**: **행성에 에덴 조성 가능성이 있는 지역**을 탐사·접근 제어.  
"이 지역은 에덴으로 쓸 수 있는가?" 판별 및 접근 정책(ALLOW/DENY/SCAN/ALERT).

**핵심**:
- Eden Basin 진입 차단·허용 정책 (GuardDecision)
- 물리 해석: risk_score, 규칙 기반 접근 제어
- **출력**: GuardDecision, risk_score, rules_hit → EdenOS Step 4에서 사용

**위치**:
- `solar._03_eden_os_underworld.eden.eden_os.cherubim_guard` (CherubimGuard, make_cherubim_guard)

---

## 5. 본편 파이프라인과의 대응

| 단계 | 본편(solar) | 테라포밍 탐색기 관점 |
|------|-------------|------------------------|
| 1 | _01_beginnings (joe) | **조** — 우주·행성 물리 탐사 |
| 2 | _02_creation_days | 조 결과 기반 환경 구축 (빛·궁창·땅·생명) |
| 3 | _03_eden_os_underworld (eden, search) | **모** — 행성 내부 디테일·에덴 후보 탐색 |
| 3 | _03_eden_os_underworld (eden_os, cherubim_guard) | **체루빔** — 에덴 조성 가능 지역·접근 제어 |
| 4 | _04_firmament_era | 궁창 환경시대 (에덴 고압·고습·저엔트로피 상태) |
| 5 | _05_noah_flood | 궁창 붕괴·대홍수·postdiluvian 지구로의 상전이 |

---

## 6. 관련 문서

- [ARCHITECTURE.md](ARCHITECTURE.md) — 시스템 개요  
- [JOE_PHYSICS_EXPANSION.md](JOE_PHYSICS_EXPANSION.md) — 조 물리 확장 방향 (9단계)  
- docs/PLANET_DYNAMICS_ENGINE.md — JOE 엔진 공식 명칭·Observer 철학
