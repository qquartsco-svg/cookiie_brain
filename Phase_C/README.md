# Phase C: 요동 (Fluctuation)

> 결정론적 시스템에 확률적 노이즈를 추가 — Langevin 방정식

---

## 요동이란

같은 초기 조건 → 항상 같은 결과. 이것이 결정론이다.
요동을 넣으면 매번 다른 결과가 나올 수 있다.

- 감쇠로 우물에 갇힌 상태에서 **우연히** 장벽을 넘는 것 (Kramers escape)
- 같은 기억에 고착되지 않고 **자발적으로** 다른 기억으로 전이하는 것
- 이것이 창의적 연상의 물리적 모델

---

## 수식

```
이전 (결정론):  ẍ = -∇V(x) + ωJv - γv + I(x,v,t)
이후 (확률적):  ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

| 기호 | 의미 |
|------|------|
| σ | 노이즈 세기 |
| ξ(t) | 백색 노이즈 (매 순간 랜덤 방향) |
| σ=0 | 결정론적 (기존과 100% 동일) |
| σ>0 | 확률적 전이 가능 |

이것은 **Langevin 방정식** (확률 미분 방정식)이다.

### 요동-소산 정리 (FDT)

σ를 직접 설정하는 대신, **온도 T**를 설정하면 물리 법칙이 σ를 결정한다:

```
σ² = 2γT/m    (kB = 1 자연단위)
```

| 기호 | 의미 | 기본값 |
|------|------|--------|
| T | 시스템 온도 (인지: 활성 수준) | None (비활성) |
| m | 입자 질량 (인지: 사고의 관성) | 1.0 |
| γ | 감쇠 계수 (Phase B에서 도입) | 0.0 |

**왜 중요한가:**
- FDT 이전: σ, γ 독립 → 물리적 제약 없음 → 비물리적 조합 가능
- FDT 이후: σ가 γ, T, m에 종속 → **Boltzmann 정상 분포 보장**
  - `P(x,v) ∝ exp(-E/T)` (열평형)
  - `⟨½mv²⟩ = T/2` (등분배, DoF 당)

**모드 우선순위:**

| 조건 | 모드 | σ |
|------|------|---|
| `noise_sigma > 0` | manual | 직접 지정값 |
| `temperature > 0` + `γ > 0` | fdt | `√(2γT/m)` |
| 그 외 | off | 0 |

---

## 구현 위치

Phase C는 독립 모듈이 아니라 **PotentialFieldEngine의 파라미터 확장**이다.

| 항목 | 파일 | 위치 |
|------|------|------|
| 핵심 구현 | `potential_field_engine.py` | PotentialFieldEngine (별도 레포) |
| config 전달 | `cookiie_brain_engine.py` | CookiieBrain |
| 검증 | `examples/fluctuation_verification.py` | CookiieBrain |

### PotentialFieldEngine 파라미터

```python
# FDT 모드 (권장): temperature 설정 → σ 자동 결정
engine = PotentialFieldEngine(
    potential_func=mwp.potential,
    field_func=mwp.field,
    omega_coriolis=0.3,     # Phase A: 자전
    gamma=0.05,             # 감쇠
    temperature=1.0,        # FDT: σ = √(2γT/m) 자동 계산
    mass=1.0,               # 입자 질량
    noise_seed=42,
    dt=0.005,
)

# Manual 모드: σ를 직접 지정 (FDT 무시)
engine = PotentialFieldEngine(
    ...,
    noise_sigma=0.15,       # 직접 지정 → temperature 무시
)
```

### CookiieBrainEngine 사용

```python
brain = CookiieBrainEngine(
    potential_field_config={
        "enable_phase_a": True,
        "phase_a_omega": 0.3,
        "gamma": 0.05,
        "temperature": 1.0,      # ← FDT 모드 (σ 자동)
        "mass": 1.0,
        "noise_seed": 42,
    },
)
```

---

## 왜 독립 모듈이 아닌가

| Phase | 폴더 | 코드 | 성격 |
|-------|------|------|------|
| A (자전) | `Phase_A/` | `rotational_field.py` | 회전 함수를 **생성**하여 PFE에 전달 |
| B (공전) | `Phase_B/` | `multi_well_potential.py` | 퍼텐셜 함수를 **생성**하여 PFE에 전달 |
| C (요동) | `Phase_C/` | **없음** (PFE 파라미터) | 생성할 게 없음. σ 값만 넘기면 됨 |

Phase A, B는 "무언가를 만들어서 전달"하는 독립 모듈이다.
Phase C는 "적분기 내부에서 노이즈를 추가"하는 것이라 별도 코드가 필요 없다.

---

## 적분 방식

Strang splitting의 감쇠(D) 스텝을 O-U exact 반스텝으로 확장:

```
기존: D-S-K-R-K-S-D     (D = dissipation only)
현재: O-S-K-R-K-S-O     (O = O-U exact: dissipation + noise 결합)

O(h):  dv = -γv dt + σ dW  의 정확해
  v → e^{-γh} · v + amp(h) · ξ,   ξ ~ N(0,1)

  amp(h) = σ √((1 - e^{-2γh}) / (2γ))
  γ→0 limit: amp(h) = σ √h
```

반스텝 h = dt/2 적용 → 시작과 끝에 대칭 래핑.

- **O-U exact**: 감쇠와 노이즈의 정확한 결합 (분리 적용이 아님)
- γ>0일 때 노이즈 분산이 `(1-e^{-2γh})/(2γ)` 로 자동 보정됨
- γ=0이면 `σ√h` (표준 Wiener increment)로 환원
- σ=0이면 기존 D 스텝과 동일 (하위 호환)

---

## 검증 결과

### Phase C v1: 요동 기본

```
python examples/fluctuation_verification.py
```

| # | 검증 | 결과 |
|---|------|------|
| 1 | 하위 호환 (σ=0) | PASS — 시드 무관 동일 궤적, E drift 2.58e-06 |
| 2 | Kramers 탈출 (σ=0.25) | PASS — 갇힌 입자 10/10 탈출 |
| 3 | 통계적 비편향 | PASS — bias ratio 0.066 |
| 4 | 감쇠+노이즈 정상 상태 | PASS — E bounded, std=0.25 |

### Phase C v2: FDT (요동-소산 정리)

```
python examples/fdt_verification.py
```

| # | 검증 | 결과 |
|---|------|------|
| 1 | 하위 호환 (temperature=None) | PASS — 기존 결정론적 동작 동일 |
| 2 | FDT σ 계산 (σ²=2γT/m) | PASS — 상대 오차 0.00e+00 |
| 3 | Manual override (noise_sigma 우선) | PASS — temperature 무시 |
| 4 | Boltzmann 등분배 (⟨½v²⟩=T/2) | PASS — 상대 오차 0.6% |
| 5 | γ=0 안전장치 | PASS — σ=0 (FDT 요구) |

---

## 요동이 들어가면 뭐가 달라지나

| 현상 | 결정론 (σ=0) | 확률적 (σ>0) |
|------|-------------|-------------|
| 우물에 갇힘 | 영원히 갇힘 | 확률적으로 탈출 가능 |
| 공전 궤도 | 항상 같은 경로 | 매번 약간 다른 경로 |
| 같은 초기 조건 | 같은 결과 | 다른 결과 가능 |
| 기억 전환 | 감쇠/주입으로만 | 자발적 전환 가능 |

---

## 향후 확장 가능성

| 확장 | 설명 | 독립 모듈 필요? |
|------|------|----------------|
| ~~상수 σ~~ | ~~직접 지정~~ | ~~아니오~~ (v1 완료) |
| ~~FDT (σ²=2γT/m)~~ | ~~온도 기반 자동 σ~~ | ~~아니오~~ (v2 완료) |
| σ(x) 위치 의존 | 우물 근처 약하고 장벽에서 강함 | **예** |
| Colored noise | 시간 상관 있는 노이즈 (OU process) | **예** |
| Temperature schedule | T(t) 시간에 따라 변함 (simulated annealing) | 아니오 (callback) |

이런 확장이 필요해지면 이 폴더에 모듈을 추가한다.

---

*Phase C v1 완료: 2026-02-24*
*Phase C v2 (FDT) 완료: 2026-02-24*
