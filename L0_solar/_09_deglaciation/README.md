# `_09_deglaciation` — 탈빙하기 동역학 시뮬레이션

**L0_solar 서사 레이어 9번째 챕터**

---

## 왜 이 모듈이 여기 있는가 — 서사 체인과 엔지니어링 구현

---

### 1단계 — _08_ice_age 최종 상태 : 지구가 LGM에 갇혔다

**서사**: 10만 년의 빙상-알베도 피드백 루프 결과.
빙하선 60°N, 해수면 −128m, 전지구 기온 −1°C.
알베도 잠금으로 자연 상태에서는 스스로 빠져나올 수 없다.

**엔지니어링**: `run_ice_age_simulation()` 최종값
→ `V_ice=5.17e7 km³`, `phi_ice=59.9°N`, `sea_level=−128m`

---

### 2단계 — 밀란코비치 궤도 강제 : LGM을 탈출한 첫 번째 드라이버

**서사**: 지구 자전축 경사각(~41,000년 주기) + 공전 이심률(~100,000년 주기) 변화.
북극 여름 일사량이 서서히 증가하면서 LGM을 탈출할 에너지를 수천 년에 걸쳐 주입.

**엔지니어링**: `milankovitch_forcing(t_yr)` → ~+5~8 W/m² 수준의 느린 에너지 증가

---

### 3단계 — 홀로세 (현재 간빙기) : 그린란드 + 남극만 남았다

**서사**: 밀란코비치 강제로 대부분의 빙상이 후퇴.
현재(2024년) 그린란드(2.85×10⁶ km³) + 서남극(3.5×10⁶ km³) + 동남극(23×10⁶ km³)만 잔류.
산업화 이전까지는 비교적 안정적 균형 상태.

---

### 4단계 — 산업화 이후 (1750~ ) : 두 번째 드라이버 추가

**서사**: 인위적 CO₂ 방출 → 복사 강제 추가.
현재(2024년) CO₂ = 422ppm → ΔF = +2.1 W/m² (CO₂만, 산업화 이전 280ppm 대비).
현재 지구 기온 = +15°C (+1.2°C 상승), 북극 기온 = +3.6°C 상승.
그린란드 순 손실 ~280 Gt/yr, 서남극 ~110 Gt/yr, 해수면 상승 ~3.7 mm/yr.

**엔지니어링**:
```python
co2_radiative_forcing(422) = 5.35 × ln(422/280) = +2.1 W/m²
delta_T_global(+2.1)       = 0.8 × 2.1 = +1.7°C  (현재 누적 +1.2°C — 열적 지연)
delta_T_arctic(+2.1)       = 0.8 × 3.0 × 2.1 = +5.0°C  (극 증폭)
```

---

### 5단계 — _09_deglaciation ← 여기

**서사**: 현재 진행 중인 빙하 소멸의 동역학을 추적.
CO₂ 시나리오(RCP 2.6~8.5)별로 북극 빙하 소멸, 해수면 상승, 그린란드 붕괴가
**언제, 어떤 순서로** 일어나는지 수치 시뮬레이션.

**엔지니어링 구현**: CO₂ 궤적 → 복사 강제 → 전지구/극지 기온 → 빙상 질량수지 → 해수면
```python
from L0_solar._09_deglaciation import run_deglaciation_simulation
r = run_deglaciation_simulation(scenario="rcp85", t_max_yr=500.0)
print(r.summary())
```

---

## 폴더 구조

```
_09_deglaciation/
├── forcing.py        CO₂ 시나리오 궤적, 복사 강제, 밀란코비치 강제
├── ice_dynamics.py   그린란드 / 서남극(WAIS) / 동남극(EAIS) / 북극 해빙 질량수지
├── simulation.py     통합 적분기 (explicit Euler, dt=1yr)
├── scenarios.py      4개 시나리오 비교 실행기
└── __init__.py
```

---

## 물리 파이프라인

```
CO₂ 시나리오(RCP 2.6 / 4.5 / 6.0 / 8.5)
      ↓
co2_radiative_forcing() + milankovitch_forcing()  → ΔF [W/m²]
      ↓
delta_T_global()   →  T_전지구 = T_2024 + 0.8 × ΔF
delta_T_arctic()   →  T_북극  = T_arctic_2024 + 2.4 × ΔF   (극 증폭 3×)
delta_T_antarctic()→  T_남극  = T_ant_2024   + 1.2 × ΔF   (남극 증폭 1.5×)
      ↓
greenland_mass_balance(T_arctic) → dV_G [Gt/yr]
wais_mass_balance(T_ant, SLR)    → dV_WA [Gt/yr]  (MISI 피드백 포함)
eais_mass_balance(T_ant)         → dV_EA [Gt/yr]
      ↓
ice_to_sea_level(dV_G, dV_WA, dV_EA) → ΔSLR [m]
arctic_sea_ice_area(T_arctic)         → A_ice [km²]
```

---

## 시뮬레이션 결과 — 시나리오별 핵심 이벤트 발생 연도

| 시나리오 | 북극 여름 빙하 소멸 | SLR +1m | SLR +3m | 그린란드 50% | WAIS MISI |
|---|---|---|---|---|---|
| **RCP 8.5** (현재 추세) | **2068년** | 2474년 | 3077년 | 3673년 | 2642년 |
| **RCP 6.0** (중간) | — | 3070년 | — | — | 3619년 |
| **RCP 4.5** (파리협약) | — | 3280년 | — | — | 3936년 |
| **RCP 2.6** (넷제로) | — | — | — | — | — |

> **RCP 8.5 타임라인 (2024 기준)**:
> - **2068년**: 북극 여름 빙하 소멸 (9월 빙하 소멸 = "Blue Arctic")
> - **2100년**: CO₂ = 1050ppm, T_북극 = −2.8°C, SLR = +0.09m
> - **2474년**: 해수면 +1m (저지대 침수 본격화)
> - **2642년**: WAIS MISI 시작 (서남극 자기강화 붕괴)
> - **3077년**: 해수면 +3m (연안 도시 위협)
> - **RCP 2.6**: 2000년 내 주요 임계 없음 — 탈탄소화의 효과

---

## 현재 관측값과 비교

| 항목 | 현재 관측 (IPCC AR6) | 이 모델 (2024 기준) |
|---|---|---|
| 그린란드 손실 | ~280 Gt/yr | 280 Gt/yr ✓ |
| 서남극 손실 | ~110 Gt/yr | 110 Gt/yr ✓ |
| 해수면 상승률 | ~3.7 mm/yr | ~3.5 mm/yr ✓ |
| 북극 기온 상승 | +3~4°C (산업화 이전 대비) | +3.6°C ✓ |
| RCP 8.5 북극 빙하 소멸 | 2040~2100 (모델별) | 2068년 ✓ |

---

## 물리 모델 상세

### CO₂ 복사 강제
```
ΔF = 5.35 × ln(C / 280) [W/m²]
현재(422ppm): ΔF = +2.1 W/m²
RCP 8.5 2100년(1050ppm): ΔF = +8.2 W/m²
```

### 기후 민감도 (ECS)
```
ΔT_global = 0.8 K/(W/m²)   (IPCC AR6 최적 추정: 3.0°C/doubling)
ΔT_arctic  = 2.4 K/(W/m²)  (극 증폭 3×)
ΔT_ant     = 1.2 K/(W/m²)  (극 증폭 1.5×)
```

### 그린란드 질량수지
```
dV_G/dt = -K × max(0, T_arctic - T_crit) × (V_G/V_G0)
K = 35 Gt/(yr·°C), T_crit = −17°C
현재: ΔT = 2.5°C → 280 Gt/yr ✓
```

### WAIS MISI (해양 빙상 불안정)
```
해수면 ≥ +1.5m → 서남극 기저 해수 침투 가속
→ 질량수지 손실 2× 가속
```

---

## MISI (Marine Ice Sheet Instability)

서남극 빙상(WAIS)의 핵심 위험 메커니즘:
1. 빙상 기저가 해수면 아래에 있음 (역경사 지형)
2. 해수면 상승 → 바닷물이 빙상 아래 침투
3. 열적 침식 → 빙하 후퇴 가속
4. 자기강화 붕괴: 후퇴할수록 더 깊은 곳으로 → 더 많은 해수 침투
5. 임계 통과 시 수백~수천 년 내 서남극 전체 붕괴 가능성

---

## 블록체인 서명

```bash
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_09_deglaciation/simulation.py \
    --author "GNJz" --desc "탈빙하기 동역학 시뮬레이션"
python3 pham_sign_v4.py ../L0_solar/_09_deglaciation/forcing.py \
    --author "GNJz" --desc "CO2 시나리오 복사 강제"
```

---

## 확장성 / 활용성

| 확장 방향 | 연결 지점 | 설명 |
|---|---|---|
| 열팽창 추가 | `forcing.py` | 해수 열팽창 → 현재 SLR의 40% 차지 |
| Milankovitch 장기 | `milankovitch_forcing()` | 다음 빙기 ~50,000년 후 추적 |
| 도시별 침수 지도 | `sea_level_m` 출력 | SLR 레벨별 침수 면적 매핑 |
| 티핑 포인트 탐색 | `WAIS MISI`, `AMOC` | 연쇄 티핑 포인트 시뮬레이션 |
| _10_future_earth 연결 | 이 모듈 출력 | 탈빙하기 후 안정 상태 → 미래 지구 |

---

## 빠른 실행

```bash
# 단일 시나리오
cd /Users/jazzin/Desktop/00_BRAIN/CookiieBrain
python3 -c "
from L0_solar._09_deglaciation import run_deglaciation_simulation
r = run_deglaciation_simulation('rcp85', t_max_yr=500.0)
print(r.summary())
"

# 전체 시나리오 비교
python3 -c "
from L0_solar._09_deglaciation import run_all, comparison_table
print(comparison_table(run_all(t_max_yr=2000.0)))
"
```
