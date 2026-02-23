# CookiieBrain 작업 로그

> 모든 구현/수정 이력을 시간순으로 기록한다.
> 각 항목: 날짜, 커밋, 변경 파일, 변경 내용, 검증 결과.

---

## 2026-02-21 — Phase A 자전 구현 + 엔진 버그 수정

### 작업 내용
- PotentialFieldEngine에 Strang splitting + exact rotation 구현
- 코리올리형 자전 `R(v) = ωJv` (에너지 보존)
- extension에 저장되는 gradient가 이전 위치 기준이던 버그 수정 (`x` → `x_new`)
- CookiieBrainEngine `well_changed` 로직 수정 (`id()` 비교 → `np.array_equal`)

### 변경 파일
| 파일 | 변경 |
|------|------|
| `potential_field_engine.py` | Strang splitting, exact rotation, gradient 버그 수정 |
| `cookiie_brain_engine.py` | well_changed 로직 수정 |
| `Phase_A/rotational_field.py` | 코리올리형 + pole형 회전 필드 |
| `Phase_A/moon.py` | 위성 중력장 |
| `Phase_A/verify_math.py` | 수학 검증 |

### 검증
- `phase_a_minimal_verification.py`: ALL PASS
  - v·R=0 (직교): PASS
  - 궤도 회전: PASS
  - 에너지 보존: PASS (rel_drift < 0.01%)
  - 궤도 유계: PASS

### PHAM 서명
- `pham_chain_potential_field_engine.json`: 블록 1 (2026-02-21 03:20)

---

## 2026-02-23 — Phase B 공전 구현

### 작업 내용
- 가우시안 합성 다중 우물 퍼텐셜 설계 및 구현
  - `V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))`
- 장벽/안장점 분석 기능 (`find_saddle_between`, `barrier_height`, `min_energy_for_orbit`)
- 3-우물 삼각형 배치 + ωJv → 순환 궤도(공전) 검증
- 공전 조건 발견: 우물 3개 비직선 배치 + 적절한 ω + E > V_saddle

### 변경 파일
| 파일 | 변경 | 커밋 |
|------|------|------|
| `Phase_B/__init__.py` | 신규 생성 | `2009baa` |
| `Phase_B/multi_well_potential.py` | 신규 생성 | `2009baa` |
| `Phase_B/README.md` | 신규 생성 → 공전 결과 반영 | `2009baa`, `f64dcf5` |
| `examples/phase_b_orbit_verification.py` | 신규 생성 → 3-우물 순환 검증 | `2009baa`, `f64dcf5` |
| `README.md` | 깨진 링크 수정, Phase B 반영, 상태 테이블 업데이트 | `2009baa`, `abb605c`, `f64dcf5` |

### 검증
- `phase_b_orbit_verification.py`: ALL PASS
  - 다중 우물 구조: PASS (V_well=-2.006, V_saddle=-0.801)
  - 장벽 양수: PASS (barrier=1.205)
  - 전이 가능성: PASS (3우물 방문, 전이 39회)
  - 순환 궤도(공전): PASS (8순환, 주방향 2→0→1 88%)
  - 에너지 보존: PASS (rel_drift=5.81e-06, 0.0006%)
  - E<V_saddle 갇힘: PASS (전이 0회)

### 파라미터 (검증 시)
```
우물: 3개 정삼각형 (r=2.5, A=2.0, σ=1.2)
omega: 0.3
dt: 0.005
n_steps: 60000
```

### PHAM 서명
- ⏳ 미서명 (아래 명령어로 실행 필요)

---

## 2026-02-23 — cookiie_brain_engine.py 버그 수정

### 작업 내용
- **치명 1**: `POTENTIAL_FIELD_AVAILABLE=False`일 때 `create_potential_from_wells(None)` 호출 크래시
  - `__init__`에 `POTENTIAL_FIELD_AVAILABLE` 가드 추가
  - `update()`에서 `enable_potential_field and POTENTIAL_FIELD_AVAILABLE` 이중 가드
- **주의 1**: Cerebellum 섹션 `state_vector` 짝수 길이 검증 추가
- **주의 2**: `phase_a_mode == "pole"` 명시적 검사 (오타 방지)
- **주의 3**: `create_minimal_rotational_field` 미사용 import 제거

### 변경 파일
| 파일 | 변경 | 커밋 |
|------|------|------|
| `cookiie_brain_engine.py` | 치명 버그 수정 + 방어 코드 | `a61f165` |
| `cookiie_brain_engine.py` | 이중 가드 (init + update) | `76d0f56` |

### PHAM 서명
- ⏳ 미서명

---

## PHAM 서명 상태

| 파일 | 서명 상태 | 체인 파일 |
|------|----------|----------|
| `potential_field_engine.py` | ✔ 서명됨 (2026-02-21) | `pham_chain_potential_field_engine.json` |
| `CONCEPT.md` | ✔ 서명됨 | `pham_chain_CONCEPT.json` |
| `grid_analyzer.py` | ✔ 서명됨 | `pham_chain_grid_analyzer.json` |
| `README.md (PFE)` | ✔ 서명됨 | `pham_chain_README.json` |
| `multi_well_potential.py` | ⏳ 미서명 | — |
| `cookiie_brain_engine.py` | ⏳ 미서명 | — |
| `phase_b_orbit_verification.py` | ⏳ 미서명 | — |
| `rotational_field.py` | ⏳ 미서명 | — |
| `moon.py` | ⏳ 미서명 | — |
