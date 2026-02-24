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
- ✔ 서명됨 (2026-02-24) — 하단 PHAM 서명 상태 참조

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
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-23 — WellFormation → Gaussian 브릿지 구현

### 작업 내용
- WellFormation 결과(W, b)를 GaussianWell 파라미터로 자동 변환하는 브릿지 모듈 구현
  - center: mean(post_activity) 기반 (pattern 모드, b=0에서도 동작)
  - amplitude: spectral_radius(W) × scale
  - sigma: scale / √(mean|λ_neg|)
- WellRegistry: 우물 누적 저장소, 거리 기반 중복 제거(병합)
- cookiie_brain_engine.py 통합: registry 누적 + wells≥3이면 Gaussian 모드 자동 전환

### 변경 파일
| 파일 | 변경 | 상태 |
|------|------|------|
| `Phase_B/well_to_gaussian.py` | 신규 생성 (브릿지 코어) | 신규 |
| `Phase_B/__init__.py` | well_to_gaussian export 추가 | 수정 |
| `Phase_B/README.md` | 브릿지 문서 추가, 상태 테이블 업데이트 | 수정 |
| `cookiie_brain_engine.py` | Phase_B import, WellRegistry 생성, update() Gaussian 분기 | 수정 |
| `examples/bridge_verification.py` | 신규 생성 (검증 스크립트) | 신규 |

### 검증
- `bridge_verification.py`: ALL PASS
  - 단일 변환 정확성: PASS (center error 0.024)
  - Registry 누적 (3개): PASS
  - 중복 제거 (dedup): PASS
  - 장벽 양수: PASS (barrier ≈ 1.96)
  - 공전 재현: PASS (5순환, 18전이, 3우물 방문)

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-23 — 에너지 주입/소산 구현

### 작업 내용
- PotentialFieldEngine에 감쇠(`-γv`)와 외부 주입(`I(x,v,t)`) 기능 추가
- 수식: `ẍ = -∇V(x) + ωJv - γv + I(x,v,t)`
- 에너지 밸런스: `dE/dt = -γ||v||² + v·I`
- 적분: Modified Strang splitting (D-S-K-R-K-S-D)
  - 감쇠: exp(-γdt/2) 정확해 (대칭 래핑, 무조건 안정)
  - 주입: kick에 포함 (gradient와 동일 평가점, 2차 정확도)
  - γ=0, I=None이면 기존 Strang splitting과 동일 (하위 호환)
- cookiie_brain_engine.py에 gamma/injection_func config 전달 경로 추가

### 변경 파일
| 파일 | 변경 | 위치 |
|------|------|------|
| `potential_field_engine.py` | gamma, injection_func 파라미터, Modified Strang splitting | PotentialFieldEngine (별도 레포) |
| `cookiie_brain_engine.py` | gamma/injection_func config 전달 | CookiieBrain |
| `examples/dissipation_injection_verification.py` | 신규 생성 (검증 스크립트) | CookiieBrain |

### 검증
- `dissipation_injection_verification.py`: ALL PASS
  - 하위 호환 (γ=0): PASS (E_rel_drift 9.25e-06, 14전이)
  - 감쇠→갇힘 (γ=0.02): PASS (E: 0.699→-1.900, 후반 전이 0)
  - 주입→전이 (pulse): PASS (E<V_saddle→3우물 방문)
  - 에너지 밸런스: PASS (correlation 0.999995, ratio 1.0001)
- Phase B 공전 검증: ALL PASS (하위 호환 확인)

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 — Phase C 요동 (Fluctuation) 구현

### 작업 내용
- PotentialFieldEngine에 Langevin noise (σξ(t)) 구현
  - `noise_sigma` 파라미터: 노이즈 세기 (σ=0이면 기존 결정론적 동작)
  - `noise_seed` 파라미터: 재현 가능한 결과를 위한 난수 시드
- Strang splitting의 D 스텝을 O-U exact 반스텝으로 확장
  - O(h): v → e^{-γh}v + σ√((1-e^{-2γh})/(2γ))·ξ  (감쇠+노이즈 정확 결합)
  - γ→0 limit: σ√h (표준 Wiener), σ=0이면 기존 D 스텝과 동일 (하위 호환)
- symplectic Euler에도 동일한 O-U exact 노이즈 추가
- cookiie_brain_engine.py에 noise_sigma/noise_seed config 전달 경로 추가

### 변경 파일
| 파일 | 변경 | 위치 |
|------|------|------|
| `potential_field_engine.py` | noise_sigma, noise_seed, _rng, O-U 반스텝 | PotentialFieldEngine (별도 레포) |
| `cookiie_brain_engine.py` | noise_sigma/noise_seed config 전달, 버전 0.3.0 | CookiieBrain |
| `examples/fluctuation_verification.py` | 신규 생성 (검증 스크립트) | CookiieBrain |

### 검증
- `fluctuation_verification.py`: ALL PASS
  - 하위 호환 (σ=0 결정론): PASS (시드 무관 동일 궤적, E drift 2.58e-06)
  - Kramers 탈출 (σ=0.25, γ=0.01): PASS (탈출 10/10, 100%)
  - 통계적 비편향 (free particle): PASS (bias ratio 0.066)
  - 감쇠+노이즈 정상 상태: PASS (E bounded, std=0.25)

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 — 전체 개념/상태 문서 정리 (Phase C 포함)

### 작업 내용
- 프로젝트 전체 개념, 물리 수식, 구현 상태, 다음 방향을 하나의 문서로 정리
- 새로 합류하는 사람이 이 문서 하나로 전체를 파악할 수 있도록 작성
- 비유 테이블, 전체 운동 방정식, 각 Phase 개념/수식/검증, 파이프라인, 설계 원칙, 용어 정리 포함

### 변경 파일
| 파일 | 변경 | 상태 |
|------|------|------|
| `docs/FULL_CONCEPT_AND_STATUS.md` | 신규 생성 (전체 개념 + 현재 상태) | 신규 |
| `docs/WORK_LOG.md` | 이 항목 추가 | 수정 |

---

## 2026-02-24 — Phase C v2: FDT (요동-소산 정리) 구현

### 작업 내용
- PotentialFieldEngine에 `temperature`, `mass` 파라미터 추가
- `noise_sigma`를 property로 전환, FDT 자동 계산: σ² = 2γT/m (kB=1)
- `noise_mode` property 추가: "fdt" / "manual" / "off"
- cookiie_brain_engine.py에 temperature/mass config 전달 경로 추가
- 모드 우선순위: noise_sigma > 0 → manual | temperature+γ → fdt | else → off
- FDT 도입으로 σ, γ, T가 열역학적으로 결합 → Boltzmann 정상 분포 보장

### 변경 파일
| 파일 | 변경 | 위치 |
|------|------|------|
| `potential_field_engine.py` | temperature, mass 파라미터, noise_sigma property (FDT), noise_mode | PotentialFieldEngine (별도 레포) |
| `cookiie_brain_engine.py` | temperature/mass config 전달 | CookiieBrain |
| `examples/fdt_verification.py` | 신규 생성 (FDT 검증 5항목) | CookiieBrain |
| `Phase_C/README.md` | FDT 섹션 추가, 사용법 업데이트 | CookiieBrain |
| `docs/FULL_CONCEPT_AND_STATUS.md` | FDT 수식/검증 추가 | CookiieBrain |
| `Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md` | 요동 상태 업데이트 | CookiieBrain |

### 검증
- `fdt_verification.py`: ALL PASS (5/5)
  - 하위 호환 (temperature=None): PASS
  - FDT σ 계산 (σ²=2γT/m): PASS (오차 0)
  - Manual override (noise_sigma 우선): PASS
  - Boltzmann 등분배 (⟨½v²⟩=T/2): PASS (오차 0.6%)
  - γ=0 안전장치: PASS (σ=0)
- `fluctuation_verification.py`: ALL PASS (하위 호환 확인)

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 — 문서 보완 + 엔진 점검 + 영어 문서

### 작업 내용
- README.md 운동 방정식 `m` 누락 보완 (`ẍ → m ẍ`, FDT 도입 후 m이 의미를 가지므로)
- 전체 검증 스크립트 6개 실행 → ALL PASS 확인 (엔진 상태 정상)
- 영어 문서 2개 신규 생성:
  - `docs/FULL_CONCEPT_AND_STATUS_EN.md` (전체 개념 영어판)
  - `Phase_C/README_EN.md` (Phase C 영어판)
- README.md 영어 섹션 업데이트 (Phase C + FDT 반영, 영어 문서 링크)
- SHA256 해시 기록 (아래 참조)

### 엔진 상태 점검 결과

| 검증 스크립트 | 항목 | 결과 |
|--------------|------|------|
| `phase_a_minimal_verification.py` | 자전 (v·R=0, 에너지, 궤도) | ALL PASS |
| `phase_b_orbit_verification.py` | 공전 (3-우물, 순환, 갇힘) | ALL PASS |
| `bridge_verification.py` | 브릿지 (변환, dedup, 공전) | ALL PASS |
| `dissipation_injection_verification.py` | 감쇠/주입 (밸런스, 전이) | ALL PASS |
| `fluctuation_verification.py` | 요동 (Kramers, 비편향, 정상) | ALL PASS |
| `fdt_verification.py` | FDT (등분배, override, γ=0) | ALL PASS |

**결론: 6개 스크립트 전부 ALL PASS. 엔진 상태 정상.**

### Phase C 완성도

| 항목 | 상태 |
|------|------|
| Langevin noise (σξ) | ✔ 완료 |
| O-U exact 적분 | ✔ 완료 |
| FDT (σ²=2γT/m) | ✔ 완료 |
| Boltzmann 등분배 검증 | ✔ 통과 (오차 0.6%) |
| 하위 호환 (σ=0 결정론) | ✔ 통과 |
| Manual override (noise_sigma 우선) | ✔ 통과 |
| γ=0 안전장치 | ✔ 통과 |
| 한국어 문서 | ✔ Phase_C/README.md |
| 영어 문서 | ✔ Phase_C/README_EN.md |

**Phase C 완성도: 100%**

### SHA256 해시 기록 (2026-02-24)

```
=== CookiieBrain ===
4b87c6d1e191...a8e2ae4  cookiie_brain_engine.py
ea761fe7fba5...344e9e   Phase_B/multi_well_potential.py
f62d3fc32a3a...7738c2   Phase_B/well_to_gaussian.py
92edd4865125...dad4252  examples/phase_b_orbit_verification.py
6ab5b4bc2956...2135e0   examples/bridge_verification.py
ad9e7f6b1473...eab409   examples/dissipation_injection_verification.py
d393fad0a139...f778d    examples/fluctuation_verification.py
c70db58fcfda...fc4293   examples/fdt_verification.py
72e328e5c289...efea6d   Phase_A/rotational_field.py
2bbf892be5d6...18aa32   Phase_A/moon.py

=== PotentialFieldEngine (별도 레포) ===
074c6f496a24...e25ebf2b potential_field_engine.py
```

### 변경 파일
| 파일 | 변경 | 상태 |
|------|------|------|
| `README.md` | m 보완, 영어 섹션 업데이트 | 수정 |
| `docs/FULL_CONCEPT_AND_STATUS_EN.md` | 전체 개념 영어판 | 신규 |
| `Phase_C/README_EN.md` | Phase C 영어판 | 신규 |
| `docs/WORK_LOG.md` | 해시 기록, 엔진 점검, Phase C 완성도 | 수정 |

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 — Layer 1: 통계역학 정식화 구현

### 개요

Phase C (FDT) 위에 첫 번째 토양(Layer 1)을 쌓았다.
시뮬레이션 궤적을 확률·열역학 언어로 번역하는 분석 모듈.

### 변경사항

| 파일 | 변경 | 상태 |
|------|------|------|
| `Layer_1/__init__.py` | 모듈 export | 신규 |
| `Layer_1/statistical_mechanics.py` | Kramers rate, TransitionAnalyzer, entropy | 신규 |
| `Layer_1/README.md` | Layer 1 개념 문서 (한국어) | 신규 |
| `Layer_1/README_EN.md` | Layer 1 concept (English) | 신규 |
| `examples/layer1_verification.py` | 5개 검증 테스트 | 신규 |
| `docs/FULL_CONCEPT_AND_STATUS.md` | Layer 1 섹션 추가, 파일 구조 업데이트 | 수정 |
| `docs/WORK_LOG.md` | 이 항목 추가 | 수정 |

### 구현된 기능

| 기능 | 수식 | 상태 |
|------|------|------|
| Kramers 탈출률 | k = (λ₊/ω_b)(ω_a/2π)exp(−ΔV/T) | ✔ |
| Rate 행렬 | K[i,j] = k(i→j), K[i,i] = −Σ K[i,j] | ✔ |
| 전이 행렬 | P[i,j] = N(i→j)/Σ N(i→k) | ✔ |
| 체류 시간 | τᵢ = time_in_i / departures_from_i | ✔ |
| 순환 흐름 | J[i,j] = N(i→j) − N(j→i) | ✔ |
| 상세 균형 지표 | Σ\|J\|/(2Σ\|N\|) | ✔ |
| 엔트로피 생산률 | Ṡ = (γ/T)(⟨\|v\|²⟩ − dT/m) − (1/T)⟨v·I⟩ | ✔ |
| 시계열 엔트로피 | 이동 평균 dS/dt(t) | ✔ |

### 검증 결과

```
python examples/layer1_verification.py → ALL PASS (5/5)
```

| # | 검증 | 결과 | 비고 |
|---|------|------|------|
| 1 | Kramers rate 공식 정합성 | PASS | 대칭, T·γ 의존성 4개 하위 검증 |
| 2 | Kramers vs 시뮬레이션 전이 | PASS | 비율 0.13 (order-of-magnitude) |
| 3 | 전이 행렬 + 상세 균형 | PASS | 행합=1, 평형 violation=0 |
| 4 | 엔트로피 생산률 | PASS | 평형 Ṡ ≈ 0 (열역학 정합) |
| 5 | Arrhenius 법칙 | PASS | T↑→rate↑ 확인 |

### 기존 검증 재실행 (회귀 확인)

Layer 1은 분석 모듈이므로 기존 엔진 코드를 변경하지 않았다.
기존 검증 스크립트 영향 없음.

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 — Trunk 리팩터링: 레이어 아키텍처

### 개요

줄기(trunk) `potential_field_engine.py`를 레이어 구조로 리팩터링.
기존 API 100% 하위 호환 유지. 내부를 3종 레이어로 분리.

### 아키텍처

```
trunk.update(state)
  ├─ Force Layers    (GradientForce, InjectionForce, CallbackForce, ...)
  ├─ Gauge Layer     (CoriolisGauge, NullGauge, ...)
  ├─ Thermo Layer    (LangevinThermo, NullThermo, ...)
  └─ TrunkChecker    (skew, fdt, conservation, dimensions)
```

고정한 것 (물리의 뼈대):
1. 상태공간: (x, v, t) 확장 가능
2. Newton 업데이트 구조
3. 보존/소산/요동 분리 (Strang splitting)
4. 극한 일관성: σ→0, γ→0, FDT, 차원

열어둔 것 (레이어에서 교체):
- 특정 퍼텐셜/차원/노이즈/상호작용/해석

### 변경사항

| 파일 | 변경 | 상태 |
|------|------|------|
| `potential_field_engine.py` (PFE) | Layer 인터페이스, _build_layers, _strang_step, _euler_step | 수정 |
| `layers.py` (PFE) | Force/Gauge/Thermo 프로토콜 + 기본 구현 + TrunkChecker | 신규 |

### 검증 결과

```
7개 기존 검증 스크립트: ALL PASS (7/7)
```

| 스크립트 | 항목 | 결과 |
|----------|------|------|
| `phase_a_minimal_verification.py` | 자전 (v·R=0, 에너지, 궤도) | ALL PASS |
| `phase_b_orbit_verification.py` | 공전 (3-우물, 순환, 갇힘) | ALL PASS |
| `bridge_verification.py` | 브릿지 (변환, dedup, 공전) | ALL PASS |
| `dissipation_injection_verification.py` | 감쇠/주입 (밸런스, 전이) | ALL PASS |
| `fluctuation_verification.py` | 요동 (Kramers, 비편향, 정상) | ALL PASS |
| `fdt_verification.py` | FDT (등분배, override, γ=0) | ALL PASS |
| `layer1_verification.py` | 통계역학 (Kramers, 전이행렬, dS/dt) | ALL PASS |

**하위 호환 완전 유지. 리팩터링으로 인한 동작 변경 없음.**

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 — Layer 1 보강: well_frequency 수치 Hessian

### 작업 내용
- `well_frequency()`: 단일 우물 해석해(A/σ²) → 합성 퍼텐셜 수치 Hessian으로 교체
- multi-well에서 다른 우물 꼬리의 곡률 기여를 정확히 반영
- `saddle_frequency()`와 동일한 중심 차분 Hessian 방식으로 통일

### 변경 파일
| 파일 | 변경 |
|------|------|
| `Layer_1/statistical_mechanics.py` | `well_frequency()` 수치 Hessian 구현 |

### 검증
- 대칭 우물(±2.0): ω_a = 1.4145 (old: 1.4142, 차이 0.02%)
- 대칭성 유지: k(0→1) = k(1→0) (정확히 일치)
- `layer1_verification.py`: ALL PASS (5/5)

---

## 2026-02-24 — Layer 2: 다체/장론 구현

### 작업 내용
- N-body 다체 동역학 모듈 구현
- trunk의 state_vector를 큰 벡터로 취급 → 레이어만 교체
- Newton 제3법칙 구조적 보장 (F_ij = -F_ji)

### 핵심 설계
trunk은 state_vector의 내부 구조를 모른다.
`[x₁...xₙ, v₁...vₙ]`를 그냥 큰 (x, v) 벡터로 적분한다.
Layer 2 ForceLayer가 내부에서 (N, d) reshape를 처리한다.

### 새 파일
| 파일 | 역할 |
|------|------|
| `Layer_2/__init__.py` | 모듈 exports |
| `Layer_2/nbody.py` | NBodyState, InteractionForce, ExternalForce, NBodyGauge |
| `Layer_2/README.md` | 개념, 수식, 검증 결과 문서 |
| `examples/layer2_verification.py` | 5개 물리 검증 |

### 구성 요소
| 클래스 | 역할 | 프로토콜 |
|--------|------|----------|
| `NBodyState` | flat ↔ (N,d) reshape 유틸리티 | — |
| `InteractionForce` | 쌍체 상호작용 Σ_{i<j} φ(r_ij) | ForceLayer |
| `ExternalForce` | 입자별 외부 퍼텐셜 Σᵢ V(xᵢ) | ForceLayer |
| `NBodyGauge` | 입자별 코리올리 회전 | GaugeLayer |

편의 함수: `gravitational_interaction()`, `spring_interaction()`, `coulomb_interaction()`

### 극한 일관성
| 극한 | 기대 | 검증 |
|------|------|------|
| N=1 | 단일 입자와 동일 | 차이 0.0 (exact) |
| γ=0, σ=0 | 에너지 보존 | drift < 0.23% |
| F_ij = -F_ji | 운동량 보존 | 변화 3.2e-14 |
| FDT + N입자 | 등분배 | 오차 2.0% |
| 중심력 | 각운동량 보존 | 변화 5.3e-15 |

### 검증
```
layer2_verification.py: ALL PASS (5/5)
  [PASS]  Newton 제3법칙 — 운동량 보존
  [PASS]  에너지 보존 — 보존계
  [PASS]  N=1 극한 — 단일 입자와 동일
  [PASS]  등분배 정리 — 열평형
  [PASS]  2체 순환 — 각운동량 보존
```

### 회귀 테스트
전체 기존 검증 7개 + Layer 2 5개 = 12/12 ALL PASS

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## 2026-02-24 (4차): Layer 3 — 게이지/기하학 구현

### 동기
Layer 2(다체)까지의 구조에서는 회전이 전역 상수(ω)였다.
Layer 3에서 "위치마다 다른 회전" — 위치 의존 자기장 B(x)를 도입한다.

### 구현 내용

1. **`Layer_3/gauge.py`** — 핵심 모듈
   - `MagneticForce`: F = B(x)·J·v (단일 입자, 2D/3D)
   - `NBodyMagneticForce`: N 입자 각각에 B(x) 적용
   - `GeometryAnalyzer`: Berry 위상, 자기 선속, 국소 곡률, E×B drift, 사이클로트론 계산
   - 편의 함수: `uniform_field`, `gaussian_field`, `dipole_field`, `multi_well_field`

2. **물리적 핵심**
   - F·v = 0 구조적 보장 → 에너지 보존
   - B(x) = const → CoriolisGauge와 동일 (극한 일관성)
   - trunk 수정 불필요: ForceLayer 프로토콜 준수

3. **E×B drift 부호 규약**
   - MagneticForce의 F = B·J·v 규약에서:
   - v_drift = (∂V/∂y, −∂V/∂x) / B
   - 적분기 주의: v-의존 힘이므로 Strang splitting 필수 (NullGauge → Euler에서는 drift 심각)

4. **적분기 제약**
   - MagneticForce는 속도 의존 힘 → Strang splitting에서 에너지 error bounded O(dt²)
   - `CoriolisGauge(0.0)` 으로 Strang 활성화 권장

### 검증 (`examples/layer3_verification.py`)

| # | 검증 | 결과 |
|---|------|------|
| 1 | 에너지 보존 (가우시안 B, Strang) | PASS — drift < 5% |
| 2 | 사이클로트론 (균일 B) | PASS — r_c 오차 < 2% |
| 3 | B=0 극한 | PASS — 궤적 차이 = 0 (exact) |
| 4 | E×B drift (collisionless) | PASS — v_drift 오차 < 0.1% |
| 5 | Berry 위상 (가우시안 B) | PASS — 면적분 오차 < 2% |

전체 기존 검증 12개 + Layer 3 5개 = 17/17 ALL PASS

### PHAM 서명
- ✔ 서명됨 (2026-02-24)

---

## PHAM 서명 상태

> 서명일: 2026-02-24. 전체 서명 완료.

### PFE 리포 (PotentialField_Engine)

| 파일 | 블록 | 해시 (앞 16자) | 스코어 | 체인 파일 |
|------|------|---------------|--------|----------|
| `potential_field_engine.py` | 2 | `841c8726bee99000` | 0.8024 | `pham_chain_potential_field_engine.json` |
| `layers.py` | 1 | `84332c0b406bb4c0` | 0.9998 | `pham_chain_layers.json` |
| `CONCEPT.md` | 1 | `fe03e9f7b7f02cf4` | — | `pham_chain_CONCEPT.json` |
| `grid_analyzer.py` | 1 | `8511871507576373` | — | `pham_chain_grid_analyzer.json` |
| `README.md (PFE)` | 1 | `f68c08d278216056` | — | `pham_chain_README.json` |

### CookiieBrain 리포

| 파일 | 해시 (앞 16자) | 스코어 | 체인 파일 |
|------|---------------|--------|----------|
| `statistical_mechanics.py` | `ffc2377780cc363e` | 0.9998 | `pham_chain_statistical_mechanics.json` |
| `nbody.py` | `345fe7b07a85eb50` | 0.9998 | `pham_chain_nbody.json` |
| `cookiie_brain_engine.py` | `4b87c6d1e1918742` | 0.9999 | `pham_chain_cookiie_brain_engine.json` |
| `multi_well_potential.py` | `ea761fe7fba5ce07` | 0.9997 | `pham_chain_multi_well_potential.json` |
| `rotational_field.py` | `72e328e5c289b00a` | 0.9996 | `pham_chain_rotational_field.json` |
| `moon.py` | `2bbf892be5d63597` | 0.9994 | `pham_chain_moon.json` |
| `well_to_gaussian.py` | `f62d3fc32a3a4f4a` | 0.9998 | `pham_chain_well_to_gaussian.json` |
| `layer1_verification.py` | `f752519bf36b9f6e` | 0.9999 | `pham_chain_layer1_verification.json` |
| `layer2_verification.py` | `72851b3f2cd57695` | 0.9999 | `pham_chain_layer2_verification.json` |
| `fdt_verification.py` | `c70db58fcfdaf5e9` | 0.9997 | `pham_chain_fdt_verification.json` |
| `fluctuation_verification.py` | `d393fad0a1399bb6` | 0.9998 | `pham_chain_fluctuation_verification.json` |
| `dissipation_injection_verification.py` | `ad9e7f6b1473d3d1` | 0.9998 | `pham_chain_dissipation_injection_verification.json` |
| `bridge_verification.py` | `6ab5b4bc2956cf18` | 0.9998 | `pham_chain_bridge_verification.json` |
| `phase_b_orbit_verification.py` | `92edd4865125412f` | 0.9998 | `pham_chain_phase_b_orbit_verification.json` |
| `gauge.py` | `1d13883c59afc5da` | 0.9997 | `pham_chain_gauge.json` |
| `layer3_verification.py` | `24eab22c565f4b4f` | 0.9998 | `pham_chain_layer3_verification.json` |

---

## Layer 4 — 비평형 일 정리 구현

**날짜**: 2026-02-24

### 동기

Layer 1(평형/근평형 열역학)을 임의의 비평형 과정으로 확장.
Jarzynski 등식은 평형에서 임의로 먼 과정에서도 성립하는 **정확한 등식**.

### 구현 상세

#### 새 파일

- `Layer_4/fluctuation_theorems.py`: 핵심 구현
  - `Protocol`: 시간 의존 퍼텐셜 V(x, λ(t))
  - `ProtocolForce`: ForceLayer 프로토콜 준수 (trunk 연결)
  - `WorkAccumulator`: W = Σ[V(x_n,λ_{n+1}) − V(x_n,λ_n)]
  - `JarzynskiEstimator`: ΔF = −T·ln⟨e^{-W/T}⟩ (log-sum-exp 안정화)
  - `CrooksAnalyzer`: 정방향/역방향 대칭 검증
  - `moving_trap()`, `stiffness_change()`, `equilibrium_sample()`
- `Layer_4/__init__.py`: 명시적 `__all__` 공개 API
- `Layer_4/README.md`: 물리 개념 + 구성 요소 + 검증 결과

#### 검증 (layer4_verification.py)

5개 물리 검증 ALL PASS:

| # | 테스트 | 핵심 수치 |
|---|------|-----------|
| 1 | Jarzynski (이동 트랩, ΔF=0) | ⟨e^{-W/T}⟩ = 1.008 |
| 2 | 제2법칙 ⟨W⟩ ≥ ΔF | ⟨W_diss⟩ = 4.76 ≥ 0 |
| 3 | Jarzynski (강성 변화) | ΔF 오차 0.03% |
| 4 | 준정적 극한 | τ↑ → ⟨W⟩↓ 단조 감소 |
| 5 | Crooks 대칭 | |ΔF_f + ΔF_r| = 0.016 |

#### 기술 노트

- Jarzynski 지수 평균은 rare event에 민감 (알려진 수치적 한계)
- 느린 프로토콜(τ=20)에서 수렴 확인 후 PASS
- 강성 변화(τ=10, 400 궤적)에서는 0.03% 오차로 수렴 — 프레임워크 정확
- log-sum-exp 트릭으로 수치 오버플로 방지

### PHAM 서명

| 파일 | 해시 (앞 16자) | 스코어 | 체인 파일 |
|------|---------------|--------|----------|
| `fluctuation_theorems.py` | `08298f280ba28849` | 0.9997 | `pham_chain_fluctuation_theorems.json` |
| `layer4_verification.py` | `4121dcc99bbfb95b` | 0.9998 | `pham_chain_layer4_verification.json` |

---

## Layer 5 — 확률역학 구현

**날짜**: 2026-02-24

### 동기

Layer 1–4의 궤적(Langevin) 관점을 확률 밀도(Fokker-Planck) 관점으로 전환.
Nelson 확률역학의 forward/backward 속도 분해로 확산 과정의 기하학적 구조를 드러냄.

### 구현 상세

#### 새 파일

- `Layer_5/stochastic_mechanics.py`: 핵심 구현
  - `FokkerPlanckSolver1D`: 1D 격자 FP 풀이 (FTCS, no-flux BC, 확률 보존)
  - `NelsonDecomposition`: v_current + v_osmotic 분해, ∇(ln ρ) 직접 계산
  - `ProbabilityCurrent`: J = bρ − D∇ρ 분석
  - `double_well_potential()`, `gaussian_initial()`, `langevin_ensemble_histogram()`
- `Layer_5/__init__.py`: 명시적 `__all__` 공개 API
- `Layer_5/README.md`: 물리 개념 + 검증 결과 + Nelson 해석

#### 검증 (layer5_verification.py)

5개 물리 검증 ALL PASS:

| # | 테스트 | 핵심 수치 |
|---|------|-----------|
| 1 | 정상 분포 = 볼츠만 | L1 = 0.023 |
| 2 | 확률 보존 ∫ρ=1 | 편차 2.2e-16 (기계 정밀도) |
| 3 | 평형 확률류 J=0 | J_max = 2.9e-04 |
| 4 | Nelson 삼투 속도 | 오차 = 0.000000 |
| 5 | Langevin ↔ FP 일치 | L1 = 0.023 (이중 우물) |

#### 기술 노트

- osmotic_velocity: ∇(ln ρ) 직접 계산 (∇ρ/ρ 대신) → 수치 정밀도 향상
- 확률 보존: no-flux 경계 + 매 스텝 재정규화 → 기계 정밀도
- Langevin-FP 일치: 50000 입자 앙상블 vs FP 볼츠만 L1 < 0.025

### PHAM 서명

| 파일 | 해시 (앞 16자) | 스코어 | 체인 파일 |
|------|---------------|--------|----------|
| `stochastic_mechanics.py` | `afc605aaafa9cf91` | 0.9997 | `pham_chain_stochastic_mechanics.json` |
| `layer5_verification.py` | `1006598f801045cf` | 0.9998 | `pham_chain_layer5_verification.json` |
