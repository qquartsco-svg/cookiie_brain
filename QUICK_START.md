# 빠른 시작 가이드

**작성일**: 2026-02-21  
**버전**: 0.1.4

---

## 📍 폴더 위치

### 메인 폴더
```
/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/
```

### Phase A 폴더
```
/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/Phase_A/
```

---

## 🚀 빠른 시작

### 1. 기본 사용

```python
from cookiie_brain_engine import CookiieBrainEngine
from brain_core.global_state import GlobalState
import numpy as np

# 통합 엔진 생성
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

# episodes 추가
state.set_extension("episodes", [...])

# 실행
result = brain.update(state)
```

### 2. 통합 테스트 데모 실행

```bash
cd /Users/jazzin/Desktop/00_BRAIN/CookiieBrain
python examples/integration_test_demo.py
```

---

## 📚 주요 문서

### 인수인계
- `HANDOVER_COMPLETE.md` - 완전 인수인계 문서 ⭐
- `HANDOVER_DOCUMENT.md` - 기본 인수인계 문서

### 개념
- `CONCEPT_ROTATION_ORBIT.md` - 자전과 공전 개념
- `Phase_A/MATHEMATICAL_FOUNDATION.md` - 수학적 기초

### 분석
- `STRUCTURAL_REVIEW.md` - 구조 점검
- `RESULT_ANALYSIS.md` - 테스트 결과 분석

### 로드맵
- `REVISED_ROADMAP.md` - 재정렬된 로드맵

---

## 🎯 현재 상태

- ✅ 기본 통합 완료
- ✅ 통합 테스트 데모 작성
- ✅ Phase A 개념 정리 완료
- ⚠️ Phase A 구현 진행 중

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.4


