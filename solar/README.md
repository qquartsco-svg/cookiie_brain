# solar/ — 3D Planetary Evolution Engine (v0.8.0)

A lightweight N-body engine with spin-orbit coupling that reproduces
Earth's axial precession from first principles.
Two equations in, six emergent phenomena out.

---

## What This Engine Demonstrates

1. **Obliquity precession naturally emerges from gravitational torque**
   on an oblate (J2) body — not from any precession-specific code.
2. **Coupled orbital-spin dynamics** can be reproduced with a symplectic
   leapfrog integrator under realistic mass and distance ratios.
3. **Long-term numerical stability** is preserved over ~250,000 steps
   (energy drift < 10⁻¹⁵).
4. **Tidal deformation and surface currents** arise from gravitational
   gradients and Coriolis deflection without explicit fluid solvers.

---

## What This Engine Does NOT Claim

- To fully reproduce Earth's geophysical evolution.
- To include general relativistic corrections (e.g. Mercury perihelion advance).
- To directly prove cognitive equivalence through physical analogy.
- To model realistic fluid turbulence, climate feedbacks, or atmospheric dynamics.
- To replace high-fidelity ephemeris codes (JPL DE series, REBOUND, etc.).

---

## Verification Results

| Quantity | Simulation | Observed (NASA) | Error |
|----------|-----------|-----------------|-------|
| Precession period | 24,575 yr | 25,772 yr | 4.6% |
| Precession direction | Retrograde | Retrograde | Match |
| Obliquity | 23.44° (conserved) | 23.44° | Match |
| Energy conservation | dE/E = 2.06×10⁻¹⁵ | — | PASS |

Full simulation output: [PRECESSION_VERIFICATION_LOG.txt](../docs/PRECESSION_VERIFICATION_LOG.txt)

---

## Installation & Run

```bash
git clone https://github.com/qquartsco-svg/cookiie_brain.git
cd cookiie_brain
python examples/planet_evolution_demo.py
```

Requires only NumPy. Runs in ~13 seconds.

---

## Architecture

### File Structure

```
solar/
├── README.md              ← this file
├── evolution_engine.py    ← 3D N-body + spin-orbit + surface ocean
├── central_body.py        ← Sun (1/r gravity well)
├── orbital_moon.py        ← Moon (elliptical orbit + tides)
├── tidal_field.py         ← force combiner (Sun + Moon)
├── tidal.py               ← backward-compat re-export
└── ocean_simulator.py     ← backward-compat re-export → analysis/
```

Core file: **`evolution_engine.py`**

### Key Classes

| Class | Role |
|-------|------|
| `Body3D` | Position, velocity, spin vector, J2, radius, moment of inertia ratio |
| `SurfaceOcean` | Parametric surface wells: tidal stretch, pressure currents, vorticity |
| `EvolutionEngine` | Symplectic integrator + torque coupling + ocean update loop |

### Simulation Phases

```
Phase 0 — Birth:   Point mass placed in solar gravity field
Phase 1 — Ocean:   Surface wells form (12 parametric wells)
Phase 2 — Impact:  Giant impact → Moon ejected, spin axis tilted to 23.44°
Phase 3 — Tides:   Lunar gravity deforms circular wells into ellipses
Phase 4 — Precess: Sun+Moon torque → spin axis retrograde rotation (~25 kyr)
Phase 5 — Currents: Coriolis + tidal pressure → surface flow patterns
```

**What is prescribed vs. what emerges:**

| Element | Prescribed | Emergent |
|---------|-----------|----------|
| Gravity law (F = GMm/r²) | Yes | — |
| Torque law (τ = r × F on J2 body) | Yes | — |
| Initial positions & velocities | Yes | — |
| Giant impact event trigger | Yes | — |
| Number of ocean wells (12) | Yes | — |
| Obliquity precession | — | **Yes** |
| Precession period & direction | — | **Yes** |
| Tidal deformation pattern | — | **Yes** |
| Surface current directions | — | **Yes** |
| Latitude-dependent vorticity | — | **Yes** |

The governing equations and initial/boundary conditions are prescribed.
The dynamical phenomena listed as "emergent" are not coded explicitly —
they arise from numerical integration of those equations.

---

## Limitations

| Limitation | Impact |
|-----------|--------|
| Newtonian gravity only | No GR corrections (Mercury perihelion, frame-dragging) |
| Simplified J2 model | Higher-order terms (J4, J6) omitted |
| No tidal dissipation | Moon does not recede; Earth spin does not slow |
| Fixed Moon orbital plane | Full nutation (18.6 yr cycle) not reproduced |
| Parametric ocean model | Not a fluid solver; wells are geometric, not hydrodynamic |
| Rigid body assumption | No mantle convection, elastic deformation, or core-mantle coupling |
| No atmospheric coupling | Climate, albedo, greenhouse feedbacks absent |
| Two-body torque | Multi-planet precession perturbations not included |

This engine reproduces the **core spin-orbit coupling dynamics** accurately.
It is not a complete geophysical simulator.

---

## Extension Possibilities

### Route A — Physics Refinement

| Extension | Effect |
|-----------|--------|
| J4, J6 gravity harmonics | Improved precession accuracy |
| Nutation (lunar node regression) | 18.6 yr oscillation on top of precession |
| Tidal dissipation | Moon recession + Earth spin-down over Gyr |
| Multi-planet (Mercury–Saturn) | Full solar system N-body |

→ Toward a geophysically realistic Earth-Moon evolution simulator.

### Route B — Cognitive Dynamics (CookiieBrain Integration)

| Extension | Effect |
|-----------|--------|
| CookiieBrainEngine coupling | 2D main engine ↔ 3D evolution engine |
| Information particles on currents | Data flowing along surface streams |
| Multi-body cognitive resonance | Multiple memory masses in orbital resonance |
| Value-axis tracking | Long-term drift of cognitive reference frame |

→ Toward a dynamics-based AI architecture.
See [Appendix: Cognitive Mapping](#appendix-cognitive-mapping-structural-analogy) for the analogy framework.

### Route C — Distributed Edge AI

| Extension | Effect |
|-----------|--------|
| Planet → physical device | Each edge node runs autonomously (spin = local processing) |
| Gravity field → network protocol | Coupling strength decays as 1/r² (distance-weighted influence) |
| Galaxy scale | Multiple solar systems = multiple cognitive clusters |

→ Toward a field-based distributed edge AI network.

Detailed roadmap: [docs/COGNITIVE_SOLAR_SYSTEM.md](../docs/COGNITIVE_SOLAR_SYSTEM.md)

---

## Minimal Usage

```python
from solar import EvolutionEngine, Body3D
import numpy as np

engine = EvolutionEngine()

sun   = Body3D("Sun",   mass=1.0,  pos=[0,0,0], vel=[0,0,0])
earth = Body3D("Earth", mass=3e-6, pos=[1,0,0], vel=[0, 2*np.pi, 0],
               radius=4.26e-5)

engine.add_body(sun)
engine.add_body(earth)

engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

for _ in range(250_000):
    engine.step(0.0002)

# Result: spin axis is now retrograde-precessing
```

---

## Related Files

| File | Path | Description |
|------|------|-------------|
| Engine code | [`solar/evolution_engine.py`](evolution_engine.py) | Body3D, SurfaceOcean, EvolutionEngine |
| Demo script | [`examples/planet_evolution_demo.py`](../examples/planet_evolution_demo.py) | Full 6-phase run |
| Verification log | [`docs/PRECESSION_VERIFICATION_LOG.txt`](../docs/PRECESSION_VERIFICATION_LOG.txt) | Complete simulation output |
| Concept document | [`docs/COGNITIVE_SOLAR_SYSTEM.md`](../docs/COGNITIVE_SOLAR_SYSTEM.md) | Cognitive mapping & roadmap |
| Blockchain signature | [`blockchain/pham_chain_evolution_engine.json`](../blockchain/pham_chain_evolution_engine.json) | PHAM A_HIGH (0.9999) |

---

## Appendix: Cognitive Mapping (Structural Analogy)

> **Note on scope:** The mappings below are *structural analogies* — not
> proven functional equivalences. Two systems governed by similar
> differential equations may exhibit structurally similar attractors and
> phase-space behaviors. This does **not** imply semantic or functional
> equivalence between physical and cognitive phenomena.

### Analogy Table

| Physics | Math Structure | Cognitive Interpretation |
|---------|---------------|------------------------|
| Gravity F = GMm/r² | Conservative attractive field | Memory attraction (long-term memory pulls) |
| Orbital motion | Hamiltonian flow | Cognitive state transitions |
| Spin (rotation) | Autonomous angular momentum | Independent internal processing (edge node) |
| Precession | Long-period axis rotation | Gradual shift in value/perspective reference frame |
| Tidal deformation | External gradient reshaping | Unconscious influence deforming conscious landscape |
| Ocean currents | Constrained flow under Coriolis | Thought-flow patterns under cognitive rotation |

### State Vector Reinterpretation

```
Physical:   State = (positions, velocities, spin_vectors)
Cognitive:  State = (memory_positions, activation_levels, value_axes)
```

The governing equations remain identical under this reinterpretation.
Whether this structural correspondence produces meaningful cognitive
predictions is an open research question — not a settled claim.

### Concrete Mechanisms (Hypothetical)

- Memory A → B optimal transition = Hohmann transfer orbit
- External shock absorption = Jupiter-like mass capturing perturbations
- Creative association = tidal force lowering well barriers → state tunneling
- Worldview shift = precession of value axis over long timescales

These are proposed analogies for future investigation, not validated models.

---

*v0.8.0 · PHAM Signed · GNJz (Qquarts)*
