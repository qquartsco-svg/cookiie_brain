# Joe_Engine 구현 물리 법칙 및 개념 명세

피드백을 반영하여, **현재 코드에 실제로 구현된** 물리 법칙과 개념만 구분해 정리한다.  
(설계 문서에만 있고 코드에 없는 것은 “미구현”으로 표시.)

---

## 0. 점검 대상 구분

| 구분 | 경로 | 역할 |
|------|------|------|
| **독립 엔진** | ENGINE_HUB/00_PLANET_LAYER/Joe_Engine (또는 standalone_build/Joe_Engine) | PANGEA §4 **Aggregator만** 포함. 물리량을 **직접 계산하지 않음**. |
| **본편 joe** | solar/_01_beginnings/joe | Feature Layer(물리→스냅샷) + 동일 Aggregator. **일부 물리 수식 구현.** |

아래는 두 곳을 구분해 “구현됨 / 미구현”을 명시한다.

---

## 1. 독립 엔진(ENGINE_HUB Joe_Engine)에 구현된 것

### 1.1 물리 “법칙”이 아닌 것 — 데이터 처리·계약

- **견고한 입력 처리**  
  `_get_float(snapshot, key, default=0.0)`: 키 없음·None·비숫자 → 에러 없이 `default`(또는 0.0) 반환.  
  → 물리 법칙이 아니라 **안전한 스냅샷 읽기 규칙**.

- **정규화·포화**  
  - `normalize(x, ref_min, ref_max)`: 선형 스케일 후 [0,1] 클램프.  
  - `saturate(x)`: max(0, min(1, x)).  
  → **물리 법칙이 아니라** 스트레스/불안정도를 [0,1] 구간으로 제한하는 **규격화**.

- **CONFIG 주입**  
  계수 a1~a5, b1~b3, p_ref, ref_min, ref_max를 `DEFAULT_CONFIG` dict로 두고, `assess_planet(..., config=...)`로 오버라이드.  
  → **재현 가능성·감사**를 위한 설계이며, 물리 법칙 자체는 아님.

### 1.1.1 좌표계·벡터 규약 (JOE/solar 공통)

- 벡터 공간은 **우주 공간**이므로 절대적인 위·아래는 없다.
- 이 프로젝트에서는 **관찰자 시점에서의 일관된 계산**을 위해 다음과 같이 규약한다.
  - **+z 축 = 남극 방향 (geomagnetic N극이 있는 쪽)**  
  - 자력선은 “남극(+z)에서 북극(–z)으로 떨어지는 폭포수”처럼 해석한다.
- `solar/day1/em/magnetosphere.py`, `solar/eden/firmament.py` 등
  자기권·궁창·세차 관련 모듈에서 사용하는 `spin_axis` / `magnetic_axis`
  벡터는 이 규약을 따른다.
- 이는 **사실 확정 하드코딩이 아니라 좌표계 선택**이며,
  전체 축을 회전해도 물리 법칙(뉴턴 역학·보존 법칙)은 변하지 않는다.

### 1.2 구현된 유일한 “수식” — PANGEA §4 (현상적 합성)

독립 엔진 안에서 **수식으로 구현된 것**은 아래 두 개뿐이다.

**(1) 행성 스트레스 (거시 압력 지표)**

```
planet_stress_raw = a1·σ_plate + a2·(P_w / p_ref) + a3·S_rot
                   + a4·(W_surface / W_total) + a5·dW_surface_dt_norm
```

- **σ_plate (sigma_plate)**: 판 구조/텍토닉 활성도 proxy. **엔진 내부에서 계산하지 않음.** 스냅샷에서 읽기만 함.
- **P_w**: 내부 유체 압력 proxy. **엔진 내부에서 계산하지 않음.** 스냅샷에서 읽고 `p_ref`로 나눔.
- **S_rot**: 자전 관련 무차원 지표. **엔진 내부에서 계산하지 않음.** 스냅샷에서 읽기만 함.  
  (문서상 정의: S_rot = clamp01((ω²R)/g) — 이 식은 **독립 엔진에는 없고**, solar/joe의 feature_layers에 있음.)
- **W_surface / W_total**: 표면 수량 비율. **엔진 내부에서 계산하지 않음.** 스냅샷에서 읽어 비율만 취함.
- **dW_surface_dt_norm**: 표면 수량 변화율 정규화값. **엔진 내부에서 계산하지 않음.** 스냅샷에서 읽기만 함.

→ 즉 **“5개 항의 가중 합”**만 구현되어 있고, 각 항의 **물리적 산출(중력, 탈출속도, 회전 안정 등)**은 이 패키지 밖(호출 측 또는 solar/joe Feature Layer)에서 이루어진다.

**(2) 불안정도 (시스템 붕괴 위험 proxy)**

```
instability_raw = b1·planet_stress + b2·(W_surface / W_total) + b3·dW_surface_dt_norm
```

- 스트레스가 높을수록, 표면 수량 비율·변화율이 특정 방향일수록 불안정도가 커지도록 하는 **경험적/현상적** 합성.
- **역학 방정식(뉴턴, 보존 법칙 등)**은 전혀 들어가지 않음.

**(3) habitability_label (거주가능성 라벨)**

- **물리 법칙이 아님.** stress·instability 구간에 따른 **분류 규칙**:
  - stress ≥ 0.7 또는 inst ≥ 0.7 → `"extreme"`
  - stress ≥ 0.4 또는 inst ≥ 0.4 → `"low"`
  - stress ≥ 0.2 또는 inst ≥ 0.2 → `"moderate"`
  - 그 외 → `"high"`

정리하면, **독립 Joe_Engine에는 “물리 법칙”이라 부를 만한 것은 PANGEA §4의 가중 합 두 개와, 정규화/포화/라벨 규칙뿐**이다.  
중력, 탈출속도, 회전 안정성, 복사 플럭스 등은 **구현되어 있지 않고**, 스냅샷에 이미 들어온 값을 **읽어서만** 쓴다.

---

## 2. 본편 solar/joe에만 구현된 물리 개념

아래는 **solar/_01_beginnings/joe**의 feature_layers(및 snapshot_convention)에 있는 것만 해당한다.  
독립 엔진에는 **없음**.

### 2.1 중력·질량·회전 (feature_layers.mass_rotation)

| 개념 | 수식 | 코드 위치 |
|------|------|-----------|
| **표면 중력** | g = G·M / R² | `g = G_SI * M / (R*R)` |
| **탈출 속도** | v_escape = √(2GM/R) | `v_escape = math.sqrt(2 * G_SI * M / R)` |
| **원심 가속도** | centrifugal = ω²·R | `centrifugal = omega*omega*R` |
| **회전 안정 조건** | ω²R < g 이면 구조적 붕괴 안 함 | `rotation_stable = centrifugal < g` |
| **S_rot 표준 정의** | S_rot = clamp01((ω²R)/g) | `S_rot_from_centrifugal_ratio(ratio)` (snapshot_convention) → mass_rotation.build()에서 사용 |

→ **뉴턴 역학(만유인력, 원심가속도)**과 **회전 안정성 조건**이 여기서만 구현됨.

### 2.2 우주 필드 (feature_layers.cosmic)

| 개념 | 수식 | 비고 |
|------|------|------|
| **항성 복사 플럭스** | F_star = L_star / (4πr²) | L_star, r_au 있으면 계산. |
| **생활권(HZ) proxy** | 500 ≤ F_star ≤ 2500 [W/m²] | in_habitable_zone 불리언. |

→ 독립 엔진에는 없음.

### 2.3 대기 유지·수권 (feature_layers.retention, water_plate_proxy)

- **atm_retention_score**: v_escape와 v_thermal proxy 비율로 대기 유지 가능성 [0,1].  
- **liquid_window_score**: T_surface(또는 T_eq)가 273~373 K 구간이면 액체물 유지 가능 proxy.

→ 독립 엔진에는 없음.

---

## 3. 개념 vs 구현 요약표

| 개념 | 독립 Joe_Engine | solar/joe (본편) |
|------|------------------|-------------------|
| PANGEA §4 가중 합 (stress_raw, instability_raw) | ✅ 구현 | ✅ 동일 사용 |
| 정규화·포화·habitability 라벨 | ✅ 구현 | ✅ 동일 |
| CONFIG 주입·config_used | ✅ 구현 | ✅ 동일 |
| g = GM/R² | ❌ 없음 (스냅샷 가정) | ✅ feature_layers |
| v_escape = √(2GM/R) | ❌ 없음 | ✅ feature_layers |
| S_rot = clamp01((ω²R)/g) | ❌ 없음 (S_rot는 스냅샷 입력) | ✅ snapshot_convention + mass_rotation |
| 회전 안정성 ω²R < g | ❌ 없음 | ✅ feature_layers (rotation_stable) |
| F_star = L/(4πr²), HZ | ❌ 없음 | ✅ feature_layers (cosmic) |
| 대기 유지·액체물 창 proxy | ❌ 없음 | ✅ feature_layers (retention, water_plate_proxy) |
| Forward/Inference(역추적) | ❌ 없음 | ✅ forward_inference.py (스텁/계약만) |

---

## 4. 한 줄 정리

- **독립 Joe_Engine**:  
  **“물리 법칙”은 PANGEA §4의 두 가중 합(stress_raw, instability_raw)과 정규화·라벨 규칙뿐**이다.  
  중력·탈출속도·회전·복사 등은 **전혀 계산하지 않고**, 스냅샷에 이미 들어온 **σ_plate, P_w, S_rot, W_surface, W_total, dW_surface_dt_norm**만 읽어서 합성한다.

- **solar/joe**:  
  그 위에 **Feature Layer**로 뉴턴 중력(g, v_escape), 회전 안정성(ω²R < g), S_rot 무차원 정의, 복사 플럭스(F_star), 대기·수권 proxy를 **구현**하고, 그 결과를 같은 PANGEA §4 Aggregator에 넘긴다.

이 명세는 **현재 코드에 실제로 존재하는 물리 법칙과 개념**만을 기준으로 한 것이다.
