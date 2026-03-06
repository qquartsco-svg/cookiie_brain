# _07_polar_ice — 극지방 첫 결빙 · 빙하시대 개시

**L0_solar 서사 레이어 7번째 챕터**

> 루시퍼가 바다에 충돌했다. 하늘에서 불과 돌이 쏟아졌다.  
> 수증기 캐노피가 찢겨 사라지고, 처음으로 극지방에 얼음이 생겼다.  
> 빙하시대가 시작되었다.

---

## 서사 위치

```
_04_firmament_era   창공 시대
  수증기 캐노피가 전지구를 덮어 온실 효과 유지
  → 극지방도 0°C 근방. 얼음 없음.
        ↓
_05_noah_flood      노아 이벤트
  firmament_collapse() → impulse_shock
  → 창공 붕괴. 물이 하늘에서 쏟아짐 (40일 밤낮).
        ↓
_06_lucifer_impact  루시퍼 충돌
  E = 2.2 × 10⁶ MT  /  AOD = 1.26  /  ΔT_pole = −7K
  → 에너지·크레이터·쓰나미 계산.
        ↓
_07_polar_ice   ←  지금 여기
  창공 소멸 + 에어로졸 72% 태양광 차단
  → 충돌 후 1개월: 극지방 -3.4°C → 첫 결빙
  → 3년:  얼음 5m 형성
  → 50년: -29°C 항구적 해빙 → 빙하시대 개시
```

**서사적 의미:**  
`_07_polar_ice`는 "노아 홍수로 얼음이 생겼다"는 주장이 아니다.  
`_06_lucifer_impact`의 에너지 출력을 수치 입력으로 받아  
극지방 기후 시스템의 **상전이(phase transition)**를 동역학으로 실험하는 레이어다.  
얼음이 생기느냐 안 생기느냐는 모델 파라미터에 달려 있다 — 하드코딩이 아니다.

---

## 엔지니어링 구조

### 패키지 구성

```
_07_polar_ice/
├── __init__.py          공개 API: run_polar_simulation(), PolarSimResult
├── climate.py           충돌 후 대기 강제 다이나믹스
├── energy_balance.py    극지방 복사 수지 (Budyko-Sellers)
├── stefan_ice.py        Stefan 결빙 성장 법칙
├── simulation.py        통합 시뮬레이션 오케스트레이터
└── README.md
```

### 의존성

```
_07_polar_ice는 외부 모듈에 의존하지 않는다.
  import: numpy, math (표준 라이브러리)
  입력:   숫자값 (E_eff_MT, delta_H2O_kg, delta_T_pole_K)

_06_lucifer_impact와의 관계:
  코드 의존성: 없음
  데이터 흐름: lucifer_strike() 출력 → run_polar_simulation() 입력
```

### 빠른 사용

```python
# LuciferEngine과 연결
from L0_solar._06_lucifer_impact import lucifer_strike
from L0_solar._07_polar_ice import run_polar_simulation

ir, cr, ts = lucifer_strike(D_km=5.0, is_ocean=True, v_kms=25.0)

result = run_polar_simulation(
    E_eff_MT           = ir.E_eff_MT,          # 유효 충돌 에너지 [MT]
    delta_H2O_kg       = ir.delta_H2O_canopy,  # 수증기 주입 [kg]
    delta_T_pole_K     = ir.delta_pole_eq_K,   # 극지방 온도 강하 [K]
    lat_deg            = 85.0,                 # 시뮬레이션 위도
    t_max_yr           = 50.0,                 # 시뮬레이션 기간 [년]
    T_pole_preimpact_K = 273.15,               # 충돌 전 극지방 기온 [K]
)
print(result.summary())
```

### 출력 구조 (`PolarSimResult`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `freeze_onset_yr` | `float \| None` | 첫 결빙 시각 [년] |
| `max_ice_m` | `float` | 최대 얼음 두께 [m] |
| `ice_persists` | `bool` | 시뮬레이션 종료 시 얼음 유지 여부 |
| `steps` | `List[SimStep]` | 전체 시계열 (T, h_ice, h_snow, albedo, AOD …) |
| `events` | `List[dict]` | freeze_onset / melt 이벤트 로그 |

---

## 시뮬레이션 물리 모델

### 1. 충돌 후 기후 강제 (`climate.py`)

충돌 에너지가 대기에 미치는 영향을 시간 함수로 모델링.

| 변수 | 방정식 | 의미 |
|------|--------|------|
| AOD(t) | τ₀ · exp(−t/τ_aer) | 에어로졸 광학 깊이 감쇠 |
| τ₀ | 0.5 · (E_MT/1e5)^0.3 | 초기 AOD (에너지 경험식) |
| f_block(t) | 1 − exp(−AOD) | 태양광 차단율 |
| ΔT_global(t) | ΔT₀ · exp(−t/τ_clim) | 전지구 기온 강하 |
| H₂O(t) | C₀ · exp(−t/τ_h2o) | 수증기 캐노피 잔여량 |

**기준 파라미터 (루시퍼 5km):**
- τ₀ = 1.26 → 태양광 72% 차단 (t=0)
- τ_aer = 2년 (성층권 에어로졸 수명)
- τ_clim = 10년 (전지구 기온 회복 시상수)

### 2. 극지방 복사 수지 (`energy_balance.py`)

Budyko-Sellers 에너지 수지 모델 — 대기 자오선 열 수송 포함.

```
Q_sw · (1−α) · (1−f_block)  +  Q_ocean  +  λ · (T_global − T_pole)  =  ε · σ · T⁴

Q_sw     = S₀/4 · f_lat(θ)                  단파 입사
Q_ocean  = 15 W/m² (충돌 후 감소)             해양 열 공급
λ        = 3.3 W/(m²·K)                      자오선 대기 열 수송
ε · σ·T⁴                                     Stefan-Boltzmann 장파 방출
```

**자오선 열 수송(λ)이 필수인 이유:**  
없으면 85°N 에너지 평형 온도 = −115°C (비현실). 있으면 −25°C (관측과 일치).

**알베도 피드백:**

| 상태 | α | 결과 |
|------|---|------|
| 개방 해양 | 0.06 | 많이 흡수 → 따뜻 |
| 얼음 피복 | 0.50 | 많이 반사 → 냉각 강화 |
| 얼음 1m → f_ice = 0.5 → α = 0.28 | (점진적) | 선형 전환 |

**수치 적분 방법: 암묵적 Euler (선형화)**

```
T_new = (C · T_old + dt · [Q_src + 4εσT_old³ · T_old − εσT_old⁴])
        / (C + dt · [4εσT_old³ + λ])
```

명시적 Euler는 빙-알베도 피드백에서 수치 발산. 암묵적 Euler → 무조건 수렴.

### 3. Stefan 결빙 성장 법칙 (`stefan_ice.py`)

Josef Stefan (1891) — 해빙 두께 성장의 열역학적 해석해.

```
기본 법칙:  dh/dt = k_ice · ΔT / (ρ_ice · L_f · h)

적분 해:   h(t) = √(2 · k_ice · ΔT · t / (ρ_ice · L_f))
                = √(A · t)    [A = 2·k·ΔT/ρ·Lf,  m²/s]
```

**특성: h ∝ √t**
- 초기(h 작을 때): 빠르게 성장
- 시간이 지날수록: 점점 느려짐
- 물리적 이유: 얼음이 두꺼워질수록 열이 빠져나가기 어려워짐

**적설 단열 보정 (Maykut 1986):**

```
눈이 쌓이면 열전도 저하 → 결빙 느려짐
h_ice · (h_ice/k_ice + h_snow/k_snow) = A₀ · t
→ 이차방정식 풀이: h = (−b + √(b²+4A₀t)) / 2
```

**사용된 물리 상수:**

| 상수 | 값 | 단위 | 출처 |
|------|-----|------|------|
| k_ice | 2.1 | W/(m·K) | 해빙 열전도 |
| k_snow | 0.31 | W/(m·K) | 신설 열전도 |
| ρ_ice | 917 | kg/m³ | 얼음 밀도 |
| L_f | 334,000 | J/kg | 융해 잠열 |
| T_freeze | 271.35 | K | 해수 결빙 온도 (−1.8°C) |
| H_max | 5.0 | m | 다년빙 두께 한계 |

참조: Stefan (1891), *Ann. Phys.* 278:269 / Maykut (1986), *The Geophysics of Sea Ice*, Ch. 2

---

## 시뮬레이션 결과 — 루시퍼 5km, 85°N, 창공 전제

> 충돌 전 극지방 기온 = 0°C (수증기 캐노피 온실 효과)

```
시각(년)   T_극(°C)   얼음(m)  적설(m)   AOD    차단률
─────────────────────────────────────────────────────
  0.0       -1.77    0.000   0.000   1.264   71.7%    ← 충돌 직후. 아직 해수.
  0.1       -3.43    0.000   0.000   1.202   70.8%  ❄ ← 첫 결빙 (1개월)
  1.0      -14.72    1.628   0.216   0.767   53.5%  ❄ ← Stefan 급성장
  2.0      -22.23    3.545   0.176   0.465   37.2%  ❄ ← 알베도 피드백
  3.0      -26.33    5.000   0.108   0.282   24.6%  ❄ ← 5m 한계 도달
 10.0      -30.12    5.000   0.001   0.009    0.9%  ❄ ← 에어로졸 소진
 50.0      -29.00    5.000   0.000   0.000    0.0%  ❄ ← 항구적 빙하 (빙하시대)
```

**물리 해석:**
1. 에어로졸이 태양광 72% 차단 → 열 입력 급감
2. 창공 소멸 → 온실 효과도 동시 상실 → 복합 냉각
3. 1개월 만에 첫 결빙 → Stefan 성장 개시
4. 알베도 피드백(α: 0.06 → 0.50) → 냉각 추가 강화 (자기 강화 루프)
5. 에어로졸 10년 후 소진되도 얼음 유지 → **알베도 잠금(albedo lock-in)**
6. 결과: 영구 극지방 빙하 → 빙하시대 개시

---

## 파라미터 설명

| 파라미터 | 기본값 | 단위 | 설명 |
|----------|--------|------|------|
| `E_eff_MT` | — | MT | 유효 충돌 에너지 (LuciferEngine 출력) |
| `delta_H2O_kg` | 0.0 | kg | 대기 수증기 주입량 |
| `delta_T_pole_K` | 0.0 | K | 충돌 직후 극지방 온도 강하 (음수) |
| `lat_deg` | 85.0 | ° | 시뮬레이션 위도 |
| `t_max_yr` | 50.0 | yr | 시뮬레이션 기간 |
| `T_pole_preimpact_K` | 250.0 | K | 충돌 전 극지방 기온 (창공 전제: 273.15) |
| `tau_aerosol_yr` | 2.0 | yr | 에어로졸 수명 |
| `tau_climate_yr` | 10.0 | yr | 전지구 기온 회복 시상수 |
| `Q_ocean_base` | 15.0 | W/m² | 충돌 전 해양 열 공급 |

---

## 한계 및 주의사항

- **Stefan 법칙은 1D 열전도 모델** — 해빙 이동·동적 두께화 미포함
- **Budyko-Sellers는 연평균 에너지 수지** — 계절성(극야/백야) 미분리
- **자오선 열 수송 λ=3.3은 현재 기후 기준** — 창공 시대 대기 순환은 다를 수 있음
- **AOD 경험식은 Chicxulub 외삽** — 해양 충돌에서 에어로졸 생성량은 불확실
- **알베도 피드백 최댓값 h_max=5m** — 실제 다년빙은 수렴 이후 동적 평형

---

## 다른 레이어와의 관계

| 방향 | 레이어 | 내용 |
|------|--------|------|
| 입력 받음 | `_06_lucifer_impact` | E_eff_MT, delta_H2O, delta_T_pole |
| 독립 패키지 연결 | `ENGINE_HUB/Lucifer_Engine` | lucifer_engine.run_effects() |
| 출력 전달 | `_08_ice_age/` | T_pole_K → 빙상 질량수지 초기 조건 |
