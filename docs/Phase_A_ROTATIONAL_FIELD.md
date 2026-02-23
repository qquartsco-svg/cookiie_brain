# Phase A: 위상 생성 (Rotational Field)

**작성일**: 2026-02-21  
**버전**: 0.1.4

---

## 🎯 목표

**curl(g) ≠ 0인 성분을 주입하여 순환 운동(자전) 가능하게 만들기**

---

## 📐 수식 정리

### 현재 시스템

**필드 정의**:
```
g(x) = -∇E(x)
```

**특성**:
```
curl(g) = curl(-∇E) = 0  (보존력)
```

**결과**: 순환 운동 불가능

---

### 목표 시스템

**필드 정의**:
```
g(x) = -∇E(x) + R(x)
```

**특성**:
```
curl(g) = curl(-∇E) + curl(R) = curl(R) ≠ 0
```

**결과**: 순환 운동 가능

---

### Rotational Component 수식

#### 2D 회전 필드

**기본 형태**:
```
R(x) = ω × (x - x_center)
```

**2D에서**:
```
R(x) = ω * [-y, x]  (x_center = [0, 0] 기준)
```

**일반화**:
```
R(x) = ω * strength * [-r_y, r_x] / (||r||^2 + ε)
여기서:
  r = x - x_center
  r_x, r_y = r의 x, y 성분
  ω = 회전 방향 (+1 또는 -1)
  strength = 회전 강도
  ε = 수치 안정성 (작은 값)
```

---

### 폴(Pole) 정의

**폴의 역할**:
- 회전의 중심점
- Rotational field의 기준점

**수학적 정의**:
```
x_pole = 회전 중심 좌표
R(x) = f(x - x_pole)  (폴 기준 회전)
```

**폴 위치 결정**:
1. **에너지 최소점**: 우물 중심
2. **임의 지정**: 사용자 정의
3. **동적 계산**: 상태에 따라 변화

---

## 🔬 달/위성의 필요성 분석

### 물리적 배경

**지구-달 시스템**:
- 지구의 자전은 달의 조석력에 의해 영향을 받음
- 달은 자전을 안정화시키거나 조절하는 역할
- 하지만 자전 자체를 만드는 것은 아님

---

### 수학적 분석

#### 자전만 필요한 경우

**필요한 것**:
```
F(x) = -∇E(x) + R(x)  (curl(R) ≠ 0)
```

**결론**: 달/위성 없이도 자전 가능

---

#### 달/위성이 추가되면?

**필드 정의**:
```
g(x) = -∇E(x) + R(x) + G_moon(x)
```

**달의 중력장**:
```
G_moon(x) = -G * M_moon * (x - x_moon) / ||x - x_moon||^3
```

**효과**:
1. **조석력**: 자전 속도 조절
2. **안정화**: 자전 축 안정화
3. **복잡한 동역학**: 더 풍부한 패턴

**결론**: 
- 자전 자체를 만드는 필수 요소는 아님
- 하지만 자전을 안정화/조절하는 데 유용

---

### 구현 전략

#### 옵션 1: 자전만 (간단)

**구현**:
```
g(x) = -∇E(x) + R(x)
```

**장점**: 간단, 빠른 구현  
**단점**: 안정성 낮을 수 있음

---

#### 옵션 2: 자전 + 달 (안정)

**구현**:
```
g(x) = -∇E(x) + R(x) + G_moon(x)
```

**장점**: 안정성 높음, 복잡한 동역학  
**단점**: 복잡도 증가

---

#### 권장: 단계적 접근

1. **Phase A-1**: 자전만 구현 (R(x) 추가)
2. **Phase A-2**: 달 추가 (안정화)

---

## 🏗️ 구현 계획

### A-1. 폴(Pole) 정의

**코드 구조**:
```python
class Pole:
    def __init__(self, position, rotation_direction=1, strength=1.0):
        self.position = np.array(position)  # 폴 위치
        self.rotation_direction = rotation_direction  # +1 또는 -1
        self.strength = strength  # 회전 강도
```

---

### A-2. Rotational Field 생성

**코드 구조**:
```python
def create_rotational_field(pole, epsilon=1e-6):
    """회전 성분 생성 (curl ≠ 0)"""
    def R(x):
        r = x - pole.position
        r_norm_sq = np.dot(r, r) + epsilon
        
        # 2D 회전: R = [-y, x] 형태
        if len(r) == 2:
            R_vec = np.array([-r[1], r[0]])
        else:
            # 3D 이상: 외적 사용
            # 단순화: 2D 투영
            R_vec = np.array([-r[1], r[0], 0])[:len(r)]
        
        return pole.rotation_direction * pole.strength * R_vec / r_norm_sq
    
    return R
```

---

### A-3. Gradient + Rotational 합성

**코드 구조**:
```python
def create_combined_field(potential_func, field_func, rotational_func):
    """Gradient + Rotational 합성"""
    def combined_field(x):
        gradient = field_func(x) if field_func else -compute_gradient(potential_func, x)
        rotational = rotational_func(x)
        return gradient + rotational
    
    return combined_field
```

---

### A-4. PotentialFieldEngine 확장

**수정 사항**:
```python
class PotentialFieldEngine:
    def __init__(self, potential_func, field_func, rotational_func=None, pole=None):
        # ... 기존 코드 ...
        self.rotational_func = rotational_func
        self.pole = pole
    
    def _compute_field(self, x):
        # 기존 gradient
        gradient = self.field_func(x) if self.field_func else -compute_gradient(...)
        
        # Rotational component 추가
        if self.rotational_func:
            rotational = self.rotational_func(x)
            return gradient + rotational
        
        return gradient
```

---

### A-5. 달/위성 추가 (선택적)

**코드 구조**:
```python
class Moon:
    def __init__(self, position, mass, G=1.0):
        self.position = np.array(position)
        self.mass = mass
        self.G = G
    
    def gravity_field(self, x):
        """달의 중력장"""
        r = x - self.position
        r_norm = np.linalg.norm(r) + 1e-10
        return -self.G * self.mass * r / (r_norm**3)
```

---

## 📊 검증 방법

### A-1. Curl 계산 확인

**코드**:
```python
def verify_curl(field_func, x_range, y_range):
    """curl 계산으로 회전 성분 확인"""
    # curl = ∂F_y/∂x - ∂F_x/∂y
    # curl ≠ 0이면 회전 성분 있음
    pass
```

---

### A-2. 궤도 확인

**코드**:
```python
def verify_orbit(field_func, initial_state, n_steps):
    """궤도가 닫히는지 확인"""
    # 초기 위치로 돌아오는지 확인
    pass
```

---

### A-3. 위상 공간 확인

**코드**:
```python
def plot_phase_space(states):
    """위상 공간에서 순환 패턴 확인"""
    # (x, v) 공간에서 순환 패턴 시각화
    pass
```

---

## 🎯 구현 단계

### Step 1: 폴 정의 및 Rotational Field 생성

**작업**:
1. Pole 클래스 구현
2. create_rotational_field 함수 구현
3. 기본 테스트

**예상 시간**: 3-5일

---

### Step 2: PotentialFieldEngine 확장

**작업**:
1. rotational_func 파라미터 추가
2. _compute_field 수정
3. 기존 코드와 호환성 확인

**예상 시간**: 2-3일

---

### Step 3: 통합 테스트

**작업**:
1. curl 계산 확인
2. 궤도 확인
3. 위상 공간 시각화

**예상 시간**: 2-3일

---

### Step 4: 달/위성 추가 (선택적)

**작업**:
1. Moon 클래스 구현
2. 중력장 합성
3. 안정성 검증

**예상 시간**: 2-3일

---

## 📝 요약

### 핵심 수식

```
목표: g(x) = -∇E(x) + R(x)
조건: curl(R) ≠ 0
결과: 순환 운동 가능
```

### 달/위성 필요성

- ❌ 자전을 만드는 필수 요소 아님
- ✅ 자전을 안정화/조절하는 데 유용
- 권장: 단계적 접근 (자전 먼저, 달 나중에)

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.4


