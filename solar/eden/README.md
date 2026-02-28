# solar/eden — 에덴 시스템 (창세기 2장)

천지창조(Day1~7)가 완성된 행성 위에 올라오는 **에이전트·환경 레이어**.  
창세기 1장(물리 행성) → 창세기 2장(에덴·대홍수 환경) 구조를 코드로 구현한다.

---

## 1. 구조 요약

| 파일 | 역할 | 핵심 개념 |
|------|------|-----------|
| **firmament.py** | 궁창(Raqia) 레이어 | 상층 수증기 캐노피 → UV 차폐, 극적도 균온화, 붕괴 시 대홍수 |
| **flood.py** | 대홍수 이벤트 엔진 | 궁창 붕괴 후 환경 전이 곡선 (rising → peak → receding → stabilizing) |
| **initial_conditions.py** | 지구 초기 환경 (동역학) | 6개 독립 파라미터 → τ, T, GPP, mutation 등 자동 계산 |
| **geography.py** | 에덴 시대 지리·자기장 | f_land=0.40 노출 지형, 자기 N극=남극 좌표계, 위도별 보호 강도 |
| **search.py** | 에덴 탐색 엔진 | 파라미터 공간 스캔 → EdenCriteria 판정 → EdenCandidate 랭킹 |
| **biology.py** | 생물학 레이어 | 물리(UV, O2, GPP, mutation) → 수명·체형·생태계 안정성 |

**환경 3단계**

- **antediluvian** — 대홍수 이전 (궁창 존재, 에덴)
- **flood** — 대홍수 진행 (궁창 붕괴)
- **postdiluvian** — 대홍수 이후 (현재 Day7 기준점)

---

## 2. 개념·수식 정리

### 2.1 궁창 (firmament.py)

**창세기 1:6–7**  
"궁창 위의 물과 궁창 아래의 물" → 상층 수증기 캐노피 `H2O_canopy` 로 모델링.

| 효과 | 수식/설명 |
|------|-----------|
| UV 차폐 | `uv_shield_factor = min(0.95, H2O_canopy/0.05 × 0.95)` (H2O 5%일 때 0.95) |
| 돌연변이율 | 에덴 0.01× ↔ 현재 1.0×, 캐노피 비율로 선형 보간 |
| 알베도 | 에덴 0.20 (빙하 없음) ↔ 현재 0.306, 캐노피 비율로 보간 |
| 대기압 | `pressure_atm = 1.0 + H2O_canopy × 5` (5% → 1.25 atm) |
| 극적도 ΔT | 에덴 15 K ↔ 현재 48 K, 캐노피 비율로 보간 |
| 추가 광학깊이 | `delta_tau = α_H2O × (√(c/H2O_ref) - √(0.01/H2O_ref))`, α_H2O=0.940 |

**붕괴 시**  
`trigger_flood()` → `FloodEvent`: 해수면 상승 추정, f_land 변화, T_drop, UV 소실, mutation 점프.

---

### 2.2 대홍수 전이 (flood.py)

**창세기 7:11** — "큰 깊음의 샘들이 터지며 하늘의 창문들이 열려"

| 단계 | 시간 구간 | f_land | albedo | T, mutation, pole_eq_delta 등 |
|------|-----------|--------|--------|-------------------------------|
| rising | 0 ~ 0.11 yr (40일) | 0.40 → 0.10 | 0.20 → 0.10 | 급격한 침수, ease_in |
| peak | 0.11 ~ 0.50 yr | 0.10 | 0.10 | 절정 유지 |
| receding | 0.50 ~ 1.00 yr | 0.10 → 0.29 | 0.10 → 0.23 | 물 빠짐, ease_out |
| stabilizing | 1 ~ 10 yr | 0.29 | → 0.306 | 극지 냉각, 빙하 성장 |
| complete | 10 yr~ | 0.29 | 0.306 | 현재 지구 |

보간: `_lerp(a, b, p)`, `_ease_in(p)=p²`, `_ease_out(p)=1-(1-p)²`.

---

### 2.3 초기조건 동역학 (initial_conditions.py)

**철학**: "하드코딩이 아니라 물리 인과관계로 초기조건을 결정."

**6개 독립 파라미터**  
`CO2_ppm`, `H2O_atm_frac`, `O2_frac`, `albedo`, `f_land`, `precip_mode` (+ 선택: `H2O_canopy`, `UV_shield`, `pressure_atm` 등).

| 단계 | 수식 |
|------|------|
| 광학 깊이 | `τ = τ_base + α_CO2·ln(1+CO2/CO2_ref) + α_H2O·√(H2O/H2O_ref) + α_CH4·√(CH4/CH4_ref)` |
| 온실 효율 | `ε_a = 1 - exp(-τ)` |
| 지표 온도 | `T_surface = (F_abs/(σ·(1-ε_a/2)))^0.25`, F_abs = F_SOLAR·(1-albedo)/4 |
| 극적도 ΔT | `ΔT = 48 - 33×min(H2O_canopy/0.05, 1)` (K) |
| 밴드 온도 | `T_band = T_mean + ΔT × (cos(lat) - 0.5)×2` |
| 토양 수분 | mist: 0.75 균일; drizzle: 0.65; rain: 위도별 (적도 0.85, 극 0.25) |
| GPP | `GPP = P_MAX·f_I·f_C(CO2)·f_T(T)·f_W(W)·f_O2`, f_T 가우시안(25°C), f_O2 고기압 보정 |
| 돌연변이율 | `mutation_factor = max(1 - UV_shield×0.99, 0.01)` |

**12개 위도 밴드**  
중심 위도: ±82.5°, ±67.5°, ±52.5°, ±37.5°, ±22.5°, ±7.5°.  
빙하: T_C < -10°C; 거주가능: -40°C < T_C < 65°C.

**프리셋**

- **make_antediluvian()**: CO2 250 ppm, H2O 6%(캐노피 5%), O2 24%, albedo 0.20, f_land 0.40, mist, pressure 1.25, UV_shield 0.95.
- **make_postdiluvian()**: CO2 280 ppm, H2O 1%, O2 21%, albedo 0.306, f_land 0.29, rain, pressure 1.0, UV_shield 0.

---

### 2.4 지리·자기장 (geography.py)

**전제**

- 지리 남극 근처 = 자기 N극 (자기력선 출발).
- 세차: Rotation frame(교과서) vs Magnetic frame(자기장 기준).

| 항목 | 수식/설명 |
|------|-----------|
| 지리→자기 위도 | `mag_lat ≈ geo_lat + tilt_deg×cos(geo_lat°)`, tilt_deg=11° |
| 위도별 보호 강도 | `protection = 0.5 + 0.5×sin(|mag_lat|°)` [0~1] |

**에덴 시대 노출 지형** (f_land=0.40, 해수면 -70 m)  
Beringia, Sundaland, North_Sea_Land, Arctic_Shelf_East, Sahul, Antarctic_Coast 등 — `EDEN_EXPOSED_REGIONS`.

**북극해**  
에덴: 베링 육교·동시베리아 대륙붕 노출 → 반폐쇄 내해, 현재 대비 면적 ~45%.

---

### 2.5 에덴 탐색 (search.py)

**철학**: "에덴은 특정 좌표가 아니라 특정 파라미터 상태(state basin)이다."

**EdenCriteria (모두 만족 시 PASS)**

| 기준 | 기본값 | 의미 |
|------|--------|------|
| T_range | 15~45°C | 지표 온도 |
| GPP_min | ≥ 3.0 kg C/m²/yr | 전 지구 GPP |
| ice_bands_max | 0 | 빙하 밴드 수 |
| mutation_max | ≤ 0.10 | mutation_factor |
| hab_bands_min | ≥ 10 | 거주 가능 밴드 |

**에덴 종합 점수** [0~1]  
`compute_eden_score`:  
GPP 30% + 온도 최적성(25°C 근처 가우시안) 25% + mutation 낮음 20% + 거주 밴드 15% + 빙하 없음 10% + (geo 있으면) 자기장 보너스 최대 10%.

**밴드별 에덴 점수**  
`compute_band_eden_scores`:  
밴드마다 온도 적합도 + 토양수분 + GPP 정규화 + 자기 보호, hab·(1-ice) 마스크.

**SearchSpace**  
CO2, H2O_atm, H2O_canopy, O2, albedo, f_land, UV_shield 범위와 steps로 그리드 생성.  
`make_antediluvian_space()`, `make_postdiluvian_space()`, `make_exoplanet_space()`.

**deep_validate**  
선택: PlanetRunner로 n_steps 돌려 CO2/T 안정성·stress 확인 (ImportError 시 스킵).

---

### 2.6 생물학 (biology.py)

**철학**: "물리 환경이 생물 특성을 결정한다." (수명·체형·유전자 안정성은 IC에서 동역학 계산.)

| 인자 | 수식 | 설명 |
|------|------|------|
| UV → 수명 | `factor = min(4, 1+3×UV_shield)` | UV 차폐 → 수명 배수 |
| 온도 → 수명 | `factor = T_ref/T` (0.7~1.3 clamp) | 대사율 역관계 |
| mutation → 수명 | `factor = 1/√(mutation_factor)` (상한 5) | 게놈 무결성 |
| 수명 종합 | 기하평균(UV, 대사, 게놈) × BASELINE_LIFESPAN, 상한 LIFESPAN_PHYSICAL_MAX_YR=600 | |
| O2 분압 → 체형 | `(O2_frac×pressure/0.21)^0.4` (상한 1.8×) | 호흡 효율 |
| GPP → 체형 | `(GPP/2.33)^0.2` (0.8~1.5) | 먹이 풍요도 |
| 신장 | `170 × (body_mult)^(1/3)` cm | 체중^1/3 비례 |

**물리 한계**  
수명 600 yr, 체형 1.8× (서사 900년은 코드 밖).  
거대동물: body_mult≥1.2 and GPP≥4; 안정 생태계: mutation≤0.10 and GPP≥3.

---

## 3. 사용 예

```python
from solar.eden import make_firmament, make_flood_engine, make_antediluvian, make_postdiluvian
from solar.eden import make_eden_search, make_eden_geography, compute_biology

# 궁창 환경 → PlanetRunner에 주입
fl = make_firmament(phase='antediluvian')
env = fl.get_env_overrides()   # H2O_override, albedo_override, pole_eq_delta_K, ...

# 대홍수 발동 후 전이
fl.trigger_flood()
flood = make_flood_engine()
for _ in range(12):
    snap = flood.step(dt_yr=1.0)
    print(snap.flood_phase, snap.T_surface_K)

# 에덴 vs 현재 초기조건
ic_eden = make_antediluvian()
ic_post = make_postdiluvian()
print(ic_eden.summary())

# 에덴 탐색
engine = make_eden_search(phase='antediluvian', strict=False)
result = engine.search(max_candidates=50, min_score=0.50)
result.save("docs/EDEN_SEARCH_RESULT.md")
engine.compare_phases()

# 생물학 비교
state_eden = compute_biology(ic_eden)
print(state_eden.summary())
from solar.eden import compare_biology
print(compare_biology(ic_eden, ic_post))
```

---

## 4. 의존성

- **numpy**: initial_conditions, search, (band 배열).
- **solar 패키지 내부**: eden 모듈끼리만 참조; Day7 runner는 search.deep_validate에서 선택적(ImportError 시 스킵).
- 참고 문서: `docs/ANTEDILUVIAN_ENV.md`, `docs/EDEN_SEARCH_STANDALONE_ENGINE.md`.

---

## 5. 버전

- `__version__`: 0.1.0 (solar.eden)
