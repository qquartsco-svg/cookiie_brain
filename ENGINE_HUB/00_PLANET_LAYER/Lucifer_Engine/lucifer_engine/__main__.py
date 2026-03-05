"""CLI: 혜성/소행성 충돌 예상·탐색.

사용 예:
  python -m lucifer_engine
  python -m lucifer_engine /path/to/params.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import ImpactParams, estimate_impact


def _default_params() -> ImpactParams:
    return ImpactParams(
        D_km=10.0,
        rho_gcm3=3.0,
        v_kms=20.0,
        theta_deg=45.0,
        h_km=4.0,
        lat_deg=-30.0,
        lon_deg=120.0,
    )


def main() -> None:
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        raw = json.loads(path.read_text())
        params = ImpactParams(
            D_km=float(raw.get("D_km", 10.0)),
            rho_gcm3=float(raw.get("rho_gcm3", 3.0)),
            v_kms=float(raw.get("v_kms", 20.0)),
            theta_deg=float(raw.get("theta_deg", 45.0)),
            h_km=float(raw.get("h_km", 4.0)),
            lat_deg=float(raw.get("lat_deg", 0.0)),
            lon_deg=float(raw.get("lon_deg", 0.0)),
        )
    else:
        params = _default_params()

    result = estimate_impact(params)
    out = {
        "E_total_J": result.E_total_J,
        "E_eff_J": result.E_eff_J,
        "f_atm": result.f_atm,
        "f_ocean": result.f_ocean,
        "f_crust": result.f_crust,
        "delta_H2O_canopy": result.delta_H2O_canopy,
        "delta_pressure_atm": result.delta_pressure_atm,
        "delta_sea_level_m": result.delta_sea_level_m,
        "delta_pole_eq_delta_K": result.delta_pole_eq_delta_K,
        "shock_strength": result.shock_strength,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
