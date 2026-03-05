"""solar/fire/ — 전지구 산불 발생 예측 엔진 (Phase 7f → v2.3)

설계 철학:
  "환경 설정(O2, T, W, 위도, 계절)만 하면
   항상성에 의해 산불이 발생할 지점이 자연스럽게 창발된다"

구조:
  fire_risk.py          → 단일 위도×계절 산불 위험도 ODE (로컬 플럭스만)
  fire_engine.py        → 전지구 예측 엔진 (BandEco, provider 주입, ΔO2_frac)
  stress_accumulator.py → 뉴런(ms)→기관(hr)→행성(yr) 3단계 번역기 + LocalFireReset

독립 모듈:
  solar/biosphere/에 의존하지 않음
  환경 snapshot(O2, T, W, B_wood)만 받아서 동작
  LatitudeBands와 연결하거나 단독 실행 모두 가능

v2.3 추가:
  StressAccumulator: 뉴런 스트레스 → 행성 산불 압력 3단계 번역기
  LocalFireReset:    산불 발생 시 B_wood 국소 소각 + 스트레스 해소
  HOMEO_MAP:         미시(뉴런)-거시(행성) 완전 변수 매핑
"""

from .fire_risk import (
    compute_fire_risk,
    FireRiskState,
    f_O2_fire,
    f_fuel,
    f_temperature,
    f_dryness,
    dry_season_modifier,
    O2_IGNITION_MIN,
    O2_IGNITION_HIGH,
    K_FIRE_INTENSITY,
)
from .fire_engine import (
    FireEngine,
    FireEnvSnapshot,
    FireBandResult,
    BandEco,
    BAND_CENTERS_DEG,
    BAND_WEIGHTS,
    BAND_COUNT,
    KG_O2_PER_FRAC,
    LAND_AREA_M2,
)
from .stress_accumulator import (
    StressAccumulator,
    LocalFireReset,
    NeuronEvent,
    CellStressState,
    OrganFatigueState,
    PlanetStressIndex,
)

__all__ = [
    # fire_risk
    "compute_fire_risk", "FireRiskState",
    "f_O2_fire", "f_fuel", "f_temperature", "f_dryness", "dry_season_modifier",
    "O2_IGNITION_MIN", "O2_IGNITION_HIGH", "K_FIRE_INTENSITY",
    # fire_engine
    "FireEngine", "FireEnvSnapshot", "FireBandResult", "BandEco",
    "BAND_CENTERS_DEG", "BAND_WEIGHTS", "BAND_COUNT",
    "KG_O2_PER_FRAC", "LAND_AREA_M2",
    # stress_accumulator
    "StressAccumulator", "LocalFireReset", "NeuronEvent",
    "CellStressState", "OrganFatigueState", "PlanetStressIndex",
]
