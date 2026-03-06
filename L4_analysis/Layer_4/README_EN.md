# Layer 4 — Non-equilibrium Work Theorems

> Exact equalities for protocol-driven processes starting from equilibrium.

**Position**: Layer 1 (statistical mechanics) → **Layer 4**

---

## Core equations

**Jarzynski equality** (exact, not an approximation):
```
⟨e^{-W/T}⟩ = e^{-ΔF/T}
```
Valid for protocol-driven processes starting from an initial equilibrium distribution.

**Second law** (follows from Jensen's inequality):
```
⟨W⟩ ≥ ΔF
```

**Crooks fluctuation theorem**:
```
P_F(W) / P_R(-W) = e^{(W-ΔF)/T}
```

## Work definition

**Inclusive work** (only external parameter changes, no dissipation/noise mixing):
```
W = Σ [V(x_n, λ_{n+1}) − V(x_n, λ_n)]
```
Position x_n held fixed; only protocol parameter λ changes.

## Components

| Class | Role |
|-------|------|
| `Protocol` | V(x, λ(t)) and g(x, λ(t)) |
| `ProtocolForce` | Force layer for engine integration |
| `WorkAccumulator` | Accumulates inclusive work per trajectory |
| `JarzynskiEstimator` | ΔF from work samples (log-sum-exp stabilized) |
| `CrooksAnalyzer` | Bidirectional Jarzynski level analysis |
| `EntropyBridge` | ΔS_tot = (⟨W⟩ − ΔF) / T (Layer 1 connection) |

## Layer 1 dependency

- **FDT required**: σ² = 2γT/m
- **Initial equilibrium required**: x ~ exp(−V(x,λ₀)/T)
- **O-U exact step**: preserves FDT even with large dt

## Verification (5/5 ALL PASS)

| # | Test | Result |
|---|------|--------|
| 1 | Jarzynski moving trap (ΔF=0) | PASS |
| 2 | Second law ⟨W⟩ ≥ ΔF | PASS |
| 3 | Jarzynski stiffness change (known ΔF) | PASS |
| 4 | Quasi-static limit W → ΔF | PASS |
| 5 | Crooks forward/reverse symmetry | PASS |
