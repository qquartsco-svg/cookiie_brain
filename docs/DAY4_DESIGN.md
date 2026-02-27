# 넷째날 설계 문서 — 순환하는 행성 항상성

**설계 철학**: "초기 조건만 주면 스스로 순환한다"

---

## 셋째날 → 넷째날 전환점

셋째날이 만든 것:
```
돌땅 → 토양 → 식물 생애주기 → 탄소 순환 → 산불 항상성 → 뉴런-행성 연결
```

셋째날의 한계:
```
루프들이 존재하지만 장주기 순환(kyr~Myr)이 아직 없다.
세차, 토양, 질소, 중력 → 이것들이 수천~수만 년 주기를 만든다.
```

넷째날이 할 일:
```
기존 루프들을 장주기 드라이버(세차·조석·질소)와 연결
→ 짧은 주기(yr) + 긴 주기(kyr) 가 중첩된 진짜 항상성 구현
```

---

## 넷째날 순환 3개

### 순환 1 — 질소 루프 (nitrogen/)
```
개념: N₂ ↔ 고정 질소(NH₃, NO₃) ↔ 단백질 ↔ 사체 분해 ↔ N₂

수식:
  N_fix(t) = K_fix × B_pioneer × f_O2_n(O2) × f_T × f_W
  N_denitrify = K_denit × N_soil × (1 - f_O2)   # 혐기성 조건
  N_uptake = K_uptake × N_soil × GPP_rate
  dN_soil/dt = N_fix - N_uptake - N_denitrify

항상성:
  높은 N_soil → GPP↑ → 식물 성장↑ → N_uptake↑ → N_soil↓ (음의 피드백)
  낮은 O₂ → N_denitrify↑ → N₂ 방출↑ → N_soil↓ (무산소 환경 루프)

파일:
  nitrogen/fixation.py    — 질소고정 ODE (pioneer + 번개)
  nitrogen/cycle.py       — 질소순환 통합 (토양↔대기↔식물)
  nitrogen/column.py      — NitrogenColumn (상태 + 스텝)
  nitrogen/__init__.py
```

### 순환 2 — 장주기 순환 드라이버 (cycles/)
```
개념: Milankovitch 주기 → 계절성 진폭 → 빙하기-간빙기 → 생물권 변화

수식:
  eccentricity(t): e = e₀ + Σ aᵢ cos(2πt/Tᵢ)   # T ~ 100kyr
  obliquity(t):    ε = ε₀ + Σ bᵢ cos(2πt/Tᵢ)   # T ~ 41kyr
  precession(t):   ψ = 2πt/T_prec                # T ~ 26kyr

출력 → Loop C 강화:
  insolation(t, φ) = F₀/r(t)² × cos(θ_zenith(ε,ψ,φ,t))
  → fire_risk.dry_amplitude 동적 변경
  → biosphere.GPP 변조
  → 빙하기 진입/탈출 자연 창발

파일:
  cycles/milankovitch.py  — 이심률/경사/세차 ODE
  cycles/insolation.py    — 위도×시간 일사량 계산
  cycles/ice_albedo.py    — 빙하 알베도 피드백 (얼음↑→A↑→T↓→얼음↑)
  cycles/__init__.py
```

### 순환 3 — 중력-조석 주기 (gravity_tides/)
```
개념: 조석력 → 해양 혼합 → 영양염 순환 → 생산성 → 탄소 격리

수식:
  F_tidal(t) = F_moon(t) + F_sun(t)   # 조석 합력
  mixing_depth = K_mix × F_tidal        # 해양 혼합 깊이
  nutrient_upwelling = K_up × mixing_depth × (C_deep - C_surface)
  → 표층 영양염↑ → 식물플랑크톤↑ → 탄소 격리↑

항상성:
  강한 조석 → 혼합↑ → CO₂ 용해↑ → 대기 CO₂↓ → T↓ (음의 피드백)
  약한 조석 → 성층화↑ → 영양염 격리 → 생산성↓ → CO₂↑ (양의 피드백)

파일:
  gravity_tides/tidal_mixing.py   — 조석 혼합 ODE
  gravity_tides/ocean_nutrients.py — 영양염 upwelling 모델
  gravity_tides/carbon_pump.py     — 생물학적 탄소 펌프
  gravity_tides/__init__.py
```

---

## 넷째날 확장 포인트 (미래)

```
[예약됨, 넷쨋날 이후]

자기권-방사선 루프:
  em/magnetosphere.py → biosphere/column.py
  B↓ → cosmic_ray↑ → DNA 손상↑ → GPP↓

토양수분-증산 루프:
  biosphere/column.transpiration → atmosphere/water_cycle
  식생↑ → 증산↑ → 대기수분↑ → 강수↑ → 토양수분↑

대기화학 루프 (오존):
  O₂ + UV → O₃ 생성 (성층권)
  O₃ → UV 차단 → 식물 보호 → GPP↑
```

---

## 넷째날 파일 의존 구조

```
의존 방향 (기어 분리 원칙 유지):

data/ → core/ ← cognitive/
              ← em/
              ← atmosphere/ (em/, surface/ 읽기)
              ← surface/ (독립)
              ← biosphere/ (atmosphere/ 읽기)
              ← fire/ (독립)
              ← nitrogen/ (biosphere/ 읽기)    ← 넷째날 신규
              ← cycles/ (core/, fire/ 읽기)   ← 넷째날 신규
              ← gravity_tides/ (core/, biosphere/ 읽기) ← 넷째날 신규

연결기 (connector):
  gaia_loop_connector.py  — Loop A/B/C (셋째날 완성)
  gaia_bridge.py          — 뉴런-Gaia (셋째날 완성)
  day4_loop_connector.py  — 질소+Milankovitch+조석 (넷째날 신규)
```

---

## 구현 순서 (우선순위)

```
1단계 (가장 임팩트): Milankovitch → insolation → 계절성 드라이버
  → Loop C가 이미 obliquity_scale 받을 준비 완료
  → insolation(t, φ) 함수만 구현하면 즉시 연결 가능

2단계 (질소 루프): N_fix → GPP 연결
  → biosphere/column.py의 GPP 계산에 N_soil 게이트 추가
  → pioneer 단계부터 질소고정 시작

3단계 (조석-영양염): TidalField → ocean_nutrients
  → core/tidal_field.py가 이미 있음 → 연결만 필요

4단계 (빙하 알베도): 얼음 커버 → surface.albedo 동적 변경
  → Loop B의 연장선
```

---

## 수치 목표

```
넷째날 완성 시 기대 동작:

시작: 원시 행성 (O₂=0%, CO₂=5%, T=280K)
→ 100yr:  pioneer 토양 형성, 질소고정 시작
→ 3000yr: 원시토양 완성, 식물 발아
→ 1만yr:  O₂ 5% 도달, 질소 순환 안정
→ 10만yr: Milankovitch 빙하기 1사이클 완료
→ 1백만yr: 탄소-질소-산불 항상성 안정화

측정 지표:
  CO₂ [ppm]     → 280~400ppm 사이 진동 (Milankovitch)
  O₂ [%]        → 21% 수렴 (산불 attractor)
  N_soil [g/m²] → 5~15 g/m² 진동 (질소 루프)
  GFI [0~1]     → 0.003~0.01 (정상 지구 산불 강도)
  T_surface [K] → 285~295K 진동
```

---

*작성: GNJz/Qquarts + Claude Opus 4.6*
*날짜: 2026-02-27*
