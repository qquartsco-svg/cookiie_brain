# CookiieBrain 레이어 아키텍처

## 레이어 구조

```
┌─────────────────────────────────────────────┐
│  Layer 4: ANALYSIS (측정)                    │
│  analysis/Layer_1~6, brain_analyzer.py       │
│  궤적을 받아 물리량만 측정. 시스템을 변경 안 함  │
├─────────────────────────────────────────────┤
│  Layer 3: MEMORY (기억 운영)                  │
│  hippo/                                      │
│  장(field)을 시간에 따라 변화시킴               │
│  우물 생성 · 강화 · 감쇠 · 소멸               │
│  에너지 주입 정책 (탐색/정착/리콜)             │
├─────────────────────────────────────────────┤
│  Layer 2: FIELD (힘의 원천)                   │
│  solar/ — 태양(1/r), 달(조석), 합성기         │
│  trunk/Phase_B/ — 가우시안 우물 수식           │
│  각 천체/우물이 만드는 퍼텐셜과 힘을 정의       │
├─────────────────────────────────────────────┤
│  Layer 1: DYNAMICS (적분기)                   │
│  PFE (외부) — Strang splitting, 적분          │
│  trunk/Phase_A/ — 코리올리 회전 (ωJv)         │
│  trunk/Phase_C/ — 요동 (σξ), FDT             │
│  힘을 받아 상태 벡터를 갱신                    │
├─────────────────────────────────────────────┤
│  Layer 0: STATE (상태)                        │
│  GlobalState (x, v, energy, extensions)      │
│  모든 레이어가 공유하는 데이터 구조             │
└─────────────────────────────────────────────┘
```

## 의존 규칙

**각 레이어는 자기보다 아래 레이어만 참조한다. 위를 참조하면 안 된다.**

```
Layer 4 → Layer 0 (궤적 데이터만 읽음)
Layer 3 → Layer 2 (우물 수식), Layer 0 (상태)
Layer 2 → Layer 0 (위치 벡터만 받음)
Layer 1 → Layer 2 (힘/퍼텐셜), Layer 0 (상태)
Layer 0 → 없음 (최하위)
```

## 오케스트레이터

```
cookiie_brain_engine.py
  모든 레이어를 연결하는 유일한 파일.
  각 레이어를 순서대로 호출:
    1. Layer 2 (Field): 퍼텐셜/힘 구성
    2. Layer 1 (Dynamics): PFE로 상태 적분
    3. Layer 3 (Memory): Hippo로 우물 갱신
    4. Layer 4 (Analysis): 선택적 분석
```

## 폴더 ↔ 레이어 매핑

| 폴더 | 레이어 | 역할 |
|------|--------|------|
| `solar/central_body.py` | L2 Field | 태양: 1/r 장거리 중력 |
| `solar/orbital_moon.py` | L2 Field | 달: 공전+자전+조석력 |
| `solar/tidal_field.py` | L2 Field | 합성기: 태양+달 힘 합산 |
| `solar/ocean_simulator.py` | L4 Analysis | 바다: 우물 안 유속 시뮬레이션 |
| `trunk/Phase_A/` | L1 Dynamics | 자전: ωJv 코리올리 회전 |
| `trunk/Phase_B/` | L2 Field | 우물: 가우시안 다중 우물 수식 |
| `trunk/Phase_C/` | L1 Dynamics | 요동: Langevin 노이즈, FDT |
| `hippo/memory_store.py` | L3 Memory | 우물 생성·강화·감쇠·소멸 |
| `hippo/energy_budgeter.py` | L3 Memory | 에너지 주입 정책 |
| `analysis/Layer_1~6/` | L4 Analysis | 측정 도구 |
| `cookiie_brain_engine.py` | Orchestrator | 전체 연결 |

## 개념 용어 정리

| 용어 | 뭔지 | 비유 | 레이어 |
|------|------|------|--------|
| 태양 | 1/r 거대질량 중심체 | 장기기억 중심 | L2 |
| 우물 (지구) | Gaussian 국소 끌림 | 개별 기억 | L2 |
| 달 | 우물 주위를 도는 소질량 | 외부 리듬 | L2 |
| 조석 (tidal) | 달 중력의 공간적 차이 | 기억 안 파동 | L2 |
| 바다 | 우물 안 여러 tracer의 흐름 | 활성 패턴 | L4 |
| 자전 | ωJv, 에너지 보존 회전 | 위상 유지 | L1 |
| 공전 | 다중 우물 사이 순환 | 연상/전환 | L1+L2 |
| 감쇠 | -γv | 피로/활성 감소 | L1 |
| 요동 | σξ(t) 노이즈 | 확률적 전이 | L1 |
| 주입 | I(x,v,t) | 새 자극 | L3 |
