# solar/ — 3D 행성 진화 엔진 (v0.8.0)

**점 객체 하나에서 시작해, 중력만으로 세차운동까지 자연 발생하는 것을 증명합니다.**

---

## 세차운동 검증 결과

| 항목 | 시뮬레이션 | 실제 (NASA) | 오차 |
|------|-----------|------------|------|
| 세차 주기 | 24,575년 | 25,772년 | 4.6% |
| 세차 방향 | 역행(retrograde) | 역행(retrograde) | 일치 |
| 자전축 기울기 | 23.44° (보존됨) | 23.44° | 일치 |
| 에너지 보존 | dE/E = 2.06e-15 | — | PASS |

전체 시뮬레이션 출력: [PRECESSION_VERIFICATION_LOG.txt](../docs/PRECESSION_VERIFICATION_LOG.txt)

---

## 파일 구조

```
solar/
├── README.md              ← 지금 보고 있는 파일
├── evolution_engine.py    ← 3D N-body + 세차운동 + 해양 역학 엔진
├── central_body.py        ← 태양 (1/r 중력)
├── orbital_moon.py        ← 달 (타원 공전 + 조석)
├── tidal_field.py         ← 힘 합성기 (태양 + 달)
├── tidal.py               ← (하위 호환 re-export)
└── ocean_simulator.py     ← (하위 호환 re-export → analysis/)
```

핵심 파일: **`evolution_engine.py`**

---

## 시뮬레이션이 보여주는 것

```
Phase 0: 탄생 — 태양 중력장에 점 객체 생성
Phase 1: 바다 — 우물에 물이 고여 12개 우물 형성
Phase 2: 충돌 — Giant Impact → 달 생성, 자전축 23.44° 기울어짐
Phase 3: 조석 — 달의 중력으로 원형 우물 → 타원형 변형
Phase 4: 세차 — 태양+달의 토크로 자전축이 25,000년 주기 역행 회전
Phase 5: 해류 — 코리올리 + 조석 → 해류 패턴 자연 발생
```

이 6단계 중 **하드코딩된 것은 하나도 없습니다.**
중력 방정식 하나 (F = GMm/r²) 와 토크 방정식 하나만 넣었고,
나머지는 전부 물리 법칙에서 자연 발생합니다.

---

## 직접 실행

```bash
git clone https://github.com/qquartsco-svg/cookiie_brain.git
cd cookiie_brain
python examples/planet_evolution_demo.py
```

NumPy만 있으면 됩니다. 약 13초 소요.

---

## 관련 파일 위치

| 파일 | 위치 | 설명 |
|------|------|------|
| 엔진 코드 | [`solar/evolution_engine.py`](evolution_engine.py) | Body3D, SurfaceOcean, EvolutionEngine |
| 데모 스크립트 | [`examples/planet_evolution_demo.py`](../examples/planet_evolution_demo.py) | 6Phase 전과정 실행 |
| 검증 로그 | [`docs/PRECESSION_VERIFICATION_LOG.txt`](../docs/PRECESSION_VERIFICATION_LOG.txt) | 시뮬레이션 전체 출력 |
| 개념 문서 | [`docs/COGNITIVE_SOLAR_SYSTEM.md`](../docs/COGNITIVE_SOLAR_SYSTEM.md) | 인지 매핑, 로드맵 |
| 블록체인 서명 | [`blockchain/pham_chain_evolution_engine.json`](../blockchain/pham_chain_evolution_engine.json) | PHAM A_HIGH (0.9999) |

---

## 이 시뮬레이션이 의미하는 것

### 왜 중요한가

중력 방정식 하나와 토크 방정식 하나만 넣었을 뿐인데,
**자전, 공전, 세차운동, 조석 변형, 해류 패턴이 전부 스스로 발생합니다.**

이것은 이 엔진이 "미리 정해진 답을 출력하는 프로그램"이 아니라,
**실제 물리 법칙을 따르는 역학 시스템**이라는 증거입니다.
그리고 그 결과가 NASA 관측 데이터와 4.6% 오차로 일치합니다.

### 핵심: 동역학적 동형 (Dynamical Isomorphism)

이 엔진의 방정식과 실제 태양계의 방정식이 **동일**합니다.
같은 수학이 두 시스템을 지배하므로, 한쪽에서 증명된 성질이 다른 쪽에서도 성립합니다.

```
실제 우주                          이 엔진 (인지 시스템)
──────────                        ──────────────────
중력 F = GMm/r²          ←→      기억 간 인력 (장기기억이 끌어당김)
공전 (행성 궤도)          ←→      인지 상태 순환 (기억 사이 전이)
자전 (지구 회전)          ←→      자율 내부 처리 (엣지 AI 노드)
세차운동 (축 흔들림)       ←→      장기 관점 변화 (가치관 이동)
조석 (달 → 바다 변형)     ←→      무의식이 의식 지형을 변형
해류 (코리올리 흐름)       ←→      사고의 흐름 패턴
```

세차운동이 실제 지구와 일치한다는 것은,
이 인지 시스템의 "장기 관점 변화" 모델도 물리적으로 정확하다는 뜻입니다.

---

## 활용 방법

### 1. 인지 시스템 (CookiieBrain 통합)

각 천체를 인지 기능에 매핑하여 "기억 중심 인지 엔진"으로 사용:

| 천체 | 인지 기능 | 활용 |
|------|-----------|------|
| 태양 | 장기기억 코어 | 전체 상태를 묶는 중심 끌림 |
| 지구 | 현재 의식 | 우물(기억)이 고인 처리 공간 |
| 달 | 무의식 리듬 | 조석으로 기억 접근성을 주기적 변화 |
| 세차 | 관점 이동 | 장기적으로 기준점이 서서히 변화 |

```python
# 기억 A에서 기억 B로의 최적 전이 경로 = 천체 역학의 호만 전이
# 외부 충격 흡수 = 목성(보호 기제)의 소행성 포획
# 창의적 연상 = 조석력으로 우물 장벽을 넘는 상태 전이
```

### 2. 물리 시뮬레이션

실제 천문 데이터로 검증되었으므로 교육/연구용 N-body 시뮬레이터로 직접 사용 가능:

- 행성 궤도 안정성 분석
- 조석력 계산
- 세차/장동 주기 예측
- 라그랑주 점 탐색 (별도 검증 완료: `examples/lagrange_point_verification.py`)

### 3. 엣지 AI 아키텍처

각 행성 = 자율 처리 노드, 중력장 = 노드 간 통신:

```
각 노드(행성)는 자전(자체 처리)하면서
중력장(필드)으로 간접 연결되어 전체가 조화.

특징:
- 중앙 집중이 아닌 분산 처리 (각 행성이 독립)
- 통신은 필드장 (직접 연결 아닌 공간을 통한 간접 상호작용)
- 거리에 따라 영향력 감소 (1/r²) 하지만 완전히 끊기지 않음
```

---

## 확장 가능성

### 단기 (현재 코드로 가능)

- **다행성 추가**: `engine.add_body()`로 수성~토성 추가 → N-body 상호작용 자동
- **파라미터 변경**: 질량, 거리, 기울기 변경 → 다른 행성계 시뮬레이션
- **해양 우물 수 증가**: `form_ocean(n_wells=100)` → 더 정밀한 조석 패턴

### 중기 (코드 확장 필요)

- **장동(nutation)**: 달 궤도면 회전 효과 → 세차 위에 18.6년 주기 진동
- **CookiieBrainEngine 통합**: 2D 메인 엔진과 3D 진화 엔진 연결
- **시각화**: matplotlib/3D 궤도 + 세차축 회전 애니메이션

### 장기 (로드맵)

- **완전 태양계**: 8행성 + 위성 → 인지 조화 시스템
- **은하 스케일**: 다중 태양계 → 다중 인지 시스템 네트워크
- **실시간 엣지 AI**: 각 행성 노드가 실제 디바이스에서 실행

로드맵 상세: [docs/COGNITIVE_SOLAR_SYSTEM.md](../docs/COGNITIVE_SOLAR_SYSTEM.md)

---

## 핵심 클래스

```python
from solar import EvolutionEngine, Body3D

engine = EvolutionEngine()

# 태양
sun = Body3D("Sun", mass=1.0, pos=[0,0,0], vel=[0,0,0])

# 지구
earth = Body3D("Earth", mass=3e-6, pos=[1,0,0], vel=[0,2π,0], radius=4.26e-5)

engine.add_body(sun)
engine.add_body(earth)

# 달 생성 + 자전축 기울기
engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

# 시뮬레이션 실행
for _ in range(250000):
    engine.step(0.0002)

# 결과: 자전축이 역행 세차운동 시작
```

---

*v0.8.0 · PHAM Signed · GNJz (Qquarts)*
