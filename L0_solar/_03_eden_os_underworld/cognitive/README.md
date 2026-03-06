## cognitive/ — 인지 레이어 (Ring Attractor + Spin–Ring Coupling)

### 1. 이 폴더가 하는 일 / What this folder is for

- **역할 (Role)**  
  `cognitive/` 는 **“인지 엔진”** 을 모아둔 폴더입니다.  
  - `day4/core` 가 만드는 물리적 세차·자전축 상태를  
  - **Ring Attractor** 라는 신경망 형식의 관성 기억 엔진에 연결해서,  
  - “물리적인 축 방향 변화”를 **인지 상태공간(위상·안정성)** 으로 옮겨 적는 레이어입니다.
  - 의존성: `numpy`, `solar.day4.core` 만 사용합니다. (EM, atmosphere 등은 직접 참조하지 않음)

- **직관적인 비유 (Intuition)**  
  - `core/` 가 **“행성의 물리 몸”** 이라면,  
  - `cognitive/` 는 그 위에 붙어 있는 **“자기 방향 감각 · 자세 기억 시스템”** 입니다.  
  - 자전축이 어떻게 흔들려도, Ring Attractor가 그 방향을 “기억”하고,  
    외란이 있어도 원래 상태로 돌아가려는 **관성 기억(inertial memory)** 를 만듭니다.

### 2. 포함된 엔진 / Engines

- `ring_attractor.py`  
  - `RingAttractorEngine`, `RingState` 를 정의합니다.  
  - Mexican-hat 연결(topology)을 갖는 **연속 attractor** 로,  
    입력 신호가 사라진 뒤에도 특정 위상(phase)의 “범프(bump)”를 유지합니다.  
  - 수학적으로는 S¹(원형 위상 공간) 위에서
    \[
      a_i(t+dt) = a_i(t) + dt \cdot [-a_i + \sum_j W_{ij} f(a_j) + I_i]
    \]
    형태의 동역학을 가지며, \(W_{ij}\) 는 Gaussian excitation + global inhibition(Mexican‑hat)입니다.

- `spin_ring_coupling.py`  
  - `SpinRingCoupling`, `CouplingState` 를 정의합니다.  
  - `EvolutionEngine` 로부터 **자전축 벡터·경사각·세차 위상**을 읽어 와서,  
    그 방위각(azimuth)을 Ring Attractor의 입력으로 넣고 함께 적분(step)합니다.  
  - 출력(`CouplingState`)에는
    - 물리 상태: 시간, 자전축 벡터, obliquity(경사각), spin azimuth  
    - 인지 상태: ring phase, amplitude, stability, drift  
    - 결합 상태: phase_error, coupling_strength, synchronized 여부  
    가 모두 포함되어, **물리·인지가 얼마나 잘 동기화되어 있는지**를 한 번에 볼 수 있습니다.

### 3. 사용 예시 / Usage example

```python
from solar.day4.core import EvolutionEngine, Body3D
from solar.cognitive import SpinRingCoupling

engine = EvolutionEngine()
engine.add_body(Body3D("Sun", mass=1.0))
engine.add_body(Body3D("Earth", mass=3e-6))

coupler = SpinRingCoupling(engine, target_body="Earth", coupling_strength=1.0)

for _ in range(1000):
    state = coupler.step(dt=0.001)
    print(state.time, state.spin_azimuth, state.ring_phase, state.phase_error)
```

### 4. 다른 레이어와의 관계 / Relation to other layers

- **입력 (Inputs)**  
  - `day4/core` 의 `EvolutionEngine` 이 제공하는 궤도·스핀 상태만 읽습니다.
- **출력 (Outputs)**  
  - 인지 상태(`RingState`, `CouplingState`)는  
    BrainCore, 에이전트, 분석 스크립트가 **“행성 수준의 방향감각/자세 기억”** 을 읽는 포트입니다.
- **제약 (Constraints)**  
  - `cognitive/` 는 **core의 물리를 바꾸지 않습니다.**  
    오직 관찰·기억·분석만 수행하는 **관측자 레이어(observer layer)** 입니다.

### 5. 버전 및 PHAM 서명 / Version & PHAM

- 최초 통합: `solar` v1.x (Ring Attractor), v2.x 에서 Creation Days 구조로 재정렬.  
- 검증 스크립트: `examples/brain_core_environment_demo.py`, `examples/gaia_attractor_sim.py` (간접 사용).  
- PHAM 체인: 향후 `blockchain/pham_chain_cognitive_layer.json` 으로 통합 예정.

*v2.x · PHAM-ready · GNJz (Qquarts) + Claude 5.1*

