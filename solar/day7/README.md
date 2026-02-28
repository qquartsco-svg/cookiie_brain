# Day 7 — 일곱째 날: 완성·안식 (Sabbath / Completion)

> *"하나님이 그가 하시던 일을 일곱째 날에 마치시니 그가 하시던 모든 일을 그치고 일곱째 날에 안식하시니라"*
> — 창세기 2:2

---

## 1. 포지션

```
Day1 → Day2 → Day3 → Day4 → Day5 → Day6 → Day7
빛    대기    땅/불  리듬   이동   진화   완성

Day1~6 = physics + biology   (execution engines)
Day7   = cybernetics layer   (kernel supervisor)
```

Day6까지 "창조"가 완성됐다.
Day7은 새 물리 기어를 추가하지 않고, **Day1~6 전체가 안정적으로 돌아가는지 관측·판정하는 OS 레이어**다.

```
시스템 이론 번역:

Day1~6  →  simulation layer   (physics plant)
Day7    →  control layer      (stability monitor)
Eden    →  observer/controller (Adam/Eve — 다음 단계)
```

---

## 2. Day7의 진짜 정체 — Kernel Scheduler + Stability Monitor

Day7은 **시뮬레이터가 아니라 OS 커널 레이어**다.

| 개념 | Day7 대응 |
|------|-----------|
| Kernel Scheduler | PlanetRunner — 12엔진 실행 순서 결정 |
| Stability Monitor | SabbathJudge — steady-state 판정 |
| State Snapshot | PlanetSnapshot — 전 레이어 상태 직렬화 |
| Global Loss Fn | StressEngine (12번째) — 행성 전체 비용 함수 |

이 구조는 다음과 동형이다:
```
Unity Game Loop          → PlanetRunner.step()
Climate GCM timestep     → 12엔진 순차 호출
Reinforcement Env.step() → PlanetSnapshot 반환
Control theory supervisor→ SabbathJudge
```

---

## 3. 핵심 구조

### PlanetRunner — 통합 스텝 드라이버

```python
runner = make_planet_runner(n_bands=12, n_species=4, seed=42)
snap   = runner.step(dt_yr=1.0)   # ← 이게 "하루"
```

한 번의 `step(dt_yr)` 안에서 12개 엔진이 **물리 인과 순서**대로 실행된다:

| 순서 | 엔진 | 역할 | 인과 분류 |
|------|------|------|-----------|
| 1 | RhythmEngine | 장주기 리듬 (Milankovitch) | 외부 forcing 먼저 |
| 2 | AtmosphereEngine | 대기 온도·CO₂ | 환경 상태 설정 |
| 3 | LatitudeBands | 12개 밴드 생물권 | 생물권은 대기 의존 |
| 4 | SeasonEngine | 계절 위상·온도 편차 | 공간 분화 |
| 5 | NitrogenEngine × 12 | 밴드별 질소 순환 | 자원 제한 |
| 6 | OceanEngine | 조석·탄소 펌프 | 전 지구 순환 |
| 7 | FoodWebEngine × 12 | 밴드별 트로픽 ODE | nutrient → trophic |
| 8 | TransportEngine | 씨드 밴드 간 확산 | local 후 diffusion |
| 9 | MutationEngine | 변이 이벤트 | 환경 결과 이후 진화 |
| 10 | FeedbackEngine | Genome → 환경 피드백 | 진화 → 환경 역방향 |
| 11 | NicheEngine | 자원 경쟁·점유 | 진화 OS 마무리 |
| **12** | **StressEngine** | **스트레스 누적·요약** | **global cost fn** |

**순서 설계 원칙:**
```
forcing → environment → biology → transport → evolution → stress(cost)
```
이 순서는 물리 인과관계를 위반하지 않는다.
12번째 StressEngine은 전 스텝의 결과를 집계하는 **global loss function** 역할.

---

### SabbathJudge — 안식 판정기

```python
judge = make_sabbath_judge(window=12)
judge.push(snap)
eq = judge.judge()
# eq.is_stable → True  = 🌿 안식 (steady-state 확인)
# eq.is_stable → False = ⚡ 불안정 (아직 과도 응답 중)
```

**판정 기준 — drift 기반 (절대값이 아님):**

| 기준 | 임계값 | 의미 |
|------|--------|------|
| CO₂ drift | < 2.0 ppm/step | 탄소 루프 수렴 |
| T drift | < 0.5 K/step | 에너지 균형 수렴 |
| Stress | < 0.3 | 생태 안정 |

> **"안정 ≠ 상수, 안정 = bounded change"**
> 실제 GCM(Global Climate Model)에서도 `dT/dt → 0`, `dCO2/dt → small`을
> equilibrium 조건으로 사용한다. 동일한 판정 기준.

`window=12` — **spatial sampling completeness condition.**
12개 밴드가 전부 관측되는 최소 시간 = `window ≥ N_bands`.
12지파가 모두 안정되어야 안식이 인정된다.

---

### PlanetSnapshot — 전 지구 상태 직렬화

```python
# 전 지구 스칼라
snap.CO2_ppm          # 탄소 루프
snap.T_surface_K      # 에너지 균형
snap.planet_stress    # 행성 비용 [0~1]
snap.obliquity_deg    # 궤도 리듬
snap.mutation_events  # 진화 활동도

# 12개 밴드 (지파) 벡터
snap.band_T           # 온도 분포
snap.band_N_soil      # 질소 분포 (12우물)
snap.band_trophic     # 먹이사슬 상태
snap.band_niche       # 자원 점유
snap.band_seed        # 씨드 확산
```

이 인터페이스면 visualizer / RL agent / optimizer / analysis tool
전부 직접 연결 가능.

---

## 4. 12의 의미

```
공간: 12개 위도 밴드        window >= N_bands
기능: 12개 독립 엔진        모든 물리·생물 역할 완결
시간: window=12 스텝        1 spatial circulation cycle
     ↓
PlanetRunner = 세 개의 12가 교차하는 지점
```

`12 = 2×2×3` — 약수 6개 — 어느 방향으로 분할해도 나머지 없음.

자세한 분석 → [`docs/WHY_12_SYSTEMIC.md`](../../docs/WHY_12_SYSTEMIC.md)

---

## 5. 알려진 한계 — Day8 이후 개선 사항

### ⚠️ Explicit Euler Ordering (현재)

```python
# 현재: 순차 실행 (explicit)
atmosphere.step()   # t
biosphere.step()    # t + dt (대기 결과 사용)
```

실제 물리에서 `Atmosphere ↔ Biosphere`는 **동시 방정식**이다.
현재는 explicit Euler ordering — 단일 스텝에서 약한 결합으로 근사.

```python
# 미래 개선: sub-iteration loop (implicit coupling)
for k in range(inner_iters):
    atmosphere.step()
    biosphere.step()
    if converged(): break
```

**지금은 문제 없음.** `dt_yr=1.0` 스케일에서 explicit ordering 오차는 수렴.
장기 시뮬레이션(>1000yr) 또는 빠른 피드백 루프 구현 시 필요.

### 메모: Day8 설계 포인트
이 한계를 해결하는 것이 Day8의 핵심 과제가 될 수 있다.
→ [`docs/DAY8_CONCEPT.md`](../../docs/DAY8_CONCEPT.md) 참고

---

## 6. 다음 단계 — 에덴 시스템 (Observer/Controller)

```
Day1~6: physics + biology   (plant)
Day7:   cybernetics layer   (supervisor)  ← 여기
Eden:   observer + controller             ← 다음
```

시스템 이론에서 supervisor(Day7) 다음 단계는
자연스럽게 **observer/controller 삽입**이다.

아담 = observer (12 밴드 상태를 읽고 이름 붙이는 에이전트)
이브 = controller (이상 감지 → 피드백 생성)
계승 = 다음 세대 observer/controller 자동 생성 (ReproductionEngine)

→ [`docs/ADAM_EVE_SYSTEM.md`](../../docs/ADAM_EVE_SYSTEM.md)

---

## 7. 파일 구조

```
solar/day7/
├── __init__.py          ← 공개 API
├── runner.py            ← PlanetRunner — Kernel Scheduler
├── sabbath.py           ← SabbathJudge — Stability Monitor
├── completion_engine.py ← CompletionEngine — 메타 래퍼
├── day7_demo.py         ← V1~V7 ALL PASS
└── README.md            ← 이 파일
```

---

## 8. 빠른 시작

```python
from solar.day7 import make_planet_runner, make_sabbath_judge

runner = make_planet_runner()
judge  = make_sabbath_judge(window=12)

for i in range(24):          # 24스텝 = 12밴드 × 2사이클
    snap = runner.step(dt_yr=1.0)
    judge.push(snap)
    eq = judge.judge()
    if eq and eq.is_stable:
        print(f"🌿 안식 확인 — t={snap.time_yr:.0f}yr")
        break
    print(snap.summary())
```
