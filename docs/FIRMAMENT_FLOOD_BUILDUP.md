# 궁창·대홍수 빌드업 — 개념·타임라인·엔진 연결

**목적**: 에너지 총량·수명 개념을 고정한 뒤, **노아 등장 → 궁창 소멸(대홍수)** 이벤트를 설계·구현할 때 쓰는 빌드업 명세.  
레이어 분리(PHYSICAL_FACT / SCENARIO / LORE) 유지.

---

## 1. 전제 (환경 셋팅)

- **현재 엔진이 가정하는 지구 환경** = **대홍수 이전(궁창 존재)**.
- 궁창이 사라진 **이후**의 세계: 극지 빙하 형성 → 빙하기 → 빙하 후퇴 → **오늘날 잔빙 = 남극·그린란드**.
- 따라서 "지금" 시뮬레이션 상태는 **궁창 시대**이고, 대홍수 이벤트는 이 환경이 **한 번에 전환**되는 지점이다.

---

## 2. 개념·수식 고정 (빌드업 전 확정)

자세한 유도는 **docs/LIFESPAN_ENERGY_BUDGET_CONCEPT.md** 참조. 여기서는 빌드업에 필요한 것만 정리.

| 심볼 | 의미 |
|------|------|
| **E_total** | 개체 평생 에너지 예산 (상수 또는 초기값) |
| **M(t)** | 유지비 (대사·항상성·환경 방어). **환경(궁창 유무)에 의존** |
| **R(t)** | 번식/생식 비용 |
| **L(t)** | 추가 손실 (갈등·스트레스·엔트로피) |
| **T** | 수명. \(T \approx E_{\mathrm{total}} / \overline{M+R+L}\) |

**유지비를 환경으로 분리:**

\[
M(t) = M_{\mathrm{base}}(\mathrm{env}) + M_{\mathrm{other}}(t)
\]

- **궁창 시대 (antediluvian)**: M_base 낮음 → 아담 계열 900년, 일반 120년 차이는 **R만**으로 설명.
- **궁창 붕괴 후 (postdiluvian)**: M_base 폭등 → 아담 계열도 600→400→200→175년으로 다운그레이드.
- **현대**: 일반 인류는 과학·의료로 유효 M 감소 → 80~100년에서 두 그룹 **수렴**.

---

## 3. 타임라인 (이벤트 빌드업 순서)

1. **궁창 시대**  
   - `FirmamentLayer(phase='antediluvian')`, `EdenWorldEnv` = 궁창시대 스냅샷.  
   - 수명 = E_total / (M+R+L), M = M_base(antediluvian).

2. **대홍수 발동**  
   - `FirmamentLayer.trigger_flood()` → `FloodEvent`.  
   - 궁창 H2O 낙하, 해수면 상승, UV·알베도·극적도 온도차 점프.

3. **홍수 전이**  
   - `FloodEngine`: rising → peak → receding → complete.  
   - `phase` → `postdiluvian`, `firmament_active=False`.

4. **궁창 붕괴 후**  
   - M_base(postdiluvian) 적용 → 수명 급감.  
   - 극지 빙하 → 빙하기 → 후퇴 → 현재 잔빙(남극·그린란드) — LORE/지리 해석.

---

## 4. 엔진 연결 (코드 위치)

| 역할 | 위치 |
|------|------|
| 환경 상태(궁창 유무) | `solar/eden/firmament.py` — `FirmamentLayer`, `FirmamentState`, `get_env_overrides()` |
| 시대별 초기조건 | `solar/eden/initial_conditions.py` — `make_antediluvian()`, `make_postdiluvian()`, `make_flood_peak()` |
| 대홍수 전이 곡선 | `solar/eden/flood.py` — `FloodEngine`, `FloodSnapshot`, `FLOOD_PHASES` |
| 수명/에너지 공식 | SCENARIO — `env`/`firmament_active`로 M_base(env) 결정 후 T 또는 integrity 감쇠에 반영 |
| **S(t), env_load** | **UnderWorld** | `HadesObserver.listen(..., layer0_snapshot=...)` 로 Layer0에서 주입. `DeepSnapshot.shield_strength`, `.env_load`. 없으면 None → 경고 없음. |

---

## 5. 노아·대홍수 이벤트 설계 시 체크리스트

- [ ] E_total, M_base(env), R, L, T 수식이 **LIFESPAN_ENERGY_BUDGET_CONCEPT.md**와 일치하는지 확인.
- [ ] "현재 시뮬 = 궁창 시대"가 `EdenWorldEnv`/`FirmamentLayer` 기본값으로 반영되는지 확인.
- [ ] `trigger_flood()` 시점에 M_base(env)가 antediluvian → postdiluvian으로 전환되도록 SCENARIO/Homeostasis 쪽에 연결.
- [ ] 궁창 붕괴 이후 타임라인(빙하기, 잔빙)은 LORE/서사로만 다루고, 물리 코어(day1~7)는 변경하지 않음.

**Layer0 → Hades 연결 (구현됨)**  
Eden/Runner에서 `layer0_snapshot` 객체를 만들어 `hades.listen(tick, ..., layer0_snapshot=snap)` 에 넘긴다.  
`snap` 은 `shield_strength` (S(t) ∈ [0,1], 예: 궁창 활성 시 1, H2O_canopy 비율로 스케일), `env_load` (L_env(t), 선택) 속성을 가지면 된다 (덕 타이핑).  
S(t) < 0.5 이면 Hades가 `ENTROPY_WARNING` "궁창/보호막 약화" 를 낸다. `docs/ENERGY_ENTROPY_FIRMAMENT_SYSTEM.md` 참조.
