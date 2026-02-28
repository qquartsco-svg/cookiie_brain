# 12 Well System — 독립 엔진 모음

> *"엘림에 이르니 거기에 물 샘 열둘과 종려나무 일흔 그루가 있는지라"*
> — 출애굽기 15:27

---

## 개념

12개의 우물(Well) = 12개의 완전 독립 엔진.

각 엔진은:
- **`solar/` 패키지 없이** 이 폴더만 복사해도 동작
- **stdlib + numpy 만** 의존 (외부 패키지 최소화)
- **단일 역할 완결** — 입력 포트 명확, 출력 단일
- **상용화 발매 가능** 수준의 독립 모듈

---

## 12개 엔진 목록

| 번호 | 폴더 | 엔진 | 역할 | 창세기 대응 |
|------|------|------|------|------------|
| 01 | `01_solar_well/` | SolarLuminosity | 태양 광도·복사 계산 | 빛이 있으라 (1:3) |
| 02 | `02_magno_well/` | Magnetosphere | 자기권 차폐 | 궁창이 있으라 (1:6) |
| 03 | `03_atmos_well/` | AtmosphereColumn | 대기 ODE 적분 | 궁창 아래의 물 (1:7) |
| 04 | `04_hydro_well/` | OceanNutrients | 조석·탄소 펌프 | 물이 한 곳으로 (1:9) |
| 05 | `05_litho_well/` | BiosphereColumn | 생물권 GPP·호흡 | 땅이 드러나라 (1:9) |
| 06 | `06_gaia_well/` | StressAccumulator | 항상성·스트레스 EMA | 각기 종류대로 (1:11) |
| 07 | `07_fire_well/` | FireEngine | O₂ 자기 조절·산불 | 연단하는 불 (말3:2) |
| 08 | `08_orbit_well/` | MilankovitchCycle | 장주기 궤도 리듬 | 해·달·별 (1:14) |
| 09 | `09_nutrient_well/` | NitrogenCycle | 질소 순환 ODE | 씨 맺는 채소 (1:11) |
| 10 | `10_net_well/` | SeedTransport | 보존형 확산 수송 | 새들이 날으라 (1:20) |
| 11 | `11_trophic_well/` | FoodWeb | 트로픽 ODE | 바다·하늘·땅 생물 (1:28) |
| 12 | `12_evos_well/` | MutationEngine | 진화 OS 변이 | 하나님의 형상 (1:27) |

---

## 구조

```
solar/engines/
├── __init__.py          ← solar 패키지용 통합 진입점 (re-export)
├── engines_demo.py      ← 12/12 smoke test
├── README.md            ← 이 파일
│
├── 01_solar_well/       ← 에너지 엔진 (독립 복사본)
│   ├── solar_engine.py
│   ├── _constants.py
│   └── README.md
├── 02_magno_well/       ← 보호막 엔진
│   ├── magno_engine.py
│   ├── magnetic_dipole.py
│   ├── solar_wind.py
│   ├── _constants.py
│   └── README.md
├── 03_atmos_well/       ← 호흡 엔진
│   ├── atmos_engine.py
│   ├── greenhouse.py
│   ├── water_cycle.py
│   ├── _constants.py
│   └── README.md
│   ... (04~12 동일 구조)
└── 12_evos_well/        ← 지능 엔진
    ├── evos_engine.py
    └── README.md
```

---

## 사용법

### solar 패키지 안에서 (통합 진입점)
```python
from solar.engines import (
    StressEngine, RhythmEngine, NitrogenEngine,
    OceanEngine, SeasonEngine, TransportEngine,
    FoodWebEngine, MutationEngine, FeedbackEngine,
    NicheEngine, AtmosphereEngine, BiosphereEngine,
)
```

### 완전 독립 실행 (폴더만 복사 후)
```python
import sys
sys.path.insert(0, './08_orbit_well')
from orbit_engine import MilankovitchCycle

mc  = MilankovitchCycle()
obl = mc.obliquity(t_yr=0.0)
print(f"경사각={obl:.2f}°")
```

### 전체 행성 통합 실행 (Day7 PlanetRunner)
```python
from solar.day7 import make_planet_runner, make_sabbath_judge

runner = make_planet_runner()   # 12엔진 × 12밴드
judge  = make_sabbath_judge()
snap   = runner.step(dt_yr=1.0)
print(snap.summary())
```

---

## 12라는 숫자

```
공간: 12개 위도 밴드   (LatitudeBands, 15° 간격)
기능: 12개 독립 엔진   (이 폴더)
자원: 12개 N_soil 밴드 (12우물)
시간: window=12 스텝   (SabbathJudge, 1사이클)
```

12 = 2×2×3 — 약수 6개 — **어느 방향으로 분할해도 나머지 없음.**
제대로 설계하면 12가 나온다. 이미 나왔다.

→ 자세한 분석: [`docs/WHY_12_SYSTEMIC.md`](../../docs/WHY_12_SYSTEMIC.md)
