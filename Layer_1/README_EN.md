# Layer 1 — Statistical Mechanics Formalization

> The first soil laid on top of the trunk (Langevin + FDT).
> Translates trajectories into the language of probability and thermodynamics.

**Position**: Phase C (Fluctuation / FDT) → **Layer 1** → Layer 2 (Many-body / Field Theory)

---

## Architecture — Trunk and Branches

```
              ┌─ Layer 6: Topology ──────┐
              │  Layer 5: Quantum Bridge  │
              │  Layer 4: Non-eq Thermo   │
              │  Layer 3: Gauge/Geometry  │
              │  Layer 2: Many-body/Field │
             ┌┴──────────────────────────┴┐
             │ ★ Layer 1: Statistical Mech │  ← this module
             └┬──────────────────────────┬┘
              │                          │
    ┌─────────┴──────────────────────────┴─────────┐
    │  Trunk: m ẍ = -∇V + ωJv - γv + I + σξ(t)    │
    │         σ² = 2γT/m  (FDT)                    │
    └──────────────────────────────────────────────┘
```

Layer 1 is the **soil** for all subsequent extensions (Layers 2–6).
Without Kramers rates, transition matrices, and entropy production
from this layer, the upper branches have no roots.

---

## Components

### ① Kramers Escape Rate

**Physics**: Thermal transition frequency over barrier ΔV at temperature T.

```
k(i→j) = (λ₊ / ω_b) · (ω_a / 2π) · exp(−ΔV / T)
```

| Symbol | Meaning |
|--------|---------|
| ω_a | Well-bottom frequency √(A / mσ²) |
| ω_b | Saddle unstable frequency (numerical Hessian) |
| λ₊ | Kramers-Grote-Hynes correction: −γ/(2m) + √((γ/(2m))² + ω_b²) |
| ΔV | Barrier height V_saddle − V_well |
| T | Temperature (kB=1) |

`kramers_rate_matrix(mwp, T, γ, m)` → full rate matrix K.
K is the generator of a continuous-time Markov chain: dp/dt = K^T p.

### ② Transition Analyzer (`TransitionAnalyzer`)

Extracts empirical statistics from simulation trajectories.

| Method | Returns |
|--------|---------|
| `observe(x, mwp, dt)` | One-step observation (updates counts, times) |
| `transition_matrix()` | P[i,j] = N(i→j) / Σ_k N(i→k) (stochastic matrix) |
| `mean_residence_times()` | τᵢ = (time in well i) / (departures from well i) |
| `occupation_fractions()` | Time-based occupancy fraction per well |
| `net_circulation()` | J[i,j] = N(i→j) − N(j→i) (non-equilibrium current) |
| `detailed_balance_violation()` | Σ|J| / (2Σ|N|) (0=equilibrium, 1=far-from-eq) |

### ③ Entropy Production Rate

```
Ṡ = (γ/T)(⟨|v|²⟩ − dT/m) − (1/T)⟨v·I⟩
```

| Term | Physics |
|------|---------|
| (γ/T)⟨\|v\|²⟩ | Dissipation power / T |
| (γ/T)(dT/m) | Equilibrium maintenance cost from heat bath (baseline) |
| (1/T)⟨v·I⟩ | Work done by external driving |

Limit consistency:
- **Equilibrium (I=0, FDT)**: ⟨|v|²⟩ = dT/m → **Ṡ = 0** (2nd law consistent)
- **Non-equilibrium (I≠0)**: Ṡ > 0 (irreversible entropy production)

---

## Verification Results (2026-02-24)

```
python examples/layer1_verification.py → ALL PASS (5/5)
```

| # | Test | Result |
|---|------|--------|
| 1 | Kramers rate formula consistency (symmetry, T↑→k↑, γ↑→k↓) | PASS |
| 2 | Kramers rate vs simulation transition frequency | PASS (order-of-magnitude) |
| 3 | Transition matrix row-sum=1, equilibrium detailed balance ≈0 | PASS |
| 4 | Entropy production: equilibrium Ṡ ≈ 0 (limit consistency) | PASS |
| 5 | Arrhenius law (T↑ → rate↑ confirmed) | PASS |

---

*GNJz (Qquarts) · CookiieBrain Layer 1*
