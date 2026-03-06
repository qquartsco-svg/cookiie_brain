#!/usr/bin/env python3
"""
Grid Engine ↔ Solar 연결 테스트.

실행 위치: CookiieBrain 루트 또는 examples/
  python -m examples.grid_engine_connection_demo
  python examples/grid_engine_connection_demo.py

조건: 데스크탑 00_BRAIN/Archive/Integrated/3.Grid_Engine/package 가 있어야 함.
"""

from __future__ import annotations

import sys
from pathlib import Path

# 프로젝트 루트
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from L0_solar.bridge.grid_engine_bridge import (
    GRID_ENGINE_AVAILABLE,
    get_grid_engine_path,
    is_available,
    get_import_error,
    create_latitude_grid_agent,
)


def main():
    print("=" * 60)
    print("  Grid Engine ↔ Solar 12 위도밴드 연결 테스트")
    print("=" * 60)
    print()
    p = get_grid_engine_path()
    print(f"  Grid Engine 경로: {p}")
    print(f"  폴더 존재:       {p.is_dir()}")
    print(f"  import 가능:     {is_available()}")
    print()

    if not GRID_ENGINE_AVAILABLE:
        print("  ❌ Grid Engine을 불러올 수 없습니다.")
        err = get_import_error()
        if err:
            print(f"     오류: {err}")
        print("     - 00_BRAIN/Archive/Integrated/3.Grid_Engine/package 가 있는지 확인하세요.")
        print("     - grid_engine 의존성(ring-attractor-engine 등)이 설치되어 있는지 확인하세요.")
        print("=" * 60)
        return 1

    print("  ✅ Grid Engine 사용 가능")
    print()
    agent = create_latitude_grid_agent(initial_band=0, ring_size=15)
    if agent is None:
        print("  ❌ create_latitude_grid_agent() 실패")
        return 1
    print("  ✅ LatitudeGridAdapter 생성됨 (초기 밴드=0)")
    b0 = agent.get_band_index()
    print(f"     get_band_index() = {b0}")
    b1 = agent.step(velocity_lat=0.5)
    print(f"     step(velocity_lat=0.5) 후 밴드 = {b1}")
    agent.reset(band=6)
    print(f"     reset(band=6) 후 밴드 = {agent.get_band_index()}")
    print()
    print("  Solar 12밴드와 연결 가능 상태입니다.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
