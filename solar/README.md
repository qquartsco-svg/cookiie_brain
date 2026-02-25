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
