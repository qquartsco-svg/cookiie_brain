# Layer 3 — Gauge / Geometry

> Position-dependent magnetic-type force B(x) and geometric analysis.

**Position**: Layer 2 (N-body) → **Layer 3** → Layer 6 (information geometry)

---

## Core idea

The trunk's global Coriolis rotation ω becomes a spatially varying field B(x):

```
F = B(x) · J · v
```

- **Energy conserving**: F·v = 0 (structurally guaranteed, antisymmetric)
- **Limit**: B(x) = const → CoriolisGauge, B(x) = 0 → free particle

## Components

| Class | Role |
|-------|------|
| `MagneticForce` | F = B(x)·J·v for single particle |
| `NBodyMagneticForce` | Per-particle B(x_i) |
| `GeometryAnalyzer` | Flux, Abelian phase, E×B drift, curvature |

## Built-in field generators

| Function | B(x) profile |
|----------|-------------|
| `uniform_field(B₀)` | Constant |
| `gaussian_field(B₀, σ)` | Gaussian decay from origin |
| `dipole_field(m)` | Magnetic dipole ∝ 1/r³ |
| `multi_well_field(wells, B₀)` | B concentrated near wells |

## Verification (5/5 ALL PASS)

| # | Test | Result |
|---|------|--------|
| 1 | Energy conservation F·v = 0 | PASS |
| 2 | Cyclotron radius ≈ mv/(qB) | PASS |
| 3 | B=0 → free particle | PASS |
| 4 | E×B drift direction | PASS |
| 5 | Flux-based Abelian phase | PASS |
