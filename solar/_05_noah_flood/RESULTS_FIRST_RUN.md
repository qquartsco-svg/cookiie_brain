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
```

요약 테이블:

| 시나리오        | 궁창 붕괴 | 홍수 진행        | postdiluvian_ok | 해석                                    |
|-----------------|-----------|------------------|-----------------|-----------------------------------------|
| macro_only      | O         | stabilizing 까지 | NG (`has_post_ic=False`) | 거시 불안정도로 붕괴·홍수는 발생, 안착 전 종료 |
| macro_decay     | X         | X                | NG              | instability=0.4 유지 → 임계 0.85 미달     |
| combined_ramp   | X         | X                | NG              | eff_inst 최대 0.779 → 붕괴 미발생        |
| impulse_shock   | O         | complete         | OK              | 외부 임펄스 1회로 붕괴 + 완전 상전이      |

---

## 3. 1차 결론 — “가장 큰 영향”은 무엇인가?

현재 파라미터 셋과 시나리오 정의에서 보면:

- **macro_only (거시 물리 램프업)**  
  - JOE instability 만으로도 **궁창 붕괴와 대홍수 시작**까지는 충분히 만든다.
  - 다만 25년이라는 시뮬레이션 기간에서 FloodEngine 이 `complete` 에
    도달하지 못해 post_ic 가 생성되지 않았다.  
  - → **거시 구조만으로도 대홍수는 필연**, 하지만 “지구형 안착”까지는
    더 긴 감쇠 시간이 필요하다는 시그널.

- **macro_decay / combined_ramp (노화·환경 복합)**  
  - 설정된 instability / risk 램프가 임계 0.85에 도달하지 못해
    **궁창이 끝까지 유지**된다.  
  - → 이 파라미터 셋에서는 “느린 노화”나 “완만한 환경 변화”만으로는
    노아급 붕괴를 설명하기 어렵다는 방향의 결과.

- **impulse_shock (외부 임펄스)**  
  - 평소에는 안정적인 상태에서, **짧은 시간의 강한 충격**만으로
    궁창이 무너지고 FloodEngine 이 complete 까지 진행,  
    `evaluate_postdiluvian()` 모든 체크를 통과하는 **완전한 상전이**를 만든다.
  - → 현재 모델·파라미터 기준에서,
    > “대홍수 이벤트를 끝까지 밀어 지구형 환경으로 안착시키는 데
    > 가장 큰 영향은 **외부 임펄스(충격) 시나리오**다.”

**1차 요약**  

- 행성 거시 불안정도(JOE)만으로도 붕괴·홍수 자체는 설명 가능하다.  
- 그러나 “에덴 궁창 시대 → 현재 지구(Postdiluvian)”까지의 **완전한 상전이**는  
  현재 실험 셋업에서는 **강한 외부 충격(impulse_shock)** 이 있을 때 가장 자연스럽게 닫힌다.

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

