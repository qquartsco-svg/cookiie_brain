# 환경 설정 현황 및 다음 물리 레이어

**기준**: v1.5.0 (2026-02-26)

---

## 1. 현재 환경 설정 — 어디까지 되었는가

### 레이어 구조 (아래→위 순)

| 층 | 구성 | 물리·개념 | 버전 |
|----|------|-----------|------|
| **data/** | NASA/JPL 실측, build_solar_system() | 질량, 궤도, 스핀, J2, 반지름 | — |
| **core/** | EvolutionEngine, Body3D, SurfaceOcean | N-body 중력, 스핀-궤도 토크, 조석, 세차, 해류 | v1.0 |
| **em/** | SolarLuminosity, MagneticDipole, SolarWind, Magnetosphere | L=M^α, F∝1/r², B∝1/r³, P_sw∝1/r², 자기권 | v1.1~1.3 |
| **atmosphere/** | greenhouse, column, water_cycle | τ→ε_a, 열적 관성, PT 경계(궁창), 증발·응결·잠열 | v1.4, v1.5 |
| **cognitive/** | RingAttractor, SpinRingCoupling | 관성 기억, 물리↔인지 필드 연결 | v0.9 |

### 의존 방향

```
data/ → core/ ← em/
              ← atmosphere/  (em 읽기, core 읽기)
              ← cognitive/   (core 읽기)
```

### 구현된 물리 법칙·개념

| 법칙/개념 | 모듈 | 수식/역할 |
|-----------|------|-----------|
| N-body 중력 | core | F = GMm/r² |
| 스핀-궤도 토크 | core | 세차, 조석 변형 |
| 질량-광도 | em | L ∝ M^α |
| 복사 역제곱 | em | F = L/(4πr²) |
| Stefan-Boltzmann | em, atmosphere | T_eq = [F(1-A)/(4σ)]^¼ |
| 자기쌍극자 | em | B ∝ 1/r³ |
| 태양풍 동압 | em | P_sw ∝ 1/r² |
| Chapman-Ferraro | em | r_mp = R·(kB²/P_sw)^(1/6) |
| 광학 깊이 τ | atmosphere | τ(CO₂,H₂O,CH₄) 파라메트릭 |
| 1-layer emissivity | atmosphere | ε_a = 1 - exp(-τ) |
| 열적 관성 | atmosphere | C·dT/dt = F_in - F_out |
| PT 경계 (궁창) | atmosphere | T>273.16, P>611.73 → liquid |
| Clausius-Clapeyron | atmosphere | e_sat(T) |
| 증발·잠열 | atmosphere | E, Q_latent = L_v×E |

### 아직 없는 것 (README 등에서 언급만)

- 대기 순환 (해들리셀)
- 구름/강수
- 광화학 (오존층)
- Outgassing (CO₂/H₂O 탄생)
- τ 스펙트럼/밴드 모델

---

## 2. 다음 환경 설정 후보 — 물리 법칙·개념

### Phase 6c급 (atmosphere 연장)

| 후보 | 물리 법칙·개념 | 입력 | 출력 | 의존 |
|------|----------------|------|------|------|
| **구름/강수** | 수증기→운滴, 알베도 피드백 | q, T, P | cloud_cover, albedo_mod | water_cycle, column |
| **수증기 피드백 강화** | CC + 경로 의존, 포화 수렴 | T, q | τ(H₂O) 갱신 | water_cycle |
| **τ 밴드/스펙트럼** | 파장별 흡수 (IR/UV) | 조성, F(λ) | τ_band, ε_a | greenhouse, em |

### 상위 레이어 (지권·광화학)

| 후보 | 물리 법칙·개념 | 입력 | 출력 | 의존 |
|------|----------------|------|------|------|
| **광화학 (오존층)** | UV → O₂ 해리 → O₃ | F_UV, O₂ | O₃, 흡수 스펙트럼 | em, atmosphere |
| **Outgassing** | 맨틀·화산 → CO₂, H₂O | 맨틀 T, 화산률 | composition 갱신 | 지권(미구축) |
| **대기 순환** | 해들리셀, 위도별 풍속 | T, g, Ω | U(lat), 수송 | core(코리올리) |

### 정리

- **6c급**: water_cycle/column 위에 직접 얹을 수 있음.
- **광화학**: em에 UV 스펙트럼(또는 λ 분해) 필요.
- **Outgassing**: 지권(맨틀, 판 구조) 레이어 없음 → 새 층 필요.
- **대기 순환**: 1D column 한계, 2D/3D 확장 또는 단순화 모델 필요.

---

## 3. 요약

| 구분 | 상태 |
|------|------|
| **구성 완료** | data → core → em → atmosphere(6a,6b) → cognitive |
| **물리 코어** | 중력, 세차, 조석, 해류, 복사, 자기장, 자기권, 온실, 수순환 |
| **다음 후보** | 6c(구름/강수), 수증기 피드백, τ 밴드, 광화학, Outgassing, 대기 순환 |

현재는 **0D 단일 대기 컬럼(전지구 평균)**까지 확정된 상태이며,  
다음은 **Phase 6c(구름/강수)** 또는 **수증기 피드백 강화**가 의존성이 가장 짧고 구현 용이함.
