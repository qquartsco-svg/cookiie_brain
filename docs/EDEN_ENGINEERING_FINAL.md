# 에덴 엔진 최종 점검 (시스템·물리·엔지니어링)

리뷰 피드백 반영: 패키지 인덱스 검증 + 통합 시 더블카운트 방지 규칙.

---

## 1. 패키지 인덱스 검증 (진입점)

**결론: `solar/eden/__init__.py`가 Eden 패키지 인덱스가 맞다.**

- **from solar.eden import ...** 진입점은 이 파일이다.
- Re-export: firmament, flood, initial_conditions, geography, search, biology (Eden 전용).
- Day5 인덱스(SeedTransport / BirdAgent / FoodWeb)는 `solar/day5/__init__.py`에 있으며, Eden과 별도다.
- 업로드/배포 시 `solar/eden/__init__.py`를 Day5와 혼동하지 않도록 경로 확인 권장.

---

## 2. τ / albedo / ΔT 중복 적용(더블카운트) 방지 규칙

Eden initial_conditions는 이미 다음을 **동역학으로 계산**한다:

- **τ** (광학깊이): `_optical_depth(CO2, H2O, CH4)` → greenhouse 동일 공식
- **ε_a**: `1 - exp(-τ)`
- **T_surface_K**: `_T_surface(τ, albedo)` (1-layer 온실 평형)
- **pole_eq_delta_K**: `_pole_eq_delta(H2O_canopy)` (극적도 온도차)

**Day2 / Day3 / Day7 통합 시 규칙:**

1. **Eden override 사용 시**  
   PlanetRunner(또는 Day7)에 IC를 넘길 때, **Eden이 계산한 τ, ε_a, T_surface_K, pole_eq_delta_K, albedo**를 그대로 사용한다.  
   Day2 AtmosphereColumn이 같은 τ를 **다시 계산해 누적하지 않는다**.

2. **역할 분담**
   - Eden IC: “초기조건 한 번 결정” → τ, albedo, ΔT, band_T 등 제공.
   - Day2: Eden이 값을 넘겼으면 그 값을 쓰고, 넘기지 않았을 때만 자체 τ/온도 계산.

3. **구현 시 체크**
   - `to_runner_kwargs()`가 이미 `T_surface_K_init`, `pole_eq_delta_K`, `albedo_init`, `pressure_atm` 등을 넘김.
   - Runner/AtmosphereColumn 쪽에서 `init`/override가 있으면 **그 값을 최종값으로 쓰고, τ/ε/T를 재계산하지 않는** 분기 필요.
   - 통합 시점에 Day2 코드에서 “Eden IC에서 온 τ”와 “Day2 자체 τ”가 둘 다 적용되는 구간이 없는지 한 번 더 검사.

---

## 3. 상수/계수 Config 화 (규약 준수)

- **상태**: `initial_conditions.py`는 EDEN_IC_CONFIG로 상수/계수 관리, 규약 준수.
- **규약**: “모든 상수는 config/dict로 모아 override 가능하게.”
- **적용 완료**: `initial_conditions.py`에 **EDEN_IC_CONFIG** 도입. 내부 함수는 `config or EDEN_IC_CONFIG` 사용, 호출부에서 `config=`로 override 가능. 통합 시 다른 모듈도 동일 규약 적용 권장.

---

## 4. 기타 리뷰 요약

- **firmament.py**: 개념/수식 반영 OK. H2O_canopy=0.05는 “서사 기반 파라미터화된 월드 룰”로 취급. delta_tau와 Day2 τ 중복은 위 “더블카운트 방지” 규칙으로 통합 시 해소.
- **flood.py**: 전이 구조 OK. Flood 후 postdiluvian 수렴 시 Day7 SabbathJudge 정책(전이 이벤트 제외 여부)은 통합 시 정책 결정.
- **geography.py**: 자기 프레임은 “field line 나오는 쪽/들어가는 쪽”으로 정의 고정 권장. 지리 북/남 vs 자기 북/남 네이밍 충돌만 주의.
- **biology.py**: 수명/체형은 “모델 룰”임을 README/주석에 명시.
- **표현**: 엔지니어링 맥락에서는 “생물체” 사용 권장(agent/organism 단위).

---

## 5. 완결 판정

- **패키지 인덱스**: `solar/eden/__init__.py` 확인 완료 → import path / re-export 완결.
- **τ/albedo/ΔT**: 위 “더블카운트 방지 규칙”으로 통합 시 정책 고정.
- **Config 화**: `EDEN_IC_CONFIG` 도입으로 규약 준수 상태 유지.

이 두 개(인덱스 검증 + 더블카운트 규칙)와 config 화가 정리되면, 에덴 시스템 레이어를 Day7 위에 안정적으로 얹을 수 있는 상태로 본다.
