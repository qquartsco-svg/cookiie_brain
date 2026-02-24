# Layer 6 — Information Geometry

> Fisher information metric on parameter space.

**Position**: Layer 3 (physical-space gauge) → **Layer 6** (parameter-space geometry)

---

## Core equations

**Fisher metric** (for ρ ∝ exp(−V/T)):
```
g_μν(λ) = (1/T²) · Cov_λ(∂_μV, ∂_νV)
```

- **Positive definite** when parameters actually affect the distribution
- **Semi-definite** in singular cases (parameter has no effect on ρ)

**Gaussian curvature** (Brioschi formula):
```
K = [det(A) − det(B)] / det(g)²
```
K ≠ 0 in general — nontrivial intrinsic geometry on parameter space.

**Geodesic distance**:
```
L = ∫ √(g_μν dλ^μ dλ^ν)
```
Statistical cost of parameter change. L_Fisher ≥ L_Euclid only when g > δ (not universal).

## Why naive Berry phase = 0 in 1D classical

```
A_μ = ∂⟨x⟩/∂λ_μ = ∇_λ f   (gradient of a scalar)
F = curl(∇f) = 0             (always, by Schwarz's theorem)
```

This is a mathematical fact, not a bug.
- Quantum: |ψ⟩ has complex phase → U(1) fiber bundle → nontrivial Berry phase
- Classical: ρ is real positive → gradient connection → trivial

Fisher metric provides nontrivial geometry **independent** of Berry phase.

## Quantum correspondence

| Quantum | Classical (this implementation) |
|---------|-------------------------------|
| Fubini-Study metric | Fisher information metric |
| Berry connection A_μ | Trivial (curl = 0) |
| Berry curvature F_μν | Gaussian curvature K |
| Chern number (integer) | ∫∫ K dA (continuous) |

Fisher metric = classical limit of quantum Fubini-Study metric.

## Verification (5/5 ALL PASS)

| # | Test | Result |
|---|------|--------|
| 1 | Fisher metric positive definite | PASS |
| 2 | Analytical check (Gaussian) | PASS — error < 1e-12 |
| 3 | Gaussian curvature K ≠ 0 | PASS — |K|_max = 0.24 |
| 4 | Fisher ≠ Euclidean (nontrivial) | PASS |
| 5 | Symmetry point g₁₂ = 0 | PASS |
