# Phase A: 위상 생성 (Rotational Field)

**버전**: 0.1.4

---

## 🎯 목표

**curl(g) ≠ 0인 성분을 주입하여 순환 운동(자전) 가능하게 만들기**

---

## 📐 핵심 수식

### Rotational Component

```
R(x) = ω * strength * [-r_y, r_x] / (||r||^2 + ε)

여기서:
  r = x - pole.position
  ω = pole.rotation_direction (+1 또는 -1)
  strength = pole.strength
  ε = epsilon (수치 안정성)
```

### Combined Field

```
g(x) = -∇E(x) + R(x)  (curl(R) ≠ 0)
```

---

## 🏗️ 구조

### 모듈

- `rotational_field.py`: Rotational field 생성
- `moon.py`: 달/위성 중력장
- `__init__.py`: 모듈 초기화

---

## 📖 사용법

### 기본 사용 (Rotational Field만)

```python
from Phase_A import Pole, create_rotational_field, create_combined_field
import numpy as np

# 폴 정의
pole = Pole(
    position=np.array([0.0, 0.0]),
    rotation_direction=1,  # 반시계
    strength=1.0
)

# Rotational field 생성
R = create_rotational_field(pole)

# Gradient field (기존)
def gradient_field(x):
    return -compute_gradient(potential_func, x)

# 합성 필드
combined_field = create_combined_field(gradient_field, R)
```

### 달 추가 (선택적)

```python
from Phase_A import Moon, create_moon_gravity_field, create_field_with_moon

# 달 정의
moon = Moon(
    position=np.array([2.0, 0.0]),
    mass=0.1,
    G=1.0
)

# 달의 중력장
G_moon = create_moon_gravity_field(moon)

# 합성 필드 (Gradient + Rotational + Moon)
field_with_moon = create_field_with_moon(
    gradient_field,
    R,
    G_moon
)
```

---

## 🔬 달/위성 필요성 분석

### 결론

- ❌ 자전을 만드는 필수 요소 아님
- ✅ 자전을 안정화/조절하는 데 유용
- 권장: 단계적 접근 (자전 먼저, 달 나중에)

---

## 📊 검증 방법

### Curl 확인

```python
from Phase_A import compute_curl_2d

curl = compute_curl_2d(combined_field, test_point)
# curl ≠ 0이면 회전 성분 있음
```

### Rotational Component 확인

```python
from Phase_A import verify_rotational_component

has_rotation = verify_rotational_component(
    combined_field,
    test_points
)
```

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.4


