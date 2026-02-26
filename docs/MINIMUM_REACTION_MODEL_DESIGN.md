# 자가순환 최소 반응 모델 통합 설계

**AUTONOMOUS_CYCLE_PHYSICS** 요약:
- 단순 역학+복사+온실만으로는 자가순환 객체 불가
- **화학 반응 + 구배 + 확산 + 경계 형성** 필요
- 최소 수학: Ȧ = f(A,B), Ḃ = g(A,B) — Brusselator, Lotka-Volterra, BZ

---

## 1. 목표

지금 시스템(CookiieBrain 환경)에 **최소 반응 모델**을 붙여,
**어느 조건에서** 자가순환이 나타나는지 **측정·기록**한다.

---

## 2. 후보 모델

| 모델 | 수식 | 특징 |
|------|------|------|
| **Lotka-Volterra** | ẋ = ax - bxy, ẏ = cxy - dy | 포식자-피식자, limit cycle |
| **Brusselator** | Ȧ = k₁ - k₂A + k₃A²B, Ḃ = k₂A - k₃A²B | 자가촉매, oscillatory |
| **BZ (Belousov-Zhabotinsky)** | 복잡한 반응 네트워크 | 공간 패턴, spiral |

**우선순위**: Lotka-Volterra 또는 Brusselator (단순, 2변수)

---

## 3. 통합 포인트

### 입력 (환경에서)

| 환경 변수 | 의미 | CookiieBrain 출처 |
|-----------|------|-------------------|
| F_solar | 복사 조도 | solar_environment.bodies["Earth"]["F_solar"] |
| T_surface | 표면 온도 | solar_environment.bodies["Earth"]["T_surface"] |
| habitable | 액체 물 가능 | solar_environment.bodies["Earth"]["habitable"] |

→ **에너지 구배**, **비평형** 정도를 환경에서 받음.

### 출력 (반응 모델)

| 변수 | 의미 |
|------|------|
| A(t), B(t) | 농도 또는 활동도 |
| oscillation | 진동 여부 |
| limit_cycle | 자가 유지 진동 여부 |

### 연결 규칙

- 반응 모델은 **독립 레이어**. atmosphere/를 수정하지 않음.
- 환경(T, F)을 **파라미터**로 받아 반응 속도에 반영.
- 결과를 `state.set_extension("reaction_dynamics", {...})` 로 저장.

---

## 4. 폴더·모듈 설계

```
solar/
├── reaction/              ← 신규 (Phase 8?)
│   ├── __init__.py
│   ├── lotka_volterra.py  ← Ȧ, Ḃ
│   ├── brusselator.py     ← (옵션)
│   └── brain_core_bridge.py  ← extension 형식
```

또는 00_BRAIN 레벨에 **독립 엔진**으로:
```
00_BRAIN/
├── Engines/
│   └── ReactionDynamics_Engine/   ← Brusselator, L-V
```

**선택**: CookiieBrain 내 `solar/reaction/` 이 의존성이 짧음 (solar_environment 읽기).

---

## 5. 상태 변수

GlobalState extensions:
- `solar_environment`: 이미 정의됨
- `reaction_dynamics`: `{ "A": float, "B": float, "oscillating": bool, "t": float }`

---

## 6. 다음 단계

1. **Lotka-Volterra** 단위 구현 (순수 ODE, 환경 무관)
2. **환경 연동**: T 또는 F를 반응률 파라미터에 매핑
3. **창발 조건 기록**: 어느 (T, F, 초기조건)에서 limit cycle 생기는지
4. **BrainCore extension** 형식으로 저장

---

## 7. 반응 동역학 레이어 — 최소 사양

상세: [REACTION_DYNAMICS_LAYER_SPEC.md](REACTION_DYNAMICS_LAYER_SPEC.md)

**최소 입력**: temperature_field, energy_flux, concentration_vector, diffusion, boundary_condition  
**창발 판정**: limit_cycle, entropy_production_rate, Lyapunov_exponent, autocatalytic_loop  
**현실**: 반응 ODE만으로는 부족 → 반응-확산 PDE 필요

---

## 8. 분기점 — 첫 기어 선택

| 후보 | 특징 |
|------|------|
| Brusselator | 자가촉매, oscillatory |
| Gray-Scott | 2종 피드백, 공간 패턴 |
| autocatalytic loop | A + B → 2A (최소) |
| pH gradient 기반 | 전기화학 구배 |

→ **여기서부터가 진짜 시작.**  
물리에서 화학으로 넘어가는 **첫 기어를 어디에 꽂을지** 결정해야 함.

---

## 9. 체크리스트

- [ ] 반응 ODE 구현 (1단계, 공간 무관)
- [ ] 반응-확산 PDE 확장 (2단계, 경계 형성)
- [ ] solar_environment 읽기 (T, F) → energy_input
- [ ] extension 형식 정의
- [ ] 창발 판정 (limit_cycle, entropy_production, Lyapunov)
- [ ] VERSION_LOG, README 반영
