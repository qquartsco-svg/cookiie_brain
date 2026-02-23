# 🧠 Cookiie Brain 통합 엔진

**모든 개별 엔진들을 연결하는 통합 시스템**

Version: 0.1.2  
License: PHAM-OPEN  
Python: 3.8+

---

## 🎯 핵심 기능

✅ **엔진 간 자동 연결**
- WellFormationEngine → PotentialFieldEngine 자동 연결
- 데이터 흐름 자동 관리
- 상태 자동 동기화

✅ **전체 시스템으로 작동**
- 하나의 입력으로 전체 시스템 작동
- 엔진 간 상호작용 자동 발생

✅ **모듈화**
- 각 엔진은 독립적으로 작동 가능
- 필요한 엔진만 활성화 가능

---

## 📐 엔진 연결 순서

```
1. WellFormationEngine
   ↓ (W, b 생성)
2. PotentialFieldEngine
   ↓ (퍼텐셜 필드 변환 및 상태 업데이트)
3. HippoMemoryEngine (선택적, 구현 예정)
   ↓ (장기 기억 시스템)
4. CerebellumEngine (선택적, 통합 완료 ✅)
   ↓ (운동 조율 및 학습)
```

---

## 🚀 설치

### 의존성

```bash
pip install numpy
```

### BrainCore 연동 (필수)

```bash
# BrainCore 설치 또는 PYTHONPATH에 추가
```

### 엔진 설치

```bash
# WellFormationEngine 설치
cd Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/WellFormationEngine
pip install -e .

# PotentialFieldEngine 설치
cd ../PotentialFieldEngine
pip install -e .
```

---

## 📖 사용법

### 기본 사용

```python
from cookiie_brain_engine import CookiieBrainEngine
from brain_core.global_state import GlobalState
import numpy as np

# CookiieBrainEngine 생성
brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
)

# 상태 생성
state = GlobalState(
    state_vector=np.concatenate([
        np.array([1.0, 0.0]),  # 위치
        np.array([0.0, 0.0]),  # 속도
    ]),
    energy=0.0,
    risk=0.0,
)

# episodes 추가 (WellFormationEngine용)
state.set_extension("episodes", [
    # episodes 데이터...
])

# 통합 엔진 실행
result = brain.update(state)

# 에너지 확인
energy = brain.get_energy(result)
print(f"에너지: {energy}")
```

### 고급 사용

```python
# 모든 엔진 활성화
brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    enable_cerebellum=True,
    enable_hippo_memory=False,  # 구현 예정
    error_isolation=True,  # 에러 격리 모드
    cerebellum_config={  # CerebellumEngine 설정
        "memory_dim": 10,
        "dt": 0.002,
        "correction_scale": 0.02,
    },
)

# 설정 커스터마이징
brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    well_formation_config={
        # WellFormationEngine 설정...
    },
    potential_field_config={
        # PotentialFieldEngine 설정...
    },
    cerebellum_config={
        # CerebellumEngine 설정...
    },
)
```

### 통합 테스트 데모

```python
# examples/integration_test_demo.py 실행
python examples/integration_test_demo.py
```

이 데모는:
- WellFormationEngine이 episodes로부터 기억 우물 생성
- PotentialFieldEngine이 우물을 퍼텐셜 필드로 변환
- 상태가 우물(에너지 최소점)로 수렴하는지 검증
- 시각화 결과 생성 (`examples/output/integration_test_convergence.png`)
```

---

## 🔗 엔진 연결 구조

### WellFormationEngine → PotentialFieldEngine

**연결 구조**:
1. **WellFormationEngine**: W, b 생성 (Hopfield 에너지)
   - Hopfield 에너지: `E(x) = -(1/2) * Σ_ij w_ij x_i x_j - Σ_i b_i x_i`
2. **PotentialFieldEngine**: 에너지 지형 → 퍼텐셜 필드 변환
   - 퍼텐셜: `V(x) = E(x)`
   - 필드: `g(x) = -∇E(x) = Wx + b`

**설계 목적**:
- 구조적 통합 레이어 구축
- 엔진 간 데이터 흐름 자동 관리
- 확장 가능한 아키텍처

---

## 📁 파일 구조

```
CookiieBrain/
├── cookiie_brain_engine.py    # 통합 엔진
├── README.md                  # 이 파일
├── HANDOVER_DOCUMENT.md       # 인수인계 문서
├── CODE_REVIEW_FIXES.md       # 코드 리뷰 피드백 반영 사항
├── FOLDER_STRUCTURE_ANALYSIS.md  # 폴더 구조 분석
└── examples/                  # 예제 코드
    ├── basic_usage.py         # 기본 사용 예제
    └── advanced_usage.py      # 고급 사용 예제
```

---

## ✅ 설계 원칙

1. **불변성 유지**
   - state를 직접 수정하지 않고 copy-and-return (deep=True)
   - 완전한 복제로 extension 내부 dict, numpy 배열도 복제

2. **엔진 간 자동 연결**
   - 데이터 흐름 자동 관리
   - WellFormationEngine → PotentialFieldEngine 자동 연결

3. **Well 변경 감지**
   - Well 결과 변경 시 potential 함수 및 엔진 재생성
   - stale field 방지

4. **에러 격리**
   - error_isolation=True 시 엔진 실패해도 계속 진행

5. **상태 자동 동기화**
   - GlobalState가 전체 시스템에서 공유
   - 엔진 간 상태 자동 동기화

6. **모듈화**
   - 각 엔진은 독립적으로 작동 가능
   - 필요한 엔진만 활성화 가능

---

## 🔍 Extensions 저장 규약

### WellFormationEngine 결과

```python
state.set_extension("well_formation", {
    "W": well_result.W.copy(),  # numpy 배열 복제
    "b": well_result.b.copy(),  # numpy 배열 복제
    "well_result": well_result,
})
```

### PotentialFieldEngine 결과

```python
state.set_extension("potential_field", {
    "potential": V,
    "field": g,
    "acceleration": a,
})
```

### CerebellumEngine 결과

```python
state.set_extension("cerebellum", {
    "correction": correction,
    "target_state": target_state,
})
```

---

## 📝 표준 API

### 필수 메서드

- `update(state: GlobalState) -> GlobalState`: 상태 업데이트

### 선택 메서드

- `get_energy(state: GlobalState) -> float`: 에너지 반환
- `get_state() -> Dict[str, Any]`: 엔진 내부 상태 반환
- `reset()`: 상태 리셋

---

## 🎯 다음 단계

1. **통합 테스트 작성**
   - 엔진 간 데이터 흐름 검증
   - 상태 동기화 검증

2. **HippoMemoryEngine 통합**
   - HippoMemoryEngine 구조 확인
   - GlobalState 인터페이스 래핑

3. **다른 엔진들 통합**
   - Ring Attractor Engine
   - Grid Engine
   - 기타 엔진들

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.1  
**상태**: 구조 개선 완료, 통합 테스트 데모 추가 ✅

