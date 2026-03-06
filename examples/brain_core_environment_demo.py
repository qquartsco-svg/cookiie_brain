"""BrainCore 연동 데모 — solar 환경 상태를 extension으로 제공

GEAR_CONNECTION_STRATEGY Phase 1: CookiieBrain → BrainCore
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar.brain_core_bridge import (
    get_solar_environment_extension,
    create_default_environment,
)

# BrainCore optional
try:
    from brain_core.global_state import GlobalState
    BRAINCORE_AVAILABLE = True
except ImportError:
    BRAINCORE_AVAILABLE = False


def main():
    print("=" * 60)
    print(" BrainCore \uc5f0\ub3d9: solar_environment extension")
    print("=" * 60)

    engine, sun, atmospheres = create_default_environment(
        use_water_cycle=False,
        use_surface_schema=True,
    )

    # 1 step
    data = get_solar_environment_extension(engine, sun, atmospheres, dt_yr=0.01)

    print(f"\n  time_yr = {data['time_yr']:.4f}")
    print(f"  any_habitable = {data['global']['any_habitable']}")
    for name, b in data["bodies"].items():
        if b.get("T_surface") is not None:
            print(f"  {name}: T={b['T_surface']:.1f}K P={b['P_surface']:.0f}Pa "
                  f"habitable={b['habitable']} phase={b['water_phase']}")

    # BrainCore 연동 시뮬레이션
    if BRAINCORE_AVAILABLE:
        state = GlobalState(
            state_vector=__import__("numpy").array([1.0, 0.0, 0.0, 0.0]),
            energy=0.0,
            risk=0.0,
        )
        state.set_extension("solar_environment", data)
        env = state.get_extension("solar_environment")
        print(f"\n  [BrainCore] state.get_extension('solar_environment') \u2705")
        print(f"  Earth T = {env['bodies']['Earth']['T_surface']:.1f} K")
    else:
        print("\n  [BrainCore optional] extension \ud615\uc2dd \ud655\uc778 \uc644\ub8cc")
        print("  (BrainCore \uc124\uce58 \uc2dc state.set_extension \uc0ac\uc6a9)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
