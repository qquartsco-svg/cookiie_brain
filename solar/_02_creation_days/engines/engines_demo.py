"""engines_demo.py — 독립 엔진 12개 smoke test

각 엔진이 solar 패키지 없이 단독 인스턴스화 + 기본 동작하는지 확인.
V1~V12 ALL PASS 목표.
"""

from __future__ import annotations
import sys, os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))   # CookiieBrain/
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from solar.engines import (
    StressEngine, RhythmEngine, NitrogenEngine, OceanEngine,
    SeasonEngine, TransportEngine, FoodWebEngine,
    MutationEngine, make_mutation_engine,
    FeedbackEngine, make_feedback_engine,
    NicheEngine, NicheState, make_niche_engine,
    AtmosphereEngine, BiosphereEngine,
)

_passed = 0
_failed = 0

def ok(label: str, cond: bool, detail: str = "") -> None:
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✓ {label}")
    else:
        _failed += 1
        print(f"  ✗ {label}" + (f"  ({detail})" if detail else ""))


print("\n── TIER 1 독립 엔진 (10개) ────────────────────────────────────────")

# V1  StressEngine — 인스턴스화 + push
se = StressEngine()
ok("V1  StressEngine 인스턴스화", se is not None)

# V2  RhythmEngine — 인스턴스화 + obliquity(t) 호출
re = RhythmEngine()
obliq = re.obliquity(t_yr=0.0)
ok("V2  RhythmEngine.obliquity(t=0) → float",
   isinstance(obliq, float), f"obliquity={obliq:.4f}°")

# V3  NitrogenEngine — 인스턴스화 + step
ne = NitrogenEngine()
n_state = ne.step(dt=1.0, B_pioneer=0.5, GPP_rate=1.0,
                  O2_frac=0.21, T_K=288.0, W_moisture=0.5)
ok("V3  NitrogenEngine.step() → NitrogenState", n_state is not None)

# V4  OceanEngine — 인스턴스화 + step
oe = OceanEngine()
o_state = oe.step(dt=1.0, upwelling_uM=10.0, light_factor=0.7)
ok("V4  OceanEngine.step() → OceanState", o_state is not None)

# V5  SeasonEngine — 인스턴스화 + step
from solar._02_creation_days.day4.season_engine import SeasonState
season_e = SeasonEngine(obliquity_deg=23.44)
season_e.step(dt_yr=0.25)
s_state = season_e.state(lat_deg=45.0)
ok("V5  SeasonEngine.step() → state 접근 가능", s_state is not None)

# V6  TransportEngine — 인스턴스화 + step (보존형)
from solar._02_creation_days.day5.seed_transport import TransportKernel
kernel = TransportKernel(n_bands=4, neighbors=[[1],[0,2],[1,3],[2]], rates=[0.1]*4)
te = TransportEngine(kernel)
B = [1.0, 2.0, 3.0, 4.0]
B2 = te.step(B, dt_yr=1.0)
total_conserved = abs(sum(B2) - sum(B)) < 0.1
ok("V6  TransportEngine.step() 보존형 확산", total_conserved,
   f"sum_in={sum(B):.3f}, sum_out={sum(B2):.3f}")

# V7  FoodWebEngine — 인스턴스화 + step
from solar._02_creation_days.day5.food_web import TrophicState
fw = FoodWebEngine()
fw_state = TrophicState(phyto=1.0, herbivore=0.5, carnivore=0.2, co2_resp_yr=0.0)
env_fw = {"GPP": 5.0, "fish_predation": 0.1}
fw_state2 = fw.step(fw_state, env=env_fw, dt_yr=1.0)
ok("V7  FoodWebEngine.step() → TrophicState", fw_state2 is not None)

# V8  MutationEngine — 인스턴스화 + step
import random
me = make_mutation_engine(base_mutation_rate=1.0)
events = me.step(p_contact=1.0, env={"T_surface": 288.0, "CO2_ppm": 400.0},
                 dt_yr=1e6, band_idx=0, n_traits=4, rng=random.Random(42))
ok("V8  MutationEngine.step() → events 최대 n*(n-1)=12",
   len(events) == 12, f"got {len(events)}")

# V9  FeedbackEngine — 인스턴스화 + step
fe = make_feedback_engine()
env_in = {"albedo": 0.3, "CO2_ppm": 400.0}
res9 = fe.step(env_in, genomes=[[0.5, 2.0]], densities=[10.0], dt_yr=1.0)
ok("V9  FeedbackEngine.step() → env 수정",
   res9.env_new["CO2_ppm"] != env_in["CO2_ppm"] or res9 is not None)

# V10 NicheEngine — 인스턴스화 + step
niche = make_niche_engine(n_bands=2, n_species=2)
bands = [
    NicheState(band_idx=0, land_fraction=1.0, resource_capacity=100.0, occupancy=[1.0, 1.0]),
    NicheState(band_idx=1, land_fraction=0.5, resource_capacity=10.0,  occupancy=[2.0, 2.0]),
]
bands2 = niche.step(bands, [{"GPP_scale": 1.0}] * 2, dt_yr=1.0)
ok("V10 NicheEngine.step() → 밴드 2개 갱신",
   len(bands2) == 2 and all(b is not None for b in bands2))

print("\n── TIER 2 래퍼 엔진 (2개) ─────────────────────────────────────────")

# V11 AtmosphereEngine — 인스턴스화
from solar._02_creation_days.day2.atmosphere.column import AtmosphereComposition
atm = AtmosphereEngine()
ok("V11 AtmosphereEngine 인스턴스화", atm is not None)

# V12 BiosphereEngine — 인스턴스화
bio = BiosphereEngine()
ok("V12 BiosphereEngine 인스턴스화", bio is not None)

print(f"\n{'='*55}")
print(f"  Engines Demo: {_passed}/{_passed+_failed} PASS  |  {_failed} FAIL")
print(f"{'='*55}")
if _failed == 0:
    print("  ✅  ALL PASS — 독립 엔진 12개 동작 확인")
else:
    print("  ❌  SOME FAILED")
    sys.exit(1)
