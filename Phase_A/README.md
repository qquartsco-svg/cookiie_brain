# Phase A: 자전 (Rotational Field)

**정적 기억 우물에 회전(리듬)을 부여하는 모듈**

```
Version : 0.2.0
Author  : GNJz (Qquarts)
```

---

## 왜 자전이 필요한가

퍼텐셜 우물만 있으면 상태는 골짜기 바닥으로 수렴해서 멈춥니다.
현실의 뇌 상태는 멈추지 않습니다 — 수면 중에도 뉴런은 리듬을 유지합니다.

자전을 넣으면:
- 상태가 골짜기 안에서 **계속 회전** → 위상(phase)이 생김
- 에너지는 변하지 않음 → 시스템이 발산하거나 소멸하지 않음
- "기억에 머무르면서도 고정되지 않는" 동적 상태가 가능해짐

---

## 두 가지 회전 방식

### 1. 코리올리형 (에너지 보존) — 주력

힘을 속도에 수직으로 건다. 방향만 바뀌고 에너지는 보존된다.

```
R(x, v) = ωJv

왜 에너지가 보존되나:
  힘이 한 일 = v · F = v · (ωJv) = ω(v'Jv) = 0
  J는 반대칭 행렬 → v'Jv는 항상 0 → 회전항이 일을 하지 않음
```

사용처: PotentialFieldEngine의 `omega_coriolis` 파라미터로 활성화.
적분기가 Strang splitting + exact rotation으로 자동 전환되어 수치적으로도 에너지 보존.

### 2. Pole형 (위치 의존, 에너지 비보존)

공간의 특정 위치(pole) 주변에 소용돌이를 만든다.

```
R(x) = ωJ(x - x_pole)

주의: v · R(x) ≠ 0 (일반적) → 에너지 비보존
```

사용처: 소용돌이 장, 탐색 루프, 순환 편향 등 에너지 제어를 별도로 하는 경우.

---

## 파일 구조

```
Phase_A/
├── rotational_field.py    # 회전 생성기 (코리올리형 + pole형)
├── moon.py                # 위성 중력장 (외부 섭동용)
├── verify_math.py         # 수학 검증 (부호, 직교성)
├── __init__.py            # 모듈 export
└── docs/                  # 작업 기록, 수학 문서
```

---

## 사용법

### 코리올리형 자전 (권장)

CookiieBrainEngine에서 활성화:

```python
brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    potential_field_config={
        "enable_phase_a": True,
        "phase_a_mode": "minimal",
        "phase_a_omega": 1.0,
    },
)
```

또는 PotentialFieldEngine 직접 사용:

```python
engine = PotentialFieldEngine(
    potential_func=V,
    field_func=g,
    omega_coriolis=1.0,     # 이것만 넣으면 자전 ON
    rotation_axis=(0, 1),
    dt=0.005,
)
```

### Pole형 소용돌이

```python
from Phase_A import Pole, create_rotational_field

pole = Pole(position=np.array([0.0, 0.0]), rotation_direction=1, strength=1.0)
R = create_rotational_field(pole)
```

### 외부 중력장 (위성/달)

기본 우물 외에 추가 끌어당김을 합성. 궤도를 변형/섭동시키는 실험용.

```python
from Phase_A import Moon, create_moon_gravity_field, create_field_with_moon

moon = Moon(position=np.array([2.0, 0.0]), mass=0.1)
G_moon = create_moon_gravity_field(moon)
field = create_field_with_moon(gradient_func, rotational_func, G_moon)
```

---

## 검증

### 자전 검증 (4항목 ALL PASS)

```bash
python examples/phase_a_minimal_verification.py
```

| 항목 | 내용 | 기준 |
|------|------|------|
| v · R = 0 | 코리올리 직교성 | 수치 오차 < 1e-12 |
| 궤도 회전 | 자전 효과 존재 | 0.5바퀴 이상 |
| 에너지 보존 | Strang splitting | rel_drift < 0.01% |
| 궤도 유계 | 발산하지 않음 | r_max < 3.0 |

### 수학 기본 검증

```bash
python Phase_A/verify_math.py
```

| 항목 | 내용 |
|------|------|
| 부호 | field(x) = -∇V(x) 확인 |
| 직교성 | r · R(x) = 0 (pole형 기하학적 직교) |

---

## 현재 상태

| 항목 | 상태 |
|------|------|
| 코리올리형 자전 (ωJv) | 완료, 검증 통과 |
| Strang splitting 적분 | 완료, 에너지 보존 확인 |
| Pole형 소용돌이 | 코드 존재, 엔진 통합 가능 |
| 위성장 (moon.py) | 코드 존재, 엔진 미통합 |

---

## 단계 로드맵

```
1. 정적 퍼텐셜 (우물)         ← 완료
2. 자전 (내부 리듬)           ← 완료 (지금 여기)
3. 공전 (다중 중심 상호작용)   ← 미착수
4. 요동 (확률적 불확정성)      ← 미착수
```

> 고전 구조가 먼저. 확률은 마지막에 얹는다.
> 구조가 있어야 요동의 의미가 생긴다.

상세: [STAGES_SPIN_ORBIT_FLUCTUATION.md](STAGES_SPIN_ORBIT_FLUCTUATION.md)
