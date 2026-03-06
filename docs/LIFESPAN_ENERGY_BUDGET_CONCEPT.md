# 수명·에너지 총량 모델 — 개념 확인 및 레이어 배치

**목적**: 대홍수(궁창 붕괴) 이벤트 **전후** 시스템 파라미터 변화를 **에너지/엔트로피 동역학**으로 고정해, 수명·항상성·경고·FSM 전이가 모두 동역학으로 따라오게 한다.  
종교 해석이 아니라 **정의 → 수식(최소) → 이벤트 전/후 파라미터**로 고정.  
**동역학 수식 확정판**: `docs/ENERGY_ENTROPY_FIRMAMENT_SYSTEM.md` (E_cap, C(t), S(t), L_env, 3구간, 수렴, 다음 작업).

---

## 1. 텍스트 패턴 (관찰, 레퍼런스만)

- **창세기 5장**: 아담 계열 수명 대략 700~950년.
- **창세기 6:3**: “그들의 날은 120년이 되리라” — 인간 수명 상한 등장.
- **창세기 11장**: 홍수 이후 계보에서 수명 급감 (600 → 400 → 200 → 175 …).
- **두 흐름**: 창1 “남녀 창조·번성” 집단 vs 창2 아담 계열(에덴·계보). 텍스트 내부에 “두 종류의 인간 상태”가 있음.

**관찰 요약**: 같은 환경으로 읽히는 세계 안에서 **수명 비율이 최대 약 7.5배**(900 vs 120) 차이난다.

---

## 2. 에너지 총량 모델 (가설)

개체를 **총 에너지 예산**을 쓰는 시스템으로 본다.

- **E_total**: 개체가 평생 쓸 수 있는 총 예산 (상수 또는 초기 조건).
- **M(t)**: 유지비 (대사·항상성·수리).
- **R(t)**: 번식/생식 관련 비용 (이벤트 또는 활성도에 비례).
- **L(t)**: 추가 손실 (갈등·스트레스·환경·엔트로피 누수).

제약:

\[
E_{\mathrm{total}} = \int_0^T \bigl( M(t) + R(t) + L(t) \bigr) \, dt
\]

단순화 (평균 소모율):

\[
E_{\mathrm{total}} \approx T \cdot \overline{M+R+L}
\quad\Rightarrow\quad
T \approx \frac{E_{\mathrm{total}}}{\overline{M+R+L}}
\]

**두 집단 A(900년), B(120년)**  
같은 E_total 가정 시:

\[
\frac{T_A}{T_B} = \frac{\overline{M+R+L}_B}{\overline{M+R+L}_A} = \frac{900}{120} = 7.5
\]

즉: 120년 집단은 900년 집단보다 **평균 소모율이 7.5배 크다**고 두면 수치가 맞는다.

**R(t)를 “번식/성 관련 비용”으로 두는 경우**

- 이벤트 합: \(R(t) = \sum_k c_{\mathrm{rep}} \, \delta(t - t_k)\) → 빈도 ↑ ⇒ \(\overline{R}\) ↑ ⇒ T ↓.
- 연속형: \(R(t) = k_{\mathrm{rep}} \cdot a_{\mathrm{rep}}(t)\) (활성도 0~1).  
→ 텍스트의 “난교/무분별한 방출”은 **R 평균을 높이는 서사**로 읽을 수 있음 (해석).  
→ 코드에서는 **R에 기여하는 SCENARIO 변수**(예: `reproduction_activity`, `reproduction_event_count`)로만 넣으면 됨.

---

## 3. 레이어 배치 (엔진과 섞이지 않게)

| 내용 | 레이어 | 설명 |
|------|--------|------|
| E_total, M, R, L, 소모율 공식 | **SCENARIO** | 규칙·파라미터. CONFIG/데이터로 주입. 물리 코어를 바꾸지 않음. |
| “아담 계열”, “120년”, “번성·혼합” | **LORE** | 명명·서사·로그. 수치 계산에 직접 관여하지 않음. |
| 온도·CO2·중력·광도 | **PHYSICAL_FACT** | 기존 day1~7. 변경 없음. |
| 지하 경고 (Hades) | **UnderWorld** | 측정만. 이 모델의 “입력”으로 쓸 수 있음 (L에 기여 등). |

**수명 T 또는 “남은 예산”**  
→ SCENARIO 레이어에서 **파생량**으로 계산.  
→ 그 결과를 **지상 동역학(Homeostasis/IntegrityFSM)** 에 **넣을지만** 정하면 됨.

---

## 4. 지상 동역학과의 접점 (구현 위치)

현재 구조:

- **HomeostasisEngine**: `stress_index`, `integrity` 매 틱.  
  입력: world(eden_index), hades_signal(severity), stress_injection(선악과).
- **IntegrityFSM**: `integrity`와 θ1, θ2, N틱으로 IMMORTAL → DEGRADED → MORTAL 전이.

**수명 모델을 붙이는 방법 (선택지)**

1. **integrity 감쇠율에 반영**  
   - SCENARIO에서 `(M+R+L)_avg` 또는 `reproduction_activity`를 계산해,  
   - **integrity가 매 틱 줄어드는 속도**를 그에 비례하게 둠.  
   - R 높음 → 감쇠 빠름 → θ2 이하 도달 시간 단축 → “수명 짧음”으로 이어짐.

2. **별도 변수 `lifespan_remaining`**  
   - \(E_{\mathrm{remaining}}(t) = E_{\mathrm{total}} - \int_0^t (M+R+L)\,d\tau\).  
   - `lifespan_remaining <= 0` 이면 **강제 MORTAL 전이** 또는 **integrity = 0** 처리.  
   - FSM은 기존대로 integrity만 보거나, “수명 소진”을 별도 전이 조건으로 추가.

3. **stress_index에 R 기여분 추가**  
   - 현재: base_stress + hades_severity + stress_injection.  
   - 여기에 **SCENARIO에서 계산한 R_contribution**(번식 비용에 비례)을 더해 stress ↑ → integrity ↓.  
   - R 높은 “모드”일수록 같은 hades_signal에도 더 빨리 무너짐.

공통 원칙:

- **UnderWorld**: 그대로. Hades는 측정만.  
- **수명/에너지 공식**: 모두 SCENARIO(또는 eden_os 내부의 “에너지 예산” 전용 모듈)에서만 계산.  
- **물리 코어(day1~7)**: 건드리지 않음.

---

## 5. 요약 (개념 확인)

- **텍스트**: 900년 vs 120년, 두 인간 그룹, “120년 제한” 선언 → **수명 비율 7.5배**.
- **모델**: \(T = E_{\mathrm{total}} / \overline{M+R+L}\). R(번식 비용) ↑ ⇒ \(\overline{M+R+L}\) ↑ ⇒ T ↓.
- **레이어**: E_total, M, R, L, 수식 → **SCENARIO**. 명명·서사 → **LORE**. 물리·지하 → 기존 유지.
- **구현**: 수명/에너지 예산을 **SCENARIO 쪽 파생량**으로 두고, 그 결과만 **Homeostasis(integrity 감쇠 또는 stress 가산)** 또는 **IntegrityFSM 전이 조건**에 넣으면, 레이어가 섞이지 않는다.

다음 단계: SCENARIO용 CONFIG 스키마와, R(t) 또는 \(\overline{M+R+L}\) 을 계산하는 **한 개의 작은 모듈**(예: `lifespan_budget.py` 또는 `evolution_config` 확장) 설계 → 그 출력을 Homeostasis/FSM에 어떻게 넘길지 인터페이스만 정하면 된다.

---

## 6. 환경 상태(궁창)와 대홍수 빌드업

**전제**: 지금 엔진/시나리오가 다루는 지구 환경은 **대홍수 이벤트 이전(궁창 존재)** 이다.  
궁창이 사라지는 대격변 이후의 환경(극지 빙하, 빙하기, 현재 잔빙=남극·그린란드)은 **이벤트 이후** 타임라인으로 이어지므로, 에너지·수명 개념을 먼저 고정한 뒤 대홍수 빌드업을 해야 한다.

### 6.1 환경 상태 정의 (시스템 변수)

| 심볼 | 의미 | 코드 대응 |
|------|------|-----------|
| **env** | 환경 시대 | `FirmamentState.phase`: `antediluvian` \| `flood` \| `postdiluvian` |
| **firmament_active** | 궁창 존재 여부 | `FirmamentState.active` (True = 궁창 시대) |
| **H2O_canopy** | 상층 수증기 캐노피 비율 | `FirmamentState.H2O_canopy` (에덴 ≈ 0.05, 붕괴 후 = 0) |

- **궁창 시대 (antediluvian)**: `firmament_active=True`. UV 차폐·극적도 균온화·저 알베도·안개 강수. **유지비 M(t)가 낮은 환경**.
- **궁창 붕괴 후 (postdiluvian)**: `firmament_active=False`. UV 노출·극적도 온도차 확대·빙하 형성·강우. **유지비 M(t)가 높은 환경**.

### 6.2 유지비 M(t)를 환경에 연결

유지비를 환경 의존으로 분리:

\[
M(t) = M_{\mathrm{base}}(\mathrm{env}) + M_{\mathrm{other}}(t)
\]

- **M_base(env)**  
  - `env =` 궁창 시대: 낮음 (UV 차폐, 균온, 빙하 없음 → 수리·항상성 비용 낮음).  
  - `env =` 궁창 붕괴 후: 높음 (UV·기후 스트레스, 극한 기온 → 방어 비용 폭증).
- **M_other(t)**: 개체별·시대별 추가 유지(질병, 영양 등). SCENARIO에서 필요 시 추가.

**타임라인 의미**  
- 궁창 시대: 아담 계열 900년 vs 일반 120년 차이는 **R(t) 차이**(같은 M_base)로 설명.  
- 궁창 붕괴 직후: M_base가 한 번에 상승 → 아담 계열도 600→400→200→175년으로 **다운그레이드**.  
- 이후 "일반 인류"는 과학·의료로 M_other 또는 유효 M을 낮춰 평균 수명이 40→60→80년으로 **업그레이드**.  
- 현재: 두 곡선이 80~100년 근처에서 **수렴(동적 평형)** — 엔진에서 재현할 목표 패턴.

### 6.3 대홍수 이벤트 타임라인 (빌드업용)

엔진/서사 순서:

1. **궁창 시대 (현재 시뮬 환경)**  
   - `FirmamentLayer(phase='antediluvian')`, `EdenWorldEnv` = 궁창시대 스냅샷.  
   - 수명: E_total / (M+R+L). M = M_base(antediluvian). R만 그룹별로 다르게 두면 900 vs 120 비율 성립.

2. **대홍수 이벤트**  
   - `FirmamentLayer.trigger_flood()` → `FloodEvent` 발생.  
   - 궁창 H2O 전량 낙하, 해수면 상승, 알베도·UV·극적도 온도차 점프.  
   - `FloodEngine`으로 4단계 전이: rising → peak → receding → complete.

3. **궁창 붕괴 후**  
   - `phase='postdiluvian'`, `firmament_active=False`.  
   - M_base = M_base(postdiluvian) ↑ → 아담 계열 수명 급감.  
   - 극지 빙하 형성 → 빙하기 → 이후 빙하 후퇴 → **현재 잔빙 = 남극·그린란드** (LORE/지리 해석).

4. **현재 시대**  
   - 일반 인류: 의료·위생으로 유효 M 감소 → 평균 수명 70~80년.  
   - 아담 계열 계보는 이미 M_base 상승으로 하향 수렴.  
   - 두 그룹이 80~100년 구간에서 만나는 **수렴** 상태.

### 6.4 수식 정리 (빌드업용 고정)

- **총 예산**: \(E_{\mathrm{total}} = \int_0^T (M + R + L)\,dt\), \(T \approx E_{\mathrm{total}} / \overline{M+R+L}\).
- **유지비 분리**: \(M(t) = M_{\mathrm{base}}(\mathrm{env}) + M_{\mathrm{other}}(t)\).  
  - env = antediluvian ⇒ M_base 낮음.  
  - env = postdiluvian ⇒ M_base 높음 (궁창 붕괴의 지속 효과).
- **R(t)**: 번식/생식 비용. 궁창 시대에만 900 vs 120 차이를 만드는 주 변수.
- **120년 제한**: 궁창 시대 말 선언 — R이 큰 쪽에 대한 상한이자, 이후 시대에서는 M_base 상승으로 전체 수명이 더 낮아짐.

### 6.5 엔진과의 연결 (구현 시)

- **환경 상태**: `solar/eden/firmament.py` — `FirmamentLayer`, `FirmamentState`, `get_env_overrides()`.  
  `solar/eden/initial_conditions.py` — `antediluvian` / `postdiluvian` / `make_flood_peak()`.
- **대홍수 전이**: `solar/eden/flood.py` — `FloodEngine`, `FloodSnapshot`, `FLOOD_PHASES`.
- **수명/에너지**: SCENARIO 레이어에서 `env`(또는 `firmament_active`)를 읽어  
  `M_base(env)`를 결정하고, `T = E_total / (M+R+L)` 또는 integrity 감쇠율에 반영.

이렇게 **에너지 총량·M/R/L·환경(궁창) 개념을 고정**해 두면, 노아 등장과 궁창 소멸을 포함한 **대홍수 이벤트 빌드업**을 같은 수식·타임라인 위에서 이어갈 수 있다.
