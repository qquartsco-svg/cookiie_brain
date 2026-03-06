# Noah Flood 시나리오 1차 실험 결과 요약

이 문서는 `_05_noah_flood/scenarios.py` 를 이용해 실행한 **1차 시뮬레이션 결과**를
정리한 것이다. 목표는:

- 현재 파라미터 셋에서 어떤 시나리오가 실제로
  > 궁창 시대 → 붕괴 → 대홍수 → postdiluvian 지구  
  로 완전 상전이를 만드는지,
- 그 과정에서 **대홍수의 “가장 큰 영향 요인”이 무엇으로 보이는지**
  1차 감을 잡는 것이다.

실행 커맨드:

```bash
cd /Users/jazzin/Desktop/00_BRAIN/CookiieBrain
python -m solar._05_noah_flood.scenarios
```

---

## 1. 시뮬레이션 설정 요약

- 공통:
  - `run_noah_cycle()` 를 사용해 years / dt_yr 범위에서 타임라인 시뮬레이션.
  - `evaluate_postdiluvian(result)` 로 post-flood IC 의 지구형 타깃 적합도 평가.
- 임계 조건:
  - `FirmamentLayer.step(..., instability)` 에서  
    `effective_instability ≥ 0.85` 를 붕괴 트리거로 사용.
- 환경 타깃 (make_postdiluvian 기준):
  - `f_land ≈ 0.29`, `albedo ≈ 0.306`, `pressure_atm ≈ 1.0`,
  - `H2O_canopy ≈ 0`, `UV_shield ≈ 0`, `mutation_factor ≈ 1.0`,
  - `T_surface_C ≈ 13.3`, `pole_eq_delta_K ≈ 48`.

---

## 2. 시나리오별 정량 결과

시나리오 러너: `scenarios.py`  
실행: `python -m solar._05_noah_flood.scenarios`

출력(요약):

```text
[macro_only] steps=250
  t_start=0.00 yr, instability=0.100, firmament_phase=antediluvian
  t_end=24.90 yr, instability=0.996, firmament_phase=postdiluvian,
         flood_phase=stabilizing, sea_level_anom=6.56
  postdiluvian_ok=False, checks_ng=['has_post_ic']

[macro_decay] steps=160
  t_start=0.00 yr, instability=0.400, firmament_phase=antediluvian
  t_end=79.50 yr, instability=0.400, firmament_phase=antediluvian
  postdiluvian_ok=False, checks_ng=['has_post_ic']

[combined_ramp] steps=250
  t_start=0.00 yr, instability=0.160, firmament_phase=antediluvian
  t_end=24.90 yr, instability=0.779, firmament_phase=antediluvian
  postdiluvian_ok=False, checks_ng=['has_post_ic']

[impulse_shock] steps=200
  t_start=0.00 yr, instability=0.207, firmament_phase=antediluvian
  t_end=19.90 yr, instability=0.207, firmament_phase=postdiluvian
  postdiluvian_ok=True
  checks_ok=['has_post_ic', 'f_land', 'albedo', 'pressure_atm',
             'H2O_canopy', 'UV_shield', 'mutation_factor',
             'T_surface_C', 'pole_eq_delta_K']

[combined_impulse] steps=300
  t_start=0.00 yr, instability=0.195, firmament_phase=antediluvian
  t_end=29.90 yr, instability=0.779, firmament_phase=postdiluvian,
         flood_phase=complete, sea_level_anom=0.0
  postdiluvian_ok=True
  checks_ok=['has_post_ic', 'f_land', 'albedo', 'pressure_atm',
             'H2O_canopy', 'UV_shield', 'mutation_factor',
             'T_surface_C', 'pole_eq_delta_K']
```

요약 테이블:

| 시나리오           | 궁창 붕괴 | 홍수 진행        | postdiluvian_ok | 해석                                                |
|--------------------|-----------|------------------|-----------------|-----------------------------------------------------|
| macro_only         | O         | stabilizing 까지 | NG (`has_post_ic=False`) | 거시 불안정도로 붕괴·홍수는 발생, 안착 전 종료           |
| macro_decay        | X         | X                | NG              | instability=0.4 유지 → 임계 0.85 미달                   |
| combined_ramp      | X         | X                | NG              | eff_inst 최대 0.779 → 붕괴 미발생                      |
| impulse_shock      | O         | (사실상) complete | OK              | 외부 임펄스 1회로 붕괴 + postdiluvian 타깃 정합         |
| combined_impulse   | O         | complete         | OK              | 복합 스트레스(L1~L3) + 외부 임펄스(L4)가 함께 작동하는 Fuse 모델 |

---

## 3. 1차 결론 — “가장 큰 영향”은 무엇인가?

현재 파라미터 셋과 시나리오 정의에서 보면:

- **macro_only (거시 물리 램프업)**  
  - JOE instability 만으로도 **궁창 붕괴와 대홍수 시작**까지는 충분히 만든다.
  - 다만 25년이라는 시뮬레이션 기간에서 FloodEngine 이 `stabilizing` 단계까지
    진행되었을 뿐 `complete` 에 도달하지 못해 post_ic 가 생성되지 않았다.  
  - → **거시 구조만으로도 대홍수는 필연**, 하지만 “지구형 안착”까지는
    더 긴 감쇠 시간이 필요하다는 시그널.

- **macro_decay / combined_ramp (노화·환경 복합)**  
  - 설정된 instability / risk 램프가 임계 0.85에 도달하지 못해
    **궁창이 끝까지 유지**된다.  
  - → 이 파라미터 셋에서는 “느린 노화”나 “완만한 환경 변화”만으로는
    노아급 붕괴를 설명하기 어렵다는 방향의 결과.

- **impulse_shock (외부 임펄스 단독)**  
  - 평소에는 안정적인 상태에서, **짧은 시간의 강한 충격**만으로
    궁창이 무너지고 FloodEngine 이 사실상 바로 postdiluvian 상태로 점프,  
    `evaluate_postdiluvian()` 모든 체크를 통과하는 **완전한 상전이**를 만든다.

- **combined_impulse (Fuse 모델 — 복합 스트레스 + 외부 임펄스)**  
  - combined_ramp 처럼 거시+환경 스트레스를 먼저 쌓아 effective_instability 를
    임계 바로 아래(0.7~0.8대)까지 올린 뒤,
  - impulse_shock 처럼 shock_time 근처에 임펄스를 추가로 겹쳐
    궁창 붕괴 → 홍수 5단계 → FloodEngine `complete` → postdiluvian IC 생성까지
    깔끔하게 완주한다.
  - → 현재 모델·파라미터 기준에서,  
    > “이미 임계 근처까지 올라온 복합 스트레스 위에 **외부 임펄스(혜성 등)**가
    > 마지막 도화선 역할을 하는 Fuse 시나리오가 매우 자연스럽다.”

**1차 요약**  

- 행성 거시 불안정도(JOE)만으로도 붕괴·홍수 자체는 설명 가능하다.  
- 그러나 “에덴 궁창 시대 → 현재 지구(Postdiluvian)”까지의 **완전한 상전이**는  
  현재 실험 셋업에서는  
  - 순수 외부 임펄스(impulse_shock) 이거나,  
  - 또는 **복합 스트레스(L1~L3) + 외부 도화선(L4)** 이 겹치는 Fuse 모델(combined_impulse)일 때
    가장 자연스럽게 닫힌다.

---

## 4. 후속 실험 아이디어

1. **macro_only / combined_ramp 기간 확장**  
   - years 를 50~100 yr 로 늘려, 시간만 충분히 주면
     FloodEngine 이 complete 까지 가며 post_ic 가 생기는지 확인.
2. **임계·가중치 스윕**  
   - `compute_effective_instability` 의 가중치와
     Firmament 임계(0.85)를 스윕하면서 “내부 요인만으로도 완전 상전이가 되는
     파라미터 영역”을 탐색.
3. **EdenOS 연동**  
   - impulse_shock 의 post_ic 를 `eden_os_bridge` 에 연결해
     “포스트-플러드 문명(노아 이후 세대)” 시나리오를 실행·분석.


---

## 5. 피드백 반영 요약 (구현·해석 정합)

- **"가장 큰 영향이 외부 임펄스인가?"**  
  현재 **코드 기준**에서는, complete/post_ic 까지 닫히게 만드는 **입력 파형**이 임펄스형이었다는 뜻이지,  
  현실 지구의 사실을 단정하는 것이 아니다.
- **4가지 요인(거시·미시·시간·외부충격) 동역학**  
  `joe_instability_fn(t)` + `risk_fn(t)` + (선택) decay/시간 보정 + **estimate_impact().shock_strength** 를  
  `effective_instability` 로 합성해 FirmamentLayer 에 주입하는 구조로 이미 수용 가능하다.
- **combined_impulse 에 루시퍼 임팩트 꽂기**  
  `run_scenario_combined_impulse(impact_params=ImpactParams(...))` 로  
  임펄스를 하드코딩이 아니라 **(D, v, ρ, θ, h)** 로부터 나온 물리량으로 생성할 수 있다.  
  → "어떤 D/v/ρ 조합이 postdiluvian_ok 를 만드는가" 스윕 실험이 가능하다.
