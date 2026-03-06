# Phase A — 무슨 작업 했는지 / 건드린 파일 내용 전체 보기

이 파일 하나만 열면 된다. 아래에서 각 파일 경로 누르면(또는 찾아가면) **실제로 건드린 코드·문서 내용**이 바로 보인다.

---

## 1. PotentialFieldEngine (수정한 코드)

**경로**: `Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/PotentialFieldEngine/potential_field_engine.py`

**한 일**: `rotational_func` 인자 추가. 필드 계산 시 **g + R(x)** 더함.

### 건드린 부분 — __init__

```python
def __init__(
    self,
    potential_func: Callable[[np.ndarray], float],
    field_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    rotational_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,  # ← 추가
    dt: float = None,
    ...
):
    ...
    self.rotational_func = rotational_func  # 회전 항 (Optional, Phase A)
```

### 건드린 부분 — _compute_field

```python
def _compute_field(self, x: np.ndarray) -> np.ndarray:
    # 기울기 성분
    if self.field_func is not None:
        g = self.field_func(x)
    else:
        # 수치 기울기 ... (생략)
        g = -grad
    # 회전 항 (Phase A) ← 추가
    if self.rotational_func is not None:
        r = self.rotational_func(x)
        if len(g) != len(r):
            raise ValueError(...)
        g = g + r
    return g
```

---

## 2. CookiieBrain 엔진 (수정한 코드)

**경로**: `CookiieBrain/cookiie_brain_engine.py`

**한 일**: Phase_A import, `potential_field_config` 저장, `enable_phase_a` 켜면 회전항 만들어서 엔진에 넘김.

### 건드린 부분 — Phase_A import

```python
# Phase_A (Rotational field, 자전) import
try:
    phase_a_path = Path(__file__).parent
    if str(phase_a_path) not in sys.path:
        sys.path.insert(0, str(phase_a_path))
    from Phase_A import Pole, create_rotational_field
    PHASE_A_AVAILABLE = True
except ImportError:
    PHASE_A_AVAILABLE = False
    Pole = None
    create_rotational_field = None
```

### 건드린 부분 — config 저장

```python
self.potential_field_config = potential_field_config or {}
self.enable_phase_a = self.potential_field_config.get("enable_phase_a", False)
self.phase_a_pole_position = self.potential_field_config.get("phase_a_pole_position")
self.phase_a_strength = self.potential_field_config.get("phase_a_strength", 1.0)
self.phase_a_rotation_direction = self.potential_field_config.get("phase_a_rotation_direction", 1)
```

### 건드린 부분 — PotentialFieldEngine 생성 시 회전항 넘기기

```python
if not self.potential_field_engine:
    rotational_func = None
    if self.enable_phase_a and PHASE_A_AVAILABLE and Pole is not None and create_rotational_field is not None:
        dim = len(self.current_well_result.b)
        pole_position = self.phase_a_pole_position
        if pole_position is None:
            pole_position = np.zeros(dim)
        else:
            pole_position = np.array(pole_position)
        if len(pole_position) != dim:
            pole_position = np.zeros(dim)
        pole = Pole(
            position=pole_position,
            rotation_direction=int(self.phase_a_rotation_direction),
            strength=float(self.phase_a_strength),
        )
        rotational_func = create_rotational_field(pole, use_simple_form=True)
    self.potential_field_engine = PotentialFieldEngine(
        potential_func=self.current_potential_func,
        field_func=self.current_field_func,
        rotational_func=rotational_func,  # ← 추가
    )
```

---

## 3. verify_math.py (새로 만든 검증 스크립트)

**경로**: `CookiieBrain/Phase_A/verify_math.py`

**한 일**: 부호(field = -∇E), 직교성(r·R=0) 수치로 체크. 실행하면 PASS/FAIL 출력.

### 파일 전체

```python
"""Phase A: 부호 및 직교성 수치 검증 (MATH_VERIFICATION_CHECKLIST)
체크 1: field_func = -∇E 인지 (고정 W, b로 수치 미분과 비교)
체크 2: r·R(x) ≈ 0 인지 (여러 x, pole에 대해)
"""
import numpy as np
import sys
from pathlib import Path
# ... path 설정 ...

def test_field_sign():
    """체크 1: create_field_from_wells 반환값이 -∇E 인지 확인."""
    # 고정 W, b (2x2) → V, field 만든 뒤
    # 수치 -∇E 와 field(x) 비교 → 오차 norm 출력, 1e-5 미만이면 OK

def test_orthogonality():
    """체크 2: r·R(x) ≈ 0 (단순형)."""
    # Pole, create_rotational_field 로 R 만들고
    # 여러 점 x에서 np.dot(r, R(x)) ≈ 0 확인

def main():
    r1 = test_field_sign()
    r2 = test_orthogonality()
    print("전체:", "PASS" if (r1 and r2) else "일부 FAIL")
```

---

## 4. phase_a_integration_test.py (새로 만든 테스트 스크립트)

**경로**: `CookiieBrain/examples/phase_a_integration_test.py`

**한 일**: 우물 하나 + `enable_phase_a=True` 로 CookiieBrain 돌리고, curl 한 점에서 계산, 궤도 200 step 출력.

### 핵심 부분

```python
brain = CookiieBrainEngine(
    ...
    potential_field_config={
        "enable_phase_a": True,
        "phase_a_pole_position": [0.0, 0.0],
        "phase_a_strength": 0.8,
        "phase_a_rotation_direction": 1,
    },
    ...
)
# Well 생성 후 curl(합성 필드) 계산해서 출력
# 200 step 돌려서 위치 이력·원점으로부터 거리 출력
```

---

## 5. CURRENT_WORK_OVERVIEW.md (한 페이지 요약 문서)

**경로**: `CookiieBrain/Phase_A/CURRENT_WORK_OVERVIEW.md`

**한 일**: 목표(우물 자전), 무슨 작업 했는지, 당신이 나중에 할 수 있는 것, 한 줄 요약.

### 내용 요약

- **목표**: 우물에 고인 걸 자전 시키기.
- **한 작업**: (1) PotentialFieldEngine에 회전 항 옵션 (2) CookiieBrain에 자전 켜는 설정 (3) 검증·테스트 스크립트 (4) 문서 정리.
- **당신이 할 일**: 아직 없음. 나중에 `phase_a_integration_test.py`, `verify_math.py` 실행해 보면 됨.

---

## 6. 기타 문서 (경로만)

- `CookiieBrain/Phase_A/NEXT_WORK.md` — 다음에 할 작업 정리
- `CookiieBrain/Phase_A/MATH_VERIFICATION_CHECKLIST.md` — 수학 검증 체크리스트
- `CookiieBrain/Phase_A/STATUS_CHECK.md` — 작업 상황 점검 (사실만)
- `CookiieBrain/Phase_A/FEEDBACK_AND_STATUS.md` — 피드백 반영·불일치 정리
- `CookiieBrain/Phase_A/MODIFIED_FILES_LIST.txt` — 손댄 파일 목록

---

**이 파일**: `CookiieBrain/Phase_A/FULL_WORK_HISTORY.md`  
→ 여기만 열면 **무슨 작업했는지**랑 **건드린 코드/문서**가 다 보인다.

---

## 마지막 작업 요약 (열어서 확인)

작업·수정 후 **마지막에** 뭘 했는지 확인하려면 아래 파일을 연다.

- **경로**: `CookiieBrain/Phase_A/LAST_WORK_SUMMARY.md`  
- **규칙**: 작업할 때마다 이 요약 파일을 갱신하고, 대화 끝에 그 내용을 보여준다.
