# _05_noah_flood 시나리오 모음 — 조·모·궁창·대홍수 상전이 실험

이 폴더는 노아 대홍수 이벤트를 **여러 트리거 패턴으로 돌려보는 실험 레이어**다.

- 물리 엔진 본체: `solar/_03_eden_os_underworld/eden/firmament.py`, `flood.py`,
  `initial_conditions.py`, `_01_beginnings/joe/*`
- 상전이 오케스트레이션: `engine.py` (`run_noah_cycle`, `evaluate_postdiluvian`)
- 이 파일: 각 시나리오 정의 / 실행법 / 결과 해석 요약

> ⚠️ 주의  
> 여기서 말하는 "시나리오"는 **사실 확정 하드코딩이 아니라,  
> instability(t) / risk(t) 에 대한 설정**이다.  
> 물리 법칙은 그대로 두고, 관찰자·모델러가 입력 파형을 어떻게 선택하느냐에 따라
> 서로 다른 상전이 경로를 실험하는 용도다.

---

## 1. 시나리오 정의

시나리오들은 모두 `scenarios.py` 에 구현되어 있다.

- 공통:
  - `run_noah_cycle()` 에 `joe_instability_fn(t)` / `risk_fn(t)` / `mode` 를 넘겨
    `NoahSimulationResult` 를 얻는다.
  - 이후 `evaluate_postdiluvian(result)` 로 post-flood IC 가
    현재 지구(Postdiluvian) 타깃과 얼마나 가까운지 평가한다.

### A. macro_only — JOE 거시 물리만으로 붕괴

- 함수: `run_scenario_macro_only()`
- 설정:
  - years = 25 yr, dt_yr = 0.1 yr
  - `joe_instability_fn(t)`:
    - t=0 → 0.1, t=years → 1.0 근방 선형 증가
  - `risk_fn = None`, `mode="macro"`
- 해석:
  - 질량·회전·판/물 예산 같은 거시 구조만 서서히 한계에 다다라,
    궁창이 피로 누적 없이 **조(JOE) 시그널 하나만으로 붕괴**하는 경우를 본다.
  - 시뮬레이션 기간(years)이 충분하지 않으면 FloodEngine 이 `complete`에
    도달하지 못해 `post_ic` 가 생성되지 않을 수 있다는 점에 유의해야 한다
    (즉, “붕괴·홍수는 발생하지만 아직 완전 안착 전” 상태가 나올 수 있다).

### B. macro_decay — 낮은 instability + 장기 decay

- 함수: `run_scenario_macro_decay()`
- 설정:
  - years = 80 yr, dt_yr = 0.5 yr
  - `joe_instability_fn(t) = 0.3` (상대적으로 낮은 값 유지)
  - `risk_fn = None`, `mode="decay"`
- 해석:
  - instability 자체는 낮지만, decay 모드가 상향 보정을 해 주어
    **“JOE 신호를 약간 더 높게 본 상태에서, 여전히 임계치를 넘지 못하는지”**를 보는 케이스다.
  - 현재 구현에서는 시간 누적/감쇠 항이 없기 때문에,
    `joe_instability_fn(t)` 또는 `risk_fn(t)` 가 시간에 따라 올라가지 않으면
    **자연스럽게 붕괴로 가지 않는다**는 점을 확인하는 용도다
    (즉, “장기 안정” 시나리오).

### C. combined_ramp — 조 + 수순환 + 온실 + 자기권 램프업

- 함수: `run_scenario_combined_ramp()`
- 설정:
  - years = 25 yr, dt_yr = 0.1 yr
  - `joe_instability_fn(t)`:
    - t=0 → 0.2, t=years → 0.8 정도까지 선형 증가
  - `risk_fn(t)`:
    - t < 0.4·years: water/greenhouse/magnetosphere ≈ 0.1 (안정기)
    - 0.4·years ≤ t < 0.7·years: 수순환·온실 리스크를 0.8 근방까지 가파르게 램프업
    - t ≥ 0.7·years: high-risk 구간 유지
  - `mode="combined"`
- 해석:
  - 거시 불안정성과 미시 환경 리스크가 함께 상승해
    **고에너지 궁창 시대가 스스로 버티지 못하고 무너지는** 복합 상전이.
  - 질문에서 언급한 “시나리오 C (복합 트리거)”를 코드로 옮긴 버전이다.

### D. impulse_shock — 외부 임팩트(혜성/플레어 등) 임펄스

- 함수: `run_scenario_impulse_shock()`
- 설정:
  - years = 20 yr, dt_yr = 0.1 yr, shock_time ≈ 10 yr
  - `joe_instability_fn(t)`:
    - 기본선 0.25 (안정)
    - |t - shock_time| < 0.5 yr   → 0.9 (강한 임펄스)
    - |t - shock_time| < 1.0 yr   → 0.7 (완충 구간)
  - `risk_fn(t)`:
    - water/greenhouse/magnetosphere 리스크에 비슷한 임펄스 부여
  - `mode="combined"`
- 해석:
  - 평소에는 안정적인 궁창이지만,
  - 혜성 충돌, 거대 태양 플레어, 외부 필드 쇼크 등으로
    **짧은 시간 동안 instability·risk 가 임계선을 뛰어넘는 경우**를 모델링한다.

### E. combined_impulse — 퓨즈 모델(복합 램프 + 임펄스)

- 함수: `run_scenario_combined_impulse(..., impact_params=None)`
- 설정:
  - combined_ramp 와 동일한 거시·환경 램프로 임계 근처(0.7~0.8)까지 올린 뒤,
  - shock_time 근처에 임펄스를 겹친다.
  - **impact_params** 가 주어지면 `_06_lucifer_impact.estimate_impact(impact_params)` 로
    `shock_strength` 를 산출해 그 값으로 임펄스 크기를 정한다.
  - `impact_params=None` 이면 기존과 동일(하드코딩 0.25/0.10, 0.9/0.7).
- 해석:
  - "이미 임계 근처까지 쌓인 스트레스(L1~L3) + 외부 도화선(L4)" Fuse 모델.
  - **(D, v, ρ, θ, h) 스윕**: `impact_params=ImpactParams(D_km=..., v_kms=..., ...)` 를 바꿔 가며
    `run_scenario_combined_impulse(impact_params=...)` 를 반복 호출하면,
    "어떤 충돌 조합이 postdiluvian_ok 를 만드는가"를 동역학 실험으로 볼 수 있다.

### F. lucifer_impact_mid_ocean — 루시퍼 임팩트(10km 심해)

- 함수: `run_scenario_lucifer_impact_mid_ocean()`
- 설정: 10km 암석, 20 km/s, 45°, h_km=4.0 등 고정 → `estimate_impact()` → shock_strength 를
  combined_impulse 패턴에 적용. 즉 E의 `impact_params` 를 한 조합으로 고정한 편의 시나리오.

---

## 2. 실행 방법

### 2.1 Python 모듈에서 호출

```python
from solar._05_noah_flood import scenarios

# 시나리오 C — 복합 램프
result, report = scenarios.run_scenario_combined_ramp()

print(report["ok"], report["checks"])
print(report["values"])
```

### 2.2 CLI 로 한 번에 네 가지 시나리오 실행

`scenarios.py` 는 `__main__` 블록을 포함하고 있으므로,
아래처럼 네 가지 시나리오를 순서대로 돌려볼 수 있다.

```bash
python -m solar._05_noah_flood.scenarios
```

출력 예(형식):

```text
[macro_only] steps=...
  t_start=..., instability=..., firmament_phase=...
  t_end=...,   instability=..., firmament_phase=..., flood_phase=..., sea_level_anom=...
  postdiluvian_ok=True
  checks_ok=['...']

...
```

각 시나리오별로:

- 궁창이 언제 어떤 phase 에서 붕괴하는지
- FloodEngine 이 어느 시점에 complete 에 도달하는지
- post-flood IC 가 지구형 타깃과 일치하는지 (`report["ok"]`)

를 비교할 수 있다.

---

## 3. “어떤 시나리오가 더 가능성이 있는가?”를 해석할 때

이 레이어의 목표는 **“역사적 사실을 확정한다”가 아니라,  
주어진 물리·환경·생물 파라미터 안에서 어떤 경로들이
동역학적으로 일관된지를 비교하는 것**이다.

- macro_only / macro_decay:
  - 조(JOE) 거시 구조만으로도 상전이가 가능한지,  
    혹은 긴 시간 축의 노화로만 붕괴 가능한지 본다.
- combined_ramp:
  - 수순환·온실·자기권 같은 MOE 스타일 리스크가 함께 작동할 때
    붕괴 시점이 어떻게 조정되는지 확인한다.
- impulse_shock:
  - 외부 임팩트가 없이는 붕괴하지 않는 상태에서,
    한 번의 강한 쇼크만으로 상전이가 발생 가능한지 테스트한다.

실제 “가능성” 평가는:

- 어떤 시나리오가 현재 지구(Postdiluvian)의 타깃 값과 가장 잘 맞는지
- 어떤 시나리오에서 Firmament/Flood 곡선이 **더 물리적으로 자연스러운지**

를 함께 비교해서 판단해야 한다.

---

## 4. 다음 단계 아이디어

- 시뮬레이션 결과(steps 리스트)를 CSV/JSON 으로 덤프하는 헬퍼 추가  
  → `_meta/20_CONCEPT/` 아래에 각 시나리오별 플롯/리포트 저장.
- postdiluvian IC 에서 EdenSearch / EdenOS 를 다시 가동해
  “포스트-플러드 문명 시나리오” 를 별도 레이어로 작성.
- ENGINE_HUB 의 JOE/MOE 독립 엔진과 직접 연결해,
  instability / risk(t) 함수를 실제 평가기로부터 바로 가져오는 모드 구현.

