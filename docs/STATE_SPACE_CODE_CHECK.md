# 상태공간 — 코드 기준 점검

**목적**: "상태 공간이 분리되었는가?"를 **실제 코드**에서 어디에 상태가 살아 있고, 누가 갱신하며, 어디서 합쳐지는지로 정리.

---

## 1. 결론 (한 줄)

**예. 레이어별로 상태 소유권이 나뉘어 있고, 서로의 상태를 직접 덮어쓰지 않는다.**  
통합 노출은 `brain_core_bridge`가 **읽기·집계**만 할 뿐, 별도 상태를 소유하지 않는다.

---

## 2. 상태가 "살아 있는" 코드 위치

### 2.1 코어 (행성 궤도·스핀·표면 해양)

| 파일 | 소유 객체 | 상태 변수 | 갱신 위치 |
|------|-----------|-----------|-----------|
| **solar/core/evolution_engine.py** | `Body3D` (engine.bodies[i]) | `pos`, `vel`, `spin_axis`, `obliquity`, `spin_rate`, `J2`, `radius` | `engine.step(dt)` 내부 배열 `_pos`, `_vel` 동기화 + `_precess()` |
| **solar/core/evolution_engine.py** | `SurfaceOcean` (engine.oceans[name]) | `depths`, `current_vel`, `vorticity`, `tidal_stretch` | `engine._ocean(dt)` → `ocean.update(...)` |

- **진짜 저장소**: `engine.bodies[i].pos` 등과 `engine._pos`, `engine._vel` (내부 배열이 body에 다시 쓰임).
- **의존**: core는 **다른 레이어를 import 하지 않음.** 상태는 core 안에만 있음.

### 2.2 대기 (열·압력·조성)

| 파일 | 소유 객체 | 상태 변수 | 갱신 위치 |
|------|-----------|-----------|-----------|
| **solar/atmosphere/column.py** | `AtmosphereColumn` | `self.T_surface`, `self.composition` (CO2, H2O, CH4 등) | `atm.step(F_si, dt)` |

- **읽는 것**: `F_si`(em에서 r로 계산), `albedo`(생성 시 인자 — surface에서 넘긴 값).
- **쓰는 것**: core/ surface를 **수정하지 않음.** atmosphere 인스턴스 자신만 갱신.

### 2.3 표면 (땅·바다) — "상태"가 아님

| 파일 | 객체 | 역할 |
|------|------|------|
| **solar/surface/surface_schema.py** | `SurfaceSchema` | `land_fraction`, `albedo_land`, `albedo_ocean` — **파라미터** (입력 설정값). |
| | `effective_albedo()` | 위 파라미터로 **한 개 숫자** \(A_{\mathrm{eff}}\) 반환. |

- **진화하는 상태 없음.** ODE로 적분되는 변수가 아니라, 경계조건용 상수/파라미터 → 하나의 알베도 값.
- 따라서 "상태공간 분리"에서 surface는 **경계조건 레이어**로만 쓰이고, **상태 소유권**은 core / atmosphere 쪽에만 있다고 보면 됨.

### 2.4 전자기 (em) — 관측/파생만

| 파일 | 역할 |
|------|------|
| **solar/em/** | `F(r)`, `B(x)`, `P_sw`, `r_mp` 등 — **core의 pos, spin_axis를 읽어** 계산한 결과. |

- em은 **자체적으로 적분되는 상태를 두지 않음.** core 상태 + 시간을 넣으면 출력이 정해지는 **관측 레이어**.

### 2.5 통합 노출 (bridge)

| 파일 | 동작 |
|------|------|
| **solar/brain_core_bridge.py** | `get_solar_environment_extension(engine, sun, atmospheres, dt_yr)` |

- `engine.step(dt_yr)` 호출 → **core 상태만** 갱신.
- `atm.step(F_si, dt_yr)`, `atm.state(F_si)` 호출 → **atmosphere 상태만** 갱신.
- `body.pos`, `st.T_surface`, `st.P_surface` 등을 **읽어서** dict로 만든 뒤 반환.
- **bridge는 새 상태를 소유하지 않음.** 조회·집계만 함.

---

## 3. 분리 여부 요약

| 레이어 | 상태 소유 | 다른 레이어 상태 직접 수정 여부 |
|--------|-----------|----------------------------------|
| **core** | bodies[].pos, vel, spin_axis; oceans[].depths, vorticity | 없음 |
| **atmosphere** | T_surface, composition | 없음 |
| **surface** | 없음 (파라미터 → A_eff) | 없음 |
| **em** | 없음 (관측만) | 없음 |
| **brain_core_bridge** | 없음 (반환용 dict만 생성) | 없음 |

- **데이터 흐름**: surface → atmosphere (albedo 숫자만 생성 시 전달). core → em, core → atmosphere (r, pos 등 읽기).  
- **상태가 “섞이는” 곳은 없다.**  
  atmosphere의 `T_surface`와 core의 `depths`는 서로 다른 객체에 있고, bridge가 둘 다 **읽기만** 해서 한 dict로 넘겨줄 뿐이다.

---

## 4. 현재 코드 상태 (스냅샷)

- **core**: `evolution_engine.py` — Body3D, SurfaceOcean, EvolutionEngine. `step(dt)`로 pos/vel/spin_axis/depths/vorticity 갱신.
- **atmosphere**: `column.py` — AtmosphereColumn. `step(F, dt)`로 T_surface, composition.H2O 갱신.
- **surface**: `surface_schema.py` — SurfaceSchema, effective_albedo(). 갱신 로직 없음.
- **bridge**: `brain_core_bridge.py` — engine + atmospheres 읽어서 extension dict 반환.  
  참고: `engine.step(dt_yr)`가 **두 번** 호출되는 부분이 있음 (44행, 46행) — 시간이 두 배로 진행될 수 있는 버그 후보.

---

## 5. 정리

- **상태공간은 레이어별로 분리되어 있다.**  
  core / atmosphere만 진짜 “상태”를 갖고, surface/em은 파라미터·관측, bridge는 집계만 한다.
- **어떤 코드 상태인지** 확인할 때는 위 2절의 **파일·객체·변수·갱신 위치** 표를 보면 된다.
