# NOAH_FUSE_MODEL — 복합 스트레스 + 외부 임펄스 퓨즈 모델

이 문서는 `_05_noah_flood` 레이어에서 사용 가능한
**“4레이어 + 혜성 도화선”** 개념을 정리한다.

핵심 아이디어:

- 대홍수는 단일 원인이 아니라,
  1) 거시 물리(JOE)  
  2) 열역학/수권·온실(MOE 스타일)  
  3) 생물권/운영(EdenOS 피드백)  
  4) 외부 임펄스(혜성/플레어 등)  
  가 레이어처럼 쌓여 임계 근처까지 간 뒤,
- 짧은 임펄스가 “도화선(trigger)” 역할을 하며
  궁창 붕괴 → 홍수 → postdiluvian 지구형 상전이로 이어진다는 구조다.

---

## 1. 레이어별 역할 (개념)

| 레이어 | 개념 축 | 효과 |
|--------|---------|------|
| L1 | 거시 물리 (JOE) | 질량, 반지름, 자전, 수권 예산, 판 구조 등으로 planet_stress / instability 기본값을 올림. |
| L2 | 열역학·수권·온실 (MOE 스타일) | 궁창 수증기, 온실 효과, 수순환 리스크로 effective_instability 를 추가 증폭. |
| L3 | 생물권·운영 (EdenOS) | 생물 대발생, 대기 조성 교란, 운영 한계 등으로 환경 스트레스에 장기적 편향을 더함. |
| L4 | 외부 임펄스 (혜성/플레어 등) | 이미 임계 근처까지 올라온 시스템에 짧은 시간 강한 spike 를 넣어 임계선(0.85)을 넘김. |

요약하면:

> L1~L3 가 시스템을 **“임계 근처의 불안정 평형”**까지 밀어 올리고,  
> L4 임펄스가 마지막 스파크가 되어 궁창 붕괴를 촉발한다.

---

## 2. 코드 레이어와의 대응

- **L1 — 거시 물리(JOE)**  
  - 경로: `solar/_01_beginnings/joe/*`  
  - 역할: PANGEA §4 Aggregator (`planet_stress`, `instability`) 계산.
- **L2 — 열역학·수권·온실**  
  - 경로: `_02_creation_days/day2/atmosphere/*`, `.../greenhouse.py`,  
    `_03_eden_os_underworld/eden/initial_conditions.py` (`H2O_canopy`, `tau`, `T_surface_K` 등).
  - 역할: water_cycle_risk, greenhouse_proxy, magnetosphere_risk 의 근거가 되는 필드들.
- **L3 — 생물권·운영 (EdenOS)**  
  - 경로: `_03_eden_os_underworld/eden/eden_os/*`, `lifespan_budget.py` 등.
  - 역할: 생물권/정책 피드백이 mutation_factor, pressure_atm, UV_shield 등 장기 상태에 영향을 줌.
- **L4 — 외부 임펄스**  
  - 경로: `_05_noah_flood/scenarios.py` (`run_scenario_impulse_shock`, `run_scenario_combined_impulse`)  
  - 역할: 특정 시간 `shock_time` 근처에서 instability / risk 에 단기 스파이크를 주입.

`compute_effective_instability(...)` 는 이 모든 축을
`effective_instability(t)` 하나로 합성해 FirmamentLayer 에 전달한다.

---

## 3. Fuse 시나리오 — combined_impulse 개념

Fuse 모델을 직접 실험하기 위한 러너가
`_05_noah_flood/scenarios.py` 의 `run_scenario_combined_impulse()` 다.

- 기본 구조:
  - combined_ramp 처럼 거시+환경 리스크를 서서히 올림 (L1~L3).
  - shock_time 근처에 impulse_shock 처럼 짧은 임펄스를 겹침 (L4).
- 목적:
  - “이미 임계 근처까지 올라온 상태에서, 작은 외부 충격이 노아급 전이를 일으키는지”
    동역학적으로 확인한다.

실행 예:

```bash
python -m solar._05_noah_flood.scenarios
```

마지막에 `[combined_impulse]` 섹션이 함께 출력된다.

---

## 4. 해석 가이드

- macro_only / combined_ramp:
  - L1~L2(±L3) 만으로 임계선을 넘길 수 있는지 보는 내부 요인 시나리오.
- impulse_shock:
  - 거의 안정 상태(L1~L3 낮음)에서 L4 임펄스만으로 상전이가 가능한지 보는 순수 외부 요인 시나리오.
- combined_impulse (Fuse):
  - L1~L3 로 미리 “도화선에 불을 붙여 놓은 상태”에서,
    L4 임펄스가 최종 붕괴를 일으키는 복합 모델.

1차 실험 결과(RESULTS_FIRST_RUN.md 기준)에서는
impulse_shock 가 유일하게 완전 상전이를 만들었지만,
Fuse 모델(combined_impulse)은 **“내부 스트레스 + 외부 도화선” 구조를
명시적으로 실험하기 위한 개념 레이어**다.

