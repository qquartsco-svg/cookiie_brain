# Phase A 구현 계획: 수학적 정확성 기반

**작성일**: 2026-02-21  
**버전**: 0.1.4

---

## 🎯 목표

**수학적으로 정확한 자전 구현**

**핵심 수식**:
```
F(x) = -∇E(x) + ω J x
```

**조건**:
```
∇ × (ω J x) ≠ 0  (회전 성분 존재)
```

---

## 📐 수학적 정의

### 1. 상태 공간

```
x ∈ ℝⁿ
```

### 2. 에너지

```
E(x) = -(1/2) x^T W x - b^T x
```

### 3. 보존력

```
F_conservative(x) = -∇E(x)
특성: ∇ × F_conservative = 0
```

### 4. 회전력

```
F_rotational(x) = ω J x
여기서 J는 반대칭 행렬
특성: ∇ × F_rotational ≠ 0
```

### 5. 합성 힘

```
F(x) = -∇E(x) + ω J x
```

---

## 🔄 동역학

### 1차 형식

```
ẋ = -∇E(x) + ω J x
```

### 2차 형식 (현재 시스템)

```
ẍ = -∇E(x) + ω J ẋ
```

### 안정화된 자전

```
ẋ = -∇E(x) + ω J x - γ x
조건: |ω| > γ
```

---

## 🏗️ 구현 단계

### Step 1: 반대칭 행렬 생성 ✅

**구현**:
```python
def create_skew_symmetric_matrix(n, axis=[0, 1]):
    J = np.zeros((n, n))
    J[axis[0], axis[1]] = -1
    J[axis[1], axis[0]] = 1
    return J
```

**상태**: ✅ 완료

---

### Step 2: 회전 항 생성 ✅

**구현**:
```python
def create_rotational_field(pole, use_simple_form=True):
    if use_simple_form:
        # R(x) = ω * J * (x - x_pole)
        J = create_skew_symmetric_matrix(n)
        return lambda x: pole.rotation_direction * pole.strength * (J @ (x - pole.position))
```

**상태**: ✅ 완료

---

### Step 3: PotentialFieldEngine 확장 ⚠️

**필요한 수정**:
1. `rotational_func` 파라미터 추가
2. `pole` 파라미터 추가
3. `_compute_field()` 수정:
   ```python
   def _compute_field(self, x):
       gradient = self.field_func(x)
       if self.rotational_func:
           rotational = self.rotational_func(x)
           return gradient + rotational
       return gradient
   ```

**상태**: ⚠️ 진행 필요

---

### Step 4: 안정화 항 추가 (선택적)

**구현**:
```python
# 감쇠 항 추가
ẋ = -∇E(x) + ω J x - γ x
```

**조건**: `|ω| > γ` (자전 유지)

**상태**: ⚠️ 설계 필요

---

## 🔬 검증 방법

### 1. Curl 계산

**수식**:
```
curl = ∇ × F
```

**2D에서**:
```
curl = ∂F_y/∂x - ∂F_x/∂y
```

**검증**:
```python
curl = compute_curl_2d(combined_field, test_point)
assert abs(curl) > threshold  # curl ≠ 0 확인
```

---

### 2. Limit Cycle 확인

**검증**:
- 궤도가 닫히는지 확인
- 주기성 확인
- 안정성 확인

---

### 3. 위상 공간 확인

**검증**:
- (x, v) 공간에서 순환 패턴 확인
- 위상 구조 확인

---

## 📊 달/위성 필요성 최종 결론

### 물리적 사실

- ✅ 행성은 달 없이도 자전
- ✅ 자전은 각운동량 때문
- ❌ 위성은 자전의 원인 아님

### 수학적 분석

**자전 발생 조건**:
```
∇ × F ≠ 0
```

**위성 필요 조건**:
- 세차 안정화
- 주기 동기화
- 다중 주파수 결합

**결론**:
- ❌ 자전에는 필요 없음
- ✅ 복잡 리듬에는 도움됨

---

## 🎯 구현 우선순위

### Phase A-1: 기본 자전 (최우선)

**구현**:
```
F(x) = -∇E(x) + ω J x
```

**검증**:
- curl ≠ 0 확인
- 순환 운동 확인

**예상 시간**: 2-3일

---

### Phase A-2: 안정화 (선택적)

**구현**:
```
F(x) = -∇E(x) + ω J x - γ x
```

**조건**: `|ω| > γ`

**예상 시간**: 1-2일

---

### Phase A-3: 달 추가 (선택적)

**구현**:
```
F(x) = -∇E(x) + ω J x + F_tidal(x, t)
```

**예상 시간**: 1-2일

---

## ✅ 최종 정리

### 수학적 정의

- ✅ 상태 공간: x ∈ ℝⁿ
- ✅ 에너지: E(x) = -(1/2) x^T W x - b^T x
- ✅ 보존력: F = -∇E (curl = 0)
- ✅ 회전력: R = ω J x (curl ≠ 0)
- ✅ 합성: F = -∇E + ω J x

### 구현 방향

- ✅ 단일 코어 자전 먼저
- ❌ 다중 코어 공전은 나중에
- ❌ 달은 선택적 (안정화용)

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.4


