# Phase A: 구현 전 수학 검증 체크리스트

**목적**: 구현 직전 수학적 일관성·에너지 보존·차원·안정성 확인  
**평가/감정 없음. 사실만 기록.**

---

## 1. field_func 부호 일관성

**목표**: 합성 필드가 `g(x) = -∇E(x) + R(x)` 로 동작하는지 확인.

| 항목 | 위치 | 결과 |
|------|------|------|
| 문서/주석 상의 정의 | `potential_field_engine.py` docstring | `g(x) = -∇V(x)` (V=E 사용) |
| `well_formation_integration.py` | `create_field_from_wells` | 주석: "g(x) = -∇E(x) = Wx + b" |
| 실제 반환값 | `field(x)` | `return np.dot(W, x) + b` |
| E 정의 | 동일 파일 | E(x) = -(1/2)x'Wx - b'x → ∇E = -Wx - b → **-∇E = Wx + b** |

**결론**: field_func는 **-∇E**를 반환한다. 합성 시 `g + R` 하면 `-∇E + R` 맞음.

**체크**: [ ] 코드 배포 전 한 번 더 단위 테스트로 확인 권장 (W, b 고정값으로 -∇E 수치 미분과 비교).  
→ **실행**: `Phase_A/verify_math.py` (test_field_sign).

---

## 2. 회전항 에너지 보존 (x·R(x) = 0)

**목표**: 회전항이 에너지를 주입/빼지 않도록, `r·R(r)=0` (r = x - x_pole) 확인.

| 형태 | 수식 | r·R 검증 |
|------|------|----------|
| 단순형 (use_simple_form=True) | R = ω J r, J 반대칭 | r'(J r) = 0 (반대칭이면 r'Jr=0). **만족** |
| 거리 의존형 (use_simple_form=False) | R = ω·strength·[-r_y,r_x]/(‖r‖²+ε) | r_x·(-r_y)+r_y·r_x = 0. **만족** |

**구현 확인** (`rotational_field.py`):

- 단순형: `J = create_skew_symmetric_matrix(n, axis=[0,1])`, `R_vec = ω * (J @ r)`. J는 반대칭.
- 2D에서 J@r = [-r_y, r_x] → r·(J@r) = 0.

**체크**: [ ] 단위 테스트: 여러 x, pole에 대해 `np.dot(r, R(x))` ≈ 0 (단순형·거리의존형 각각).  
→ **실행**: `Phase_A/verify_math.py` (test_orthogonality).

---

## 3. 감쇠 및 시간 스텝

**목표**: 무감쇠 + 회전항일 때 수치 안정성·발산 여부 확인.

| 항목 | 현재 상태 |
|------|-----------|
| PotentialFieldEngine 감쇠 항 γ | **없음**. `v_new = v + dt*a`, `x_new = x + dt*v_new` 만 사용. |
| CONFIG | `DT = 0.01` (CONFIG.py). 엔진 기본 dt. |
| 회전항만 추가 시 | 무감쇠이면 spiral out/in 가능. 문서상 안정화는 Phase A-2(선택)에서 `-γx` 검토. |

**체크**:

- [ ] 단일 우물 + 회전항만으로 시뮬레이션 시, 사용 dt에서 에너지/반경이 폭발하지 않는지 확인.
- [ ] (선택) dt를 올렸을 때 불안정해지는 구간 확인. 필요 시 Phase A-2에서 γ 도입.

---

## 4. 차원 및 curl 검증 범위

**목표**: Phase A 수식·검증이 어떤 차원에서 유효한지 명확히.

| 항목 | 내용 |
|------|------|
| `compute_curl_2d` | **2D 전용**. `∂F_y/∂x - ∂F_x/∂y`. |
| rotational_field | 단순형은 n≥2에서 동작. J는 xy 평면(axis=[0,1]) 기준. 3D 이상이어도 회전은 2D 평면에만. |
| CookiieBrain 기본 차원 | 예제: `integration_test_demo.py`는 `n_dim=2`. 다른 예제는 호출부에서 결정. |

**결론**: **curl 검증은 2D에서만 의미 있음.** state_vector 길이 4 이상이면 위치 차원 2 가능. 3D 이상이면 curl 스칼라 하나로는 부족.

**체크**:

- [ ] Phase A 통합 테스트는 **위치 차원 2**로 고정하고 진행할 것인지 결정.
- [ ] 문서/주석에 "Phase A curl 검증은 2D 전용" 명시.

---

## 5. 회전항 형태 선택 (ωJx vs pole·거리의존)

**목표**: 단순 자전부터 할지, pole·1/r² 형태부터 할지 명확히.

| 형태 | 코드 | 용도 |
|------|------|------|
| 단순형 | `R(x) = ω J (x - x_pole)`, use_simple_form=True | 단순 자전. pole은 회전 중심만 제공. |
| 거리 의존형 | `R = ω·strength·[-r_y,r_x]/(‖r‖²+ε)` | 크기가 거리에 반비례. 위성/외부장 느낌에 가깝다. |

**현재 문서/기본값**: `use_simple_form=True` 권장. 단순 자전 먼저가 안전.

**체크**: [ ] Phase A-1은 **단순형만** 사용할지 확정. (이미 구현·문서는 단순형 우선.)

---

## 6. 구현 전 점검 순서 (우선순위)

1. [ ] **field_func 부호**: 단위 테스트로 `field(x)` = -∇E(x) 확인 (고정 W, b).
2. [ ] **rotational_func 에너지**: `r·R(x)` ≈ 0 테스트 (단순형, pole 일부 케이스).
3. [ ] **단일 우물 + 회전항 시뮬**: 2D, 단순형만, 감쇠 없이. 궤도·에너지 추이 확인.
4. [ ] **차원**: Phase A 통합 테스트를 2D로 고정할지 결정하고 문서화.

---

## 7. 현재 작업 상태 (사실만)

| 구분 | 상태 |
|------|------|
| 설계 논리 | PotentialFieldEngine에 rotational_func 추가, _compute_field에서 g+r 반환, CookiieBrain에서 플래그 제어. 기존 호환 유지. |
| field_func 부호 | 코드·수식 상 -∇E 반환. 검증 테스트는 미실행. |
| 회전항 x·R=0 | 단순형·거리의존형 모두 수식상 만족. 구현은 반대칭 J 사용. 검증 테스트 미실행. |
| 감쇠 | 없음. dt=0.01 기본. 안정성 실험 미실행. |
| 차원 | curl은 2D 전용. 기본 상태 차원은 예제별 상이. |
| 구현 | PotentialFieldEngine 확장·CookiieBrain 연동 미구현. |
| 수학 검증 | 위 체크리스트 미실행. |
| 안정성 검증 | 미실행. |

---

**다음 단계**: 위 체크리스트 1~4번 항목부터 순서대로 실행한 뒤, 결과만 기록하고 구현(엔진 확장·통합) 진행.
