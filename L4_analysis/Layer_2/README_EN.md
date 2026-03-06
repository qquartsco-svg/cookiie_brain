# Layer 2 — Many-body / Field Theory

> Extends single particle → N particles with pairwise interactions.

**Position**: Layer 1 (statistical mechanics) → **Layer 2** → Layer 3 (gauge)

---

## Why N-body?

A "field" has no meaning for a single particle.
Only when multiple particles interact does collective dynamics emerge.

## Core equation

```
F_i = -∇_i Σ_{j≠i} φ(|x_i - x_j|)
    = -Σ_{j≠i} φ'(r_ij) · (x_i - x_j) / r_ij
```

**Newton's 3rd law**: F_ij = −F_ji (structurally guaranteed) → total momentum conserved.

**Force sign convention**: φ'(r) > 0 → attraction, φ'(r) < 0 → repulsion.

## Components

| Class | Role |
|-------|------|
| `NBodyState` | Multi-particle state management (positions, velocities, momenta) |
| `InteractionForce` | Pairwise potential φ(r), F_ij = −F_ji |
| `ExternalForce` | Per-particle external potential |
| `NBodyGauge` | Per-particle Coriolis rotation |

## Built-in interactions

| Factory | φ(r) | φ'(r) | Type |
|---------|------|-------|------|
| `gravitational_interaction()` | −G/r | +G/r² | Attraction |
| `spring_interaction()` | ½k(r−r₀)² | k(r−r₀) | Restoring |
| `coulomb_interaction()` | q²/r | −q²/r² | Repulsion (same charge) |

## Verification (5/5 ALL PASS)

| # | Test | Result |
|---|------|--------|
| 1 | Newton 3rd law F_ij = −F_ji | PASS |
| 2 | Total momentum conservation | PASS |
| 3 | Gravitational energy conservation | PASS |
| 4 | Spring equilibrium distance | PASS |
| 5 | 2-body angular momentum conservation | PASS |
