# LUCIFER_IMPACT_MODEL — 루시퍼 임팩트(혜성 충돌) 개념 레이어

이 문서는 `_06_lucifer_impact/impact_estimator.py` 와
`_05_noah_flood/scenarios.py` 의 루시퍼 임팩트 시나리오가
어떤 개념 구조를 가지는지 정리한다.

목표:

- "지름 D, 밀도 ρ, 속도 v, 깊이 h 의 충돌체가
  궁창/대기/해수/극-적도 온도차에 어느 정도 영향을 줄 수 있는지"
  를 오더 수준에서 추정하고,
- 그 결과를 Noah 시나리오(run_noah_cycle)에 연결해
  **현재와 같은 postdiluvian 지구 상태가 나올 수 있는지**를 실험하는 것.

---

## 1. 레이어 구조 (개념)

| 레이어 | 축 | 설명 |
|--------|----|------|
| L0 | 충돌 파라미터 | (D_km, ρ, v_kms, θ, h_km, lat, lon) |
| L1 | 운동 에너지 | \(E = 0.5 m v^2\), 입사각에 따른 유효 에너지 \(E_\text{eff} = E \sin\theta\) |
| L2 | 매질 분배 | 대기/해수/지각으로 에너지가 어떻게 나뉘는지 (f_atm, f_ocean, f_crust) |
| L3 | 환경 델타 | ΔH2O_canopy, Δpressure_atm, Δsea_level, Δpole_eq_delta_K 추정 |
| L4 | Noah 연결 | shock_strength 및 환경 델타를 instability(t), risk(t), IC 에 주입 |

요약하면:

> L0~L2 에서 에너지 스케일을 잡고,  
> L3 에서 "궁창·대기·해수·극지"가 얼마나 바뀌는지 추정하고,  
> L4 에서 Noah 시나리오에 연결해 postdiluvian 검증까지 본다.

---

## 2. 코드 대응

- `_06_lucifer_impact/impact_estimator.py`
  - `ImpactParams` : D_km, rho_gcm3, v_kms, theta_deg, h_km, lat_deg, lon_deg
  - `ImpactResult` : E_total_J, E_eff_J, f_atm/f_ocean/f_crust,
    ΔH2O_canopy, Δpressure_atm, Δsea_level_m, Δpole_eq_delta_K, shock_strength
  - 내부에서 Chicxulub 급(10km rock, 20km/s) 충돌을 스케일 1.0 으로 두고
    전지구 평균 에너지밀도(J/m²)를 기반으로 정규화한다.

- `_05_noah_flood/scenarios.py`
  - `run_scenario_lucifer_impact_mid_ocean()`  
    → 중간 크기 암석체가 심해에 떨어지는 경우를 가정해,
      combined_impulse 패턴에 `_06_lucifer_impact` 의 shock_strength 를 얹어 본다.

---

## 3. 물리적 해석 (주의사항)

- 이 모델은 "정밀한 충돌 지질학"이 아니라,
  - 궁창 캐노피 0.05 → 0.0, pressure_atm 1.25 → 1.0,
  - sea_level_peaks ≈ 80m,
  - pole_eq_delta_K ≈ 15K → 48K
  와 같은 Noah/Firmament/IC 타깃을 맞추기 위한 **오더 추정기**다.

- 실제 지구에서 어떤 충돌이 있었는지(언제, 어디, 얼마만큼)는
  - 이 레이어만으로는 확정할 수 없고,
  - 별도의 지질 데이터(크레이터, 퇴적층, 빙하 코어 등)와의 캘리브레이션이 필요하다.

---

## 4. Noah 시나리오와의 연결

1. `ImpactParams` 를 정한다 (예: 10km rock, 20km/s, 심해 4km, θ=45°).
2. `estimate_impact(params)` 로 ImpactResult 를 구한다.
3. ImpactResult.shock_strength 를 instability(t), risk(t) 의
   shock 구간에 상수배로 얹는다.
4. 필요하면 ΔH2O_canopy, Δpressure_atm 등을
   `make_antediluvian()` 출력에 적용해 "충돌 직후 IC" 를 만든 뒤,
   Noah 시나리오를 실행한다.

이렇게 해서,

> "이 정도 크기/속도/깊이의 충돌이 있었을 때,  
> 현재 우리가 알고 있는 postdiluvian 지구 상태로 상전이할 수 있는가?"

를 실제 코드로 실험할 수 있다.

