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
- ⏳ 미서명

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
- ⏳ 미서명

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
- ⏳ 미서명

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
- ⏳ 미서명

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
| `well_to_gaussian.py` | ⏳ 미서명 | — |
| `bridge_verification.py` | ⏳ 미서명 | — |
| `dissipation_injection_verification.py` | ⏳ 미서명 | — |
| `fluctuation_verification.py` | ⏳ 미서명 | — |
| `fdt_verification.py` | ⏳ 미서명 | — |
