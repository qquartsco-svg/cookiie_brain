# `_08_ice_age` — 빙하시대 진입 시뮬레이션

> L0_solar 서사 레이어 8번째 챕터

---

## 서사적 위치

```
창공 붕괴 (_04)
    └─ 노아 홍수 (_05)
           └─ 루시퍼 충돌 (_06)
                  └─ 극지방 첫 결빙 (_07)
                         └─ 대륙 빙상 성장 · 빙하시대 ← 여기 (_08)
```

루시퍼 충돌의 에어로졸 겨울이 걷힌 이후에도, 극지방에는 이미 _07에서 형성된
영구 해빙이 자리잡고 있다. 이 해빙의 높은 알베도는 지속적인 태양 반사를 일으켜
전지구 기온을 서서히 낮추고 — 빙상-알베도 양의 피드백이 시작된다.

수천 년이 지나면 북반구 대륙 위에 두꺼운 빙상이 쌓이고,
빙하선은 위도 60°N을 향해 전진하기 시작한다.
바닷물이 얼음으로 고정되면서 해수면은 수백 미터 낮아진다.

이것이 CookiieBrain 서사에서 말하는 **노아 이후 빙하시대** 의 물리적 기원이다.

---

## 물리 파이프라인

```
V_ice (빙상 부피)
    ↓
φ_ice (빙하선 위도)    ← volume_to_geometry()
    ↓
α_global (행성 알베도) ← global_albedo()
    ↓
ΔQ (복사 강제력)       ← radiative_forcing()
    ↓
T_global (전지구 기온) ← global_temperature()
    ↓
T_pole (극지 기온)     ← polar_temperature()  [PA=2.5]
    ↓
B_net (순 질량수지)    ← mass_balance()
    ↓
dV/dt = B_net × A      ← explicit Euler, dt=50 yr
```

---

## 파일 구성

| 파일 | 역할 | 핵심 함수 |
|---|---|---|
| `ice_sheet.py` | 빙상 기하 · 질량수지 · 해수면 | `mass_balance()`, `volume_to_geometry()`, `sea_level_change()` |
| `feedback.py` | 알베도 피드백 · 온도 결합 | `global_albedo()`, `global_temperature()`, `polar_temperature()` |
| `simulation.py` | 장기 시간 적분 | `run_ice_age_simulation()` |
| `__init__.py` | 패키지 진입점 | — |

---

## 물리 모델 상세

### 1. 빙상 질량수지

**강설 누적 (Accumulation)**

$$B_{acc}(T_{pole}) = B_{max} \cdot \exp\left(-\frac{(T_{pole} - T_{opt})^2}{2\sigma^2}\right)$$

- $T_{opt} = -15°C$: 수분 수송과 저온의 균형점
- $\sigma = 15K$: 너무 춥거나 따뜻하면 강설 감소
- $B_{max} = 0.5\ m/yr$

**융빙 제거 (Ablation)**

$$B_{abl}(T_{margin}) = k_{abl} \cdot \max(0,\ T_{margin})$$

$$T_{margin}(\phi_{ice}) = T_{pole} + (T_{eq} - T_{pole}) \cdot (1 - (\phi_{ice}/90°)^{0.8})$$

- 빙하선 위도의 기온이 0°C 이상이면 융빙 시작
- $k_{abl} = 1.5\ m/yr/°C$ (PDD 근사)

**부피 변화**

$$\frac{dV}{dt} = B_{net} \cdot A \quad [km^3/yr]$$

### 2. 빙상 기하 (Volume-Area 관계)

평균 두께 $h_{mean} = 1.5\ km$ (LGM 보정):

$$A = V / h_{mean} \quad [km^2]$$

구면 적(球面積)으로 빙하선 위도 변환:

$$\sin\phi_{ice} = 1 - \frac{A}{2\pi R_\oplus^2}$$

### 3. 빙상-알베도 피드백 (Budyko-Sellers)

$$\alpha_{global} = \alpha_{ice} \cdot f_{ice} + \alpha_0 \cdot (1 - f_{ice})$$

$$f_{ice} = 1 - \sin\phi_{ice} \quad \text{(반구 빙상 면적 비율)}$$

$$\Delta Q = -\frac{S_0}{4} \cdot (\alpha_{global} - \alpha_0) \quad [W/m^2]$$

| 파라미터 | 값 | 설명 |
|---|---|---|
| $\alpha_{ice}$ | 0.65 | 대륙 빙상 알베도 |
| $\alpha_0$ | 0.30 | 기준 전지구 알베도 |
| $S_0$ | 1361 W/m² | 태양 상수 |

### 4. 전지구 기온 응답

$$T_{global} = T_{ref} + S_{clim} \cdot (\Delta Q + Q_{CO_2})$$

$$T_{pole} = T_{pole,0} + PA \cdot (T_{global} - T_{global,0})$$

- $S_{clim} = 0.8\ K/(W/m^2)$ (ECS = 3K / 3.7 W/m²)
- $PA = 2.5$ (극 증폭 계수, 관측 기반)

### 5. 해수면 변화

$$\Delta SL = -\frac{(V - V_0) \cdot \rho_{ice}}{\rho_{water} \cdot A_{ocean}}$$

LGM 검증: $V = 5 \times 10^7\ km^3 \Rightarrow \Delta SL \approx -120\ m$ ✓

### 6. 스노우볼 임계 (Budyko Criterion)

빙하선 $\phi_{ice} \leq 30°N$ 도달 시 알베도 런어웨이 시작.
양의 피드백이 음의 피드백(수분 감소)을 초과 → 전지구 결빙 가능.

---

## 시뮬레이션 파라미터

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `T_pole_init_K` | 243.15 K | _07 결빙 후 극지 기온 (-30°C) |
| `T_global_init_K` | 285.0 K | 충돌 후 전지구 기온 (12°C) |
| `V_ice_init_km3` | 1e5 km³ | 초기 대륙 빙상 부피 |
| `t_max_yr` | 50,000 yr | 시뮬레이션 기간 |
| `dt_yr` | 50 yr | 시간 간격 |
| `climate_sensitivity` | 0.8 K/(W/m²) | 기후 감도 |
| `co2_forcing_W_m2` | 0.0 | 장기 온난화 강제 (탈빙하기용) |

---

## 예상 결과 (기본값 기준)

| 시각 | 빙상 부피 | 빙하선 | 해수면 |
|---|---|---|---|
| 0 yr | 1×10⁵ km³ | ~89°N | 0 m |
| 3,500 yr | 2×10⁵ km³ | ~88°N | −0.5 m |
| 10,000 yr | ~5×10⁶ km³ | ~80°N | −13 m |
| 20,000 yr | ~2×10⁷ km³ | ~70°N | −50 m |
| 40,000 yr | ~5×10⁷ km³ | ~60°N | −120 m |

**성장 시간 스케일:** $V$ 두 배 ≈ 3,500 yr
(지수 성장 초기 → LGM 수준 도달 ≈ 20,000~40,000 yr)

---

## _07 → _08 연결

```python
from L0_solar._07_polar_ice import run_polar_simulation
from L0_solar._08_ice_age   import run_ice_age_simulation

# Step 1: 극지방 첫 결빙 (_07, 단기 50년)
p07 = run_polar_simulation(
    E_eff_MT           = 2.2e6,
    delta_T_pole_K     = -7.03,
    T_pole_preimpact_K = 273.15,
    t_max_yr           = 50.0,
)

# Step 2: 대륙 빙상 성장 → 빙하시대 (_08, 장기 50,000년)
p08 = run_ice_age_simulation(
    T_pole_init_K   = p07.steps[-1].T_pole_K,   # _07 최종 극지 기온 전달
    T_global_init_K = 285.0,                     # 에어로졸 제거 후 전지구 기온
    V_ice_init_km3  = 1e5,                       # _07 결빙 → 핵생성 초기 빙상
    t_max_yr        = 50_000.0,
)
print(p08.summary())
```

---

## 한계 및 주의

1. **계절성 없음**: 연평균 EBM. 실제 빙상은 여름 융빙이 중요한데 미반영.
2. **경도 없음**: 북아메리카 / 유라시아 빙상 분리 불가, 단일 반구 평균.
3. **빙상 유동 없음**: 빙하 흐름(ice flow)과 기저 마찰 미반영.
4. **해양 순환 없음**: AMOC 붕괴/약화가 빙상 성장에 미치는 영향 미반영.
5. **궤도 강제 없음**: 밀란코비치 주기 미포함 (co2_forcing_W_m2로 대체 가능).

> **결론**: 이 모델은 Lucifer impact → 극지 결빙 → 빙하시대 진입까지의
> 동역학 가설을 실험하는 **EBM 수준 research prototype** 이다.

---

## 참조

- Budyko (1969), Tellus — 에너지 수지 기후 모델
- North (1981), J. Atmos. Sci. — 1D EBM 정식화
- Oerlemans (1981), Nature — 북반구 빙하화 시뮬레이션
- Bahr et al. (1997), J. Geophys. Res. — 빙상 부피-면적 스케일링
- CLIMAP (1981) — LGM 빙상 재구성
