# Phase A: 작업 상황 점검 (사실만)

**기준일**: 2026-02-22  
**범위**: 설계 논리, 4개 확인 포인트, 작업 상태, 우선순위. 감정·평가 없음.

---

## 1. 설계 논리

- PotentialFieldEngine에 `rotational_func` 추가, `_compute_field`에서 `g + r` 반환.
- CookiieBrain에서 enable 플래그로 제어.
- 기존 코드와 호환 유지 (`rotational_func=None`이면 동일 동작).
- 구조적으로 설계 방향 문제 없음.

---

## 2. 확인 포인트 4개 (코드 기준)

### 체크 1: field_func 부호

- **문서**: `well_formation_integration.py` — "g(x) = -∇E(x) = Wx + b".
- **구현**: `field(x) = np.dot(W, x) + b`. E = -(1/2)x'Wx - b'x → ∇E = -Wx - b → **-∇E = Wx + b**.
- **결과**: field_func는 **-∇E** 반환. 합성 시 `g + R` = -∇E + R 맞음. 부호 일관됨.

### 체크 2: 회전항 에너지 보존 (r·R = 0)

- **단순형**: R = ω J r, J 반대칭 → r'(Jr)=0. **만족**.
- **거리 의존형**: R ∝ [-r_y, r_x] → r·R = 0. **만족**.
- **구현**: `create_skew_symmetric_matrix` + `R_vec = ω * (J @ r)`. 반대칭 사용. 수식상 일치.

### 체크 3: 감쇠 여부

- **PotentialFieldEngine**: 감쇠 항 γ **없음**. `v_new = v + dt*a`, `x_new = x + dt*v_new` 만 존재.
- **CONFIG**: `DT = 0.01`. dt 안정성 범위 문서/실험 없음.
- **의미**: 회전항만 넣으면 무감쇠. spiral out/in 가능성 있음. 검증 필요.

### 체크 4: 차원 제한

- **compute_curl_2d**: 2D 전용. `len(x)==2` 아님 시 ValueError.
- **Phase A curl 검증**: 2D에서만 유효. 3D 이상이면 curl 스칼라 하나로 부족.
- **CookiieBrain**: 예제 `integration_test_demo.py`는 n_dim=2. 기본 차원은 예제/호출부에 따름.

---

## 3. 현재 작업 상태

| 구분 | 상태 |
|------|------|
| 설계 | 완료. 문서화됨. |
| 코드 통합 | **완료.** (PotentialFieldEngine 확장, CookiieBrain 연동, phase_a_integration_test.py 있음.) |
| 수학 검증 | **미실행.** 실행 스크립트는 있음: `Phase_A/verify_math.py` (부호·직교성). |
| 안정성 검증 | 미실행. (감쇠·dt·궤도.) |

구현은 들어가 있음. 다음은 수학 검증 스크립트 실행 후, 필요 시 보완.

---

## 4. 우선순위 (당장 할 순서)

1. field_func 부호 단위 검증 (선택이지만 권장).
2. rotational_func가 skew-symmetric 기반인지 및 r·R=0 검증.
3. 단일 우물 + 회전항만으로 2D 단순 시뮬 테스트.
4. 그 다음: PotentialFieldEngine 확장, CookiieBrain 연동.

태양·달·세차는 이후 단계.

---

## 5. 회전항 형태

- **단순형** (use_simple_form=True): R = ω J (x - x_pole). 단순 자전. 현재 권장.
- **거리 의존형**: R ∝ [-r_y, r_x]/(‖r‖²+ε). 위성/외부장에 가깝다.
- 문서·기본값은 단순형. 단순 자전부터가 안전.

---

## 6. 결론 (사실만)

- 설계 방향: 타당. 구조 호환성 유지.
- 수학적 일관성: 코드상 field_func=-∇E, R은 r·R=0 만족. 검증 테스트는 미실행.
- 에너지 보존성: 회전항 수식·구현 상 만족. 검증 테스트 미실행.
- 차원: curl 검증은 2D 전용. 기본 차원은 예제 의존.
- 안정성: 감쇠 없음, dt 실험 없음.
- 단계: Phase A는 시작선. 구현 전에 수학 검증 체크리스트 확정·실행 단계.

---

**상세 체크리스트**: `MATH_VERIFICATION_CHECKLIST.md` 참고.
