# Phase C: Fluctuation

> Adding stochastic noise to a deterministic system — Langevin equation

---

## What is fluctuation

Same initial conditions → always the same result. That is determinism.
Adding fluctuation allows different outcomes each time.

- A state trapped by damping **randomly** crossing a barrier (Kramers escape)
- Not getting stuck on the same memory but **spontaneously** transitioning to another
- This is the physical model for creative association

---

## Equation

```
Before (deterministic):  m ẍ = -∇V(x) + ωJv - γv + I(x,v,t)
After  (stochastic):     m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

| Symbol | Meaning |
|--------|---------|
| σ | Noise intensity |
| ξ(t) | White noise (random direction every instant) |
| σ=0 | Deterministic (100% identical to previous behavior) |
| σ>0 | Stochastic transitions possible |

This is a **Langevin equation** (stochastic differential equation).

### Fluctuation-Dissipation Theorem (FDT)

Instead of setting σ directly, set **temperature T** and physics determines σ:

```
σ² = 2γT/m    (kB = 1, natural units)
```

| Symbol | Meaning | Default |
|--------|---------|---------|
| T | System temperature (cognitive: activity level) | None (inactive) |
| m | Particle mass (cognitive: inertia of thought) | 1.0 |
| γ | Damping coefficient (introduced in Phase B) | 0.0 |

**Why this matters:**
- Before FDT: σ, γ independent → no physical constraint → unphysical combinations possible
- After FDT: σ depends on γ, T, m → **Boltzmann steady state guaranteed**
  - `P(x,v) ∝ exp(-E/T)` (thermal equilibrium)
  - `⟨½mv²⟩ = T/2` (equipartition, per DoF)

**Mode priority:**

| Condition | Mode | σ |
|-----------|------|---|
| `noise_sigma > 0` | manual | Direct value |
| `temperature > 0` + `γ > 0` | fdt | `√(2γT/m)` |
| Otherwise | off | 0 |

---

## Implementation location

Phase C is not a standalone module but a **parameter extension of PotentialFieldEngine**.

| Item | File | Location |
|------|------|----------|
| Core implementation | `potential_field_engine.py` | PotentialFieldEngine (separate repo) |
| Config pass-through | `cookiie_brain_engine.py` | CookiieBrain |
| Verification (v1) | `examples/fluctuation_verification.py` | CookiieBrain |
| Verification (v2 FDT) | `examples/fdt_verification.py` | CookiieBrain |

### PotentialFieldEngine parameters

```python
# FDT mode (recommended): set temperature → σ auto-calculated
engine = PotentialFieldEngine(
    potential_func=mwp.potential,
    field_func=mwp.field,
    omega_coriolis=0.3,     # Phase A: spin
    gamma=0.05,             # damping
    temperature=1.0,        # FDT: σ = √(2γT/m) auto
    mass=1.0,               # particle mass
    noise_seed=42,
    dt=0.005,
)

# Manual mode: specify σ directly (FDT ignored)
engine = PotentialFieldEngine(
    ...,
    noise_sigma=0.15,       # direct → temperature ignored
)
```

### CookiieBrainEngine usage

```python
brain = CookiieBrainEngine(
    potential_field_config={
        "enable_phase_a": True,
        "phase_a_omega": 0.3,
        "gamma": 0.05,
        "temperature": 1.0,      # FDT mode (σ auto)
        "mass": 1.0,
        "noise_seed": 42,
    },
)
```

---

## Why not a standalone module

| Phase | Folder | Code | Nature |
|-------|--------|------|--------|
| A (Spin) | `Phase_A/` | `rotational_field.py` | **Creates** a rotation function and passes it to PFE |
| B (Orbit) | `Phase_B/` | `multi_well_potential.py` | **Creates** a potential function and passes it to PFE |
| C (Fluctuation) | `Phase_C/` | **None** (PFE parameter) | Nothing to create. Just pass σ or T |

Phase A and B are standalone modules that "create something and hand it over."
Phase C is "adding noise inside the integrator" — no separate code needed.

---

## Integration method

Strang splitting's damping half-step extended to O-U exact half-step:

```
Previous: D-S-K-R-K-S-D     (D = dissipation only)
Current:  O-S-K-R-K-S-O     (O = O-U exact: dissipation + noise coupled)

O(h):  dv = -γv dt + σ dW  exact solution
  v → e^{-γh} · v + amp(h) · ξ,   ξ ~ N(0,1)

  amp(h) = σ √((1 - e^{-2γh}) / (2γ))
  γ→0 limit: amp(h) = σ √h
```

Half-step h = dt/2 applied symmetrically at start and end.

---

## Verification results

### Phase C v1: Fluctuation basics

```
python examples/fluctuation_verification.py
```

| # | Test | Result |
|---|------|--------|
| 1 | Backward compat (σ=0) | PASS — seed-independent identical trajectory, E drift 2.58e-06 |
| 2 | Kramers escape (σ=0.25) | PASS — trapped particle escaped 10/10 |
| 3 | Unbiased noise | PASS — bias ratio 0.066 |
| 4 | Damping+noise steady state | PASS — E bounded, std=0.25 |

### Phase C v2: FDT (Fluctuation-Dissipation Theorem)

```
python examples/fdt_verification.py
```

| # | Test | Result |
|---|------|--------|
| 1 | Backward compat (temperature=None) | PASS |
| 2 | FDT σ calculation (σ²=2γT/m) | PASS — relative error 0 |
| 3 | Manual override (noise_sigma priority) | PASS |
| 4 | Boltzmann equipartition (⟨½v²⟩=T/2) | PASS — error 0.6% |
| 5 | γ=0 safety guard | PASS — σ=0 |

---

## Future extensions

| Extension | Description | Standalone module? |
|-----------|-------------|-------------------|
| ~~Constant σ~~ | ~~Direct setting~~ | ~~No~~ (v1 done) |
| ~~FDT (σ²=2γT/m)~~ | ~~Temperature-based auto σ~~ | ~~No~~ (v2 done) |
| σ(x) position-dependent | Weak near wells, strong at barriers | **Yes** |
| Colored noise | Time-correlated noise (OU process) | **Yes** |
| Temperature schedule | T(t) varies over time (simulated annealing) | No (callback) |

---

*Phase C v1 completed: 2026-02-24*
*Phase C v2 (FDT) completed: 2026-02-24*
