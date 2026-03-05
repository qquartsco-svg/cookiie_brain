"""solar.pipeline — 시간 흐름 엔진. 5단계 순서대로 실행.

흐름: 행성 탐사 → 천지창조 day1~7 → 에덴·OS·언더월드 → 궁창 환경시대 → 노아 대홍수 이벤트
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineState:
    """파이프라인 단계 간 공유 상태."""
    # 1단계
    joe_result: Optional[tuple] = None
    # 2단계
    planet_runner: Any = None
    creation_snapshot: Any = None
    # 3단계
    eden_runner: Any = None
    eden_snapshot: Any = None
    # 4단계
    firmament: Any = None
    layer0: Any = None
    # 5단계
    flood_engine: Any = None
    flood_snapshot: Any = None


def run_beginnings(ic: Any = None, water_snapshot: Optional[dict] = None) -> tuple:
    """1단계: 행성 탐사. (planet_stress, instability) 반환."""
    from solar._01_beginnings.joe import run as joe_run
    from solar._03_eden_os_underworld.eden.initial_conditions import make_antediluvian
    if ic is None:
        ic = make_antediluvian()
    return joe_run(ic, water_snapshot=water_snapshot)


def run_creation_days(
    initial_conditions: Any = None,
    dt_yr: float = 0.01,
    state: Optional[PipelineState] = None,
) -> Any:
    """2단계: 천지창조 day1~7 한 스텝. PlanetSnapshot 반환."""
    from solar._02_creation_days.day7.runner import PlanetRunner, make_planet_runner
    from solar._03_eden_os_underworld.eden.initial_conditions import make_antediluvian
    if initial_conditions is None:
        initial_conditions = make_antediluvian()
    runner = make_planet_runner(initial_conditions=initial_conditions.to_runner_kwargs())
    return runner.step(dt_yr=dt_yr)


def run_eden_os_underworld(steps: int = 1, state: Optional[PipelineState] = None) -> Any:
    """3단계: 에덴·OS·언더월드 (EdenOS 러너 steps 스텝)."""
    from solar._03_eden_os_underworld.eden.eden_os import make_eden_os_runner
    runner = make_eden_os_runner()
    runner.run(steps=steps)
    return runner


def run_firmament_era(
    dt_yr: float = 1.0,
    state: Optional[PipelineState] = None,
) -> tuple:
    """4단계: 궁창 환경시대 한 스텝. (firmament, layer0, instability) 반환."""
    from solar._04_firmament_era.engine import run_firmament_era_step
    return run_firmament_era_step(dt_yr=dt_yr)


def run_noah_flood(
    flood_engine: Any = None,
    dt_yr: float = 1.0,
    state: Optional[PipelineState] = None,
) -> Any:
    """5단계: 노아 대홍수 한 스텝. FloodSnapshot 반환."""
    from solar._05_noah_flood.engine import run_flood_step
    return run_flood_step(flood_engine=flood_engine, dt_yr=dt_yr)


def run_pipeline(
    steps_per_stage: Optional[Dict[str, int]] = None,
    state: Optional[PipelineState] = None,
) -> PipelineState:
    """전체 흐름 엔진: 1→2→3→4→5 순서로 한 사이클 실행."""
    if state is None:
        state = PipelineState()
    if steps_per_stage is None:
        steps_per_stage = {"beginnings": 1, "creation": 1, "eden": 1, "firmament": 1, "flood": 0}

    # 1. 행성 탐사
    if steps_per_stage.get("beginnings", 1) > 0:
        state.joe_result = run_beginnings()

    # 2. 천지창조 day1~7
    if steps_per_stage.get("creation", 1) > 0:
        state.creation_snapshot = run_creation_days(state=state)

    # 3. 에덴·OS·언더월드
    if steps_per_stage.get("eden", 1) > 0:
        state.eden_runner = run_eden_os_underworld(steps=steps_per_stage.get("eden", 1), state=state)

    # 4. 궁창 환경시대
    if steps_per_stage.get("firmament", 1) > 0:
        firmament, layer0, inst = run_firmament_era(state=state)
        state.firmament = firmament
        state.layer0 = layer0

    # 5. 노아 대홍수 (선택)
    if steps_per_stage.get("flood", 0) > 0:
        state.flood_snapshot = run_noah_flood(dt_yr=1.0, state=state)

    return state


__all__ = [
    "PipelineState",
    "run_beginnings",
    "run_creation_days",
    "run_eden_os_underworld",
    "run_firmament_era",
    "run_noah_flood",
    "run_pipeline",
]
