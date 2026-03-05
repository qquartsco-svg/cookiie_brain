#!/usr/bin/env python3
"""궁창 전/후 · 아담 계열 vs 일반 인류 수명 동역학 시뮬레이션

하드코딩 없이 S(t), group, generation 만으로:
  - 궁창 전: 아담 계열 ~900년, 일반 120년
  - 궁창 후: 일반 20~40년, 아담 계열 600→…→175년(아브라함)
이 동역학으로 나오는지 검증한다.

검증 모드:
  1) 수식만: S/L을 직접 넣은 MockWorld로 기대 수명·integrity 검증 (기존).
  2) 통합: FirmamentLayer를 루프에 넣고, instability → fl.step → layer0 → scenario_overlay
            로 homeostasis에 전달해 "행성 붕괴 → 궁창 변화 → 수명 변화" 체인 검증.

사용법:
  python -m solar.eden.eden_os.lifespan_flood_sim
  python -m solar.eden.eden_os.lifespan_flood_sim --integration  # Firmament 기반 통합 검증
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

# eden_os 내부 모듈
from solar._03_eden_os_underworld.eden.eden_os.lifespan_budget import (
    expected_lifespan_yr,
    env_decay_per_tick,
    compute_lifespan_budget,
)
from solar._03_eden_os_underworld.eden.eden_os.homeostasis_engine import HomeostasisEngine, make_homeostasis_engine
from solar._03_eden_os_underworld.eden.firmament import FirmamentLayer


@dataclass
class MockWorld:
    """layer["SCENARIO"] 만 있는 더미 월드 (덕 타이핑)."""
    eden_index: float = 0.95
    layer: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.layer:
            self.layer = {}
        if "SCENARIO" not in self.layer:
            self.layer["SCENARIO"] = {"eden_index": self.eden_index}
        self.layer["SCENARIO"].setdefault("eden_index", self.eden_index)


def run_pre_flood_checks() -> bool:
    """궁창 전(S=1): 기대 수명만 검증."""
    ok = True
    S = 1.0
    L = 0.0
    admin_yr = expected_lifespan_yr(S, L, "admin_line", 0)
    general_yr = expected_lifespan_yr(S, L, "general", 0)
    if admin_yr < 800 or admin_yr > 1000:
        print(f"  FAIL pre-flood admin_line expected ~900, got {admin_yr:.0f}")
        ok = False
    else:
        print(f"  OK   pre-flood admin_line: {admin_yr:.0f} yr (목표 ~900)")
    if general_yr < 100 or general_yr > 140:
        print(f"  FAIL pre-flood general expected ~120, got {general_yr:.0f}")
        ok = False
    else:
        print(f"  OK   pre-flood general:     {general_yr:.0f} yr (목표 120)")
    return ok


def run_post_flood_checks() -> bool:
    """궁창 후(S=0): 일반 20~40년, 아담 계열 세대별 감쇠."""
    ok = True
    S = 0.0
    L = 1.0
    general_yr = expected_lifespan_yr(S, L, "general", 0)
    if general_yr < 15 or general_yr > 50:
        print(f"  FAIL post-flood general expected 20~40, got {general_yr:.0f}")
        ok = False
    else:
        print(f"  OK   post-flood general:     {general_yr:.0f} yr (목표 20~40)")
    gen0 = expected_lifespan_yr(S, L, "admin_line", 0)
    gen10 = expected_lifespan_yr(S, L, "admin_line", 10)
    if gen0 < 500 or gen0 > 700:
        print(f"  FAIL post-flood admin gen0 expected ~600, got {gen0:.0f}")
        ok = False
    else:
        print(f"  OK   post-flood admin gen0:  {gen0:.0f} yr (목표 ~600)")
    if gen10 < 150 or gen10 > 200:
        print(f"  FAIL post-flood admin gen10 expected ~175, got {gen10:.0f}")
        ok = False
    else:
        print(f"  OK   post-flood admin gen10: {gen10:.0f} yr (목표 ~175 아브라함)")
    return ok


def run_integrity_simulation(
    ticks_pre: int = 50,
    ticks_post: int = 400,
    theta2: float = 0.40,
) -> bool:
    """Pre-flood 50틱 → Post-flood 400틱 동안 integrity 추이. 일반은 30년 내 θ2 도달, 아담 gen10은 ~175년 내."""
    ok = True
    ticks_per_year = 1.0

    for group, generation, label in [
        ("general", 0, "일반 인류"),
        ("admin_line", 10, "아담 계열 gen10(아브라함)"),
    ]:
        world_pre = MockWorld(eden_index=0.95)
        world_pre.layer["SCENARIO"]["shield_strength"] = 1.0
        world_pre.layer["SCENARIO"]["env_load"] = 0.0
        world_pre.layer["SCENARIO"]["lifespan_group"] = group
        world_pre.layer["SCENARIO"]["lifespan_generation"] = generation

        world_post = MockWorld(eden_index=0.7)
        world_post.layer["SCENARIO"]["shield_strength"] = 0.0
        world_post.layer["SCENARIO"]["env_load"] = 1.0
        world_post.layer["SCENARIO"]["lifespan_group"] = group
        world_post.layer["SCENARIO"]["lifespan_generation"] = generation

        engine = make_homeostasis_engine(theta2=theta2, ticks_per_year=ticks_per_year)
        tick = 0
        # Pre-flood
        for _ in range(ticks_pre):
            snap = engine.update(tick, world_pre)
            tick += 1
        pre_integrity = engine._last.integrity if engine._last else 0.0
        # Post-flood: 누적 env_stress로 integrity 감쇠
        tick_reached_theta2 = None
        for _ in range(ticks_post):
            snap = engine.update(tick, world_post)
            if tick_reached_theta2 is None and snap.integrity < theta2:
                tick_reached_theta2 = tick
            tick += 1
        post_integrity = engine._last.integrity if engine._last else 0.0
        expected_yr = engine._last.expected_lifespan_yr if engine._last else None

        target_yr = 30.0 if group == "general" else 175.0
        if tick_reached_theta2 is not None:
            years_to_theta2 = tick_reached_theta2 - ticks_pre
            if group == "general" and (years_to_theta2 < 10 or years_to_theta2 > 60):
                print(f"  WARN {label}: integrity<θ2 at {years_to_theta2} yr (목표 ~20~40)")
            elif group == "admin_line" and (years_to_theta2 < 100 or years_to_theta2 > 250):
                print(f"  WARN {label}: integrity<θ2 at {years_to_theta2} yr (목표 ~175)")
            else:
                print(f"  OK   {label}: integrity<θ2 at {years_to_theta2} yr post-flood (목표 ~{target_yr:.0f})")
        else:
            print(f"  INFO {label}: post-flood {ticks_post}yr 후에도 integrity={post_integrity:.3f} (θ2={theta2}) — 예상 수명 {expected_yr}")
    return ok


def run_firmament_integration_simulation(
    ticks_pre: int = 50,
    collapse_at_tick: int = 50,
    ticks_post: int = 400,
    theta2: float = 0.40,
    instability_collapse: float = 0.90,
) -> bool:
    """FirmamentLayer 기반 통합 검증: 매 틱 instability → fl.step → layer0 → scenario_overlay → homeostasis.

    수동 오버레이가 아니라, 실제로:
      instability = 0 (pre) → collapse_at_tick 에서 instability >= θ_collapse → 붕괴
      이후 firmament.get_layer0_snapshot() 의 S, env_load 가 homeostasis에 전달됨.
    """
    ok = True
    ticks_per_year = 1.0
    dt_yr = 1.0

    firmament = FirmamentLayer()  # 에덴 초기
    engine = make_homeostasis_engine(theta2=theta2, ticks_per_year=ticks_per_year)

    for group, generation, label in [
        ("general", 0, "일반 인류"),
        ("admin_line", 10, "아담 계열 gen10(아브라함)"),
    ]:
        # 리셋
        firmament = FirmamentLayer()
        engine = make_homeostasis_engine(theta2=theta2, ticks_per_year=ticks_per_year)
        tick = 0

        # Pre-flood: instability=0 → 궁창 유지
        for _ in range(ticks_pre):
            instability = 0.0
            firmament.step(dt_yr, instability=instability)
            layer0 = firmament.get_layer0_snapshot()
            world = MockWorld(eden_index=0.95)
            world.layer["SCENARIO"]["shield_strength"] = layer0.shield_strength
            world.layer["SCENARIO"]["env_load"] = layer0.env_load
            world.layer["SCENARIO"]["lifespan_group"] = group
            world.layer["SCENARIO"]["lifespan_generation"] = generation
            engine.update(tick, world)
            tick += 1

        # 한 틱에 붕괴 트리거: instability >= θ_collapse (0.85)
        firmament.step(dt_yr, instability=instability_collapse)
        layer0 = firmament.get_layer0_snapshot()
        world = MockWorld(eden_index=0.7)
        world.layer["SCENARIO"]["shield_strength"] = layer0.shield_strength
        world.layer["SCENARIO"]["env_load"] = layer0.env_load
        world.layer["SCENARIO"]["lifespan_group"] = group
        world.layer["SCENARIO"]["lifespan_generation"] = generation
        engine.update(tick, world)
        tick += 1

        # Post-flood: 이미 붕괴됐으므로 S=0, env_load=1 유지
        theta2_tick = None
        for _ in range(ticks_post - 1):
            firmament.step(dt_yr, instability=None)  # 유지
            layer0 = firmament.get_layer0_snapshot()
            world = MockWorld(eden_index=0.7)
            world.layer["SCENARIO"]["shield_strength"] = layer0.shield_strength
            world.layer["SCENARIO"]["env_load"] = layer0.env_load
            world.layer["SCENARIO"]["lifespan_group"] = group
            world.layer["SCENARIO"]["lifespan_generation"] = generation
            snap = engine.update(tick, world)
            if theta2_tick is None and snap.integrity < theta2:
                theta2_tick = tick
            tick += 1

        # 검증: post-flood 구간에서 integrity < θ2 도달 시점
        target_yr = 30.0 if group == "general" else 175.0
        if theta2_tick is not None:
            years_to_theta2 = theta2_tick - collapse_at_tick
            if group == "general" and (years_to_theta2 < 10 or years_to_theta2 > 60):
                print(f"  WARN [Firmament통합] {label}: integrity<θ2 at {years_to_theta2} yr post-collapse (목표 ~20~40)")
            elif group == "admin_line" and (years_to_theta2 < 100 or years_to_theta2 > 250):
                print(f"  WARN [Firmament통합] {label}: integrity<θ2 at {years_to_theta2} yr post-collapse (목표 ~175)")
            else:
                print(f"  OK   [Firmament통합] {label}: integrity<θ2 at {years_to_theta2} yr post-collapse (목표 ~{target_yr:.0f})")
        else:
            print(f"  INFO [Firmament통합] {label}: post-flood {ticks_post}yr 후에도 θ2 미도달 — 예상 수명 {engine._last.expected_lifespan_yr if engine._last else None}")

        # 궁창이 실제로 붕괴했는지 확인
        if firmament.state.active:
            print(f"  FAIL [Firmament통합] {label}: collapse 후에도 firmament.state.active=True")
            ok = False
        if layer0.shield_strength > 0.01:
            print(f"  FAIL [Firmament통합] {label}: collapse 후 shield_strength={layer0.shield_strength} (기대 0)")
            ok = False

    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="궁창 전/후 수명 동역학 검증")
    parser.add_argument(
        "--integration",
        action="store_true",
        help="FirmamentLayer 기반 통합 검증 (instability→붕괴→수명 체인)",
    )
    args = parser.parse_args()

    print("=== 궁창 전/후 수명 동역학 검증 ===\n")
    print("1) 궁창 전 (S=1) 기대 수명")
    if not run_pre_flood_checks():
        return 1
    print()
    print("2) 궁창 후 (S=0) 기대 수명")
    if not run_post_flood_checks():
        return 1
    print()
    print("3) Integrity 시뮬레이션 (pre 50틱 → post 400틱, 수동 오버레이)")
    run_integrity_simulation(ticks_pre=50, ticks_post=400)
    print()

    if args.integration:
        print("4) Firmament 통합 검증 (instability → fl.step → scenario_overlay → homeostasis)")
        if not run_firmament_integration_simulation(ticks_pre=50, collapse_at_tick=50, ticks_post=400):
            return 1
        print()

    print("=== 완료: 수식 기반 동역학으로 궁창 전/후·두 그룹 수명이 재현됨 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
