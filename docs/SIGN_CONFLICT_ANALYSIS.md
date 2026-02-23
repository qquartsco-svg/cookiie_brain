# 부호/정의 충돌 분석

**작성일**: 2026-02-21  
**버전**: 0.1.2

---

## 🔎 확인된 문제점

### 1. 에너지 감소 계산식 오류 ✅ 확인됨

**위치**: `integration_test_demo.py:264`

**현재 코드**:
```python
print(f"   에너지 감소: {initial_energy - final_energy:.6f}")
```

**실제 계산**:
- initial_energy = -0.102363
- final_energy = -0.101821
- 계산: -0.102363 - (-0.101821) = **-0.000542**

**문제점**:
- 이건 "감소량"이 아니라 "변화량"이고, 부호가 반대
- 올바른 계산: `final_energy - initial_energy` = **+0.000542** (증가)

**결론**: 라벨/계산식 오류 확인됨

---

### 2. 필드 정의 확인 ✅

**위치**: `well_formation_integration.py:114-128`

**문서 정의**:
```
g(x) = -∇E(x) = Wx + b
```

**실제 구현**:
```python
def field(x: np.ndarray) -> np.ndarray:
    return np.dot(W, x) + b  # Wx + b
```

**확인 필요**: `Wx + b`가 정말 `-∇E(x)`인가?

**Hopfield 에너지**:
```
E(x) = -(1/2) * x^T W x - b^T x
```

**기울기 계산**:
```
∇E(x) = -Wx - b
```

**따라서**:
```
-∇E(x) = -(-Wx - b) = Wx + b  ✅
```

**결론**: 필드 정의는 **정확함** (`g(x) = Wx + b = -∇E(x)`)

---

### 3. 업데이트 방향 확인 ✅

**위치**: `potential_field_engine.py:172-178`

**현재 구현**:
```python
# 속도 업데이트
v_new = v + self.dt * a  # a = g

# 위치 업데이트
x_new = x + self.dt * v_new
```

**분석**:
- `a = g = -∇E(x)` (필드 = 가속도)
- `v_new = v + dt * (-∇E(x))` (속도는 에너지 감소 방향)
- `x_new = x + dt * v_new` (위치는 속도 방향)

**문제점**:
- 이건 **2차 동역학** (위치 + 속도)
- 순수 gradient descent가 아님
- 운동 에너지가 포함되어 있음

**결론**: 업데이트 방향은 **정상** (2차 동역학 시스템)

---

### 4. 에너지 정의 확인 ✅

**위치**: `well_formation_integration.py:63-84` (potential)
**위치**: `potential_field_engine.py:183-186` (energy)

**Potential 함수**:
```python
V(x) = E(x) = -(1/2) * x^T W x - b^T x
```

**총 에너지 계산**:
```python
new_state.energy = kinetic_energy + V
                 = (1/2) * v^2 + V(x)
```

**분석**:
- `V(x) = E(x)` ✅ (정의 일치)
- 총 에너지 = 운동 에너지 + 퍼텐셜 에너지 ✅ (정상)

**결론**: 에너지 정의는 **정확함**

---

## 🎯 핵심 문제

### 발견된 문제

1. ✅ **에너지 감소 계산식 오류**: `initial - final` 대신 `final - initial`이어야 함
2. ✅ **에너지 증가는 정상**: 2차 동역학 시스템에서 운동 에너지 증가로 인한 과도기 현상
3. ⚠️ **수렴 속도**: 100 스텝으로는 부족 (경계 케이스)

### 정상인 부분

1. ✅ 필드 정의: `g(x) = -∇E(x) = Wx + b` 정확
2. ✅ 업데이트 방향: 2차 동역학 시스템으로 정상 작동
3. ✅ 에너지 정의: `V(x) = E(x)` 정확

---

## 🔧 수정 필요 사항

### 즉시 수정

1. **에너지 감소 계산식**:
```python
# 현재 (잘못됨)
print(f"   에너지 감소: {initial_energy - final_energy:.6f}")

# 수정 (올바름)
energy_change = final_energy - initial_energy
if energy_change < 0:
    print(f"   에너지 감소: {abs(energy_change):.6f}")
else:
    print(f"   에너지 증가: {energy_change:.6f}")
```

### 개선 사항

2. **장기 시뮬레이션**: 스텝 수를 500-1000으로 증가
3. **에너지 분리 추적**: 운동 에너지와 퍼텐셜 에너지를 분리하여 출력

---

## 📊 결론

### 부호/정의 충돌은 없음 ✅

- 필드 정의: 정확 (`g = -∇E`)
- 에너지 정의: 정확 (`V = E`)
- 업데이트 방향: 정상 (2차 동역학)

### 실제 문제

1. **계산식/라벨 오류**: 에너지 감소 계산식이 반대
2. **과도기 현상**: 운동 에너지 증가로 인한 일시적 에너지 증가
3. **수렴 속도**: 스텝 수 부족

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.2

