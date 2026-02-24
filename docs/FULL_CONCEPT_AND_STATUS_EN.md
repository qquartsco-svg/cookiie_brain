# CookiieBrain — Full Concept and Current Status

> This document consolidates the project's physics, implementation status, verification results,
> and future direction. A new contributor should be able to understand the entire system from this
> document alone.

**Last updated: 2026-02-24 (Phase C v2 FDT included)**

---

## 0. One-sentence summary

**We are building a system where a ball rolls across a terrain of hills and valleys.**
Valley = memory, ball = current state, ball's trajectory = stream of thought.

---

## 1. The big picture

### Analogy table

| Physics | Cognitive analogy |
|---|---|
| Valley (Gaussian well) | A single memory |
| Valley depth (amplitude) | Memory strength |
| Valley width (sigma) | Attraction range of a memory |
| Ball (state vector) | Current thought state |
| Ball velocity | Thought activity level |
| Ball spinning inside a valley (spin) | Active recall of a single memory |
| Ball moving between valleys (orbit) | Association, thought transition |
| Damping (γ) | Fatigue, forgetting, activity decay |
| External injection (I) | New stimulus, arousal, external input |
| Fluctuation (ξ) | Unpredictable variation, creative transition |

### Full equation of motion (current)

```
m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

| Term | Name | Role | Energy effect |
|---|---|---|---|
| `-∇V(x)` | Potential gradient | Pulls toward valley (conservative) | Conserved |
| `ωJv` | Coriolis rotation | Deflects velocity only (spin/orbit direction) | Conserved (v·Jv=0) |
| `-γv` | Damping | Removes energy proportional to speed | **Dissipation** |
| `I(x,v,t)` | External injection | Supplies energy from outside | **Injection** |
| `σξ(t)` | Stochastic fluctuation | Random push every instant | **Stochastic** |

**Fluctuation-Dissipation Theorem (FDT):**
```
σ² = 2γT/m    (kB = 1, natural units)
```
When temperature (T) is set, σ is automatically determined from γ, T, m.
Steady-state distribution guaranteed: P(x,v) ∝ exp(-E/T), equipartition ⟨½mv²⟩ = T/2 (per DoF).

**Energy balance:**
```
E = ½||v||² + V(x)
dE/dt = -γ||v||² + v·I(x,v,t) + (noise contribution)
```

- γ=0, I=0, σ=0 → energy conserved
- γ>0, I=0, σ=0 → energy decays (trapped in one valley)
- γ>0, σ>0 → damping + fluctuation equilibrium (thermal steady state, Kramers escape possible)

---

## 2. Concepts and equations per phase

### 2-1. Static potential (foundation)

**Hopfield potential** (WellFormationEngine output, single well):
```
V_hopfield(x) = -½ x'Wx - b'x
```

**Gaussian multi-well potential** (Phase B, multiple memories):
```
V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))
```

A "bridge" accumulates Hopfield results and converts them to Gaussian multi-well potentials.

---

### 2-2. Phase A — Spin

**Equation:** Apply a force perpendicular to velocity.
```
R(v) = ωJv     where J = [[0, -1], [1, 0]]
```
- v·Jv = 0 → energy unchanged (structurally guaranteed)
- Integration: Strang splitting (Boris method) with exact rotation

**Verification:** ALL PASS (energy drift < 0.01%, orbit bounded, v·R=0)

---

### 2-3. Phase B — Orbit

**Concept:** Ball circulates between multiple valleys (memory association loop).

**Orbit conditions (empirically discovered):**
- ≥ 3 wells in non-collinear arrangement (triangle)
- E > V_saddle (energy exceeds barrier)
- ωJv (Coriolis) creates circulation direction
- Appropriate ω magnitude

**Verification (3-well triangle, ω=0.3):**
- 8 circulation cycles, 88% directional consistency, energy drift 0.0006%

---

### 2-4. WellFormation → Gaussian bridge

**Pipeline:**
```
Experience 1 → WellFormation → W₁, b₁ → GaussianWell #0 → Registry
Experience 2 → WellFormation → W₂, b₂ → GaussianWell #1 → Registry
Experience 3 → WellFormation → W₃, b₃ → GaussianWell #2 → Registry
                                                          ↓ (count ≥ 3)
                                                 MultiWellPotential
                                                          ↓
                                                 PotentialFieldEngine
                                                          ↓
                                                 Spin + Orbit auto-start
```

**Verification:** ALL PASS (center error 0.024, dedup, barrier ≈ 1.96, 5 cycles)

---

### 2-5. Energy injection / dissipation

```
Before:  ẍ = -∇V(x) + ωJv                     (conservative)
After:   ẍ = -∇V(x) + ωJv - γv + I(x,v,t)    (non-conservative)
```

**Integration:** Modified Strang splitting (D-S-K-R-K-S-D), exact exp(-γdt/2) damping.

**Verification:** ALL PASS (backward compat, damping→trapping, injection→escape, energy balance correlation 0.999995)

---

## 3. Phase C — Fluctuation [complete]

### Phase C v1: Langevin noise

Adds `+σξ(t)` to the equation of motion. O-U exact half-step integration:
```
O-S-K-R-K-S-O

O(h):  v → e^{-γh} · v + σ√((1-e^{-2γh})/(2γ)) · ξ
       γ→0 limit: v → v + σ√h · ξ
```

**Verification:** ALL PASS (backward compat, Kramers escape 100%, unbiased noise, steady state)

### Phase C v2: FDT (Fluctuation-Dissipation Theorem)

Instead of setting σ directly, set **temperature T** and let physics determine σ:
```
σ² = 2γT/m    (kB = 1)
Steady state: P(x,v) ∝ exp(-E/T)
Equipartition: ⟨½mv²⟩ = T/2  (per DoF)
```

**Mode priority:**
- `noise_sigma > 0` → manual (direct override)
- `temperature > 0` + `γ > 0` → fdt (auto-calculated)
- Otherwise → off (deterministic)

**Verification:** ALL PASS (5/5)
| # | Test | Result |
|---|------|--------|
| 1 | Backward compat (temperature=None) | PASS |
| 2 | FDT σ calculation (σ²=2γT/m) | PASS — error 0 |
| 3 | Manual override | PASS |
| 4 | Boltzmann equipartition (⟨½v²⟩=T/2) | PASS — ⟨|v|²⟩=2.01 vs theory 2.00, error 0.6% |
| 5 | γ=0 safety guard | PASS |

---

## 4. Implementation status summary

| Phase | Status | Core equation | Verification |
|---|---|---|---|
| Static potential | ✔ | V = -½x'Wx - b'x | — |
| Spin (Phase A) | ✔ | ẍ = g(x) + ωJv | ALL PASS (energy <0.01%) |
| Orbit (Phase B) | ✔ | V = -ΣA exp(...) + ωJv | ALL PASS (8 cycles, 88%) |
| WellFormation bridge | ✔ | W,b → center/A/σ | ALL PASS (5 items) |
| Energy injection/dissipation | ✔ | -γv + I(x,v,t) | ALL PASS (corr 0.999995) |
| Fluctuation (Phase C) | ✔ | +σξ(t), σ²=2γT/m (FDT) | ALL PASS (v1: 4, v2: 5) |

---

## 5. File structure

```
CookiieBrain/
├── cookiie_brain_engine.py          # Orchestration engine
├── README.md                        # Project overview (KR + EN)
├── Phase_A/                         # Spin module
│   ├── rotational_field.py          #   Coriolis ωJv + pole-type
│   ├── moon.py                      #   Satellite gravity field
│   └── STAGES_SPIN_ORBIT_FLUCTUATION.md
├── Phase_B/                         # Orbit module
│   ├── multi_well_potential.py      #   Gaussian multi-well potential
│   ├── well_to_gaussian.py          #   WellFormation → Gaussian bridge
│   └── README.md
├── Phase_C/                         # Fluctuation (Langevin noise)
│   └── README.md
├── examples/
│   ├── phase_a_minimal_verification.py
│   ├── phase_b_orbit_verification.py
│   ├── bridge_verification.py
│   ├── dissipation_injection_verification.py
│   ├── fluctuation_verification.py
│   └── fdt_verification.py
└── docs/
    ├── FULL_CONCEPT_AND_STATUS.md   # Full concept (Korean)
    ├── FULL_CONCEPT_AND_STATUS_EN.md # Full concept (English, this file)
    └── WORK_LOG.md                  # Chronological work log

(Separate repo)
PotentialFieldEngine/
└── potential_field_engine.py        # Physics integration engine
                                       Strang splitting, symplectic Euler
                                       omega_coriolis, gamma, injection_func,
                                       noise_sigma, temperature, mass (FDT)
```

---

## 6. Design principles

| Principle | Description |
|---|---|
| No hardcoding | All physics constants, paths, scales as CONFIG/params |
| State immutability | `state.copy()` then return new object |
| Backward compatibility | New features must not break existing behavior (γ=0 → conservative) |
| Verification required | Every physics change must have a numerical verification script |
| Structure first, stochasticity last | Classical structure → then stochastic layer on top |
| Engine perturbs, not dictates | Not a system that gives answers, but provides structure |

---

## 7. Key terminology

| Term | Definition |
|---|---|
| Potential V(x) | Energy landscape at position x. Lower = more stable |
| Gradient g(x) | -∇V(x). Direction of steepest descent |
| Well | Local minimum of potential. Corresponds to one memory |
| Saddle point | Barrier peak between two wells |
| Spin | Ball rotating inside a well. Implemented via ωJv |
| Orbit | Ball circulating between wells. Multi-well + ωJv |
| Dissipation | -γv. Removes energy, slows the ball |
| Injection | I(x,v,t). Supplies energy from outside |
| Fluctuation | σξ(t). Stochastic noise. Cause of non-deterministic transitions |
| FDT | σ²=2γT/m. Couples noise to dissipation via temperature |

---

*GNJz (Qquarts) · CookiieBrain*
*"Rather than presenting the answer, guiding each person to find their own is the greater purpose."*
