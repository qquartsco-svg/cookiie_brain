#!/usr/bin/env python3
"""solar 전체 import·별칭 검증. 문서대로 구현되어 있는지 확인."""
from __future__ import annotations

import os
import sys

# 프로젝트 루트를 path에 추가 (solar/verify_imports.py 로 실행 시)
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
if _root not in sys.path:
    sys.path.insert(0, _root)

def main():
    errors = []
    # 1) 루트 import
    try:
        import L0_solar
    except Exception as e:
        errors.append(f"import solar: {e}")
        return 1

    # 2) 문서에 나온 별칭 전부 로드
    aliases = [
        "day1", "day2", "day3", "day4", "day5", "day6", "day7",
        "fields", "surface", "physics", "bridge", "engines",
        "eden", "biosphere", "cognitive", "governance", "underworld", "monitoring",
        "precreation", "joe", "planet_dynamics",
    ]
    for name in aliases:
        try:
            m = getattr(solar, name, None)
            if m is None:
                errors.append(f"solar.{name} is None")
            else:
                assert m is not None
        except Exception as e:
            errors.append(f"solar.{name}: {e}")

    # 3) 문서에 나온 핵심 심볼
    symbols = [
        ("SurfaceSchema", getattr(solar, "SurfaceSchema", None)),
        ("effective_albedo", getattr(solar, "effective_albedo", None)),
        ("EvolutionEngine", getattr(solar, "EvolutionEngine", None)),
        ("GaiaBridge", getattr(solar, "GaiaBridge", None)),
        ("run_pipeline", getattr(solar, "run_pipeline", None)),
        ("PipelineState", getattr(solar, "PipelineState", None)),
    ]
    for sym_name, sym_val in symbols:
        if sym_val is None:
            errors.append(f"symbol {sym_name} is None")

    if hasattr(solar, "biosphere"):
        if getattr(solar.biosphere, "BiosphereColumn", None) is None:
            errors.append("solar.biosphere.BiosphereColumn is None")

    # 4) planet_dynamics = joe
    if hasattr(solar, "planet_dynamics") and hasattr(solar, "joe"):
        if solar.planet_dynamics is not solar.joe:
            errors.append("solar.planet_dynamics is not solar.joe")

    # 5) surface = day3.surface
    if hasattr(solar, "surface"):
        if "day3.surface" not in getattr(solar.surface, "__name__", ""):
            errors.append("solar.surface should be day3.surface")

    # 6) day6 in _02_creation_days
    if hasattr(solar, "day6"):
        if "_02_creation_days.day6" not in getattr(solar.day6, "__name__", ""):
            errors.append("solar.day6 should be _02_creation_days.day6")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    print("OK: all aliases and symbols verified.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
