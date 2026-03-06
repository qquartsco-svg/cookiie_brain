# Layer 5 — Stochastic Mechanics / Fokker-Planck

> Shifts from trajectory (Langevin) to probability density ρ(x,t) evolution.

**Position**: Layer 1 (Langevin) → **Layer 5**

---

## Core equations

**Fokker-Planck (overdamped only)**:
```
∂ρ/∂t = ∇·(∇V·ρ/(mγ)) + D∇²ρ = −∇·J
```

**Diffusion coefficient**: D = T/(mγ) — from FDT.

**Stationary distribution**: ρ_eq ∝ exp(−V/T) — Boltzmann.

**Nelson decomposition**:
```
v_current = b = −∇V/(mγ)     (drift)
v_osmotic = D·∇ln ρ           (osmotic)
v_+ = v_current + v_osmotic    (forward, = 0 at equilibrium)
```

**Probability current**: J = bρ − D∇ρ, equilibrium J = 0 (detailed balance).

## Scope

- **Implemented**: overdamped (position-space) Fokker-Planck
- **Not implemented**: underdamped Kramers FP (phase-space, future work):
  `∂ρ/∂t = −v·∂_xρ + ∂_v(γvρ + V'ρ/m) + (γT/m)·∂²_vρ`

## Components

| Class | Role |
|-------|------|
| `FokkerPlanckSolver1D` | 1D grid-based ρ(x,t) evolution (conservative flux) |
| `NelsonDecomposition` | v_osmotic = D·∇ln ρ (numerically stable) |
| `ProbabilityCurrent` | J = bρ − D∇ρ |

## Verification (5/5 ALL PASS)

| # | Test | Result |
|---|------|--------|
| 1 | Stationary = Boltzmann | PASS |
| 2 | Probability conservation ∫ρ = 1 | PASS |
| 3 | Equilibrium current J = 0 | PASS |
| 4 | Nelson osmotic velocity | PASS |
| 5 | Langevin ↔ FP consistency | PASS |
