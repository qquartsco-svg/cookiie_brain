# solar/ — 3D 행성 진화 엔진 (v0.8.0)

스핀-궤도 결합을 포함한 경량 N-body 엔진.
첫 원리(first principles)로부터 지구 자전축 세차운동을 재현한다.
방정식 2개 입력, 창발 현상 6개 출력.

> *A lightweight N-body engine with spin-orbit coupling that reproduces
> Earth's axial precession from first principles.
> Two equations in, six emergent phenomena out.*

---

## 점에서 세차운동까지: 작동 원리 / From Point Mass to Precession

```
① 점 질량 탄생
   빈 공간에 태양(대질량)과 지구(소질량) 두 점을 놓는다.
   지구에 초기 속도를 주면, 중력 F = GMm/r² 하나만으로
   안정된 타원 궤도가 형성된다. (케플러 궤도)

        태양 ●─────────────── ○ 지구
             ← F = GMm/r² →     v↑ (접선 속도)

② 바다 형성
   지구 표면에 12개 우물(well)을 배치한다.
   아직 외부 힘이 없으므로 우물은 원형 대칭.

③ 거대 충돌 (Giant Impact)
   외부 천체가 비스듬히 충돌 → 두 가지 결과:
   (a) 파편이 궤도에 진입 → 달 생성
   (b) 충돌 각운동량 전달 → 자전축이 23.44° 기울어짐
   이제 지구는 "기울어진 채 회전하는 편평 구(oblate spheroid)"가 된다.

                 자전축 ↗ (23.44° 기울어짐)
                  ╱
        지구 ── ○ ── 적도 팽대부 (J2)
                  ╲
                   달 ◦ (궤도 진입)

④ 조석 변형
   달의 중력은 지구에 균일하지 않다.
   가까운 쪽은 더 강하게, 먼 쪽은 더 약하게 당긴다.
   이 중력 구배(gradient)가 원형 우물을 타원으로 늘린다.

        달 ◦ ──→ 지구 우물: ○ → ⬮ (타원 변형)

⑤ 세차운동 발생 (핵심)
   지구는 편평하다 (적도가 볼록 = J2).
   자전축은 궤도면에서 23.44° 기울어져 있다.

   태양과 달이 이 볼록한 적도 부분을 당기면,
   자전축을 궤도면으로 "눕히려는" 토크가 발생한다.

   그런데 지구는 회전하고 있다 (각운동량 보유).
   회전하는 물체에 토크를 가하면 — 토크 방향이 아니라
   토크에 수직인 방향으로 축이 움직인다.
   (팽이가 쓰러지지 않고 원을 그리며 흔들리는 것과 같은 원리)

        토크 τ = (3GM/2r³) · J2 · R² · sin(2ε)
                  ↓
        자전축이 원뿔을 그리며 회전 (세차)
        주기 ≈ 25,000년, 방향 = 역행(retrograde)

             ↗ 자전축 (시간 t₁)
        ── ○ ──
             ↗  ↖ 자전축 (시간 t₂)  ← 축이 서서히 이동
        25,000년 후 한 바퀴 완성

⑥ 해류 패턴
   기울어진 자전 + 조석 변형 → 우물 간 수심 차이 발생
   수심 차이 → 압력 차이 → 유동 (해류)
   자전하는 계에서 유동 → 코리올리 편향
   결과: 위도별로 다른 와도(vorticity)와 해류 패턴이 자연 발생

        고위도: 강한 코리올리 → 서풍 편향
        적도:   약한 코리올리 → 직선 흐름
```

**위 전 과정에서 세차운동을 직접 코딩한 코드는 없다.**
중력(F = GMm/r²)과 토크(τ = r × F)만 넣었고,
J2 편평체 위에서 작동시키면 세차가 수학적 필연으로 발생한다.

---

## 이 엔진이 증명하는 것 / What This Engine Demonstrates

1. **경사 세차(obliquity precession)는 중력 토크에서 자연 발생한다**
   — 편평(J2) 천체에 작용하는 토크로부터. 세차 전용 코드 없음.
2. **결합 궤도-스핀 역학**을 심플렉틱 립프로그 적분기로
   실제 질량비·거리비 하에서 재현할 수 있다.
3. **장기 수치 안정성** — ~250,000 스텝에서 에너지 드리프트 < 10⁻¹⁵.
4. **조석 변형 및 표면 해류**가 중력 구배와 코리올리 편향으로부터
   유체 솔버 없이 발생한다.

---

## 이 엔진이 주장하지 않는 것 / What This Engine Does NOT Claim

- 지구의 지구물리학적 진화를 완전히 재현한다.
- 일반상대론 보정을 포함한다 (수성 근일점 이동 등).
- 물리적 유사성으로 인지적 동치를 직접 증명한다.
- 실제 유체 난류, 기후 피드백, 대기 역학을 모델링한다.
- 고정밀 천체력 코드를 대체한다 (JPL DE 시리즈, REBOUND 등).

---

## 검증 결과 / Verification Results

| 항목 | 시뮬레이션 | 관측값 (NASA) | 오차 |
|------|-----------|--------------|------|
| 세차 주기 | 24,575년 | 25,772년 | 4.6% |
| 세차 방향 | 역행(retrograde) | 역행(retrograde) | 일치 |
| 자전축 기울기 | 23.44° (보존됨) | 23.44° | 일치 |
| 에너지 보존 | dE/E = 2.06×10⁻¹⁵ | — | PASS |

전체 시뮬레이션 출력: [PRECESSION_VERIFICATION_LOG.txt](../docs/PRECESSION_VERIFICATION_LOG.txt)

---

## 설치 및 실행 / Installation & Run

```bash
git clone https://github.com/qquartsco-svg/cookiie_brain.git
cd cookiie_brain
python examples/planet_evolution_demo.py
```

NumPy만 필요. 약 13초 소요.

---

## 아키텍처 / Architecture

### 파일 구조

```
solar/
├── README.md              ← 지금 보고 있는 파일
├── evolution_engine.py    ← 3D N-body + 스핀-궤도 + 표면 해양
├── central_body.py        ← 태양 (1/r 중력 우물)
├── orbital_moon.py        ← 달 (타원 공전 + 조석)
├── tidal_field.py         ← 힘 합성기 (태양 + 달)
├── tidal.py               ← 하위 호환 re-export
└── ocean_simulator.py     ← 하위 호환 re-export → analysis/
```

핵심 파일: **`evolution_engine.py`**

### 주요 클래스

| 클래스 | 역할 |
|--------|------|
| `Body3D` | 위치, 속도, 스핀 벡터, J2, 반지름, 관성모멘트 비 |
| `SurfaceOcean` | 파라메트릭 표면 우물: 조석 변형, 압력 해류, 와도 |
| `EvolutionEngine` | 심플렉틱 적분기 + 토크 결합 + 해양 업데이트 루프 |

### 시뮬레이션 단계

```
Phase 0 — 탄생:  태양 중력장에 점 질량 배치
Phase 1 — 바다:  표면 우물 형성 (12개 파라메트릭 우물)
Phase 2 — 충돌:  거대 충돌 → 달 방출, 자전축 23.44° 기울어짐
Phase 3 — 조석:  달 중력이 원형 우물을 타원으로 변형
Phase 4 — 세차:  태양+달 토크 → 자전축 역행 회전 (~25,000년 주기)
Phase 5 — 해류:  코리올리 + 조석 압력 → 표면 유동 패턴
```

### 설정된 것 vs 창발된 것 / Prescribed vs. Emergent

| 요소 | 설정(Prescribed) | 창발(Emergent) |
|------|:---:|:---:|
| 중력 법칙 (F = GMm/r²) | O | — |
| 토크 법칙 (τ = r × F, J2 천체) | O | — |
| 초기 위치 & 속도 | O | — |
| 거대 충돌 이벤트 트리거 | O | — |
| 해양 우물 개수 (12) | O | — |
| 경사 세차운동 | — | **O** |
| 세차 주기 & 방향 | — | **O** |
| 조석 변형 패턴 | — | **O** |
| 표면 해류 방향 | — | **O** |
| 위도별 와도 분포 | — | **O** |

지배 방정식과 초기/경계 조건은 설정된다.
"창발"로 표시된 동역학 현상들은 명시적으로 코딩된 것이 아니라,
해당 방정식의 수치 적분으로부터 발생한다.

---

## 한계 / Limitations

| 한계 | 영향 |
|------|------|
| 뉴턴 중력만 사용 | GR 보정 없음 (수성 근일점, 관성계 끌림) |
| 단순화된 J2 모델 | 고차항 (J4, J6) 생략 |
| 조석 소산 없음 | 달이 후퇴하지 않음; 지구 자전이 느려지지 않음 |
| 달 궤도면 고정 | 완전한 장동 (18.6년 주기) 미재현 |
| 파라메트릭 해양 모델 | 유체 솔버가 아님; 우물은 기하학적, 유체역학적이 아님 |
| 강체 가정 | 맨틀 대류, 탄성 변형, 핵-맨틀 결합 없음 |
| 대기 결합 없음 | 기후, 알베도, 온실 피드백 부재 |
| 2체 토크 | 다행성 세차 섭동 미포함 |

이 엔진은 **핵심 스핀-궤도 결합 역학**을 정확히 재현한다.
완전한 지구물리 시뮬레이터는 아니다.

---

## 확장 가능성 / Extension Possibilities

### 루트 A — 물리 정밀화

| 확장 | 효과 |
|------|------|
| J4, J6 중력 고조파 | 세차 정밀도 향상 |
| 장동 (달 교점 퇴행) | 세차 위 18.6년 진동 |
| 조석 소산 | Gyr 스케일 달 후퇴 + 지구 자전 감속 |
| 다행성 (수성~토성) | 완전 태양계 N-body |

→ 지구물리학적으로 현실적인 지구-달 진화 시뮬레이터 방향.

### 루트 B — 인지 동역학 (CookiieBrain 통합)

| 확장 | 효과 |
|------|------|
| CookiieBrainEngine 결합 | 2D 메인 엔진 ↔ 3D 진화 엔진 |
| 해류 위 정보 입자 | 표면 흐름을 따라 데이터 유동 |
| 다체 인지 공명 | 다중 기억 질량의 궤도 공명 |
| 가치축 추적 | 인지 기준 프레임의 장기 드리프트 |

→ 동역학 기반 AI 아키텍처 방향.
유비 프레임워크는 [부록: 인지 매핑](#부록-인지-매핑-구조적-유비--appendix-cognitive-mapping) 참조.

### 루트 C — 분산 엣지 AI

| 확장 | 효과 |
|------|------|
| 행성 → 물리 디바이스 | 각 엣지 노드가 자율 실행 (자전 = 로컬 처리) |
| 중력장 → 네트워크 프로토콜 | 결합 강도가 1/r²로 감쇠 (거리 가중 영향) |
| 은하 스케일 | 다중 태양계 = 다중 인지 클러스터 |

→ 필드 기반 분산 엣지 AI 네트워크 방향.

상세 로드맵: [docs/COGNITIVE_SOLAR_SYSTEM.md](../docs/COGNITIVE_SOLAR_SYSTEM.md)

---

## 최소 사용 예 / Minimal Usage

```python
from solar import EvolutionEngine, Body3D
import numpy as np

engine = EvolutionEngine()

sun   = Body3D("Sun",   mass=1.0,  pos=[0,0,0], vel=[0,0,0])
earth = Body3D("Earth", mass=3e-6, pos=[1,0,0], vel=[0, 2*np.pi, 0],
               radius=4.26e-5)

engine.add_body(sun)
engine.add_body(earth)

# 달 생성 + 자전축 기울기
engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

# 시뮬레이션 실행
for _ in range(250_000):
    engine.step(0.0002)

# 결과: 자전축이 역행 세차운동 중
```

---

## 관련 파일 / Related Files

| 파일 | 경로 | 설명 |
|------|------|------|
| 엔진 코드 | [`solar/evolution_engine.py`](evolution_engine.py) | Body3D, SurfaceOcean, EvolutionEngine |
| 데모 스크립트 | [`examples/planet_evolution_demo.py`](../examples/planet_evolution_demo.py) | 6단계 전과정 실행 |
| 검증 로그 | [`docs/PRECESSION_VERIFICATION_LOG.txt`](../docs/PRECESSION_VERIFICATION_LOG.txt) | 시뮬레이션 전체 출력 |
| 개념 문서 | [`docs/COGNITIVE_SOLAR_SYSTEM.md`](../docs/COGNITIVE_SOLAR_SYSTEM.md) | 인지 매핑 & 로드맵 |
| 블록체인 서명 | [`blockchain/pham_chain_evolution_engine.json`](../blockchain/pham_chain_evolution_engine.json) | PHAM A_HIGH (0.9999) |

---

## 부록: 인지 매핑 (구조적 유비) / Appendix: Cognitive Mapping

> **범위 주의:** 아래 매핑은 *구조적 유비(structural analogy)*이며,
> 증명된 기능적 동치가 아니다. 유사한 미분방정식이 지배하는 두 시스템은
> 구조적으로 유사한 끌개(attractor)와 위상 공간 거동을 보일 수 있다.
> 이것이 물리 현상과 인지 현상 사이의 **의미적 또는 기능적 동치를
> 함의하지는 않는다.**
>
> *The mappings below are structural analogies — not proven functional
> equivalences. Similar differential equations may yield structurally
> similar attractors and phase-space behaviors. This does not imply
> semantic or functional equivalence between physical and cognitive phenomena.*

### 유비 테이블 / Analogy Table

| 물리 현상 | 수학 구조 | 인지 해석 |
|-----------|-----------|-----------|
| 중력 F = GMm/r² | 보존적 인력 장 | 기억 간 끌림 (장기기억이 당김) |
| 공전 (궤도 운동) | 해밀턴 흐름 | 인지 상태 전이 |
| 자전 (회전) | 자율 각운동량 | 독립 내부 처리 (엣지 노드) |
| 세차운동 | 장주기 축 회전 | 가치관/관점 기준 프레임의 점진적 이동 |
| 조석 변형 | 외부 구배에 의한 재형성 | 무의식이 의식 지형을 변형 |
| 해류 | 코리올리 하 구속 유동 | 인지 회전 하의 사고 흐름 패턴 |

### 상태 벡터 재해석 / State Vector Reinterpretation

```
물리:  State = (positions, velocities, spin_vectors)
인지:  State = (memory_positions, activation_levels, value_axes)
```

지배 방정식은 이 재해석 하에서 동일하게 유지된다.
이 구조적 대응이 의미 있는 인지 예측을 생성하는지는
**열린 연구 질문이며, 확정된 주장이 아니다.**

### 구체적 메커니즘 (가설) / Concrete Mechanisms (Hypothetical)

- 기억 A → B 최적 전이 = 호만 전이 궤도
- 외부 충격 흡수 = 목성형 대질량에 의한 섭동 포획
- 창의적 연상 = 조석력이 우물 장벽을 낮춤 → 상태 터널링
- 세계관 변화 = 가치축의 장기 세차운동

**위 메커니즘은 향후 조사를 위한 가설적 유비이며, 검증된 모델이 아니다.**

---

*v0.8.0 · PHAM Signed · GNJz (Qquarts)*
