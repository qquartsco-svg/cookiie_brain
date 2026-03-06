# L0_solar — 서사 레이어 (Layer 0)

> **CookiieBrain 상태공간의 서사가 실행되는 곳.**
> 태초의 빛에서 빙하시대까지 — 전체 창조·붕괴·전이 서사를 단계별 물리 모듈로 구현한다.

---

## 서사 전체 흐름

```
[태초]
  _01_beginnings          ← 빛·시간 시작. JOE 관찰자가 행성 거시 조건 탐색
        ↓
  _02_creation_days       ← Day 1~7. 대기·수권·지질·자기권·궤도·생물권 구축
        ↓
  _03_eden_os_underworld  ← 에덴OS 운영. 창공·체루빔·하데스·인지 시스템
        ↓
  _04_firmament_era       ← 창공(수증기 캐노피) 안정화. 극지방 0°C 유지
        ↓
[상전이 트리거]
  _05_noah_flood          ← instability ≥ 0.85 → 창공 붕괴 → 노아 대홍수
        ↓
  _06_lucifer_impact      ← 루시퍼 혜성 충돌. AOD=1.26, 태양광 72% 차단
        ↓
[크라이오스피어 전이]
  _07_polar_ice           ← 충돌 후 1개월 → 극지 결빙. Stefan 법칙. (단기 0~50yr)
        ↓
  _08_ice_age             ← 빙상-알베도 피드백. LGM 재현. 해수면 −125m (장기 ~100,000yr)
```

이 흐름은 **독립적인 물리 모듈**들이 **상태 벡터를 넘겨받아** 순서대로 실행되는 파이프라인이다.
각 단계의 출력이 다음 단계의 초기 조건(initial condition)이 된다.

---

## 상태공간 결합 구조

CookiieBrain의 모든 레이어는 하나의 **상태공간(State Space)** 위에서 맞물린다.
L0_solar는 그 상태공간의 **서사 축**이다.

```
상태공간 벡터 S = {T_global, T_pole, V_ice, instability, AOD, H2O_canopy, sea_level, ...}
                            ↑
          L0_solar의 각 모듈이 S를 읽고, 갱신하고, 다음 모듈에 전달
                            ↓
L1_dynamics   → 자전·조석·에너지 지형  (S의 동역학 장 제공)
L3_memory     → 이벤트 우물 생성·강화  (S의 이벤트를 기억으로 각인)
L4_analysis   → 궤적 측정·분석        (S를 관측, 시스템 변경 없음)
```

---

## 폴더 구조

```
L0_solar/
│
├── _01_beginnings/              태초. 빛·시간 개념 시작
│   └── joe/                     JOE 관찰자: 행성 거시 조건 평가 (instability, planet_stress)
│
├── _02_creation_days/           천지창조 Day 1~7
│   ├── day1/  em/               전자기장·태양풍·자기권·태양광
│   ├── day2/  atmosphere/       대기 기둥·온실 효과·물 순환
│   ├── day3/  biosphere/surface 육지·식물·토양·생태계
│   ├── day4/  core/ cycles/     태양·달·별·조석·밀란코비치
│   ├── day5/                    씨앗·이동·먹이사슬
│   ├── day6/                    종 분화·진화
│   ├── day7/                    완성·안식
│   ├── bridge/                  Gaia Loop ↔ CookiieBrain 연결 브릿지
│   ├── engines/  (01~12)        태양·자기·대기·수권·지권·가이아·궤도 등 서브엔진
│   ├── fields/   firmament/     창공 장(field) 초기화
│   └── physics/  lucifer_core/  루시퍼 코어 물리
│
├── _03_eden_os_underworld/      에덴OS + 언더월드 + 하데스
│   ├── eden/    eden_os/        에덴 탐색·운영·체루빔 가드
│   ├── underworld/              심층 모니터링·전파·규칙
│   ├── biosphere/               생태계 연동
│   ├── cognitive/               스핀-링 커플링 (인지 레이어)
│   ├── governance/  hades/      하데스 거버넌스
│   └── monitoring/              시스템 모니터
│
├── _04_firmament_era/           창공(수증기 캐노피) 안정화 시대
│   ├── engine.py                run_firmament_era_step() — 궁창 1스텝 실행
│   └── __init__.py
│
├── _05_noah_flood/              노아 대홍수 상전이
│   ├── engine.py                run_noah_scenario() — 궁창 붕괴 → 홍수 → 전이
│   ├── scenarios.py             시나리오 비교 (충격 규모별)
│   └── __init__.py
│
├── _06_lucifer_impact/          루시퍼 충돌 (독립 레이어)
│   ├── impact_estimator.py      로컬 폴백 충돌 추정기
│   └── __init__.py              lucifer_strike() — 3-tier API
│
├── _07_polar_ice/               극지방 결빙 시뮬레이션 (단기)
│   ├── climate.py               AOD·태양 차단·수증기·온도 강제
│   ├── energy_balance.py        Budyko-Sellers 복사 수지
│   ├── stefan_ice.py            Stefan 결빙 성장 법칙
│   ├── simulation.py            implicit Euler 통합기
│   └── __init__.py
│
├── _08_ice_age/                 빙하시대 진입 시뮬레이션 (장기)
│   ├── ice_sheet.py             질량수지·기하학·해수면
│   ├── feedback.py              알베도 피드백·극 증폭·온도 결합
│   ├── simulation.py            explicit Euler 장기 통합기
│   ├── scenarios.py             4개 시나리오 비교 실행기
│   └── __init__.py
│
├── _meta/                       개념 맵·설계 문서·감사 보고서
├── pipeline.py                  서사 전체 파이프라인 실행기
└── verify_imports.py            import 검증
```

---

## 모듈 간 인터페이스 계약

각 레이어는 **명시적인 상태 벡터**를 주고받는다.

### _04 → _05: 창공 → 노아 홍수

```python
# FirmamentLayer.step() 출력
firmament_state = {
    "T_global_K":    float,   # 전지구 기온
    "instability":   float,   # 0.0 ~ 1.0 (≥0.85 → 붕괴 트리거)
    "H2O_canopy_kg": float,   # 수증기 캐노피 잔량
    "collapse_triggered": bool,
}
# → _05_noah_flood/engine.py 가 이 상태를 받아 FloodEngine 실행
```

### _05 → _06: 노아 홍수 → 루시퍼 충돌

```python
# FloodEngine.step() → FloodSnapshot
flood_snapshot = {
    "sea_level_anomaly_m": float,
    "T_global_K":          float,
    "impulse_shock":       float,   # 충돌 에너지 입력 (외부 주입 가능)
    "combined_impulse":    float,
}
# impulse_shock이 임계를 넘으면 _06_lucifer_impact 호출
```

### _06 → _07: 루시퍼 충돌 → 극지 결빙

```python
from L0_solar._06_lucifer_impact import lucifer_strike
ir, cr, ts = lucifer_strike(D_km=5.0, is_ocean=True, v_kms=25.0)

# 출력값이 _07의 초기 조건
from L0_solar._07_polar_ice import run_polar_simulation
p07 = run_polar_simulation(
    E_eff_MT           = ir.E_eff_MT,        # 충돌 에너지
    delta_H2O_kg       = ir.delta_H2O_canopy, # 수증기 주입
    delta_T_pole_K     = ir.delta_pole_eq_K,  # 극지 온도 충격
    T_pole_preimpact_K = 273.15,              # 창공 시대 극지 기온 (0°C)
)
```

### _07 → _08: 극지 결빙 → 빙하시대

```python
from L0_solar._08_ice_age import run_ice_age_simulation
p08 = run_ice_age_simulation(
    T_pole_init_K   = p07.steps[-1].T_pole_K,  # _07 최종 극지 기온 전달
    T_global_init_K = 285.0,                    # 에어로졸 소산 후 전지구 기온
    V_ice_init_km3  = 1e5,                      # 핵생성된 초기 대륙 빙상
    t_max_yr        = 100_000.0,
)
# 출력: 빙하선 60°N, 해수면 −125m (LGM 재현)
```

---

## 전체 파이프라인 실행

```python
# pipeline.py
from L0_solar._06_lucifer_impact import lucifer_strike
from L0_solar._07_polar_ice       import run_polar_simulation
from L0_solar._08_ice_age         import run_ice_age_simulation

# 1. 충돌
ir, cr, ts = lucifer_strike(D_km=5.0, is_ocean=True)

# 2. 극지 결빙 (단기 50년)
p07 = run_polar_simulation(
    E_eff_MT=ir.E_eff_MT, delta_H2O_kg=ir.delta_H2O_canopy,
    delta_T_pole_K=ir.delta_pole_eq_K, T_pole_preimpact_K=273.15,
    t_max_yr=50.0,
)

# 3. 빙하시대 (장기 100,000년)
p08 = run_ice_age_simulation(
    T_pole_init_K=p07.steps[-1].T_pole_K,
    T_global_init_K=285.0, V_ice_init_km3=1e5,
    t_max_yr=100_000.0,
)

print(f"빙하선: {p08.max_extent_lat:.1f}°N")
print(f"해수면: {p08.sea_level_min_m:.1f} m")
```

---

## 시뮬레이션 결과 요약

### 표준 시나리오 (루시퍼 E=2.2×10⁶ MT, 창공 붕괴 포함)

| 시각 | 이벤트 | 수치 결과 |
|---|---|---|
| t = 0 | 창공 시대 | T_pole = 0°C, 빙하 없음 |
| t = 0 + 충돌 1개월 | 첫 결빙 | T_pole = −8.5°C |
| t = 3년 | 극지 빙하 포화 | h_ice = 5m, 항구적 해빙 |
| t = 10,000yr | 빙상 성장 초기 | 빙하선 86°N, SL = −1.5m |
| t = 50,000yr | 빙하시대 중반 | 빙하선 65°N, SL = −86m |
| t = 100,000yr | LGM 도달 | 빙하선 60°N, SL = −125m |

### 시나리오 비교

| 시나리오 | 빙하선 | 해수면 | T_전지구 |
|---|---|---|---|
| S1 루시퍼 + 창공 붕괴 (기준선) | 60.5°N | −122 m | −0.5°C |
| S2 에덴 상태 (충돌 없음) | 89°N | 0 m | +23.8°C |
| S3 약한 충돌 (소행성급) | 52.4°N | −197 m | −5.9°C |
| S4 탈빙하기 (+19 W/m²) | 44.2°N | −163 m | −1.8°C |

> **탈빙하기 임계**: +27~30 W/m² — 이 이상에서만 빙하 완전 소멸.
> 이하에서는 빙상-알베도 양의 피드백이 이긴다 (Budyko Bistability).

---

## 다른 레이어와의 관계

```
L0_solar (서사)
    │
    ├─── 읽기 ───→ L1_dynamics    자전·조석·에너지 지형 장(field)
    │                              Phase_A: 회전장  Phase_B: 에너지 우물  Phase_C: 요동
    │
    ├─── 쓰기 ───→ L3_memory      서사 이벤트를 Hippo 우물로 각인
    │                              노아 홍수 impulse → well 생성
    │                              루시퍼 충돌 → well 강화
    │
    └─── 관찰됨 ─→ L4_analysis    서사 실행 결과를 6개 레이어로 측정
                                   궤적·물리량·통계역학·게이지·요동정리·기하위상
```

---

## 블록체인 (PHAM Chain) 서명

모든 모듈 파일은 `blockchain/pham_sign_v4.py`로 서명되어 **변조 추적**이 가능하다.

```bash
# 파일 서명 (CookiieBrain 루트에서)
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_07_polar_ice/simulation.py \
    --author "GNJz" --desc "극지 결빙 시뮬레이션 v2"

# 서명 검증
python3 pham_verify_chain.py pham_chain_simulation.json
```

체인 파일: `blockchain/pham_chain_<모듈명>.json`
각 블록: `{ sha256, author, timestamp, description, prev_hash }`

**서명된 핵심 모듈**:
`firmament`, `flood`, `exploration`, `consciousness`, `hades`,
`initial_conditions`, `cookiie_brain_engine`, ...
→ `blockchain/pham_chain_*.json` 목록 참조

---

## 물리 방정식 계층

| 레이어 | 사용 모델 | 주요 방정식 |
|---|---|---|
| `_04_firmament_era` | 온실 EBM | $T = T_{eq} \cdot (1 + \alpha_{H2O})$ |
| `_05_noah_flood` | 상전이 역학 | instability ≥ 0.85 → FloodEngine |
| `_06_lucifer_impact` | 충돌 스케일링 | $E = \frac{1}{2}mv^2$, AOD(E) |
| `_07_polar_ice` | Budyko-Sellers + Stefan | $dh/dt = k\Delta T / (\rho L h)$ |
| `_08_ice_age` | 빙상 EBM + 알베도 피드백 | $T = T_{ref} + S_{clim} \cdot \Delta Q$ |

---

## 확장 가능성

| 다음 단계 | 연결 지점 | 설명 |
|---|---|---|
| `_09_deglaciation` | `_08_ice_age` 출력 | 화산 CO₂ + 궤도 강제로 탈빙하기 |
| `_10_holocene` | `_09` 출력 | 현재 지구 상태 재현 (T=14.2°C) |
| Milankovitch 연동 | `_02_creation_days/day4` | 궤도 강제를 `_08_ice_age`에 직접 주입 |
| 대륙 이동 연동 | `_03_eden_os_underworld` | 판 구조론 상태가 빙상 분포에 영향 |
| 독립 엔진화 | `ENGINE_HUB/` | `_07_polar_ice`, `_08_ice_age`를 독립 패키지로 배포 |

---

## 관련 독립 엔진

```
ENGINE_HUB/
└── 00_PLANET_LAYER/
    └── Lucifer_Engine/    혜성 궤도·MOID·충돌 확률·피해 추정 완전 독립 패키지
        ├── lucifer_engine/
        ├── pyproject.toml
        └── README.md
```

설치: `pip install -e ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine`
→ 설치 시 `_06_lucifer_impact`가 full_pipeline 모드로 자동 업그레이드

---

## 참조

| 모듈 | 핵심 참조 |
|---|---|
| `_05_noah_flood` | FirmamentLayer (eden/firmament.py), FloodEngine (eden/flood.py) |
| `_06_lucifer_impact` | Holsapple (1993) 크레이터, Ward&Asphaug (2002) 쓰나미 |
| `_07_polar_ice` | Toon et al. (1997), Budyko (1969), Stefan (1891), Maykut (1986) |
| `_08_ice_age` | North (1981), Oerlemans (1981), CLIMAP (1981), IPCC AR6 |
