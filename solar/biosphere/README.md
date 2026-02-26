# solar/biosphere/ — 척박→선구→광합성→대기→호흡 식생 (Phase 7b)

**창 1:11** “땅은 풀과 씨 맺는 채소와 씨 가진 열매 맺는 나무를 내라”를  
**환경이 한 번에 준비되지 않고**, **척박 → 선구 생존 → 광합성 → 대기 변화 → 호흡 식물** 순서로 구현한다.

---

## 1. 단계 요약

| 단계 | 환경 | 생물 | 상태변수 |
|------|------|------|----------|
| 0 | 셋째날 직후, 척박 | 없음 | — |
| 1 | 선구 | 균사·이끼·지의류 (극소 조건 생존) | `pioneer_biomass`, `organic_layer` |
| 2 | 토양 준비됨 | 광합성 활성화 | `B_leaf`, `B_root`, `B_wood`, GPP/NPP |
| 3 | 대기 변화 | O₂↑, CO₂↓ | `AtmosphereComposition` 피드백 |
| 4 | O₂ 임계 이상 | 호흡형·나무·씨/열매 | `f_O2`로 wood/seed 비중 증가 |

---

## 2. 모듈

| 파일 | 역할 |
|------|------|
| `_constants.py` | 선구/광합성/O₂/알베도 상수 |
| `state.py` | `BiosphereState` (관측·연동용 스냅샷) |
| `pioneer.py` | 선구 NPP, organic_layer 축적/분해 |
| `photo.py` | f_I, f_C, f_T, f_O2, GPP, Resp, 증산, latent heat |
| `column.py` | `BiosphereColumn.step(env, dt)` → 피드백 dict |

---

## 3. 입출력 포트

**입력 (env dict)**: `F_solar_si`, `T_surface`, `P_surface`, `CO2`, `H2O`, `O2`, `water_phase`, (옵션) `soil_moisture`.

**출력 (step 반환)**: `delta_CO2`, `delta_O2`, `transpiration_kg_per_m2_yr`, `latent_heat_biosphere_W`, `delta_albedo_land`, `GPP`, `Resp`, `NPP`, `photo_active`.

---

## 4. 사용 예

```python
from solar.biosphere import BiosphereColumn

bio = BiosphereColumn(body_name="Earth", land_fraction=0.29)
env = {
    "F_solar_si": 1361.0,
    "T_surface": 288.0,
    "P_surface": 101e3,
    "CO2": 400e-6,
    "H2O": 0.01,
    "O2": 0.0,
    "water_phase": "liquid",
}
for _ in range(100):
    feedback = bio.step(env, 0.01)
    # feedback["delta_CO2"], feedback["delta_O2"] → atmosphere 조성 갱신
```

---

## 5. 상세 사양

[docs/BIOSPHERE_LAYER_SPEC.md](../../docs/BIOSPHERE_LAYER_SPEC.md)
