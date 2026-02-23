# Phase A: 다음 작업 정리

**작성일**: 2026-02-22  
**기준**: IMPLEMENTATION_STATUS.md, PotentialFieldEngine·CookiieBrain 코드 확인

---

## 1. 다음에 할 일 (우선순위)

| 순서 | 작업 | 담당 위치 | 예상 |
|------|------|-----------|------|
| 1 | PotentialFieldEngine에 회전 항 연동 | PotentialFieldEngine + CookiieBrain | 2~3일 |
| 2 | Phase A 통합 테스트 (curl / 궤도 / 시각화) | CookiieBrain/Phase_A 또는 examples | 2~3일 |

---

## 2. 작업 1: PotentialFieldEngine 확장

### 2.1 목표

- 현재: `g(x) = -∇E(x)` (field_func만 사용)
- 목표: `g(x) = -∇E(x) + R(x)` (회전 항 추가, curl ≠ 0)

### 2.2 수정할 파일

#### A. `Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/PotentialFieldEngine/potential_field_engine.py`

**변경 요약**:

1. **`__init__`에 선택 인자 추가**
   - `rotational_func: Optional[Callable[[np.ndarray], np.ndarray]] = None`
   - 설명: `R(x)` 반환 함수. 없으면 기존과 동일 동작.

2. **`_compute_field(self, x)` 수정**
   - 현재: `return self.field_func(x)` 또는 수치 기울기.
   - 변경:
     ```python
     g = self.field_func(x) if self.field_func is not None else (-수치기울기)
     if self.rotational_func is not None:
         r = self.rotational_func(x)
         if len(g) != len(r):
             raise ValueError("field and rotational dimension mismatch")
         return g + r
     return g
     ```

**호환성**: `rotational_func=None`이면 기존와 동일. 기존 호출부 수정 불필요.

---

#### B. `CookiieBrain/cookiie_brain_engine.py`

**변경 요약**:

1. **설정 저장**
   - 현재 `potential_field_config`를 인자로 받지만 **저장하지 않음**. `self.potential_field_config = potential_field_config or {}` 추가 필요.
   - Phase A 사용 여부·폴 위치는 이 config에서 읽음: `enable_phase_a`, `phase_a_pole_position` 등.

2. **Phase A 사용 여부 설정**
   - `potential_field_config`에 예: `enable_phase_a: bool = False`, `phase_a_pole_position: Optional[np.ndarray] = None` 등으로 제어.
   - 또는 생성자에 `enable_phase_a=False`, `phase_a_config=None` 추가 (config와 둘 중 하나만 일관되게 사용).

3. **PotentialFieldEngine 생성 시 회전 항 넘기기**
   - `enable_phase_a`(또는 동일 의미 설정)가 True일 때:
     - Phase_A에서 `Pole`, `create_rotational_field` import.
     - 폴 위치: `phase_a_pole_position`이 있으면 사용, 없으면 에너지 최소점(또는 0) 등으로 설정.
     - `rotational_func = create_rotational_field(pole, use_simple_form=True)`.
   - `PotentialFieldEngine(..., field_func=self.current_field_func, rotational_func=rotational_func)` 형태로 전달.

4. **Well 변경 시**
   - 이미 `potential_field_engine = None`으로 재생성하고 있으므로, 다음 `update`에서 새로 만든 엔진에 새 `rotational_func`도 들어가면 됨.

**주의**: Phase_A는 `CookiieBrain/Phase_A`에 있으므로, `cookiie_brain_engine.py`에서 import 경로는 `from Phase_A import Pole, create_rotational_field` 또는 상대 경로로 처리. 실행 경로·PYTHONPATH에 따라 조정 필요.

---

### 2.3 검증 (작업 1 완료 후)

- CookiieBrain을 `enable_phase_a=True`(또는 config에 동일 설정)로 실행.
- **위치 차원**이 2 이상일 때만 2D curl 의미 있음. `state_vector` 길이가 4 이상이면 dim=2.
- Phase_A의 `compute_curl_2d(combined_field, x)`로 필드 계산 시 curl ≠ 0 확인.

---

## 3. 작업 2: Phase A 통합 테스트

### 3.1 목표

- 합성 필드 `g(x) = -∇E(x) + R(x)`에 대해:
  - curl ≠ 0 확인
  - 시간 적분 시 궤도가 한 점으로만 수렴하지 않고 순환하는지 확인
  - (선택) 위상 공간 (x, v) 시각화

### 3.2 방법

- **옵션 A**: `CookiieBrain/examples/` 아래에 `phase_a_integration_test.py` 추가.
  - WellFormationEngine으로 간단한 Well 하나 생성.
  - 동일한 potential/field + Phase_A `create_rotational_field`로 합성 필드 구성.
  - PotentialFieldEngine에 `rotational_func` 넘겨서 여러 스텝 업데이트.
  - 몇 개 테스트 점에서 `compute_curl_2d` 호출해 curl 값 출력.
  - 초기 상태를 우물 가장자리 등에 두고, 궤도가 닫히는지/도는지 눈으로 확인 (또는 거리/각도 로그).

- **옵션 B**: `Phase_A/` 아래에 `test_phase_a_integration.py` 등 단위 테스트.
  - `create_combined_field(gradient_field, R)`로 합성 필드만 만들고 curl 검증.
  - 실제 엔진은 쓰지 않고, “필드 함수만으로 Phase A 수식이 맞는지” 검증.

둘 다 하면 좋고, 최소한 옵션 A에서 curl 확인 + 궤도 한 번 돌려보기 권장.

---

## 4. 요약

| 항목 | 내용 |
|------|------|
| 다음 할 일 1 | PotentialFieldEngine에 `rotational_func` 추가, `_compute_field`에서 `g + R` 반환 |
| 다음 할 일 2 | CookiieBrain에서 Phase A 활성화 시 Pole·rotational_func 생성해 엔진에 전달 |
| 다음 할 일 3 | Phase A 통합 테스트: curl 확인 + 궤도(순환) 확인, 필요 시 시각화 |
| 호환성 | `rotational_func=None`이면 기존 동작 유지 |
| 참고 문서 | `IMPLEMENTATION_PLAN.md`, `IMPLEMENTATION_STATUS.md` |

---

## 5. 검증 결과 (2026-02-22)

- **PotentialFieldEngine**: `__init__`에 `rotational_func` 추가, `_compute_field`에서 `g + R` 반환 — 코드 구조와 일치.
- **CookiieBrain**: `potential_field_config`는 인자로만 받고 저장하지 않음 → 저장 추가 후 config에서 Phase A 옵션 읽기 필요.
- **Well 변경 시**: `potential_field_engine = None` 후 재생성하므로, 재생성 시점에 `rotational_func`만 넣어주면 됨.
- **Import**: `cookiie_brain_engine.py`는 `CookiieBrain/` 아래, Phase_A는 `CookiieBrain/Phase_A/` — 실행 경로/PYTHONPATH에 따라 `from Phase_A import ...` 또는 경로 조정 필요.

**결론**: 작업 계획 맞음. 위 보완 반영 후 진행하면 됨.

---

**작성**: Phase A 검토 기준 정리
